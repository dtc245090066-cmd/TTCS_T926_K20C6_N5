const express = require('express');
const router = express.Router();

const roomController = require('../controllers/roomController');

// Xóa phòng
router.delete('/:id', roomController.deleteRoom);

module.exports = router;