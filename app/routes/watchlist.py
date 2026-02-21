from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
from app import db
from app.models.watchlist import Watchlist
from app.models.auction import Auction
from app.utils.validators import error_response, success_response

watchlist_bp = Blueprint('watchlist', __name__)


@watchlist_bp.route('', methods=['GET'])
@jwt_required()
def get_watchlist():
    """Get user's watchlist"""
    try:
        user_id = get_jwt_identity()
        
        watchlist_items = Watchlist.query.filter_by(user_id=user_id).all()
        auction_ids = [item.auction_id for item in watchlist_items]
        
        # Get auctions with eager loading
        auctions = Auction.query.options(
            joinedload(Auction.seller)
        ).filter(Auction.id.in_(auction_ids)).all()
        
        return success_response({
            'watchlist': [item.to_dict() for item in watchlist_items],
            'auctions': [auction.to_dict(include_seller=True) for auction in auctions]
        }, 'Watchlist retrieved successfully')
    except Exception as e:
        return error_response(f'Error retrieving watchlist: {str(e)}', 500)


@watchlist_bp.route('/auction/<int:auction_id>', methods=['POST'])
@jwt_required()
def add_to_watchlist(auction_id):
    """Add auction to watchlist"""
    try:
        user_id = get_jwt_identity()
        
        auction = Auction.query.get(auction_id)
        if not auction:
            return error_response('Auction not found', 404)
        
        # Check if already watching
        existing = Watchlist.query.filter_by(
            user_id=user_id,
            auction_id=auction_id
        ).first()
        
        if existing:
            return error_response('Already in watchlist', 400)
        
        data = request.get_json() or {}
        
        watchlist_item = Watchlist(
            user_id=user_id,
            auction_id=auction_id,
            notify_on_bid=data.get('notify_on_bid', True),
            notify_on_ending=data.get('notify_on_ending', True),
            notify_on_outbid=data.get('notify_on_outbid', True)
        )
        
        # Increment watch count
        auction.watch_count += 1
        
        db.session.add(watchlist_item)
        db.session.commit()
        
        return success_response(watchlist_item.to_dict(), 'Added to watchlist', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error adding to watchlist: {str(e)}', 500)


@watchlist_bp.route('/auction/<int:auction_id>', methods=['DELETE'])
@jwt_required()
def remove_from_watchlist(auction_id):
    """Remove auction from watchlist"""
    try:
        user_id = get_jwt_identity()
        
        watchlist_item = Watchlist.query.filter_by(
            user_id=user_id,
            auction_id=auction_id
        ).first()
        
        if not watchlist_item:
            return error_response('Not in watchlist', 404)
        
        auction = Auction.query.get(auction_id)
        if auction and auction.watch_count > 0:
            auction.watch_count -= 1
        
        db.session.delete(watchlist_item)
        db.session.commit()
        
        return success_response(None, 'Removed from watchlist')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error removing from watchlist: {str(e)}', 500)


@watchlist_bp.route('/auction/<int:auction_id>', methods=['GET'])
@jwt_required()
def check_watchlist(auction_id):
    """Check if auction is in user's watchlist"""
    try:
        user_id = get_jwt_identity()
        
        watchlist_item = Watchlist.query.filter_by(
            user_id=user_id,
            auction_id=auction_id
        ).first()
        
        return success_response({
            'is_watching': watchlist_item is not None,
            'watchlist_item': watchlist_item.to_dict() if watchlist_item else None
        }, 'Watchlist status retrieved')
    except Exception as e:
        return error_response(f'Error checking watchlist: {str(e)}', 500)
