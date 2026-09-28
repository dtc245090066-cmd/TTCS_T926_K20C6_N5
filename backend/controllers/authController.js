const crypto = require('crypto');
const userModel = require('../models/userModel');

const SESSION_COOKIE = 'hotel_session';
const SESSION_DURATION_MS = 8 * 60 * 60 * 1000;

function getSessionToken(req) {
    const cookies = req.headers.cookie || '';
    const cookie = cookies.split(';').map((value) => value.trim())
        .find((value) => value.startsWith(`${SESSION_COOKIE}=`));
    return cookie ? decodeURIComponent(cookie.slice(SESSION_COOKIE.length + 1)) : null;
}

function setSessionCookie(res, token, maxAgeSeconds) {
    const secure = process.env.NODE_ENV === 'production' ? '; Secure' : '';
    res.setHeader('Set-Cookie', `${SESSION_COOKIE}=${encodeURIComponent(token)}; HttpOnly; SameSite=Lax; Path=/; Max-Age=${maxAgeSeconds}${secure}`);
}

async function login(req, res) {
    try {
        const username = String(req.body.username || '').trim();
        const password = String(req.body.password || '');

        if (!username || !password) {
            return res.status(400).json({ message: 'Vui lòng nhập tên đăng nhập và mật khẩu.' });
        }

        const account = await userModel.findActiveByUsername(username);
        const passwordMatches = account && await userModel.verifyAndUpgradePassword(account, password);
        if (!passwordMatches) {
            return res.status(401).json({ message: 'Tên đăng nhập hoặc mật khẩu không đúng.' });
        }

        const token = crypto.randomBytes(32).toString('hex');
        const expiresAt = new Date(Date.now() + SESSION_DURATION_MS);
        await userModel.createSession(token, account.id, expiresAt);

        setSessionCookie(res, token, SESSION_DURATION_MS / 1000);
        res.json({
            user: {
                id: account.id,
                username: account.username,
                fullName: account.full_name,
                role: account.role
            }
        });
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Không thể đăng nhập lúc này. Hãy kiểm tra kết nối cơ sở dữ liệu.' });
    }
}

function me(req, res) {
    if (!req.authUser) return res.status(401).json({ message: 'Phiên đăng nhập đã hết hạn.' });

    res.json({
        user: {
            id: req.authUser.id,
            username: req.authUser.username,
            fullName: req.authUser.full_name,
            role: req.authUser.role
        }
    });
}

async function logout(req, res) {
    try {
        const token = getSessionToken(req);
        if (token) await userModel.deleteSession(token);

        setSessionCookie(res, '', 0);
        res.json({ message: 'Đã đăng xuất.' });
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Không thể đăng xuất lúc này.' });
    }
}

module.exports = { getSessionToken, login, logout, me, setSessionCookie };