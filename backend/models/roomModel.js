const pool = require('../config/db');

async function getDashboardData() {
    const [rooms, [roomTypeRows]] = await Promise.all([
        pool.query(`
            SELECT rooms.room_number, rooms.floor, rooms.status, room_types.name AS room_type
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

module.exports = { getDashboardData };