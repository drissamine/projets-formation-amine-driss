const express = require('express');
const router = express.Router();
const User = require('../models/User');
const Post = require('../models/Post');

// GET - Recherche globale
router.get('/', async (req, res) => {
  try {
    const query = req.query.q;
    
    if (!query) {
      return res.status(400).json({
        success: false,
        erreur: 'Paramètre de recherche "q" requis'
      });
    }

    // Recherche d'utilisateurs par nom
    const users = await User.find(
      { $text: { $search: query } },
      { score: { $meta: "textScore" } }
    ).sort({ score: { $meta: "textScore" } });

    // Recherche de posts par contenu
    const posts = await Post.find(
      { $text: { $search: query } },
      { score: { $meta: "textScore" } }
    ).sort({ score: { $meta: "textScore" } });

    res.json({
      success: true,
      results: {
        users: users,
        posts: posts
      }
    });
  } catch (err) {
    res.status(500).json({ success: false, erreur: err.message });
  }
});

module.exports = router;