from app import db
from datetime import datetime


class CarImage(db.Model):
    """Car image model for storing auction car images"""
    __tablename__ = 'car_images'
    
    id = db.Column(db.Integer, primary_key=True)
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.id'), nullable=False, index=True)
    image_url = db.Column(db.String(500), nullable=False)  # Cloudinary secure URL
    cloudinary_public_id = db.Column(db.String(500), nullable=True, unique=True, index=True)  # Cloudinary public ID
    image_title = db.Column(db.String(200), nullable=True)
    is_primary = db.Column(db.Boolean, default=False, index=True)
    display_order = db.Column(db.Integer, default=0)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Indexes for common queries
    __table_args__ = (
        db.Index('idx_auction_primary', 'auction_id', 'is_primary'),
    )
    
    def to_dict(self):
        """Convert car image to dictionary"""
        return {
            'id': self.id,
            'auction_id': self.auction_id,
            'image_url': self.image_url,
            'cloudinary_public_id': self.cloudinary_public_id,
            'image_title': self.image_title,
            'is_primary': self.is_primary,
            'display_order': self.display_order,
            'uploaded_at': self.uploaded_at.isoformat()
        }
    
    def __repr__(self):
        return f'<CarImage {self.id} - Auction {self.auction_id}>'
