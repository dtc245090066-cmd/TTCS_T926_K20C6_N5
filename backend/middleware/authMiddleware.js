const authController = require('../controllers/authController');
const userModel = require('../models/userModel');

async function loadAuthenticatedUser(req, res, next) {
    try {
        const token = authController.getSessionToken(req);
        req.authUser = token ? await userModel.findActiveUserBySessionToken(token) : null;
        next();
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Không thể xác thực phiên đăng nhập.' });
    }
}

module.exports = { loadAuthenticatedUser };