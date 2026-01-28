"""Image handling utilities with Cloudinary integration"""

import os
import cloudinary
import cloudinary.uploader
from werkzeug.utils import secure_filename
from datetime import datetime
from flask import current_app

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}


def init_cloudinary():
    """Initialize Cloudinary with credentials from config"""
    if current_app.config.get('CLOUDINARY_CLOUD_NAME'):
        cloudinary.config(
            cloud_name=current_app.config['CLOUDINARY_CLOUD_NAME'],
            api_key=current_app.config['CLOUDINARY_API_KEY'],
            api_secret=current_app.config['CLOUDINARY_API_SECRET']
        )
        return True
    return False


def is_allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_extension(filename):
    """Get file extension"""
    if '.' not in filename:
        return None
    return filename.rsplit('.', 1)[1].lower()


def generate_image_filename(auction_id, original_filename):
    """Generate a unique filename for uploaded image"""
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    ext = get_file_extension(original_filename)
    return f"{auction_id}_{timestamp}.{ext}"


def get_file_size(file_obj):
    """Get file size in bytes"""
    file_obj.seek(0, os.SEEK_END)
    size = file_obj.tell()
    file_obj.seek(0)
    return size


def validate_image_file(file_obj, filename):
    """Validate image file"""
    errors = []
    
    if not filename:
        errors.append('Filename is required')
    
    if not is_allowed_file(filename):
        errors.append(f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}')
    
    file_size = get_file_size(file_obj)
    max_size = current_app.config.get('MAX_IMAGE_SIZE', 5 * 1024 * 1024)
    if file_size > max_size:
        errors.append(f'File too large. Maximum size: {max_size / 1024 / 1024:.1f}MB')
    
    if file_size == 0:
        errors.append('File is empty')
    
    return errors


def upload_to_cloudinary(file_obj, auction_id, image_title=None):
    """Upload image to Cloudinary"""
    try:
        if not init_cloudinary():
            raise Exception('Cloudinary not configured')
        
        # Generate public ID for the image
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        public_id = f"{current_app.config['CLOUDINARY_FOLDER']}/{auction_id}/{timestamp}_{secure_filename(image_title or 'image')}"
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            file_obj,
            public_id=public_id,
            overwrite=False,
            resource_type='auto',
            quality='auto',
            fetch_format='auto',
            transformation=[
                {
                    'width': 1600,
                    'height': 1200,
                    'crop': 'limit',
                    'quality': current_app.config.get('IMAGE_QUALITY', 85)
                }
            ]
        )
        
        return {
            'public_id': result['public_id'],
            'secure_url': result['secure_url'],
            'url': result['url'],
            'width': result['width'],
            'height': result['height'],
            'bytes': result['bytes'],
            'format': result['format']
        }
    
    except Exception as e:
        raise Exception(f'Cloudinary upload failed: {str(e)}')


def delete_from_cloudinary(public_id):
    """Delete image from Cloudinary"""
    try:
        if not init_cloudinary():
            raise Exception('Cloudinary not configured')
        
        cloudinary.uploader.destroy(public_id)
        return True
    except Exception as e:
        print(f'Error deleting image from Cloudinary: {str(e)}')
        return False


def get_image_dimensions(file_obj):
    """Get image dimensions (requires PIL)"""
    try:
        from PIL import Image
        file_obj.seek(0)
        img = Image.open(file_obj)
        width, height = img.size
        file_obj.seek(0)
        return width, height
    except Exception as e:
        print(f'Error getting image dimensions: {str(e)}')
        return None, None


def get_cloudinary_url(public_id, width=None, height=None, quality=None):
    """Generate Cloudinary URL with transformations"""
    try:
        if not init_cloudinary():
            return None
        
        transformations = []
        if width or height:
            transform = {}
            if width:
                transform['width'] = width
            if height:
                transform['height'] = height
            transform['crop'] = 'limit'
            transformations.append(transform)
        
        if quality:
            transformations.append({'quality': quality})
        
        if transformations:
            url = cloudinary.CloudinaryResource(public_id).build_url(
                transformation=transformations
            )
        else:
            url = cloudinary.CloudinaryResource(public_id).build_url()
        
        return url
    except Exception as e:
        print(f'Error generating Cloudinary URL: {str(e)}')
        return None


def generate_thumbnail_url(public_id, width=300, height=300):
    """Generate thumbnail URL"""
    return get_cloudinary_url(
        public_id,
        width=width,
        height=height,
        quality=80
    )
