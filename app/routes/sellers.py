from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.seller import Seller, SellerApprovalLog
from app.utils.seller_approval_service import SellerApprovalService
from app.utils.validators import error_response, success_response
import logging


sellers_bp = Blueprint('sellers', __name__)
logger = logging.getLogger(__name__)


@sellers_bp.route('/register', methods=['POST'])
@jwt_required()
def register_seller():
    """Register as a seller
    
    Requires: JWT authentication
    Body:
    {
        "business_name": "string",
        "business_phone": "string",
        "business_address": "string",
        "documents": ["url1", "url2"]  (optional)
    }
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return error_response('User not found', 404)
        
        # Check if already is seller
        if user.role == 'seller':
            existing_seller = Seller.query.filter_by(user_id=user_id).first()
            if existing_seller:
                return error_response('Already registered as seller', 409)
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['business_name', 'business_phone', 'business_address']
        for field in required_fields:
            if not data.get(field):
                return error_response(f'Missing required field: {field}', 400)
        
        # Validate phone format (basic)
        business_phone = data.get('business_phone', '').strip()
        if len(business_phone) < 10:
            return error_response('Invalid phone number', 400)
        
        # Create seller profile
        documents = data.get('documents', [])
        seller = SellerApprovalService.create_seller(
            user_id=user_id,
            business_name=data['business_name'],
            business_phone=business_phone,
            business_address=data['business_address'],
            documents=documents
        )
        
        # Update user role
        user.role = 'seller'
        user.approved = False  # Sellers start unapproved
        
        db.session.commit()
        
        current_app.logger.info(f"Seller registered: user_id={user_id}, business={data['business_name']}")
        
        return success_response({
            'message': 'Seller registered successfully. Awaiting approval.',
            'seller': seller.to_dict()
        }, 201)
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error registering seller: {str(e)}")
        return error_response(str(e), 500)


@sellers_bp.route('/<int:seller_id>/verify-documents', methods=['POST'])
@jwt_required()
def verify_documents(seller_id):
    """Verify seller documents (mock endpoint)
    
    Requires: JWT authentication
    Body:
    {
        "document_paths": ["path1", "path2"]
    }
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return error_response('User not found', 404)
        
        # Verify ownership or admin
        seller = Seller.query.get(seller_id)
        if not seller:
            return error_response('Seller not found', 404)
        
        if seller.user_id != user_id and user.role != 'admin':
            return error_response('Unauthorized', 403)
        
        data = request.get_json()
        document_paths = data.get('document_paths', [])
        
        # Verify documents
        success, message = SellerApprovalService.verify_documents(
            seller_id=seller_id,
            document_paths=document_paths,
            admin_id=user_id if user.role == 'admin' else None
        )
        
        if success:
            db.session.commit()
            return success_response({
                'message': message,
                'seller': seller.to_dict()
            }, 200)
        else:
            return error_response(message, 400)
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error verifying documents: {str(e)}")
        return error_response(str(e), 500)


@sellers_bp.route('/<int:seller_id>/verify-email-otp', methods=['POST'])
@jwt_required()
def verify_email_otp(seller_id):
    """Verify email via OTP
    
    Requires: JWT authentication
    Body:
    {
        "otp_token": "123456"
    }
    """
    try:
        user_id = int(get_jwt_identity())
        seller = Seller.query.get(seller_id)
        
        if not seller:
            return error_response('Seller not found', 404)
        
        if seller.user_id != user_id:
            return error_response('Unauthorized', 403)
        
        data = request.get_json()
        otp_token = data.get('otp_token', '')
        
        success, message = SellerApprovalService.verify_email_otp(seller_id, otp_token)
        
        if success:
            db.session.commit()
            return success_response({
                'message': message,
                'seller': seller.to_dict()
            }, 200)
        else:
            return error_response(message, 400)
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error verifying email OTP: {str(e)}")
        return error_response(str(e), 500)


@sellers_bp.route('/<int:seller_id>/verify-phone-otp', methods=['POST'])
@jwt_required()
def verify_phone_otp(seller_id):
    """Verify phone via OTP
    
    Requires: JWT authentication
    Body:
    {
        "otp_token": "123456"
    }
    """
    try:
        user_id = int(get_jwt_identity())
        seller = Seller.query.get(seller_id)
        
        if not seller:
            return error_response('Seller not found', 404)
        
        if seller.user_id != user_id:
            return error_response('Unauthorized', 403)
        
        data = request.get_json()
        otp_token = data.get('otp_token', '')
        
        success, message = SellerApprovalService.verify_phone_otp(seller_id, otp_token)
        
        if success:
            db.session.commit()
            return success_response({
                'message': message,
                'seller': seller.to_dict()
            }, 200)
        else:
            return error_response(message, 400)
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error verifying phone OTP: {str(e)}")
        return error_response(str(e), 500)


@sellers_bp.route('/<int:seller_id>/process-approval', methods=['POST'])
@jwt_required()
def process_approval(seller_id):
    """Process automatic seller approval based on risk score
    
    Requires: JWT authentication (seller can request their own approval)
    Processes risk score and either auto-approves or flags for manual review
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return error_response('User not found', 404)
        
        seller = Seller.query.get(seller_id)
        if not seller:
            return error_response('Seller not found', 404)
        
        # Seller can request their own, or admin can request for any
        if seller.user_id != user_id and user.role != 'admin':
            return error_response('Unauthorized', 403)
        
        # Process approval
        approved, message, details = SellerApprovalService.process_seller_approval(seller_id)
        
        db.session.commit()
        
        if approved:
            return success_response({
                'message': message,
                'approved': True,
                'auto_approved': seller.auto_approved,
                'seller': seller.to_dict(),
                'details': details
            }, 200)
        else:
            return success_response({
                'message': message,
                'approved': False,
                'approval_status': seller.approval_status,
                'seller': seller.to_dict(),
                'details': details
            }, 200)
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing approval: {str(e)}")
        return error_response(str(e), 500)


@sellers_bp.route('/<int:seller_id>/manual-approve', methods=['POST'])
@jwt_required()
def manual_approve(seller_id):
    """Manually approve seller (admin only)
    
    Requires: JWT authentication + admin role
    Body:
    {
        "reason": "string (optional)"
    }
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return error_response('Admin access required', 403)
        
        seller = Seller.query.get(seller_id)
        if not seller:
            return error_response('Seller not found', 404)
        
        data = request.get_json() or {}
        reason = data.get('reason', '')
        
        success, message = SellerApprovalService.manual_approve_seller(seller_id, user_id, reason)
        
        if success:
            db.session.commit()
            return success_response({
                'message': message,
                'seller': seller.to_dict()
            }, 200)
        else:
            return error_response(message, 400)
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error manually approving seller: {str(e)}")
        return error_response(str(e), 500)


@sellers_bp.route('/<int:seller_id>/manual-reject', methods=['POST'])
@jwt_required()
def manual_reject(seller_id):
    """Manually reject seller (admin only)
    
    Requires: JWT authentication + admin role
    Body:
    {
        "reason": "string"
    }
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return error_response('Admin access required', 403)
        
        seller = Seller.query.get(seller_id)
        if not seller:
            return error_response('Seller not found', 404)
        
        data = request.get_json()
        reason = data.get('reason', '')
        
        if not reason:
            return error_response('Reason is required', 400)
        
        success, message = SellerApprovalService.manual_reject_seller(seller_id, user_id, reason)
        
        if success:
            db.session.commit()
            return success_response({
                'message': message,
                'seller': seller.to_dict()
            }, 200)
        else:
            return error_response(message, 400)
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error rejecting seller: {str(e)}")
        return error_response(str(e), 500)


@sellers_bp.route('/<int:seller_id>/suspend', methods=['POST'])
@jwt_required()
def suspend_seller(seller_id):
    """Suspend seller account (admin only)
    
    Requires: JWT authentication + admin role
    Body:
    {
        "reason": "string"
    }
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return error_response('Admin access required', 403)
        
        seller = Seller.query.get(seller_id)
        if not seller:
            return error_response('Seller not found', 404)
        
        data = request.get_json()
        reason = data.get('reason', '')
        
        success, message = SellerApprovalService.suspend_seller(seller_id, user_id, reason)
        
        if success:
            db.session.commit()
            return success_response({
                'message': message,
                'seller': seller.to_dict()
            }, 200)
        else:
            return error_response(message, 400)
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error suspending seller: {str(e)}")
        return error_response(str(e), 500)


@sellers_bp.route('/<int:seller_id>/flag-suspicious', methods=['POST'])
@jwt_required()
def flag_suspicious(seller_id):
    """Flag seller for suspicious activity (admin only)
    
    Requires: JWT authentication + admin role
    Body:
    {
        "reason": "string"
    }
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return error_response('Admin access required', 403)
        
        seller = Seller.query.get(seller_id)
        if not seller:
            return error_response('Seller not found', 404)
        
        data = request.get_json()
        reason = data.get('reason', '')
        
        success, message = SellerApprovalService.flag_suspicious_activity(seller_id, reason)
        
        if success:
            db.session.commit()
            return success_response({
                'message': message,
                'seller': seller.to_dict()
            }, 200)
        else:
            return error_response(message, 400)
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error flagging suspicious activity: {str(e)}")
        return error_response(str(e), 500)


@sellers_bp.route('/<int:seller_id>', methods=['GET'])
@jwt_required()
def get_seller(seller_id):
    """Get seller profile
    
    Requires: JWT authentication
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return error_response('User not found', 404)
        
        seller = Seller.query.get(seller_id)
        if not seller:
            return error_response('Seller not found', 404)
        
        # Only seller themselves or admin can view
        if seller.user_id != user_id and user.role != 'admin':
            return error_response('Unauthorized', 403)
        
        return success_response({
            'seller': seller.to_dict()
        }, 200)
    
    except Exception as e:
        logger.error(f"Error getting seller: {str(e)}")
        return error_response(str(e), 500)


@sellers_bp.route('/<int:seller_id>/logs', methods=['GET'])
@jwt_required()
def get_approval_logs(seller_id):
    """Get approval audit logs for seller
    
    Requires: JWT authentication (admin only)
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return error_response('Admin access required', 403)
        
        seller = Seller.query.get(seller_id)
        if not seller:
            return error_response('Seller not found', 404)
        
        limit = request.args.get('limit', 50, type=int)
        logs = SellerApprovalService.get_seller_approval_logs(seller_id, limit)
        
        return success_response({
            'seller_id': seller_id,
            'logs': [log.to_dict() for log in logs]
        }, 200)
    
    except Exception as e:
        logger.error(f"Error getting approval logs: {str(e)}")
        return error_response(str(e), 500)
