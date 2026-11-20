const jwt = require('jsonwebtoken');
require('dotenv').config();

const generateToken = (payload) => {
  return jwt.sign(
    payload, 
    process.env.JWT_SECRET || 'votre-secret-jwt-par-defaut',
    { expiresIn: process.env.JWT_EXPIRE || '7d' }
  );
};

const verifyToken = (token) => {
  try {
    return jwt.verify(
      token, 
      process.env.JWT_SECRET || 'votre-secret-jwt-par-defaut'
    );
  } catch (error) {
    throw new Error('Token invalide');
  }
};

const decodeToken = (token) => {
  return jwt.decode(token);
};

const generateRefreshToken = (payload) => {
  return jwt.sign(
    payload,
    process.env.JWT_REFRESH_SECRET || 'votre-refresh-secret-jwt',
    { expiresIn: '30d' }
  );
};

const verifyRefreshToken = (token) => {
  try {
    return jwt.verify(
      token,
      process.env.JWT_REFRESH_SECRET || 'votre-refresh-secret-jwt'
    );
  } catch (error) {
    throw new Error('Refresh token invalide');
  }
};

module.exports = {
  generateToken,
  verifyToken,
  decodeToken,
  generateRefreshToken,
  verifyRefreshToken
};
