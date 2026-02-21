from app import db
from datetime import datetime


class SellerRating(db.Model):
    """Seller ratings and reviews"""
    __tablename__ = 'seller_ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.id'), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review = db.Column(db.Text, nullable=True)
    communication = db.Column(db.Integer, nullable=True)  # 1-5
    accuracy = db.Column(db.Integer, nullable=True)  # 1-5
    shipping = db.Column(db.Integer, nullable=True)  # 1-5
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Unique constraint - one rating per buyer per auction
    __table_args__ = (
        db.UniqueConstraint('buyer_id', 'auction_id', name='unique_buyer_auction_rating'),
    )
    
    # Relationships
    seller = db.relationship('User', foreign_keys=[seller_id], backref='received_ratings')
    buyer = db.relationship('User', foreign_keys=[buyer_id], backref='given_ratings')
    
    def to_dict(self, include_buyer=True):
        data = {
            'id': self.id,
            'seller_id': self.seller_id,
            'buyer_id': self.buyer_id,
            'auction_id': self.auction_id,
            'rating': self.rating,
            'review': self.review,
            'communication': self.communication,
            'accuracy': self.accuracy,
            'shipping': self.shipping,
            'created_at': self.created_at.isoformat()
        }
        
        if include_buyer:
            data['buyer'] = {
                'id': self.buyer.id,
                'username': self.buyer.username
            }
        
        return data
    
    def __repr__(self):
        return f'<SellerRating {self.rating} stars for Seller {self.seller_id}>'
