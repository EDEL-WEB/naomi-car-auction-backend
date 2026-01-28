from app import db
from datetime import datetime


class Auction(db.Model):
    """Auction model for car listings"""
    __tablename__ = 'auctions'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    starting_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    brand = db.Column(db.String(100), nullable=False, index=True)
    car_model = db.Column(db.String(100), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False, index=True)
    status = db.Column(db.String(20), default='active', index=True)  # active, closed, sold
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    ends_at = db.Column(db.DateTime, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bids = db.relationship('Bid', backref='auction', lazy='dynamic', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='auction', lazy='dynamic', cascade='all, delete-orphan')
    car_spec = db.relationship('CarSpecification', backref='auction', uselist=False, cascade='all, delete-orphan')
    images = db.relationship('CarImage', backref='auction', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_seller=False, include_images=False):
        """Convert auction to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'starting_price': self.starting_price,
            'current_price': self.current_price,
            'brand': self.brand,
            'car_model': self.car_model,
            'year': self.year,
            'status': self.status,
            'seller_id': self.seller_id,
            'created_at': self.created_at.isoformat(),
            'ends_at': self.ends_at.isoformat(),
            'bid_count': self.bids.count(),
            'is_active': self.status == 'active'
        }
        
        if include_seller:
            data['seller'] = self.seller.to_dict()
        
        if include_images:
            primary_image = self.images.filter_by(is_primary=True).first()
            all_images = self.images.order_by('display_order').all()
            data['primary_image'] = primary_image.to_dict() if primary_image else None
            data['images'] = [img.to_dict() for img in all_images]
        
        return data
    
    def __repr__(self):
        return f'<Auction {self.title}>'
