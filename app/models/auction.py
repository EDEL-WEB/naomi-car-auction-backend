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
    reserve_price = db.Column(db.Float, nullable=True)  # Hidden minimum price
    reserve_met = db.Column(db.Boolean, default=False)  # Has reserve been met
    buy_now_price = db.Column(db.Float, nullable=True)  # Instant purchase price
    brand = db.Column(db.String(100), nullable=False, index=True)
    car_model = db.Column(db.String(100), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False, index=True)
    vin = db.Column(db.String(17), nullable=True, index=True)  # Vehicle VIN
    video_url = db.Column(db.String(500), nullable=True)  # Video URL
    status = db.Column(db.String(20), default='active', index=True)  # active, closed, sold
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    view_count = db.Column(db.Integer, default=0)  # Track views
    watch_count = db.Column(db.Integer, default=0)  # Track watchers
    auto_extend = db.Column(db.Boolean, default=True)  # Auto-extend on last-minute bids
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    ends_at = db.Column(db.DateTime, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bids = db.relationship('Bid', backref='auction', lazy='dynamic', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='auction', lazy='dynamic', cascade='all, delete-orphan')
    car_spec = db.relationship('CarSpecification', backref='auction', uselist=False, cascade='all, delete-orphan')
    images = db.relationship('CarImage', backref='auction', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('AuctionComment', backref='auction', lazy='dynamic', cascade='all, delete-orphan')
    watchers = db.relationship('Watchlist', backref='auction', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_seller=False, include_images=False, include_reserve=False):
        """Convert auction to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'starting_price': self.starting_price,
            'current_price': self.current_price,
            'reserve_met': self.reserve_met,
            'has_reserve': self.reserve_price is not None,
            'buy_now_price': self.buy_now_price,
            'brand': self.brand,
            'car_model': self.car_model,
            'year': self.year,
            'vin': self.vin,
            'video_url': self.video_url,
            'status': self.status,
            'seller_id': self.seller_id,
            'view_count': self.view_count,
            'watch_count': self.watch_count,
            'created_at': self.created_at.isoformat(),
            'ends_at': self.ends_at.isoformat(),
            'bid_count': self.bids.count(),
            'comment_count': self.comments.count(),
            'is_active': self.status == 'active'
        }
        
        if include_reserve:
            data['reserve_price'] = self.reserve_price
        
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
