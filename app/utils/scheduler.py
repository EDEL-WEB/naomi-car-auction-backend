from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from app import db
from app.models.auction import Auction
from app.models.bid import Bid
import logging

logger = logging.getLogger(__name__)


def close_expired_auctions(app):
    """Close auctions that have passed their end time"""
    try:
        with app.app_context():
            expired_auctions = Auction.query.filter(
                Auction.status == 'active',
                Auction.ends_at <= datetime.utcnow()
            ).all()
            
            for auction in expired_auctions:
                auction.status = 'closed'
                logger.info(f"Auto-closed auction {auction.id}: {auction.title}")
            
            if expired_auctions:
                db.session.commit()
                logger.info(f"Closed {len(expired_auctions)} expired auctions")
    
    except Exception as e:
        logger.error(f"Error closing expired auctions: {str(e)}")
        db.session.rollback()


def check_auction_extensions(app):
    """Check for last-minute bids and extend auctions"""
    try:
        with app.app_context():
            # Find auctions ending in next 2 minutes
            soon_ending = Auction.query.filter(
                Auction.status == 'active',
                Auction.auto_extend == True,
                Auction.ends_at <= datetime.utcnow() + timedelta(minutes=2),
                Auction.ends_at > datetime.utcnow()
            ).all()
            
            for auction in soon_ending:
                # Check if there was a bid in the last 2 minutes
                recent_bid = Bid.query.filter(
                    Bid.auction_id == auction.id,
                    Bid.is_retracted == False,
                    Bid.timestamp >= datetime.utcnow() - timedelta(minutes=2)
                ).first()
                
                if recent_bid:
                    # Extend by 2 minutes
                    auction.ends_at = auction.ends_at + timedelta(minutes=2)
                    logger.info(f"Extended auction {auction.id} by 2 minutes due to last-minute bid")
            
            if soon_ending:
                db.session.commit()
    
    except Exception as e:
        logger.error(f"Error checking auction extensions: {str(e)}")
        db.session.rollback()


def start_scheduler(app):
    """Start the auction scheduler"""
    scheduler = BackgroundScheduler()
    
    # Close expired auctions every minute
    scheduler.add_job(
        func=lambda: close_expired_auctions(app),
        trigger="interval",
        seconds=app.config.get('AUCTION_CHECK_INTERVAL', 60),
        id='close_expired_auctions',
        replace_existing=True
    )
    
    # Check for auction extensions every 30 seconds
    scheduler.add_job(
        func=lambda: check_auction_extensions(app),
        trigger="interval",
        seconds=30,
        id='check_auction_extensions',
        replace_existing=True
    )
    
    scheduler.start()
    app.logger.info("Auction scheduler started")
    return scheduler
