const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const elements = new Map();
const element = selector => {
  if (!elements.has(selector)) elements.set(selector, {
    textContent:"", innerHTML:"", disabled:false, open:false,
    addEventListener() {}, replaceChildren() { this.innerHTML = ""; },
    showModal() { this.open = true; }, close() { this.open = false; },
  });
  return elements.get(selector);
};
const context = vm.createContext({
  Intl, URLSearchParams, FormData: class { *[Symbol.iterator]() {} },
  window: {location: {search:"?year=2026&month=11"}},
  document: {querySelector:element, getElementById:id => element(`#${id}`)},
});
const source = fs.readFileSync("static/js/booking-history.js", "utf8");
vm.runInContext(source.slice(0, source.lastIndexOf("if (Number.isInteger(historyYear)")), context);
const run = code => vm.runInContext(code, context);
const booking = {id:1, code:"NOV-A", customer_name:'<img src=x onerror="alert(1)">',
  customer_phone:"0901234567", customer_email:"anh@test.local", room_code:"101",
  check_in:"2026-10-30", check_out:"2026-11-01", total:7050000, nights:2, status:"checked_out"};
const report = {page:1,pages:2,count:21,summary:{booking_count:21,revenue:7050000,booking_value:7050000,cancelled_count:0},bookings:[booking]};
(async () => {
  const urls = [];
  context.fetch = async url => { urls.push(url); return {ok:true,json:async () => report}; };
  await run("loadHistory()");
  assert.match(urls[0], /year=2026&month=11&page=1/);
  assert.match(element("#historyRows").innerHTML, /&lt;img/);
  assert.ok(!element("#historyRows").innerHTML.includes("<img"));
  assert.match(element("#historyRevenue").textContent, /7\.050\.000/);
  assert.equal(element("#historyNext").disabled, false);
  context.fetch = async () => ({ok:true,json:async () => ({booking})});
  await run("showHistoryDetail(1)");
  assert.equal(element("#historyDetail").open, true);
  assert.match(element("#historyDetailContent").innerHTML, /0901234567/);
  assert.match(element("#historyDetailContent").innerHTML, /7\.050\.000/);
  assert.match(element("#historyDetailContent").innerHTML, /01\/11\/2026/);
  const pending = [];
  context.fetch = () => new Promise(resolve => pending.push(resolve));
  const first = run("loadHistory()");
  const second = run("loadHistory()");
  pending[1]({ok:true,json:async () => ({...report,count:0,bookings:[]})});
  await second;
  pending[0]({ok:true,json:async () => report});
  await first;
  assert.equal(element("#historyRows").innerHTML, "");
  assert.match(element("#historyMessage").textContent, /Không có đơn/);
  context.fetch = async () => ({ok:false,json:async () => ({message:"Không đủ quyền"})});
  await run("loadHistory()");
  assert.equal(element("#historyMessage").textContent, "Không đủ quyền");
  assert.equal(element("#historyRevenue").textContent, "—");
  console.log("Booking history: period, rendering, escaping, detail, pagination state, stale requests and errors passed.");
})().catch(error => {console.error(error); process.exitCode = 1;});
