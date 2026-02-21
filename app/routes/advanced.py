from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, limiter
from app.models.bid import Bid
from app.models.auction import Auction
from app.utils.vin_decoder import VINDecoder
from app.utils.proxy_bidding import ProxyBiddingService
from app.utils.validators import error_response, success_response
from datetime import datetime, timedelta

advanced_bp = Blueprint('advanced', __name__)


# VIN Decoder Routes
@advanced_bp.route('/vin/decode/<string:vin>', methods=['GET'])
@limiter.limit("20 per hour")
def decode_vin(vin):
    """Decode VIN and return vehicle information"""
    try:
        if not VINDecoder.validate_vin(vin):
            return error_response('Invalid VIN format', 400)
        
        result = VINDecoder.decode(vin)
        
        if 'error' in result:
            return error_response(result['error'], 400)
        
        return success_response(result, 'VIN decoded successfully')
    except Exception as e:
        return error_response(f'Error decoding VIN: {str(e)}', 500)


# Proxy Bidding Routes
@advanced_bp.route('/proxy-bid/auction/<int:auction_id>', methods=['POST'])
@limiter.limit("30 per hour")
@jwt_required()
def place_proxy_bid(auction_id):
    """Place a proxy bid"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('max_bid'):
            return error_response('max_bid required', 400)
        
        max_bid = float(data['max_bid'])
        
        result = ProxyBiddingService.place_proxy_bid(auction_id, user_id, max_bid)
        
        if 'error' in result:
            return error_response(result['error'], 400)
        
        return success_response(result['bid'], 'Proxy bid placed successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error placing proxy bid: {str(e)}', 500)


# Bid Retraction
@advanced_bp.route('/retract-bid/<int:bid_id>', methods=['POST'])
@limiter.limit("3 per day")
@jwt_required()
def retract_bid(bid_id):
    """Retract a bid (only within 1 hour of placement)"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        bid = Bid.query.get(bid_id)
        
        if not bid:
            return error_response('Bid not found', 404)
        
        if bid.user_id != user_id:
            return error_response('Unauthorized', 403)
        
        if bid.is_retracted:
            return error_response('Bid already retracted', 400)
        
        # Check if within 1 hour
        time_since_bid = datetime.utcnow() - bid.timestamp
        if time_since_bid > timedelta(hours=1):
            return error_response('Can only retract bids within 1 hour of placement', 400)
        
        # Check if it's the highest bid
        auction = Auction.query.get(bid.auction_id)
        highest_bid = auction.bids.filter_by(is_retracted=False).order_by(Bid.bid_amount.desc()).first()
        
        if highest_bid and highest_bid.id == bid.id:
            return error_response('Cannot retract the current highest bid', 400)
        
        bid.is_retracted = True
        bid.retraction_reason = data.get('reason', 'User requested retraction')
        
        db.session.commit()
        
        return success_response(bid.to_dict(), 'Bid retracted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error retracting bid: {str(e)}', 500)


# Buy Now
@advanced_bp.route('/buy-now/auction/<int:auction_id>', methods=['POST'])
@limiter.limit("10 per hour")
@jwt_required()
def buy_now(auction_id):
    """Buy auction instantly at buy now price"""
    try:
        user_id = get_jwt_identity()
        
        auction = Auction.query.get(auction_id)
        
        if not auction:
            return error_response('Auction not found', 404)
        
        if not auction.buy_now_price:
            return error_response('Buy now not available for this auction', 400)
        
        if auction.status != 'active':
            return error_response('Auction is not active', 400)
        
        if auction.seller_id == user_id:
            return error_response('Cannot buy your own auction', 400)
        
        # Create winning bid
        bid = Bid(
            auction_id=auction_id,
            user_id=user_id,
            bid_amount=auction.buy_now_price,
            is_proxy=False
        )
        
        # Close auction and mark as sold
        auction.status = 'sold'
        auction.current_price = auction.buy_now_price
        
        db.session.add(bid)
        db.session.commit()
        
        return success_response({
            'bid': bid.to_dict(),
            'auction': auction.to_dict()
        }, 'Purchase successful', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error processing buy now: {str(e)}', 500)
