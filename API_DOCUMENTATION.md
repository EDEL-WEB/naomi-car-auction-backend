# NaomiAutoHub API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication
Most endpoints require JWT authentication. Include the access token in the request header:
```
Authorization: Bearer <access_token>
```

---

## Authentication Endpoints

### Register User
**POST** `/auth/register`

Create a new user account.

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password",
  "phone": "555-1234",
  "address": "123 Main St, City, State"
}
```

**Response (201):**
```json
{
  "message": "User created successfully",
  "data": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  }
}
```

### Login
**POST** `/auth/login`

Authenticate and receive JWT tokens.

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "secure_password"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "phone": "555-1234",
      "address": "123 Main St, City, State",
      "created_at": "2024-01-28T10:30:00"
    }
  }
}
```

### Refresh Token
**POST** `/auth/refresh`

Get a new access token using the refresh token.

**Headers:**
```
Authorization: Bearer <refresh_token>
```

**Response (200):**
```json
{
  "message": "Token refreshed successfully",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

### Logout
**POST** `/auth/logout`

Logout the current user.

**Response (200):**
```json
{
  "message": "Logout successful",
  "data": null
}
```

---

## Auction Endpoints

### List Auctions
**GET** `/auctions`

Get all auctions with optional filtering and pagination.

**Query Parameters:**
- `brand` (string): Filter by car brand
- `min_price` (number): Minimum price filter
- `max_price` (number): Maximum price filter
- `status` (string): Filter by status (active, closed, sold) - default: active
- `page` (integer): Page number - default: 1
- `per_page` (integer): Items per page - default: 20

**Example:**
```
GET /auctions?brand=Ferrari&min_price=100000&page=1
```

**Response (200):**
```json
{
  "message": "Auctions retrieved successfully",
  "data": {
    "auctions": [
      {
        "id": 1,
        "title": "2019 Ferrari 488 GTB",
        "description": "...",
        "starting_price": 250000,
        "current_price": 275000,
        "brand": "Ferrari",
        "car_model": "488 GTB",
        "year": 2019,
        "status": "active",
        "seller_id": 1,
        "created_at": "2024-01-28T10:00:00",
        "ends_at": "2024-02-04T10:00:00",
        "bid_count": 5,
        "is_active": true,
        "seller": { ... }
      }
    ],
    "total": 1,
    "pages": 1,
    "current_page": 1
  }
}
```

### Get Auction Details
**GET** `/auctions/<auction_id>`

Get detailed information about a specific auction.

**Response (200):**
```json
{
  "message": "Auction retrieved successfully",
  "data": {
    "id": 1,
    "title": "2019 Ferrari 488 GTB",
    "description": "...",
    "starting_price": 250000,
    "current_price": 275000,
    "brand": "Ferrari",
    "car_model": "488 GTB",
    "year": 2019,
    "status": "active",
    "seller_id": 1,
    "created_at": "2024-01-28T10:00:00",
    "ends_at": "2024-02-04T10:00:00",
    "bid_count": 5,
    "is_active": true,
    "seller": { ... },
    "car_specification": {
      "id": 1,
      "auction_id": 1,
      "brand": "Ferrari",
      "model": "488 GTB",
      "year": 2019,
      "mileage": 12500,
      "condition": "excellent",
      "fuel_type": "Gasoline",
      "transmission": "Automatic",
      "color": "Red",
      "engine": "V8 3.9L Turbo",
      "features": ["Carbon Fiber Trim", "Premium Sound System"]
    },
    "recent_bids": [
      {
        "id": 1,
        "auction_id": 1,
        "user_id": 2,
        "bid_amount": 275000,
        "timestamp": "2024-01-28T11:30:00",
        "user": { ... }
      }
    ]
  }
}
```

### Create Auction
**POST** `/auctions`

Create a new auction listing. Requires authentication.

**Request Body:**
```json
{
  "title": "2019 Ferrari 488 GTB",
  "description": "Stunning red Ferrari with excellent condition",
  "starting_price": 250000,
  "brand": "Ferrari",
  "car_model": "488 GTB",
  "year": 2019,
  "ends_at": "2024-02-04T10:00:00Z",
  "car_specification": {
    "mileage": 12500,
    "condition": "excellent",
    "fuel_type": "Gasoline",
    "transmission": "Automatic",
    "color": "Red",
    "engine": "V8 3.9L Turbo",
    "features": ["Carbon Fiber Trim", "Premium Sound System"]
  }
}
```

**Response (201):**
```json
{
  "message": "Auction created successfully",
  "data": {
    "id": 1,
    "title": "2019 Ferrari 488 GTB",
    ...
  }
}
```

### Update Auction
**PUT** `/auctions/<auction_id>`

Update an auction. Only the seller can update their auction.

**Request Body:**
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "status": "closed"
}
```

**Response (200):**
```json
{
  "message": "Auction updated successfully",
  "data": { ... }
}
```

### Delete Auction
**DELETE** `/auctions/<auction_id>`

Delete an auction. Only the seller can delete their auction.

**Response (200):**
```json
{
  "message": "Auction deleted successfully",
  "data": null
}
```

### Search Auctions
**GET** `/auctions/search?q=query`

Search auctions by title, description, or brand.

**Query Parameters:**
- `q` (string, required): Search query

**Response (200):**
```json
{
  "message": "Search completed successfully",
  "data": [
    { ... auction objects ... }
  ]
}
```

---

## Bid Endpoints

### Get Auction Bids
**GET** `/bids/auction/<auction_id>`

Get all bids for a specific auction.

**Query Parameters:**
- `page` (integer): Page number - default: 1
- `per_page` (integer): Items per page - default: 50

**Response (200):**
```json
{
  "message": "Bids retrieved successfully",
  "data": {
    "bids": [
      {
        "id": 1,
        "auction_id": 1,
        "user_id": 2,
        "bid_amount": 275000,
        "timestamp": "2024-01-28T11:30:00"
      }
    ],
    "total": 5,
    "pages": 1,
    "current_page": 1,
    "current_price": 275000,
    "highest_bidder_id": 2
  }
}
```

### Place Bid
**POST** `/bids/auction/<auction_id>`

Place a bid on an auction. Requires authentication.

**Request Body:**
```json
{
  "bid_amount": 280000
}
```

**Validation Rules:**
- Bid amount must be greater than current price
- Bid amount must be at least (current_price + minimum_increment)
- Auction must be active
- Auction must not have ended
- Seller cannot bid on their own auction

**Response (201):**
```json
{
  "message": "Bid placed successfully",
  "data": {
    "id": 2,
    "auction_id": 1,
    "user_id": 3,
    "bid_amount": 280000,
    "timestamp": "2024-01-28T11:45:00"
  }
}
```

**Error Response (400):**
```json
{
  "error": "Bid amount must be at least 275100 (current: 275000 + minimum increment: 100)"
}
```

### Get User Bids
**GET** `/bids/user`

Get all bids placed by the current user. Requires authentication.

**Query Parameters:**
- `page` (integer): Page number - default: 1
- `per_page` (integer): Items per page - default: 50

**Response (200):**
```json
{
  "message": "User bids retrieved successfully",
  "data": {
    "bids": [ ... ],
    "total": 3,
    "pages": 1,
    "current_page": 1
  }
}
```

### Get Specific Bid
**GET** `/bids/<bid_id>`

Get details about a specific bid.

**Response (200):**
```json
{
  "message": "Bid retrieved successfully",
  "data": {
    "id": 1,
    "auction_id": 1,
    "user_id": 2,
    "bid_amount": 275000,
    "timestamp": "2024-01-28T11:30:00",
    "user": { ... }
  }
}
```

---

## Favorite Endpoints

### Get User Favorites
**GET** `/favorites`

Get all favorited auctions for the current user. Requires authentication.

**Query Parameters:**
- `page` (integer): Page number - default: 1
- `per_page` (integer): Items per page - default: 20

**Response (200):**
```json
{
  "message": "Favorites retrieved successfully",
  "data": {
    "favorites": [
      {
        "id": 1,
        "user_id": 1,
        "auction_id": 1,
        "created_at": "2024-01-28T10:00:00",
        "auction": { ... }
      }
    ],
    "total": 3,
    "pages": 1,
    "current_page": 1
  }
}
```

### Add to Favorites
**POST** `/favorites/auction/<auction_id>`

Add an auction to the current user's favorites. Requires authentication.

**Response (201):**
```json
{
  "message": "Auction added to favorites",
  "data": {
    "id": 1,
    "user_id": 1,
    "auction_id": 1,
    "created_at": "2024-01-28T10:00:00",
    "auction": { ... }
  }
}
```

### Remove from Favorites
**DELETE** `/favorites/auction/<auction_id>`

Remove an auction from the current user's favorites. Requires authentication.

**Response (200):**
```json
{
  "message": "Auction removed from favorites",
  "data": null
}
```

### Check Favorite Status
**GET** `/favorites/auction/<auction_id>`

Check if an auction is in the current user's favorites. Requires authentication.

**Response (200):**
```json
{
  "message": "Favorite status retrieved successfully",
  "data": {
    "is_favorite": true,
    "favorite_id": 1
  }
}
```

---

## User Endpoints

### Get User Profile
**GET** `/users/profile`

Get the current user's profile. Requires authentication.

**Response (200):**
```json
{
  "message": "Profile retrieved successfully",
  "data": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "phone": "555-1234",
    "address": "123 Main St, City, State",
    "created_at": "2024-01-28T10:00:00"
  }
}
```

### Update User Profile
**PUT** `/users/profile`

Update the current user's profile. Requires authentication.

**Request Body:**
```json
{
  "email": "newemail@example.com",
  "phone": "555-5678",
  "address": "456 New Ave, Another City, State"
}
```

**Response (200):**
```json
{
  "message": "Profile updated successfully",
  "data": { ... }
}
```

### Get Public User Profile
**GET** `/users/<user_id>`

Get a user's public profile information.

**Response (200):**
```json
{
  "message": "User retrieved successfully",
  "data": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "phone": "555-1234",
    "address": "123 Main St",
    "created_at": "2024-01-28T10:00:00"
  }
}
```

### Get User Dashboard
**GET** `/users/dashboard`

Get comprehensive dashboard data for the current user. Requires authentication.

**Response (200):**
```json
{
  "message": "Dashboard retrieved successfully",
  "data": {
    "user": { ... },
    "statistics": {
      "total_auctions": 5,
      "active_auctions": 3,
      "total_bids": 12,
      "total_bid_amount": 850000,
      "highest_bidder_count": 2
    },
    "recent_auctions": [ ... ],
    "recent_bids": [ ... ]
  }
}
```

### Get User Auctions
**GET** `/users/<user_id>/auctions`

Get all auctions created by a specific user.

**Query Parameters:**
- `page` (integer): Page number - default: 1
- `per_page` (integer): Items per page - default: 20

**Response (200):**
```json
{
  "message": "User auctions retrieved successfully",
  "data": {
    "auctions": [ ... ],
    "total": 5,
    "pages": 1,
    "current_page": 1
  }
}
```

### Get User Bids
**GET** `/users/<user_id>/bids`

Get all bids placed by a specific user.

**Query Parameters:**
- `page` (integer): Page number - default: 1
- `per_page` (integer): Items per page - default: 50

**Response (200):**
```json
{
  "message": "User bids retrieved successfully",
  "data": {
    "bids": [ ... ],
    "total": 12,
    "pages": 1,
    "current_page": 1
  }
}
```

---

## Socket.io Events

### Client to Server Events

#### Join Auction
```javascript
socket.emit('join_auction', { auction_id: 1 });
// Received: { message: 'Joined auction 1', auction_id: 1 }
```

#### Leave Auction
```javascript
socket.emit('leave_auction', { auction_id: 1 });
// Received: { message: 'Left auction 1', auction_id: 1 }
```

#### Bid Placed
```javascript
socket.emit('bid_placed', {
  auction_id: 1,
  bid_amount: 280000,
  user_id: 3,
  timestamp: "2024-01-28T11:45:00"
});
```

#### Auction Status Update
```javascript
socket.emit('auction_status_update', {
  auction_id: 1,
  status: 'closed',
  message: 'Auction closed'
});
```

### Server to Client Events

#### Connection Response
```javascript
// Received on connection
{
  message: 'Connected to auction server',
  data: 'Connected'
}
```

#### Auction Joined
```javascript
{
  message: 'Joined auction 1',
  auction_id: 1
}
```

#### Auction Left
```javascript
{
  message: 'Left auction 1',
  auction_id: 1
}
```

#### New Bid
```javascript
{
  auction_id: 1,
  bid_amount: 280000,
  user_id: 3,
  timestamp: "2024-01-28T11:45:00",
  current_price: 280000
}
```

#### Bid Update
```javascript
{
  auction_id: 1,
  bid_amount: 280000,
  user_id: 3,
  timestamp: "2024-01-28T11:45:00"
}
```

#### Status Changed
```javascript
{
  auction_id: 1,
  status: 'closed',
  message: 'Auction closed due to end time'
}
```

#### User Typing
```javascript
{
  user_id: 2,
  auction_id: 1
}
```

---

## Error Responses

### Common Error Codes

**400 Bad Request**
```json
{
  "error": "Invalid request data"
}
```

**401 Unauthorized**
```json
{
  "error": "Unauthorized",
  "message": "Token has expired"
}
```

**403 Forbidden**
```json
{
  "error": "Unauthorized to perform this action"
}
```

**404 Not Found**
```json
{
  "error": "Resource not found"
}
```

**409 Conflict**
```json
{
  "error": "Resource already exists"
}
```

**500 Internal Server Error**
```json
{
  "error": "Internal server error"
}
```

---

## Rate Limiting
Currently not implemented. Can be added using Flask-Limiter.

## Pagination
Default limit: 20 items per page
Maximum limit: 100 items per page

## Timestamp Format
All timestamps are in ISO 8601 format (UTC):
```
2024-01-28T10:30:00
```

## CORS
CORS is enabled for all endpoints. Configure allowed origins in `.env`:
```
SOCKETIO_CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```
