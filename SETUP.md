# NaomiAutoHub Backend - Quick Start Guide

## Prerequisites

- Python 3.9+
- PostgreSQL installed and running
- Pipenv installed

## Setup Instructions

### 1. Create PostgreSQL Database

Open PostgreSQL and create the development database:

```bash
# Using psql
psql -U postgres
CREATE DATABASE naomi_auction_dev;
\q

# Or using createdb command
createdb -U postgres naomi_auction_dev
```

### 2. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and update the database connection string if needed:

```env
FLASK_ENV=development
FLASK_APP=run.py
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/naomi_auction_dev
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
SOCKETIO_CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

### 3. Install Dependencies

```bash
pipenv install
```

### 4. Activate Virtual Environment

```bash
pipenv shell
```

### 5. Initialize Database

```bash
python init_app.py
```

### 6. (Optional) Load Sample Data

```bash
python load_sample_data.py
```

This will create sample users and auctions for testing.

### 7. Start the Server

```bash
python run.py
```

The server will start on `http://localhost:5000`

### 8. Test the Server

Check the health endpoint:

```bash
curl http://localhost:5000/api/health
```

Response:
```json
{
  "status": "healthy"
}
```

## Testing the API

### Using cURL

#### Register a user:
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

#### Login:
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

#### Get auctions:
```bash
curl http://localhost:5000/api/auctions
```

#### Get auctions with filters:
```bash
curl "http://localhost:5000/api/auctions?brand=Ferrari&min_price=100000"
```

### Using Postman

1. Import the API endpoints into Postman
2. Set the base URL to `http://localhost:5000/api`
3. Create requests for each endpoint
4. For authenticated endpoints, add the access token in the Authorization header:
   ```
   Authorization: Bearer <access_token_from_login>
   ```

### Using Python Requests

```python
import requests
import json

BASE_URL = "http://localhost:5000/api"

# Register
response = requests.post(f"{BASE_URL}/auth/register", json={
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
})
print(response.json())

# Login
login_response = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "testuser",
    "password": "password123"
})
token = login_response.json()['data']['access_token']

# Get auctions
headers = {"Authorization": f"Bearer {token}"}
auctions = requests.get(f"{BASE_URL}/auctions", headers=headers)
print(auctions.json())
```

## Testing Socket.io Events

### Using Python client-socketio:

```bash
pip install python-socketio python-engineio
```

```python
import socketio

sio = socketio.Client()

@sio.on('connection_response')
def on_connect(data):
    print('Connected', data)
    sio.emit('join_auction', {'auction_id': 1})

@sio.on('auction_joined')
def on_auction_joined(data):
    print('Joined auction:', data)

@sio.on('new_bid')
def on_new_bid(data):
    print('New bid received:', data)

sio.connect('http://localhost:5000')
sio.wait()
```

### Using JavaScript client:

```html
<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
<script>
  const socket = io('http://localhost:5000');
  
  socket.on('connection_response', (data) => {
    console.log('Connected:', data);
    socket.emit('join_auction', { auction_id: 1 });
  });
  
  socket.on('auction_joined', (data) => {
    console.log('Joined auction:', data);
  });
  
  socket.on('new_bid', (data) => {
    console.log('New bid:', data);
  });
</script>
```

## Sample Test Users (if sample data loaded)

```
Username: john_doe          Email: john_doe@example.com
Username: jane_smith        Email: jane_smith@example.com
Username: collector_mike    Email: collector_mike@example.com
Username: luxury_buyer      Email: luxury_buyer@example.com

Password: password123 (for all test users)
```

## Running Tests

```bash
pytest
```

## Debugging

### Enable Flask Debug Mode

The app runs in debug mode when `FLASK_ENV=development`. This provides:
- Automatic server reload on code changes
- Interactive debugger on errors
- Detailed error pages

### View Database

Using psql:

```bash
psql -U postgres -d naomi_auction_dev

# List tables
\dt

# View users
SELECT * FROM users;

# View auctions
SELECT * FROM auctions;

# View bids
SELECT * FROM bids;

# Exit
\q
```

### Check Logs

Monitor the server output for request logs and errors.

## Troubleshooting

### Database Connection Error

```
Error: could not connect to server: Connection refused
```

**Solution:** Make sure PostgreSQL is running:

```bash
# macOS
brew services start postgresql

# Linux
sudo service postgresql start

# Windows
# Start PostgreSQL service from Services app
```

### Port Already in Use

```
Address already in use
```

**Solution:** Change the port in `run.py`:

```python
socketio.run(app, host='0.0.0.0', port=5001)  # Use different port
```

### JWT Token Expired

**Solution:** Use the refresh token endpoint to get a new access token:

```bash
curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Authorization: Bearer <refresh_token>"
```

### Database Locked

```
database is locked
```

**Solution:** Close any other connections to the database and try again.

## Production Deployment

For production deployment:

1. Change `FLASK_ENV` to `production`
2. Update `JWT_SECRET_KEY` to a strong random string
3. Use a production WSGI server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 run:app
   ```
4. Set up a reverse proxy (Nginx/Apache)
5. Use a PostgreSQL managed service (AWS RDS, Heroku, etc.)
6. Enable HTTPS/SSL
7. Configure proper CORS origins
8. Set up monitoring and logging

## Development Tips

- Use `flask shell` for interactive debugging
- Enable SQL logging: `SQLALCHEMY_ECHO=True` in config
- Use SQLAlchemy models directly in the shell for testing
- Keep migrations clean with meaningful messages
- Test endpoints with different user roles
- Monitor database queries for optimization

## Next Steps

1. Frontend Integration: Connect your React app to these endpoints
2. Add WebSocket tests
3. Implement advanced features:
   - Email notifications
   - Auction auto-close mechanism
   - Advanced search filters
   - User ratings/reviews
   - Payment integration
4. Add comprehensive error handling
5. Implement request rate limiting
6. Add request/response logging
7. Set up automated testing CI/CD pipeline

## Support

For issues or questions:
- Check the API_DOCUMENTATION.md for endpoint details
- Review model definitions in app/models/
- Check route implementations in app/routes/
- Review error messages and logs

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/)
- [Flask-SocketIO](https://flask-socketio.readthedocs.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

Happy coding!
