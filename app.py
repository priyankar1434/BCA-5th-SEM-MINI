# app.py
import os
import json
import logging
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime
from functools import wraps
from PIL import Image
import re
import io
from dotenv import load_dotenv
from storage import upload_file_to_s3, delete_file_from_s3, get_presigned_url

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

# Initialize the Flask application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Fallback for local development
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- Vehicle Database (JSON) ---
VEHICLE_DB_FILE = 'vehicle_database.json'

def load_vehicles():
    """Load authorized vehicles from JSON file."""
    try:
        with open(VEHICLE_DB_FILE, 'r') as f:
            data = json.load(f)
            return [v.upper() for v in data.get('authorized_vehicles', [])]
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def is_vehicle_authorized(vehicle_number):
    """Check if a vehicle is authorized."""
    authorized_vehicles = load_vehicles()
    return vehicle_number.upper() in authorized_vehicles

# --- Authentication Functions ---
def authenticate_user(username, password):
    """Simple in-memory authentication fallback.

    This avoids requiring `auth.db`. For production, replace with a proper
    authentication backend or a JSON-based users file.
    """
    # Basic sample users (username, password)
    users = [
        {'id': 1, 'username': 'admin', 'password': 'admin123', 'full_name': 'Administrator', 'role': 'admin'},
        {'id': 2, 'username': 'student1', 'password': 'pass123', 'full_name': 'Rahul Sharma', 'role': 'student'},
        {'id': 3, 'username': 'student2', 'password': 'pass123', 'full_name': 'Priya Patel', 'role': 'student'},
    ]

    for u in users:
        if u['username'] == username and u['password'] == password:
            return {
                'id': u['id'],
                'username': u['username'],
                'full_name': u['full_name'],
                'role': u['role']
            }
    return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Core Logic Functions ---

def extract_license_plate_from_image(image_file):
    try:
        if not TESSERACT_AVAILABLE:
            return {
                'success': False,
                'error': 'Tesseract OCR not installed. Please install it to use OCR functionality.',
                'detected_plates': [],
                'note': 'Tesseract must be installed separately. Visit: https://github.com/UB-Mannheim/tesseract/wiki'
            }
        
        pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        img = Image.open(image_file)
        img = img.convert('RGB')
        ocr_text = pytesseract.image_to_string(img)
        license_plates = extract_license_plates_from_text(ocr_text)
        return {
            'success': True,
            'raw_text': ocr_text,
            'detected_plates': license_plates
        }
    except FileNotFoundError:
        return {
            'success': False,
            'error': 'Tesseract executable not found at default location. Please install Tesseract OCR.',
            'detected_plates': [],
            'note': 'Download from: https://github.com/UB-Mannheim/tesseract/wiki'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'OCR processing error: {str(e)}',
            'detected_plates': []
        }

def extract_license_plates_from_text(text):
    patterns = [
        r'[A-Z]{2}\d{2}[A-Z]{2}\d{4}',
        r'[A-Z]{2}\d{2}[A-Z]\d{4}',
        r'[A-Z]{2}\d{1,2}[A-Z]{2}\d{3,4}',
    ]
    
    plates = []
    text_upper = text.upper().replace(' ', '').replace('-', '')
    
    for pattern in patterns:
        matches = re.findall(pattern, text_upper)
        plates.extend(matches)
    
    return list(set(plates))

def verify_vehicle(license_plate):
    """
    Lookup the license plate in JSON vehicle database and return authorization info.
    """
    clean_plate = license_plate.strip().upper().replace(" ", "")
    authorized_vehicles = load_vehicles()
    
    if clean_plate in authorized_vehicles:
        return {
            "is_authorized": True,
            "plate": clean_plate,
            "details": {"status": "Authorized"},
            "message": f"SUCCESS! Vehicle {clean_plate} is AUTHORIZED.",
            "alert_type": "success",
        }
    else:
        # Unknown vehicle: treat as unauthorized
        return {
            "is_authorized": False,
            "plate": clean_plate,
            "details": {"status": "Unauthorized"},
            "message": f"ALERT! Vehicle {clean_plate or 'UNKNOWN'} is UNAUTHORIZED.",
            "alert_type": "error",
        }

def save_image(file, plate, is_authorized):
    """Save image to S3 if configured, otherwise save locally"""
    try:
        # For S3 storage
        if all([os.getenv('AWS_ACCESS_KEY_ID'), 
                os.getenv('AWS_SECRET_ACCESS_KEY'), 
                os.getenv('S3_BUCKET_NAME')]):
            result = upload_file_to_s3(file)
            if result:
                return result['url']
            raise Exception("Failed to upload to S3")
        
        # Fallback to local storage
        else:
            filename = secure_filename(f"{datetime.utcnow().timestamp()}_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return filename
            
    except Exception as e:
        logger.error(f"Error saving image: {str(e)}")
        raise

def get_images():
    """Get list of uploaded images"""
    try:
        # For local development, return list of files in upload folder
        if not all([os.getenv('AWS_ACCESS_KEY_ID'), 
                   os.getenv('AWS_SECRET_ACCESS_KEY'), 
                   os.getenv('S3_BUCKET_NAME')]):
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                return []
            return [f for f in os.listdir(app.config['UPLOAD_FOLDER']) 
                   if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        
        # In production, this would list files from S3
        # For simplicity, we'll return an empty list
        return []
    except Exception as e:
        logger.error(f"Error getting images: {str(e)}")
        return []

# --- Flask Routes ---

@app.route('/')
def index():
    """
    The main route serving the web interface (dashboard).
    """
    if 'user_id' not in session:
        return render_template('login.html')
    images = get_images()
    user = {
        'username': session.get('username'),
        'full_name': session.get('full_name'),
        'role': session.get('role')
    }
    return render_template('index.html', images=images, user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login page for college authentication.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = authenticate_user(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['role'] = user['role']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """
    Logout the user and clear session.
    """
    session.clear()
    return redirect(url_for('login'))

@app.route('/scan', methods=['POST'])
@login_required
def scan_vehicle():
    """
    API endpoint to handle the vehicle scan request (triggered by the web interface).
    """
    data = request.get_json()
    license_plate = data.get('license_plate', '').strip()
    if not license_plate:
        return jsonify({
            "is_authorized": False,
            "message": "Error: No license plate detected.",
            "alert_type": "warning"
        }), 400
    result = verify_vehicle(license_plate)
    print(f"[{result['alert_type'].upper()}] Vehicle Scanned: {result['plate']} at {request.host_url}scan") 
    return jsonify(result)

@app.route('/ocr', methods=['POST'])
@login_required
def ocr_extract():
    if 'image' not in request.files:
        return jsonify({
            "success": False,
            "message": "No image uploaded",
            "detected_plates": []
        }), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({
            "success": False,
            "message": "No selected file",
            "detected_plates": []
        }), 400
    
    try:
        ocr_result = extract_license_plate_from_image(file)
        return jsonify(ocr_result)
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "detected_plates": []
        }), 500

@app.route('/upload', methods=['POST'])
@login_required
def upload_image():
    """
    API endpoint to handle image upload and immediate database save.
    """
    if 'image' not in request.files:
        return jsonify({"message": "No image uploaded"}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400
    plate = request.form.get('license_plate', 'UNKNOWN')
    result = verify_vehicle(plate)
    filename = save_image(file, plate, result['is_authorized'])
    return jsonify({"message": "Image uploaded", "filename": filename, "result": result})

@app.route('/gallery')
@login_required
def gallery():
    """
    API endpoint to fetch all images for gallery display.
    """
    images = get_images()
    return jsonify(images)

@app.route('/static/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files from local filesystem (development only)"""
    if not all([os.getenv('AWS_ACCESS_KEY_ID'), 
               os.getenv('AWS_SECRET_ACCESS_KEY'), 
               os.getenv('S3_BUCKET_NAME')]):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    # In production, redirect to S3 URL
    s3_path = f"uploads/{filename}"
    presigned_url = get_presigned_url(s3_path)
    if presigned_url:
        return redirect(presigned_url)
    return "File not found", 404

# --- Application Run ---

if __name__ == '__main__':
    # Check for required environment variables in production
    if os.getenv('FLASK_ENV') == 'production':
        required_vars = ['SECRET_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            exit(1)
    
    # Run the application
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_ENV') != 'production')