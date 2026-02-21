-- Fix database permissions
GRANT ALL ON SCHEMA public TO car_auction;
GRANT ALL ON SCHEMA public TO public;
ALTER DATABASE car_auction OWNER TO car_auction;
