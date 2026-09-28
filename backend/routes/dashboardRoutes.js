const express = require('express');
const dashboardController = require('../controllers/dashboardController');
const { loadAuthenticatedUser } = require('../middleware/authMiddleware');

const router = express.Router();

router.get('/', loadAuthenticatedUser, dashboardController.getDashboard);

module.exports = router;