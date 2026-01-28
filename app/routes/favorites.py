from flask import Blueprint, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app import db
from app.models.favorite import Favorite
from app.models.auction import Auction
from app.utils.validators import error_response, success_response

favorites_bp = Blueprint('favorites', __name__)


@favorites_bp.route('', methods=['GET'])
def get_user_favorites():
    """Get all favorites for the current user"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        paginated = Favorite.query.filter_by(user_id=user_id).order_by(
            Favorite.created_at.desc()
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        favorites = [fav.to_dict() for fav in paginated.items]
        
        return success_response({
            'favorites': favorites,
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page
        }, 'Favorites retrieved successfully')
    
    except Exception as e:
        return error_response(f'Error retrieving favorites: {str(e)}', 500)


@favorites_bp.route('/auction/<int:auction_id>', methods=['POST'])
def add_favorite(auction_id):
    """Add an auction to user's favorites"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        auction = Auction.query.get(auction_id)
        
        if not auction:
            return error_response('Auction not found', 404)
        
        # Check if already favorited
        existing = Favorite.query.filter_by(
            user_id=user_id,
            auction_id=auction_id
        ).first()
        
        if existing:
            return error_response('Auction already in favorites', 409)
        
        # Create favorite
        favorite = Favorite(
            user_id=user_id,
            auction_id=auction_id
        )
        
        db.session.add(favorite)
        db.session.commit()
        
        return success_response(favorite.to_dict(), 'Auction added to favorites', 201)
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error adding favorite: {str(e)}', 500)


@favorites_bp.route('/auction/<int:auction_id>', methods=['DELETE'])
def remove_favorite(auction_id):
    """Remove an auction from user's favorites"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        favorite = Favorite.query.filter_by(
            user_id=user_id,
            auction_id=auction_id
        ).first()
        
        if not favorite:
            return error_response('Favorite not found', 404)
        
        db.session.delete(favorite)
        db.session.commit()
        
        return success_response(None, 'Auction removed from favorites')
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error removing favorite: {str(e)}', 500)


@favorites_bp.route('/auction/<int:auction_id>', methods=['GET'])
def is_favorite(auction_id):
    """Check if an auction is in user's favorites"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        favorite = Favorite.query.filter_by(
            user_id=user_id,
            auction_id=auction_id
        ).first()
        
        return success_response({
            'is_favorite': favorite is not None,
            'favorite_id': favorite.id if favorite else None
        }, 'Favorite status retrieved successfully')
    
    except Exception as e:
        return error_response(f'Error checking favorite status: {str(e)}', 500)
