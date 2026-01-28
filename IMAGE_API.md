# Car Images API Documentation

This document covers all image-related endpoints for the NaomiAutoHub auction platform.

## Image Endpoints

### Upload Image
**POST** `/images/auction/<auction_id>`

Upload an image for an auction. Only the auction seller can upload images.

**Authentication:** Required (Bearer token)

**Request:**
- Content-Type: `multipart/form-data`
- Parameters:
  - `image` (file, required): Image file (JPG, PNG, GIF, WebP, max 5MB)
  - `image_title` (string, optional): Title/description for the image
  - `is_primary` (boolean, optional): Set as primary/cover image - default: false
  - `display_order` (integer, optional): Order to display image

**Example:**
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
    "image_url": "/uploads/1_20240128_101530_car.jpg",
    "image_title": "Front View",
    "is_primary": true,
    "display_order": 0,
    "uploaded_at": "2024-01-28T10:15:30"
  }
}
```

### Get Auction Images
**GET** `/images/auction/<auction_id>`

Get all images for a specific auction.

**Response (200):**
```json
{
  "message": "Auction images retrieved successfully",
  "data": {
    "auction_id": 1,
    "images": [
      {
        "id": 1,
        "auction_id": 1,
        "image_url": "/uploads/1_20240128_101530_car.jpg",
        "image_title": "Front View",
        "is_primary": true,
        "display_order": 0,
        "uploaded_at": "2024-01-28T10:15:30"
      },
      {
        "id": 2,
        "auction_id": 1,
        "image_url": "/uploads/1_20240128_101545_interior.jpg",
        "image_title": "Interior",
        "is_primary": false,
        "display_order": 1,
        "uploaded_at": "2024-01-28T10:15:45"
      }
    ],
    "total": 2
  }
}
```

### Get Primary Image
**GET** `/images/auction/<auction_id>/primary`

Get the primary (cover) image for an auction. Returns the first image if no primary is set.

**Response (200):**
```json
{
  "message": "Primary image retrieved successfully",
  "data": {
    "id": 1,
    "auction_id": 1,
    "image_url": "/uploads/1_20240128_101530_car.jpg",
    "image_title": "Front View",
    "is_primary": true,
    "display_order": 0,
    "uploaded_at": "2024-01-28T10:15:30"
  }
}
```

### Get Image Details
**GET** `/images/<image_id>`

Get details about a specific image.

**Response (200):**
```json
{
  "message": "Image retrieved successfully",
  "data": {
    "id": 1,
    "auction_id": 1,
    "image_url": "/uploads/1_20240128_101530_car.jpg",
    "image_title": "Front View",
    "is_primary": true,
    "display_order": 0,
    "uploaded_at": "2024-01-28T10:15:30"
  }
}
```

### Update Image Metadata
**PUT** `/images/<image_id>`

Update image title, set as primary, or change display order. Only the auction seller can update images.

**Authentication:** Required (Bearer token)

**Request Body:**
```json
{
  "image_title": "Updated Title",
  "is_primary": true,
  "display_order": 0
}
```

**Response (200):**
```json
{
  "message": "Image updated successfully",
  "data": {
    "id": 1,
    "auction_id": 1,
    "image_url": "/uploads/1_20240128_101530_car.jpg",
    "image_title": "Updated Title",
    "is_primary": true,
    "display_order": 0,
    "uploaded_at": "2024-01-28T10:15:30"
  }
}
```

### Delete Image
**DELETE** `/images/<image_id>`

Delete an image from an auction. Only the auction seller can delete images. The image file is removed from storage.

**Authentication:** Required (Bearer token)

**Response (200):**
```json
{
  "message": "Image deleted successfully",
  "data": null
}
```

### Reorder Images
**POST** `/images/auction/<auction_id>/reorder`

Reorder images for an auction by specifying the new order of image IDs.

**Authentication:** Required (Bearer token)

**Request Body:**
```json
{
  "image_ids": [2, 1, 3]
}
```

Each image will be assigned a display_order matching its position in the array.

**Response (200):**
```json
{
  "message": "Images reordered successfully",
  "data": [
    {
      "id": 2,
      "auction_id": 1,
      "image_url": "/uploads/1_20240128_101545_interior.jpg",
      "image_title": "Interior",
      "is_primary": false,
      "display_order": 0,
      "uploaded_at": "2024-01-28T10:15:45"
    },
    {
      "id": 1,
      "auction_id": 1,
      "image_url": "/uploads/1_20240128_101530_car.jpg",
      "image_title": "Front View",
      "is_primary": false,
      "display_order": 1,
      "uploaded_at": "2024-01-28T10:15:30"
    },
    {
      "id": 3,
      "auction_id": 1,
      "image_url": "/uploads/1_20240128_101600_back.jpg",
      "image_title": "Rear View",
      "is_primary": false,
      "display_order": 2,
      "uploaded_at": "2024-01-28T10:16:00"
    }
  ]
}
```

## Image File Access

Uploaded images are served from the `/uploads/` endpoint:

```
http://localhost:5000/uploads/1_20240128_101530_car.jpg
```

Use this URL to display images in your frontend application.

## Image Requirements

### File Types
- **Allowed:** JPG, JPEG, PNG, GIF, WebP
- **Recommended:** JPEG or WebP for best compression

### File Size
- **Maximum:** 5 MB
- **Recommended:** 1-2 MB for faster loading

### Image Dimensions
- **Recommended:** 800x600 minimum
- **Aspect Ratio:** 4:3 or 16:9 recommended

## Best Practices

1. **Upload Primary Image First**
   ```bash
   curl -X POST http://localhost:5000/api/images/auction/1 \
     -H "Authorization: Bearer <token>" \
     -F "image=@cover.jpg" \
     -F "is_primary=true" \
     -F "image_title=Vehicle Cover Photo"
   ```

2. **Upload Multiple Angles**
   - Front view
   - Rear view
   - Side views
   - Interior shots
   - Engine bay
   - Detail shots

3. **Optimize Images Before Upload**
   - Resize to reasonable dimensions
   - Compress using tools like ImageOptim or TinyPNG
   - Use WebP format when possible

4. **Set Meaningful Titles**
   ```json
   {
     "image_title": "Front 3/4 View",
     "image_title": "Detailed Interior Dashboard",
     "image_title": "Engine Bay - Excellent Condition"
   }
   ```

5. **Organize Display Order**
   ```bash
   curl -X POST http://localhost:5000/api/images/auction/1/reorder \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{
       "image_ids": [1, 3, 2, 4, 5]
     }'
   ```

## Error Responses

### Invalid File Type
```json
{
  "error": "File type not allowed. Allowed types: jpg, jpeg, png, gif, webp"
}
```

### File Too Large
```json
{
  "error": "File too large. Maximum size: 5.0MB"
}
```

### Unauthorized
```json
{
  "error": "Unauthorized to upload images for this auction"
}
```

### Auction Not Found
```json
{
  "error": "Auction not found"
}
```

## Image Storage

By default, images are stored in the `./uploads/` directory relative to the project root.

To customize the storage location, set the `UPLOAD_FOLDER` environment variable:

```env
UPLOAD_FOLDER=/var/www/nao_hub/uploads
```

## Frontend Integration Example

```javascript
// React example for uploading an image

const uploadImage = async (auctionId, file, token) => {
  const formData = new FormData();
  formData.append('image', file);
  formData.append('image_title', file.name);
  formData.append('is_primary', true);

  const response = await fetch(
    `http://localhost:5000/api/images/auction/${auctionId}`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    }
  );

  const result = await response.json();
  return result.data;
};

// Get all images for an auction
const fetchAuctionImages = async (auctionId) => {
  const response = await fetch(
    `http://localhost:5000/api/images/auction/${auctionId}`
  );
  const result = await response.json();
  return result.data.images;
};

// Display primary image
const displayPrimaryImage = async (auctionId) => {
  const response = await fetch(
    `http://localhost:5000/api/images/auction/${auctionId}/primary`
  );
  const result = await response.json();
  return result.data.image_url;
};
```

## Advanced Usage

### Batch Upload
Upload multiple images efficiently:

```bash
for image in *.jpg; do
  curl -X POST http://localhost:5000/api/images/auction/1 \
    -H "Authorization: Bearer <token>" \
    -F "image=@$image" \
    -F "image_title=$image"
done
```

### Update Gallery
```javascript
// Fetch, display, and allow users to reorder images
async function updateImageGallery(auctionId, token) {
  const response = await fetch(`/api/images/auction/${auctionId}`);
  const images = await response.json();
  
  // Display in UI with drag-and-drop reordering
  displayGallery(images.data.images);
}

// Handle reordering
async function saveImageOrder(auctionId, imageIds, token) {
  const response = await fetch(
    `/api/images/auction/${auctionId}/reorder`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ image_ids: imageIds })
    }
  );
  return response.json();
}
```

## Troubleshooting

### Uploads Directory Permission Error
```bash
# Ensure uploads directory is writable
chmod 755 ./uploads
```

### Images Not Displaying
- Check that images exist in the uploads folder
- Verify the image_url is correct
- Check browser console for 404 errors
- Verify CORS settings are correct

### Storage Full
- Monitor disk usage in the uploads directory
- Implement cleanup of old images
- Consider cloud storage (AWS S3, Cloudinary, etc.)

## Future Enhancements

- Image compression on upload
- Thumbnail generation
- Image cropping tool
- Cloud storage integration (AWS S3)
- CDN support
- Watermarking
- Image filters/effects
- Video support
