from flask import request
from flask_socketio import emit, join_room, leave_room, rooms


def register_socket_events(socketio):
    """Register all Socket.io events"""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        print(f'Client {request.sid} connected')
        emit('connection_response', {
            'message': 'Connected to auction server',
            'data': 'Connected'
        })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        print(f'Client {request.sid} disconnected')
    
    @socketio.on('join_auction')
    def on_join_auction(data):
        """Join an auction room to receive real-time updates"""
        auction_id = data.get('auction_id')
        
        if not auction_id:
            emit('error', {'message': 'auction_id is required'})
            return
        
        room = f'auction_{auction_id}'
        join_room(room)
        
        emit('auction_joined', {
            'message': f'Joined auction {auction_id}',
            'auction_id': auction_id
        }, room=room)
        
        print(f'Client {request.sid} joined auction {auction_id}')
    
    @socketio.on('leave_auction')
    def on_leave_auction(data):
        """Leave an auction room"""
        auction_id = data.get('auction_id')
        
        if not auction_id:
            emit('error', {'message': 'auction_id is required'})
            return
        
        room = f'auction_{auction_id}'
        leave_room(room)
        
        emit('auction_left', {
            'message': f'Left auction {auction_id}',
            'auction_id': auction_id
        }, room=room)
        
        print(f'Client {request.sid} left auction {auction_id}')
    
    @socketio.on('bid_placed')
    def on_bid_placed(data):
        """Handle bid placed event from client (for validation if needed)"""
        auction_id = data.get('auction_id')
        
        if not auction_id:
            emit('error', {'message': 'auction_id is required'})
            return
        
        # Broadcast to all clients in the auction room
        room = f'auction_{auction_id}'
        emit('bid_update', {
            'auction_id': auction_id,
            'bid_amount': data.get('bid_amount'),
            'user_id': data.get('user_id'),
            'timestamp': data.get('timestamp')
        }, room=room)
        
        print(f'Bid placed on auction {auction_id}: {data.get("bid_amount")}')
    
    @socketio.on('auction_status_update')
    def on_auction_status_update(data):
        """Broadcast auction status updates"""
        auction_id = data.get('auction_id')
        
        if not auction_id:
            emit('error', {'message': 'auction_id is required'})
            return
        
        room = f'auction_{auction_id}'
        emit('status_changed', {
            'auction_id': auction_id,
            'status': data.get('status'),
            'message': data.get('message')
        }, room=room)
        
        print(f'Auction {auction_id} status changed to {data.get("status")}')
    
    @socketio.on('typing')
    def on_typing(data):
        """Handle typing events (for future comment feature)"""
        auction_id = data.get('auction_id')
        user_id = data.get('user_id')
        
        if auction_id:
            room = f'auction_{auction_id}'
            emit('user_typing', {
                'user_id': user_id,
                'auction_id': auction_id
            }, room=room, skip_sid=request.sid)
    
    @socketio.on('error')
    def handle_error(data):
        """Handle error messages"""
        print(f'Error from {request.sid}: {data}')
        emit('error_response', {
            'message': 'Error received',
            'error': data
        })
    
    @socketio.on_error_default
    def default_error_handler(e):
        """Default error handler"""
        print(f'Socket.io error: {str(e)}')
        emit('error', {'message': 'An error occurred', 'error': str(e)})
