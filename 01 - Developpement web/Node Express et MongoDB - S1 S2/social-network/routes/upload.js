const express = require('express');
const router = express.Router();
const upload = require('../config/multer');
const { auth } = require('../middleware/auth');

// POST - Upload d'une seule image
router.post('/single', auth, upload.single('image'), (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        success: false,
        erreur: 'Aucun fichier uploadé'
      });
    }
    
    res.json({
      success: true,
      message: 'Image uploadée avec succès',
      filename: req.file.filename,
      path: `/uploads/${req.file.filename}`,
      size: req.file.size,
      mimetype: req.file.mimetype
    });
  } catch (err) {
    res.status(500).json({ success: false, erreur: err.message });
  }
});

// POST - Upload de plusieurs images
router.post('/multiple', auth, upload.array('images', 5), (req, res) => {
  try {
    if (!req.files || req.files.length === 0) {
      return res.status(400).json({
        success: false,
        erreur: 'Aucun fichier uploadé'
      });
    }
    
    const filesInfo = req.files.map(file => ({
      filename: file.filename,
      path: `/uploads/${file.filename}`,
      size: file.size,
      mimetype: file.mimetype
    }));
    
    res.json({
      success: true,
      message: `${req.files.length} images uploadées avec succès`,
      count: req.files.length,
      files: filesInfo
    });
  } catch (err) {
    res.status(500).json({ success: false, erreur: err.message });
  }
});

// GET - Liste des images uploadées (pour développement)
router.get('/list', auth, (req, res) => {
  const fs = require('fs');
  const path = require('path');
  const uploadDir = path.join(__dirname, '../uploads');
  
  try {
    const files = fs.readdirSync(uploadDir);
    const images = files.filter(file => {
      const ext = path.extname(file).toLowerCase();
      return ['.jpg', '.jpeg', '.png', '.gif', '.webp'].includes(ext);
    });
    
    res.json({
      success: true,
      count: images.length,
      images
    });
  } catch (err) {
    res.status(500).json({ success: false, erreur: err.message });
  }
});

module.exports = router;