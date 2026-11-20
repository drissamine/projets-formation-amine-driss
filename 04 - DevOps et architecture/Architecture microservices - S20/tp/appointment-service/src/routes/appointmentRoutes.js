const express = require('express');
const router = express.Router();
const appointmentController = require('../infrastructure/controllers/appointmentController');
const authMiddleware = require('../config/authMiddleware');

// Apply JWT authentication to all routes
router.use(authMiddleware);

// CRUD Endpoints
router.post('/', appointmentController.create);       // CREATE
router.get('/:id', appointmentController.getById);    // READ
router.put('/:id/cancel', appointmentController.cancel); // UPDATE

module.exports = router;
