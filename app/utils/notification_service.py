"""Notification service for managing and sending notifications"""

from app import db, socketio
from app.models.notification import Notification, NotificationPreference
from datetime import datetime


class NotificationService:
    """Service for creating and managing notifications"""
    
    @staticmethod
    def create_notification(user_id, notification_type, title, message, 
                          related_auction_id=None, related_image_id=None):
        """
        Create a new notification
        
        Args:
            user_id: User to notify
            notification_type: Type of notification (image_uploaded, bid_placed, etc.)
            title: Notification title
            message: Notification message
            related_auction_id: Optional auction ID
            related_image_id: Optional image ID
        
        Returns:
            Notification object
        """
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            related_auction_id=related_auction_id,
            related_image_id=related_image_id
        )
        
        db.session.add(notification)
        db.session.commit()
        
        return notification
    
    @staticmethod
    def notify_image_uploaded(user_id, auction_id, image_id, image_title):
        """Notify when an image is uploaded"""
        title = "New Image Uploaded"
        message = f"Image '{image_title}' was uploaded to your auction"
        
        notification = NotificationService.create_notification(
            user_id=user_id,
            notification_type='image_uploaded',
            title=title,
            message=message,
            related_auction_id=auction_id,
            related_image_id=image_id
        )
        
        # Emit real-time notification
        socketio.emit('notification', notification.to_dict(), room=f'user_{user_id}')
        
        return notification
    
    @staticmethod
    def notify_bid_placed(seller_id, auction_id, bidder_username, bid_amount):
        """Notify seller when a bid is placed"""
        title = "New Bid Received"
        message = f"{bidder_username} placed a bid of ${bid_amount:,.2f}"
        
        notification = NotificationService.create_notification(
            user_id=seller_id,
            notification_type='bid_placed',
            title=title,
            message=message,
            related_auction_id=auction_id
        )
        
        socketio.emit('notification', notification.to_dict(), room=f'user_{seller_id}')
        
        return notification
    
    @staticmethod
    def notify_outbid(user_id, auction_id, auction_title, current_price):
        """Notify user they've been outbid"""
        title = "You've Been Outbid"
        message = f"Someone placed a higher bid on {auction_title}. Current price: ${current_price:,.2f}"
        
        notification = NotificationService.create_notification(
            user_id=user_id,
            notification_type='outbid',
            title=title,
            message=message,
            related_auction_id=auction_id
        )
        
        socketio.emit('notification', notification.to_dict(), room=f'user_{user_id}')
        
        return notification
    
    @staticmethod
    def notify_auction_ending(user_id, auction_id, auction_title, time_remaining):
        """Notify when an auction is ending soon"""
        title = "Auction Ending Soon"
        message = f"{auction_title} is ending in {time_remaining}"
        
        notification = NotificationService.create_notification(
            user_id=user_id,
            notification_type='auction_ending',
            title=title,
            message=message,
            related_auction_id=auction_id
        )
        
        socketio.emit('notification', notification.to_dict(), room=f'user_{user_id}')
        
        return notification
    
    @staticmethod
    def notify_auction_won(user_id, auction_id, auction_title, final_price):
        """Notify user they won an auction"""
        title = "Congratulations! You Won!"
        message = f"You won the auction for {auction_title} with a final bid of ${final_price:,.2f}"
        
        notification = NotificationService.create_notification(
            user_id=user_id,
            notification_type='auction_won',
            title=title,
            message=message,
            related_auction_id=auction_id
        )
        
        socketio.emit('notification', notification.to_dict(), room=f'user_{user_id}')
        
        return notification
    
    @staticmethod
    def notify_auction_ended_no_winner(seller_id, auction_id, auction_title):
        """Notify seller when auction ends with no bids"""
        title = "Auction Ended - No Bids"
        message = f"Your auction for {auction_title} ended without any bids"
        
        notification = NotificationService.create_notification(
            user_id=seller_id,
            notification_type='auction_no_bids',
            title=title,
            message=message,
            related_auction_id=auction_id
        )
        
        socketio.emit('notification', notification.to_dict(), room=f'user_{seller_id}')
        
        return notification
    
    @staticmethod
    def mark_as_read(notification_id):
        """Mark notification as read"""
        notification = Notification.query.get(notification_id)
        if notification:
            notification.is_read = True
            notification.updated_at = datetime.utcnow()
            db.session.commit()
            return notification
        return None
    
    @staticmethod
    def mark_all_as_read(user_id):
        """Mark all notifications as read for a user"""
        Notification.query.filter_by(user_id=user_id, is_read=False).update(
            {Notification.is_read: True, Notification.updated_at: datetime.utcnow()},
            synchronize_session=False
        )
        db.session.commit()
    
    @staticmethod
    def delete_notification(notification_id):
        """Delete a notification"""
        notification = Notification.query.get(notification_id)
        if notification:
            db.session.delete(notification)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def get_user_notifications(user_id, unread_only=False, limit=20):
        """Get user notifications"""
        query = Notification.query.filter_by(user_id=user_id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        return query.order_by(Notification.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_unread_count(user_id):
        """Get count of unread notifications"""
        return Notification.query.filter_by(user_id=user_id, is_read=False).count()
    
    @staticmethod
    def create_or_get_preference(user_id):
        """Create or get notification preferences for user"""
        preference = NotificationPreference.query.filter_by(user_id=user_id).first()
        
        if not preference:
            preference = NotificationPreference(user_id=user_id)
            db.session.add(preference)
            db.session.commit()
        
        return preference
