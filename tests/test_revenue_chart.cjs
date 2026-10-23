const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const source = fs.readFileSync("static/js/app.js", "utf8");
const elements = new Map();
const element = selector => {
  if (!elements.has(selector)) elements.set(selector, {
    textContent: "", innerHTML: "", value: "", classList: { toggle() {}, add() {}, remove() {} },
  });
  return elements.get(selector);
};
let destroyed = 0;
const context = vm.createContext({
  Intl, console, $: element, document: { getElementById: id => element(`#${id}`) },
  Chart: class { constructor(canvas, config) { this.config = config; } destroy() { destroyed++; } },
});
vm.runInContext(`let revenueChart; let revenueRequestId = 0; let selectedRevenueYear = 2026; let api;
${source.slice(source.indexOf("function money("), source.indexOf("function padTime("))}
${source.slice(source.indexOf("async function fetchRevenueStatistics("), source.indexOf("async function exportRevenuePdf("))}
${source.slice(source.indexOf("function renderRevenueStatistics("), source.indexOf("function renderDashboard("))}
`, context);
const run = text => vm.runInContext(text, context);

(async () => {
  run('renderRevenueStatistics({year:2026,total:7050000,months:[{month:3,total:7050000}]})');
  assert.equal(run("revenueChart.config.data.datasets[0].data.length"), 12);
  assert.equal(run("revenueChart.config.data.datasets[0].data[0]"), 0);
  assert.equal(run("revenueChart.config.data.datasets[0].data[2]"), 7050000);
  assert.equal((element("#revenueTableBody").innerHTML.match(/<tr>/g) || []).length, 12);
  assert.ok(element("#revenueTableBody").innerHTML.includes("7.050.000"));
  assert.match(run('revenueChart.config.options.plugins.tooltip.callbacks.label({parsed:{y:7050000}})'), /7\.050\.000\s*₫/);
  assert.equal(run("revenueChart.config.options.maintainAspectRatio"), false);
  context.window = {location: {assign(url) { context.clickedUrl = url; }}};
  run('revenueChart.config.options.onClick({}, [{index:10}])');
  assert.equal(context.clickedUrl, "/booking-history?year=2026&month=11");
  run('revenueChart.config.options.onClick({}, [{index:1}])');
  assert.equal(context.clickedUrl, "/booking-history?year=2026&month=2");
  run('revenueChart.config.options.onClick({}, [])');
  assert.equal(context.clickedUrl, "/booking-history?year=2026&month=2");
  assert.ok(element("#revenueTableBody").innerHTML.includes('/booking-history?year=2026&month=11'));
  assert.equal(run('revenueChart.config.options.scales.x.ticks.callback.call({chart:{width:375}},11)'), "T12");
  assert.equal(run('revenueChart.config.options.scales.x.ticks.callback.call({chart:{width:1024},getLabelForValue:()=>"Tháng 12"},11)'), "Tháng 12");
  run('renderRevenueStatistics({year:2025,total:0,months:[]})');
  assert.equal(destroyed, 1);
  assert.match(element("#revenueChartMessage").textContent, /2025.*chưa có doanh thu/);

  const pending = [];
  context.mockApi = () => new Promise(resolve => pending.push(resolve));
  run("api = mockApi");
  const first = run("fetchRevenueStatistics(2025)");
  const second = run("fetchRevenueStatistics(2026)");
  pending[1]({response:{ok:true}, data:{year:2026,total:5,months:[{month:1,total:5}]}});
  await second;
  pending[0]({response:{ok:true}, data:{year:2025,total:10,months:[]}});
  await first;
  assert.equal(run("selectedRevenueYear"), 2026);
  assert.equal(run("revenueChart.config.data.datasets[0].data[0]"), 5);
  run('api = async () => ({response:{ok:false},data:{}})');
  await run("fetchRevenueStatistics(2024)");
  assert.equal(run("revenueChart"), null);
  assert.equal(element("#revenueYearValue").textContent, "—");
  assert.match(element("#revenueChartMessage").textContent, /Không thể tải/);
  run('api = async () => { throw new Error("network"); }');
  await run("fetchRevenueStatistics(2023)");
  assert.equal(run("revenueChart"), null);
  for (const months of [
    [{month:1,total:5},{month:1,total:5}],
    [{month:13,total:10}],
    [{month:1,total:"invalid"}],
    [{month:1,total:9}],
    [null],
  ]) {
    context.invalidMonths = months;
    run('api = async () => ({response:{ok:true},data:{year:2026,total:10,months:invalidMonths}})');
    await run("fetchRevenueStatistics(2026)");
    assert.equal(run("revenueChart"), null);
    assert.equal(element("#revenueYearValue").textContent, "—");
  }
  run('Chart = undefined; renderRevenueStatistics({year:2026,total:0,months:[]})');
  assert.match(element("#revenueChartMessage").textContent, /thư viện/);
  console.log("Revenue chart: data, tooltip, responsive labels, empty state, lifecycle, stale requests and errors passed.");
})().catch(error => { console.error(error); process.exitCode = 1; });
