const pool = require('../config/db');

async function getDashboardData() {
    const [rooms, [roomTypeRows]] = await Promise.all([
        pool.query(`
            SELECT rooms.id, rooms.room_number, rooms.floor, rooms.status, room_types.name AS room_type
            FROM rooms
            LEFT JOIN room_types ON room_types.id = rooms.room_type_id
            ORDER BY rooms.floor IS NULL, rooms.floor, rooms.room_number
        `),
        pool.query('SELECT COUNT(*) AS total FROM room_types')
    ]);

    return {
        rooms: rooms[0],
        totalRoomTypes: roomTypeRows[0].total
    };
}

// Xóa phòng
async function deleteRoom(roomId) {
    // Kiểm tra phòng có tồn tại không
    const [rooms] = await pool.query(
        'SELECT id, room_number, status FROM rooms WHERE id = ?',
        [roomId]
    );

    if (rooms.length === 0) {
        return {
            success: false,
            message: 'Không tìm thấy phòng'
        };
    }

    const room = rooms[0];

    // Không cho xóa phòng đang được sử dụng
    if (room.status !== 'AVAILABLE') {
        return {
            success: false,
            message: 'Không thể xóa phòng đang được sử dụng'
        };
    }

    // Kiểm tra phòng đã từng xuất hiện trong lịch sử đặt phòng chưa
    const [bookingDetails] = await pool.query(
        'SELECT id FROM booking_details WHERE room_id = ? LIMIT 1',
        [roomId]
    );

    if (bookingDetails.length > 0) {
        return {
            success: false,
            message: 'Không thể xóa phòng vì phòng đã có lịch sử đặt phòng'
        };
    }

    // Xóa phòng
    await pool.query(
        'DELETE FROM rooms WHERE id = ?',
        [roomId]
    );

    return {
        success: true,
        message: `Đã xóa phòng ${room.room_number}`
    };
}

module.exports = {
    getDashboardData,
    deleteRoom
};