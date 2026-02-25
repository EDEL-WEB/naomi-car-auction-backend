from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt, verify_jwt_in_request, get_jwt_identity
from app import db, limiter
from app.models.user import User
from app.utils.validators import validate_user_input, error_response, success_response
from app.utils.jwt_blacklist import JWTBlacklist
from datetime import timedelta, datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per hour")
def register():
    """Register a new buyer or seller account
    
    Only 'buyer' and 'seller' roles allowed. Admin must be created via CLI command.
    Sellers require approval before they can login.
    """
    try:
        data = request.get_json()
        
        if not data:
            return error_response('No data provided', 400)
        
        # Validate input
        errors = validate_user_input(data)
        if errors:
            return error_response(', '.join(errors), 400)
        
        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return error_response('Username already exists', 409)
        
        if User.query.filter_by(email=data['email']).first():
            return error_response('Email already exists', 409)
        
        # Get requested role (default: "buyer")
        requested_role = data.get('role', 'buyer').lower()
        
        # REJECT admin role in public registration
        if requested_role == 'admin':
            return error_response('Cannot register as admin. Admin accounts must be created by system administrator.', 403)
        
        if requested_role not in ['buyer', 'seller']:
            return error_response('Invalid role. Must be "buyer" or "seller".', 400)
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            phone=data.get('phone'),
            address=data.get('address'),
            role=requested_role,
            approved=True if requested_role == 'buyer' else False  # Sellers need approval
        )
        
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        message = 'Account created successfully'
        if requested_role == 'seller':
            message = 'Seller account created. Awaiting admin approval to enable selling.'
        
        return success_response(
            user.to_dict(),
            message,
            201
        )
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return error_response(f'Error creating account: {str(e)}', 500)


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Login user and return JWT token
    
    Sellers must be approved before they can login.
    Buyers and admins can login immediately.
    """
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return error_response('Username and password required', 400)
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return error_response('Invalid username or password', 401)
    
    # Check if user is approved (sellers need approval)
    if user.role == 'seller' and not user.approved:
        return error_response(
            'Your seller account is pending admin approval. You will be able to login once approved.',
            403
        )
    
    # Create tokens with role information
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={'role': user.role}
    )
    refresh_token = create_refresh_token(
        identity=str(user.id),
        additional_claims={'role': user.role}
    )
    
    return success_response(
        {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        },
        'Login successful'
    )


@auth_bp.route('/refresh', methods=['POST'])
@limiter.limit("20 per hour")
def refresh():
    """Refresh access token using refresh token"""
    try:
        verify_jwt_in_request(refresh=True)
        user_id = get_jwt_identity()
        claims = get_jwt()
        
        new_access_token = create_access_token(
            identity=str(user_id),
            additional_claims={'role': claims.get('role', 'user')}
        )
        
        return success_response(
            {'access_token': new_access_token},
            'Token refreshed successfully'
        )
    except Exception as e:
        return error_response(f'Token refresh failed: {str(e)}', 401)


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user and blacklist token"""
    try:
        verify_jwt_in_request()
        jwt_data = get_jwt()
        jti = jwt_data['jti']
        exp = jwt_data['exp']
        
        # Calculate remaining time until token expiration
        expires_in = exp - int(datetime.utcnow().timestamp())
        
        if expires_in > 0:
            JWTBlacklist.add_token_to_blacklist(jti, expires_in)
        
        return success_response(None, 'Logout successful')
    except Exception as e:
        return error_response(f'Logout failed: {str(e)}', 500)
