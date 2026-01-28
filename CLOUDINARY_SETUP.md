# Cloudinary Integration & Image Notifications Setup Guide

## Overview

The NaomiAutoHub backend now integrates with Cloudinary for cloud-based image storage and includes an email notification system for image uploads and auction events.

## Features Added

### 1. Cloudinary Integration
- **Cloud Storage**: Images stored securely on Cloudinary instead of local disk
- **Auto-Optimization**: Automatic image compression and format optimization
- **CDN**: Global content delivery network for fast image loading
- **Transformations**: On-the-fly image transformations for different sizes and qualities
- **Backup**: Automatic backup and disaster recovery

### 2. Image Notifications
- Email notifications when images are uploaded
- Notifications when images are deleted
- Auction publication notifications
- Bidder notifications about high-quality image listings
- Customizable email templates with HTML formatting

### 3. User Roles
- **User**: Standard bidder
- **Seller**: Can create auctions and upload images
- **Admin**: Full platform management

## Setup Instructions

### Step 1: Create Cloudinary Account

1. Go to [Cloudinary.com](https://cloudinary.com/)
2. Sign up for a free account
3. Verify your email
4. Navigate to Dashboard → Settings → API Keys
5. Copy your:
   - Cloud Name
   - API Key
   - API Secret

### Step 2: Configure Environment Variables

Update your `.env` file with Cloudinary credentials:

```env
# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
CLOUDINARY_FOLDER=naomi-auction

# Image Configuration
IMAGE_QUALITY=85

# Email Notifications (Gmail example)
ENABLE_IMAGE_NOTIFICATIONS=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
NOTIFICATION_EMAIL_FROM=noreply@naomiautohub.com
```

### Step 3: Set Up Email Notifications

#### Using Gmail (Recommended)

1. Enable 2-Factor Authentication on your Gmail account
2. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Generate an App Password for "Mail" and "Windows Computer"
4. Use this app password in `SMTP_PASSWORD`

**Example Gmail Setup:**
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
NOTIFICATION_EMAIL_FROM=your_email@gmail.com
```

#### Using Other Email Services

**SendGrid:**
```env
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=SG.xxxxxxxxxxxxx
```

**Mailgun:**
```env
SMTP_SERVER=smtp.mailgun.org
SMTP_PORT=587
SMTP_USERNAME=postmaster@yourdomain.com
SMTP_PASSWORD=your_mailgun_password
```

### Step 4: Install Dependencies

```bash
pipenv install
```

New packages added:
- `cloudinary` - Cloudinary SDK
- `Pillow` - Image processing

### Step 5: Update Database

Run migrations to add new fields:

```bash
# Create migration for new fields
pipenv run flask db migrate -m "Add Cloudinary fields and role to users"

# Apply migration
pipenv run flask db upgrade
```

## Database Schema Changes

### Users Table
Added:
- `role` (String(20)) - User role: user, seller, admin

### CarImages Table
Updated with:
- `cloudinary_public_id` (String(500)) - Cloudinary public ID for deletions
- `width` (Integer) - Image width
- `height` (Integer) - Image height
- `file_size` (Integer) - File size in bytes

## API Usage

### Upload Image with Cloudinary

```bash
curl -X POST http://localhost:5000/api/images/auction/1 \
  -H "Authorization: Bearer <token>" \
  -F "image=@car.jpg" \
  -F "image_title=Front View" \
  -F "is_primary=true"
```

**Response:**
```json
{
  "message": "Image uploaded successfully",
  "data": {
    "id": 1,
    "auction_id": 1,
    "image_url": "https://res.cloudinary.com/your-cloud/image/upload/c_limit,h_1200,q_85,w_1600/naomi-auction/1/20240128_101530_Front%20View.jpg",
    "cloudinary_public_id": "naomi-auction/1/20240128_101530_Front View",
    "image_title": "Front View",
    "is_primary": true,
    "display_order": 0,
    "width": 1600,
    "height": 1200,
    "file_size": 245832,
    "uploaded_at": "2024-01-28T10:15:30"
  }
}
```

### Get Thumbnail URL

```python
from app.utils.image_utils import generate_thumbnail_url

thumbnail_url = generate_thumbnail_url('naomi-auction/1/image.jpg', width=300, height=300)
# Returns: https://res.cloudinary.com/.../c_limit,h_300,q_80,w_300/naomi-auction/1/image.jpg
```

## Image Notifications

### Upload Notification

Sent to seller when image is uploaded:

```
Subject: Image uploaded for [Auction Title]

Email includes:
- Auction name
- Total images count
- Upload timestamp
- Link to seller dashboard
```

### Deletion Notification

Sent to seller when image is deleted:

```
Subject: Image deleted from [Auction Title]

Email includes:
- Auction name
- Remaining images count
- Deletion timestamp
```

### Auction Publication

Sent to seller when auction goes live:

```
Subject: Your auction [Title] is now live!

Email includes:
- Auction name
- Number of images
- Publication timestamp
- Link to view auction
```

### Bidder Notification

Sent to interested bidders when new auction with images is posted:

```
Subject: [Title] has [N] high-quality images

Email includes:
- Auction name
- Image count
- Call to action to view and bid
```

## Notification Service Usage

```python
from app.utils.notifications import ImageNotificationService

# Notify image upload
ImageNotificationService.notify_image_uploaded(
    user_email='seller@example.com',
    user_name='John Doe',
    auction_title='2019 Ferrari 488 GTB',
    image_count=5
)

# Notify image deletion
ImageNotificationService.notify_image_deleted(
    user_email='seller@example.com',
    user_name='John Doe',
    auction_title='2019 Ferrari 488 GTB',
    remaining_count=4
)

# Notify auction publication
ImageNotificationService.notify_auction_published_with_images(
    user_email='seller@example.com',
    user_name='John Doe',
    auction_title='2019 Ferrari 488 GTB',
    image_count=5
)

# Notify bidders
ImageNotificationService.notify_bidder_image_quality(
    bidder_email='bidder@example.com',
    bidder_name='Jane Smith',
    auction_title='2019 Ferrari 488 GTB',
    image_count=5
)
```

## Image Upload Routes

### POST /api/images/auction/<auction_id>

Upload image to Cloudinary.

**Form Parameters:**
- `image` (file, required) - Image file
- `image_title` (string, optional) - Image title
- `is_primary` (boolean, optional) - Set as cover image

**Returns:** Image object with Cloudinary URL

### GET /api/images/auction/<auction_id>

Get all images for auction.

**Returns:** Array of image objects

### PUT /api/images/<image_id>

Update image metadata.

**JSON Body:**
```json
{
  "image_title": "Updated Title",
  "is_primary": true,
  "display_order": 0
}
```

### DELETE /api/images/<image_id>

Delete image (removes from Cloudinary and database).

## Image Transformations

### Available Transformations

```python
from app.utils.image_utils import get_cloudinary_url

# Full size (optimized)
url = get_cloudinary_url('naomi-auction/1/image.jpg')

# Thumbnail
url = get_cloudinary_url('naomi-auction/1/image.jpg', width=300, height=300)

# Medium size
url = get_cloudinary_url('naomi-auction/1/image.jpg', width=800, height=600)

# Custom quality
url = get_cloudinary_url('naomi-auction/1/image.jpg', quality=90)

# Combination
url = get_cloudinary_url('naomi-auction/1/image.jpg', width=400, height=300, quality=85)
```

### Frontend Image Usage

```javascript
// React example

// Original image
<img src={imageData.image_url} alt={imageData.image_title} />

// Thumbnail
<img src={imageData.image_url.replace('/upload/', '/upload/w_300,h_300/')} 
     alt={imageData.image_title} />

// Responsive image
<picture>
  <source media="(min-width: 1024px)" 
          srcSet={imageData.image_url} />
  <source media="(min-width: 768px)" 
          srcSet={imageData.image_url.replace('/upload/', '/upload/w_800,h_600/')} />
  <img src={imageData.image_url.replace('/upload/', '/upload/w_400,h_300/')} 
       alt={imageData.image_title} />
</picture>
```

## Security Considerations

1. **API Keys**: Never commit `.env` file to version control
2. **Signed URLs**: Use Cloudinary signed uploads for production
3. **User Validation**: Only sellers can upload to their auctions
4. **File Type Validation**: Restricted to image formats
5. **File Size Limits**: 5MB maximum per image
6. **Email Security**: Use app-specific passwords for email services

## Production Deployment

### Cloudinary Setup
1. Upgrade to a paid plan for production
2. Enable resource list
3. Configure folder structure for organization
4. Set up transformation presets for common sizes
5. Enable automatic backup to external storage

### Email Configuration
1. Use professional email service (SendGrid, Mailgun, AWS SES)
2. Set up SPF, DKIM, DMARC records
3. Configure sender reputation monitoring
4. Implement bounce handling
5. Set up email templates in service

### Monitoring
```python
# Log all image uploads
print(f'Image uploaded: {public_id}')

# Monitor notification success
if ImageNotificationService.notify_image_uploaded(...):
    print('Notification sent successfully')
else:
    print('Notification failed - check SMTP config')
```

## Troubleshooting

### Image Upload Fails: "Cloudinary not configured"
**Solution:** Check that all three Cloudinary env vars are set:
```bash
echo $CLOUDINARY_CLOUD_NAME
echo $CLOUDINARY_API_KEY
echo $CLOUDINARY_API_SECRET
```

### Images Not Displaying
**Solution:** Verify the image_url in response starts with `https://res.cloudinary.com/`

### Email Notifications Not Sending
**Solution:**
1. Check SMTP credentials are correct
2. Verify ENABLE_IMAGE_NOTIFICATIONS=true
3. Check SMTP_USERNAME and SMTP_PASSWORD
4. For Gmail: Verify app password is correct (not regular password)

### Rate Limiting on Cloudinary
**Solution:** Implement queue system for batch uploads (use Celery/RQ)

### Large File Upload Timeout
**Solution:** Configure Cloudinary unsigned uploads for frontend uploads

## Cost Estimation

### Cloudinary Free Plan
- 25 GB storage
- 25 GB bandwidth/month
- Perfect for development/testing

### Cloudinary Paid Plans
- Basic ($99/month): 500 GB storage, 1TB bandwidth
- Growth ($399/month): 2TB storage, 5TB bandwidth
- Enterprise: Custom pricing

### Email Service Costs
- Gmail: Free (with account)
- SendGrid: $20/month (up to 100k emails)
- Mailgun: $20/month (up to 50k emails)
- AWS SES: Pay per email (~$0.10 per 1000)

## Next Steps

1. Test image uploads with Cloudinary
2. Verify email notifications are sending
3. Set up image gallery in React frontend
4. Implement drag-drop image upload UI
5. Add image cropping tool
6. Set up automatic image optimization

## References

- [Cloudinary Documentation](https://cloudinary.com/documentation)
- [Cloudinary Python SDK](https://cloudinary.com/documentation/python_integration)
- [Python SMTP Documentation](https://docs.python.org/3/library/smtplib.html)
- [Email Best Practices](https://sendgrid.com/blog/email-best-practices/)

## Support

For issues:
1. Check .env file has all required variables
2. Verify Cloudinary credentials are correct
3. Test SMTP connection separately
4. Review application logs for error messages
5. Check Cloudinary dashboard for upload activity
