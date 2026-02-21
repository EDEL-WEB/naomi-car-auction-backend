from flask import jsonify
from datetime import datetime


def validate_auction_input(data):
    """Validate auction input data"""
    errors = []
    
    required_fields = ['title', 'description', 'starting_price', 'brand', 'car_model', 'year', 'ends_at']
    
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f'{field} is required')
    
    if 'starting_price' in data:
        try:
            price = float(data['starting_price'])
            if price <= 0:
                errors.append('starting_price must be greater than 0')
        except (ValueError, TypeError):
            errors.append('starting_price must be a valid number')
    
    if 'year' in data:
        try:
            year = int(data['year'])
            current_year = datetime.utcnow().year
            if year < 1900 or year > current_year:
                errors.append(f'year must be between 1900 and {current_year}')
        except (ValueError, TypeError):
            errors.append('year must be a valid number')
    
    if 'ends_at' in data:
        try:
            ends_at = datetime.fromisoformat(data['ends_at'].replace('Z', '+00:00'))
            if ends_at <= datetime.utcnow():
                errors.append('ends_at must be in the future')
        except (ValueError, TypeError, AttributeError):
            errors.append('ends_at must be a valid ISO datetime')
    
    return errors


def validate_bid_input(data):
    """Validate bid input data"""
    errors = []
    
    if 'bid_amount' not in data or not data['bid_amount']:
        errors.append('bid_amount is required')
    
    try:
        amount = float(data['bid_amount'])
        if amount <= 0:
            errors.append('bid_amount must be greater than 0')
    except (ValueError, TypeError):
        errors.append('bid_amount must be a valid number')
    
    return errors


def validate_user_input(data):
    """Validate user input data"""
    errors = []
    
    # Check required fields
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f'{field} is required')
    
    if 'username' in data and data['username']:
        if len(data['username']) < 3:
            errors.append('username must be at least 3 characters')
        if len(data['username']) > 80:
            errors.append('username must be at most 80 characters')
    
    if 'email' in data and data['email']:
        if '@' not in data['email'] or '.' not in data['email']:
            errors.append('email must be valid')
    
    if 'password' in data and data['password']:
        if len(data['password']) < 6:
            errors.append('password must be at least 6 characters')
    
    return errors


def error_response(message, status_code=400):
    """Generate error response"""
    return jsonify({'error': message}), status_code


def success_response(data, message='Success', status_code=200):
    """Generate success response"""
    return jsonify({'message': message, 'data': data}), status_code
