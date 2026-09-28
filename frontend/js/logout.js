document.addEventListener("DOMContentLoaded", function () {
    const apiBaseUrl = window.location.port === "3000" ? window.location.origin : "http://localhost:3000";
    const logoutBtn = document.getElementById("logoutBtn");

    if (!logoutBtn) {
        return;
    }

    logoutBtn.addEventListener("click", function () {

        const confirmLogout = confirm(
            "Bạn có chắc chắn muốn đăng xuất khỏi hệ thống?"
        );

        if (!confirmLogout) {
            return;
        }

        fetch(`${apiBaseUrl}/api/auth/logout`, { method: "POST", credentials: "include" })
            .finally(function () {
                window.location.href = "/pages/login.html";
            });
    });
});