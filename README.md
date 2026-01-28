# NaomiAutoHub - Luxury Car Auction Backend

A full-featured Flask backend for a luxury car auction platform with real-time bidding using Socket.io.

## Features

- **User Authentication**: JWT-based authentication with refresh tokens
- **Auction Management**: Create, read, update, and delete auctions
- **Real-time Bidding**: Socket.io integration for live bid updates
- **Bid Validation**: Automatic validation of bid amounts and auction status
- **Favorites System**: Users can save favorite auctions
- **User Dashboard**: Comprehensive dashboard with statistics
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Flask-Migrate for database versioning
- **CORS Support**: Ready for React frontend integration
- **Error Handling**: Comprehensive error handling and validation

## Project Structure

```
naomi-car-auction-backend/
├── app/
│   ├── __init__.py           # App factory
│   ├── models/               # Database models
│   │   ├── user.py          # User model
│   │   ├── auction.py       # Auction model
│   │   ├── bid.py           # Bid model
│   │   ├── favorite.py      # Favorite model
│   │   └── car_specification.py  # Car specs model
│   ├── routes/              # API endpoints
│   │   ├── auth.py          # Authentication routes
│   │   ├── auctions.py      # Auction routes
│   │   ├── bids.py          # Bid routes
│   │   ├── favorites.py     # Favorite routes
│   │   └── users.py         # User routes
│   ├── events/              # Socket.io events
│   │   └── socket_events.py # Real-time events
│   └── utils/               # Utility functions
│       ├── validators.py    # Input validators
│       └── decorators.py    # Custom decorators
├── config.py                # Configuration
├── run.py                   # Entry point
├── Pipfile                  # Dependencies
└── .env.example             # Environment variables template
```

## Installation

1. **Clone the repository** (if applicable)

2. **Install dependencies**:
   ```bash
   pipenv install
   ```

3. **Activate the virtual environment**:
   ```bash
   pipenv shell
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Create database** (PostgreSQL must be running):
   ```bash
   createdb naomi_auction_dev
   ```

6. **Run migrations**:
   ```bash
   flask db upgrade
   ```

## Running the Application

Start the development server:

```bash
python run.py
```

The server will start on `http://localhost:5000`

### Health Check
```bash
curl http://localhost:5000/api/health
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout user

### Auctions
- `GET /api/auctions` - List all auctions (with filtering)
- `GET /api/auctions/<id>` - Get auction details
- `POST /api/auctions` - Create new auction
- `PUT /api/auctions/<id>` - Update auction
- `DELETE /api/auctions/<id>` - Delete auction
- `GET /api/auctions/search?q=query` - Search auctions

### Bids
- `GET /api/bids/auction/<auction_id>` - Get auction bids
- `POST /api/bids/auction/<auction_id>` - Place a bid
- `GET /api/bids/user` - Get user's bids
- `GET /api/bids/<id>` - Get specific bid

### Favorites
- `GET /api/favorites` - Get user's favorites
- `POST /api/favorites/auction/<auction_id>` - Add to favorites
- `DELETE /api/favorites/auction/<auction_id>` - Remove from favorites
- `GET /api/favorites/auction/<auction_id>` - Check if favorited

### Users
- `GET /api/users/profile` - Get current user profile
- `PUT /api/users/profile` - Update profile
- `GET /api/users/<id>` - Get user public profile
- `GET /api/users/dashboard` - Get user dashboard
- `GET /api/users/<id>/auctions` - Get user's auctions
- `GET /api/users/<id>/bids` - Get user's bids

## Socket.io Events

### Client -> Server
- `join_auction` - Join real-time updates for an auction
- `leave_auction` - Leave auction room
- `bid_placed` - Notify bid placement
- `auction_status_update` - Update auction status

### Server -> Client
- `connection_response` - Connection confirmation
- `auction_joined` - Joined auction room
- `auction_left` - Left auction room
- `new_bid` - New bid placed
- `bid_update` - Bid update notification
- `status_changed` - Auction status changed
- `user_typing` - User typing indicator

## Database Models

### User
- username (unique)
- email (unique)
- password_hash
- phone
- address
- created_at

### Auction
- title
- description
- starting_price
- current_price
- brand
- car_model
- year
- status (active, closed, sold)
- seller_id (FK)
- created_at
- ends_at

### Bid
- auction_id (FK)
- user_id (FK)
- bid_amount
- timestamp

### Favorite
- user_id (FK)
- auction_id (FK)
- created_at

### CarSpecification
- auction_id (FK, unique)
- brand
- model
- year
- mileage
- condition
- fuel_type
- transmission
- color
- engine
- features (JSON)

## Configuration

Edit `config.py` to customize:
- Database URI
- JWT settings
- Bid increment minimum
- Auction check interval
- Socket.io CORS origins

## Error Handling

All endpoints return JSON responses with consistent format:

Success:
```json
{
  "message": "Success message",
  "data": {}
}
```

Error:
```json
{
  "error": "Error message"
}
```

## Security Features

- JWT authentication with expiring tokens
- Password hashing with Werkzeug
- CORS enabled for frontend
- Input validation on all endpoints
- SQL injection prevention via SQLAlchemy ORM

## Development

### Create migrations after model changes:
```bash
flask db migrate -m "Description"
flask db upgrade
```

### Run tests (if added):
```bash
pytest
```

## Environment Variables

Required in `.env`:
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - Secret key for JWT signing
- `FLASK_ENV` - Environment (development/production)
- `SOCKETIO_CORS_ALLOWED_ORIGINS` - Allowed origins for Socket.io

Optional:
- `PORT` - Server port (default: 5000)

## License

This project is part of the NaomiAutoHub platform.

## Support

For issues or questions, please contact the development team.
