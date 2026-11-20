const express = require('express');
const router = express.Router();
const User = require('../models/User');
const jwt = require('jsonwebtoken');
const bcryptjs = require('bcryptjs');
const { cacheGet, cacheSet, cacheDel } = require('../config/redis');
const { auth } = require('../middleware/auth');

// GET - Tous les utilisateurs
router.get('/', async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;
    const cacheKey = `users_page_${page}_limit_${limit}`;

    // Vérifier le cache
    const cachedData = await cacheGet(cacheKey);
    if (cachedData) {
      return res.json(cachedData);
    }

    const users = await User.find().select('-motDePasse').skip(skip).limit(limit);
    const total = await User.countDocuments();

    const result = {
      success: true,
      count: users.length,
      total,
      page,
      totalPages: Math.ceil(total / limit),
      data: users
    };

    // Mettre en cache pour 5 minutes
    await cacheSet(cacheKey, result, 300);

    res.json(result);
  } catch (err) {
    res.status(500).json({ success: false, erreur: err.message });
  }
});

// GET - Profil utilisateur connecté
router.get('/me', auth, async (req, res) => {
  try {
    const user = await User.findById(req.user.userId).select('-motDePasse');
    if (!user) {
      return res.status(404).json({ success: false, erreur: 'Utilisateur non trouvé' });
    }
    res.json({ success: true, data: user });
  } catch (err) {
    res.status(500).json({ success: false, erreur: err.message });
  }
});

// GET - Un utilisateur par ID
router.get('/:id', async (req, res) => {
  try {
    const cacheKey = `user_${req.params.id}`;

    // Vérifier le cache
    const cachedData = await cacheGet(cacheKey);
    if (cachedData) {
      return res.json(cachedData);
    }

    const user = await User.findById(req.params.id)
      .populate('followers', 'nom avatar')
      .populate('following', 'nom avatar');

    if (!user) {
      return res.status(404).json({
        success: false,
        erreur: 'Utilisateur non trouve'
      });
    }

    const result = { success: true, data: user };

    // Mettre en cache pour 10 minutes
    await cacheSet(cacheKey, result, 600);

    res.json(result);
  } catch (err) {
    res.status(500).json({ success: false, erreur: err.message });
  }
});

// POST - Creer un utilisateur
router.post('/', async (req, res) => {
  try {
    const { nom, email, motDePasse } = req.body;

    if (!nom || !email || !motDePasse) {
      return res.status(400).json({
        success: false,
        erreur: 'nom, email et motDePasse obligatoires'
      });
    }

    // Verifier doublon
    const existing = await User.findOne({ email });
    if (existing) {
      return res.status(400).json({
        success: false,
        erreur: 'Email deja utilise'
      });
    }

    // Hachage manuel du mot de passe
    const salt = await bcryptjs.genSalt(10);
    const hashedPassword = await bcryptjs.hash(motDePasse, salt);

    const user = await User.create({
      nom,
      email,
      motDePasse: hashedPassword
    });

    // On ne renvoie pas le mot de passe
    user.motDePasse = undefined;

    res.status(201).json({
      success: true,
      message: 'Utilisateur cree',
      data: user
    });
  } catch (err) {
    res.status(400).json({
      success: false,
      erreur: err.message
    });
  }
});

// POST - Login utilisateur
router.post('/login', async (req, res) => {
  try {
    const { email, motDePasse } = req.body;

    if (!email || !motDePasse) {
      return res.status(400).json({
        success: false,
        erreur: 'Email et mot de passe obligatoires'
      });
    }

    // Trouver l'utilisateur
    const user = await User.findOne({ email }).select('+motDePasse');
    if (!user) {
      return res.status(401).json({
        success: false,
        erreur: 'Email ou mot de passe invalide'
      });
    }

    // Vérifier le mot de passe avec bcryptjs directement
    const isMatch = await bcryptjs.compare(motDePasse, user.motDePasse);
    if (!isMatch) {
      return res.status(401).json({
        success: false,
        erreur: 'Email ou mot de passe invalide'
      });
    }

    // Générer le token JWT
    const secret = process.env.JWT_SECRET || 'fallback_secret_key_12345';

    const token = jwt.sign(
      {
        userId: user._id,
        email: user.email,
        nom: user.nom
      },
      secret,
      { expiresIn: '1h' }
    );

    res.json({
      success: true,
      message: 'Connexion réussie',
      token,
      user: {
        _id: user._id,
        nom: user.nom,
        email: user.email
      }
    });
  } catch (err) {
    console.error('Login error:', err);
    res.status(500).json({ success: false, erreur: err.message });
  }
});

// PUT - Modifier un utilisateur
router.put('/:id', auth, async (req, res) => {
  try {
    // Vérifier que l'utilisateur ne modifie que son propre compte
    if (req.user.userId !== req.params.id) {
      return res.status(403).json({
        success: false,
        erreur: 'Non autorise a modifier ce compte'
      });
    }

    const user = await User.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true, runValidators: true }
    );

    if (!user) {
      return res.status(404).json({
        success: false,
        erreur: 'Utilisateur non trouve'
      });
    }

    // Invalider le cache pour cet utilisateur
    await cacheDel(`user_${req.params.id}`);

    res.json({
      success: true,
      message: 'Utilisateur modifie',
      data: user
    });
  } catch (err) {
    res.status(400).json({ success: false, erreur: err.message });
  }
});

// DELETE - Supprimer
router.delete('/:id', auth, async (req, res) => {
  try {
    // Vérifier que l'utilisateur ne supprime que son propre compte
    if (req.user.userId !== req.params.id) {
      return res.status(403).json({
        success: false,
        erreur: 'Non autorise a supprimer ce compte'
      });
    }

    const user = await User.findByIdAndDelete(req.params.id);

    if (!user) {
      return res.status(404).json({
        success: false,
        erreur: 'Utilisateur non trouve'
      });
    }

    // Invalider le cache
    await cacheDel(`user_${req.params.id}`);

    res.json({
      success: true,
      message: 'Utilisateur supprime'
    });
  } catch (err) {
    res.status(500).json({ success: false, erreur: err.message });
  }
});

router.post('/:id/follow/:followId', async (req, res) => {
  try {
    const user = await User.findById(req.params.id);
    const userToFollow = await User.findById(req.params.followId);

    if (!user || !userToFollow) {
      return res.status(404).json({
        success: false,
        erreur: 'Utilisateur non trouve'
      });
    }

    if (!user.following.includes(req.params.followId)) {
      user.following.push(req.params.followId);
      user.nombreFollowing++;

      userToFollow.followers.push(req.params.id);
      userToFollow.nombreFollowers++;

      await user.save();
      await userToFollow.save();
    }

    res.json({ success: true, message: 'Suivi!' });
  } catch (err) {
    res.status(400).json({ success: false, erreur: err.message });
  }
});

router.post('/:id/unfollow/:followId', async (req, res) => {
  try {
    const user = await User.findById(req.params.id);
    const userToUnfollow = await User.findById(req.params.followId);

    if (!user || !userToUnfollow) {
      return res.status(404).json({
        success: false,
        erreur: 'Utilisateur non trouve'
      });
    }

    user.following = user.following.filter(id => id.toString() !== req.params.followId);
    user.nombreFollowing--;

    userToUnfollow.followers = userToUnfollow.followers.filter(id => id.toString() !== req.params.id);
    userToUnfollow.nombreFollowers--;

    await user.save();
    await userToUnfollow.save();

    res.json({ success: true, message: 'Ne suivre plus!' });
  } catch (err) {
    res.status(400).json({ success: false, erreur: err.message });
  }
});

router.get('/:id/notifications', async (req, res) => {
  try {
    const Notification = require('../models/Notification');
    const notifications = await Notification.find({ userId: req.params.id }).sort({ createdAt: -1 });

    res.json({
      success: true,
      count: notifications.length,
      data: notifications
    });
  } catch (err) {
    res.status(500).json({ success: false, erreur: err.message });
  }
});

module.exports = router;
