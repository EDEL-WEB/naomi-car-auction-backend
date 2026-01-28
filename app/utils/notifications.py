"""Image notification system"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
from datetime import datetime


class ImageNotificationService:
    """Service for sending image-related notifications"""
    
    @staticmethod
    def init_smtp():
        """Initialize SMTP configuration"""
        return {
            'server': current_app.config.get('SMTP_SERVER'),
            'port': current_app.config.get('SMTP_PORT'),
            'username': current_app.config.get('SMTP_USERNAME'),
            'password': current_app.config.get('SMTP_PASSWORD'),
            'from_email': current_app.config.get('NOTIFICATION_EMAIL_FROM')
        }
    
    @staticmethod
    def send_email(to_email, subject, html_body, text_body=None):
        """Send email notification"""
        if not current_app.config.get('ENABLE_IMAGE_NOTIFICATIONS'):
            return False
        
        try:
            smtp_config = ImageNotificationService.init_smtp()
            
            if not all([smtp_config['username'], smtp_config['password']]):
                print('SMTP credentials not configured')
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = smtp_config['from_email']
            msg['To'] = to_email
            
            # Attach text and HTML versions
            if text_body:
                msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(smtp_config['server'], smtp_config['port']) as server:
                server.starttls()
                server.login(smtp_config['username'], smtp_config['password'])
                server.sendmail(
                    smtp_config['from_email'],
                    to_email,
                    msg.as_string()
                )
            
            return True
        except Exception as e:
            print(f'Error sending email: {str(e)}')
            return False
    
    @staticmethod
    def notify_image_uploaded(user_email, user_name, auction_title, image_count):
        """Notify user when image is uploaded"""
        subject = f'Image uploaded for {auction_title}'
        
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #2c3e50;">Image Upload Successful</h2>
                    
                    <p>Hello {user_name},</p>
                    
                    <p>Your image has been successfully uploaded to the auction:</p>
                    
                    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <strong>Auction:</strong> {auction_title}<br>
                        <strong>Total Images:</strong> {image_count}<br>
                        <strong>Uploaded at:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
                    </div>
                    
                    <p>You can manage your images anytime from your seller dashboard.</p>
                    
                    <p style="color: #666; font-size: 12px; margin-top: 30px;">
                        <strong>NaomiAutoHub</strong><br>
                        Luxury Car Auction Platform<br>
                        <a href="https://naomiautohub.com" style="color: #3498db; text-decoration: none;">Visit Platform</a>
                    </p>
                </div>
            </body>
        </html>
        """
        
        text_body = f"""
        Image Upload Successful
        
        Hello {user_name},
        
        Your image has been successfully uploaded to the auction:
        
        Auction: {auction_title}
        Total Images: {image_count}
        Uploaded at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
        
        You can manage your images anytime from your seller dashboard.
        
        NaomiAutoHub - Luxury Car Auction Platform
        """
        
        return ImageNotificationService.send_email(
            user_email,
            subject,
            html_body,
            text_body
        )
    
    @staticmethod
    def notify_image_deleted(user_email, user_name, auction_title, remaining_count):
        """Notify user when image is deleted"""
        subject = f'Image deleted from {auction_title}'
        
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #2c3e50;">Image Deleted</h2>
                    
                    <p>Hello {user_name},</p>
                    
                    <p>An image has been deleted from your auction:</p>
                    
                    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <strong>Auction:</strong> {auction_title}<br>
                        <strong>Remaining Images:</strong> {remaining_count}<br>
                        <strong>Deleted at:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
                    </div>
                    
                    <p>You can manage your images from your seller dashboard.</p>
                    
                    <p style="color: #666; font-size: 12px; margin-top: 30px;">
                        <strong>NaomiAutoHub</strong><br>
                        Luxury Car Auction Platform<br>
                        <a href="https://naomiautohub.com" style="color: #3498db; text-decoration: none;">Visit Platform</a>
                    </p>
                </div>
            </body>
        </html>
        """
        
        text_body = f"""
        Image Deleted
        
        Hello {user_name},
        
        An image has been deleted from your auction:
        
        Auction: {auction_title}
        Remaining Images: {remaining_count}
        Deleted at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
        
        NaomiAutoHub - Luxury Car Auction Platform
        """
        
        return ImageNotificationService.send_email(
            user_email,
            subject,
            html_body,
            text_body
        )
    
    @staticmethod
    def notify_auction_published_with_images(user_email, user_name, auction_title, image_count):
        """Notify user when auction is published with images"""
        subject = f'Your auction {auction_title} is now live!'
        
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #2c3e50;">🎉 Auction Now Live</h2>
                    
                    <p>Hello {user_name},</p>
                    
                    <p>Congratulations! Your auction is now published and live:</p>
                    
                    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <strong>Auction:</strong> {auction_title}<br>
                        <strong>Images:</strong> {image_count}<br>
                        <strong>Published at:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
                    </div>
                    
                    <p>Your auction with {image_count} high-quality images is now visible to all bidders on our platform.</p>
                    
                    <p>Monitor bids and activity from your seller dashboard.</p>
                    
                    <p style="color: #666; font-size: 12px; margin-top: 30px;">
                        <strong>NaomiAutoHub</strong><br>
                        Luxury Car Auction Platform<br>
                        <a href="https://naomiautohub.com" style="color: #3498db; text-decoration: none;">View Auction</a>
                    </p>
                </div>
            </body>
        </html>
        """
        
        text_body = f"""
        Auction Now Live
        
        Hello {user_name},
        
        Congratulations! Your auction is now published and live:
        
        Auction: {auction_title}
        Images: {image_count}
        Published at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
        
        NaomiAutoHub - Luxury Car Auction Platform
        """
        
        return ImageNotificationService.send_email(
            user_email,
            subject,
            html_body,
            text_body
        )
    
    @staticmethod
    def notify_bidder_image_quality(bidder_email, bidder_name, auction_title, image_count):
        """Notify bidder about high-quality images in an auction"""
        subject = f'{auction_title} has {image_count} high-quality images'
        
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #2c3e50;">📸 High-Quality Images Available</h2>
                    
                    <p>Hello {bidder_name},</p>
                    
                    <p>A luxury auction you're interested in has just been posted with high-quality images:</p>
                    
                    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <strong>Auction:</strong> {auction_title}<br>
                        <strong>Images:</strong> {image_count} professional photos<br>
                        <strong>Posted:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
                    </div>
                    
                    <p>Browse the detailed images and place your bid now!</p>
                    
                    <p style="color: #666; font-size: 12px; margin-top: 30px;">
                        <strong>NaomiAutoHub</strong><br>
                        Luxury Car Auction Platform<br>
                        <a href="https://naomiautohub.com" style="color: #3498db; text-decoration: none;">View Auction</a>
                    </p>
                </div>
            </body>
        </html>
        """
        
        text_body = f"""
        High-Quality Images Available
        
        Hello {bidder_name},
        
        A luxury auction with {image_count} high-quality images is now available:
        
        Auction: {auction_title}
        Images: {image_count}
        Posted: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
        
        NaomiAutoHub - Luxury Car Auction Platform
        """
        
        return ImageNotificationService.send_email(
            bidder_email,
            subject,
            html_body,
            text_body
        )
