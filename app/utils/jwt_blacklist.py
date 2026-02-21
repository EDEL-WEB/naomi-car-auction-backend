import redis
from flask import current_app
from datetime import timedelta


class JWTBlacklist:
    """JWT token blacklist using Redis"""
    
    _redis_client = None
    
    @classmethod
    def get_redis_client(cls):
        """Get or create Redis client"""
        if cls._redis_client is None:
            redis_url = current_app.config.get('REDIS_URL', 'redis://localhost:6379/0')
            cls._redis_client = redis.from_url(redis_url, decode_responses=True)
        return cls._redis_client
    
    @classmethod
    def add_token_to_blacklist(cls, jti, expires_in):
        """Add token JTI to blacklist with expiration"""
        try:
            redis_client = cls.get_redis_client()
            redis_client.setex(
                f"blacklist:{jti}",
                expires_in,
                "true"
            )
            return True
        except Exception as e:
            current_app.logger.error(f"Error adding token to blacklist: {str(e)}")
            return False
    
    @classmethod
    def is_token_blacklisted(cls, jti):
        """Check if token JTI is blacklisted"""
        try:
            redis_client = cls.get_redis_client()
            return redis_client.exists(f"blacklist:{jti}") > 0
        except Exception as e:
            current_app.logger.error(f"Error checking token blacklist: {str(e)}")
            return False
