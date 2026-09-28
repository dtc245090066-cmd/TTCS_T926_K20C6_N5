const roomModel = require('../models/roomModel');

async function getDashboard(req, res) {
    try {
        if (!req.authUser) {
            return res.status(401).json({ message: 'Vui lòng đăng nhập để xem dữ liệu.' });
        }

        res.json(await roomModel.getDashboardData());
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Không thể tải sơ đồ phòng' });
    }
}

module.exports = { getDashboard };