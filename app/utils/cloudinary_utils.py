"""Cloudinary image handling utilities"""

import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
from datetime import datetime

# Cloudinary configuration
def configure_cloudinary():
    """Configure Cloudinary with environment variables"""
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET')
    )


# File validation
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def is_allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_extension(filename):
    """Get file extension"""
    if '.' not in filename:
        return None
    return filename.rsplit('.', 1)[1].lower()


def validate_image_file(file_obj, filename):
    """Validate image file"""
    errors = []
    
    if not filename:
        errors.append('Filename is required')
    
    if not is_allowed_file(filename):
        errors.append(f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}')
    
    file_size = get_file_size(file_obj)
    if file_size > MAX_FILE_SIZE:
        errors.append(f'File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024:.1f}MB')
    
    if file_size == 0:
        errors.append('File is empty')
    
    return errors


def get_file_size(file_obj):
    """Get file size in bytes"""
    file_obj.seek(0)
    file_obj.seek(0, 2)  # Seek to end
    size = file_obj.tell()
    file_obj.seek(0)  # Reset to beginning
    return size


def upload_to_cloudinary(file_obj, auction_id, folder='naomi-auction'):
    """
    Upload image to Cloudinary
    
    Returns:
        dict: Contains 'url', 'public_id', 'secure_url', 'width', 'height'
    """
    try:
        configure_cloudinary()
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        public_id = f"{folder}/{auction_id}/{timestamp}"
        
        result = cloudinary.uploader.upload(
            file_obj,
            public_id=public_id,
            resource_type='auto',
            quality='auto',
            fetch_format='auto',
            eager=[
                {'width': 1600, 'height': 1200, 'crop': 'fill', 'quality': 'auto', 'fetch_format': 'auto'},
                {'width': 400, 'height': 300, 'crop': 'fill', 'quality': 'auto', 'fetch_format': 'auto'}
            ],
            tags=[f'auction_{auction_id}'],
            metadata={
                'auction_id': str(auction_id),
                'uploaded_at': timestamp
            }
        )
        
        return {
            'url': result.get('secure_url'),
            'public_id': result.get('public_id'),
            'width': result.get('width'),
            'height': result.get('height'),
            'format': result.get('format'),
            'eager_transformations': result.get('eager', [])
        }
    
    except Exception as e:
        raise Exception(f'Cloudinary upload failed: {str(e)}')


def delete_from_cloudinary(public_id):
    """Delete image from Cloudinary"""
    try:
        configure_cloudinary()
        result = cloudinary.uploader.destroy(public_id)
        return result.get('result') == 'ok'
    except Exception as e:
        print(f'Error deleting from Cloudinary: {str(e)}')
        return False


def get_cloudinary_url(public_id, transformations=None):
    """Get Cloudinary URL with optional transformations"""
    try:
        configure_cloudinary()
        
        if transformations:
            return cloudinary.CloudinaryResource(public_id).build_url(**transformations)
        else:
            return cloudinary.CloudinaryResource(public_id).build_url(secure=True)
    
    except Exception as e:
        print(f'Error generating Cloudinary URL: {str(e)}')
        return None


def get_thumbnail_url(public_id, width=400, height=300):
    """Get thumbnail URL"""
    return get_cloudinary_url(public_id, {
        'width': width,
        'height': height,
        'crop': 'fill',
        'quality': 'auto',
        'fetch_format': 'auto'
    })


def get_optimized_url(public_id, width=1600, height=1200):
    """Get optimized URL for display"""
    return get_cloudinary_url(public_id, {
        'width': width,
        'height': height,
        'crop': 'fill',
        'quality': 'auto',
        'fetch_format': 'auto'
    })


def get_resource_info(public_id):
    """Get resource information from Cloudinary"""
    try:
        configure_cloudinary()
        return cloudinary.api.resource(public_id)
    except Exception as e:
        print(f'Error getting resource info: {str(e)}')
        return None


def list_resources_by_tag(tag):
    """List all resources with a specific tag"""
    try:
        configure_cloudinary()
        return cloudinary.api.resources_by_tag(tag)
    except Exception as e:
        print(f'Error listing resources: {str(e)}')
        return []


def delete_resources_by_tag(tag):
    """Delete all resources with a specific tag"""
    try:
        configure_cloudinary()
        resources = cloudinary.api.resources_by_tag(tag)
        for resource in resources.get('resources', []):
            cloudinary.uploader.destroy(resource['public_id'])
        return True
    except Exception as e:
        print(f'Error deleting resources by tag: {str(e)}')
        return False
