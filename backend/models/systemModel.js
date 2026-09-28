const pool = require('../config/db');

async function getDatabaseName() {
    const [rows] = await pool.query('SELECT DATABASE() AS database_name');
    return rows[0].database_name;
}

module.exports = { getDatabaseName };