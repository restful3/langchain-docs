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
// localStorage 가 file:// 또는 private browsing 에서 SecurityError 던지면
// 그 이후 모든 var 선언·핸들러 등록이 막혀 슬라이드 네비게이션 자체가 안 됨.
var savedTheme = null;
try { savedTheme = localStorage.getItem('aio-deck-theme'); } catch (e) {}
// 기본은 light. 시스템 다크 모드 자동 추적은 끔 (메뉴 버튼으로 명시 토글만 인정).
var currentTheme = savedTheme || 'light';
function applyTheme(t) {
  document.documentElement.className = 'theme-' + t;
  var icon = document.getElementById('themeIcon');
  var label = document.getElementById('themeLabel');
  if (icon) icon.textContent = t === 'dark' ? '🌙' : '☀️';
  if (label) label.textContent = t === 'dark' ? 'Dark' : 'Light';
  try { localStorage.setItem('aio-deck-theme', t); } catch (e) {}
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

function goTo(i, opts) {
  opts = opts || {};
  curIdx = Math.max(0, Math.min(total - 1, i));
  slidesEl.style.transform = 'translateX(-' + (curIdx * 100) + '%)';
  var curEl = document.getElementById('slideCur');
  if (curEl) {
    if ('value' in curEl) curEl.value = (curIdx + 1);
    else curEl.textContent = (curIdx + 1);
  }
  document.getElementById('progressFill').style.width = ((curIdx + 1) / total * 100) + '%';
  slides.forEach(function(s, idx) { s.classList.toggle('is-active', idx === curIdx); });
  animateCountersOnSlide(slides[curIdx]);
  updateTocCurrent();
  if (!opts.skipHash) setSlideHash(curIdx);
}
function nextSlide() { goTo(curIdx + 1); }
function prevSlide() { goTo(curIdx - 1); }

// Keyboard nav
document.addEventListener('keydown', function(e) {
  if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.isContentEditable)) return;
  if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') { e.preventDefault(); nextSlide(); }
  if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); prevSlide(); }
  if (e.key === 'Home') { e.preventDefault(); goTo(0); }
  if (e.key === 'End') { e.preventDefault(); goTo(total - 1); }
});

// Page number input
var slideCurInput = document.getElementById('slideCur');
if (slideCurInput && 'value' in slideCurInput) {
  slideCurInput.addEventListener('focus', function() { slideCurInput.select(); });
  slideCurInput.addEventListener('input', function() {
    slideCurInput.value = slideCurInput.value.replace(/[^0-9]/g, '').slice(0, 4);
  });
  slideCurInput.addEventListener('keydown', function(e) {
    e.stopPropagation();
    if (e.key === 'Enter') {
      var n = parseInt(slideCurInput.value, 10);
      if (n >= 1) goTo(n - 1);
      slideCurInput.blur();
    } else if (e.key === 'Escape') {
      slideCurInput.value = (curIdx + 1);
      slideCurInput.blur();
    }
  });
  slideCurInput.addEventListener('blur', function() {
    slideCurInput.value = (curIdx + 1);
  });
}

// Table of contents
var tocPanel = document.getElementById('tocPanel');
var tocToggle = document.getElementById('tocToggle');

function slideLabel(slide, idx) {
  if (slide.classList.contains('slide--cover')) return '표지';
  if (slide.classList.contains('slide--closing')) return '마무리';
  if (slide.classList.contains('slide--section')) {
    var sectionTitle = slide.querySelector('h1');
    var sectionNum = slide.querySelector('.section-num');
    var n = sectionNum ? sectionNum.textContent.trim() : '';
    return (n ? 'S' + n + '  ' : '') + (sectionTitle ? sectionTitle.textContent.trim() : '섹션');
  }
  var h = slide.querySelector('.slide-title, h1');
  return (slide.getAttribute('aria-label') || (h ? h.textContent.trim() : '') || ('슬라이드 ' + (idx + 1))).trim();
}

function buildToc() {
  if (!tocPanel || tocPanel.dataset.built === '1') return;
  tocPanel.dataset.built = '1';
  var title = document.createElement('div');
  title.className = 'toc-panel__title';
  title.textContent = '목차';
  tocPanel.appendChild(title);
  slides.forEach(function(s, idx) {
    var isSection = s.classList.contains('slide--section');
    var btn = document.createElement('button');
    btn.className = 'toc-row' + (isSection ? ' toc-row--group' : '');
    btn.dataset.idx = idx;
    var num = document.createElement('span');
    num.className = 'toc-row__num';
    num.textContent = idx + 1;
    btn.appendChild(num);
    btn.appendChild(document.createTextNode(slideLabel(s, idx)));
    btn.addEventListener('click', function() { goTo(idx); closeToc(); });
    tocPanel.appendChild(btn);
  });
}

function updateTocCurrent() {
  if (!tocPanel) return;
  tocPanel.querySelectorAll('.toc-row').forEach(function(r) {
    var on = parseInt(r.dataset.idx, 10) === curIdx;
    r.classList.toggle('current', on);
    if (on && tocPanel.classList.contains('open')) r.scrollIntoView({ block: 'nearest' });
  });
}

function openToc() {
  if (!tocPanel) return;
  buildToc();
  tocPanel.classList.add('open');
  tocPanel.setAttribute('aria-hidden', 'false');
  if (tocToggle) tocToggle.setAttribute('aria-expanded', 'true');
  updateTocCurrent();
  showChrome();
}
function closeToc() {
  if (!tocPanel) return;
  tocPanel.classList.remove('open');
  tocPanel.setAttribute('aria-hidden', 'true');
  if (tocToggle) tocToggle.setAttribute('aria-expanded', 'false');
  showChrome();
}
function toggleToc() {
  if (tocPanel && tocPanel.classList.contains('open')) closeToc();
  else openToc();
}
document.addEventListener('click', function(e) {
  if (!tocPanel || !tocPanel.classList.contains('open')) return;
  if (!e.target.closest('.toc-panel') && !e.target.closest('.toc-toggle')) closeToc();
});
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') closeToc();
});

// Shareable slide hash
function parseSlideHash() {
  var m = window.location.hash.match(/(?:slide-|\/)?(\d+)$/);
  if (!m) return 0;
  return Math.max(0, Math.min(total - 1, parseInt(m[1], 10) - 1));
}
function setSlideHash(idx) {
  var h = '#/' + (idx + 1);
  if (window.location.hash !== h) history.replaceState(null, '', h);
}
window.addEventListener('hashchange', function() {
  goTo(parseSlideHash(), { skipHash: true });
});

// Auto-hide chrome on mouse idle
var chromeTimer = null;
function hideChrome() {
  var dd = document.getElementById('vizMenuDropdown');
  if ((tocPanel && tocPanel.classList.contains('open'))
      || (dd && dd.classList.contains('open'))
      || (slideCurInput && document.activeElement === slideCurInput)) {
    chromeTimer = setTimeout(hideChrome, 3000);
    return;
  }
  document.body.classList.add('chrome-hidden');
}
function showChrome() {
  document.body.classList.remove('chrome-hidden');
  if (chromeTimer) clearTimeout(chromeTimer);
  chromeTimer = setTimeout(hideChrome, 3000);
}
document.addEventListener('mousemove', showChrome);

// Touch swipe
var touchStart = null;
document.addEventListener('touchstart', function(e) { touchStart = e.touches[0].clientX; });
document.addEventListener('touchend', function(e) {
  if (touchStart === null) return;
  var dx = e.changedTouches[0].clientX - touchStart;
  if (Math.abs(dx) > 50) { if (dx < 0) nextSlide(); else prevSlide(); }
  touchStart = null;
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
  buildToc();
  goTo(parseSlideHash(), { skipHash: true });
  document.body.classList.add('chrome-hidden');
});
