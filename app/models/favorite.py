from app import db
from datetime import datetime


class Favorite(db.Model):
    """Favorite model for user's favorite auctions"""
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Unique constraint to prevent duplicates
    __table_args__ = (
        db.UniqueConstraint('user_id', 'auction_id', name='uq_user_auction_favorite'),
    )
    
    def to_dict(self):
        """Convert favorite to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'auction_id': self.auction_id,
            'auction': self.auction.to_dict(),
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Favorite User {self.user_id} - Auction {self.auction_id}>'
