from flask import Blueprint, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app import db
from app.models.user import User
from app.models.auction import Auction
from app.models.bid import Bid
from app.utils.validators import validate_user_input, error_response, success_response

users_bp = Blueprint('users', __name__)


@users_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get current user's profile"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        user = User.query.get(user_id)
        
        if not user:
            return error_response('User not found', 404)
        
        return success_response(user.to_dict(), 'Profile retrieved successfully')
    
    except Exception as e:
        return error_response(f'Error retrieving profile: {str(e)}', 500)


@users_bp.route('/profile', methods=['PUT'])
def update_profile():
    """Update current user's profile"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        user = User.query.get(user_id)
        
        if not user:
            return error_response('User not found', 404)
        
        data = request.get_json()
        
        if not data:
            return error_response('No data provided', 400)
        
        # Validate input
        errors = validate_user_input(data)
        if errors:
            return error_response(', '.join(errors), 400)
        
        # Update fields
        if 'phone' in data:
            user.phone = data['phone']
        if 'address' in data:
            user.address = data['address']
        if 'email' in data:
            # Check if email is already in use
            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != user_id:
                return error_response('Email already in use', 409)
            user.email = data['email']
        
        db.session.commit()
        
        return success_response(user.to_dict(), 'Profile updated successfully')
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error updating profile: {str(e)}', 500)


@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a user's public profile"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return error_response('User not found', 404)
        
        return success_response(user.to_dict(), 'User retrieved successfully')
    
    except Exception as e:
        return error_response(f'Error retrieving user: {str(e)}', 500)


@users_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    """Get dashboard data for current user"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        user = User.query.get(user_id)
        
        if not user:
            return error_response('User not found', 404)
        
        # Get user's auctions
        auctions = Auction.query.filter_by(seller_id=user_id).all()
        
        # Get user's bids
        bids = Bid.query.filter_by(user_id=user_id).all()
        
        # Count active auctions
        active_auctions = Auction.query.filter_by(
            seller_id=user_id,
            status='active'
        ).count()
        
        # Get total spent on bids
        total_bid_amount = db.session.query(db.func.sum(Bid.bid_amount)).filter_by(
            user_id=user_id
        ).scalar() or 0
        
        # Get auctions where user is highest bidder
        from sqlalchemy import and_
        highest_bidder_auctions = []
        for auction in auctions:
            highest_bid = Bid.query.filter_by(auction_id=auction.id).order_by(
                Bid.bid_amount.desc()
            ).first()
            if highest_bid and highest_bid.user_id == user_id:
                highest_bidder_auctions.append(auction.to_dict())
        
        dashboard_data = {
            'user': user.to_dict(),
            'statistics': {
                'total_auctions': len(auctions),
                'active_auctions': active_auctions,
                'total_bids': len(bids),
                'total_bid_amount': total_bid_amount,
                'highest_bidder_count': len(highest_bidder_auctions)
            },
            'recent_auctions': [a.to_dict() for a in auctions[-5:]] if auctions else [],
            'recent_bids': [b.to_dict(include_user=False) for b in sorted(bids, key=lambda x: x.timestamp, reverse=True)[:5]] if bids else []
        }
        
        return success_response(dashboard_data, 'Dashboard retrieved successfully')
    
    except Exception as e:
        return error_response(f'Error retrieving dashboard: {str(e)}', 500)


@users_bp.route('/<int:user_id>/auctions', methods=['GET'])
def get_user_auctions(user_id):
    """Get all auctions for a specific user"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        paginated = Auction.query.filter_by(seller_id=user_id).order_by(
            Auction.created_at.desc()
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        auctions = [a.to_dict() for a in paginated.items]
        
        return success_response({
            'auctions': auctions,
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page
        }, 'User auctions retrieved successfully')
    
    except Exception as e:
        return error_response(f'Error retrieving user auctions: {str(e)}', 500)


@users_bp.route('/<int:user_id>/bids', methods=['GET'])
def get_user_bids_list(user_id):
    """Get all bids placed by a specific user"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        paginated = Bid.query.filter_by(user_id=user_id).order_by(
            Bid.timestamp.desc()
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        bids = [b.to_dict() for b in paginated.items]
        
        return success_response({
            'bids': bids,
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page
        }, 'User bids retrieved successfully')
    
    except Exception as e:
        return error_response(f'Error retrieving user bids: {str(e)}', 500)
