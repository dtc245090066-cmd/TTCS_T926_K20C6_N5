const crypto = require('crypto');
const { promisify } = require('util');
const pool = require('../config/db');

const scrypt = promisify(crypto.scrypt);

async function findActiveByUsername(username) {
    const [rows] = await pool.query(
        'SELECT id, username, password, full_name, role FROM users WHERE username = ? AND status = TRUE LIMIT 1',
        [username]
    );
    return rows[0] || null;
}

async function verifyAndUpgradePassword(account, password) {
    if (account.password.startsWith('scrypt$')) {
        const [, saltHex, hashHex] = account.password.split('$');
        if (!saltHex || !hashHex || !/^[0-9a-f]+$/i.test(saltHex + hashHex)) return false;

        const salt = Buffer.from(saltHex, 'hex');
        const expectedHash = Buffer.from(hashHex, 'hex');
        const submittedHash = await scrypt(password, salt, expectedHash.length);
        return expectedHash.length === submittedHash.length
            && crypto.timingSafeEqual(expectedHash, submittedHash);
    }

    const submittedPassword = Buffer.from(password);
    const storedPassword = Buffer.from(account.password);
    const matches = storedPassword.length === submittedPassword.length
        && crypto.timingSafeEqual(storedPassword, submittedPassword);
    if (!matches) return false;

    const salt = crypto.randomBytes(16);
    const hash = await scrypt(password, salt, 64);
    const upgradedPassword = `scrypt$${salt.toString('hex')}$${hash.toString('hex')}`;
    await pool.query(
        'UPDATE users SET password = ? WHERE id = ? AND password = ?',
        [upgradedPassword, account.id, account.password]
    );

    return true;
}

async function createSession(token, userId, expiresAt) {
    const tokenHash = crypto.createHash('sha256').update(token).digest('hex');
    await pool.query('DELETE FROM user_sessions WHERE expires_at <= NOW()');
    await pool.query(
        'INSERT INTO user_sessions (token_hash, user_id, expires_at) VALUES (?, ?, ?)',
        [tokenHash, userId, expiresAt]
    );
}

async function findActiveUserBySessionToken(token) {
    const tokenHash = crypto.createHash('sha256').update(token).digest('hex');
    const [rows] = await pool.query(
        `SELECT users.id, users.username, users.full_name, users.role
         FROM user_sessions
         INNER JOIN users ON users.id = user_sessions.user_id
         WHERE user_sessions.token_hash = ?
           AND user_sessions.expires_at > NOW()
           AND users.status = TRUE
         LIMIT 1`,
        [tokenHash]
    );
    return rows[0] || null;
}

async function deleteSession(token) {
    const tokenHash = crypto.createHash('sha256').update(token).digest('hex');
    await pool.query('DELETE FROM user_sessions WHERE token_hash = ?', [tokenHash]);
}

async function ensureSessionTable() {
    await pool.query(`
        CREATE TABLE IF NOT EXISTS user_sessions (
            token_hash CHAR(64) PRIMARY KEY,
            user_id INT NOT NULL,
            expires_at DATETIME NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_user_sessions_expiry (expires_at),
            CONSTRAINT fk_user_sessions_user
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    `);
}

module.exports = {
    createSession,
    deleteSession,
    ensureSessionTable,
    findActiveByUsername,
    findActiveUserBySessionToken,
    verifyAndUpgradePassword
};