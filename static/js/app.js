const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

const authView = $("#authView");
const dashboardView = $("#dashboardView");
const loginPanel = $("#loginPanel");
const registerPanel = $("#registerPanel");

let rooms = [];
let bookings = [];
let currentFilter = "all";
let chart;

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
  el.classList.add("show");
  clearTimeout(window.__toastTimer);
  window.__toastTimer = setTimeout(() => el.classList.remove("show"), 2500);
}

function message(el, text, success = false) {
  el.textContent = text || "";
  el.classList.toggle("success", success);
}

async function api(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const data = await response.json().catch(() => ({}));
  if (response.status === 401) {
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

function showDashboard(user) {
  authView.classList.add("hidden");
  dashboardView.classList.remove("hidden");
  $("#userName").textContent = user.full_name;
  $("#userRole").textContent = user.role === "manager" ? "Quản lý" : "Nhân viên";
  loadAll();
}

async function checkSession() {
  try {
    const { data } = await api("/api/session");
    if (data.user) showDashboard(data.user);
    else showLogin();
  } catch {
    showLogin();
  }
}

$("#loginForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const { response, data } = await api("/api/login", {
    method: "POST",
    body: JSON.stringify({
      email: $("#loginEmail").value,
      password: $("#loginPassword").value,
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

$("#logoutBtn").addEventListener("click", async () => {
  await api("/api/logout", { method: "POST" });
  showLogin();
  toast("Đã đăng xuất");
});

function setView(view) {
  $$(".nav-item").forEach((item) => item.classList.toggle("active", item.dataset.view === view));
  $$("[data-view-panel]").forEach((panel) => panel.classList.toggle("active", panel.dataset.viewPanel === view));
  $("#sidebar").classList.remove("open");
  if (view === "rooms") renderRooms();
  if (view === "bookings") renderBookings();
}

$$(".nav-item[data-view]").forEach((item) => {
  item.addEventListener("click", () => setView(item.dataset.view));
});

$$("[data-go]").forEach((button) => {
  button.addEventListener("click", () => setView(button.dataset.go));
});

$("#mobileMenu").addEventListener("click", () => $("#sidebar").classList.toggle("open"));

async function loadAll() {
  try {
    const [roomsResult, bookingsResult, dashboardResult] = await Promise.all([
      api("/api/rooms"),
      api("/api/bookings"),
      api("/api/dashboard"),
    ]);

    rooms = roomsResult.data.rooms || [];
    bookings = bookingsResult.data.bookings || [];

    renderRooms();
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
  $("#houseOccupied").textContent = summary.occupied_rooms;
  $("#houseCleaning").textContent = summary.cleaning_rooms;
  $("#houseMaintenance").textContent = summary.maintenance_rooms;

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

  $("#reportGrid").innerHTML = `
    <div><span>Tổng số phòng</span><strong>${summary.rooms}</strong></div>
    <div><span>Phòng trống</span><strong>${summary.available_rooms}</strong></div>
    <div><span>Đang ở</span><strong>${summary.occupied_rooms}</strong></div>
    <div><span>Đang dọn</span><strong>${summary.cleaning_rooms}</strong></div>
    <div><span>Bảo trì</span><strong>${summary.maintenance_rooms}</strong></div>
    <div><span>Doanh thu</span><strong>${money(summary.revenue)}</strong></div>`;
}

function renderRooms() {
  const filtered = currentFilter === "all"
    ? rooms
    : rooms.filter(room => room.status === currentFilter);

  $("#roomsGrid").innerHTML = filtered.length ? filtered.map(room => `
    <article class="room-card">
      <div class="room-card-top">
        <span class="room-code">${room.code}</span>
        <span class="room-status ${statusClass[room.status] || ""}">${statusMap[room.status]}</span>
      </div>
      <img src="${room.image_url || ""}" alt="${room.name}">
      <div class="room-meta">
        <h4>${room.name}</h4>
        <p>${room.description || ""}</p>
      </div>
      <div class="room-footer">
        <span class="room-type">${room.room_type.toUpperCase()} · Tầng ${room.floor}</span>
        <strong>${money(room.price)}</strong>
      </div>
      <div class="room-actions">
        <button class="mini-button" data-edit="${room.id}">Cập nhật</button>
        <button class="mini-button danger" data-delete="${room.id}" ${room.status !== "available" ? "disabled" : ""}>Xóa</button>
      </div>
    </article>
  `).join("") : `<article class="panel empty-feature"><h3>Không có phòng</h3><p>Thử đổi bộ lọc.</p></article>`;

  $$("[data-edit]").forEach(btn => btn.addEventListener("click", () => {
    const room = rooms.find(x => x.id === Number(btn.dataset.edit));
    openRoomModal(room);
  }));

  $$("[data-delete]").forEach(btn => btn.addEventListener("click", async () => {
    if (btn.disabled) return;
    if (!confirm("Bạn có chắc muốn xóa phòng này?")) return;

    const { response, data } = await api(`/api/rooms/${btn.dataset.delete}`, { method: "DELETE" });
    if (response.ok) {
      toast(data.message);
      await loadAll();
    } else {
      toast(data.message || "Không thể xóa phòng.");
    }
  }));
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

$$(".chip").forEach(button => {
  button.addEventListener("click", () => {
    $$(".chip").forEach(x => x.classList.remove("active"));
    button.classList.add("active");
    currentFilter = button.dataset.filter;
    renderRooms();
  });
});

function openModal(id) {
  $(id).classList.add("show");
}

function closeModal(id) {
  $(id).classList.remove("show");
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
  $("#roomId").value = room?.id || "";
  $("#roomModalTitle").textContent = room ? "Cập nhật phòng" : "Thêm phòng";

  if (room) {
    $("#roomCode").value = room.code;
    $("#roomName").value = room.name;
    $("#roomDescription").value = room.description || "";
    $("#roomImage").value = room.image_url || "";
    $("#roomType").value = room.room_type;
    $("#roomFloor").value = room.floor;
    $("#roomPrice").value = room.price;
    $("#roomStatus").value = room.status;
  } else {
    $("#roomFloor").value = 1;
    $("#roomPrice").value = 1000000;
    $("#roomType").value = "double";
    $("#roomStatus").value = "available";
  }

  openModal("roomModal");
}

$("#roomForm").addEventListener("submit", async (event) => {
  event.preventDefault();

  const id = $("#roomId").value;
  const payload = {
    code: $("#roomCode").value,
    name: $("#roomName").value,
    description: $("#roomDescription").value,
    image_url: $("#roomImage").value,
    room_type: $("#roomType").value,
    floor: Number($("#roomFloor").value),
    price: Number($("#roomPrice").value),
    status: $("#roomStatus").value,
  };

  const { response, data } = await api(id ? `/api/rooms/${id}` : "/api/rooms", {
    method: id ? "PUT" : "POST",
    body: JSON.stringify(payload),
  });

  message($("#roomMessage"), data.message || "", response.ok);

  if (response.ok) {
    closeModal("roomModal");
    toast(data.message);
    await loadAll();
  }
});

$("#searchInput").addEventListener("input", (event) => {
  const q = event.target.value.trim().toLowerCase();
  $$(".room-card").forEach(card => {
    card.style.display = card.textContent.toLowerCase().includes(q) ? "" : "none";
  });
  $$("#allBookings tr, #recentBookings tr").forEach(row => {
    row.style.display = row.textContent.toLowerCase().includes(q) ? "" : "none";
  });
});

checkSession();
