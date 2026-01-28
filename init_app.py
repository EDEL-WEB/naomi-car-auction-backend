#!/usr/bin/env python
"""Database setup and initialization script"""

import os
import sys
from app import create_app, db
from app.models.user import User
from app.models.auction import Auction
from app.models.bid import Bid
from app.models.favorite import Favorite
from app.models.car_specification import CarSpecification

# Create app context
app = create_app('development')

with app.app_context():
    print("Creating database tables...")
    db.create_all()
    print("✓ Database tables created successfully!")
    
    # Check if tables exist
    print("\nVerifying tables:")
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    
    required_tables = ['users', 'auctions', 'bids', 'favorites', 'car_specifications']
    for table in required_tables:
        if table in tables:
            print(f"  ✓ {table}")
        else:
            print(f"  ✗ {table} (missing)")
    
    print("\n✓ Database initialization complete!")
    print("\nYou can now run: python run.py")
