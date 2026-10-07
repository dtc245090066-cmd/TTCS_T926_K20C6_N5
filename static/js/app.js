const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

const authView = $("#authView");
const dashboardView = $("#dashboardView");
const loginPanel = $("#loginPanel");
const registerPanel = $("#registerPanel");

let rooms = [];
let roomTypes = [];
let bookings = [];
let currentFilter = "all";
let roomListFilter = "all";
let checkoutFilter = "all";
let returnToRoomListAfterBooking = false;
let lockedBookingRoomId = null;
let activeConfirmation = null;
let chart;
let selectedAvatarFile = null;
let selectedRoomImageFile = null;

const statusMap = {
  available: "Trống",
  occupied: "Đang ở",
  cleaning: "Đang dọn",
  maintenance: "Bảo trì",
};

const statusClass = {
  available: "success",
  occupied: "success",
  cleaning: "processing",
  maintenance: "delivered",
};

function money(value) {
  return new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND",
    maximumFractionDigits: 0,
  }).format(Number(value || 0));
}

function padTime(value) {
  return String(value).padStart(2, "0");
}

function setBookingDefaultTimes() {
  const checkInDate = new Date();
  const checkOutDate = new Date(checkInDate.getTime() + 3 * 60 * 60 * 1000);

  $("#bookingCheckIn").value = localDateString(checkInDate);
  $("#bookingCheckOut").value = localDateString(checkOutDate);
  $("#bookingCheckInTime").value = `${padTime(checkInDate.getHours())}:${padTime(checkInDate.getMinutes())}`;
  $("#bookingCheckOutTime").value = `${padTime(checkOutDate.getHours())}:${padTime(checkOutDate.getMinutes())}`;
}

function toast(message) {
  const el = $("#toast");
  el.textContent = "✓ " + message;
  el.classList.add("toast-centered");
  el.classList.add("show");
  clearTimeout(window.__toastTimer);
  window.__toastTimer = setTimeout(() => el.classList.remove("show"), 2000);
}

function message(el, text, success = false) {
  el.textContent = text || "";
  el.classList.toggle("success", success);
}

async function api(url, options = {}) {
  const headers = options.body instanceof FormData
    ? { ...(options.headers || {}) }
    : { "Content-Type": "application/json", ...(options.headers || {}) };
  const response = await fetch(url, {
    headers,
    ...options,
  });
  const data = await response.json().catch(() => ({}));

  const isAuthEndpoint = ["/api/login", "/api/register"].includes(url);
  if (response.status === 401 && !isAuthEndpoint) {
    showLogin("Phiên đăng nhập đã hết. Vui lòng đăng nhập lại.");
    throw new Error(data.message || "Unauthorized");
  }

  return { response, data };
}

function showLogin(error = "") {
  dashboardView.classList.add("hidden");
  authView.classList.remove("hidden");
  message($("#loginMessage"), error);
}

function setUserDisplay(user) {
  if (!user) return;
  const fullName = user.full_name || "Admin";
  $("#userName").textContent = fullName;
  $("#userRole").textContent = user.role === "manager" ? "Quản lý" : "Nhân viên";

  const initials = fullName
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map(part => part[0])
    .join("")
    .toUpperCase() || "LH";

  $("#profileAvatarBadge").textContent = initials;
  $("#topUserInitials").textContent = initials;
}

function showDashboard(user) {
  authView.classList.add("hidden");
  dashboardView.classList.remove("hidden");
  setUserDisplay(user);
  loadProfile();
  loadAll();
}

async function loadProfile() {
  try {
    const { response, data } = await api("/api/profile");
    if (!response.ok) return;

    const user = data.user || {};
    setUserDisplay(user);
    $("#profileFullName").value = user.full_name || "";
    $("#profileBirthDate").value = user.birth_date || "";
    $("#profileEmail").value = user.email || "";
    $("#profilePhone").value = user.phone || "";
    $("#profileAvatar").value = user.avatar_url || "";
    selectedAvatarFile = null;
    $("#profileAvatarFile").value = "";
    $("#profileAvatarFileName").textContent = "Chưa chọn ảnh";
    $("#profileAvatarPreview").src = user.avatar_url || "";
    $("#profileAvatarPreview").style.display = user.avatar_url ? "block" : "none";
  } catch (error) {
    console.error(error);
  }
}

async function checkSession() {
  try {
    const { data } = await api("/api/session");
    if (data.user) {
      showDashboard(data.user);
      return;
    }
    showLogin();
  } catch {
    showLogin();
  }
}

$("#loginForm").addEventListener("submit", async (event) => {
  event.preventDefault();

  const email = $("#loginEmail").value.trim();
  const password = $("#loginPassword").value;

  if (!email || !password) {
    message($("#loginMessage"), "Vui lòng nhập email và mật khẩu.");
    return;
  }

  const { response, data } = await api("/api/login", {
    method: "POST",
    body: JSON.stringify({
      email,
      password,
    }),
  });

  if (!response.ok) {
    message($("#loginMessage"), data.message || "Đăng nhập thất bại.");
    return;
  }

  message($("#loginMessage"), "");
  showDashboard(data.user);
});

$("#registerForm").addEventListener("submit", async (event) => {
  event.preventDefault();

  const { response, data } = await api("/api/register", {
    method: "POST",
    body: JSON.stringify({
      full_name: $("#registerName").value,
      email: $("#registerEmail").value,
      password: $("#registerPassword").value,
    }),
  });

  message($("#registerMessage"), data.message || "", response.ok);

  if (response.ok) {
    setTimeout(() => {
      registerPanel.classList.add("hidden");
      loginPanel.classList.remove("hidden");
      $("#loginEmail").value = $("#registerEmail").value;
    }, 700);
  }
});

$("#showRegister").addEventListener("click", () => {
  loginPanel.classList.add("hidden");
  registerPanel.classList.remove("hidden");
});

$("#showLogin").addEventListener("click", () => {
  registerPanel.classList.add("hidden");
  loginPanel.classList.remove("hidden");
});

$("#profileBtn").addEventListener("click", async () => {
  await loadProfile();
  openModal("profileModal");
});

$("#topProfileBtn").addEventListener("click", async () => {
  await loadProfile();
  openModal("profileModal");
});

function preparePasswordModal() {
  $("#passwordForm").reset();
  $("#passwordMessage").textContent = "";
  const loggedIn = !!document.getElementById("dashboardView") && !document.getElementById("dashboardView").classList.contains("hidden");
  const emailRow = document.getElementById("passwordEmailRow");
  const emailInput = document.getElementById("passwordEmail");

  if (loggedIn) {
    emailRow.style.display = "none";
    emailInput.value = "";
  } else {
    emailRow.style.display = "block";
    const loginEmail = $("#loginEmail").value.trim();
    emailInput.value = loginEmail;
  }

  $("#verificationCode").value = "";
}

async function sendPasswordVerificationCode() {
  const loggedIn = !!document.getElementById("dashboardView") && !document.getElementById("dashboardView").classList.contains("hidden");
  const email = loggedIn ? $("#profileEmail").value.trim() || $("#loginEmail").value.trim() : $("#passwordEmail").value.trim();

  if (!email) {
    message($("#passwordMessage"), "Vui lòng nhập email để nhận mã xác minh.");
    return;
  }

  const { response, data } = await api("/api/profile/password/request-code", {
    method: "POST",
    body: JSON.stringify({ email }),
  });

  message($("#passwordMessage"), data.message || "", response.ok);

  if (data.debug_code) {
    $("#verificationCode").value = data.debug_code;
    $("#verificationCode").focus();
  }
}

$("#changePasswordBtn").addEventListener("click", () => {
  preparePasswordModal();
  openModal("passwordModal");
});

$("#openPasswordModalBtn").addEventListener("click", () => {
  preparePasswordModal();
  closeModal("profileModal");
  openModal("passwordModal");
});

$("#openPasswordModalFromLogin").addEventListener("click", () => {
  preparePasswordModal();
  openModal("passwordModal");
});

$("#sendVerificationCodeBtn").addEventListener("click", sendPasswordVerificationCode);

$("#logoutBtn").addEventListener("click", async () => {
  await api("/api/logout", { method: "POST" });
  showLogin();
  toast("Đã đăng xuất");
});

$("#profileAvatarFile").addEventListener("change", () => {
  selectedAvatarFile = $("#profileAvatarFile").files[0] || null;
  $("#profileAvatarFileName").textContent = selectedAvatarFile?.name || "Chưa chọn ảnh";
  const url = selectedAvatarFile ? URL.createObjectURL(selectedAvatarFile) : $("#profileAvatar").value.trim();
  const preview = $("#profileAvatarPreview");
  preview.src = url;
  preview.style.display = url ? "block" : "none";
});

$("#profileForm").addEventListener("submit", async (event) => {
  event.preventDefault();

  if (selectedAvatarFile) {
    const formData = new FormData();
    formData.append("avatar", selectedAvatarFile);
    const upload = await api("/api/profile/avatar", { method: "POST", body: formData });
    if (!upload.response.ok) {
      message($("#profileMessage"), upload.data.message || "Không thể tải ảnh lên.");
      return;
    }
    $("#profileAvatar").value = upload.data.avatar_url;
  }

  const payload = {
    full_name: $("#profileFullName").value,
    birth_date: $("#profileBirthDate").value,
    phone: $("#profilePhone").value,
    avatar_url: $("#profileAvatar").value,
  };

  const { response, data } = await api("/api/profile", {
    method: "PUT",
    body: JSON.stringify(payload),
  });

  message($("#profileMessage"), data.message || "", response.ok);

  if (response.ok) {
    selectedAvatarFile = null;
    $("#profileAvatarFile").value = "";
    $("#profileAvatarFileName").textContent = "Chưa chọn ảnh";
    const user = data.user || {};
    setUserDisplay(user);
    $("#userName").textContent = user.full_name || $("#profileFullName").value;
    $("#profileAvatarBadge").textContent = (user.full_name || $("#profileFullName").value)
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map(part => part[0])
      .join("")
      .toUpperCase() || "LH";

    closeModal("profileModal");
    toast(data.message || "Cập nhật thành công");
    await loadAll();
  }
});

$("#passwordForm").addEventListener("submit", async (event) => {
  event.preventDefault();

  const currentPassword = $("#currentPassword").value;
  const newPassword = $("#newPassword").value;
  const confirmPassword = $("#confirmPassword").value;
  const verificationCode = $("#verificationCode").value.trim();
  const loggedIn = !!document.getElementById("dashboardView") && !document.getElementById("dashboardView").classList.contains("hidden");
  const email = $("#passwordEmail").value.trim() || ($("#profileEmail") ? $("#profileEmail").value.trim() : "");

  if (!currentPassword || !newPassword || !confirmPassword) {
    message($("#passwordMessage"), "Vui lòng nhập đầy đủ các trường bắt buộc.");
    return;
  }

  if (!loggedIn && !email) {
    message($("#passwordMessage"), "Vui lòng nhập email để xác thực tài khoản.");
    return;
  }

  if (!verificationCode || verificationCode.length !== 6) {
    message($("#passwordMessage"), "Vui lòng nhập mã xác minh 6 chữ số đã gửi qua email.");
    return;
  }

  if (newPassword.length < 8 || newPassword.length > 128) {
    message($("#passwordMessage"), "Mật khẩu mới phải có từ 8 đến 128 ký tự.");
    return;
  }

  if (newPassword !== confirmPassword) {
    message($("#passwordMessage"), "Mật khẩu xác nhận không khớp.");
    return;
  }

  const payload = {
    current_password: currentPassword,
    new_password: newPassword,
    confirm_password: confirmPassword,
    verification_code: verificationCode,
  };

  if (!loggedIn) {
    payload.email = email;
  } else {
    payload.email = $("#profileEmail").value.trim();
  }

  const { response, data } = await api("/api/profile/password", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  message($("#passwordMessage"), data.message || "", response.ok);

  if (response.ok) {
    $("#passwordForm").reset();
    closeModal("passwordModal");
    toast(data.message || "Cập nhật mật khẩu thành công");
  }
});

function setView(view) {
  $$(".nav-item").forEach((item) => item.classList.toggle("active", item.dataset.view === view || (item.dataset.view === "rooms" && ["room-list", "room-types"].includes(view))));
  $$("[data-view-panel]").forEach((panel) => panel.classList.toggle("active", panel.dataset.viewPanel === view));
  const roomMenu = $(".nav-room-group");
  const roomMenuToggle = roomMenu.querySelector('[data-view="rooms"]');
  if (view !== "rooms") roomMenu.classList.remove("expanded");
  roomMenuToggle.setAttribute("aria-expanded", String(roomMenu.classList.contains("expanded")));
  if (view === "rooms") renderRooms();
  if (view === "room-list") renderRoomList();
  if (view === "room-types") renderRoomTypes();
  if (view === "checkout") renderCheckoutList();
}

$$(".nav-item[data-view]").forEach((item) => {
  item.addEventListener("click", () => {
    if (item.dataset.view === "rooms") {
      const roomMenu = item.closest(".nav-room-group");
      const expanded = roomMenu.classList.toggle("expanded");
      item.setAttribute("aria-expanded", String(expanded));
      setView("rooms");
      return;
    }
    setView(item.dataset.view);
  });
});

$$('[data-room-subview]').forEach(button => {
  button.addEventListener("click", () => setView(button.dataset.roomSubview));
});

$$("[data-go]").forEach((button) => {
  button.addEventListener("click", () => setView(button.dataset.go));
});

async function loadAll() {
  try {
    const [roomsResult, roomTypesResult, bookingsResult, dashboardResult] = await Promise.all([
      api("/api/rooms"),
      api("/api/room-types"),
      api("/api/bookings"),
      api("/api/dashboard"),
    ]);

    rooms = roomsResult.data.rooms || [];
    roomTypes = roomTypesResult.data.room_types || [];
    bookings = bookingsResult.data.bookings || [];

    fillRoomTypeOptions();
    renderRooms();
    renderRoomList();
    renderRoomTypes();
    renderCheckoutList();
    renderDashboard(dashboardResult.data);
    fillBookingRooms();
  } catch (error) {
    console.error(error);
  }
}

function renderDashboard(summary) {
  $("#statRevenue").textContent = money(summary.revenue);
  $("#chartTotal").textContent = money(summary.revenue);
  $("#statAvailable").textContent = summary.available_rooms;
  $("#statOccupancy").textContent = `${summary.occupancy}%`;
  $("#statOccupied").textContent = summary.occupied_rooms;
  renderFrontDeskSummary();

  const total = Math.max(Number(summary.revenue || 0), 1);
  const values = [0.14, 0.21, 0.12, 0.18, 0.10, 0.16, 0.09].map(x => Math.round(total * x));

  if (chart) chart.destroy();

  const ctx = $("#salesChart");
  chart = new Chart(ctx, {
    type: "line",
    data: {
      labels: ["T2", "T3", "T4", "T5", "T6", "T7", "CN"],
      datasets: [{
        data: values,
        borderWidth: 2.5,
        borderColor: "#9d7447",
        backgroundColor: "rgba(191,151,95,.11)",
        fill: true,
        tension: .42,
        pointRadius: 3,
        pointBackgroundColor: "#fffdf9",
        pointBorderColor: "#9d7447",
        pointBorderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, grid: { color: "#eee8e0" }, border: { display: false }, ticks: { callback: v => `${Math.round(v / 1000000)}tr` } },
        x: { grid: { display: false }, border: { display: false } }
      }
    }
  });

  const featured = rooms[0];
  if (featured) {
    $("#featuredRoom").innerHTML = `
      <div class="room-feature">
        <img src="${featured.image_url || ""}" alt="${featured.name}">
        <div class="room-feature-info">
          <span class="room-status ${statusClass[featured.status] || ""}">${statusMap[featured.status]}</span>
          <h4>${featured.name}</h4>
          <p>Phòng ${featured.code} · Tầng ${featured.floor}</p>
          <strong>${money(featured.price)} <small>/ đêm</small></strong>
        </div>
      </div>`;
  }

  $("#miniRooms").innerHTML = rooms.slice(1, 4).map(room => `
    <div class="room-mini">
      <img src="${room.image_url || ""}" alt="">
      <div><b>${room.code}</b><small>${statusMap[room.status]}</small></div>
    </div>
  `).join("");

}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, character => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[character]);
}

function localDateString(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function parseLocalDate(value) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value || "")) return null;
  const [year, month, day] = value.split("-").map(Number);
  const parsed = new Date(year, month - 1, day);
  return parsed.getFullYear() === year && parsed.getMonth() === month - 1 && parsed.getDate() === day
    ? parsed
    : null;
}

function dateOffset(date, start) {
  const toUtcDay = value => Date.UTC(value.getFullYear(), value.getMonth(), value.getDate());
  return Math.round((toUtcDay(date) - toUtcDay(start)) / 86400000);
}

function renderFrontDeskSummary() {
  const roomStatuses = [
    ["available", "Phòng trống", "available"],
    ["occupied", "Đang ở", "occupied"],
    ["cleaning", "Đang dọn", "cleaning"],
    ["maintenance", "Bảo trì", "maintenance"],
  ];
  $("#roomStatusSummary").innerHTML = roomStatuses.map(([status, label, className]) => `
    <div class="room-status-count ${className}">
      <span class="room-status-indicator" aria-hidden="true"></span>
      <span>${label}</span>
      <strong>${rooms.filter(room => room.status === status).length}</strong>
    </div>
  `).join("");
}

function renderRoomList() {
  const roomCounts = {
    available: 0,
    occupied: 0,
    cleaning: 0,
    maintenance: 0,
  };
  rooms.forEach(room => {
    if (Object.prototype.hasOwnProperty.call(roomCounts, room.status)) roomCounts[room.status] += 1;
  });
  $("#roomListAvailableCount").textContent = roomCounts.available;
  $("#roomListOccupiedCount").textContent = roomCounts.occupied;
  $("#roomListCleaningCount").textContent = roomCounts.cleaning;
  $("#roomListMaintenanceCount").textContent = roomCounts.maintenance;

  const query = $("#roomListSearch").value.trim().toLowerCase();
  const filtered = rooms.filter(room => {
    const matchesStatus = roomListFilter === "all" || room.status === roomListFilter;
  const searchable = `${room.code} ${room.name} ${room.room_type_name || ""} ${room.room_type}`.toLowerCase();
    return matchesStatus && searchable.includes(query);
  });
  $("#roomListBody").innerHTML = filtered.length ? filtered.map(room => {
    const stay = getRoomStay(room);
    const statusLabel = statusMap[room.status] || "Không rõ";
    const canRent = room.status === "available";
    return `
      <tr>
        <td><strong>${escapeHtml(room.code)}</strong></td>
        <td>${escapeHtml(room.name)}</td>
        <td>${escapeHtml(room.room_type_name || (room.room_type || "").toUpperCase())} · Tầng ${escapeHtml(room.floor)}</td>
        <td><strong>${money(room.price)}</strong></td>
        <td>${escapeHtml(stay?.check_in_time || "--")}</td>
        <td>${escapeHtml(stay?.check_out_time || "--")}</td>
        <td><span class="room-list-status ${escapeHtml(room.status)}">${escapeHtml(statusLabel)}</span></td>
        <td><div class="room-list-actions">
          <button class="mini-button" data-room-view="${room.id}">Xem</button>
          ${room.status === "occupied"
    ? `<button class="mini-button" data-checkout="${room.id}">Trả phòng</button>`
    : `<button class="mini-button" data-rent="${room.id}" ${canRent ? "" : "disabled"} title="${canRent ? "Cho thuê phòng" : "Phòng không khả dụng để cho thuê"}">Cho thuê</button>`}
          <button class="mini-button" data-edit="${room.id}">Sửa</button>
          <button class="mini-button danger" data-delete="${room.id}" ${room.status !== "available" ? "disabled" : ""}>Xóa</button>
        </div></td>
      </tr>`;
  }).join("") : `<tr><td class="room-list-empty" colspan="8">Không tìm thấy phòng phù hợp.</td></tr>`;
}

function openRoomDetails(room) {
  $("#roomDetailsName").textContent = room.name || "Chi tiết phòng";
  $("#roomDetailsCode").textContent = room.code || "-";
  $("#roomDetailsType").textContent = room.room_type_name || (room.room_type || "-").toUpperCase();
  $("#roomDetailsFloor").textContent = `Tầng ${room.floor}`;
  $("#roomDetailsPrice").textContent = money(room.price);
  const roomStatus = $("#roomDetailsStatus");
  roomStatus.className = `room-status ${statusClass[room.status] || ""}`;
  roomStatus.textContent = statusMap[room.status] || "Không rõ";
  $("#roomDetailsDescription").textContent = room.description || "Chưa có mô tả phòng.";
  const image = $("#roomDetailsImage");
  image.src = room.image_url || "";
  image.alt = room.name || "Ảnh phòng";
  image.hidden = !room.image_url;
  openModal("roomDetailsModal");
}

async function deleteRoom(roomId) {
  const room = rooms.find(item => item.id === roomId);
  if (!room || !await requestConfirmation({
    modalId: "roomDeleteConfirmModal",
    roomCodeId: "roomDeleteConfirmRoomCode",
    submitId: "roomDeleteConfirmSubmit",
    roomCode: room.code,
  })) return;

  const { response, data } = await api(`/api/rooms/${roomId}`, { method: "DELETE" });
  if (response.ok) {
    toast(data.message || "Xóa phòng thành công.");
    await loadAll();
  } else {
    toast(data.message || "Không thể xóa phòng.");
  }
}

$("#roomListSearch").addEventListener("input", renderRoomList);

$$('[data-room-list-filter]').forEach(button => {
  button.addEventListener("click", () => {
    roomListFilter = button.dataset.roomListFilter;
    $$('[data-room-list-filter]').forEach(filter => filter.classList.toggle("active", filter === button));
    renderRoomList();
  });
});

$("#roomsGrid").addEventListener("click", handleRoomCardAction);
$("#roomListBody").addEventListener("click", handleRoomCardAction);
$("#checkoutRoomsGrid").addEventListener("click", handleRoomCardAction);

function getRoomStay(room) {
  return bookings.find(booking =>
    booking.room_code === room.code && ["booked", "checked_in"].includes(booking.status)
  );
}

function roomCardMarkup(room, showDetails = false) {
  const stay = getRoomStay(room);
  const statusLabel = showDetails && room.status === "occupied"
    ? "Đã có người thuê"
    : statusMap[room.status] || "Không rõ";
  const canRent = room.status === "available";
  return `
    <article class="room-card room-card-${escapeHtml(room.status || "unknown")}">
      <div class="room-card-top">
        <span class="room-code">${escapeHtml(room.code)}</span>
        <span class="room-status ${statusClass[room.status] || ""}">${escapeHtml(statusLabel)}</span>
      </div>
      <img src="${escapeHtml(room.image_url || "")}" alt="${escapeHtml(room.name)}">
      <div class="room-meta">
        <h4>${escapeHtml(room.name)}</h4>
        <p>${escapeHtml(room.description || "")}</p>
      </div>
      <div class="room-stay-times" aria-label="Thời gian lưu trú">
        <div><span>◷ Giờ vào</span><strong>${escapeHtml(stay?.check_in_time || "--")}</strong></div>
        <div><span>◷ Giờ ra</span><strong>${escapeHtml(stay?.check_out_time || "--")}</strong></div>
      </div>
      <div class="room-cost"><strong>${money(room.price)}</strong></div>
  <div class="room-footer"><span class="room-type">${escapeHtml(room.room_type_name || (room.room_type || "").toUpperCase())} · Tầng ${escapeHtml(room.floor)}</span></div>
      <div class="room-actions">
        ${showDetails ? `<button class="mini-button" data-room-view="${room.id}">Xem</button>` : ""}
    ${room.status === "occupied"
    ? `<button class="mini-button" data-checkout="${room.id}">Trả phòng</button>`
    : `<button class="mini-button" data-rent="${room.id}" ${canRent ? "" : "disabled"} title="${canRent ? "Cho thuê phòng" : "Phòng không khả dụng để cho thuê"}">Cho thuê</button>`}
    <button class="mini-button" data-edit="${room.id}">Cập nhật</button>
    <button class="mini-button danger" data-delete="${room.id}" ${room.status !== "available" ? "disabled" : ""}>Xóa</button>
  </div>
    </article>`;
}
function renderRoomCards(container, roomItems, showDetails = false) {
  container.innerHTML = roomItems.length
    ? roomItems.map(room => roomCardMarkup(room, showDetails)).join("")
    : `<div class="empty-feature rooms-empty"><h3>Không tìm thấy phòng</h3><p>Thử đổi từ khóa hoặc bộ lọc.</p></div>`;
}
function handleRoomCardAction(event) {
  const viewButton = event.target.closest("[data-room-view]");
  const rentButton = event.target.closest("[data-rent]");
  const checkoutButton = event.target.closest("[data-checkout]");
  const editButton = event.target.closest("[data-edit]");
  const deleteButton = event.target.closest("[data-delete]");
  const roomId = Number(viewButton?.dataset.roomView || rentButton?.dataset.rent || checkoutButton?.dataset.checkout || editButton?.dataset.edit || deleteButton?.dataset.delete);
  if (!roomId) return;
  const room = rooms.find(item => item.id === roomId);
  if (!room) return;
  if (viewButton) openRoomDetails(room);
  if (checkoutButton) {
    checkoutRoom(room);
    return;
  }
  if (rentButton && !rentButton.disabled) {
    $("#bookingForm").reset();
    $("#bookingMessage").textContent = "";
    $("#bookingCheckOutError").textContent = "";
    returnToRoomListAfterBooking = true;
    lockedBookingRoomId = roomId;
    setBookingDefaultTimes();
    fillBookingRooms(roomId);
    $("#bookingRoom").disabled = true;
    $("#bookingCheckIn").disabled = true;
    $("#bookingCheckInTime").disabled = true;
    openModal("bookingModal");
    return;
  }
  if (editButton) openRoomModal(room);
  if (deleteButton && !deleteButton.disabled) deleteRoom(roomId);
}

function closeConfirmation(confirmed) {
  if (!activeConfirmation) return;

  const { resolve, trigger, modal } = activeConfirmation;
  activeConfirmation = null;
  modal.hidden = true;
  if (trigger?.isConnected) trigger.focus();
  resolve(confirmed);
}

function requestConfirmation({ modalId, roomCodeId, submitId, roomCode }) {
  if (activeConfirmation) return Promise.resolve(false);

  const modal = $(`#${modalId}`);
  $(`#${roomCodeId}`).textContent = roomCode;

  return new Promise(resolve => {
    activeConfirmation = { resolve, trigger: document.activeElement, modal };
    modal.hidden = false;
    requestAnimationFrame(() => {
      if (!modal.hidden) $(`#${submitId}`).focus();
    });
  });
}

[
  ["checkoutConfirmModal", "checkoutConfirmCancel", "checkoutConfirmClose", "checkoutConfirmSubmit"],
  ["roomDeleteConfirmModal", "roomDeleteConfirmCancel", "roomDeleteConfirmClose", "roomDeleteConfirmSubmit"],
].forEach(([modalId, cancelId, closeId, submitId]) => {
  $(`#${cancelId}`).addEventListener("click", () => closeConfirmation(false));
  $(`#${closeId}`).addEventListener("click", () => closeConfirmation(false));
  $(`#${submitId}`).addEventListener("click", () => closeConfirmation(true));
  $(`#${modalId}`).addEventListener("click", event => {
    if (event.target === event.currentTarget) closeConfirmation(false);
  });
});

document.addEventListener("keydown", event => {
  if (!activeConfirmation) return;
  if (event.key === "Escape") {
    event.preventDefault();
    closeConfirmation(false);
    return;
  }
  if (event.key !== "Tab") return;

  const focusable = [...activeConfirmation.modal.querySelectorAll("button:not(:disabled)")];
  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
});

async function checkoutRoom(room) {
  if (!await requestConfirmation({
    modalId: "checkoutConfirmModal",
    roomCodeId: "checkoutConfirmRoomCode",
    submitId: "checkoutConfirmSubmit",
    roomCode: room.code,
  })) return;

  try {
    const { response, data } = await api(`/api/rooms/${room.id}/checkout`, {
      method: "POST",
    });
    if (!response.ok) {
      toast(data.message || "Không thể trả phòng. Vui lòng thử lại.");
      return;
    }

    await loadAll();
    toast(data.message || "Trả phòng thành công!");
  } catch (error) {
    if (error.message === "Unauthorized") return;
    console.error("Không thể trả phòng:", error);
    toast("Không thể trả phòng. Vui lòng thử lại.");
  }
}

function renderRooms() {
  const filtered = currentFilter === "all"
    ? rooms
    : rooms.filter(room => room.status === currentFilter);
  renderRoomCards($("#roomsGrid"), filtered);
}

function getCheckoutBooking(room) {
  return bookings.find(booking => booking.room_code === room.code && booking.status === "checked_in")
    || getRoomStay(room);
}

function bookingCheckoutTime(booking) {
  if (!booking?.check_out) return null;
  const date = parseLocalDate(booking.check_out);
  if (!date) return null;
  const time = /^([01]\d|2[0-3]):[0-5]\d$/.test(booking.check_out_time || "")
    ? booking.check_out_time
    : "23:59";
  const [hours, minutes] = time.split(":").map(Number);
  date.setHours(hours, minutes, 0, 0);
  return date;
}

function formatBookingDateTime(date, time) {
  if (!date) return "--";
  return `${date}${time ? ` · ${time}` : ""}`;
}

function checkoutRoomCardMarkup(room) {
  const booking = getCheckoutBooking(room);
  const checkInDate = parseLocalDate(booking?.check_in);
  const stayDays = checkInDate
    ? Math.max(1, dateOffset(new Date(), checkInDate))
    : null;
  const image = room.image_url
    ? `<img src="${escapeHtml(room.image_url)}" alt="${escapeHtml(room.name || `Phòng ${room.code}`)}">`
    : "";

  return `
    <article class="checkout-card">
      <div class="checkout-card-header">
        <div><span class="section-label">PHÒNG</span><strong>${escapeHtml(room.code)}</strong></div>
        <span class="checkout-status"><i aria-hidden="true"></i>Đang ở</span>
      </div>
      ${image}
      <div class="checkout-card-body">
        <h3>${escapeHtml(room.name || `Phòng ${room.code}`)}</h3>
        <p class="checkout-room-type">${escapeHtml(room.room_type_name || room.room_type || "Phòng")} · Tầng ${escapeHtml(room.floor)}</p>
        <dl class="checkout-details">
          <div><dt>Khách đang ở</dt><dd>${escapeHtml(booking?.customer_name || "--")}</dd></div>
          <div><dt>Giờ vào</dt><dd>${escapeHtml(formatBookingDateTime(booking?.check_in, booking?.check_in_time))}</dd></div>
          <div><dt>Giờ trả dự kiến</dt><dd>${escapeHtml(formatBookingDateTime(booking?.check_out, booking?.check_out_time))}</dd></div>
          <div><dt>Thời gian ở</dt><dd>${stayDays === null ? "--" : `${stayDays} ngày`}</dd></div>
        </dl>
        <div class="checkout-prices">
          <div><span>Giá phòng</span><strong>${money(room.price)} / đêm</strong></div>
          ${booking?.total != null ? `<div><span>Tổng tiền</span><strong>${money(booking.total)}</strong></div>` : ""}
        </div>
        <button class="mini-button" data-checkout="${room.id}">Trả phòng</button>
      </div>
    </article>`;
}

function renderCheckoutList() {
  const today = localDateString(new Date());
  const occupiedRooms = rooms.filter(room => room.status === "occupied");
  const query = $("#checkoutSearch").value.trim().toLocaleLowerCase("vi");
  $("#checkoutSearchClear").hidden = !query;
  $("#checkoutBadge").textContent = occupiedRooms.length;
  const filteredRooms = occupiedRooms.filter(room => {
    if (checkoutFilter === "all") return true;
    const booking = getCheckoutBooking(room);
    if (checkoutFilter === "today") return booking?.check_out === today;
    if (checkoutFilter === "overdue") {
      const dueAt = bookingCheckoutTime(booking);
      return Boolean(dueAt && dueAt < new Date());
    }
    return true;
  }).filter(room => {
    if (!query) return true;
    const searchable = [
      room.code,
      room.name,
      room.room_type_name,
      room.room_type,
    ].filter(Boolean).join(" ").toLocaleLowerCase("vi");
    return searchable.includes(query);
  });

  $("#checkoutRoomsGrid").innerHTML = filteredRooms.length
    ? filteredRooms.map(checkoutRoomCardMarkup).join("")
    : `<div class="empty-feature rooms-empty"><h3>${occupiedRooms.length ? "Không tìm thấy phòng phù hợp" : "Hiện không có phòng cần trả"}</h3><p>${occupiedRooms.length ? "Thử từ khóa hoặc bộ lọc khác." : "Các phòng đang ở sẽ tự động xuất hiện tại đây."}</p></div>`;
}

$("#checkoutSearch").addEventListener("input", renderCheckoutList);
$("#checkoutSearchClear").addEventListener("click", () => {
  $("#checkoutSearch").value = "";
  renderCheckoutList();
  $("#checkoutSearch").focus();
});

$$("[data-checkout-filter]").forEach(button => {
  button.addEventListener("click", () => {
    checkoutFilter = button.dataset.checkoutFilter;
    $$("[data-checkout-filter]").forEach(filter => filter.classList.toggle("active", filter === button));
    renderCheckoutList();
  });
});

function fillBookingRooms(selectedRoomId = null) {
  const roomSelect = $("#bookingRoom");
  if (!roomSelect) return;

  const availableRooms = rooms.filter(room => room.status === "available" || room.id === Number(selectedRoomId));
  roomSelect.innerHTML = availableRooms.map(room => `<option value="${room.id}">Phòng ${room.code} — ${room.name} — ${money(room.price)}/đêm</option>`).join("");

  if (selectedRoomId !== null && selectedRoomId !== undefined) {
    const chosen = availableRooms.some(room => room.id === Number(selectedRoomId));
    roomSelect.value = chosen ? String(selectedRoomId) : (availableRooms[0]?.id ?? "");
  } else {
    roomSelect.value = availableRooms[0]?.id ? String(availableRooms[0].id) : "";
  }

  updateBookingSummary();
}

function getBookingRoom() {
  const roomId = Number($("#bookingRoom").value || 0);
  return rooms.find(room => room.id === roomId) || null;
}

function updateBookingSummary() {
  const room = getBookingRoom();
  const bookingCheckIn = $("#bookingCheckIn");
  const bookingCheckOut = $("#bookingCheckOut");
  const bookingCheckInTime = $("#bookingCheckInTime");
  const bookingCheckOutTime = $("#bookingCheckOutTime");
  const durationEl = $("#bookingDurationText");
  const priceEl = $("#bookingPriceText");
  const totalEl = $("#bookingTotalText");
  const roomSummaryName = $("#bookingRoomSummaryName");
  const roomSummaryMeta = $("#bookingRoomSummaryMeta");
  const roomImage = $("#bookingRoomImage");
  const roomPlaceholder = $("#bookingRoomPlaceholder");

  if (!room) {
    durationEl.textContent = "0 giờ";
    priceEl.textContent = "0₫";
    totalEl.textContent = "0₫";
    roomSummaryName.textContent = "Chọn phòng";
    roomSummaryMeta.textContent = "-";
    $("#bookingRoomCode").textContent = "-";
    $("#bookingRoomType").textContent = "-";
    $("#bookingRoomFloor").textContent = "-";
    $("#bookingRoomPrice").textContent = "-";
    $("#bookingRoomStatus").textContent = "-";
    $("#bookingRoomDescription").textContent = "";
    roomImage.hidden = true;
    roomImage.removeAttribute("src");
    roomPlaceholder.hidden = false;
    return;
  }

  roomSummaryName.textContent = `${room.code} · ${room.name}`;
  roomSummaryMeta.textContent = `${room.room_type_name || room.room_type || "Phòng"} · ${money(room.price)}/đêm`;
  $("#bookingRoomCode").textContent = room.code;
  $("#bookingRoomType").textContent = room.room_type_name || room.room_type || "Phòng";
  $("#bookingRoomFloor").textContent = room.floor;
  $("#bookingRoomPrice").textContent = `${money(room.price)} / đêm`;
  $("#bookingRoomStatus").textContent = statusMap[room.status] || "Không rõ";
  $("#bookingRoomDescription").textContent = room.description || "";
  roomImage.alt = room.name || "Ảnh phòng";
  roomImage.hidden = !room.image_url;
  roomPlaceholder.hidden = Boolean(room.image_url);
  roomImage.onerror = () => {
    roomImage.hidden = true;
    roomPlaceholder.hidden = false;
  };
  if (room.image_url) roomImage.src = room.image_url;

  if (!bookingCheckIn.value || !bookingCheckOut.value || !bookingCheckInTime.value || !bookingCheckOutTime.value) {
    durationEl.textContent = "0 giờ";
    priceEl.textContent = money(room.price);
    totalEl.textContent = "0₫";
    bookingCheckOutTime.setCustomValidity("");
    $("#bookingCheckOutError").textContent = "";
    return;
  }

  const start = new Date(`${bookingCheckIn.value}T${bookingCheckInTime.value}:00`);
  const end = new Date(`${bookingCheckOut.value}T${bookingCheckOutTime.value}:00`);
  let checkoutError = "";
  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) {
    checkoutError = "Vui lòng nhập thời gian thuê hợp lệ.";
  } else if (end <= start) {
    checkoutError = "Thời gian trả phòng phải lớn hơn thời gian thuê.";
  } else if (end <= new Date()) {
    checkoutError = "Thời gian trả phòng không được trong quá khứ.";
  }
  bookingCheckOutTime.setCustomValidity(checkoutError);
  $("#bookingCheckOutError").textContent = checkoutError;

  if (checkoutError) {
    durationEl.textContent = "0 giờ";
    priceEl.textContent = money(room.price);
    totalEl.textContent = "0₫";
    return;
  }

  const durationMs = end - start;
  const totalMinutes = Math.floor(durationMs / 60000);
  const totalHours = durationMs / 3600000;
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  const hourlyRate = Number(room.price || 0) / 24;
  const total = totalHours * hourlyRate;
  durationEl.textContent = `${hours} giờ${minutes ? ` ${minutes} phút` : ""}`;
  priceEl.textContent = `${money(hourlyRate)} / giờ · ${money(room.price)} / đêm`;
  totalEl.textContent = money(total);
}

function fillRoomTypeOptions(selectedCode = "") {
  const select = $("#roomTypeSelect");
  if (!select) return;

  const availableTypes = roomTypes.filter(type => type.status === "active" || type.code === selectedCode);
  select.innerHTML = availableTypes.map(type =>
    `<option value="${escapeHtml(type.code)}">${escapeHtml(type.name)}${type.status === "inactive" ? " (Ngừng sử dụng)" : ""}</option>`
  ).join("");
  select.value = selectedCode || availableTypes[0]?.code || "";
}

function renderRoomTypes() {
  const tbody = $("#roomTypesTable");
  if (!tbody) return;

  tbody.innerHTML = roomTypes.length ? roomTypes.map(type => `
    <tr>
      <td><strong>${escapeHtml(type.code)}</strong></td>
      <td><strong>${escapeHtml(type.name)}</strong></td>
      <td>${escapeHtml(type.description || "")}</td>
      <td><strong>${money(type.price)}</strong></td>
      <td>${type.max_guests} khách</td>
      <td><span class="status ${type.status === "active" ? "success" : "delivered"}">${type.status === "active" ? "Đang dùng" : "Ngừng dùng"}</span></td>
      <td><div class="room-actions" style="padding:0"><button class="mini-button" data-room-type-edit="${type.id}">Sửa</button><button class="mini-button danger" data-room-type-delete="${type.id}">Xóa</button></div></td>
    </tr>
  `).join("") : `<tr><td colspan="7">Chưa có loại phòng.</td></tr>`;

  $$('[data-room-type-edit]').forEach(button => {
    button.addEventListener("click", () => {
      const type = roomTypes.find(item => item.id === Number(button.dataset.roomTypeEdit));
      if (type) openRoomTypeModal(type);
    });
  });

  $$('[data-room-type-delete]').forEach(button => {
    button.addEventListener("click", async () => {
      if (!confirm("Bạn có chắc muốn xóa loại phòng này?")) return;
      const { response, data } = await api(`/api/room-types/${button.dataset.roomTypeDelete}`, {
        method: "DELETE",
      });
      if (response.ok) {
        toast(data.message);
        await loadAll();
      } else {
        toast(data.message || "Không thể xóa loại phòng.");
      }
    });
  });
}

function openRoomTypeModal(type = null) {
  $("#roomTypeForm").reset();
  $("#roomTypeMessage").textContent = "";
  $("#roomTypeId").value = type?.id || "";
  $("#roomTypeModalTitle").textContent = type ? "Cập nhật loại phòng" : "Thêm loại phòng";

  if (type) {
    $("#roomTypeCode").value = type.code;
    $("#roomTypeName").value = type.name;
    $("#roomTypeDescription").value = type.description || "";
    $("#roomTypePrice").value = type.price;
    $("#roomTypeGuests").value = type.max_guests;
    $("#roomTypeStatus").value = type.status;
  } else {
    $("#roomTypePrice").value = 1800000;
    $("#roomTypeGuests").value = 4;
    $("#roomTypeStatus").value = "active";
  }
  openModal("roomTypeModal");
}

$("#openRoomTypeForm").addEventListener("click", () => openRoomTypeModal());

$("#roomTypeForm").addEventListener("submit", async event => {
  event.preventDefault();
  const id = $("#roomTypeId").value;
  const payload = {
    code: $("#roomTypeCode").value,
    name: $("#roomTypeName").value,
    description: $("#roomTypeDescription").value,
    price: Number($("#roomTypePrice").value),
    max_guests: Number($("#roomTypeGuests").value),
    status: $("#roomTypeStatus").value,
  };
  const { response, data } = await api(
    id ? `/api/room-types/${id}` : "/api/room-types",
    { method: id ? "PUT" : "POST", body: JSON.stringify(payload) }
  );
  message($("#roomTypeMessage"), data.message || "", response.ok);
  if (response.ok) {
    closeModal("roomTypeModal");
    toast(data.message);
    await loadAll();
  }
});

$$(".chip").forEach(button => {
  button.addEventListener("click", () => {
    $$(".chip").forEach(x => x.classList.remove("active"));
    button.classList.add("active");
    currentFilter = button.dataset.filter;
    renderRooms();
  });
});

$("#openRoomListForm").addEventListener("click", () => openRoomModal());

function openModal(id) {
  const modal = document.getElementById(id) || $(id);
  if (!modal) {
    console.warn(`Modal not found: ${id}`);
    return;
  }
  modal.classList.add("show");
}

function closeModal(id) {
  const modal = document.getElementById(id) || $(id);
  if (!modal) return;
  modal.classList.remove("show");
}

$$("[data-close]").forEach(button => {
  button.addEventListener("click", () => closeModal(button.dataset.close));
});

$("#bookingRoom").addEventListener("change", updateBookingSummary);
$("#bookingCheckIn").addEventListener("change", updateBookingSummary);
$("#bookingCheckOut").addEventListener("change", updateBookingSummary);
$("#bookingCheckInTime").addEventListener("change", updateBookingSummary);
$("#bookingCheckOutTime").addEventListener("change", updateBookingSummary);

$("#bookingForm").addEventListener("submit", async (event) => {
  event.preventDefault();

  const customerName = $("#bookingCustomer").value.trim();
  const roomId = Number($("#bookingRoom").value);
  const checkIn = $("#bookingCheckIn").value;
  const checkOut = $("#bookingCheckOut").value;
  const checkInTime = $("#bookingCheckInTime").value;
  const checkOutTime = $("#bookingCheckOutTime").value;
  updateBookingSummary();
  if (!$("#bookingForm").reportValidity()) return;

  if (!customerName) {
    message($("#bookingMessage"), "Vui lòng nhập tên khách hàng.");
    return;
  }
  if (!roomId || !checkIn || !checkOut) {
    message($("#bookingMessage"), "Vui lòng chọn phòng và ngày thuê hợp lệ.");
    return;
  }
  if (!checkInTime || !checkOutTime) {
    message($("#bookingMessage"), "Vui lòng chọn giờ nhận phòng và giờ trả phòng.");
    return;
  }

  const start = new Date(`${checkIn}T${checkInTime}:00`);
  const end = new Date(`${checkOut}T${checkOutTime}:00`);
  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime()) || end <= start) {
    message($("#bookingMessage"), "Giờ trả phòng phải sau giờ nhận phòng.");
    return;
  }

  const room = rooms.find(item => item.id === roomId);
  if (!room) {
    message($("#bookingMessage"), "Không tìm thấy phòng.");
    return;
  }
  if (lockedBookingRoomId !== null && roomId !== lockedBookingRoomId) {
    message($("#bookingMessage"), "Vui lòng giữ nguyên phòng đã chọn.");
    return;
  }
  const roomPrice = Number(room.price);
  if (!Number.isFinite(roomPrice) || roomPrice <= 0) {
    message($("#bookingMessage"), "Giá phòng không hợp lệ.");
    return;
  }

  const totalHours = (end - start) / 3600000;
  const expectedTotal = (Number(room.price || 0) / 24) * totalHours;
  const { response, data } = await api("/api/bookings", {
    method: "POST",
    body: JSON.stringify({
      customer_name: customerName,
      room_id: roomId,
      check_in: checkIn,
      check_out: checkOut,
      check_in_time: checkInTime,
      check_out_time: checkOutTime,
      total: expectedTotal,
    }),
  });

  message($("#bookingMessage"), data.message || "", response.ok);

  if (response.ok) {
    closeModal("bookingModal");
    toast("Cho thuê phòng thành công");
    await loadAll();
    if (returnToRoomListAfterBooking) {
      roomListFilter = "all";
      $$("[data-room-list-filter]").forEach(button =>
        button.classList.toggle("active", button.dataset.roomListFilter === "all")
      );
      setView("room-list");
    }
    returnToRoomListAfterBooking = false;
    lockedBookingRoomId = null;
  }
});

$("#openRoomForm").addEventListener("click", () => openRoomModal());

function openRoomModal(room = null) {
  $("#roomForm").reset();
  $("#roomMessage").textContent = "";
  selectedRoomImageFile = null;
  $("#roomImageFileName").textContent = "Chưa chọn ảnh";
  $("#roomId").value = room?.id || "";
  $("#roomModalTitle").textContent = room ? "Cập nhật phòng" : "Thêm phòng";
  fillRoomTypeOptions(room?.room_type || "");

  if (room) {
    $("#roomCode").value = room.code;
    $("#roomName").value = room.name;
    $("#roomDescription").value = room.description || "";
    $("#roomImage").value = room.image_url || "";
    $("#roomTypeSelect").value = room.room_type || "";
    $("#roomFloor").value = room.floor;
    $("#roomPrice").value = room.price;
    $("#roomStatus").value = room.status;
  } else {
    $("#roomFloor").value = 1;
    $("#roomPrice").value = 1000000;
    $("#roomStatus").value = "available";
  }

  openModal("roomModal");
}

$("#roomImageFile").addEventListener("change", () => {
  selectedRoomImageFile = $("#roomImageFile").files[0] || null;
  $("#roomImageFileName").textContent = selectedRoomImageFile?.name || "Chưa chọn ảnh";
});

$("#roomForm").addEventListener("submit", async (event) => {
  event.preventDefault();

  const roomTypeValue = $("#roomTypeSelect").value;
  if (!roomTypeValue) {
    message($("#roomMessage"), "Vui lòng chọn loại phòng.");
    return;
  }

  const id = $("#roomId").value;
  if (selectedRoomImageFile) {
    const formData = new FormData();
    formData.append("image", selectedRoomImageFile);
    const upload = await api("/api/rooms/image", { method: "POST", body: formData });
    if (!upload.response.ok) {
      message($("#roomMessage"), upload.data.message || "Không thể tải ảnh phòng lên.");
      return;
    }
    $("#roomImage").value = upload.data.image_url;
  }

  const payload = {
    code: $("#roomCode").value,
    name: $("#roomName").value,
    description: $("#roomDescription").value,
    image_url: $("#roomImage").value,
    room_type: roomTypeValue,
    floor: Number($("#roomFloor").value),
    price: Number($("#roomPrice").value),
    status: $("#roomStatus").value || "available",
  };

  const { response, data } = await api(id ? `/api/rooms/${id}` : "/api/rooms", {
    method: id ? "PUT" : "POST",
    body: JSON.stringify(payload),
  });

  message($("#roomMessage"), data.message || "", response.ok);

  if (response.ok) {
    selectedRoomImageFile = null;
    $("#roomImageFile").value = "";
    $("#roomImageFileName").textContent = "Chưa chọn ảnh";
    closeModal("roomModal");
    toast(data.message);
    await loadAll();
  }
});

checkSession();
