from app import db
from app.models.bid import Bid
from app.models.auction import Auction
from config import Config
from flask import current_app


class ProxyBiddingService:
    """Handle proxy/automatic bidding"""
    
    @classmethod
    def place_proxy_bid(cls, auction_id, user_id, max_bid):
        """Place a proxy bid - system will auto-bid up to max_bid"""
        auction = Auction.query.get(auction_id)
        
        if not auction:
            return {'error': 'Auction not found'}
        
        if auction.status != 'active':
            return {'error': 'Auction is not active'}
        
        # Check if user already has a proxy bid
        existing_proxy = Bid.query.filter_by(
            auction_id=auction_id,
            user_id=user_id,
            is_proxy=True,
            is_retracted=False
        ).order_by(Bid.timestamp.desc()).first()
        
        # Get current highest bid
        highest_bid = auction.bids.filter_by(is_retracted=False).order_by(Bid.bid_amount.desc()).first()
        
        # Calculate actual bid amount
        if not highest_bid:
            # First bid
            actual_bid = auction.starting_price
        else:
            # Check if max_bid can beat current highest
            if max_bid <= highest_bid.bid_amount:
                return {'error': f'Max bid must be higher than current price: {highest_bid.bid_amount}'}
            
            # Bid minimum increment above current
            actual_bid = highest_bid.bid_amount + Config.MINIMUM_BID_INCREMENT
            
            # Don't exceed max_bid
            if actual_bid > max_bid:
                actual_bid = max_bid
        
        # Create the bid
        bid = Bid(
            auction_id=auction_id,
            user_id=user_id,
            bid_amount=actual_bid,
            max_bid=max_bid,
            is_proxy=True
        )
        
        # Update auction current price
        auction.current_price = actual_bid
        
        # Check reserve
        if auction.reserve_price and actual_bid >= auction.reserve_price:
            auction.reserve_met = True
        
        db.session.add(bid)
        db.session.commit()
        
        # Check if we need to trigger other proxy bids
        cls._trigger_proxy_bids(auction_id, user_id)
        
        return {'success': True, 'bid': bid.to_dict()}
    
    @classmethod
    def _trigger_proxy_bids(cls, auction_id, exclude_user_id):
        """Trigger other users' proxy bids if they're outbid"""
        auction = Auction.query.get(auction_id)
        
        # Get all active proxy bids except the one that just bid
        proxy_bids = Bid.query.filter(
            Bid.auction_id == auction_id,
            Bid.is_proxy == True,
            Bid.is_retracted == False,
            Bid.user_id != exclude_user_id
        ).order_by(Bid.max_bid.desc()).all()
        
        for proxy_bid in proxy_bids:
            # Check if this proxy bid can still compete
            if proxy_bid.max_bid > auction.current_price:
                new_bid_amount = min(
                    auction.current_price + Config.MINIMUM_BID_INCREMENT,
                    proxy_bid.max_bid
                )
                
                # Create new bid
                new_bid = Bid(
                    auction_id=auction_id,
                    user_id=proxy_bid.user_id,
                    bid_amount=new_bid_amount,
                    max_bid=proxy_bid.max_bid,
                    is_proxy=True
                )
                
                auction.current_price = new_bid_amount
                
                # Check reserve
                if auction.reserve_price and new_bid_amount >= auction.reserve_price:
                    auction.reserve_met = True
                
                db.session.add(new_bid)
                db.session.commit()
                
                current_app.logger.info(f"Proxy bid triggered for user {proxy_bid.user_id} on auction {auction_id}")
                break  # Only trigger one proxy bid at a time
