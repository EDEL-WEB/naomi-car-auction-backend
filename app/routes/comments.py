from flask import Blueprint, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, jwt_required
from app import db, limiter
from app.models.auction_comment import AuctionComment
from app.models.auction import Auction
from app.utils.validators import error_response, success_response

comments_bp = Blueprint('comments', __name__)


@comments_bp.route('/auction/<int:auction_id>', methods=['GET'])
def get_comments(auction_id):
    """Get all comments for an auction"""
    try:
        auction = Auction.query.get(auction_id)
        if not auction:
            return error_response('Auction not found', 404)
        
        # Get top-level comments only
        comments = AuctionComment.query.filter_by(
            auction_id=auction_id,
            parent_id=None
        ).order_by(AuctionComment.created_at.desc()).all()
        
        return success_response(
            [comment.to_dict(include_replies=True) for comment in comments],
            'Comments retrieved successfully'
        )
    except Exception as e:
        return error_response(f'Error retrieving comments: {str(e)}', 500)


@comments_bp.route('/auction/<int:auction_id>', methods=['POST'])
@limiter.limit("20 per hour")
@jwt_required()
def add_comment(auction_id):
    """Add a comment to an auction"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('comment'):
            return error_response('Comment text required', 400)
        
        auction = Auction.query.get(auction_id)
        if not auction:
            return error_response('Auction not found', 404)
        
        comment = AuctionComment(
            auction_id=auction_id,
            user_id=user_id,
            comment=data['comment'],
            parent_id=data.get('parent_id'),
            is_seller_response=(user_id == auction.seller_id)
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return success_response(comment.to_dict(), 'Comment added successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error adding comment: {str(e)}', 500)


@comments_bp.route('/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    """Delete a comment"""
    try:
        user_id = get_jwt_identity()
        comment = AuctionComment.query.get(comment_id)
        
        if not comment:
            return error_response('Comment not found', 404)
        
        if comment.user_id != user_id:
            return error_response('Unauthorized', 403)
        
        db.session.delete(comment)
        db.session.commit()
        
        return success_response(None, 'Comment deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error deleting comment: {str(e)}', 500)
