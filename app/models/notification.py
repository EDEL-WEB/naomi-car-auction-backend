from app import db
from datetime import datetime


class Notification(db.Model):
    """Notification model for user notifications"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False, index=True)  # image_uploaded, auction_ending, bid_placed, etc.
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    related_auction_id = db.Column(db.Integer, db.ForeignKey('auctions.id'), nullable=True, index=True)
    related_image_id = db.Column(db.Integer, db.ForeignKey('car_images.id'), nullable=True)
    is_read = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='notifications')
    auction = db.relationship('Auction')
    image = db.relationship('CarImage')
    
    def to_dict(self):
        """Convert notification to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'related_auction_id': self.related_auction_id,
            'related_image_id': self.related_image_id,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Notification {self.type} - {self.title}>'


class NotificationPreference(db.Model):
    """User notification preferences"""
    __tablename__ = 'notification_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True, index=True)
    image_uploads = db.Column(db.Boolean, default=True)
    auction_updates = db.Column(db.Boolean, default=True)
    bid_notifications = db.Column(db.Boolean, default=True)
    auction_ending = db.Column(db.Boolean, default=True)
    email_notifications = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='notification_preference', uselist=False)
    
    def to_dict(self):
        """Convert preference to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'image_uploads': self.image_uploads,
            'auction_updates': self.auction_updates,
            'bid_notifications': self.bid_notifications,
            'auction_ending': self.auction_ending,
            'email_notifications': self.email_notifications
        }
    
    def __repr__(self):
        return f'<NotificationPreference User {self.user_id}>'
