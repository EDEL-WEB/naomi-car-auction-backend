from flask import Blueprint, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from sqlalchemy.orm import joinedload
from app import db, limiter
from app.models.auction import Auction
from app.models.user import User
from app.models.car_specification import CarSpecification
from app.utils.validators import validate_auction_input, error_response, success_response
from datetime import datetime

auctions_bp = Blueprint('auctions', __name__)


@auctions_bp.route('', methods=['GET'])
def get_auctions():
    """Get all auctions with optional filtering"""
    try:
        # Get query parameters
        brand = request.args.get('brand')
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')
        status = request.args.get('status', 'active')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)  # Cap at 100
        image = request.args.get('image')
        
        # Fix N+1 query by eager loading seller
        query = Auction.query.options(joinedload(Auction.seller))
        
        # Apply filters
        if brand:
            query = query.filter_by(brand=brand)
        if status:
            query = query.filter_by(status=status)
        if min_price:
            try:
                query = query.filter(Auction.current_price >= float(min_price))
            except ValueError:
                return error_response('Invalid min_price', 400)
        if max_price:
            try:
                query = query.filter(Auction.current_price <= float(max_price))
            except ValueError:
                return error_response('Invalid max_price', 400)
        
        # Paginate results
        paginated = query.order_by(Auction.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        auctions = [auction.to_dict(include_seller=True) for auction in paginated.items]
        
        return success_response({
            'auctions': auctions,
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page
        }, 'Auctions retrieved successfully')
    
    except Exception as e:
        return error_response(f'Error retrieving auctions: {str(e)}', 500)


@auctions_bp.route('/<int:auction_id>', methods=['GET'])
def get_auction(auction_id):
    """Get a specific auction"""
    try:
        # Fix N+1 query by eager loading relationships
        auction = Auction.query.options(
            joinedload(Auction.seller),
            joinedload(Auction.car_spec),
            joinedload(Auction.images)
        ).get(auction_id)
        
        if not auction:
            return error_response('Auction not found', 404)
        
        auction_data = auction.to_dict(include_seller=True, include_images=True)
        
        # Include car specifications
        if auction.car_spec:
            auction_data['car_specification'] = auction.car_spec.to_dict()
        
        # Include recent bids with user info (fix N+1)
        from app.models.bid import Bid
        from app.models.user import User
        recent_bids = db.session.query(Bid).options(
            joinedload(Bid.bidder)
        ).filter_by(auction_id=auction_id).order_by(Bid.timestamp.desc()).limit(10).all()
        auction_data['recent_bids'] = [bid.to_dict(include_user=True) for bid in recent_bids]
        
        return success_response(auction_data, 'Auction retrieved successfully')
    
    except Exception as e:
        return error_response(f'Error retrieving auction: {str(e)}', 500)


@auctions_bp.route('', methods=['POST'])
@limiter.limit("10 per hour")
def create_auction():
    """Create a new auction"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        data = request.get_json()
        
        if not data:
            return error_response('No data provided', 400)
        
        # Validate input
        errors = validate_auction_input(data)
        if errors:
            return error_response(', '.join(errors), 400)
        
        # Create auction
        auction = Auction(
            title=data['title'],
            description=data['description'],
            starting_price=float(data['starting_price']),
            current_price=float(data['starting_price']),
            brand=data['brand'],
            car_model=data['car_model'],
            year=int(data['year']),
            seller_id=user_id,
            ends_at=datetime.fromisoformat(data['ends_at'].replace('Z', '+00:00'))
        )
        
        db.session.add(auction)
        db.session.flush()
        
        # Add car specification if provided
        if data.get('car_specification'):
            spec_data = data['car_specification']
            car_spec = CarSpecification(
                auction_id=auction.id,
                brand=spec_data.get('brand', data['brand']),
                model=spec_data.get('model', data['car_model']),
                year=spec_data.get('year', data['year']),
                mileage=spec_data.get('mileage', 0),
                condition=spec_data.get('condition', 'unknown'),
                fuel_type=spec_data.get('fuel_type'),
                transmission=spec_data.get('transmission'),
                color=spec_data.get('color'),
                engine=spec_data.get('engine'),
                features=spec_data.get('features', [])
            )
            db.session.add(car_spec)
        
        db.session.commit()
        
        return success_response(auction.to_dict(), 'Auction created successfully', 201)
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error creating auction: {str(e)}', 500)


@auctions_bp.route('/<int:auction_id>', methods=['PUT'])
def update_auction(auction_id):
    """Update an auction"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        auction = Auction.query.get(auction_id)
        
        if not auction:
            return error_response('Auction not found', 404)
        
        if auction.seller_id != user_id:
            return error_response('Unauthorized to update this auction', 403)
        
        data = request.get_json()
        
        if not data:
            return error_response('No data provided', 400)
        
        # Update fields
        if 'title' in data:
            auction.title = data['title']
        if 'description' in data:
            auction.description = data['description']
        if 'status' in data:
            auction.status = data['status']
        
        db.session.commit()
        
        return success_response(auction.to_dict(), 'Auction updated successfully')
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error updating auction: {str(e)}', 500)


@auctions_bp.route('/<int:auction_id>', methods=['DELETE'])
def delete_auction(auction_id):
    """Delete an auction"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        auction = Auction.query.get(auction_id)
        
        if not auction:
            return error_response('Auction not found', 404)
        
        if auction.seller_id != user_id:
            return error_response('Unauthorized to delete this auction', 403)
        
        db.session.delete(auction)
        db.session.commit()
        
        return success_response(None, 'Auction deleted successfully')
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error deleting auction: {str(e)}', 500)


@auctions_bp.route('/search', methods=['GET'])
def search_auctions():
    """Search auctions by title or description"""
    try:
        query_str = request.args.get('q', '')
        
        if not query_str:
            return error_response('Search query required', 400)
        
        auctions = Auction.query.filter(
            db.or_(
                Auction.title.ilike(f'%{query_str}%'),
                Auction.description.ilike(f'%{query_str}%'),
                Auction.brand.ilike(f'%{query_str}%')
            )
        ).filter_by(status='active').all()
        
        return success_response(
            [auction.to_dict() for auction in auctions],
            'Search completed successfully'
        )
    
    except Exception as e:
        return error_response(f'Error searching auctions: {str(e)}', 500)
