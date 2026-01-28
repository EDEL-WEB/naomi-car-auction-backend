#!/usr/bin/env python
"""Sample data loader for development"""

from app import create_app, db
from app.models.user import User
from app.models.auction import Auction
from app.models.car_specification import CarSpecification
from app.models.car_image import CarImage
from datetime import datetime, timedelta

app = create_app('development')

def load_sample_data():
    """Load sample data for testing"""
    
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        db.session.query(Auction).delete()
        db.session.query(User).delete()
        db.session.commit()
        
        # Create sample users
        print("Creating sample users...")
        users = []
        usernames = ['john_doe', 'jane_smith', 'collector_mike', 'luxury_buyer']
        
        for i, username in enumerate(usernames):
            user = User(
                username=username,
                email=f'{username}@example.com',
                phone=f'555-{1000+i:04d}',
                address=f'{100+i} Luxury Lane, Beverly Hills, CA'
            )
            user.set_password('password123')
            users.append(user)
            db.session.add(user)
        
        db.session.commit()
        print(f"✓ Created {len(users)} users")
        
        # Create sample auctions
        print("Creating sample auctions...")
        auctions_data = [
            {
                'title': '2019 Ferrari 488 GTB - Excellent Condition',
                'description': 'Stunning red Ferrari 488 GTB with all maintenance records. Low mileage, pristine interior.',
                'starting_price': 250000,
                'brand': 'Ferrari',
                'car_model': '488 GTB',
                'year': 2019,
                'seller_id': users[0].id,
                'spec': {
                    'mileage': 12500,
                    'condition': 'excellent',
                    'fuel_type': 'Gasoline',
                    'transmission': 'Automatic',
                    'color': 'Rosso Corsa',
                    'engine': 'V8 3.9L Turbo',
                    'features': ['Carbon Fiber Trim', 'Premium Sound System', 'Leather Interior']
                }
            },
            {
                'title': '2020 Lamborghini Huracán Evo - Like New',
                'description': 'Nearly new Lamborghini Huracán Evo with minimal miles. Garaged since purchase.',
                'starting_price': 350000,
                'brand': 'Lamborghini',
                'car_model': 'Huracán Evo',
                'year': 2020,
                'seller_id': users[1].id,
                'spec': {
                    'mileage': 2300,
                    'condition': 'excellent',
                    'fuel_type': 'Gasoline',
                    'transmission': 'Automatic',
                    'color': 'Pearl White',
                    'engine': 'V10 5.2L NA',
                    'features': ['Glass Engine Cover', 'Navigation System', 'Dual Climate Control']
                }
            },
            {
                'title': '2018 Porsche 911 Turbo S - Black on Black',
                'description': 'Black beauty with every option. Heated leather seats, panoramic roof, sport exhaust.',
                'starting_price': 150000,
                'brand': 'Porsche',
                'car_model': '911 Turbo S',
                'year': 2018,
                'seller_id': users[2].id,
                'spec': {
                    'mileage': 28900,
                    'condition': 'good',
                    'fuel_type': 'Gasoline',
                    'transmission': 'Automatic',
                    'color': 'Black',
                    'engine': 'Flat 6 3.8L Turbo',
                    'features': ['Ceramic Brakes', 'Heated Seats', 'Panoramic Sunroof']
                }
            },
            {
                'title': '2021 Bentley Continental GT - Mulliner Edition',
                'description': 'Exclusive Mulliner edition with bespoke leather. Full Bentley service history.',
                'starting_price': 200000,
                'brand': 'Bentley',
                'car_model': 'Continental GT',
                'year': 2021,
                'seller_id': users[0].id,
                'spec': {
                    'mileage': 8100,
                    'condition': 'excellent',
                    'fuel_type': 'Gasoline',
                    'transmission': 'Automatic',
                    'color': 'Midnight Sapphire',
                    'engine': 'W12 6.0L Twin-Turbo',
                    'features': ['Mulliner Package', 'Custom Leather', 'Rotating Display']
                }
            },
            {
                'title': '2017 McLaren 570S - Orange Metallic',
                'description': 'Vibrant orange McLaren with incredible performance history. Track certified.',
                'starting_price': 170000,
                'brand': 'McLaren',
                'car_model': '570S',
                'year': 2017,
                'seller_id': users[3].id,
                'spec': {
                    'mileage': 18700,
                    'condition': 'excellent',
                    'fuel_type': 'Gasoline',
                    'transmission': 'Automatic',
                    'color': 'Papaya Spark',
                    'engine': 'V8 3.8L Twin-Turbo',
                    'features': ['Carbon Fiber Package', 'Track Telemetry', 'Racing Seat']
                }
            }
        ]
        
        for i, data in enumerate(auctions_data):
            spec_data = data.pop('spec')
            
            # Set end time to 7 days from now
            ends_at = datetime.utcnow() + timedelta(days=7)
            
            auction = Auction(
                title=data['title'],
                description=data['description'],
                starting_price=data['starting_price'],
                current_price=data['starting_price'],
                brand=data['brand'],
                car_model=data['car_model'],
                year=data['year'],
                seller_id=data['seller_id'],
                ends_at=ends_at,
                status='active'
            )
            
            db.session.add(auction)
            db.session.flush()
            
            # Add car specification
            car_spec = CarSpecification(
                auction_id=auction.id,
                brand=spec_data.get('brand', data['brand']),
                model=spec_data.get('model', data['car_model']),
                year=spec_data.get('year', data['year']),
                mileage=spec_data['mileage'],
                condition=spec_data['condition'],
                fuel_type=spec_data.get('fuel_type'),
                transmission=spec_data.get('transmission'),
                color=spec_data.get('color'),
                engine=spec_data.get('engine'),
                features=spec_data.get('features', [])
            )
            db.session.add(car_spec)
        
        db.session.commit()
        print(f"✓ Created {len(auctions_data)} auctions with specifications")
        
        # Add sample images for each auction
        print("Adding sample images...")
        image_samples = [
            [
                {'title': 'Front View', 'primary': True, 'order': 0, 'url': '/uploads/sample_ferrari_front.jpg'},
                {'title': 'Side View', 'primary': False, 'order': 1, 'url': '/uploads/sample_ferrari_side.jpg'},
                {'title': 'Interior', 'primary': False, 'order': 2, 'url': '/uploads/sample_ferrari_interior.jpg'},
            ],
            [
                {'title': 'Front View', 'primary': True, 'order': 0, 'url': '/uploads/sample_lamborghini_front.jpg'},
                {'title': 'Side View', 'primary': False, 'order': 1, 'url': '/uploads/sample_lamborghini_side.jpg'},
            ],
            [
                {'title': 'Front View', 'primary': True, 'order': 0, 'url': '/uploads/sample_porsche_front.jpg'},
                {'title': 'Rear View', 'primary': False, 'order': 1, 'url': '/uploads/sample_porsche_rear.jpg'},
            ],
            [
                {'title': 'Front View', 'primary': True, 'order': 0, 'url': '/uploads/sample_bentley_front.jpg'},
                {'title': 'Interior', 'primary': False, 'order': 1, 'url': '/uploads/sample_bentley_interior.jpg'},
            ],
            [
                {'title': 'Front View', 'primary': True, 'order': 0, 'url': '/uploads/sample_mclaren_front.jpg'},
                {'title': 'Rear View', 'primary': False, 'order': 1, 'url': '/uploads/sample_mclaren_rear.jpg'},
                {'title': 'Top View', 'primary': False, 'order': 2, 'url': '/uploads/sample_mclaren_top.jpg'},
            ]
        ]
        
        auctions = Auction.query.all()
        for auction, images in zip(auctions, image_samples):
            for img_data in images:
                car_image = CarImage(
                    auction_id=auction.id,
                    image_url=img_data['url'],
                    image_title=img_data['title'],
                    is_primary=img_data['primary'],
                    display_order=img_data['order']
                )
                db.session.add(car_image)
        
        db.session.commit()
        print(f"✓ Added sample images to auctions")
        
        print("\n✓ Sample data loaded successfully!")
        print("\nLogin credentials:")
        for user in users:
            print(f"  - username: {user.username}, password: password123")

if __name__ == '__main__':
    load_sample_data()
