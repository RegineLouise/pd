import express from 'express';
import mongoose from 'mongoose';
import multer from 'multer';
import path from 'path';
import { fileURLToPath } from 'url';

const app = express();
const PORT = process.env.PORT || 5000;

// MongoDB connection
mongoose.connect('mongodb://localhost:27017/onychomycosis', {
  useNewUrlParser: true,
  useUnifiedTopology: true,
});

const db = mongoose.connection;
db.on('error', console.error.bind(console, 'MongoDB connection error:'));
db.once('open', () => {
  console.log('Connected to MongoDB');
});

// Image Schema
const imageSchema = new mongoose.Schema({
  data: Buffer,
  contentType: String,
  createdAt: { type: Date, default: Date.now },
});
const Image = mongoose.model('Image', imageSchema);

// Multer setup for image upload
const storage = multer.memoryStorage();
const upload = multer({ storage });

app.use(express.json());

// Upload endpoint
app.post('/api/upload', upload.single('image'), async (req, res) => {
  try {
    const img = new Image({
      data: req.file.buffer,
      contentType: req.file.mimetype,
    });
    await img.save();
    res.status(201).json({ message: 'Image saved to database.' });
  } catch (err) {
    res.status(500).json({ error: 'Failed to save image.' });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
