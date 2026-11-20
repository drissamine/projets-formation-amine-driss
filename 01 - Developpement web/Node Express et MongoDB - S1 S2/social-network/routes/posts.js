const express = require('express');
const router = express.Router();
const Post = require('../models/Post');
const User = require('../models/User');
const { cacheGet, cacheSet, cacheDel } = require('../config/redis');
const { auth } = require('../middleware/auth');
const upload = require('../config/multer');

// GET - Tous les posts
router.get('/', async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;
    const cacheKey = `posts_page_${page}_limit_${limit}`;

    // Vérifier le cache
    const cachedData = await cacheGet(cacheKey);
    if (cachedData) {
      return res.json(cachedData);
    }

    const posts = await Post.find()
      .populate('auteur', 'nom avatar')
      .populate('commentaires.auteur', 'nom avatar')
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(limit);

    const total = await Post.countDocuments();

    const result = {
      success: true,
      count: posts.length,
      total,
      page,
      totalPages: Math.ceil(total / limit),
      data: posts
    };

    // Mettre en cache pour 2 minutes
    await cacheSet(cacheKey, result, 120);

    res.json(result);
  } catch (err) {
    res.status(500).json({ success: false, erreur: err.message });
  }
});

// GET - Posts d'un utilisateur
router.get('/user/:userId', async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;

    const posts = await Post.find({ auteur: req.params.userId })
      .populate('auteur', 'nom avatar')
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(limit);

    const total = await Post.countDocuments({ auteur: req.params.userId });

    res.json({
      success: true,
      count: posts.length,
      total,
      page,
      totalPages: Math.ceil(total / limit),
      data: posts
    });
  } catch (err) {
    res.status(500).json({ success: false, erreur: err.message });
  }
});

// POST - Creer un post avec upload d'images
router.post('/', auth, upload.array('images', 5), async (req, res) => {
  try {
    const { contenu } = req.body;
    console.log('DEBUG POST CREATION:');
    console.log('Body:', req.body);
    console.log('Files:', req.files);
    console.log('Content-Type:', req.headers['content-type']);

    const auteur = req.user.userId;

    if (!contenu) {
      console.log('Error: Contenu missing');
      return res.status(400).json({
        success: false,
        erreur: 'contenu obligatoire'
      });
    }

    // Récupérer les noms des fichiers uploadés
    const imageFilenames = req.files ? req.files.map(file => file.filename) : [];

    const post = await Post.create({
      contenu,
      auteur,
      images: imageFilenames
    });

    // Incrementer compteur posts de l'utilisateur
    await User.findByIdAndUpdate(auteur, { $inc: { nombrePosts: 1 } });

    // Invalider le cache des posts
    await cacheDel('posts_page_1_limit_10');

    res.status(201).json({
      success: true,
      message: 'Post cree',
      data: post
    });
  } catch (err) {
    res.status(400).json({ success: false, erreur: err.message });
  }
});

// PUT - Modifier un post
router.put('/:id', auth, async (req, res) => {
  try {
    const post = await Post.findById(req.params.id);

    if (!post) {
      return res.status(404).json({
        success: false,
        erreur: 'Post non trouve'
      });
    }

    // Vérifier que l'utilisateur est l'auteur du post
    if (post.auteur.toString() !== req.user.userId) {
      return res.status(403).json({
        success: false,
        erreur: 'Non autorise a modifier ce post'
      });
    }

    const updatedPost = await Post.findByIdAndUpdate(
      req.params.id,
      { contenu: req.body.contenu, updatedAt: Date.now() },
      { new: true }
    );

    // Invalider le cache
    await cacheDel('posts_page_1_limit_10');

    res.json({
      success: true,
      message: 'Post modifie',
      data: updatedPost
    });
  } catch (err) {
    res.status(400).json({ success: false, erreur: err.message });
  }
});

// DELETE - Supprimer
router.delete('/:id', auth, async (req, res) => {
  try {
    const post = await Post.findById(req.params.id);

    if (!post) {
      return res.status(404).json({
        success: false,
        erreur: 'Post non trouve'
      });
    }

    // Vérifier que l'utilisateur est l'auteur du post
    if (post.auteur.toString() !== req.user.userId) {
      return res.status(403).json({
        success: false,
        erreur: 'Non autorise a supprimer ce post'
      });
    }

    await Post.findByIdAndDelete(req.params.id);

    // Decrementer compteur
    await User.findByIdAndUpdate(post.auteur, { $inc: { nombrePosts: -1 } });

    // Invalider le cache
    await cacheDel('posts_page_1_limit_10');

    res.json({ success: true, message: 'Post supprime' });
  } catch (err) {
    res.status(500).json({ success: false, erreur: err.message });
  }
});

// POST - Liker un post 
router.post('/:id/like/:userId', async (req, res) => {
  try {
    const post = await Post.findById(req.params.id);

    if (!post) {
      return res.status(404).json({
        success: false,
        erreur: 'Post non trouve'
      });
    }

    if (!post.likes.includes(req.params.userId)) {
      post.likes.push(req.params.userId);
      post.nombreLikes++;
      await post.save();
    }

    res.json({ success: true, message: 'Like!' });
  } catch (err) {
    res.status(400).json({ success: false, erreur: err.message });
  }
});

// POST - Unliker 
router.post('/:id/unlike/:userId', async (req, res) => {
  try {
    const post = await Post.findById(req.params.id);

    if (!post) {
      return res.status(404).json({
        success: false,
        erreur: 'Post non trouve'
      });
    }

    post.likes = post.likes.filter(id => id.toString() !== req.params.userId);
    post.nombreLikes--;
    await post.save();

    res.json({ success: true, message: 'Unlike!' });
  } catch (err) {
    res.status(400).json({ success: false, erreur: err.message });
  }
});

// POST - Ajouter un commentaire 
router.post('/:id/comment', async (req, res) => {
  try {
    const { auteur, nom, avatar, texte } = req.body;

    const post = await Post.findByIdAndUpdate(
      req.params.id,
      {
        $push: {
          commentaires: {
            auteur,
            nom,
            avatar,
            texte
          }
        }
      },
      { new: true }
    );

    res.json({
      success: true,
      message: 'Commentaire ajoute',
      data: post
    });
  } catch (err) {
    res.status(400).json({ success: false, erreur: err.message });
  }
});

module.exports = router;
