const apiBaseUrl = window.location.port === '3000' ? window.location.origin : 'http://localhost:3000';
const dashboardUrl = `${apiBaseUrl}/api/dashboard`;
const floorTabs = document.getElementById('floorTabs');
const floorMap = document.getElementById('floorMap');
const roomOverviewCount = document.getElementById('roomOverviewCount');

const statusDetails = {
	AVAILABLE: { label: 'Phòng trống', className: 'available' },
	VACANT: { label: 'Phòng trống', className: 'available' },
	EMPTY: { label: 'Phòng trống', className: 'available' },
	RENTED: { label: 'Đang sử dụng', className: 'occupied' },
	OCCUPIED: { label: 'Đang sử dụng', className: 'occupied' },
	BOOKED: { label: 'Đã đặt', className: 'reserved' },
	RESERVED: { label: 'Đã đặt', className: 'reserved' },
	MAINTENANCE: { label: 'Bảo trì', className: 'maintenance' },
	UNDER_MAINTENANCE: { label: 'Bảo trì', className: 'maintenance' }
};

let rooms = [];
let selectedFloorKey = null;

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

function getFloors() {
	const floors = new Map();

	rooms.forEach((room) => {
		const floorKey = room.floor === null ? 'unassigned' : String(room.floor);
		if (!floors.has(floorKey)) {
			floors.set(floorKey, {
				key: floorKey,
				label: room.floor === null ? 'Chưa xếp tầng' : `Tầng ${room.floor}`,
				floor: room.floor,
				rooms: []
			});
		}
		floors.get(floorKey).rooms.push(room);
	});

	return [...floors.values()].sort((first, second) => {
		if (first.floor === null) return 1;
		if (second.floor === null) return -1;
		return Number(first.floor) - Number(second.floor);
	});
}

function renderFloorMap() {
	const floors = getFloors();
	const totalFloors = floors.filter((floor) => floor.floor !== null).length;
	roomOverviewCount.textContent = `${rooms.length} phòng · ${totalFloors} tầng`;

	floorTabs.innerHTML = floors.map((floor) => `
		<button class="floor-tab" type="button" data-floor-key="${escapeHtml(floor.key)}"
			aria-pressed="${floor.key === selectedFloorKey}">
			${escapeHtml(floor.label)} <span>${floor.rooms.length}</span>
		</button>
	`).join('');

	const selectedFloor = floors.find((floor) => floor.key === selectedFloorKey);
	if (!selectedFloor) {
		floorMap.innerHTML = '<p class="floor-empty">Chưa có phòng nào trong hệ thống.</p>';
		return;
	}

	floorMap.innerHTML = `
		<div class="floor-map-heading">
			<h3>${escapeHtml(selectedFloor.label)}</h3>
			<span>${selectedFloor.rooms.length} phòng</span>
		</div>
		<div class="room-grid">
			${selectedFloor.rooms.map((room) => {
				const status = getStatus(room.status);
				return `
					<article class="room-card ${status.className}">
						<h4 class="room-number">${escapeHtml(room.room_number)}</h4>
						<p>${escapeHtml(room.room_type || 'Chưa phân loại')}</p>
						<span class="room-status-label">${escapeHtml(status.label)}</span>
					</article>
				`;
			}).join('')}
		</div>
	`;
}

floorTabs.addEventListener('click', (event) => {
	const selectedTab = event.target.closest('[data-floor-key]');
	if (!selectedTab) return;

	selectedFloorKey = selectedTab.dataset.floorKey;
	renderFloorMap();
});

async function loadDashboard() {
	try {
		const authResponse = await fetch(`${apiBaseUrl}/api/auth/me`, { credentials: 'include' });
		if (!authResponse.ok) {
			window.location.replace('/pages/login.html');
			return;
		}
		const { user } = await authResponse.json();
		document.getElementById('welcomeName').textContent = user.fullName || user.username;

		const response = await fetch(dashboardUrl, { credentials: 'include' });
		if (!response.ok) throw new Error('Máy chủ không thể tải dữ liệu phòng.');

		const dashboard = await response.json();
		rooms = Array.isArray(dashboard.rooms) ? dashboard.rooms : [];
		selectedFloorKey = getFloors()[0]?.key ?? null;

		document.getElementById('totalRooms').textContent = rooms.length;
		document.getElementById('availableRooms').textContent = rooms.filter((room) =>
			getStatus(room.status).className === 'available'
		).length;
		document.getElementById('occupiedRooms').textContent = rooms.filter((room) =>
			getStatus(room.status).className === 'occupied'
		).length;
		document.getElementById('totalRoomTypes').textContent = dashboard.totalRoomTypes ?? 0;

		renderFloorMap();
	} catch (error) {
		roomOverviewCount.textContent = 'Không tải được dữ liệu';
		floorMap.innerHTML = `<p class="floor-empty floor-error">${escapeHtml(error.message)} Hãy kiểm tra backend tại localhost:3000.</p>`;
	}
}

loadDashboard();
