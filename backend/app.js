const express = require('express');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const pool = require('./config/db');
const authRoutes = require('./routes/authRoutes');
const dashboardRoutes = require('./routes/dashboardRoutes');
const roomRoutes = require('./routes/roomRoutes');
const systemRoutes = require('./routes/systemRoutes');

const userModel = require('./models/userModel');

const app = express();

app.use(cors({ origin: true, credentials: true }));
app.use(express.json());

app.use('/api/auth', authRoutes);
app.use('/api/dashboard', dashboardRoutes);
app.use('/api/test-db', systemRoutes);
app.use('/api/rooms', roomRoutes);

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '..', 'frontend', 'index.html'));
});

const PORT = process.env.PORT || 3000;

app.use(express.static(path.join(__dirname, '..', 'frontend')));

async function startServer() {
    try {
        await userModel.ensureSessionTable();

        app.listen(PORT, () => {
            console.log(`Server đang chạy tại http://localhost:${PORT}`);
        });
    } catch (error) {
        console.error('Không thể khởi động server. Hãy kiểm tra cấu hình MySQL trong backend/.env.', error.message);
        process.exitCode = 1;
    }
}

startServer();