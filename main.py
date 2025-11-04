# app.py
import json
import base64
from pathlib import Path
import numpy as np
import streamlit as st
import streamlit.components.v1 as components

# full width with Streamlit chrome hidden
st.set_page_config(page_title="Bank of Sam — SAMBUCKS", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
/* app + page background forced dark so any gaps aren’t white */
:root { --bankofsam-bg: #06140b; }
html, body, .stApp { background: var(--bankofsam-bg) !important; }

/* nuke sidebar entirely */
[data-testid="stSidebar"] { display: none !important; }

/* fully remove the top header (visibility:hidden leaves height!) */
[data-testid="stHeader"] { display: none !important; }
header { display: none !important; }            /* older Streamlit */
footer { display: none !important; }            /* optional: hide footer */

/* remove the default top padding/margins */
[data-testid="stAppViewContainer"] > .main { padding-top: 0 !important; }
.block-container { padding: 0 !important; margin: 0 !important; max-width: 100% !important; }

/* kill any first-child spacing in the main stack */
section.main > div:first-child { margin-top: 0 !important; padding-top: 0 !important; }

/* make the component iframe not add any stray spacing */
iframe[title="st.iframe"] { display: block; margin: 0; background: transparent; }
</style>
""", unsafe_allow_html=True)


# controls bar for file inputs (kept tiny)
# with st.container():
#     c1, c2 = st.columns([1, 3])
#     with c1:
#         json_file = st.file_uploader("News JSON", type=["json"])
#     with c2:
#         logo_file = st.file_uploader("sam.png", type=["png"])
json_file = None
logo_file = None
# load sam.png as base64
def load_sam_data_url():
    if logo_file is not None:
        b = logo_file.read()
        return "data:image/png;base64," + base64.b64encode(b).decode("ascii")
    # fallback to file in repo
    p = Path(__file__).parent / "sam.png"
    if p.exists():
        return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode("ascii")
    # final fallback tiny transparent pixel
    return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8Xw8AAmMB4hQq9XcAAAAASUVORK5CYII="

sam_data_url = load_sam_data_url()

# load stories and names from JSON
def load_feed():
    # default demo content if no file provided
    default = {
        "stories": [
            {"title":"SAM Index edges higher", "body":"Traders cite strong latte demand"},
            {"title":"Robo hedger toggles on", "body":"Latency improved to probably fine"},
            {"title":"Balance sheet very green", "body":"Analysts upgrade outlook to moonish"}
        ],
        "names": ["Sam A", "Jamie Q", "Taylor R", "Jordan K", "Avery P", "Riley M"]
    }
    if json_file is None:
        return default
    try:
        raw = json.load(json_file)
        # accept either list or dict for stories
        stories = raw.get("stories", [])
        if isinstance(stories, dict):
            stories = list(stories.values())
        if not isinstance(stories, list):
            stories = default["stories"]
        names = raw.get("names", default["names"])
        if not isinstance(names, list) or not names:
            names = default["names"]
        # sanitize elements minimally
        clean_stories = []
        for s in stories:
            if isinstance(s, dict):
                t = str(s.get("title", "")).strip()
                b = str(s.get("body", "")).strip()
                if t or b:
                    clean_stories.append({"title": t or "Untitled", "body": b or ""})
        if not clean_stories:
            clean_stories = default["stories"]
        return {"stories": clean_stories, "names": names}
    except Exception:
        return default

feed = load_feed()

# seed tickers and starting prices for client simulation
rng = np.random.default_rng(7)
tickers = [f"SAM{i:02d}" for i in range(1, 11)]
start_prices = np.round(rng.uniform(4, 250, len(tickers)), 2).tolist()
vols = np.round(rng.uniform(0.2, 2.0, len(tickers)), 2).tolist()

payload = {
    "theme": "green",
    "logo": sam_data_url,
    "tickers": tickers,
    "prices": start_prices,
    "vols": vols,
    "stories": feed["stories"],
    "names": feed["names"]
}

# big HTML block
HTML = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<meta http-equiv="X-UA-Compatible" content="IE=edge" />
<title>Bank of Sam — SAMBUCKS</title>
<style>
:root {{
  /* green network vibe */
  --g1: #0b2f1a;
  --g2: #0e5a2f;
  --g3: #16a34a;
  --panel: rgba(255,255,255,0.06);
  --panel2: rgba(0,0,0,0.3);
  --border: rgba(255,255,255,0.12);
  --text: #eaf6ec;
  --muted: #b6d6bf;
  --up: #19e57a;
  --down: #ff5b4d;
  --accent: #b4ff6b;
}}
* {{ box-sizing: border-box; }}
html, body {{ margin:0; padding:0; background:#06140b; color:var(--text); font-family: Verdana, Arial, Helvetica, sans-serif; }}
.wrap {{ width: 1120px; margin: 0 auto; }}

.topbar {{
  background: linear-gradient(180deg, var(--g3), var(--g2) 60%, var(--g1));
  border-bottom: 3px solid #000;
  position: sticky; top: 0; z-index: 999;
  box-shadow: 0 4px 18px rgba(0,0,0,0.5);
}}
.brand {{
  display:flex; align-items:center; gap:14px; padding:10px 12px;
}}
.brand img {{ height:44px; border:2px solid rgba(255,255,255,0.2); box-shadow:0 2px 6px rgba(0,0,0,0.6); }}
.brand .title {{ font-weight:700; font-size:22px; letter-spacing:.5px; text-shadow:0 1px 0 #000; }}

.navbar {{
  background: linear-gradient(180deg, rgba(0,0,0,0.35), rgba(255,255,255,0.05));
  border-top:1px solid rgba(255,255,255,0.1); border-bottom:1px solid rgba(0,0,0,0.8);
  display:flex; gap:18px; padding:6px 10px; font-size:13px;
}}
.navbtn {{
  padding:5px 10px;
  border:1px solid rgba(255,255,255,0.25);
  background: linear-gradient(180deg, rgba(255,255,255,0.12), rgba(0,0,0,0.25));
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.25), 0 2px 0 rgba(0,0,0,0.5);
  text-transform: uppercase; letter-spacing:.6px; cursor:pointer;
}}
.navbtn.sam::after {{
  content: "";
  display:inline-block;
  width:16px; height:16px; margin-left:6px; vertical-align:middle;
  background: url('{payload["logo"]}') center/contain no-repeat;
  filter: drop-shadow(0 0 2px rgba(0,0,0,0.6));
}}

.banner {{
  display:grid; grid-template-columns: 1fr 280px; gap:14px; padding:10px 0 6px;
}}
.breaking {{
  background: linear-gradient(180deg, #0f3a21, #0b2a19);
  border:2px solid #000; box-shadow:0 4px 16px rgba(0,0,0,0.6); position:relative; overflow:hidden;
}}
.breaking .hdr {{
  background:#000; color:#fff; font-weight:700; padding:4px 8px; font-size:12px; letter-spacing:.8px;
}}
.breaking .hdr img {{ height:14px; vertical-align:middle; margin-left:6px; filter: invert(1); }}
.breaking .marquee {{ padding:6px 10px; white-space:nowrap; overflow:hidden; font-weight:600; }}

.ticker {{
  background:#000; border-top:2px solid #1a1a1a; border-bottom:2px solid #1a1a1a;
  overflow:hidden; white-space:nowrap; font-size:13px;
}}
.ticker-inner {{ display:inline-block; padding-left:100%; animation: ticker 18s linear infinite; }}
@keyframes ticker {{ 0% {{transform:translateX(0%);}} 100% {{transform:translateX(-100%);}} }}
.badge {{
  display:inline-block; padding:3px 8px; margin:0 16px 0 0;
  background: linear-gradient(180deg, #1b1b1b, #2b2b2b);
  border:1px solid #444; color:#fff; box-shadow: inset 0 1px 0 rgba(255,255,255,0.15);
}}
.badge.sam {{
  position: relative; padding-left: 26px;
}}
.badge.sam::before {{
  content:""; position:absolute; left:6px; top:2px; width:18px; height:18px;
  background: url('{payload["logo"]}') center/contain no-repeat;
}}

.grid {{
  display:grid; grid-template-columns: 260px 1fr 320px; gap:14px; margin-top:12px;
}}
.panel {{
  background: linear-gradient(180deg, var(--panel), var(--panel2));
  border:1px solid var(--border); box-shadow:0 6px 24px rgba(0,0,0,0.4);
}}
.panel .hdr {{
  padding:6px 10px; background: linear-gradient(180deg, rgba(255,255,255,0.15), rgba(0,0,0,0.35));
  border-bottom:1px solid rgba(0,0,0,0.6); font-weight:700; text-shadow:0 1px 0 rgba(0,0,0,0.8);
}}
.hdr .samdot {{
  display:inline-block; width:14px; height:14px; margin-left:6px; vertical-align:middle;
  background: url('{payload["logo"]}') center/contain no-repeat;
  filter: drop-shadow(0 0 2px rgba(0,0,0,0.6));
}}

.table {{ width:100%; border-collapse:collapse; font-size:12px; }}
.table th, .table td {{ border-bottom:1px solid rgba(255,255,255,0.08); padding:6px 8px; }}
.table th {{ background: rgba(0,0,0,0.35); text-align:left; font-weight:700; }}

.green {{ color: var(--up); }}
.red {{ color: var(--down); }}

.footer {{ margin:14px 0 28px; font-size:11px; color:var(--muted); text-align:center; }}

.watermark {{
  position: fixed; bottom: 18px; right: 18px; width: 200px; opacity: 0.08; z-index: 1; pointer-events: none;
  background: url('{payload["logo"]}') center/contain no-repeat;
}}
.pulse-logo {{
  position:absolute; right:10px; top:6px; width:18px; height:18px;
  background: url('{payload["logo"]}') center/contain no-repeat;
  filter: drop-shadow(0 0 4px rgba(180,255,107,0.6));
  animation: pl 2.2s ease-in-out infinite;
}}
@keyframes pl {{
  0% {{ transform: scale(1) rotate(0deg); }}
  50% {{ transform: scale(1.15) rotate(4deg); }}
  100% {{ transform: scale(1) rotate(0deg); }}
}}
</style>
</head>
<body>
  <div class="topbar">
    <div class="wrap">
      <div class="brand">
        <img src="{payload['logo']}" onerror="this.style.display='none'"/>
        <div class="title">Bank of Sam — SAMBUCKS</div>
      </div>
      <div class="navbar">
        <div class="navbtn sam">Home</div>
        <div class="navbtn">Markets</div>
        <div class="navbtn">Tech Ticker</div>
        <div class="navbtn">Your Accounts</div>
        <div class="navbtn">Research</div>
        <!-- removed Prime Pranks -->
      </div>
    </div>
  </div>

  <div class="wrap">
    <div class="banner">
      <div class="breaking">
        <div class="hdr">Breaking <img src="{payload['logo']}" alt=""></div>
        <div class="marquee" id="breaking">Loading headlines</div>
        <div class="pulse-logo"></div>
      </div>
      <div class="panel">
        <div class="hdr">Top Story <span class="samdot"></span></div>
        <div id="lead" style="padding:10px; font-size:13px;"></div>
      </div>
    </div>

    <div class="ticker">
      <div class="ticker-inner" id="ticker-strip"></div>
    </div>

    <div class="grid">
      <div class="panel">
        <div class="hdr">Watchlist <span class="samdot"></span></div>
        <div style="padding:8px;">
          <table class="table" id="watch">
            <thead>
              <tr><th>Ticker</th><th>Price</th><th>Chg</th><th>Vol</th></tr>
            </thead>
            <tbody></tbody>
          </table>
        </div>

        <div class="hdr">News <span class="samdot"></span></div>
        <div id="news" style="padding:8px; font-size:12px;"></div>
      </div>

      <div class="panel">
        <div class="hdr">Chart <span class="samdot"></span></div>
        <div style="padding:8px;">
          <canvas id="chart" width="680" height="280" style="width:100%; background:#07150b; border:1px solid rgba(255,255,255,0.08)"></canvas>
        </div>

        <div class="hdr">Order Flow <span class="samdot"></span></div>
        <div style="padding:8px; max-height:260px; overflow:auto;">
          <table class="table" id="blotter">
            <thead><tr><th>Time</th><th>Trader</th><th>Side</th><th>Symbol</th><th>Qty</th><th>Price</th></tr></thead>
            <tbody></tbody>
          </table>
        </div>
      </div>

      <div class="panel">
        <div class="hdr">Right Rail <span class="samdot"></span></div>
        <div style="padding:10px;">
          <div style="margin-bottom:10px; font-weight:700;">
            <img src="{payload['logo']}" width="14" style="vertical-align:middle; margin-right:4px;"> Research Headline
          </div>
          <div style="font-size:12px; color:var(--muted);">SAMBUCKS outlook remains very green</div>
          <hr style="border-color: rgba(255,255,255,0.08)" />
          <div style="margin-bottom:10px; font-weight:700;">
            <img src="{payload['logo']}" width="14" style="vertical-align:middle; margin-right:4px;"> Weather Bug
          </div>
          <div style="font-size:12px;">NYC Mostly numbers Feels like alpha</div>
          <hr style="border-color: rgba(255,255,255,0.08)" />
          <div style="font-weight:700;">
            <img src="{payload['logo']}" width="14" style="vertical-align:middle; margin-right:4px;"> Sponsored
          </div>
          <div style="font-size:12px; color:var(--muted);">Open a new SAMBUCKS account and receive a commemorative mouse pad</div>
        </div>
      </div>
    </div>

    <div class="footer">This is a prank site No real quotes No real advice</div>
  </div>

  <div class="watermark"></div>

<script>
// payload from Python
const SEED = {json.dumps(payload)};

// helpers
function fmt(n) {{ return Number(n).toFixed(2); }}
function nowTime() {{
  const d = new Date();
  return d.toTimeString().slice(0,8);
}}

const TICKERS = SEED.tickers.slice();
let prices = SEED.prices.slice();
const vols = SEED.vols.slice();

// build watchlist and ticker strip
function buildWatch() {{
  const tb = document.querySelector("#watch tbody");
  tb.innerHTML = "";
  for (let i=0;i<TICKERS.length;i++) {{
    const p = prices[i];
    const ch = (Math.random()*2 - 1) * 2.0;
    const cls = ch>=0 ? "green":"red";
    const v = Math.floor(1000 + Math.random()*900000);
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${{TICKERS[i]}}</td><td>${{fmt(p)}}</td><td class="${{cls}}">${{ch.toFixed(2)}}%</td><td>${{v.toLocaleString()}}</td>`;
    tb.appendChild(tr);
  }}
}}
function buildTickerStrip() {{
  const el = document.getElementById("ticker-strip");
  el.innerHTML = "";
  for (let i=0;i<TICKERS.length;i++) {{
    const dir = Math.random()>.5 ? "▲" : "▼";
    const cls = dir==="▲" ? "green":"red";
    const node = document.createElement("span");
    node.className = "badge sam";
    node.innerHTML = `<b>${{TICKERS[i]}}</b> <span class="${{cls}}">${{dir}} ${{fmt(prices[i])}}</span>`;
    el.appendChild(node);
  }}
}}

// news from JSON
const STORIES = Array.isArray(SEED.stories) ? SEED.stories : [];
function loadNews() {{
  const lead = document.getElementById("lead");
  const news = document.getElementById("news");
  if (STORIES.length) {{
    lead.innerHTML = `<div style="font-size:14px; font-weight:700; margin-bottom:6px;">${{STORIES[0].title}}</div><div>${{STORIES[0].body}}</div>`;
  }}
  news.innerHTML = "";
  STORIES.slice(1).forEach(s => {{
    const item = document.createElement("div");
    item.style.marginBottom = "10px";
    item.innerHTML = `<div style="font-weight:700;"><img src="${{SEED.logo}}" width="12" style="vertical-align:middle; margin-right:4px;">${{s.title}}</div><div style="color:var(--muted);">${{s.body}}</div>`;
    news.appendChild(item);
  }});
}}

// breaking banner rotates through stories
let headlineIdx = 0;
function spinBreaking() {{
  const el = document.getElementById("breaking");
  if (!STORIES.length) return;
  const s = STORIES[headlineIdx % STORIES.length];
  el.textContent = s.title + " — " + s.body;
  headlineIdx++;
}}

// canvas chart
const canvas = document.getElementById("chart");
const ctx = canvas.getContext("2d");
const W = canvas.width, H = canvas.height;
let series = Array.from({{length: 180}}, (_,i)=> prices[0] + Math.sin(i/8)*2 );

function drawChart() {{
  ctx.clearRect(0,0,W,H);
  // grid
  ctx.strokeStyle = "rgba(255,255,255,0.08)";
  ctx.lineWidth = 1;
  for (let x=0; x<W; x+=64) {{ ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,H); ctx.stroke(); }}
  for (let y=0; y<H; y+=56) {{ ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W,y); ctx.stroke(); }}
  // line
  const min = Math.min(...series), max = Math.max(...series);
  const scale = (H-40) / (max-min || 1);
  ctx.beginPath(); ctx.lineWidth = 2; ctx.strokeStyle = "#19e57a";
  series.forEach((val, i) => {{
    const x = i * (W/(series.length-1));
    const y = H-30 - (val - min) * scale;
    if (i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
  }});
  ctx.stroke();
  // last price flag
  const last = series[series.length-1];
  const y = H-30 - (last - min) * scale;
  ctx.fillStyle = "rgba(0,0,0,0.7)";
  ctx.fillRect(W-90, y-10, 84, 20);
  ctx.fillStyle = "#eaf6ec";
  ctx.font = "12px Verdana, sans-serif";
  ctx.fillText("$"+last.toFixed(2), W-82, y+5);
}}

// animate prices
function tickPrices() {{
  for (let i=0;i<prices.length;i++) {{
    const drift = (Math.random()-0.5) * vols[i] * 0.05;
    prices[i] = Math.max(0.01, prices[i] * (1 + drift/100));
  }}
}}
function step() {{
  const v = (Math.random()-0.5) * 0.5;
  const next = Math.max(0.1, series[series.length-1] * (1 + v/100));
  series.push(next);
  if (series.length>180) series.shift();
  tickPrices();
  drawChart();
  requestAnimationFrame(step);
}}

// order flow using names list
const NAMES = Array.isArray(SEED.names) ? SEED.names : ["Trader A"];
function addOrderRow() {{
  const tb = document.querySelector("#blotter tbody");
  const side = Math.random()>.5 ? "BUY" : "SELL";
  const cls = side === "BUY" ? "green" : "red";
  const sym = TICKERS[Math.floor(Math.random()*TICKERS.length)];
  const qty = Math.floor(10 + Math.random()*5000);
  const px = prices[TICKERS.indexOf(sym)] || 10;
  const who = NAMES[Math.floor(Math.random()*NAMES.length)];
  const tr = document.createElement("tr");
  tr.innerHTML = `<td>${{nowTime()}}</td><td>${{who}}</td><td class="${{cls}}">${{side}}</td><td>${{sym}}</td><td>${{qty.toLocaleString()}}</td><td>${{px.toFixed(2)}}</td>`;
  tb.prepend(tr);
  // keep list short
  while (tb.children.length > 40) tb.removeChild(tb.lastChild);
}}

// init
buildWatch();
buildTickerStrip();
loadNews();
spinBreaking();
drawChart();
for (let i=0;i<10;i++) addOrderRow(); // seed a few rows
requestAnimationFrame(step);
setInterval(() => {{ buildWatch(); buildTickerStrip(); }}, 6000);
setInterval(spinBreaking, 5000);
setInterval(addOrderRow, 1200);
</script>
</body>
</html>
"""

components.html(HTML, height=1200, scrolling=True)
