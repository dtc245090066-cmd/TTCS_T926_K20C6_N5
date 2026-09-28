const loginForm = document.getElementById('loginForm');
const loginMessage = document.getElementById('loginMessage');
const loginSubmit = document.getElementById('loginSubmit');
const apiBaseUrl = window.location.port === '3000' ? window.location.origin : 'http://localhost:3000';

async function readApiResponse(response) {
    const responseText = await response.text();
    try {
        return JSON.parse(responseText);
    } catch {
        throw new Error(`Backend trả phản hồi không hợp lệ (HTTP ${response.status}). Hãy mở ứng dụng qua localhost:3000.`);
    }
}

function showConnectionError() {
    loginMessage.textContent = `Không kết nối được backend tại ${apiBaseUrl}. Hãy chạy backend bằng npm start trong thư mục backend.`;
}

async function redirectIfAuthenticated() {
    try {
        const response = await fetch(`${apiBaseUrl}/api/auth/me`, { credentials: 'include' });
        if (response.ok) window.location.replace('/');
    } catch {
        showConnectionError();
    }
}

loginForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    loginMessage.textContent = '';
    loginSubmit.disabled = true;
    loginSubmit.querySelector('span').textContent = 'Đang xác thực...';

    const formData = new FormData(loginForm);

    try {
        const response = await fetch(`${apiBaseUrl}/api/auth/login`, {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: formData.get('username'),
                password: formData.get('password')
            })
        });
        const result = await readApiResponse(response);

        if (!response.ok) {
            loginMessage.textContent = result.message || 'Không thể đăng nhập.';
            return;
        }

        window.location.replace('/');
    } catch (error) {
        if (error instanceof TypeError) {
            showConnectionError();
        } else {
            loginMessage.textContent = error.message || 'Không thể đăng nhập lúc này.';
        }
    } finally {
        loginSubmit.disabled = false;
        loginSubmit.querySelector('span').textContent = 'Đăng nhập';
    }
});

redirectIfAuthenticated();
