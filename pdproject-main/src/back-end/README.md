# Project Design Backend

This is a Node.js + Express backend for image uploads, using MongoDB as the database.

## Setup

1. Make sure MongoDB is running locally on your machine (default: mongodb://localhost:27017/onychomycosis).
2. Install dependencies:
   ```powershell
   cd src\back-end
   npm install
   ```
3. Start the server:
   ```powershell
   npm start
   ```

## API Endpoint

- `POST /api/upload` — Upload an image to the database.
  - Form field name: `image`
  - Accepts: image file (PNG, JPG, etc.)

## Notes
- Images are stored as binary data in MongoDB.
- You can connect your React frontend to this endpoint to save captured images.
