const express = require('express');
const cors = require('cors');
require('dotenv').config();

const pool = require('./config/db');

const app = express();

app.use(cors());
app.use(express.json());

app.get('/', (req, res) => {
    res.json({
        message: 'Hotel Management API is running'
    });
});

app.get('/api/test-db', async (req, res) => {
    try {
        const [rows] = await pool.query('SELECT DATABASE() AS database_name');

        res.json({
            message: 'Kết nối MySQL thành công',
            database: rows[0].database_name
        });
    } catch (error) {
        console.error(error);

        res.status(500).json({
            message: 'Kết nối MySQL thất bại',
            error: error.message
        });
    }
});

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
    console.log(`Server đang chạy tại http://localhost:${PORT}`);
});