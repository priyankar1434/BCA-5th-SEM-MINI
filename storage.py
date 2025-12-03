import os
import boto3
from botocore.exceptions import NoCredentialsError
from werkzeug.utils import secure_filename
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_s3_client():
    """Initialize and return an S3 client."""
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )

def upload_file_to_s3(file, folder='uploads'):
    """
    Upload a file to an S3 bucket
    :param file: File object to upload
    :param folder: Folder in the bucket to store the file
    :return: URL of the uploaded file or None if upload failed
    """
    try:
        s3_client = get_s3_client()
        
        # Generate a unique filename
        filename = secure_filename(file.filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        s3_path = f"{folder}/{unique_filename}"
        
        # Upload the file
        s3_client.upload_fileobj(
            file,
            os.getenv('S3_BUCKET_NAME'),
            s3_path,
            ExtraArgs={
                'ACL': 'public-read',
                'ContentType': file.content_type
            }
        )
        
        # Generate the URL
        location = s3_client.get_bucket_location(Bucket=os.getenv('S3_BUCKET_NAME'))['LocationConstraint']
        region = f"{location}" if location else 'us-east-1'
        url = f"https://{os.getenv('S3_BUCKET_NAME')}.s3.{region}.amazonaws.com/{s3_path}"
        
        return {
            'url': url,
            'path': s3_path,
            'filename': unique_filename
        }
        
    except NoCredentialsError:
        logger.error("AWS credentials not available")
        return None
    except Exception as e:
        logger.error(f"Error uploading to S3: {str(e)}")
        return None

def delete_file_from_s3(s3_path):
    """Delete a file from S3"""
    try:
        s3_client = get_s3_client()
        s3_client.delete_object(
            Bucket=os.getenv('S3_BUCKET_NAME'),
            Key=s3_path
        )
        return True
    except Exception as e:
        logger.error(f"Error deleting file from S3: {str(e)}")
        return False

def get_presigned_url(s3_path, expiration=3600):
    """Generate a presigned URL for a file"""
    try:
        s3_client = get_s3_client()
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': os.getenv('S3_BUCKET_NAME'),
                'Key': s3_path
            },
            ExpiresIn=expiration
        )
        return url
    except Exception as e:
        logger.error(f"Error generating presigned URL: {str(e)}")
        return None
