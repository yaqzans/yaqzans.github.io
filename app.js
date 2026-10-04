// yaqzan's network map. the map itself is drawn by build.py, this file makes it run.

const $ = (s, el = document) => el.querySelector(s);
const NS = 'http://www.w3.org/2000/svg';
const DATA = JSON.parse($('#data').textContent);
const map = $('#map');
const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
let pending = null;     // the stop whose card should open when its train arrives
let busyUntil = 0;      // the board stays on a ride message until then

// ---------- station clock ----------
function clock() {
  const d = new Date();
  const s = d.getSeconds(), m = d.getMinutes() + s / 60, h = (d.getHours() % 12) + m / 60;
  document.querySelectorAll('.ch').forEach(n => n.setAttribute('transform', `rotate(${h * 30})`));
  document.querySelectorAll('.cm').forEach(n => n.setAttribute('transform', `rotate(${m * 6})`));
  document.querySelectorAll('.cs').forEach(n => n.setAttribute('transform', `rotate(${s * 6})`));
}
clock();
setInterval(clock, 1000);

// ---------- departures board ----------
function board(top, dest, when) {
  [['.led1', top], ['.led2', dest], ['.led3', when]].forEach(([cls, text]) => {
    document.querySelectorAll(cls).forEach(el => {
      if (el.textContent === text) return;
      el.textContent = text;
      const row = el.closest('.led');
      row.classList.remove('flip'); void row.offsetWidth; row.classList.add('flip');
    });
  });
}
const IDLE = [
  () => ['yaqzan\'s network', 'pick a stop', ''],
  () => ['6 lines from', 'first day, aiub', ''],
  () => { const s = randomStop(); return [`next: ${DATA.lines[s.lines[0]].name}`, s.name, `${1 + Math.floor(Math.random() * 6)} min`]; },
  () => { const s = randomStop(); return [`next: ${DATA.lines[s.lines[0]].name}`, s.name, `${1 + Math.floor(Math.random() * 6)} min`]; },
];
function randomStop() {
  const ids = Object.keys(DATA.stations).filter(s => s !== 'aiub');
  return DATA.stations[ids[Math.floor(Math.random() * ids.length)]];
}
let idle = 0;
setInterval(() => {
  if (Date.now() < busyUntil) return;
  board(...IDLE[idle++ % IDLE.length]());
}, 5000);

// ---------- where every stop sits along each line ----------
const lines = {};
for (const [id, ln] of Object.entries(DATA.lines)) {
  const path = $(`#L-${id}`);
  const total = path.getTotalLength();
  const at = {};
  for (const sid of ln.stations) {
    const st = DATA.stations[sid];
    let best = 0, bd = Infinity;
    for (let s = 0; s <= total; s += 2) {
      const p = path.getPointAtLength(s);
      const d = (p.x - st.x) ** 2 + (p.y - st.y) ** 2;
      if (d < bd) { bd = d; best = s; }
    }
    at[sid] = best;
  }
  lines[id] = { ...ln, id, path, total, at, stops: ln.stations.map(s => at[s]).sort((a, b) => a - b) };
}

// ---------- one train per line, running out and back ----------
const trainLayer = $('#trains');
const trains = Object.values(lines).map((ln, i) => {
  const g = document.createElementNS(NS, 'g');
  g.innerHTML = `<rect x="-15" y="-6.5" width="30" height="13" rx="2" fill="${ln.color}" stroke="#fff" stroke-width="2"/>`;
  trainLayer.append(g);
  return { ln, g, s: ln.total * ((i * .37) % 1), dir: i % 2 ? 1 : -1, wait: 0, target: null, then: null, dist: 0 };
});

function place(t) {
  const p = t.ln.path.getPointAtLength(t.s);
  const a = t.ln.path.getPointAtLength(Math.max(0, t.s - 3)), b = t.ln.path.getPointAtLength(Math.min(t.ln.total, t.s + 3));
  const ang = Math.atan2(b.y - a.y, b.x - a.x) * 180 / Math.PI;
  t.g.setAttribute('transform', `translate(${p.x.toFixed(1)} ${p.y.toFixed(1)}) rotate(${ang.toFixed(1)})`);
}

function step(t, dt) {
  if (t.wait > 0) { t.wait -= dt * 1000; return; }
  if (t.target != null) {                       // sent somewhere by a click
    const left = t.target - t.s;
    const v = Math.max(380, Math.abs(t.dist) / 1.3);
    t.s += Math.sign(left) * Math.min(Math.abs(left), v * dt);
    if (Math.abs(t.target - t.s) < .5) {
      t.s = t.target;
      const sid = t.then;
      t.target = t.then = null;
      t.wait = 1200;
      if (sid === pending) {
        pending = null;
        board('arrived at', DATA.stations[sid].name, 'now');
        busyUntil = Date.now() + 6000;
        openStation(sid);
      }
    }
    return;
  }
  const before = t.s;
  t.s += t.dir * (calm ? 30 : 60) * dt;
  const lo = Math.min(before, t.s), hi = Math.max(before, t.s);
  const hit = t.ln.stops.find(s => s > lo && s <= hi && Math.abs(s - before) > .5);
  if (hit != null) { t.s = hit; t.wait = 800; }
  if (t.s <= 0) { t.s = 0; t.dir = 1; }
  if (t.s >= t.ln.total) { t.s = t.ln.total; t.dir = -1; }
}

let prev = performance.now();
function frame(now) {
  const dt = Math.min((now - prev) / 1000, .05);
  prev = now;
  if (map.getClientRects().length) for (const t of trains) { step(t, dt); place(t); }  // laptop version only
  requestAnimationFrame(frame);
}
trains.forEach(place);
requestAnimationFrame(frame);

// ---------- picking a stop sends a train ----------
function cancelTrips() {
  pending = null;
  for (const t of trains) if (t.target != null) t.target = t.then = null;
}

function send(sid, lineId) {
  cancelTrips();
  const st = DATA.stations[sid];
  const pool = trains.filter(t => (lineId ? t.ln.id === lineId : st.lines.includes(t.ln.id)));
  let best = pool[0];
  for (const t of pool) if (Math.abs(t.s - t.ln.at[sid]) < Math.abs(best.s - best.ln.at[sid])) best = t;
  document.querySelectorAll('.stn.on').forEach(n => n.classList.remove('on'));
  $(`.stn[data-id="${sid}"]`).classList.add('on');
  const goal = best.ln.at[sid];
  if (Math.abs(best.s - goal) < 1) {
    board('arrived at', st.name, 'now');
    busyUntil = Date.now() + 6000;
    openStation(sid);
    return;
  }
  board(`${best.ln.name} line to`, st.name, 'due');
  busyUntil = Date.now() + 8000;
  best.wait = 0;
  best.target = goal;
  best.dist = goal - best.s;
  best.then = sid;
  pending = sid;
}

document.querySelectorAll('.stn').forEach(n => {
  n.addEventListener('click', e => { e.stopPropagation(); send(n.dataset.id); });
  n.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); send(n.dataset.id); } });
});

// ---------- the card ----------
const card = $('#card');
function esc(s) { return String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }
function light(hex) {
  const [r, g, b] = [1, 3, 5].map(i => parseInt(hex.slice(i, i + 2), 16));
  return .299 * r + .587 * g + .114 * b > 170;
}
function chips(ids) {
  return ids.map(l => {
    const { color, name } = DATA.lines[l];
    return `<span style="--c:${esc(color)};color:${light(color) ? '#1d1d1f' : '#fff'}">${esc(name)} line</span>`;
  }).join('');
}

function show(title, tag, lineIds, text, linksHtml) {
  card.style.setProperty('--c', DATA.lines[lineIds[0]].color);
  $('h2', card).textContent = title;
  $('.card-tag', card).textContent = tag;
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
  return `<button class="go" style="--c:${esc(DATA.lines[l].color)}" data-go="${esc(sid)}" data-line="${esc(lineId || '')}">${esc(st.name)}</button>`;
}

function openStation(sid) {
  const st = DATA.stations[sid];
  const links = st.links.map(([label, url]) =>
    `<a href="${esc(url)}"${url.startsWith('http') ? ' target="_blank" rel="noopener"' : ''}>${esc(label)} ↗</a>`).join('');
  show(st.name, st.tag, st.lines, st.text, links + st.related.map(r => goButton(r)).join(''));
}

function openLine(id) {
  const ln = DATA.lines[id];
  show(`${ln.name} line`, `${ln.stations.length} stops`, [id], 'pick a stop and a train takes you there.',
    ln.stations.map(s => goButton(s, id)).join(''));
}

function closeCard() {
  cancelTrips();
  card.hidden = true;
  document.querySelectorAll('.stn.on').forEach(n => n.classList.remove('on'));
}
$('.x', card).addEventListener('click', closeCard);
addEventListener('keydown', e => { if (e.key === 'Escape') { closeCard(); focusLine(null); } });
map.addEventListener('click', () => { closeCard(); focusLine(null); });

// ---------- legend: highlight a line and list its stops ----------
let focused = null;
function focusLine(id) {
  focused = id;
  map.classList.toggle('focus', !!id);
  map.querySelectorAll('.line, .cap, .badge, .glow').forEach(n => n.classList.toggle('hl', n.dataset.line === id));
  document.querySelectorAll('.ldot').forEach(b => b.classList.toggle('on', b.dataset.line === id));
}
document.querySelectorAll('.ldot').forEach(b => b.addEventListener('click', e => {
  e.stopPropagation();
  if (focused === b.dataset.line) { focusLine(null); closeCard(); return; }
  focusLine(b.dataset.line);
  openLine(b.dataset.line);
}));

// ---------- external links open in a new tab ----------
document.querySelectorAll('.exits a[href^="http"]').forEach(a => { a.target = '_blank'; a.rel = 'noopener'; });

// ---------- phone version: one line at a time, drawn top to bottom ----------
const route = $('#m-route');
let mLine = null;

function mShow(lineId) {
  mLine = lineId;
  const ln = DATA.lines[lineId];
  document.querySelectorAll('.m-tab').forEach(b => b.setAttribute('aria-selected', b.dataset.line === lineId));
  route.style.setProperty('--c', ln.color);
  route.innerHTML = `<h2><i></i>${esc(ln.name)} line</h2><div class="m-strip"><div class="m-train"></div>${
    ln.stations.map(sid => {
      const st = DATA.stations[sid];
      const links = st.links.map(([label, url]) =>
        `<a href="${esc(url)}"${url.startsWith('http') ? ' target="_blank" rel="noopener"' : ''}>${esc(label)} ↗</a>`).join('');
      return `<div class="m-stop${sid === 'start' ? ' hub' : ''}" data-id="${esc(sid)}" tabindex="0" role="button">
        <span class="dot"></span>
        <div><div class="name">${esc(st.name)}</div><div class="tag">${esc(st.tag)}</div></div>
        <div class="more">${esc(st.text)}${links ? `<div class="links">${links}</div>` : ''}</div>
      </div>`;
    }).join('')}</div>`;
  route.querySelectorAll('.m-stop').forEach(n => {
    n.addEventListener('click', e => { if (!e.target.closest('a')) mRide(n.dataset.id); });
    n.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); mRide(n.dataset.id); } });
  });
  mMoveTrain(route.querySelector('.m-stop'), false);
  if (route.getClientRects().length) {          // only when the phone version is the one showing
    board(`${ln.name} line`, 'now boarding', '');
    busyUntil = Date.now() + 6000;
  }
}

function mMoveTrain(stopEl, animate = true) {
  const train = route.querySelector('.m-train');
  const dot = stopEl.querySelector('.dot');
  const y = stopEl.offsetTop + dot.offsetTop + dot.offsetHeight / 2 - 15;
  if (!animate) train.style.transition = 'none';
  train.style.transform = `translateY(${y}px)`;
  if (!animate) { void train.offsetWidth; train.style.transition = ''; }
}

function mRide(sid) {
  const el = route.querySelector(`.m-stop[data-id="${sid}"]`);
  const wasOpen = el.classList.contains('open');
  route.querySelectorAll('.m-stop.open').forEach(n => n.classList.remove('open'));
  if (wasOpen) return;
  const st = DATA.stations[sid];
  board(`${DATA.lines[mLine].name} line to`, st.name, 'due');
  busyUntil = Date.now() + 8000;
  mMoveTrain(el);
  setTimeout(() => {
    el.classList.add('open');
    board('arrived at', st.name, 'now');
    mMoveTrain(el, false);   // the stop grew, keep the train on its dot
  }, calm ? 0 : 900);
}

document.querySelectorAll('.m-tab').forEach(b => b.addEventListener('click', () => mShow(b.dataset.line)));
document.querySelectorAll('.m-exits a[href^="http"]').forEach(a => { a.target = '_blank'; a.rel = 'noopener'; });
mShow(Object.keys(DATA.lines)[0]);
