from app import db


class CarSpecification(db.Model):
    """Car specification model with detailed information"""
    __tablename__ = 'car_specifications'
    
    id = db.Column(db.Integer, primary_key=True)
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.id'), nullable=False, unique=True, index=True)
    brand = db.Column(db.String(100), nullable=False, index=True)
    model = db.Column(db.String(100), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False, index=True)
    mileage = db.Column(db.Float, nullable=False)
    condition = db.Column(db.String(50), nullable=False)  # excellent, good, fair, poor
    fuel_type = db.Column(db.String(50), nullable=True)
    transmission = db.Column(db.String(50), nullable=True)
    color = db.Column(db.String(50), nullable=True)
    engine = db.Column(db.String(100), nullable=True)
    features = db.Column(db.JSON, nullable=True, default=[])
    
    def to_dict(self):
        """Convert car specification to dictionary"""
        return {
            'id': self.id,
            'auction_id': self.auction_id,
            'brand': self.brand,
            'model': self.model,
            'year': self.year,
            'mileage': self.mileage,
            'condition': self.condition,
            'fuel_type': self.fuel_type,
            'transmission': self.transmission,
            'color': self.color,
            'engine': self.engine,
            'features': self.features or []
        }
    
    def __repr__(self):
        return f'<CarSpec {self.year} {self.brand} {self.model}>'
