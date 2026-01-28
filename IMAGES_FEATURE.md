# Car Images Feature - Implementation Summary

## Overview

The NaomiAutoHub backend now includes comprehensive car image management functionality, allowing users to upload, organize, and manage multiple images for each auction listing.

## What's Been Added

### 1. New Database Model
**CarImage Model** (`app/models/car_image.py`)
- Stores image metadata and URLs
- Links images to auctions
- Supports primary/cover image designation
- Maintains display order for gallery
- Tracks upload timestamps

Fields:
- `id` - Primary key
- `auction_id` - Foreign key to Auction
- `image_url` - Path to the uploaded image
- `image_title` - User-friendly title/description
- `is_primary` - Boolean flag for cover image
- `display_order` - Integer for gallery ordering
- `uploaded_at` - Timestamp of upload

### 2. Updated Auction Model
- Added relationship to CarImage model
- Updated `to_dict()` method to include images with `include_images=True`
- Supports fetching primary image and all images in order

### 3. New Routes Module
**Images Blueprint** (`app/routes/images.py`)

#### Endpoints:
1. **POST** `/api/images/auction/<auction_id>`
   - Upload new image
   - Requires: image file, optional title, optional is_primary flag
   - Returns: Image record with URL

2. **GET** `/api/images/auction/<auction_id>`
   - Get all images for an auction
   - Returns: Array of image objects with metadata

3. **GET** `/api/images/auction/<auction_id>/primary`
   - Get the primary/cover image
   - Returns: Single image object

4. **GET** `/api/images/<image_id>`
   - Get specific image details
   - Returns: Image object

5. **PUT** `/api/images/<image_id>`
   - Update image metadata (title, primary flag, order)
   - Returns: Updated image object

6. **DELETE** `/api/images/<image_id>`
   - Delete image (removes from DB and disk)
   - Returns: Success message

7. **POST** `/api/images/auction/<auction_id>/reorder`
   - Reorder images by providing array of image IDs
   - Updates display_order for all images
   - Returns: Reordered images array

### 4. File Upload Configuration
**Image Upload Settings:**
- Allowed formats: JPG, JPEG, PNG, GIF, WebP
- Maximum file size: 5 MB
- Storage location: `./uploads/` (configurable via `UPLOAD_FOLDER` env var)
- Filename generation: `{auction_id}_{timestamp}.{ext}`

### 5. Static File Serving
**New Endpoint:**
- `GET` `/uploads/<filename>` - Serve uploaded images
- Configured in app factory to serve files from uploads directory

### 6. Utility Module
**Image Utilities** (`app/utils/image_utils.py`)
- File validation functions
- Filename generation
- Image compression helpers
- Dimension detection (optional PIL support)

### 7. Documentation
**IMAGE_API.md** - Comprehensive guide including:
- All endpoint documentation
- Request/response examples
- Best practices for image uploads
- Frontend integration examples
- Troubleshooting guide
- Future enhancement suggestions

## Usage Examples

### Upload an Image
```bash
curl -X POST http://localhost:5000/api/images/auction/1 \
  -H "Authorization: Bearer <token>" \
  -F "image=@car.jpg" \
  -F "image_title=Front View" \
  -F "is_primary=true"
```

### Get All Images
```bash
curl http://localhost:5000/api/images/auction/1
```

### Display Image in Frontend
```html
<img src="http://localhost:5000/uploads/1_20240128_101530_car.jpg" 
     alt="Ferrari Front View">
```

### React Component Example
```javascript
const [images, setImages] = useState([]);

// Fetch images
useEffect(() => {
  fetch(`/api/images/auction/${auctionId}`)
    .then(res => res.json())
    .then(data => setImages(data.data.images));
}, [auctionId]);

// Display gallery
return (
  <div className="gallery">
    {images.map(img => (
      <img key={img.id} src={img.image_url} alt={img.image_title} />
    ))}
  </div>
);
```

## Database Schema

```sql
CREATE TABLE car_images (
  id SERIAL PRIMARY KEY,
  auction_id INTEGER NOT NULL REFERENCES auctions(id) ON DELETE CASCADE,
  image_url VARCHAR(500) NOT NULL,
  image_title VARCHAR(200),
  is_primary BOOLEAN DEFAULT FALSE,
  display_order INTEGER DEFAULT 0,
  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  INDEX idx_auction_primary (auction_id, is_primary)
);
```

## File Structure

```
naomi-car-auction-backend/
├── app/
│   ├── models/
│   │   └── car_image.py          [NEW] Car image model
│   ├── routes/
│   │   └── images.py              [NEW] Image endpoints
│   └── utils/
│       └── image_utils.py          [NEW] Image utilities
├── uploads/                        [NEW] Directory for uploaded files
│   └── .gitkeep
├── IMAGE_API.md                    [NEW] Image API documentation
├── .env.example                    [UPDATED] Added UPLOAD_FOLDER
├── .gitignore                      [UPDATED] Ignores uploads/*
└── ...
```

## Configuration

Add to `.env`:
```env
UPLOAD_FOLDER=./uploads
```

## Security Features

1. **File Type Validation**
   - Only allows image formats (JPG, PNG, GIF, WebP)
   - Validates file extension

2. **File Size Limits**
   - Maximum 5 MB per image
   - Prevents server storage overflow

3. **Authorization Checks**
   - Only auction sellers can upload/modify images
   - Uses JWT authentication
   - Verifies user ownership of auction

4. **Filename Sanitization**
   - Uses `secure_filename()` to prevent directory traversal
   - Generates unique timestamps to avoid collisions
   - Includes auction ID for organization

5. **Safe Deletion**
   - Validates ownership before deletion
   - Removes files from disk
   - Maintains referential integrity

## Integration with Auction Model

When fetching auction details, include images:

```python
auction = Auction.query.get(1)
auction_dict = auction.to_dict(include_images=True)
# Returns auction with:
# - primary_image: the cover image
# - images: array of all images in order
```

## Sample Data

The `load_sample_data.py` script now includes sample images for all test auctions:
- Up to 3 images per auction
- Primary images set for cover display
- Organized with meaningful titles

## API Response Format

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
      }
    ],
    "total": 1
  }
}
```

## Next Steps for Production

1. **Cloud Storage Integration**
   - Consider AWS S3, CloudFront CDN
   - Or Cloudinary for image hosting

2. **Image Optimization**
   - Implement automatic compression
   - Generate thumbnails
   - Use WebP format with fallbacks

3. **Advanced Features**
   - Image cropping tool
   - Drag-and-drop reordering UI
   - Image filters
   - Video support

4. **Performance**
   - Add caching headers
   - Implement lazy loading
   - Use CDN for faster delivery

5. **Monitoring**
   - Track storage usage
   - Monitor upload times
   - Log access patterns

## Testing

### Manual Testing
```bash
# Upload image
curl -X POST http://localhost:5000/api/images/auction/1 \
  -H "Authorization: Bearer <token>" \
  -F "image=@test.jpg" \
  -F "image_title=Test Image"

# Get all images
curl http://localhost:5000/api/images/auction/1

# View image
curl http://localhost:5000/uploads/1_20240128_101530_car.jpg

# Reorder images
curl -X POST http://localhost:5000/api/images/auction/1/reorder \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"image_ids": [2, 1]}'
```

## Troubleshooting

**Images not displaying:**
- Check uploads folder exists and is writable
- Verify image_url in database is correct
- Check file permissions

**Upload fails with "File too large":**
- Image exceeds 5 MB limit
- Compress image before uploading
- Use JPEG or WebP for smaller files

**Unauthorized error:**
- Ensure correct JWT token is provided
- Verify user is the auction seller
- Check token hasn't expired

## Support

For more details, see:
- [IMAGE_API.md](IMAGE_API.md) - Complete API reference
- [README.md](README.md) - General project documentation
- [SETUP.md](SETUP.md) - Setup and deployment guide
