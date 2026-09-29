const apiBaseUrl = 'http://localhost:3001';

const roomListGrid = document.getElementById('roomListGrid');

const statusDetails = {
    AVAILABLE: {
        label: 'Phòng trống',
        className: 'available'
    },
    VACANT: {
        label: 'Phòng trống',
        className: 'available'
    },
    EMPTY: {
        label: 'Phòng trống',
        className: 'available'
    },
    RENTED: {
        label: 'Đang sử dụng',
        className: 'occupied'
    },
    OCCUPIED: {
        label: 'Đang sử dụng',
        className: 'occupied'
    },
    BOOKED: {
        label: 'Đã đặt',
        className: 'reserved'
    },
    RESERVED: {
        label: 'Đã đặt',
        className: 'reserved'
    },
    MAINTENANCE: {
        label: 'Bảo trì',
        className: 'maintenance'
    },
    UNDER_MAINTENANCE: {
        label: 'Bảo trì',
        className: 'maintenance'
    }
};

function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, (character) => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    })[character]);
}

function getStatus(status) {
    const normalizedStatus = String(status || '').trim().toUpperCase();

    return statusDetails[normalizedStatus] || {
        label: normalizedStatus || 'Chưa xác định',
        className: 'maintenance'
    };
}

async function loadRooms() {
    try {
        roomListGrid.innerHTML = '<p>Đang tải danh sách phòng...</p>';

        // Kiểm tra đăng nhập
        const authResponse = await fetch(
            `${apiBaseUrl}/api/auth/me`,
            {
                credentials: 'include'
            }
        );

        if (!authResponse.ok) {
            window.location.replace('login.html');
            return;
        }

        // Lấy danh sách phòng
        const response = await fetch(
            `${apiBaseUrl}/api/dashboard`,
            {
                credentials: 'include'
            }
        );

        if (!response.ok) {
            throw new Error('Không thể tải danh sách phòng.');
        }

        const dashboard = await response.json();
        const rooms = Array.isArray(dashboard.rooms)
            ? dashboard.rooms
            : [];

        renderRooms(rooms);

    } catch (error) {
        console.error('Lỗi tải danh sách phòng:', error);

        roomListGrid.innerHTML = `
            <p class="floor-empty floor-error">
                ${escapeHtml(error.message)}
            </p>
        `;
    }
}

function renderRooms(rooms) {
    if (rooms.length === 0) {
        roomListGrid.innerHTML = `
            <p class="floor-empty">
                Chưa có phòng nào trong hệ thống.
            </p>
        `;
        return;
    }

    roomListGrid.innerHTML = rooms.map((room) => {
        const status = getStatus(room.status);

        return `
            <article class="room-card ${status.className}">
                <div>
                    <h3 class="room-number">
                        Phòng ${escapeHtml(room.room_number)}
                    </h3>

                    <p>
                        ${escapeHtml(room.room_type || 'Chưa phân loại')}
                    </p>

                    <p>
                        Tầng:
                        ${room.floor === null
                            ? 'Chưa xếp tầng'
                            : escapeHtml(room.floor)}
                    </p>

                    <span class="room-status-label">
                        ${escapeHtml(status.label)}
                    </span>
                </div>

                <button
                    type="button"
                    class="delete-room-btn"
                    data-room-id="${escapeHtml(room.id)}"
                    data-room-number="${escapeHtml(room.room_number)}"
                >
                    Xóa phòng
                </button>
            </article>
        `;
    }).join('');

    document.querySelectorAll('.delete-room-btn').forEach((button) => {
        button.addEventListener('click', () => {
            const roomId = button.dataset.roomId;
            const roomNumber = button.dataset.roomNumber;

            deleteRoom(roomId, roomNumber);
        });
    });
}

async function deleteRoom(roomId, roomNumber) {
    const confirmed = confirm(
        `Bạn có chắc chắn muốn xóa phòng ${roomNumber}?`
    );

    if (!confirmed) {
        return;
    }

    try {
        const response = await fetch(
            `${apiBaseUrl}/api/rooms/${roomId}`,
            {
                method: 'DELETE',
                credentials: 'include'
            }
        );

        const result = await response.json();

        if (!response.ok || !result.success) {
            alert(result.message || 'Không thể xóa phòng.');
            return;
        }

        alert(result.message || 'Xóa phòng thành công.');

        // Tải lại danh sách phòng
        await loadRooms();

    } catch (error) {
        console.error('Lỗi xóa phòng:', error);

        alert('Không thể kết nối tới máy chủ.');
    }
}

loadRooms();