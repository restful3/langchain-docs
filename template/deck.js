// ===== Menu =====
function toggleMenu() {
  var d = document.getElementById('vizMenuDropdown');
  if (d) d.classList.toggle('open');
}
document.addEventListener('click', function(e) {
  if (!e.target.closest('.viz-menu')) {
    var d = document.getElementById('vizMenuDropdown');
    if (d) d.classList.remove('open');
  }
});
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') {
    var d = document.getElementById('vizMenuDropdown');
    if (d) d.classList.remove('open');
  }
});

// ===== Theme =====
var savedTheme = localStorage.getItem('aio-deck-theme');
var currentTheme = savedTheme || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
function applyTheme(t) {
  document.documentElement.className = 'theme-' + t;
  var icon = document.getElementById('themeIcon');
  var label = document.getElementById('themeLabel');
  if (icon) icon.textContent = t === 'dark' ? '🌙' : '☀️';
  if (label) label.textContent = t === 'dark' ? 'Dark' : 'Light';
  localStorage.setItem('aio-deck-theme', t);
  currentTheme = t;
  if (typeof onThemeChange === 'function') onThemeChange();
}
function cycleTheme() { applyTheme(currentTheme === 'dark' ? 'light' : 'dark'); }
applyTheme(currentTheme);

// ===== Slide Navigation =====
var slidesEl = document.getElementById('slidesContainer');
var slides = slidesEl.querySelectorAll('.slide');
var total = slides.length;
var curIdx = 0;
document.getElementById('slideTotal').textContent = total;

function goTo(i) {
  curIdx = Math.max(0, Math.min(total - 1, i));
  slidesEl.style.transform = 'translateX(-' + (curIdx * 100) + '%)';
  document.getElementById('slideCur').textContent = (curIdx + 1);
  document.getElementById('progressFill').style.width = ((curIdx + 1) / total * 100) + '%';
  slides.forEach(function(s, idx) { s.classList.toggle('is-active', idx === curIdx); });
  // Animate counters on slides as they become active
  animateCountersOnSlide(slides[curIdx]);
}
function nextSlide() { goTo(curIdx + 1); }
function prevSlide() { goTo(curIdx - 1); }

// Keyboard nav
document.addEventListener('keydown', function(e) {
  if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') { e.preventDefault(); nextSlide(); }
  if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); prevSlide(); }
  if (e.key === 'Home') { e.preventDefault(); goTo(0); }
  if (e.key === 'End') { e.preventDefault(); goTo(total - 1); }
});

// Touch swipe
var touchStart = null;
document.addEventListener('touchstart', function(e) { touchStart = e.touches[0].clientX; });
document.addEventListener('touchend', function(e) {
  if (touchStart === null) return;
  var dx = e.changedTouches[0].clientX - touchStart;
  if (Math.abs(dx) > 50) { if (dx < 0) nextSlide(); else prevSlide(); }
  touchStart = null;
});

// Click left/right third of screen
document.querySelector('.deck').addEventListener('click', function(e) {
  if (e.target.closest('.slide-nav') || e.target.closest('.viz-menu') || e.target.closest('button') || e.target.closest('a')) return;
  var x = e.clientX, w = window.innerWidth;
  if (x < w * 0.33) prevSlide();
  else if (x > w * 0.66) nextSlide();
});

// ===== Number Counter (per slide) =====
function animateCountersOnSlide(slide) {
  var els = slide.querySelectorAll('[data-count]');
  els.forEach(function(el) {
    if (el.dataset.counted === '1') return;
    el.dataset.counted = '1';
    var target = parseFloat(el.dataset.count);
    var suffix = el.dataset.suffix || '';
    var prefix = el.dataset.prefix || '';
    var start = performance.now(), duration = 1100;
    var isFloat = String(target).indexOf('.') > -1;
    (function tick(now) {
      var p = Math.min((now - start) / duration, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      var v = target * eased;
      el.textContent = prefix + (isFloat ? v.toFixed(1) : Math.round(v).toLocaleString()) + suffix;
      if (p < 1) requestAnimationFrame(tick);
    })(start);
  });
}

// ===== Chart.js =====
var chartsBuilt = false;
var barsChart = null;
function getChartColors() {
  var s = getComputedStyle(document.documentElement);
  return {
    text: s.getPropertyValue('--text').trim(),
    textSecondary: s.getPropertyValue('--text-secondary').trim(),
    border: s.getPropertyValue('--border').trim(),
    surface: s.getPropertyValue('--surface').trim(),
    lgRed: s.getPropertyValue('--brand-primary').trim(),
    lgRedDeep: s.getPropertyValue('--brand-deep').trim(),
  };
}
function resetCanvas(id) {
  var old = document.getElementById(id);
  if (!old) return null;
  var parent = old.parentNode;
  var c = document.createElement('canvas');
  c.id = id;
  c.setAttribute('role', 'img');
  c.setAttribute('aria-label', 'Bars chart');
  parent.replaceChild(c, old);
  return c;
}
function buildCharts() {
  if (typeof Chart === 'undefined') { console.error('Chart.js not loaded'); return; }
  if (chartsBuilt) return;
  var c = getChartColors();
  // Create red gradient (computed inline in plugin)
  try { if (barsChart) { barsChart.destroy(); barsChart = null; } } catch (e) {}
  var ctx = resetCanvas('barsChart');
  if (!ctx) return;
  var gctx = ctx.getContext('2d');
  var grad = gctx.createLinearGradient(0, 0, ctx.parentElement.clientWidth, 0);
  grad.addColorStop(0, c.lgRedDeep);
  grad.addColorStop(1, c.lgRed);
  var gray = gctx.createLinearGradient(0, 0, ctx.parentElement.clientWidth, 0);
  gray.addColorStop(0, '#4A4A52');
  gray.addColorStop(1, '#8A8A92');
  barsChart = new Chart(gctx, {
    type: 'bar',
    data: {
      labels: ['배포 계획', '거버넌스 성숙', '프로덕션 운영', '성숙 단계 도달'],
      datasets: [{
        label: '%',
        data: [74, 21, 51, 11],
        backgroundColor: [grad, gray, grad, gray],
        borderRadius: 6,
        borderSkipped: false,
        barThickness: 32,
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      layout: { padding: { top: 10, right: 30, bottom: 10, left: 10 } },
      plugins: {
        legend: { display: false },
        tooltip: {
          enabled: true,
          backgroundColor: c.text,
          titleColor: c.surface,
          bodyColor: c.surface,
          padding: 12,
          cornerRadius: 8,
          displayColors: false,
          callbacks: { label: function(ctx) { return ctx.parsed.x + '%'; } }
        }
      },
      scales: {
        x: {
          beginAtZero: true,
          max: 100,
          ticks: { color: c.textSecondary, font: { size: 12, family: 'Inter', weight: '600' }, callback: function(v) { return v + '%'; } },
          grid: { color: c.border, drawBorder: false },
          border: { display: false }
        },
        y: {
          ticks: { color: c.text, font: { size: 14, family: 'Inter', weight: '700' } },
          grid: { display: false },
          border: { display: false }
        }
      }
    }
  });
  chartsBuilt = true;
}
function onThemeChange() {
  chartsBuilt = false;
  setTimeout(buildCharts, 120);
}

// ===== Fit stage to viewport (interactive only) =====
function fitStage() {
  var s = Math.min(window.innerWidth / 1280, window.innerHeight / 720);
  document.documentElement.style.setProperty('--deck-scale', s);
}
window.addEventListener('resize', fitStage);

// ===== Rebuild charts before print =====
window.addEventListener('beforeprint', function() {
  chartsBuilt = false;
  buildCharts();
});
window.addEventListener('afterprint', function() {
  chartsBuilt = false;
  setTimeout(buildCharts, 100);
});

// ===== Init =====
window.addEventListener('load', function() {
  fitStage();
  buildCharts();
  goTo(0);
});

// ===== Download PNG =====
async function downloadImage() {
  var menu = document.querySelector('.viz-menu');
  var nav = document.querySelector('.slide-nav');
  var prog = document.querySelector('.deck-progress');
  menu.style.display = 'none';
  nav.style.display = 'none';
  prog.style.display = 'none';
  try {
    var url = await htmlToImage.toPng(document.body, { quality: 1, pixelRatio: 2 });
    var a = document.createElement('a');
    a.href = url;
    a.download = 'ai-odyssey-slide-' + (curIdx + 1) + '.png';
    a.click();
  } catch (e) { console.error('Download failed:', e); }
  menu.style.display = '';
  nav.style.display = '';
  prog.style.display = '';
}
치환 2 건
