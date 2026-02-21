from app import db
from datetime import datetime


class AuctionComment(db.Model):
    """Comments/Q&A on auctions"""
    __tablename__ = 'auction_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    comment = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('auction_comments.id'), nullable=True)  # For replies
    is_seller_response = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='comments')
    replies = db.relationship('AuctionComment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    
    def to_dict(self, include_user=True, include_replies=False):
        data = {
            'id': self.id,
            'auction_id': self.auction_id,
            'user_id': self.user_id,
            'comment': self.comment,
            'parent_id': self.parent_id,
            'is_seller_response': self.is_seller_response,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_user:
            data['user'] = {
                'id': self.user.id,
                'username': self.user.username
            }
        
        if include_replies:
            data['replies'] = [reply.to_dict(include_replies=False) for reply in self.replies.all()]
        
        return data
    
    def __repr__(self):
        return f'<AuctionComment {self.id} on Auction {self.auction_id}>'
