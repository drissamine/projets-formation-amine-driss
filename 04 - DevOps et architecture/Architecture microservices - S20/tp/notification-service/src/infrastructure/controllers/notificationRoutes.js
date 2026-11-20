const express = require('express');
const router = express.Router();
const notificationController = require('./notificationController');

// Routes
router.post('/', notificationController.create);       // CREATE
router.get('/:id', notificationController.getById);  // READ

module.exports = router;
