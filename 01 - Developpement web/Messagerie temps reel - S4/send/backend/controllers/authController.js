const User = require('../models/User');
const { generateToken, generateRefreshToken } = require('../utils/jwt');

// @desc    Inscription d'un utilisateur
// @route   POST /api/auth/register
// @access  Public
const register = async (req, res) => {
  try {
    const { username, email, password } = req.body;

    // Validation des données
    if (!username || !email || !password) {
      return res.status(400).json({
        success: false,
        message: 'Veuillez remplir tous les champs requis.'
      });
    }

    // Vérifier si l'utilisateur existe déjà
    const existingUser = await User.findOne({
      $or: [{ email }, { username }]
    });

    if (existingUser) {
      return res.status(400).json({
        success: false,
        message: existingUser.email === email 
          ? 'Un utilisateur avec cet email existe déjà.' 
          : 'Ce nom d\'utilisateur est déjà pris.'
      });
    }

    // Créer le nouvel utilisateur
    const user = new User({
      username,
      email,
      password
    });

    await user.save();

    // Générer les tokens
    const token = generateToken({ userId: user._id });
    const refreshToken = generateRefreshToken({ userId: user._id });

    // Réponse sans le mot de passe
    const userResponse = user.toJSON();

    res.status(201).json({
      success: true,
      message: 'Inscription réussie.',
      data: {
        user: userResponse,
        token,
        refreshToken
      }
    });

  } catch (error) {
    console.error('Erreur lors de l\'inscription:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de l\'inscription.'
    });
  }
};

// @desc    Connexion d'un utilisateur
// @route   POST /api/auth/login
// @access  Public
const login = async (req, res) => {
  try {
    const { email, password } = req.body;

    // Validation des données
    if (!email || !password) {
      return res.status(400).json({
        success: false,
        message: 'Veuillez fournir l\'email et le mot de passe.'
      });
    }

    // Trouver l'utilisateur par email
    const user = await User.findOne({ email });
    if (!user) {
      return res.status(401).json({
        success: false,
        message: 'Identifiants invalides.'
      });
    }

    // Vérifier le mot de passe
    const isPasswordValid = await user.comparePassword(password);
    if (!isPasswordValid) {
      return res.status(401).json({
        success: false,
        message: 'Identifiants invalides.'
      });
    }

    // Mettre à jour le statut en ligne
    user.status = 'online';
    user.lastSeen = new Date();
    await user.save();

    // Générer les tokens
    const token = generateToken({ userId: user._id });
    const refreshToken = generateRefreshToken({ userId: user._id });

    // Réponse sans le mot de passe
    const userResponse = user.toJSON();

    res.json({
      success: true,
      message: 'Connexion réussie.',
      data: {
        user: userResponse,
        token,
        refreshToken
      }
    });

  } catch (error) {
    console.error('Erreur lors de la connexion:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de la connexion.'
    });
  }
};

// @desc    Déconnexion d'un utilisateur
// @route   POST /api/auth/logout
// @access  Private
const logout = async (req, res) => {
  try {
    // Mettre à jour le statut de l'utilisateur
    req.user.status = 'offline';
    req.user.lastSeen = new Date();
    await req.user.save();

    res.json({
      success: true,
      message: 'Déconnexion réussie.'
    });

  } catch (error) {
    console.error('Erreur lors de la déconnexion:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de la déconnexion.'
    });
  }
};

// @desc    Obtenir le profil de l'utilisateur connecté
// @route   GET /api/auth/profile
// @access  Private
const getProfile = async (req, res) => {
  try {
    res.json({
      success: true,
      data: {
        user: req.user
      }
    });

  } catch (error) {
    console.error('Erreur lors de la récupération du profil:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de la récupération du profil.'
    });
  }
};

// @desc    Mettre à jour le profil de l'utilisateur
// @route   PUT /api/auth/profile
// @access  Private
const updateProfile = async (req, res) => {
  try {
    const { username, email, avatar } = req.body;

    // Vérifier que les nouvelles données ne sont pas déjà utilisées
    if (username || email) {
      const existingUser = await User.findOne({
        _id: { $ne: req.user._id },
        $or: [
          ...(username ? [{ username }] : []),
          ...(email ? [{ email }] : [])
        ]
      });

      if (existingUser) {
        return res.status(400).json({
          success: false,
          message: existingUser.username === username 
            ? 'Ce nom d\'utilisateur est déjà pris.' 
            : 'Cet email est déjà utilisé.'
        });
      }
    }

    // Mettre à jour les champs fournis
    if (username) req.user.username = username;
    if (email) req.user.email = email;
    if (avatar) req.user.avatar = avatar;

    await req.user.save();

    res.json({
      success: true,
      message: 'Profil mis à jour avec succès.',
      data: {
        user: req.user
      }
    });

  } catch (error) {
    console.error('Erreur lors de la mise à jour du profil:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de la mise à jour du profil.'
    });
  }
};

// @desc    Renouveler le token
// @route   POST /api/auth/refresh
// @access  Public
const refreshToken = async (req, res) => {
  try {
    const { refreshToken } = req.body;

    if (!refreshToken) {
      return res.status(401).json({
        success: false,
        message: 'Refresh token requis.'
      });
    }

    const { verifyRefreshToken } = require('../utils/jwt');
    const decoded = verifyRefreshToken(refreshToken);

    // Récupérer l'utilisateur
    const user = await User.findById(decoded.userId).select('-password');
    if (!user) {
      return res.status(401).json({
        success: false,
        message: 'Utilisateur non trouvé.'
      });
    }

    // Générer de nouveaux tokens
    const newToken = generateToken({ userId: user._id });
    const newRefreshToken = generateRefreshToken({ userId: user._id });

    res.json({
      success: true,
      data: {
        token: newToken,
        refreshToken: newRefreshToken
      }
    });

  } catch (error) {
    console.error('Erreur lors du renouvellement du token:', error);
    res.status(401).json({
      success: false,
      message: 'Refresh token invalide.'
    });
  }
};

module.exports = {
  register,
  login,
  logout,
  getProfile,
  updateProfile,
  refreshToken
};
