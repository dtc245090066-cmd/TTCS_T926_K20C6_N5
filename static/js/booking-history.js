"use strict";
const historyParams = new URLSearchParams(window.location.search);
const historyYear = Number(historyParams.get("year"));
const historyMonth = Number(historyParams.get("month"));
const historyForm = document.querySelector("#historyFilters");
const historyDialog = document.querySelector("#historyDetail");
const bookingLabels = {booked: "Đã đặt", checked_in: "Đang ở", checked_out: "Đã trả phòng", cancelled: "Đã hủy"};
let historyPage = 1;
let historyPages = 1;
let historyRequest = 0;
let detailRequest = 0;
const historyMoney = value => new Intl.NumberFormat("vi-VN", {style:"currency", currency:"VND"}).format(value);
const historyEscape = value => String(value ?? "—").replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
const historyDisplay = value => value === null || value === undefined || value === "" ? "—" : value;
function historyDate(value, time) {
  if (!value) return "—";
  const parts = value.split("-");
  return (parts.length === 3 ? parts.reverse().join("/") : value) + (time ? ` ${time}` : "");
}
async function historyApi(url) {
  const response = await fetch(url, {headers:{Accept:"application/json"}, cache:"no-store"});
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.message || "Không thể tải dữ liệu. Vui lòng thử lại.");
  return data;
}
function updateHistoryPager(loading = false) {
  document.querySelector("#historyPrevious").disabled = loading || historyPage <= 1;
  document.querySelector("#historyNext").disabled = loading || historyPage >= historyPages;
}
async function loadHistory() {
  const requestId = ++historyRequest;
  const message = document.querySelector("#historyMessage");
  message.textContent = "Đang tải lịch sử đặt phòng…";
  document.querySelector("#historyRows").replaceChildren();
  for (const id of ["historyCount", "historyRevenue", "historyCancelled"]) document.getElementById(id).textContent = "—";
  document.querySelector("#historyValue").textContent = "";
  document.querySelector("#historyPage").textContent = "";
  updateHistoryPager(true);
  const query = new URLSearchParams(new FormData(historyForm));
  query.set("year", historyYear);
  query.set("month", historyMonth);
  query.set("page", historyPage);
  try {
    const data = await historyApi(`/api/booking-history?${query}`);
    if (requestId !== historyRequest) return;
    historyPage = data.page;
    historyPages = data.pages;
    document.querySelector("#historyCount").textContent = data.summary.booking_count;
    document.querySelector("#historyRevenue").textContent = historyMoney(data.summary.revenue);
    document.querySelector("#historyCancelled").textContent = data.summary.cancelled_count || 0;
    document.querySelector("#historyValue").textContent = `Tổng giá trị đơn trong tháng (gồm đơn hủy): ${historyMoney(data.summary.booking_value)}. Các thẻ tổng quan tính cho cả tháng, không thay đổi theo bộ lọc danh sách.`;
    document.querySelector("#historyRows").innerHTML = data.bookings.map(item => {
      const cells = [item.code, item.customer_name, item.customer_phone, item.customer_email,
        [item.room_code, item.room_name].filter(Boolean).join(" · "), historyDate(item.check_in, item.check_in_time),
        historyDate(item.check_out, item.check_out_time), item.nights, historyMoney(item.total), bookingLabels[item.status] || item.status, "—"];
      return `<tr>${cells.map(value => `<td>${historyEscape(historyDisplay(value))}</td>`).join("")}<td><button type="button" data-booking-id="${Number(item.id)}">Xem chi tiết</button></td></tr>`;
    }).join("");
    message.textContent = data.count ? `${data.count} đơn phù hợp · Sắp xếp theo ngày trả phòng mới nhất.` : "Không có đơn đặt phòng phù hợp trong tháng được chọn.";
    document.querySelector("#historyPage").textContent = `Trang ${data.page} / ${data.pages}`;
    updateHistoryPager();
  } catch (error) {
    if (requestId !== historyRequest) return;
    message.textContent = error.message;
  }
}
function detailSection(title, fields) {
  return `<section><h3>${historyEscape(title)}</h3><dl>${fields.map(([label,value]) => `<dt>${historyEscape(label)}</dt><dd>${historyEscape(historyDisplay(value))}</dd>`).join("")}</dl></section>`;
}
async function showHistoryDetail(id) {
  const requestId = ++detailRequest;
  const content = document.querySelector("#historyDetailContent");
  content.textContent = "Đang tải chi tiết…";
  historyDialog.showModal();
  try {
    const {booking: b} = await historyApi(`/api/booking-history/${id}`);
    if (requestId !== detailRequest || !historyDialog.open) return;
    content.innerHTML = `<div class="history-detail-grid">${[
      detailSection("Thông tin đặt phòng", [["Mã đặt phòng",b.code],["Ngày tạo (theo dữ liệu lưu)",b.created_at],["Trạng thái",bookingLabels[b.status] || b.status],["Nguồn đặt phòng",null]]),
      detailSection("Khách hàng", [["Họ tên",b.customer_name],["Điện thoại",b.customer_phone],["Email",b.customer_email]]),
      detailSection("Lưu trú", [["Phòng",[b.room_code,b.room_name].filter(Boolean).join(" · ")],["Loại phòng",b.room_type_name],["Nhận phòng",historyDate(b.check_in,b.check_in_time)],["Trả phòng",historyDate(b.check_out,b.check_out_time)],["Số đêm (chênh lệch ngày)",b.nights],["Số khách",null],["Yêu cầu đặc biệt",null]]),
      detailSection("Thanh toán", [["Giá phòng/đêm tại lúc đặt",null],["Số đêm",b.nights],["Phụ phí / dịch vụ",null],["Giảm giá",null],["Tổng tiền đơn",historyMoney(b.total)],["Đã thanh toán",null],["Còn nợ",null],["Phương thức",null],["Trạng thái thanh toán",null],["Thời điểm thanh toán",null]]),
      detailSection("Lịch sử thay đổi trạng thái", [["Lịch sử",null]])
    ].join("")}</div><p class="history-note">Dấu “—” thể hiện thông tin chưa được lưu. Giá phòng hiện tại không được dùng thay cho giá tại thời điểm đặt; số đêm hiển thị không làm thay đổi tổng tiền đơn.</p>`;
  } catch (error) {
    if (requestId === detailRequest && historyDialog.open) content.textContent = error.message;
  }
}
document.querySelector("#closeHistoryDetail").addEventListener("click", () => historyDialog.close());
historyDialog.addEventListener("close", () => { detailRequest++; document.querySelector("#historyDetailContent").replaceChildren(); });
document.querySelector("#historyRows").addEventListener("click", event => {
  const button = event.target.closest("[data-booking-id]");
  if (button) showHistoryDetail(Number(button.dataset.bookingId));
});
historyForm.addEventListener("submit", event => { event.preventDefault(); historyPage = 1; loadHistory(); });
document.querySelector("#historyPrevious").addEventListener("click", () => { if (historyPage > 1) { historyPage--; loadHistory(); } });
document.querySelector("#historyNext").addEventListener("click", () => { if (historyPage < historyPages) { historyPage++; loadHistory(); } });
if (Number.isInteger(historyYear) && historyYear >= 1 && historyYear <= 9999 && Number.isInteger(historyMonth) && historyMonth >= 1 && historyMonth <= 12) {
  document.querySelector("#historyPeriod").textContent = `Tháng ${historyMonth} năm ${historyYear}`;
  document.querySelector("#backToRevenue").href = `/?view=revenue&year=${historyYear}`;
  loadHistory();
} else {
  document.querySelector("#historyMessage").textContent = "Tháng hoặc năm không hợp lệ. Vui lòng quay lại thống kê và chọn tháng.";
  historyForm.querySelectorAll("input, select, button").forEach(element => { element.disabled = true; });
  updateHistoryPager(true);
}
