from flask import Blueprint, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app import db, socketio
from app.models.auction import Auction
from app.models.car_image import CarImage
from app.utils.validators import error_response, success_response
from app.utils.cloudinary_utils import (
    upload_to_cloudinary, delete_from_cloudinary, 
    validate_image_file, get_thumbnail_url
)
from app.utils.notification_service import NotificationService
from datetime import datetime
import os

images_bp = Blueprint('images', __name__)


@images_bp.route('/auction/<int:auction_id>', methods=['GET'])
def get_auction_images(auction_id):
    """Get all images for an auction"""
    try:
        auction = Auction.query.get(auction_id)
        
        if not auction:
            return error_response('Auction not found', 404)
        
        images = auction.images.order_by(CarImage.display_order).all()
        
        return success_response({
            'auction_id': auction_id,
            'images': [img.to_dict() for img in images],
            'total': len(images)
        }, 'Auction images retrieved successfully')
    
    except Exception as e:
        return error_response(f'Error retrieving images: {str(e)}', 500)


@images_bp.route('/auction/<int:auction_id>', methods=['POST'])
def upload_image(auction_id):
    """Upload an image for an auction using Cloudinary"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        auction = Auction.query.get(auction_id)
        
        if not auction:
            return error_response('Auction not found', 404)
        
        if auction.seller_id != user_id:
            return error_response('Unauthorized to upload images for this auction', 403)
        
        # Check if file is in request
        if 'image' not in request.files:
            return error_response('No image file provided', 400)
        
        file = request.files['image']
        
        if file.filename == '':
            return error_response('No image file selected', 400)
        
        # Validate file
        errors = validate_image_file(file, file.filename)
        if errors:
            return error_response(', '.join(errors), 400)
        
        try:
            # Upload to Cloudinary
            cloudinary_result = upload_to_cloudinary(file, auction_id)
            
            # Create image record
            image_title = request.form.get('image_title', file.filename)
            is_primary = request.form.get('is_primary', 'false').lower() == 'true'
            display_order = request.form.get('display_order', auction.images.count(), type=int)
            
            # If this is the primary image, unset other primary images
            if is_primary:
                CarImage.query.filter_by(auction_id=auction_id, is_primary=True).update({CarImage.is_primary: False})
            
            car_image = CarImage(
                auction_id=auction_id,
                image_url=cloudinary_result['url'],
                cloudinary_public_id=cloudinary_result['public_id'],
                image_title=image_title,
                is_primary=is_primary,
                display_order=display_order
            )
            
            db.session.add(car_image)
            db.session.commit()
            
            # Send notification
            NotificationService.notify_image_uploaded(
                user_id=user_id,
                auction_id=auction_id,
                image_id=car_image.id,
                image_title=image_title
            )
            
            # Emit socket event
            socketio.emit('image_uploaded', {
                'auction_id': auction_id,
                'image': car_image.to_dict()
            }, room=f'auction_{auction_id}')
            
            return success_response(car_image.to_dict(), 'Image uploaded successfully', 201)
        
        except Exception as e:
            db.session.rollback()
            return error_response(f'Error uploading image: {str(e)}', 500)
    
    except Exception as e:
        return error_response(f'Error uploading image: {str(e)}', 500)


@images_bp.route('/<int:image_id>', methods=['GET'])
def get_image(image_id):
    """Get a specific image"""
    try:
        image = CarImage.query.get(image_id)
        
        if not image:
            return error_response('Image not found', 404)
        
        return success_response(image.to_dict(), 'Image retrieved successfully')
    
    except Exception as e:
        return error_response(f'Error retrieving image: {str(e)}', 500)


@images_bp.route('/<int:image_id>', methods=['PUT'])
def update_image(image_id):
    """Update image metadata"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        image = CarImage.query.get(image_id)
        
        if not image:
            return error_response('Image not found', 404)
        
        if image.auction.seller_id != user_id:
            return error_response('Unauthorized to update this image', 403)
        
        data = request.get_json()
        
        if not data:
            return error_response('No data provided', 400)
        
        # Update fields
        if 'image_title' in data:
            image.image_title = data['image_title']
        
        if 'is_primary' in data:
            is_primary = data['is_primary']
            if is_primary:
                # Unset other primary images
                CarImage.query.filter_by(
                    auction_id=image.auction_id,
                    is_primary=True
                ).update({CarImage.is_primary: False})
            image.is_primary = is_primary
        
        if 'display_order' in data:
            image.display_order = data['display_order']
        
        db.session.commit()
        
        return success_response(image.to_dict(), 'Image updated successfully')
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error updating image: {str(e)}', 500)


@images_bp.route('/<int:image_id>', methods=['DELETE'])
def delete_image(image_id):
    """Delete an image"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        image = CarImage.query.get(image_id)
        
        if not image:
            return error_response('Image not found', 404)
        
        if image.auction.seller_id != user_id:
            return error_response('Unauthorized to delete this image', 403)
        
        # Delete from Cloudinary
        if hasattr(image, 'cloudinary_public_id') and image.cloudinary_public_id:
            delete_from_cloudinary(image.cloudinary_public_id)
        
        db.session.delete(image)
        db.session.commit()
        
        # Emit socket event
        socketio.emit('image_deleted', {
            'auction_id': image.auction_id,
            'image_id': image_id
        }, room=f'auction_{image.auction_id}')
        
        return success_response(None, 'Image deleted successfully')
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error deleting image: {str(e)}', 500)


@images_bp.route('/auction/<int:auction_id>/primary', methods=['GET'])
def get_primary_image(auction_id):
    """Get the primary (cover) image for an auction"""
    try:
        auction = Auction.query.get(auction_id)
        
        if not auction:
            return error_response('Auction not found', 404)
        
        primary_image = auction.images.filter_by(is_primary=True).first()
        
        if not primary_image:
            # Return first image if no primary is set
            primary_image = auction.images.order_by(CarImage.display_order).first()
        
        if not primary_image:
            return error_response('No images found for this auction', 404)
        
        return success_response(primary_image.to_dict(), 'Primary image retrieved successfully')
    
    except Exception as e:
        return error_response(f'Error retrieving primary image: {str(e)}', 500)


@images_bp.route('/auction/<int:auction_id>/reorder', methods=['POST'])
def reorder_images(auction_id):
    """Reorder images for an auction"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        auction = Auction.query.get(auction_id)
        
        if not auction:
            return error_response('Auction not found', 404)
        
        if auction.seller_id != user_id:
            return error_response('Unauthorized to reorder images for this auction', 403)
        
        data = request.get_json()
        
        if not data or 'image_ids' not in data:
            return error_response('image_ids array is required', 400)
        
        image_ids = data['image_ids']
        
        # Validate all images belong to this auction
        for i, image_id in enumerate(image_ids):
            image = CarImage.query.get(image_id)
            if not image or image.auction_id != auction_id:
                return error_response(f'Invalid image ID: {image_id}', 400)
            image.display_order = i
        
        db.session.commit()
        
        images = auction.images.order_by(CarImage.display_order).all()
        
        # Emit socket event
        socketio.emit('images_reordered', {
            'auction_id': auction_id,
            'images': [img.to_dict() for img in images]
        }, room=f'auction_{auction_id}')
        
        return success_response(
            [img.to_dict() for img in images],
            'Images reordered successfully'
        )
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error reordering images: {str(e)}', 500)
