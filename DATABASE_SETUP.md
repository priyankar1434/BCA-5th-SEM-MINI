# Vehicle Authorization System Documentation

## Overview
Your vehicle authorization system now uses a single, clean JSON database for storing and verifying authorized vehicle license numbers.

## Database Structure

### File: `vehicle_database.json`
```json
{
    "authorized_vehicles": [
        "M2346021",
        "UP70BD4567",
        "DL5CAB1234",
        "MH12AB1234",
        "RJ14CD5678",
        "RM1A23DFEW",
        "UP70AB6226",
        "UK06AF6226"
    ]
}
```

**Note:** All vehicle numbers are stored in UPPERCASE for case-insensitive verification.

---

## How the System Works

### 1. **Vehicle Verification Flow**

When a user uploads/captures a license plate image:
1. **OCR Extraction**: The system extracts the license plate number from the image
2. **JSON Lookup**: The extracted number is checked against `vehicle_database.json`
3. **Result Display**: The system shows:
   - ✓ **SUCCESS** (Green) - Vehicle is authorized
   - ✗ **ALERT** (Red) - Vehicle is NOT authorized

### 2. **Using Flask Web Interface (app.py)**

When a license plate is scanned/entered:
```python
result = verify_vehicle("MH12AB1234")
# Returns:
# {
#     "is_authorized": True,
#     "plate": "MH12AB1234",
#     "message": "SUCCESS! Vehicle MH12AB1234 is AUTHORIZED.",
#     "alert_type": "success"
# }
```

### 3. **Using Command Line (check_vehicle.py)**

Run the interactive tool:
```bash
python check_vehicle.py
```

Options:
- **Check Vehicle**: Enter a license plate to verify if it's authorized
- **Add Vehicle**: Add a new authorized vehicle to the database
- **Remove Vehicle**: Remove a vehicle from the database
- **View All Vehicles**: Display all authorized vehicles
- **Exit**: Close the program

---

## File Changes Made

### Removed Files (Cleaned Up)
- `authorized_vehicles.txt` - No longer needed
- `vehicle.db` - SQLite database (replaced by JSON)
- `vehicles.db` - SQLite database (replaced by JSON)
- `auth.db` - SQLite database (replaced by JSON)

### Updated Files
1. **app.py**
   - Removed all SQLite database imports
   - Updated `verify_vehicle()` to use JSON lookup
   - Simplified `save_image()` function
   - All vehicle checks now use `load_vehicles()` function

2. **check_vehicle.py**
   - Enhanced with `remove_vehicle()` method
   - Added `get_all_vehicles()` method
   - Interactive CLI menu for easy management
   - Automatic JSON file handling

### Key Functions

#### In `app.py`:
```python
def load_vehicles():
    """Load authorized vehicles from JSON file."""
    # Returns list of all authorized vehicle numbers

def is_vehicle_authorized(vehicle_number):
    """Check if a vehicle is authorized."""
    # Returns True/False

def verify_vehicle(license_plate):
    """Verify vehicle and return authorization details."""
    # Returns dict with status, message, alert type
```

#### In `check_vehicle.py`:
```python
class VehicleValidator:
    def is_vehicle_authorized(vehicle_number)    # Check authorization
    def add_vehicle(vehicle_number)               # Add new vehicle
    def remove_vehicle(vehicle_number)            # Remove vehicle
    def get_all_vehicles()                        # Get all vehicles
```

---

## Updating the Vehicle Database

### Method 1: Direct JSON Edit
Simply open `vehicle_database.json` and add/remove vehicle numbers in the list.

### Method 2: Using Python
```python
from check_vehicle import VehicleValidator

validator = VehicleValidator()
validator.add_vehicle("HR26EF1234")      # Add a vehicle
validator.remove_vehicle("DL5CAB1234")   # Remove a vehicle
```

### Method 3: Using CLI
```bash
python check_vehicle.py
# Then select option 2 to add or option 3 to remove
```

---

## Testing the System

Run the test script to verify everything works:
```bash
python test_vehicle_system.py
```

Expected output:
- ✓ All test cases pass
- All vehicles loaded correctly from JSON
- Verification works for authorized and unauthorized vehicles

---

## Benefits of JSON-Based System

✓ **Single Source of Truth** - One JSON file for all vehicle data  
✓ **No Database Overhead** - No need for SQLite, no database setup  
✓ **Easy to Update** - Simple text format, easy to edit manually  
✓ **Fast Lookup** - Loaded into memory for quick verification  
✓ **Portable** - Easy to backup, share, or migrate  
✓ **Version Control** - Can be tracked in Git  
✓ **No Dependencies** - JSON is built into Python  

---

## Integration with Your App

Your Flask application automatically uses the JSON database. When a user:
1. Uploads an image → OCR extracts plate
2. System calls `verify_vehicle(extracted_plate)`
3. Function checks against `vehicle_database.json`
4. Result displayed to user (Success or Alert)

No additional configuration needed!

---

## Troubleshooting

**Issue**: "File not found" error
- **Solution**: Ensure `vehicle_database.json` exists in the same directory as `app.py`

**Issue**: Vehicle not found even though it's in the file
- **Solution**: Check if the vehicle number has spaces or is in lowercase. The system auto-converts to uppercase and removes spaces.

**Issue**: JSON parsing errors
- **Solution**: Validate your JSON at https://jsonlint.com/ to ensure proper formatting

---

## Summary

Your vehicle authorization system is now:
- ✓ Simplified (JSON instead of multiple databases)
- ✓ Faster (no database queries)
- ✓ Cleaner (removed 4 unnecessary files)
- ✓ Maintainable (easy to update manually)
- ✓ Reliable (case-insensitive verification)

All vehicle verification now flows through a single, clean JSON database!
