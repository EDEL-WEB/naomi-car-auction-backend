from flask import Blueprint, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app import db, socketio
from app.models.bid import Bid
from app.models.auction import Auction
from app.utils.validators import validate_bid_input, error_response, success_response
from app.utils.notification_service import NotificationService
from config import Config
from datetime import datetime

bids_bp = Blueprint('bids', __name__)


@bids_bp.route('/auction/<int:auction_id>', methods=['GET'])
def get_auction_bids(auction_id):
    """Get all bids for an auction"""
    try:
        auction = Auction.query.get(auction_id)
        
        if not auction:
            return error_response('Auction not found', 404)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        paginated = auction.bids.order_by(Bid.timestamp.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        bids = [bid.to_dict(include_user=True) for bid in paginated.items]
        
        return success_response({
            'bids': bids,
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page,
            'current_price': auction.current_price,
            'highest_bidder_id': auction.bids.order_by(Bid.bid_amount.desc()).first().user_id if auction.bids.count() > 0 else None
        }, 'Bids retrieved successfully')
    
    except Exception as e:
        return error_response(f'Error retrieving bids: {str(e)}', 500)


@bids_bp.route('/auction/<int:auction_id>', methods=['POST'])
def place_bid(auction_id):
    """Place a bid on an auction"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        auction = Auction.query.get(auction_id)
        
        if not auction:
            return error_response('Auction not found', 404)
        
        if auction.status != 'active':
            return error_response('Auction is not active', 400)
        
        if auction.ends_at < datetime.utcnow():
            auction.status = 'closed'
            db.session.commit()
            return error_response('Auction has ended', 400)
        
        if auction.seller_id == user_id:
            return error_response('Sellers cannot bid on their own auctions', 400)
        
        data = request.get_json()
        
        if not data:
            return error_response('No data provided', 400)
        
        # Validate bid input
        errors = validate_bid_input(data)
        if errors:
            return error_response(', '.join(errors), 400)
        
        bid_amount = float(data['bid_amount'])
        minimum_bid = auction.current_price + Config.MINIMUM_BID_INCREMENT
        
        if bid_amount <= auction.current_price:
            return error_response(
                f'Bid amount must be greater than current price ({auction.current_price})',
                400
            )
        
        if bid_amount < minimum_bid:
            return error_response(
                f'Bid amount must be at least {minimum_bid} (current: {auction.current_price} + minimum increment: {Config.MINIMUM_BID_INCREMENT})',
                400
            )
        
        # Create bid
        bid = Bid(
            auction_id=auction_id,
            user_id=user_id,
            bid_amount=bid_amount
        )
        
        # Update auction's current price
        auction.current_price = bid_amount
        
        db.session.add(bid)
        db.session.commit()
        
        # Send notification to seller
        NotificationService.notify_bid_placed(
            seller_id=auction.seller_id,
            auction_id=auction_id,
            bidder_username=bid.bidder.username,
            bid_amount=bid_amount
        )
        
        # Notify previous highest bidder if they are being outbid
        previous_bids = Bid.query.filter_by(auction_id=auction_id).order_by(Bid.bid_amount.desc()).offset(1).first()
        if previous_bids:
            NotificationService.notify_outbid(
                user_id=previous_bids.user_id,
                auction_id=auction_id,
                auction_title=auction.title,
                current_price=bid_amount
            )
        
        # Emit socket.io event for real-time update
        socketio.emit('new_bid', {
            'auction_id': auction_id,
            'bid_amount': bid_amount,
            'user_id': user_id,
            'timestamp': bid.timestamp.isoformat(),
            'current_price': auction.current_price
        }, room=f'auction_{auction_id}')
        
        return success_response(bid.to_dict(), 'Bid placed successfully', 201)
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error placing bid: {str(e)}', 500)


@bids_bp.route('/user', methods=['GET'])
def get_user_bids():
    """Get all bids placed by the current user"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        paginated = Bid.query.filter_by(user_id=user_id).order_by(Bid.timestamp.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        bids = [bid.to_dict() for bid in paginated.items]
        
        return success_response({
            'bids': bids,
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page
        }, 'User bids retrieved successfully')
    
    except Exception as e:
        return error_response(f'Error retrieving user bids: {str(e)}', 500)


@bids_bp.route('/<int:bid_id>', methods=['GET'])
def get_bid(bid_id):
    """Get a specific bid"""
    try:
        bid = Bid.query.get(bid_id)
        
        if not bid:
            return error_response('Bid not found', 404)
        
        return success_response(bid.to_dict(include_user=True), 'Bid retrieved successfully')
    
    except Exception as e:
        return error_response(f'Error retrieving bid: {str(e)}', 500)
