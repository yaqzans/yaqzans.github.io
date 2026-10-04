// yaqzan's metro. the map itself is drawn by build.py, this file makes it run.

const $ = (s, el = document) => el.querySelector(s);
const NS = 'http://www.w3.org/2000/svg';
const DATA = JSON.parse($('#data').textContent);
const map = $('#map');
const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;

let speed = 1;          // 0 paused, 1 play, 3 fast forward
let pending = null;     // the station whose card should open when its train arrives
let riders = 0;
try { riders = +localStorage.getItem('riders') || 0; } catch (e) {}

// ---------- clock + day, top right ----------
const ticks = $('.clock .ticks');
for (let i = 0; i < 12; i++) {
  const a = i * Math.PI / 6, l = document.createElementNS(NS, 'line');
  l.setAttribute('x1', 21 * Math.sin(a)); l.setAttribute('y1', -21 * Math.cos(a));
  l.setAttribute('x2', 24 * Math.sin(a)); l.setAttribute('y2', -24 * Math.cos(a));
  ticks.append(l);
}
function clock() {
  const d = new Date();
  $('#dayname').textContent = d.toLocaleDateString('en-US', { weekday: 'short' }).toUpperCase();
  $('#hand').setAttribute('transform', `rotate(${((d.getHours() % 12) + d.getMinutes() / 60) * 30})`);
}
clock();
setInterval(clock, 20000);
const counter = $('#count');
const showRiders = () => { counter.textContent = riders; };
showRiders();

// ---------- where every station sits along each line ----------
const lines = {};
for (const [id, ln] of Object.entries(DATA.lines)) {
  const path = $(`#L-${id}`);
  const total = path.getTotalLength();
  const samples = [];
  for (let s = 0; s <= total; s += 2) samples.push([s, path.getPointAtLength(s)]);
  const at = {};
  for (const sid of ln.stations) {
    const st = DATA.stations[sid];
    let best = 0, bd = Infinity;
    for (const [s, p] of samples) {
      const d = (p.x - st.x) ** 2 + (p.y - st.y) ** 2;
      if (d < bd) { bd = d; best = s; }
    }
    at[sid] = best;
  }
  lines[id] = { ...ln, id, path, total, at, stops: ln.stations.map(s => at[s]).sort((a, b) => a - b) };
}

// ---------- one train per line, shuttling end to end like the game ----------
const trainLayer = $('#trains');
const trains = Object.values(lines).map((ln, i) => {
  const g = document.createElementNS(NS, 'g');
  g.setAttribute('class', 'train');
  g.innerHTML = `<rect x="-19" y="-10" width="38" height="20" rx="3.5" fill="${ln.color}"/>`;
  trainLayer.append(g);
  return { ln, g, s: (ln.total * (i * .37 % 1)), dir: i % 2 ? 1 : -1, wait: 0, target: null, then: null };
});

function place(t) {
  const p = t.ln.path.getPointAtLength(t.s);
  const a = t.ln.path.getPointAtLength(Math.max(0, t.s - 3)), b = t.ln.path.getPointAtLength(Math.min(t.ln.total, t.s + 3));
  const ang = Math.atan2(b.y - a.y, b.x - a.x) * 180 / Math.PI;
  t.g.setAttribute('transform', `translate(${p.x.toFixed(1)} ${p.y.toFixed(1)}) rotate(${ang.toFixed(1)})`);
}

function stationAt(ln, s) {
  return ln.stations.find(sid => Math.abs(ln.at[sid] - s) < .5);
}

function arrive(t, sid) {
  t.wait = 900;
  board(sid);
}

function step(t, dt) {
  if (t.wait > 0) { t.wait -= dt * 1000; return; }
  if (t.target != null) {                       // sent somewhere by a click
    const left = t.target - t.s;
    const v = Math.max(380, Math.abs(t.dist) / 1.3);
    const move = Math.sign(left) * Math.min(Math.abs(left), v * dt);
    t.s += move;
    if (Math.abs(t.target - t.s) < .5) {
      t.s = t.target;
      const sid = t.then;
      t.target = t.then = null;
      arrive(t, sid);
      if (sid === pending) { pending = null; openStation(sid); }
    }
    return;
  }
  const before = t.s;
  t.s += t.dir * 70 * dt;
  const lo = Math.min(before, t.s), hi = Math.max(before, t.s);
  const hit = t.ln.stops.find(s => s > lo && s <= hi && Math.abs(s - before) > .5);
  if (hit != null) { t.s = hit; arrive(t, stationAt(t.ln, hit)); }
  if (t.s <= 0) { t.s = 0; t.dir = 1; }
  if (t.s >= t.ln.total) { t.s = t.ln.total; t.dir = -1; }
}

let prev = performance.now();
function frame(now) {
  const dt = Math.min((now - prev) / 1000, .05) * speed;
  prev = now;
  if (dt > 0) for (const t of trains) { step(t, dt); place(t); }
  requestAnimationFrame(frame);
}
trains.forEach(place);
requestAnimationFrame(frame);

// ---------- passengers: little shapes that pile up and get picked up ----------
const SHAPES = ['circle', 'square', 'triangle', 'pentagon', 'diamond', 'cross', 'star'];
const pax = Object.fromEntries(Object.keys(DATA.stations).map(s => [s, []]));
const paxLayer = $('#pax');

function drawPax(sid) {
  paxLayer.querySelectorAll(`[data-s="${sid}"]`).forEach(n => n.remove());
  const st = DATA.stations[sid];
  const below = st.side === 't';
  pax[sid].forEach((shape, i) => {
    const u = document.createElementNS(NS, 'use');
    u.setAttribute('href', `#sh-${shape}`);
    u.setAttribute('data-s', sid);
    u.setAttribute('width', 13); u.setAttribute('height', 13);
    u.setAttribute('x', st.x + 22 + (i % 4) * 15);
    u.setAttribute('y', below ? st.y + 18 + Math.floor(i / 4) * 15 : st.y - 32 - Math.floor(i / 4) * 15);
    u.setAttribute('class', 'p');
    paxLayer.append(u);
  });
}

function spawn() {
  if (speed > 0) {
    const ids = Object.keys(pax).filter(s => pax[s].length < 6);
    const sid = ids[Math.floor(Math.random() * ids.length)];
    if (sid) {
      const own = DATA.stations[sid].shape;
      const opts = SHAPES.filter(s => s !== own);
      pax[sid].push(opts[Math.floor(Math.random() * opts.length)]);
      drawPax(sid);
    }
  }
  setTimeout(spawn, (calm ? 4000 : 1400) / Math.max(speed, 1));
}
spawn();

function board(sid) {
  if (!sid || !pax[sid].length) return;
  riders += pax[sid].length;
  pax[sid] = [];
  drawPax(sid);
  showRiders();
  try { localStorage.setItem('riders', riders); } catch (e) {}
}

// ---------- clicking a station sends a train ----------
function cancelTrips() {
  pending = null;
  for (const t of trains) if (t.target != null) { t.target = t.then = null; }
}

function send(sid, lineId) {
  cancelTrips();
  const st = DATA.stations[sid];
  const pool = trains.filter(t => (lineId ? t.ln.id === lineId : st.lines.includes(t.ln.id)));
  let best = pool[0];
  for (const t of pool) if (Math.abs(t.s - t.ln.at[sid]) < Math.abs(best.s - best.ln.at[sid])) best = t;
  document.querySelectorAll('.stn.on').forEach(n => n.classList.remove('on'));
  $(`.stn[data-id="${sid}"]`).classList.add('on');
  $('#hint').classList.add('gone');
  const goal = best.ln.at[sid];
  if (speed === 0 || Math.abs(best.s - goal) < 1) { openStation(sid); return; }
  pending = sid;
  best.wait = 0;
  best.target = goal;
  best.dist = goal - best.s;
  best.then = sid;
  best.dir = Math.sign(goal - best.s) || 1;
}

document.querySelectorAll('.stn').forEach(n => {
  n.addEventListener('click', e => { e.stopPropagation(); send(n.dataset.id); });
  n.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); send(n.dataset.id); } });
});

// ---------- the card ----------
const card = $('#card');
function esc(s) { return s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }
function light(hex) {
  const [r, g, b] = [1, 3, 5].map(i => parseInt(hex.slice(i, i + 2), 16));
  return .299 * r + .587 * g + .114 * b > 170;
}
function chips(ids) {
  return ids.map(l => {
    const { color, name } = DATA.lines[l];
    return `<span style="--c:${esc(color)};color:${light(color) ? '#2f2f2f' : '#fff'}">${esc(name)}</span>`;
  }).join('');
}

function show(icon, title, lineIds, text, linksHtml) {
  $('.card-shape use', card).setAttribute('href', icon ? `#sh-${icon}` : '');
  $('.card-shape', card).style.display = icon ? '' : 'none';
  $('h2', card).textContent = title;
  $('.card-lines', card).innerHTML = chips(lineIds);
  $('.card-text', card).textContent = text;
  $('.card-links', card).innerHTML = linksHtml;
  card.hidden = false;
  card.style.animation = 'none'; void card.offsetWidth; card.style.animation = '';
  card.querySelectorAll('.go').forEach(b => b.addEventListener('click', () => send(b.dataset.go, b.dataset.line || undefined)));
}

function goButton(sid, lineId) {
  const st = DATA.stations[sid];
  const l = lineId || st.lines[0];
  return `<button class="go" style="--c:${DATA.lines[l].color}" data-go="${sid}" data-line="${lineId || ''}">${esc(st.name)}</button>`;
}

function openStation(sid) {
  const st = DATA.stations[sid];
  const links = st.links.map(([label, url]) =>
    `<a href="${esc(url)}"${url.startsWith('http') ? ' target="_blank" rel="noopener"' : ''}>${esc(label)} ↗</a>`).join('');
  const related = st.related.map(r => goButton(r)).join('');
  show(st.shape, st.name, st.lines, st.text, links + related);
}

function openLine(id) {
  const ln = DATA.lines[id];
  $('#hint').classList.add('gone');
  show(null, `${ln.name} line`, [id], `${ln.stations.length} stops. pick one.`, ln.stations.map(s => goButton(s, id)).join(''));
}

function closeCard() {
  cancelTrips();
  card.hidden = true;
  document.querySelectorAll('.stn.on').forEach(n => n.classList.remove('on'));
}
$('.x', card).addEventListener('click', closeCard);
addEventListener('keydown', e => { if (e.key === 'Escape') { closeCard(); focusLine(null); } });
map.addEventListener('click', () => { closeCard(); focusLine(null); });

// ---------- line buttons: highlight a line and list its stops ----------
let focused = null;
function focusLine(id) {
  focused = id;
  map.classList.toggle('focus', !!id);
  map.querySelectorAll('.line, .cap').forEach(n => n.classList.toggle('hl', n.dataset.line === id));
  document.querySelectorAll('.ldot').forEach(b => b.classList.toggle('on', b.dataset.line === id));
}
document.querySelectorAll('.ldot').forEach(b => b.addEventListener('click', e => {
  e.stopPropagation();
  if (focused === b.dataset.line) { focusLine(null); closeCard(); return; }
  focusLine(b.dataset.line);
  openLine(b.dataset.line);
}));

// ---------- pause / play / fast forward ----------
document.querySelectorAll('.speed button').forEach(b => b.addEventListener('click', () => {
  speed = +b.dataset.speed;
  document.querySelectorAll('.speed button').forEach(x => x.classList.toggle('on', x === b));
}));

// ---------- external links open in a new tab ----------
document.querySelectorAll('.tools a[href^="http"]').forEach(a => { a.target = '_blank'; a.rel = 'noopener'; });

// ---------- phone held upright: start with aiub in the middle ----------
const sc = $('#scroller');
if (sc.scrollWidth > sc.clientWidth) {
  const aiub = DATA.stations.aiub;
  sc.scrollLeft = aiub.x / 1600 * sc.scrollWidth - sc.clientWidth / 2;
  $('#hint').textContent = 'swipe around, tap a station';
}
