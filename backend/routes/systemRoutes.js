const express = require('express');
const systemController = require('../controllers/systemController');

const router = express.Router();

router.get('/', systemController.testDatabase);

module.exports = router;