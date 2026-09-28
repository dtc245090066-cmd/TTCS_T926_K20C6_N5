const systemModel = require('../models/systemModel');

async function testDatabase(req, res) {
    try {
        const database = await systemModel.getDatabaseName();
        res.json({
            message: 'Kết nối MySQL thành công',
            database
        });
    } catch (error) {
        console.error(error);
        res.status(500).json({
            message: 'Kết nối MySQL thất bại',
            error: error.message
        });
    }
}

module.exports = { testDatabase };