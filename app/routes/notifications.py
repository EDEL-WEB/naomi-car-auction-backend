from flask import Blueprint, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app import db
from app.models.notification import Notification, NotificationPreference
from app.utils.notification_service import NotificationService
from app.utils.validators import error_response, success_response

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('', methods=['GET'])
def get_notifications():
    """Get user's notifications"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        query = Notification.query.filter_by(user_id=user_id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        paginated = query.order_by(Notification.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        notifications = [n.to_dict() for n in paginated.items]
        unread_count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
        
        return success_response({
            'notifications': notifications,
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page,
            'unread_count': unread_count
        }, 'Notifications retrieved successfully')
    
    except Exception as e:
        return error_response(f'Error retrieving notifications: {str(e)}', 500)


@notifications_bp.route('/unread-count', methods=['GET'])
def get_unread_count():
    """Get count of unread notifications"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        unread_count = NotificationService.get_unread_count(user_id)
        
        return success_response({
            'unread_count': unread_count
        }, 'Unread count retrieved successfully')
    
    except Exception as e:
        return error_response(f'Error retrieving unread count: {str(e)}', 500)


@notifications_bp.route('/<int:notification_id>', methods=['GET'])
def get_notification(notification_id):
    """Get specific notification"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        notification = Notification.query.get(notification_id)
        
        if not notification:
            return error_response('Notification not found', 404)
        
        if notification.user_id != user_id:
            return error_response('Unauthorized to view this notification', 403)
        
        return success_response(notification.to_dict(), 'Notification retrieved successfully')
    
    except Exception as e:
        return error_response(f'Error retrieving notification: {str(e)}', 500)


@notifications_bp.route('/<int:notification_id>/read', methods=['PUT'])
def mark_as_read(notification_id):
    """Mark notification as read"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        notification = Notification.query.get(notification_id)
        
        if not notification:
            return error_response('Notification not found', 404)
        
        if notification.user_id != user_id:
            return error_response('Unauthorized to update this notification', 403)
        
        NotificationService.mark_as_read(notification_id)
        
        return success_response(notification.to_dict(), 'Notification marked as read')
    
    except Exception as e:
        return error_response(f'Error marking notification as read: {str(e)}', 500)


@notifications_bp.route('/mark-all-read', methods=['PUT'])
def mark_all_read():
    """Mark all notifications as read"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        NotificationService.mark_all_as_read(user_id)
        
        return success_response(None, 'All notifications marked as read')
    
    except Exception as e:
        return error_response(f'Error marking all notifications as read: {str(e)}', 500)


@notifications_bp.route('/<int:notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    """Delete a notification"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        notification = Notification.query.get(notification_id)
        
        if not notification:
            return error_response('Notification not found', 404)
        
        if notification.user_id != user_id:
            return error_response('Unauthorized to delete this notification', 403)
        
        NotificationService.delete_notification(notification_id)
        
        return success_response(None, 'Notification deleted successfully')
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error deleting notification: {str(e)}', 500)


@notifications_bp.route('/preferences', methods=['GET'])
def get_preferences():
    """Get user's notification preferences"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        preference = NotificationService.create_or_get_preference(user_id)
        
        return success_response(preference.to_dict(), 'Preferences retrieved successfully')
    
    except Exception as e:
        return error_response(f'Error retrieving preferences: {str(e)}', 500)


@notifications_bp.route('/preferences', methods=['PUT'])
def update_preferences():
    """Update user's notification preferences"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        preference = NotificationService.create_or_get_preference(user_id)
        data = request.get_json()
        
        if not data:
            return error_response('No data provided', 400)
        
        # Update preference fields
        if 'image_uploads' in data:
            preference.image_uploads = data['image_uploads']
        if 'auction_updates' in data:
            preference.auction_updates = data['auction_updates']
        if 'bid_notifications' in data:
            preference.bid_notifications = data['bid_notifications']
        if 'auction_ending' in data:
            preference.auction_ending = data['auction_ending']
        if 'email_notifications' in data:
            preference.email_notifications = data['email_notifications']
        
        db.session.commit()
        
        return success_response(preference.to_dict(), 'Preferences updated successfully')
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error updating preferences: {str(e)}', 500)
