# -*- coding: utf-8 -*-
"""
Olist 电商数据大屏 —— 科技风 ECharts 模板模块
================================================
仅包含大屏 HTML/CSS/JS 模板字符串与渲染函数，数据由外部注入：
    render_dashboard_html(payload: dict, geojson: dict) -> str

依赖：ECharts 5.5.1（npmmirror CDN 为主，jsdelivr 兜底）。
"""

# 占位符：构建时用 json.dumps 结果替换
_PAYLOAD_PLACEHOLDER = "__PAYLOAD_JSON__"
_GEOJSON_PLACEHOLDER = "__GEOJSON_JSON__"


def _js_json(obj) -> str:
    """序列化并安全嵌入 <script>（防止 </script> 提前闭合）。"""
    import json

    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def render_dashboard_html(payload: dict, geojson: dict) -> str:
    """把聚合数据与大屏模板组装为完整 HTML。"""
    return _TEMPLATE.replace(_PAYLOAD_PLACEHOLDER, _js_json(payload)).replace(
        _GEOJSON_PLACEHOLDER, _js_json(geojson)
    )


_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<script src="https://registry.npmmirror.com/echarts/5.5.1/files/dist/echarts.min.js"></script>
<script>window.__ECHARTS__ = false; window.addEventListener('error', function(e){ if(!window.__ECHARTS__ && e.target && e.target.tagName === 'SCRIPT'){ var s = document.createElement('script'); s.src = 'https://cdn.jsdelivr.net/npm/echarts@5.5.1/dist/echarts.min.js'; document.head.appendChild(s); } }, true);</script>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 100%; }
body {
  background:
    radial-gradient(ellipse at 50% -18%, rgba(20, 80, 190, .30) 0%, rgba(5, 15, 40, 0) 58%),
    radial-gradient(ellipse at 110% 110%, rgba(0, 120, 220, .12) 0%, rgba(5, 15, 40, 0) 50%),
    linear-gradient(180deg, #04102c 0%, #020818 100%);
  font-family: "Segoe UI", "Microsoft YaHei", "PingFang SC", sans-serif;
  color: #cfe8ff;
  overflow-x: hidden;
  min-height: 100vh;
}
/* ---- 网格背景 + 扫描线 ---- */
body::before {
  content: ""; position: fixed; inset: 0; z-index: 0; pointer-events: none;
  background-image:
    linear-gradient(rgba(0, 220, 255, .045) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 220, 255, .045) 1px, transparent 1px);
  background-size: 44px 44px;
  -webkit-mask-image: radial-gradient(ellipse at 50% 30%, #000 30%, transparent 82%);
          mask-image: radial-gradient(ellipse at 50% 30%, #000 30%, transparent 82%);
}
.scanline {
  position: fixed; left: 0; right: 0; top: 0; height: 140px; z-index: 1; pointer-events: none;
  background: linear-gradient(180deg, transparent, rgba(0, 229, 255, .05), transparent);
  animation: scanmove 9s linear infinite;
}
@keyframes scanmove { 0% { transform: translateY(-160px); } 100% { transform: translateY(120vh); } }

.dash { position: relative; z-index: 2; padding: 14px 16px 10px; }
/* ---- 顶部标题栏 ---- */
.dash-header {
  position: relative; display: flex; align-items: center; justify-content: center;
  height: 56px; margin-bottom: 12px;
}
.dash-header::before {
  content: ""; position: absolute; left: 0; right: 0; top: 50%;
  height: 1px; transform: translateY(-50%);
  background: linear-gradient(90deg, transparent, rgba(0, 229, 255, .85), rgba(61, 126, 255, .85), transparent);
}
.dash-header .halo {
  position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%);
  width: 620px; max-width: 92%; height: 58px; background: radial-gradient(ellipse, rgba(0, 160, 255, .28), transparent 70%);
  filter: blur(6px); pointer-events: none;
}
.dash-title {
  position: relative; z-index: 2; padding: 6px 44px;
  background: linear-gradient(180deg, rgba(4, 16, 44, .9), rgba(4, 12, 34, .9));
  border: 1px solid rgba(0, 229, 255, .35);
  border-radius: 30px; box-shadow: 0 0 22px rgba(0, 160, 255, .25), inset 0 0 16px rgba(0, 120, 255, .15);
  text-align: center; letter-spacing: .18em; font-weight: 700;
  font-size: 20px; color: #eafcff;
  text-shadow: 0 0 14px rgba(0, 229, 255, .8);
}
.dash-title small { display: block; font-size: 9px; letter-spacing: .34em; color: #6ea8dd; font-weight: 400; text-shadow: none; }
.dash-clock {
  position: absolute; right: 4px; top: 50%; transform: translateY(-50%);
  text-align: right; z-index: 2;
}
.dash-clock .t { font-size: 15px; font-weight: 700; color: #dff6ff; text-shadow: 0 0 10px rgba(0, 229, 255, .6); font-variant-numeric: tabular-nums; }
.dash-clock .d { font-size: 10px; color: #6ea8dd; letter-spacing: .08em; }

/* ---- KPI 行 ---- */
.kpi-row { display: flex; gap: 12px; margin-bottom: 12px; flex-wrap: wrap; }
.kpi-card {
  position: relative; flex: 1 1 0; min-width: 0; padding: 12px 14px 11px;
  background: linear-gradient(165deg, rgba(9, 32, 74, .82), rgba(3, 12, 34, .92));
  border: 1px solid rgba(0, 200, 255, .30); border-radius: 10px; overflow: hidden;
}
.kpi-card::before { content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 2px;
  background: linear-gradient(90deg, transparent, var(--kc), transparent); filter: drop-shadow(0 0 6px var(--kc)); }
.kpi-card .k-ico { position: absolute; right: 8px; top: 6px; font-size: 22px; opacity: .85; filter: drop-shadow(0 0 6px var(--kc)); }
.kpi-card .k-label { font-size: 11px; color: #83aed4; letter-spacing: .05em; }
.kpi-card .k-value { font-size: 23px; font-weight: 700; color: #eafcff; line-height: 1.25;
  text-shadow: 0 0 12px rgba(0, 229, 255, .45); font-variant-numeric: tabular-nums;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.kpi-card .k-value em { font-style: normal; font-size: 12px; color: #5eead4; font-weight: 600; margin-left: 3px; }

/* ---- 面板 ---- */
.grid-main { display: grid; grid-template-columns: repeat(12, 1fr); grid-auto-rows: 54px; gap: 10px; }
.panel {
  position: relative; min-width: 0; min-height: 0;
  background: linear-gradient(165deg, rgba(8, 26, 62, .78), rgba(3, 11, 30, .9));
  border: 1px solid rgba(0, 180, 255, .26); border-radius: 10px; overflow: hidden;
  box-shadow: 0 0 18px rgba(0, 100, 220, .12), inset 0 0 30px rgba(0, 70, 180, .05);
}
.panel::before, .panel::after { content: ""; position: absolute; width: 18px; height: 18px; z-index: 3; pointer-events: none; border-color: #00e5ff; border-style: solid; }
.panel::before { top: 3px; left: 3px; border-width: 2px 0 0 2px; filter: drop-shadow(0 0 4px #00e5ff); }
.panel::after { bottom: 3px; right: 3px; border-width: 0 2px 2px 0; filter: drop-shadow(0 0 4px #00e5ff); }
.panel-title {
  display: flex; align-items: center; flex-wrap: wrap; gap: 8px; padding: 8px 14px 6px;
  font-size: 14px; font-weight: 600; color: #bdf3ff; letter-spacing: .08em;
  border-bottom: 1px solid rgba(0, 180, 255, .15);
  background: linear-gradient(90deg, rgba(0, 140, 255, .12), transparent 70%);
}
.panel-title::before { content: ""; width: 4px; height: 14px; border-radius: 2px;
  background: linear-gradient(180deg, #00e5ff, #3d7eff); box-shadow: 0 0 8px #00e5ff; }
.panel-title .pt-tag { margin-left: auto; font-size: 9px; letter-spacing: .22em; color: #4f8cc0; font-weight: 400; }
.panel-title select {
  margin-left: auto; background: rgba(3, 12, 34, .9); color: #bdf3ff; border: 1px solid rgba(0, 200, 255, .4);
  border-radius: 4px; font-size: 11px; padding: 2px 6px; outline: none; cursor: pointer;
  max-width: 100%; min-width: 0;
}
.panel-title select:focus { border-color: #00e5ff; box-shadow: 0 0 8px rgba(0, 229, 255, .4); }
.chart { position: absolute; left: 0; right: 0; top: 34px; bottom: 0; }

/* 布局占位：左列 3 块 + 中间地图 + 右列 4 块 */
.p-trend   { grid-column: 1 / 5; grid-row: 1 / 5; }
.p-cat     { grid-column: 1 / 5; grid-row: 5 / 9; }
.p-delivery{ grid-column: 1 / 5; grid-row: 9 / 13; }
.p-map     { grid-column: 5 / 9; grid-row: 1 / 13; }
.p-pay     { grid-column: 9 / 13; grid-row: 1 / 4; }
.p-rfm     { grid-column: 9 / 13; grid-row: 4 / 7; }
.p-score   { grid-column: 9 / 13; grid-row: 7 / 10; }
.p-status  { grid-column: 9 / 13; grid-row: 10 / 13; }

.dash-footer { text-align: center; margin-top: 10px; font-size: 10px; color: #42688f; letter-spacing: .3em; }
@media (max-width: 1100px) {
  .kpi-row { gap: 8px; }
  .kpi-card { flex: 1 1 30%; min-width: 108px; }
  .grid-main { grid-template-columns: repeat(6, 1fr); }
  .p-trend   { grid-column: 1 / 4; grid-row: 1 / 5; }
  .p-cat     { grid-column: 4 / 7; grid-row: 1 / 5; }
  .p-pay     { grid-column: 1 / 4; grid-row: 5 / 8; }
  .p-rfm     { grid-column: 4 / 7; grid-row: 5 / 8; }
  .p-map     { grid-column: 1 / 7; grid-row: 8 / 20; }
  .p-score   { grid-column: 1 / 4; grid-row: 20 / 23; }
  .p-status  { grid-column: 4 / 7; grid-row: 20 / 23; }
  .p-delivery{ grid-column: 1 / 7; grid-row: 23 / 27; }
}
@media (max-width: 560px) {
  .kpi-card { flex: 1 1 44%; min-width: 96px; }
  .kpi-card .k-value { font-size: 18px; }
  .panel-title { padding: 7px 10px 5px; font-size: 13px; }
}
</style>
</head>
<body>
<div class="scanline"></div>
<div class="dash">
  <header class="dash-header">
    <div class="halo"></div>
    <div class="dash-title">
      Olist 电商数据大屏
      <small>OMMA · BRAZILIAN E-COMMERCE MULTI-MODAL ANALYTICS</small>
    </div>
    <div class="dash-clock">
      <div class="t" id="hdClock">--:--:--</div>
      <div class="d" id="hdDate">----/--/--</div>
    </div>
  </header>

  <div class="kpi-row" id="kpiRow"></div>

  <div class="grid-main">
    <div class="panel p-trend">
      <div class="panel-title">月度销售趋势<span class="pt-tag">ORDER × SALES</span></div>
      <div class="chart" id="chTrend"></div>
    </div>
    <div class="panel p-cat">
      <div class="panel-title">热销品类 Top 10<span class="pt-tag">CATEGORY</span></div>
      <div class="chart" id="chCat"></div>
    </div>
    <div class="panel p-map">
      <div class="panel-title">巴西州级指标分布
        <select id="mapMetric">
          <option value="sales">销售额 (R$)</option>
          <option value="orders">订单数</option>
          <option value="customers">客户数</option>
          <option value="score">平均评分</option>
          <option value="delivery">平均配送天数</option>
        </select>
        <span class="pt-tag">BRAZIL GEO</span>
      </div>
      <div class="chart" id="chMap"></div>
    </div>
    <div class="panel p-pay">
      <div class="panel-title">支付方式结构<span class="pt-tag">PAYMENT</span></div>
      <div class="chart" id="chPay"></div>
    </div>
    <div class="panel p-rfm">
      <div class="panel-title">客户价值分群<span class="pt-tag">RFM</span></div>
      <div class="chart" id="chRfm"></div>
    </div>
    <div class="panel p-delivery">
      <div class="panel-title">配送时效与评分<span class="pt-tag">LOGISTICS</span></div>
      <div class="chart" id="chDelivery"></div>
    </div>
    <div class="panel p-score">
      <div class="panel-title">评分分布<span class="pt-tag">REVIEW</span></div>
      <div class="chart" id="chScore"></div>
    </div>
    <div class="panel p-status">
      <div class="panel-title">订单状态分布<span class="pt-tag">STATUS</span></div>
      <div class="chart" id="chStatus"></div>
    </div>
  </div>

  <footer class="dash-footer">DATA SOURCE: KAGGLE · OLIST BRAZILIAN E-COMMERCE &nbsp;|&nbsp; FOR LEARNING & RESEARCH ONLY</footer>
</div>

<script>
(function(){
"use strict";
var PAYLOAD = __PAYLOAD_JSON__;
var BR_GEO = __GEOJSON_JSON__;

var ACCENT = ['#00e5ff', '#3d7eff', '#00ffa3', '#ffb020', '#ff4d8f', '#8b5cf6', '#ff7a3d', '#5eead4'];
var TXT = { color: '#a9c9e8', fontFamily: '"Segoe UI","Microsoft YaHei",sans-serif', fontSize: 11 };
var charts = [];

function mkChart(id) {
  var el = document.getElementById(id);
  if (!el) return null;
  var c = echarts.init(el);
  charts.push(c);
  return c;
}
function fmtNum(v) {
  return Number(v).toLocaleString('en-US');
}
function fmtMoney(v) {
  return 'R$ ' + Number(v).toLocaleString('en-US', { maximumFractionDigits: 0 });
}
function tip(extra) {
  return Object.assign({
    backgroundColor: 'rgba(5, 18, 44, .94)',
    borderColor: 'rgba(0, 229, 255, .45)',
    borderWidth: 1,
    textStyle: { color: '#dff3ff', fontSize: 12 },
    extraCssText: 'box-shadow: 0 0 14px rgba(0,140,255,.35); border-radius:6px;'
  }, extra || {});
}
function axisCommon() {
  return {
    axisLine: { lineStyle: { color: 'rgba(120, 180, 230, .32)' } },
    axisTick: { show: false },
    axisLabel: { color: '#7fa8cf', fontSize: 11 },
    splitLine: { lineStyle: { color: 'rgba(120, 180, 230, .12)' } }
  };
}
function legendCommon(data) {
  return { data: data, top: 4, right: 8, textStyle: TXT, itemWidth: 14, itemHeight: 8 };
}

/* ============ KPI（数字滚动） ============ */
function fitText(el) {
  var size = parseFloat(window.getComputedStyle(el).fontSize);
  while (el.scrollWidth > el.clientWidth + 2 && size > 11) {
    size -= 1;
    el.style.fontSize = size + 'px';
  }
}
function renderKPI() {
  var row = document.getElementById('kpiRow');
  var html = '';
  PAYLOAD.kpi.forEach(function (k) {
    html += '<div class="kpi-card" style="--kc:' + k.color + '">' +
      '<span class="k-ico">' + k.icon + '</span>' +
      '<div class="k-label">' + k.label + '</div>' +
      '<div class="k-value" data-v="' + k.value + '" data-dec="' + (k.decimals || 0) + '">0<em>' + k.unit + '</em></div>' +
      '</div>';
  });
  row.innerHTML = html;
  var cards = row.querySelectorAll('.k-value');
  cards.forEach(function (el) {
    var target = parseFloat(el.getAttribute('data-v'));
    var dec = parseInt(el.getAttribute('data-dec'), 10);
    var unitEl = el.querySelector('em');
    var unitText = unitEl ? unitEl.textContent : '';
    var dur = 1200, start = null;
    var finished = false;
    function paint(p) {
      var v = target * (1 - Math.pow(1 - p, 3));
      var disp = dec > 0 ? v.toFixed(dec) : Math.round(v).toLocaleString('en-US');
      el.innerHTML = disp + '<em>' + unitText + '</em>';
    }
    function finish() { paint(1); fitText(el); finished = true; }
    function step() {
      if (finished) return;
      if (start === null) start = Date.now();
      var p = Math.min((Date.now() - start) / dur, 1);
      paint(p);
      if (p < 1) { setTimeout(step, 16); } else { finish(); }
    }
    step();
    // 页面不可见（rAF 停摆）时用 setTimeout 兜底，恢复可见时立即补全
    document.addEventListener('visibilitychange', function () {
      if (!document.hidden) finish();
    });
    setTimeout(finish, dur + 600);
  });
}

/* ============ 月度趋势 ============ */
function renderTrend() {
  var c = mkChart('chTrend');
  var m = PAYLOAD.monthly;
  var g = {
    tooltip: tip({ trigger: 'axis', axisPointer: { type: 'shadow' } }),
    legend: legendCommon(['订单数', '销售额']),
    grid: { left: 46, right: 62, top: 38, bottom: 26 },
    xAxis: Object.assign({ type: 'category', data: m.months }, axisCommon()),
    yAxis: [
      Object.assign({ type: 'value', name: '订单', nameTextStyle: { color: '#7fa8cf' } }, axisCommon()),
      Object.assign({ type: 'value', name: 'R$', nameTextStyle: { color: '#7fa8cf' }, splitLine: { show: false } }, axisCommon())
    ],
    series: [
      {
        name: '订单数', type: 'bar', data: m.orders, barWidth: '46%',
        itemStyle: {
          borderRadius: [3, 3, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#3d7eff' }, { offset: 1, color: 'rgba(61,126,255,.10)' }
          ])
        }
      },
      {
        name: '销售额', type: 'line', yAxisIndex: 1, data: m.sales, smooth: true,
        symbol: 'circle', symbolSize: 5,
        lineStyle: { color: '#00ffa3', width: 2.4, shadowColor: 'rgba(0,255,163,.55)', shadowBlur: 8 },
        itemStyle: { color: '#00ffa3', borderColor: '#032410', borderWidth: 1 },
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(0,255,163,.22)' }, { offset: 1, color: 'rgba(0,255,163,0)' }]) }
      }
    ]
  };
  c.setOption(g);
}

/* ============ 热销品类 ============ */
function renderCat() {
  var c = mkChart('chCat');
  var cats = PAYLOAD.categories.slice().reverse();
  c.setOption({
    tooltip: tip({ trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: function (p) {
      var d = p[0].data;
      return p[0].name + '<br/>销量：<b>' + fmtNum(d[1]) + '</b> 件<br/>销售额：<b>' + fmtMoney(d[2]) + '</b>';
    } }),
    grid: { left: 108, right: 40, top: 18, bottom: 22 },
    xAxis: Object.assign({ type: 'value', splitLine: { show: false } }, axisCommon()),
    yAxis: Object.assign({ type: 'category', data: cats.map(function (x) { return x.name; }), axisLine: { show: false } }, axisCommon()),
    series: [{
      type: 'bar', data: cats.map(function (x) { return { value: x.count, sales: x.sales }; }),
      barWidth: '56%',
      label: { show: true, position: 'right', color: '#8fd8ff', fontSize: 10, formatter: function (p) { return fmtNum(p.value); } },
      itemStyle: {
        borderRadius: [0, 3, 3, 0],
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: 'rgba(0,140,255,.25)' }, { offset: 1, color: '#00c8ff' }
        ]),
        shadowColor: 'rgba(0,200,255,.35)', shadowBlur: 8
      }
    }]
  });
}

/* ============ 巴西地图 ============ */
var MAP_META = {
  sales:    { label: '销售额 (R$)',  fmt: fmtMoney, color: ['#081a3d', '#0d3f8c', '#0f8fd6', '#00e5ff', '#7dffb0'] },
  orders:   { label: '订单数',      fmt: fmtNum,   color: ['#081a3d', '#1b3f8f', '#1f7fd6', '#35b6ff', '#c9f2ff'] },
  customers:{ label: '客户数',      fmt: fmtNum,   color: ['#081a3d', '#233a8f', '#2e6fd6', '#5f9dff', '#d8e8ff'] },
  score:    { label: '平均评分',    fmt: function (v) { return v.toFixed(2); }, color: ['#5a1f3a', '#b03060', '#e05f7f', '#ff9d5f', '#ffe28a'] },
  delivery: { label: '平均配送天数', fmt: function (v) { return v.toFixed(1); }, color: ['#081a3d', '#12406b', '#187d8f', '#2cc9c0', '#7dffd8'] }
};
function renderMap(metricKey) {
  var c = mkChart('chMap');
  var st = PAYLOAD.states;
  var meta = MAP_META[metricKey] || MAP_META.sales;
  var data = st.map(function (s) { return { name: s.sigla, value: s[metricKey], full: s.name }; });
  var vals = data.map(function (d) { return d.value; });
  var vmin = Math.min.apply(null, vals), vmax = Math.max.apply(null, vals);
  if (vmin === vmax) vmax = vmin + 1;
  var opt = {
    tooltip: tip({
      formatter: function (p) {
        if (!p.value) return '';
        return '<b>' + p.data.full + ' (' + p.name + ')</b><br/>' + meta.label + '：<b style="color:#00ffa3">' + meta.fmt(p.value) + '</b>';
      }
    }),
    visualMap: {
      min: vmin, max: vmax, calculable: true, left: 12, bottom: 10, orient: 'horizontal',
      itemWidth: 10, itemHeight: 90, textStyle: { color: '#7fa8cf', fontSize: 10 },
      inRange: { color: meta.color }
    },
    geo: {
      map: 'BR', roam: true, zoom: 1.12, scaleLimit: { min: 0.8, max: 5 },
      label: { show: true, fontSize: 8.5, color: '#bfe9ff', formatter: function (p) { return p.name; } },
      itemStyle: { areaColor: '#0b1e45', borderColor: '#2a7fff', borderWidth: 0.7, shadowColor: 'rgba(0,120,255,.35)', shadowBlur: 6 },
      emphasis: { label: { color: '#fff', fontSize: 10 }, itemStyle: { areaColor: '#0e4a9e' } },
      select: { itemStyle: { areaColor: '#155fc0' } },
      regions: [{ name: 'Brasil', silent: true, itemStyle: { areaColor: 'rgba(255,255,255,.02)' } }]
    },
    series: [{ type: 'map', map: 'BR', geoIndex: 0, data: data, zlevel: 2 }]
  };
  c.setOption(opt, true);
  c.on('georoam', function () { c.resize(); });
}
function bindMapSelect() {
  var sel = document.getElementById('mapMetric');
  sel.addEventListener('change', function () { renderMap(sel.value); });
}

/* ============ 支付方式 ============ */
function renderPay() {
  var c = mkChart('chPay');
  var pays = PAYLOAD.payments;
  var total = pays.reduce(function (s, x) { return s + x.amount; }, 0);
  c.setOption({
    tooltip: tip({ trigger: 'item', formatter: function (p) {
      return p.name + '<br/>金额：<b>' + fmtMoney(p.value) + '</b>（' + p.percent + '%）<br/>订单数：' + fmtNum(p.orders);
    } }),
    legend: { orient: 'vertical', right: 6, top: 'middle', textStyle: TXT, icon: 'circle', itemWidth: 9, itemHeight: 9 },
    series: [{
      type: 'pie', radius: ['46%', '70%'], center: ['34%', '52%'],
      itemStyle: { borderColor: '#04102c', borderWidth: 2, shadowBlur: 8, shadowColor: 'rgba(0,0,0,.4)' },
      label: { show: true, color: '#cfe8ff', fontSize: 10, formatter: '{b}\n{d}%' },
      labelLine: { length: 8, length2: 8, lineStyle: { color: 'rgba(160,200,240,.35)' } },
      data: pays.map(function (x, i) { return { name: x.name, value: x.amount, orders: x.orders, itemStyle: { color: ACCENT[i % ACCENT.length] } }; })
    }],
    graphic: [{
      type: 'text', left: '34%', top: '50%', style: {
        text: '总金额\n' + fmtMoney(total),
        textAlign: 'center', fill: '#eafcff', fontSize: 12, lineHeight: 18,
        fontFamily: '"Segoe UI","Microsoft YaHei",sans-serif',
        shadowColor: 'rgba(0,229,255,.6)', shadowBlur: 10
      }
    }]
  });
}

/* ============ RFM 分群 ============ */
function renderRfm() {
  var c = mkChart('chRfm');
  var segs = PAYLOAD.rfm;
  c.setOption({
    tooltip: tip({ trigger: 'item', formatter: function (p) {
      return p.name + '<br/>客户数：<b>' + fmtNum(p.value) + '</b>（' + p.percent + '%）<br/>人均金额：<b>' + fmtMoney(p.data.money) + '</b>';
    } }),
    legend: { orient: 'vertical', right: 4, top: 'middle', textStyle: Object.assign({}, TXT, { fontSize: 10 }), icon: 'circle', itemWidth: 8, itemHeight: 8 },
    series: [{
      type: 'pie', radius: ['40%', '66%'], center: ['34%', '52%'],
      itemStyle: { borderColor: '#04102c', borderWidth: 2 },
      label: { show: false }, emphasis: { label: { show: true, color: '#fff', fontSize: 11, formatter: '{b} {d}%' } },
      data: segs.map(function (x, i) {
        return { name: x.name, value: x.count, money: x.money, itemStyle: { color: ACCENT[i % ACCENT.length] } };
      })
    }],
    graphic: [{
      type: 'text', left: '34%', top: '50%', style: {
        text: '客户总数\n' + fmtNum(PAYLOAD.kpi[1].value),
        textAlign: 'center', fill: '#eafcff', fontSize: 12, lineHeight: 18,
        fontFamily: '"Segoe UI","Microsoft YaHei",sans-serif',
        shadowColor: 'rgba(0,229,255,.6)', shadowBlur: 10
      }
    }]
  });
}

/* ============ 订单状态 ============ */
function renderStatus() {
  var c = mkChart('chStatus');
  var st = PAYLOAD.status;
  var total = st.reduce(function (s, x) { return s + x.count; }, 0);
  c.setOption({
    tooltip: tip({ trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: function (p) {
      var d = p[0].data;
      return p[0].name + '<br/>' + fmtNum(d[1]) + ' 单（' + (d[1] / total * 100).toFixed(2) + '%）';
    } }),
    grid: { left: 74, right: 30, top: 12, bottom: 22 },
    xAxis: Object.assign({ type: 'value', splitLine: { show: false } }, axisCommon()),
    yAxis: Object.assign({ type: 'category', data: st.map(function (x) { return x.name; }), axisLine: { show: false } }, axisCommon()),
    series: [{
      type: 'bar', data: st.map(function (x, i) { return { value: [0, x.count] }; }),
      barWidth: '52%',
      label: { show: true, position: 'right', color: '#8fd8ff', fontSize: 10, formatter: function (p) { return fmtNum(p.value[1]); } },
      itemStyle: {
        borderRadius: [0, 3, 3, 0],
        color: function (p) {
          var name = st[p.dataIndex].name;
          return new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: name === 'delivered' ? 'rgba(0,255,163,.30)' : 'rgba(0,140,255,.22)' },
            { offset: 1, color: name === 'delivered' ? '#00ffa3' : '#00c8ff' }
          ]);
        },
        shadowColor: 'rgba(0,200,255,.3)', shadowBlur: 6
      }
    }]
  });
}

/* ============ 评分分布 ============ */
function renderScore() {
  var c = mkChart('chScore');
  var sc = PAYLOAD.score;
  var maxV = Math.max.apply(null, sc.map(function (x) { return x.count; }));
  c.setOption({
    tooltip: tip({ trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: function (p) {
      return p[0].name + ' 分<br/>' + fmtNum(p[0].value) + ' 条（' + (p[0].value / PAYLOAD.kpi[0].value * 100).toFixed(2) + '% 订单）';
    } }),
    grid: { left: 44, right: 20, top: 24, bottom: 26 },
    xAxis: Object.assign({ type: 'category', data: sc.map(function (x) { return x.name + ' 分'; }) }, axisCommon()),
    yAxis: Object.assign({ type: 'value', splitLine: { show: false } }, axisCommon()),
    series: [{
      type: 'bar', data: sc.map(function (x) { return x.count; }), barWidth: '46%',
      label: { show: true, position: 'top', color: '#9fdcff', fontSize: 10, formatter: function (p) { return fmtNum(p.value); } },
      itemStyle: {
        borderRadius: [3, 3, 0, 0],
        color: function (p) {
          var v = p.value / maxV;
          return new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: v > 0.85 ? '#00ffa3' : (v > 0.5 ? '#00e5ff' : '#3d7eff') },
            { offset: 1, color: 'rgba(20,60,150,.15)' }
          ]);
        },
        shadowColor: 'rgba(0,200,255,.4)', shadowBlur: 8
      },
      markLine: {
        symbol: 'none', silent: true,
        lineStyle: { color: '#ffb020', type: 'dashed', width: 1.2 },
        label: { color: '#ffd27f', fontSize: 10, formatter: '平均 ' + PAYLOAD.kpi[4].value.toFixed(2) },
        data: [{ yAxis: PAYLOAD.kpi[4].value }]
      }
    }]
  });
}

/* ============ 配送时效 ============ */
function renderDelivery() {
  var c = mkChart('chDelivery');
  var dl = PAYLOAD.delivery;
  c.setOption({
    tooltip: tip({ trigger: 'axis', axisPointer: { type: 'shadow' } }),
    legend: legendCommon(['订单占比', '平均评分']),
    grid: { left: 44, right: 40, top: 36, bottom: 26 },
    xAxis: Object.assign({ type: 'category', data: dl.map(function (x) { return x.range; }) }, axisCommon()),
    yAxis: [
      Object.assign({ type: 'value', name: '%', max: 60, nameTextStyle: { color: '#7fa8cf' } }, axisCommon()),
      Object.assign({ type: 'value', name: '评分', min: 0, max: 5, splitLine: { show: false } }, axisCommon())
    ],
    series: [
      {
        name: '订单占比', type: 'bar', data: dl.map(function (x) { return x.ratio; }), barWidth: '44%',
        itemStyle: {
          borderRadius: [3, 3, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#8b5cf6' }, { offset: 1, color: 'rgba(139,92,246,.12)' }
          ]),
          shadowColor: 'rgba(139,92,246,.4)', shadowBlur: 6
        }
      },
      {
        name: '平均评分', type: 'line', yAxisIndex: 1, data: dl.map(function (x) { return x.score; }),
        smooth: true, symbol: 'circle', symbolSize: 5,
        lineStyle: { color: '#ffb020', width: 2.2, shadowColor: 'rgba(255,176,32,.5)', shadowBlur: 7 },
        itemStyle: { color: '#ffb020' }
      }
    ]
  });
}

/* ============ 时钟 ============ */
function tickClock() {
  var now = new Date();
  var pad = function (n) { return n < 10 ? '0' + n : '' + n; };
  document.getElementById('hdClock').textContent =
    pad(now.getHours()) + ':' + pad(now.getMinutes()) + ':' + pad(now.getSeconds());
  document.getElementById('hdDate').textContent =
    now.getFullYear() + '/' + pad(now.getMonth() + 1) + '/' + pad(now.getDate()) +
    ' ' + ['日', '一', '二', '三', '四', '五', '六'][now.getDay()];
}

/* ============ 启动 ============ */
function boot() {
  if (!window.echarts) { setTimeout(boot, 400); return; }
  echarts.registerMap('BR', BR_GEO);
  renderKPI();
  renderTrend();
  renderCat();
  renderMap('sales');
  bindMapSelect();
  renderPay();
  renderRfm();
  renderStatus();
  renderScore();
  renderDelivery();
  tickClock();
  setInterval(tickClock, 1000);
  window.addEventListener('resize', function () { charts.forEach(function (c) { c.resize(); }); });
}
boot();
})();
</script>
</body>
</html>
"""
