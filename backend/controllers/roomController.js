const roomModel = require('../models/roomModel');

async function deleteRoom(req, res) {
    try {
        const { id } = req.params;

        // Kiểm tra ID có hợp lệ không
        if (!id || isNaN(id)) {
            return res.status(400).json({
                success: false,
                message: 'ID phòng không hợp lệ'
            });
        }

        const result = await roomModel.deleteRoom(Number(id));

        if (!result.success) {
            return res.status(400).json(result);
        }

        return res.status(200).json(result);

    } catch (error) {
        console.error('Lỗi xóa phòng:', error);

        return res.status(500).json({
            success: false,
            message: 'Lỗi server khi xóa phòng'
        });
    }
}

module.exports = {
    deleteRoom
};