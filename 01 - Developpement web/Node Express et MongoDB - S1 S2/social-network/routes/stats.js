const express = require('express');
const router = express.Router();
const User = require('../models/User');
const Post = require('../models/Post');
const Message = require('../models/Message');
const { cacheGet, cacheSet } = require('../config/redis');

// GET - Statistiques globales
router.get('/', async (req, res) => {
  try {
    // Statistiques utilisateurs
    const userStats = await User.aggregate([
      {
        $group: {
          _id: null,
          totalUsers: { $sum: 1 },
          avgFollowers: { $avg: "$nombreFollowers" },
          avgFollowing: { $avg: "$nombreFollowing" },
          avgPosts: { $avg: "$nombrePosts" }
        }
      }
    ]);

    // Statistiques posts
    const postStats = await Post.aggregate([
      {
        $group: {
          _id: null,
          totalPosts: { $sum: 1 },
          avgLikes: { $avg: "$nombreLikes" },
          avgComments: { $avg: { $size: "$commentaires" } }
        }
      }
    ]);

    // Statistiques messages
    const messageStats = await Message.aggregate([
      {
        $group: {
          _id: null,
          totalMessages: { $sum: 1 },
          unreadMessages: {
            $sum: {
              $cond: [{ $eq: ["$isRead", false] }, 1, 0]
            }
          }
        }
      }
    ]);

    // Posts les plus populaires
    const popularPosts = await Post.aggregate([
      { $sort: { nombreLikes: -1 } },
      { $limit: 5 },
      { $project: { contenu: 1, nombreLikes: 1, createdAt: 1 } }
    ]);

    // Utilisateurs les plus actifs
    const activeUsers = await User.aggregate([
      { $sort: { nombrePosts: -1 } },
      { $limit: 5 },
      { $project: { nom: 1, nombrePosts: 1, nombreFollowers: 1 } }
    ]);

    res.json({
      success: true,
      stats: {
        users: userStats[0] || {},
        posts: postStats[0] || {},
        messages: messageStats[0] || {},
        popularPosts,
        activeUsers
      }
    });
  } catch (err) {
    res.status(500).json({ success: false, erreur: err.message });
  }
});

// GET - Top 5 utilisateurs avec le plus de followers
router.get('/top-users', async (req, res) => {
  try {
    const cacheKey = 'top_users';
    
    // Vérifier le cache
    const cachedData = await cacheGet(cacheKey);
    if (cachedData) {
      return res.json(cachedData);
    }
    
    const topUsers = await User.aggregate([
      { $sort: { nombreFollowers: -1 } },
      { $limit: 5 },
      { $project: {
        nom: 1,
        nombreFollowers: 1,
        avatar: 1
      }}
    ]);

    const result = {
      success: true,
      count: topUsers.length,
      data: topUsers
    };
    
    // Mettre en cache pour 1 heure
    await cacheSet(cacheKey, result, 3600);
    
    res.json(result);
  } catch (err) {
    res.status(500).json({ success: false, erreur: err.message });
  }
});

// GET - Posts les plus likés
router.get('/top-posts', async (req, res) => {
  try {
    const cacheKey = 'top_posts';
    
    // Vérifier le cache
    const cachedData = await cacheGet(cacheKey);
    if (cachedData) {
      return res.json(cachedData);
    }
    
    const topPosts = await Post.aggregate([
      { $sort: { nombreLikes: -1 } },
      { $limit: 10 },
      { $lookup: {
        from: 'users',
        localField: 'auteur',
        foreignField: '_id',
        as: 'auteurDetail'
      }},
      { $unwind: "$auteurDetail" },
      { $project: {
        contenu: 1,
        nombreLikes: 1,
        createdAt: 1,
        'auteurDetail.nom': 1,
        'auteurDetail.avatar': 1
      }}
    ]);

    const result = {
      success: true,
      count: topPosts.length,
      data: topPosts
    };
    
    // Mettre en cache pour 30 minutes
    await cacheSet(cacheKey, result, 1800);
    
    res.json(result);
  } catch (err) {
    res.status(500).json({ success: false, erreur: err.message });
  }
});

// GET - Statistiques utilisateur
router.get('/users/:id', async (req, res) => {
  try {
    const userId = req.params.id;
    
    // Vérifier que l'utilisateur existe
    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({
        success: false,
        erreur: 'Utilisateur non trouvé'
      });
    }

    // Statistiques des posts de l'utilisateur
    const userPostStats = await Post.aggregate([
      { $match: { auteur: userId } },
      {
        $group: {
          _id: null,
          totalPosts: { $sum: 1 },
          totalLikes: { $sum: "$nombreLikes" },
          avgLikes: { $avg: "$nombreLikes" },
          totalComments: { $sum: { $size: "$commentaires" } }
        }
      }
    ]);

    // Statistiques des followers
    const followerStats = await User.aggregate([
      { $match: { _id: userId } },
      {
        $project: {
          followersCount: { $size: "$followers" },
          followingCount: { $size: "$following" }
        }
      }
    ]);

    res.json({
      success: true,
      userId,
      stats: {
        posts: userPostStats[0] || {},
        followers: followerStats[0] || {}
      }
    });
  } catch (err) {
    res.status(500).json({ success: false, erreur: err.message });
  }
});

module.exports = router;