from app import db
from datetime import datetime


class Watchlist(db.Model):
    """User watchlist for auctions"""
    __tablename__ = 'watchlist'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.id'), nullable=False, index=True)
    notify_on_bid = db.Column(db.Boolean, default=True)
    notify_on_ending = db.Column(db.Boolean, default=True)
    notify_on_outbid = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('user_id', 'auction_id', name='unique_user_auction_watch'),
    )
    
    # Relationships
    user = db.relationship('User', backref='watchlist')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'auction_id': self.auction_id,
            'notify_on_bid': self.notify_on_bid,
            'notify_on_ending': self.notify_on_ending,
            'notify_on_outbid': self.notify_on_outbid,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Watchlist User {self.user_id} watching Auction {self.auction_id}>'
