import logging
import secrets
from datetime import datetime
from app import db
from app.models.seller import Seller, SellerApprovalLog
from app.models.user import User


logger = logging.getLogger(__name__)


class SellerApprovalService:
    """Service for handling seller approval workflow and risk assessment"""
    
    # Risk score thresholds
    MIN_AUTO_APPROVE_SCORE = 8.0
    MAX_RISK_SCORE = 15.0
    
    @staticmethod
    def create_seller(user_id, business_name, business_phone, business_address, documents=None):
        """Create a new seller profile
        
        Args:
            user_id: User ID
            business_name: Seller's business name
            business_phone: Seller's business phone
            business_address: Seller's business address
            documents: Optional list of document URLs
        
        Returns:
            Seller instance
        """
        seller = Seller(
            user_id=user_id,
            business_name=business_name,
            business_phone=business_phone,
            business_address=business_address
        )
        
        if documents:
            seller.document_upload_paths = documents
        
        db.session.add(seller)
        db.session.flush()
        
        logger.info(f"Created seller profile for user {user_id}: {business_name}")
        
        return seller
    
    @staticmethod
    def verify_documents(seller_id, document_paths=None, admin_id=None):
        """Verify seller documents (mock verification)
        
        In production, this would:
        - Call document verification API
        - Extract and validate business info from documents
        - Check for document authenticity
        
        Args:
            seller_id: Seller ID
            document_paths: List of document file paths
            admin_id: Admin ID if manually verified
        
        Returns:
            tuple (bool, str) - (success, message)
        """
        seller = Seller.query.get(seller_id)
        if not seller:
            return False, "Seller not found"
        
        # Mock verification logic
        # In production, call actual document verification service
        if document_paths:
            seller.document_upload_paths.extend(document_paths)
        
        if len(seller.document_upload_paths) == 0:
            return False, "No documents uploaded"
        
        # Mark documents as verified
        previous_score = seller.risk_score
        previous_status = seller.approval_status
        
        seller.mark_documents_verified()
        
        # Log the action
        SellerApprovalService._log_approval_action(
            seller_id=seller_id,
            action='document_verified',
            previous_status=previous_status,
            new_status=seller.approval_status,
            previous_risk_score=previous_score,
            new_risk_score=seller.risk_score,
            reason='Documents verified successfully',
            admin_id=admin_id,
            details={'document_count': len(seller.document_upload_paths)}
        )
        
        logger.info(f"Documents verified for seller {seller_id}")
        
        return True, "Documents verified successfully"
    
    @staticmethod
    def verify_email_otp(seller_id, otp_token):
        """Verify email via OTP
        
        Args:
            seller_id: Seller ID
            otp_token: OTP token from email
        
        Returns:
            tuple (bool, str) - (success, message)
        """
        seller = Seller.query.get(seller_id)
        if not seller:
            return False, "Seller not found"
        
        # Mock OTP verification
        # In production, validate against stored OTP
        if not otp_token or len(otp_token) < 6:
            logger.warning(f"Invalid OTP attempt for seller {seller_id}")
            return False, "Invalid OTP"
        
        previous_score = seller.risk_score
        previous_status = seller.approval_status
        
        seller.mark_email_verified()
        
        SellerApprovalService._log_approval_action(
            seller_id=seller_id,
            action='email_verified',
            previous_status=previous_status,
            new_status=seller.approval_status,
            previous_risk_score=previous_score,
            new_risk_score=seller.risk_score,
            reason='Email verified via OTP'
        )
        
        logger.info(f"Email verified for seller {seller_id}")
        
        return True, "Email verified successfully"
    
    @staticmethod
    def verify_phone_otp(seller_id, otp_token):
        """Verify phone via OTP
        
        Args:
            seller_id: Seller ID
            otp_token: OTP token from SMS
        
        Returns:
            tuple (bool, str) - (success, message)
        """
        seller = Seller.query.get(seller_id)
        if not seller:
            return False, "Seller not found"
        
        # Mock OTP verification
        # In production, validate against SMS OTP service (Twilio, etc.)
        if not otp_token or len(otp_token) < 6:
            logger.warning(f"Invalid OTP attempt for seller {seller_id}")
            return False, "Invalid OTP"
        
        previous_score = seller.risk_score
        previous_status = seller.approval_status
        
        seller.mark_phone_verified()
        
        SellerApprovalService._log_approval_action(
            seller_id=seller_id,
            action='phone_verified',
            previous_status=previous_status,
            new_status=seller.approval_status,
            previous_risk_score=previous_score,
            new_risk_score=seller.risk_score,
            reason='Phone verified via OTP'
        )
        
        logger.info(f"Phone verified for seller {seller_id}")
        
        return True, "Phone verified successfully"
    
    @staticmethod
    def process_seller_approval(seller_id):
        """Process automatic seller approval
        
        Uses risk score calculation and database to determine approval:
        - If risk_score >= 8 AND documents verified: Auto-approve
        - Otherwise: Flag for manual review
        
        Args:
            seller_id: Seller ID
        
        Returns:
            tuple (bool, str, dict) - (approved, message, approval_details)
        """
        seller = Seller.query.get(seller_id)
        if not seller:
            return False, "Seller not found", {}
        
        if seller.approval_status in ['approved', 'rejected']:
            return False, f"Seller already {seller.approval_status}", {}
        
        previous_status = seller.approval_status
        previous_score = seller.risk_score
        
        # Recalculate risk score
        current_score = seller.update_risk_score()
        
        approval_details = {
            'seller_id': seller_id,
            'previous_risk_score': previous_score,
            'current_risk_score': current_score,
            'verified_documents': seller.verified_documents,
            'verified_email': seller.verified_email,
            'verified_phone': seller.verified_phone,
            'account_age_days': (datetime.utcnow() - seller.account_created_at).days,
            'suspicious_activity': seller.last_suspicious_activity is not None
        }
        
        # Check auto-approval criteria
        should_auto_approve, reason = seller.should_auto_approve()
        
        if should_auto_approve:
            seller.approve(auto_approved=True)
            
            SellerApprovalService._log_approval_action(
                seller_id=seller_id,
                action='auto_approved',
                previous_status=previous_status,
                new_status='approved',
                previous_risk_score=previous_score,
                new_risk_score=current_score,
                reason=reason,
                details=approval_details
            )
            
            # Update user role if automatic approval
            user = User.query.get(seller.user_id)
            if user:
                user.approved = True
            
            logger.info(f"Seller {seller_id} auto-approved with score {current_score}")
            
            return True, "Seller auto-approved successfully", approval_details
        else:
            seller.flag_for_manual_review(
                reason=f"Risk score: {current_score}/15. {reason}"
            )
            
            SellerApprovalService._log_approval_action(
                seller_id=seller_id,
                action='manual_review',
                previous_status=previous_status,
                new_status='manual_review',
                previous_risk_score=previous_score,
                new_risk_score=current_score,
                reason=f"Flagged for manual review. {reason}",
                details=approval_details
            )
            
            logger.info(f"Seller {seller_id} flagged for manual review. Score: {current_score}")
            
            return False, f"Flagged for manual review. {reason}", approval_details
    
    @staticmethod
    def manual_approve_seller(seller_id, admin_id, reason=''):
        """Manually approve seller (admin action)
        
        Args:
            seller_id: Seller ID
            admin_id: Admin user ID
            reason: Reason for approval
        
        Returns:
            tuple (bool, str) - (success, message)
        """
        seller = Seller.query.get(seller_id)
        if not seller:
            return False, "Seller not found"
        
        previous_status = seller.approval_status
        previous_score = seller.risk_score
        
        seller.approve(auto_approved=False)
        
        # Update user
        user = User.query.get(seller.user_id)
        if user:
            user.approved = True
        
        SellerApprovalService._log_approval_action(
            seller_id=seller_id,
            action='manual_approved',
            previous_status=previous_status,
            new_status='approved',
            previous_risk_score=previous_score,
            new_risk_score=seller.risk_score,
            reason=reason or 'Manually approved by admin',
            admin_id=admin_id,
            details={'admin_id': admin_id}
        )
        
        logger.info(f"Seller {seller_id} manually approved by admin {admin_id}")
        
        return True, "Seller approved successfully"
    
    @staticmethod
    def manual_reject_seller(seller_id, admin_id, reason=''):
        """Manually reject seller (admin action)
        
        Args:
            seller_id: Seller ID
            admin_id: Admin user ID
            reason: Reason for rejection
        
        Returns:
            tuple (bool, str) - (success, message)
        """
        seller = Seller.query.get(seller_id)
        if not seller:
            return False, "Seller not found"
        
        previous_status = seller.approval_status
        seller.reject(reason=reason)
        
        SellerApprovalService._log_approval_action(
            seller_id=seller_id,
            action='rejected',
            previous_status=previous_status,
            new_status='rejected',
            previous_risk_score=seller.risk_score,
            new_risk_score=seller.risk_score,
            reason=reason or 'Rejected by admin',
            admin_id=admin_id,
            details={'admin_id': admin_id}
        )
        
        logger.warning(f"Seller {seller_id} rejected by admin {admin_id}. Reason: {reason}")
        
        return True, "Seller rejected"
    
    @staticmethod
    def flag_suspicious_activity(seller_id, reason=''):
        """Flag seller for suspicious activity
        
        Args:
            seller_id: Seller ID
            reason: Reason for flagging
        
        Returns:
            tuple (bool, str) - (success, message)
        """
        seller = Seller.query.get(seller_id)
        if not seller:
            return False, "Seller not found"
        
        previous_score = seller.risk_score
        seller.flag_suspicious_activity()
        
        SellerApprovalService._log_approval_action(
            seller_id=seller_id,
            action='suspicious_activity_flagged',
            previous_risk_score=previous_score,
            new_risk_score=seller.risk_score,
            reason=reason or 'Suspicious activity detected',
            details={
                'login_attempts': seller.login_attempt_count,
                'score_penalty': previous_score - seller.risk_score
            }
        )
        
        logger.warning(f"Suspicious activity flagged for seller {seller_id}. Reason: {reason}")
        
        return True, "Suspicious activity logged"
    
    @staticmethod
    def suspend_seller(seller_id, admin_id, reason=''):
        """Suspend seller account (admin action)
        
        Args:
            seller_id: Seller ID
            admin_id: Admin user ID
            reason: Reason for suspension
        
        Returns:
            tuple (bool, str) - (success, message)
        """
        seller = Seller.query.get(seller_id)
        if not seller:
            return False, "Seller not found"
        
        previous_status = seller.approval_status
        seller.suspend(reason=reason)
        
        SellerApprovalService._log_approval_action(
            seller_id=seller_id,
            action='suspended',
            previous_status=previous_status,
            new_status='suspended',
            reason=reason or 'Account suspended',
            admin_id=admin_id,
            details={'admin_id': admin_id}
        )
        
        logger.warning(f"Seller {seller_id} suspended by admin {admin_id}. Reason: {reason}")
        
        return True, "Seller suspended"
    
    @staticmethod
    def get_seller_approval_logs(seller_id, limit=50):
        """Get approval logs for a seller
        
        Args:
            seller_id: Seller ID
            limit: Max number of logs
        
        Returns:
            List of SellerApprovalLog objects
        """
        return SellerApprovalLog.query.filter_by(seller_id=seller_id).order_by(
            SellerApprovalLog.created_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def _log_approval_action(seller_id, action, previous_status=None, new_status=None,
                            previous_risk_score=None, new_risk_score=None,
                            reason=None, admin_id=None, details=None):
        """Internal method to log approval actions
        
        Args:
            seller_id: Seller ID
            action: Action type
            previous_status: Status before action
            new_status: Status after action
            previous_risk_score: Risk score before action
            new_risk_score: Risk score after action
            reason: Reason for action
            admin_id: Admin user ID if applicable
            details: Additional JSON details
        """
        log_entry = SellerApprovalLog(
            seller_id=seller_id,
            action=action,
            previous_status=previous_status,
            new_status=new_status,
            previous_risk_score=previous_risk_score,
            new_risk_score=new_risk_score,
            reason=reason,
            admin_id=admin_id,
            details=details or {}
        )
        db.session.add(log_entry)
        db.session.flush()
        
        logger.info(
            f"Approval log: seller_id={seller_id}, action={action}, "
            f"risk_score={new_risk_score}, admin_id={admin_id}"
        )
