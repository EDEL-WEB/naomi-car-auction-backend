from app import db
from datetime import datetime
import json


class Seller(db.Model):
    """Seller profile model with automatic approval system"""
    __tablename__ = 'sellers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True, index=True)
    
    # Business information
    business_name = db.Column(db.String(255), nullable=False)
    business_phone = db.Column(db.String(20), nullable=False)
    business_address = db.Column(db.String(500), nullable=False)
    
    # Verification fields
    verified_documents = db.Column(db.Boolean, default=False, nullable=False)
    document_upload_paths = db.Column(db.JSON, default=list)  # List of document URLs
    documents_verified_at = db.Column(db.DateTime, nullable=True)
    
    verified_phone = db.Column(db.Boolean, default=False, nullable=False)
    phone_verification_token = db.Column(db.String(100), nullable=True)
    phone_verified_at = db.Column(db.DateTime, nullable=True)
    
    verified_email = db.Column(db.Boolean, default=False, nullable=False)
    email_verification_token = db.Column(db.String(100), nullable=True)
    email_verified_at = db.Column(db.DateTime, nullable=True)
    
    # Approval system fields
    risk_score = db.Column(db.Float, default=0.0, nullable=False, index=True)
    is_approved = db.Column(db.Boolean, default=False, nullable=False, index=True)
    approval_status = db.Column(
        db.String(20),
        default='pending',
        nullable=False,
        index=True
    )  # 'pending', 'approved', 'rejected', 'manual_review'
    auto_approved = db.Column(db.Boolean, default=False, nullable=False)
    
    # Fraud/suspicious activity tracking
    login_attempt_count = db.Column(db.Integer, default=0)
    last_suspicious_activity = db.Column(db.DateTime, nullable=True)
    suspension_reason = db.Column(db.String(500), nullable=True)
    is_suspended = db.Column(db.Boolean, default=False, nullable=False, index=True)
    
    # Account age
    account_created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='seller_profile', foreign_keys=[user_id])
    approval_logs = db.relationship(
        'SellerApprovalLog',
        backref='seller',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    def calculate_risk_score(self):
        """Calculate seller risk score based on verification status
        
        Scoring logic:
        - Verified documents: +5 points
        - Verified email: +2 points  
        - Verified phone: +2 points
        - Account age (30+ days): +1 point
        - Recent suspicious activity: -5 points
        - Multiple failed login attempts: -3 points
        
        Returns: float (score out of 15, where 8+ = auto-approved)
        """
        score = 0.0
        
        # Verified documents (+5)
        if self.verified_documents:
            score += 5.0
        
        # Verified email (+2)
        if self.verified_email:
            score += 2.0
        
        # Verified phone (+2)
        if self.verified_phone:
            score += 2.0
        
        # Account age - 30+ days (+1)
        account_age = (datetime.utcnow() - self.account_created_at).days
        if account_age >= 30:
            score += 1.0
        
        # Suspicious activity penalty (-5)
        if self.last_suspicious_activity:
            days_since_suspicious = (datetime.utcnow() - self.last_suspicious_activity).days
            if days_since_suspicious < 7:  # Recent suspicious activity (within 7 days)
                score -= 5.0
        
        # Failed login attempts penalty (-3)
        if self.login_attempt_count >= 5:
            score -= 3.0
        
        return max(0.0, score)  # Ensure score doesn't go below 0
    
    def update_risk_score(self):
        """Recalculate and update risk score"""
        self.risk_score = self.calculate_risk_score()
        return self.risk_score
    
    def should_auto_approve(self):
        """Check if seller meets auto-approval criteria
        
        Requirements:
        - Risk score >= 8
        - Not suspended
        - All documents verified
        
        Returns: tuple (bool, str) - (should_approve, reason)
        """
        if self.is_suspended:
            return False, "Account is suspended"
        
        if self.risk_score < 8.0:
            return False, f"Risk score too low ({self.risk_score}/15). Requires manual review."
        
        if not self.verified_documents:
            return False, "Documents not verified"
        
        return True, "Meets auto-approval criteria"
    
    def mark_documents_verified(self):
        """Mark documents as verified"""
        self.verified_documents = True
        self.documents_verified_at = datetime.utcnow()
        self.update_risk_score()
        return self
    
    def mark_email_verified(self):
        """Mark email as verified"""
        self.verified_email = True
        self.email_verified_at = datetime.utcnow()
        self.email_verification_token = None
        self.update_risk_score()
        return self
    
    def mark_phone_verified(self):
        """Mark phone as verified"""
        self.verified_phone = True
        self.phone_verified_at = datetime.utcnow()
        self.phone_verification_token = None
        self.update_risk_score()
        return self
    
    def flag_suspicious_activity(self):
        """Flag suspicious activity and update score"""
        self.last_suspicious_activity = datetime.utcnow()
        self.login_attempt_count += 1
        self.update_risk_score()
        return self
    
    def approve(self, auto_approved=False):
        """Approve seller account"""
        self.is_approved = True
        self.approval_status = 'approved'
        self.auto_approved = auto_approved
        self.approved_at = datetime.utcnow()
        return self
    
    def reject(self, reason=''):
        """Reject seller account"""
        self.is_approved = False
        self.approval_status = 'rejected'
        self.suspension_reason = reason
        return self
    
    def flag_for_manual_review(self, reason=''):
        """Flag seller for manual review"""
        self.approval_status = 'manual_review'
        self.suspension_reason = reason
        return self
    
    def suspend(self, reason=''):
        """Suspend seller account"""
        self.is_suspended = True
        self.is_approved = False
        self.suspension_reason = reason
        return self
    
    def to_dict(self):
        """Convert seller to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'business_name': self.business_name,
            'business_phone': self.business_phone,
            'business_address': self.business_address,
            'verified_documents': self.verified_documents,
            'verified_phone': self.verified_phone,
            'verified_email': self.verified_email,
            'risk_score': round(self.risk_score, 2),
            'is_approved': self.is_approved,
            'approval_status': self.approval_status,
            'auto_approved': self.auto_approved,
            'is_suspended': self.is_suspended,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None
        }
    
    def __repr__(self):
        return f'<Seller {self.business_name}>'


class SellerApprovalLog(db.Model):
    """Audit log for seller approval process"""
    __tablename__ = 'seller_approval_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.id'), nullable=False, index=True)
    
    # Action details
    action = db.Column(db.String(50), nullable=False, index=True)  # 'auto_approved', 'manual_review', 'rejected', 'suspended', 'document_verified', etc.
    previous_status = db.Column(db.String(20), nullable=True)
    new_status = db.Column(db.String(20), nullable=True)
    previous_risk_score = db.Column(db.Float, nullable=True)
    new_risk_score = db.Column(db.Float, nullable=True)
    
    # Reason/Details
    reason = db.Column(db.Text, nullable=True)
    details = db.Column(db.JSON, default=dict)  # Additional context as JSON
    
    # Admin action (who approved/rejected manually)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    admin = db.relationship('User', foreign_keys=[admin_id])
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """Convert log entry to dictionary"""
        return {
            'id': self.id,
            'seller_id': self.seller_id,
            'action': self.action,
            'previous_status': self.previous_status,
            'new_status': self.new_status,
            'previous_risk_score': self.previous_risk_score,
            'new_risk_score': self.new_risk_score,
            'reason': self.reason,
            'details': self.details,
            'admin_id': self.admin_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<SellerApprovalLog {self.id} - {self.action}>'
