// yaqzan's room. no build step, no libraries.

const $ = (s, el = document) => el.querySelector(s);
const stage = $('#stage');
const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;

// ---------- camcorder clock: today's date, but it's always 1998 ----------
const MONTHS = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];
function clock() {
  const d = new Date();
  const h = d.getHours() % 12 || 12;
  const pad = n => String(n).padStart(2, '0');
  const t = `${h}:${pad(d.getMinutes())}:${pad(d.getSeconds())} ${d.getHours() < 12 ? 'AM' : 'PM'}`;
  $('#date').textContent = `${MONTHS[d.getMonth()]}. ${pad(d.getDate())} 1998`;
  $('#time').textContent = t;
  $('#guide-time').textContent = t;
}
clock();
setInterval(clock, 1000);
$('#news-date').textContent = new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'long' }).toLowerCase() + ', 1998';

// ---------- the logo on the tv ----------
// screen is x 426..576, y 236..354 in room units; logo is 50 x 22 drawn at 1.4x
const SCREEN = { x0: 426, y0: 236, x1: 576, y1: 354 };
const LOGO = { w: 70, h: 31 };
const COLORS = ['#ff3b3b', '#3bff6f', '#3b8bff', '#ffe03b', '#ff3bd8', '#3bfff2', '#ff8a3b', '#ffffff'];
const dvd = $('#dvd');
let x = 470, y = 280, vx = 31, vy = 23, ci = 0, lastX = -1e9, lastY = -1e9, prev = performance.now();

let corners = 0;
try { corners = +localStorage.getItem('corners') || 0; } catch (e) {}
function showCorners() { $('#corners').textContent = corners ? `corner hits: ${corners}` : ''; }
showCorners();

function bounce(now, axis) {
  ci = (ci + 1 + Math.floor(Math.random() * (COLORS.length - 1))) % COLORS.length;
  if (axis === 'x') lastX = now; else lastY = now;
  if (Math.abs(lastX - lastY) < 90) corner();
}

function corner() {
  lastX = lastY = -1e9;  // one corner, one count
  corners++;
  try { localStorage.setItem('corners', corners); } catch (e) {}
  showCorners();
  const big = $('#big');
  big.innerHTML = 'IT HIT THE CORNER';
  big.classList.remove('on'); void big.offsetWidth; big.classList.add('on');
  setTimeout(() => big.classList.remove('on'), 2400);
  const f = $('#screenflash');
  f.setAttribute('opacity', '.9');
  setTimeout(() => f.setAttribute('opacity', '0'), 120);
}

function tick(now) {
  const dt = Math.min((now - prev) / 1000, .05) * (calm ? .4 : 1);
  prev = now;
  x += vx * dt; y += vy * dt;
  if (x <= SCREEN.x0) { x = SCREEN.x0; vx = Math.abs(vx); bounce(now, 'x'); }
  if (x + LOGO.w >= SCREEN.x1) { x = SCREEN.x1 - LOGO.w; vx = -Math.abs(vx); bounce(now, 'x'); }
  if (y <= SCREEN.y0) { y = SCREEN.y0; vy = Math.abs(vy); bounce(now, 'y'); }
  if (y + LOGO.h >= SCREEN.y1) { y = SCREEN.y1 - LOGO.h; vy = -Math.abs(vy); bounce(now, 'y'); }
  dvd.setAttribute('transform', `translate(${x.toFixed(2)} ${y.toFixed(2)}) scale(1.4)`);
  dvd.style.color = COLORS[ci];
  requestAnimationFrame(tick);
}
requestAnimationFrame(tick);

// ---------- tape noise + the tracking band that rolls through now and then ----------
if (!calm) {
  const cv = $('#noise'), cx = cv.getContext('2d'), img = cx.createImageData(cv.width, cv.height);
  setInterval(() => {
    for (let i = 0; i < img.data.length; i += 4) {
      const v = Math.random() * 255;
      img.data[i] = img.data[i + 1] = img.data[i + 2] = v;
      img.data[i + 3] = 255;
    }
    cx.putImageData(img, 0, 0);
  }, 80);

  const band = $('#band');
  (function roll() {
    band.classList.remove('run'); void band.offsetWidth; band.classList.add('run');
    setTimeout(roll, 6000 + Math.random() * 9000);
  })();
}

function glitch() {
  if (calm) return;
  document.body.classList.add('glitch');
  setTimeout(() => document.body.classList.remove('glitch'), 180);
}

// ---------- phone held upright: start looking at the tv ----------
const pan = $('#pan');
if (pan.scrollWidth > pan.clientWidth) {
  pan.scrollLeft = (pan.scrollWidth - pan.clientWidth) / 2;
  $('#hint').textContent = 'swipe to look around';
  pan.addEventListener('scroll', () => { label.style.display = 'none'; }, { passive: true });
}

// ---------- hover labels ----------
const label = $('#label');
document.querySelectorAll('.obj').forEach(o => {
  const show = () => {
    const r = o.getBoundingClientRect(), s = stage.getBoundingClientRect();
    label.textContent = `[ ${o.dataset.label} ]`;
    label.style.display = 'block';
    label.style.left = `${Math.max(4, r.left - s.left + r.width / 2 - label.offsetWidth / 2)}px`;
    label.style.top = `${Math.max(4, r.top - s.top - label.offsetHeight - 6)}px`;
  };
  const hide = () => { label.style.display = 'none'; };
  o.addEventListener('mouseenter', show);
  o.addEventListener('focus', show);
  o.addEventListener('mouseleave', hide);
  o.addEventListener('blur', hide);
  o.addEventListener('click', () => open(o.dataset.panel));
  o.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(o.dataset.panel); } });
});

// ---------- panels ----------
let current = null, opener = null;
function open(name) {
  const p = $(`#panel-${name}`);
  if (!p) return;
  $('#hint').classList.add('gone');
  opener = document.activeElement;
  glitch();
  p.hidden = false;
  p.classList.remove('in'); void p.offsetWidth; p.classList.add('in');
  current = p;
  $('.close', p).focus();
  if (name === 'tv') loadChannels();
  if (name === 'phone') beep();
}
function close() {
  if (!current) return;
  current.hidden = true;
  current = null;
  glitch();
  if (opener) opener.focus();
}
document.querySelectorAll('.panel').forEach(p => {
  p.addEventListener('click', e => { if (e.target === p) close(); });
  $('.close', p).addEventListener('click', close);
});
document.querySelectorAll('.panel a[href^="http"]').forEach(a => { a.target = '_blank'; a.rel = 'noopener'; });
addEventListener('keydown', e => {
  if (e.key === 'Escape') close();
  if (current && current.id === 'panel-phone' && /^[1-5]$/.test(e.key)) {
    const a = current.querySelectorAll('.keys a')[+e.key - 1];
    a.classList.add('pressed');
    setTimeout(() => { a.classList.remove('pressed'); a.click(); }, 150);
  }
});

// ---------- answering machine beep ----------
function beep() {
  try {
    const ac = new (window.AudioContext || window.webkitAudioContext)();
    const o = ac.createOscillator(), g = ac.createGain();
    o.frequency.value = 1000;
    g.gain.value = .06;
    o.connect(g).connect(ac.destination);
    o.start(ac.currentTime + .5);
    o.stop(ac.currentTime + .8);
  } catch (e) {}
}

// ---------- tv guide: every public repo, straight from github ----------
const BLURBS = {
  'oshudbot': 'bangla medicine lookup. 21,714 brands, ask in bangla, english or banglish',
  'who-should-count-more': 'should educated votes count more? run the election and see',
  'cvpr-two-stage-vehicle-recognition': 'vehicles on bangladeshi roads. yolo finds them, convnext names them',
  'ids-sarcasm-detection': 'can a classifier tell when a tweet is being sarcastic',
  'markdown-converter-app': 'pdf, word, ppt or excel in, clean markdown out. one exe',
  'TicTacToeInfinity': 'tic-tac-toe but you only get 4 pieces, then you have to move them',
  '2D-Parking-Game': 'park the car before the timer runs out. opengl',
  'Bus-Management-System': 'java oop final, built in 28 hours',
  'Productivity-Manager': 'notes, reminders and a timer in one c# app',
  'Pink-Calculator': 'a calculator. it is pink',
  'WT_Fall-25-26': 'web tech coursework',
  'WT_Fall-25-26_Project': 'web tech course project, php',
};
const SKIP = new Set(['yaqzans', 'yaqzans.github.io']);
let tuned = false;

async function loadChannels() {
  if (tuned) return;
  const list = $('#channels');
  let repos;
  try {
    const r = await fetch('https://api.github.com/users/yaqzans/repos?per_page=100&sort=pushed');
    if (!r.ok) throw new Error(r.status);
    repos = (await r.json()).filter(x => !x.fork && !x.private && !SKIP.has(x.name));
  } catch (e) {
    // github said no (rate limit, offline). fall back to what was public when this was written
    repos = Object.keys(BLURBS).map(name => ({ name, html_url: `https://github.com/yaqzans/${name}` }));
  }
  list.innerHTML = '';
  repos.forEach((repo, i) => {
    const li = document.createElement('li');
    const ch = document.createElement('span');
    ch.className = 'ch';
    ch.textContent = `CH ${String(i + 2).padStart(2, '0')}`;
    const show = document.createElement('span');
    show.className = 'show';
    const a = document.createElement('a');
    a.href = repo.html_url; a.target = '_blank'; a.rel = 'noopener';
    a.textContent = repo.name.toLowerCase();
    show.append(a);
    if (repo.homepage) {
      const live = document.createElement('a');
      live.href = repo.homepage; live.target = '_blank'; live.rel = 'noopener';
      live.className = 'live'; live.textContent = '[ live ]';
      show.append(live);
    }
    const s = document.createElement('small');
    s.textContent = BLURBS[repo.name] || (repo.description || '').toLowerCase();
    show.append(s);
    li.append(ch, show);
    list.append(li);
  });
  tuned = true;
}
