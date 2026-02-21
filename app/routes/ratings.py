from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from app import db, limiter
from app.models.seller_rating import SellerRating
from app.models.user import User
from app.models.auction import Auction
from app.utils.validators import error_response, success_response

ratings_bp = Blueprint('ratings', __name__)


@ratings_bp.route('/seller/<int:seller_id>', methods=['GET'])
def get_seller_ratings(seller_id):
    """Get all ratings for a seller"""
    try:
        seller = User.query.get(seller_id)
        if not seller:
            return error_response('Seller not found', 404)
        
        ratings = SellerRating.query.filter_by(seller_id=seller_id).order_by(
            SellerRating.created_at.desc()
        ).all()
        
        # Calculate averages
        avg_rating = db.session.query(func.avg(SellerRating.rating)).filter_by(seller_id=seller_id).scalar() or 0
        avg_communication = db.session.query(func.avg(SellerRating.communication)).filter_by(seller_id=seller_id).scalar() or 0
        avg_accuracy = db.session.query(func.avg(SellerRating.accuracy)).filter_by(seller_id=seller_id).scalar() or 0
        avg_shipping = db.session.query(func.avg(SellerRating.shipping)).filter_by(seller_id=seller_id).scalar() or 0
        
        return success_response({
            'ratings': [rating.to_dict() for rating in ratings],
            'total_ratings': len(ratings),
            'average_rating': round(float(avg_rating), 2),
            'average_communication': round(float(avg_communication), 2),
            'average_accuracy': round(float(avg_accuracy), 2),
            'average_shipping': round(float(avg_shipping), 2)
        }, 'Ratings retrieved successfully')
    except Exception as e:
        return error_response(f'Error retrieving ratings: {str(e)}', 500)


@ratings_bp.route('/auction/<int:auction_id>', methods=['POST'])
@limiter.limit("5 per day")
@jwt_required()
def add_rating(auction_id):
    """Add a rating for a seller"""
    try:
        buyer_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('rating'):
            return error_response('Rating required', 400)
        
        auction = Auction.query.get(auction_id)
        if not auction:
            return error_response('Auction not found', 404)
        
        # Check if already rated
        existing = SellerRating.query.filter_by(
            buyer_id=buyer_id,
            auction_id=auction_id
        ).first()
        
        if existing:
            return error_response('Already rated this auction', 400)
        
        # Validate rating
        rating_value = int(data['rating'])
        if rating_value < 1 or rating_value > 5:
            return error_response('Rating must be between 1 and 5', 400)
        
        rating = SellerRating(
            seller_id=auction.seller_id,
            buyer_id=buyer_id,
            auction_id=auction_id,
            rating=rating_value,
            review=data.get('review'),
            communication=data.get('communication'),
            accuracy=data.get('accuracy'),
            shipping=data.get('shipping')
        )
        
        db.session.add(rating)
        db.session.commit()
        
        return success_response(rating.to_dict(), 'Rating added successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error adding rating: {str(e)}', 500)
