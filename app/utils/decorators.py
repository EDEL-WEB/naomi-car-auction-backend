from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from app.models.user import User


def token_required(f):
    """Decorator to require JWT token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            return f(current_user_id, *args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Unauthorized', 'message': str(e)}), 401
    
    return decorated_function


def role_required(allowed_roles):
    """Decorator to require specific roles. 
    Usage: @role_required('admin') or @role_required(['admin', 'seller'])
    """
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                user_role = claims.get('role')
                
                if user_role not in allowed_roles:
                    return jsonify({
                        'error': 'Forbidden',
                        'message': f'This endpoint requires one of these roles: {", ".join(allowed_roles)}'
                    }), 403
                
                user_id = get_jwt_identity()
                return f(user_id, *args, **kwargs)
            except Exception as e:
                return jsonify({'error': 'Unauthorized', 'message': str(e)}), 401
        
        return decorated_function
    return decorator


def admin_required(f):
    """Decorator to require admin role only"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get('role') != 'admin':
                return jsonify({'error': 'Forbidden', 'message': 'Admin access required'}), 403
            
            user_id = get_jwt_identity()
            return f(user_id, *args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Unauthorized', 'message': str(e)}), 401
    
    return decorated_function


def seller_required(f):
    """Decorator to require seller or admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get('role')
            
            if user_role not in ['seller', 'admin']:
                return jsonify({'error': 'Forbidden', 'message': 'Seller access required'}), 403
            
            user_id = get_jwt_identity()
            return f(user_id, *args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Unauthorized', 'message': str(e)}), 401
    
    return decorated_function


