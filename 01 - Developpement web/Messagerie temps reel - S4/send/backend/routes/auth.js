const express = require('express');
const router = express.Router();
const { register, login, logout, getProfile, updateProfile, refreshToken } = require('../controllers/authController');
const { authMiddleware } = require('../middleware/auth');

// @desc    Inscription d'un utilisateur
// @route   POST /api/auth/register
// @access  Public
router.post('/register', register);

// @desc    Connexion d'un utilisateur
// @route   POST /api/auth/login
// @access  Public
router.post('/login', login);

// @desc    Déconnexion d'un utilisateur
// @route   POST /api/auth/logout
// @access  Private
router.post('/logout', authMiddleware, logout);

// @desc    Obtenir le profil de l'utilisateur connecté
// @route   GET /api/auth/profile
// @access  Private
router.get('/profile', authMiddleware, getProfile);

// @desc    Mettre à jour le profil de l'utilisateur
// @route   PUT /api/auth/profile
// @access  Private
router.put('/profile', authMiddleware, updateProfile);

// @desc    Renouveler le token
// @route   POST /api/auth/refresh
// @access  Public
router.post('/refresh', refreshToken);

// Note: Toutes les routes OAuth (Google et GitHub) ont été supprimées complètement

module.exports = router;
