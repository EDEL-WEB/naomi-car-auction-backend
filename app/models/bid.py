from app import db
from datetime import datetime


class Bid(db.Model):
    """Bid model for auction bids"""
    __tablename__ = 'bids'
    
    id = db.Column(db.Integer, primary_key=True)
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    bid_amount = db.Column(db.Float, nullable=False)
    max_bid = db.Column(db.Float, nullable=True)  # For proxy bidding
    is_proxy = db.Column(db.Boolean, default=False)  # Is this a proxy bid
    is_retracted = db.Column(db.Boolean, default=False)  # Bid retraction
    retraction_reason = db.Column(db.String(500), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Indexes for common queries
    __table_args__ = (
        db.Index('idx_auction_user', 'auction_id', 'user_id'),
    )
    
    def to_dict(self, include_user=False):
        """Convert bid to dictionary"""
        data = {
            'id': self.id,
            'auction_id': self.auction_id,
            'user_id': self.user_id,
            'bid_amount': self.bid_amount,
            'is_proxy': self.is_proxy,
            'is_retracted': self.is_retracted,
            'timestamp': self.timestamp.isoformat()
        }
        
        if include_user:
            data['user'] = {
                'id': self.bidder.id,
                'username': self.bidder.username,
                'email': self.bidder.email
            }
        
        return data
    
    def __repr__(self):
        return f'<Bid {self.bid_amount} on Auction {self.auction_id}>'
