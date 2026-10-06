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
let calendarWeekOffset = 0;
let currentBookingSubview = "list";
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

function setView(view, bookingSubview = "list") {
  $$(".nav-item").forEach((item) => item.classList.toggle("active", item.dataset.view === view || (item.dataset.view === "rooms" && ["room-list", "room-types"].includes(view))));
  $$("[data-view-panel]").forEach((panel) => panel.classList.toggle("active", panel.dataset.viewPanel === view));
  $("#bookingBtn").classList.toggle("hidden", view !== "bookings");
  const bookingMenu = $(".nav-booking-group");
  const bookingMenuToggle = bookingMenu.querySelector('[data-view="bookings"]');
  bookingMenu.classList.remove("expanded");
  bookingMenuToggle.setAttribute("aria-expanded", "false");
  const roomMenu = $(".nav-room-group");
  const roomMenuToggle = roomMenu.querySelector('[data-view="rooms"]');
  if (view !== "rooms") roomMenu.classList.remove("expanded");
  roomMenuToggle.setAttribute("aria-expanded", String(roomMenu.classList.contains("expanded")));
  if (view === "rooms") renderRooms();
  if (view === "room-list") renderRoomList();
  if (view === "room-types") renderRoomTypes();
  if (view === "bookings") {
    currentBookingSubview = bookingSubview;
    $$('[data-booking-panel]').forEach(panel => panel.classList.toggle("active", panel.dataset.bookingPanel === currentBookingSubview));
    $$('[data-booking-subview]').forEach(button => button.classList.toggle("active", button.dataset.bookingSubview === currentBookingSubview));
    renderBookings();
  }
}

$$(".nav-item[data-view]").forEach((item) => {
  item.addEventListener("click", () => {
    if (item.dataset.view === "bookings") {
      const bookingMenu = item.closest(".nav-booking-group");
      const expanded = bookingMenu.classList.toggle("expanded");
      item.setAttribute("aria-expanded", String(expanded));
      return;
    }
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

$$('[data-booking-subview]').forEach(button => {
  button.addEventListener("click", () => setView("bookings", button.dataset.bookingSubview));
});

$$('[data-room-subview]').forEach(button => {
  button.addEventListener("click", () => setView(button.dataset.roomSubview));
});

$$("[data-go]").forEach((button) => {
  button.addEventListener("click", () => setView(button.dataset.go));
});

$("#calendarBookingBtn").addEventListener("click", () => openModal("bookingModal"));

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
    renderBookings();
    renderDashboard(dashboardResult.data);
    fillBookingRooms();
  } catch (error) {
    console.error(error);
  }
}

function renderDashboard(summary) {
  $("#statRevenue").textContent = money(summary.revenue);
  $("#chartTotal").textContent = money(summary.revenue);
  $("#statBookings").textContent = summary.bookings;
  $("#bookingBadge").textContent = summary.bookings;
  $("#statAvailable").textContent = summary.available_rooms;
  $("#statOccupancy").textContent = `${summary.occupancy}%`;
  $("#statOccupied").textContent = summary.occupied_rooms;
  renderFrontDeskSummary();
  renderCalendar();

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

function formatCalendarDate(date, options) {
  return new Intl.DateTimeFormat("vi-VN", options).format(date);
}

function renderFrontDeskSummary() {
  const today = localDateString(new Date());
  const validForToday = bookings.filter(booking => booking.status !== "cancelled");
  $("#arrivalsToday").textContent = validForToday.filter(booking => booking.check_in === today).length;
  $("#departuresToday").textContent = validForToday.filter(booking => booking.check_out === today).length;

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

function renderCalendar() {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const weekStart = new Date(today);
  const mondayOffset = (weekStart.getDay() + 6) % 7;
  weekStart.setDate(weekStart.getDate() - mondayOffset + calendarWeekOffset * 7);
  const weekEnd = new Date(weekStart);
  weekEnd.setDate(weekEnd.getDate() + 7);

  const days = Array.from({ length: 7 }, (_, index) => {
    const date = new Date(weekStart);
    date.setDate(date.getDate() + index);
    return date;
  });
  const weekStartIso = localDateString(weekStart);
  const weekEndIso = localDateString(weekEnd);
  $("#calendarRange").textContent = `${formatCalendarDate(weekStart, { day: "numeric", month: "short" })} - ${formatCalendarDate(days[6], { day: "numeric", month: "short", year: "numeric" })}`;

  const dateHeader = days.map((date, index) => `
    <div class="calendar-date ${localDateString(date) === localDateString(today) ? "is-today" : ""}">
      <span>${["T2", "T3", "T4", "T5", "T6", "T7", "CN"][index]}</span>
      <strong>${formatCalendarDate(date, { day: "2-digit", month: "2-digit" })}</strong>
    </div>
  `).join("");

  const roomRows = rooms.map(room => {
    const roomBookings = bookings
      .filter(booking => booking.room_code === room.code && booking.check_in < weekEndIso && booking.check_out > weekStartIso)
      .map(booking => {
        const checkIn = parseLocalDate(booking.check_in);
        const checkOut = parseLocalDate(booking.check_out);
        if (!checkIn || !checkOut || checkOut <= checkIn) return null;
        const start = Math.max(0, dateOffset(checkIn, weekStart));
        const end = Math.min(7, dateOffset(checkOut, weekStart));
        return end > start ? { booking, start, end } : null;
      })
      .filter(Boolean)
      .sort((left, right) => left.start - right.start || left.end - right.end);

    const lanes = [];
    roomBookings.forEach(item => {
      let lane = lanes.find(candidate => candidate.end <= item.start);
      if (!lane) {
        lane = { end: 0, bookings: [] };
        lanes.push(lane);
      }
      lane.end = item.end;
      lane.bookings.push(item);
    });

    const timeline = (lanes.length ? lanes : [{ bookings: [] }]).map(lane => {
      const dayCells = days.map((date, index) => `
        <span class="calendar-day-cell ${localDateString(date) === localDateString(today) ? "is-today" : ""}" style="grid-column:${index + 1}" aria-hidden="true"></span>
      `).join("");
      const bookingBars = lane.bookings.map(({ booking, start, end }) => {
        const statusClassName = ({ booked: "booked", checked_in: "checked-in", checked_out: "checked-out", cancelled: "cancelled" })[booking.status] || "booked";
        const statusLabel = ({ booked: "Đã đặt", checked_in: "Đang ở", checked_out: "Đã trả phòng", cancelled: "Đã hủy" })[booking.status] || "Đặt phòng";
        const guestName = escapeHtml(booking.customer_name || "Khách chưa cập nhật");
        const code = escapeHtml(booking.code || "");
        const title = escapeHtml(`${booking.customer_name || "Khách"} · ${booking.check_in} - ${booking.check_out} · ${statusLabel} · #${booking.code || ""}`);
        return `<button class="calendar-booking ${statusClassName}" type="button" data-calendar-booking="${code}" title="${title}" aria-label="${title}" style="grid-column:${start + 1} / span ${end - start}"><span>${guestName}</span><small>#${code}</small></button>`;
      }).join("");
      return `<div class="calendar-lane">${dayCells}${bookingBars}</div>`;
    }).join("");

    const roomLabel = `${room.name} · ${room.code} · ${room.room_type_name || room.room_type || ""} · ${money(room.price)}/đêm`;
    return `
      <div class="calendar-room-row">
        <div class="calendar-room">
          <button type="button" class="calendar-room-link" data-calendar-room="${escapeHtml(room.code)}" aria-label="Mở phòng ${escapeHtml(room.code)}">
            <strong>${escapeHtml(room.name || `Phòng ${room.code}`)}</strong>
            <span>${escapeHtml(room.code)} · ${escapeHtml(room.room_type_name || room.room_type || "Phòng")} · ${money(room.price)}/đêm</span>
          </button>
          <i class="calendar-room-status ${escapeHtml(room.status || "available")}" title="${escapeHtml(statusMap[room.status] || "Trạng thái phòng")}"></i>
        </div>
        <div class="calendar-room-timeline">${timeline}</div>
      </div>`;
  }).join("");

  $("#reservationsCalendar").innerHTML = `
    <div class="calendar-board">
      <div class="calendar-date-row"><div class="calendar-room-heading">Phòng</div>${dateHeader}</div>
      ${roomRows || `<div class="calendar-empty">Chưa có phòng để hiển thị.</div>`}
    </div>`;
}

$$('[data-calendar-shift]').forEach(button => {
  button.addEventListener("click", () => {
    calendarWeekOffset += Number(button.dataset.calendarShift);
    renderCalendar();
  });
});

$("[data-calendar-today]").addEventListener("click", () => {
  calendarWeekOffset = 0;
  renderCalendar();
});

$("#reservationsCalendar").addEventListener("click", event => {
  const bookingButton = event.target.closest("[data-calendar-booking]");
  if (bookingButton) {
    setView("bookings");
    return;
  }

  const roomButton = event.target.closest("[data-calendar-room]");
  if (roomButton) {
    setView("rooms");
  }
});

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
    const statusLabel = room.status === "occupied" ? "Đã có người thuê" : statusMap[room.status] || "Không rõ";
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
  if (!confirm("Xóa phòng này và tất cả đặt phòng liên quan? Dữ liệu đặt phòng sẽ bị xóa vĩnh viễn.")) return;
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
  const editButton = event.target.closest("[data-edit]");
  const deleteButton = event.target.closest("[data-delete]");
  const roomId = Number(viewButton?.dataset.roomView || editButton?.dataset.edit || deleteButton?.dataset.delete);
  if (!roomId) return;
  const room = rooms.find(item => item.id === roomId);
  if (!room) return;
  if (viewButton) openRoomDetails(room);
  if (editButton) openRoomModal(room);
  if (deleteButton && !deleteButton.disabled) deleteRoom(roomId);
}

function renderRooms() {
  const filtered = currentFilter === "all"
    ? rooms
    : rooms.filter(room => room.status === currentFilter);
  renderRoomCards($("#roomsGrid"), filtered);
}

function renderBookings() {
  const html = bookings.map(booking => `
    <tr>
      <td><strong>#${booking.code}</strong></td>
      <td>${booking.customer_name}</td>
      <td>${booking.room_name} · ${booking.room_code}</td>
      <td>${booking.check_in}</td>
      <td>${booking.check_out}</td>
      <td><strong>${money(booking.total)}</strong></td>
      <td><span class="status ${booking.status === "checked_in" ? "success" : "processing"}">${booking.status === "checked_in" ? "Đang ở" : "Đã đặt"}</span></td>
    </tr>`).join("");

  $("#allBookings").innerHTML = html || `<tr><td colspan="7">Chưa có đặt phòng.</td></tr>`;
  $("#recentBookings").innerHTML = bookings.slice(0, 5).map(booking => `
    <tr>
      <td><strong>#${booking.code}</strong></td>
      <td><div class="customer"><div class="mini-avatar">${booking.customer_name[0] || "K"}</div>${booking.customer_name}</div></td>
      <td>${booking.room_name} · ${booking.room_code}</td>
      <td>${booking.check_in}</td>
      <td>${booking.check_out}</td>
      <td><strong>${money(booking.total)}</strong></td>
      <td><span class="status ${booking.status === "checked_in" ? "success" : "processing"}">${booking.status === "checked_in" ? "Đang ở" : "Đã đặt"}</span></td>
    </tr>`).join("");
}

function fillBookingRooms() {
  $("#bookingRoom").innerHTML = rooms
    .filter(room => room.status === "available")
    .map(room => `<option value="${room.id}">Phòng ${room.code} — ${room.name} — ${money(room.price)}/đêm</option>`)
    .join("");
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

$("#bookingBtn").addEventListener("click", () => {
  $("#bookingForm").reset();
  $("#bookingMessage").textContent = "";
  fillBookingRooms();
  openModal("bookingModal");
});

$("#bookingBtn2").addEventListener("click", () => {
  $("#bookingForm").reset();
  $("#bookingMessage").textContent = "";
  fillBookingRooms();
  openModal("bookingModal");
});

$("#bookingForm").addEventListener("submit", async (event) => {
  event.preventDefault();

  const { response, data } = await api("/api/bookings", {
    method: "POST",
    body: JSON.stringify({
      customer_name: $("#bookingCustomer").value,
      room_id: Number($("#bookingRoom").value),
      check_in: $("#bookingCheckIn").value,
      check_out: $("#bookingCheckOut").value,
      check_in_time: $("#bookingCheckInTime").value,
      check_out_time: $("#bookingCheckOutTime").value,
    }),
  });

  message($("#bookingMessage"), data.message || "", response.ok);

  if (response.ok) {
    closeModal("bookingModal");
    toast("Đặt phòng thành công");
    await loadAll();
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
