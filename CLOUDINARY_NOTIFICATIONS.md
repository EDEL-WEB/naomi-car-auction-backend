# Cloudinary & Notifications Integration Guide

## Overview

NaomiAutoHub now integrates Cloudinary for image storage and a comprehensive real-time notification system. This guide covers setup, usage, and best practices.

## Table of Contents
1. [Cloudinary Setup](#cloudinary-setup)
2. [Notification System](#notification-system)
3. [API Endpoints](#api-endpoints)
4. [Socket.io Events](#socketio-events)
5. [Best Practices](#best-practices)

---

## Cloudinary Setup

### What is Cloudinary?

Cloudinary is a cloud-based image and video management platform that provides:
- Cloud storage for images
- Automatic image optimization and transformation
- CDN delivery for fast loading
- Image cropping and resizing
- Format conversion and quality optimization

### Prerequisites

1. Create a Cloudinary account at https://cloudinary.com
2. Get your credentials from the Cloudinary dashboard:
   - Cloud Name
   - API Key
   - API Secret

### Environment Configuration

Add to your `.env` file:

```env
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

### How It Works

1. **Image Upload**: Users upload to Cloudinary (not your server)
2. **Cloud Storage**: Images stored on Cloudinary's secure servers
3. **Automatic Processing**: Images automatically optimized and resized
4. **CDN Delivery**: Images served from CDN for fast loading
5. **Database Storage**: Only Cloudinary URL and public ID stored in DB

### Benefits

- ✅ Unlimited storage (on Cloudinary plan)
- ✅ Automatic image optimization
- ✅ CDN acceleration globally
- ✅ Responsive image formats (WebP, AVIF)
- ✅ Reduced server load
- ✅ Advanced image transformations
- ✅ Secure image delivery

---

## Notification System

### Notification Types

The system supports multiple notification types:

1. **image_uploaded** - When a user uploads an image to an auction
2. **bid_placed** - When someone bids on an auction
3. **outbid** - When a user is outbid on an auction
4. **auction_ending** - When an auction is ending soon
5. **auction_won** - When a user wins an auction
6. **auction_no_bids** - When an auction ends without bids

### Features

- Real-time notifications via Socket.io
- User notification preferences
- Unread notification tracking
- Notification history
- Mark as read functionality

### Database Models

#### Notification Model
```python
{
    'id': int,
    'user_id': int,
    'type': str,  # image_uploaded, bid_placed, outbid, etc.
    'title': str,
    'message': str,
    'related_auction_id': int | null,
    'related_image_id': int | null,
    'is_read': bool,
    'created_at': datetime,
    'updated_at': datetime
}
```

#### NotificationPreference Model
```python
{
    'id': int,
    'user_id': int,
    'image_uploads': bool,      # Notify on image uploads
    'auction_updates': bool,    # Notify on auction updates
    'bid_notifications': bool,  # Notify on bids
    'auction_ending': bool,     # Notify when auctions ending
    'email_notifications': bool # Send email notifications
}
```

---

## API Endpoints

### Image Upload with Cloudinary

#### Upload Image
**POST** `/api/images/auction/<auction_id>`

Upload an image to Cloudinary.

**Request:**
```bash
curl -X POST http://localhost:5000/api/images/auction/1 \
  -H "Authorization: Bearer <token>" \
  -F "image=@car.jpg" \
  -F "image_title=Front View" \
  -F "is_primary=true"
```

**Response (201):**
```json
{
  "message": "Image uploaded successfully",
  "data": {
    "id": 1,
    "auction_id": 1,
    "image_url": "https://res.cloudinary.com/...",
    "cloudinary_public_id": "naomi-auction/1/20240128_101530",
    "image_title": "Front View",
    "is_primary": true,
    "display_order": 0,
    "uploaded_at": "2024-01-28T10:15:30"
  }
}
```

### Notification Endpoints

#### Get Notifications
**GET** `/api/notifications`

Get user's notifications.

**Query Parameters:**
- `page` (int): Page number - default: 1
- `per_page` (int): Items per page - default: 20
- `unread_only` (bool): Only unread - default: false

**Response (200):**
```json
{
  "message": "Notifications retrieved successfully",
  "data": {
    "notifications": [
      {
        "id": 1,
        "user_id": 1,
        "type": "bid_placed",
        "title": "New Bid Received",
        "message": "john_doe placed a bid of $250,000",
        "related_auction_id": 1,
        "related_image_id": null,
        "is_read": false,
        "created_at": "2024-01-28T10:15:30",
        "updated_at": "2024-01-28T10:15:30"
      }
    ],
    "total": 1,
    "pages": 1,
    "current_page": 1,
    "unread_count": 1
  }
}
```

#### Get Unread Count
**GET** `/api/notifications/unread-count`

Get count of unread notifications.

**Response (200):**
```json
{
  "message": "Unread count retrieved successfully",
  "data": {
    "unread_count": 3
  }
}
```

#### Get Single Notification
**GET** `/api/notifications/<notification_id>`

Get details of a specific notification.

**Response (200):**
```json
{
  "message": "Notification retrieved successfully",
  "data": { ... }
}
```

#### Mark as Read
**PUT** `/api/notifications/<notification_id>/read`

Mark a notification as read.

**Response (200):**
```json
{
  "message": "Notification marked as read",
  "data": { ... }
}
```

#### Mark All as Read
**PUT** `/api/notifications/mark-all-read`

Mark all notifications as read.

**Response (200):**
```json
{
  "message": "All notifications marked as read",
  "data": null
}
```

#### Delete Notification
**DELETE** `/api/notifications/<notification_id>`

Delete a notification.

**Response (200):**
```json
{
  "message": "Notification deleted successfully",
  "data": null
}
```

#### Get Preferences
**GET** `/api/notifications/preferences`

Get notification preferences.

**Response (200):**
```json
{
  "message": "Preferences retrieved successfully",
  "data": {
    "id": 1,
    "user_id": 1,
    "image_uploads": true,
    "auction_updates": true,
    "bid_notifications": true,
    "auction_ending": true,
    "email_notifications": false
  }
}
```

#### Update Preferences
**PUT** `/api/notifications/preferences`

Update notification preferences.

**Request Body:**
```json
{
  "image_uploads": true,
  "auction_updates": true,
  "bid_notifications": true,
  "auction_ending": true,
  "email_notifications": false
}
```

**Response (200):**
```json
{
  "message": "Preferences updated successfully",
  "data": { ... }
}
```

---

## Socket.io Events

### Real-time Notification Events

#### Connect
```javascript
socket.on('connection_response', (data) => {
  console.log('Connected to auction server', data);
});
```

#### Image Uploaded
```javascript
socket.on('image_uploaded', (data) => {
  console.log('Image uploaded:', {
    auction_id: data.auction_id,
    image: data.image
  });
});
```

#### Image Deleted
```javascript
socket.on('image_deleted', (data) => {
  console.log('Image deleted:', {
    auction_id: data.auction_id,
    image_id: data.image_id
  });
});
```

#### Images Reordered
```javascript
socket.on('images_reordered', (data) => {
  console.log('Images reordered:', {
    auction_id: data.auction_id,
    images: data.images
  });
});
```

#### New Notification
```javascript
socket.on('notification', (notification) => {
  console.log('New notification:', {
    type: notification.type,
    title: notification.title,
    message: notification.message
  });
  
  // Update UI with notification
  showNotificationBadge(notification);
});
```

### Example: Real-time Notification Dashboard

```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:5000');
const userId = getUserIdFromToken();

// Connect to socket
socket.on('connection_response', () => {
  console.log('Connected');
  joinUserRoom(userId);
});

// Listen for notifications
socket.on('notification', (notification) => {
  // Update notification count
  updateNotificationCount();
  
  // Show toast/alert
  showNotificationToast(notification);
  
  // Update notification list
  addNotificationToList(notification);
});

// Join user's notification room
function joinUserRoom(userId) {
  socket.emit('join_room', { room: `user_${userId}` });
}
```

---

## Best Practices

### Image Upload

1. **Validate Before Upload**
   ```javascript
   const validateImage = (file) => {
     const MAX_SIZE = 5 * 1024 * 1024; // 5MB
     const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
     
     if (!ALLOWED_TYPES.includes(file.type)) {
       throw new Error('Invalid file type');
     }
     if (file.size > MAX_SIZE) {
       throw new Error('File too large');
     }
   };
   ```

2. **Use Image Transformations**
   ```javascript
   // Get optimized image
   const optimizedUrl = `${imageUrl}?w=800&q=auto&f=auto`;
   
   // Get thumbnail
   const thumbnailUrl = `${imageUrl}?w=300&h=200&c=fill&q=auto&f=auto`;
   ```

3. **Lazy Load Images**
   ```html
   <img 
     src="placeholder.jpg"
     data-src="https://res.cloudinary.com/..."
     loading="lazy"
     alt="Car image"
   />
   ```

4. **Responsive Images**
   ```html
   <img 
     srcset="
       https://res.cloudinary.com/.../w_300 300w,
       https://res.cloudinary.com/.../w_600 600w,
       https://res.cloudinary.com/.../w_1200 1200w
     "
     sizes="(max-width: 600px) 300px, 100vw"
     src="https://res.cloudinary.com/.../w_600"
     alt="Car"
   />
   ```

### Notification Management

1. **Poll Unread Count**
   ```javascript
   // Check unread notifications every 30 seconds
   setInterval(async () => {
     const response = await fetch('/api/notifications/unread-count', {
       headers: { 'Authorization': `Bearer ${token}` }
     });
     const data = await response.json();
     updateNotificationBadge(data.data.unread_count);
   }, 30000);
   ```

2. **Auto-clear Old Notifications**
   ```javascript
   // Delete notifications older than 7 days
   const deleteOldNotifications = async () => {
     const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
     const notifications = await getNotifications();
     
     for (const notif of notifications) {
       if (new Date(notif.created_at) < sevenDaysAgo) {
         await deleteNotification(notif.id);
       }
     }
   };
   ```

3. **Group Notifications by Type**
   ```javascript
   const groupNotifications = (notifications) => {
     return notifications.reduce((groups, notif) => {
       if (!groups[notif.type]) {
         groups[notif.type] = [];
       }
       groups[notif.type].push(notif);
       return groups;
     }, {});
   };
   ```

### Performance Optimization

1. **Batch Delete**
   ```bash
   # Delete multiple notifications at once
   curl -X DELETE /api/notifications \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"notification_ids": [1, 2, 3]}'
   ```

2. **Pagination**
   ```javascript
   // Load notifications in chunks
   const loadNotifications = async (page = 1) => {
     const response = await fetch(`/api/notifications?page=${page}&per_page=50`, {
       headers: { 'Authorization': `Bearer ${token}` }
     });
     return response.json();
   };
   ```

3. **Cache Images**
   ```javascript
   // Cache Cloudinary URLs
   const imageCache = new Map();
   
   const getCachedImage = (publicId) => {
     if (imageCache.has(publicId)) {
       return imageCache.get(publicId);
     }
     const url = generateCloudinaryUrl(publicId);
     imageCache.set(publicId, url);
     return url;
   };
   ```

---

## Troubleshooting

### Cloudinary Issues

**Upload Fails with 401**
- Check CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET
- Verify Cloud Name is correct
- Ensure credentials are set in environment

**Images Not Optimizing**
- Verify eager transformations in config
- Check Cloudinary plan supports auto-format
- Ensure fetch_format is set to 'auto'

**Slow Image Loading**
- Use thumbnail URLs for thumbnails
- Enable lazy loading
- Use CDN endpoints
- Consider image format (WebP is smallest)

### Notification Issues

**Notifications Not Appearing**
- Check Socket.io is connected
- Verify user is in correct room
- Check notification preferences are enabled
- Look for JavaScript errors in console

**Duplicate Notifications**
- Check NotificationService for duplicate calls
- Verify bidding logic doesn't create multiple notifications
- Check for race conditions in async code

**Missing Notifications**
- Verify user_id is correct
- Check database for notification records
- Verify notification type matches the event
- Check Socket.io rooms are joined correctly

---

## Integration Examples

### React Component: Image Gallery with Upload

```jsx
import React, { useState, useEffect } from 'react';

function ImageGallery({ auctionId, token }) {
  const [images, setImages] = useState([]);
  const [uploading, setUploading] = useState(false);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('image', file);
    formData.append('image_title', file.name);
    formData.append('is_primary', images.length === 0);

    try {
      const response = await fetch(
        `/api/images/auction/${auctionId}`,
        {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` },
          body: formData
        }
      );
      const data = await response.json();
      setImages([...images, data.data]);
    } finally {
      setUploading(false);
    }
  };

  useEffect(() => {
    fetch(`/api/images/auction/${auctionId}`)
      .then(r => r.json())
      .then(d => setImages(d.data.images));
  }, [auctionId]);

  return (
    <div>
      <input type="file" onChange={handleUpload} disabled={uploading} />
      {images.map(img => (
        <img key={img.id} src={img.image_url} alt={img.image_title} />
      ))}
    </div>
  );
}
```

### React Component: Notification Center

```jsx
function NotificationCenter({ token }) {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const socket = useSocket();

  useEffect(() => {
    // Load initial notifications
    fetch('/api/notifications', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(r => r.json())
      .then(d => {
        setNotifications(d.data.notifications);
        setUnreadCount(d.data.unread_count);
      });

    // Listen for real-time notifications
    socket.on('notification', (notif) => {
      setNotifications(prev => [notif, ...prev]);
      setUnreadCount(prev => prev + 1);
    });
  }, [token, socket]);

  return (
    <div>
      <h2>Notifications ({unreadCount})</h2>
      {notifications.map(notif => (
        <NotificationItem
          key={notif.id}
          notification={notif}
          onRead={() => markAsRead(notif.id)}
        />
      ))}
    </div>
  );
}
```

---

## Migration Guide

### From Local Storage to Cloudinary

If migrating from local image storage:

```python
# Script to migrate existing images
from app.models.car_image import CarImage
from app.utils.cloudinary_utils import upload_to_cloudinary
import os

for image in CarImage.query.all():
    # Read local file
    local_path = f"uploads/{image.image_url}"
    if os.path.exists(local_path):
        # Upload to Cloudinary
        result = upload_to_cloudinary(open(local_path, 'rb'), image.auction_id)
        
        # Update database
        image.image_url = result['url']
        image.cloudinary_public_id = result['public_id']
        db.session.commit()
```

---

## Support

For issues:
1. Check Cloudinary dashboard for upload errors
2. Review Socket.io console logs
3. Check database for notification records
4. Look at Flask application logs
5. Verify environment variables are set

For more information:
- [Cloudinary Documentation](https://cloudinary.com/documentation)
- [Socket.io Documentation](https://socket.io/docs/)
- [Flask-SocketIO](https://flask-socketio.readthedocs.io/)
