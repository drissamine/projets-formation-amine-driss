const jwt = require('jsonwebtoken');

function auth(req, res, next) {
  const token = req.header('Authorization')?.replace('Bearer ', '');
  if (!token) return res.status(401).json({ erreur: 'Non autorise' }); 
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next(); 
  } catch (err) {
    res.status(400).json({ erreur: 'Token invalide' });
  }
}

// Middleware pour vérifier si l'utilisateur est admin
function adminAuth(req, res, next) {
  const token = req.header('Authorization')?.replace('Bearer ', '');
  if (!token) return res.status(401).json({ erreur: 'Non autorise' });
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    if (!decoded.isAdmin) {
      return res.status(403).json({ erreur: 'Acces interdit' });
    }
    req.user = decoded;
    next();
  } catch (err) {
    res.status(400).json({ erreur: 'Token invalide' });
  }
}

module.exports = { auth, adminAuth };