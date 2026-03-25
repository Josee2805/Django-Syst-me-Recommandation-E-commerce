/* ═══════════════════════════════════════════════
   RECOSHOP — MAIN JS  (vanilla + Chart.js)
═══════════════════════════════════════════════ */

'use strict';

/* ── CUSTOM CURSOR ── */
(function () {
  const cursor = document.getElementById('custom-cursor');
  if (!cursor || window.matchMedia('(hover: none)').matches) return;

  let mouseX = 0, mouseY = 0, cx = 0, cy = 0;

  document.addEventListener('mousemove', e => { mouseX = e.clientX; mouseY = e.clientY; });

  (function loop() {
    cx += (mouseX - cx) * 0.15;
    cy += (mouseY - cy) * 0.15;
    cursor.style.left = cx + 'px';
    cursor.style.top  = cy + 'px';
    requestAnimationFrame(loop);
  })();

  document.querySelectorAll('a, button, [role="button"], .product-card, .category-card').forEach(el => {
    el.addEventListener('mouseenter', () => cursor.classList.add('hovering'));
    el.addEventListener('mouseleave', () => cursor.classList.remove('hovering'));
  });
})();

/* ── SCROLL PROGRESS BAR ── */
(function () {
  const bar = document.getElementById('scroll-progress');
  if (!bar) return;
  function update() {
    const h = document.documentElement.scrollHeight - window.innerHeight;
    bar.style.width = (h > 0 ? (window.scrollY / h) * 100 : 0) + '%';
  }
  window.addEventListener('scroll', update, { passive: true });
  update();
})();

/* ── NAVBAR SCROLL EFFECT ── */
(function () {
  const nav = document.querySelector('.navbar');
  if (!nav) return;
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 60);
  }, { passive: true });
})();

/* ── SCROLL REVEAL (Intersection Observer) ── */
(function () {
  const els = document.querySelectorAll('[data-reveal]');
  if (!els.length) return;

  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      const delay = parseInt(e.target.dataset.revealDelay || 0);
      setTimeout(() => e.target.classList.add('revealed'), delay);
      io.unobserve(e.target);
    });
  }, { threshold: 0.10, rootMargin: '0px 0px -40px 0px' });

  els.forEach(el => io.observe(el));
})();

/* ── ANIMATED COUNTERS ── */
function animateCounter(el, target, duration) {
  duration = duration || 2000;
  const isFloat = !Number.isInteger(target);
  const start   = performance.now();
  (function tick(now) {
    const p = Math.min((now - start) / duration, 1);
    const v = (1 - Math.pow(1 - p, 3)) * target;          // ease-out cubic
    el.textContent = isFloat ? v.toFixed(2) : Math.round(v);
    if (p < 1) requestAnimationFrame(tick);
  })(start);
}

(function () {
  const els = document.querySelectorAll('[data-count]');
  if (!els.length) return;
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      animateCounter(e.target, parseFloat(e.target.dataset.count));
      io.unobserve(e.target);
    });
  }, { threshold: 0.5 });
  els.forEach(el => io.observe(el));
})();

/* ── TOAST NOTIFICATIONS ── */
function showToast(msg, type, duration) {
  type     = type     || 'default';
  duration = duration || 3000;

  let box = document.getElementById('toast-container');
  if (!box) {
    box = document.createElement('div');
    box.id = 'toast-container';
    document.body.appendChild(box);
  }

  const t = document.createElement('div');
  t.className = 'toast' + (type !== 'default' ? ' toast--' + type : '');
  const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : '✦';
  t.innerHTML = '<span>' + icon + '</span> ' + msg;
  box.appendChild(t);

  setTimeout(() => {
    t.style.animation = 'toastOut 0.3s ease forwards';
    setTimeout(() => t.remove(), 300);
  }, duration);
}

/* ── CSRF ── */
function getCookie(name) {
  let val = null;
  document.cookie.split(';').forEach(c => {
    c = c.trim();
    if (c.startsWith(name + '=')) val = decodeURIComponent(c.slice(name.length + 1));
  });
  return val;
}

/* ── ADD TO CART (AJAX) ── */
function addToCart(productId, event) {
  const btn = event.currentTarget;
  const orig = btn.innerHTML;
  btn.innerHTML = '↻';
  btn.style.animation = 'spin 0.8s linear infinite';

  fetch('/cart/add/' + productId + '/', {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
      'X-Requested-With': 'XMLHttpRequest'
    }
  })
  .then(r => r.json())
  .then(data => {
    btn.innerHTML = orig;
    btn.style.animation = '';
    if (data.success) {
      document.querySelectorAll('.navbar-badge, .cart-badge, .nav-badge').forEach(el => {
        el.textContent = data.cart_count;
        el.style.display = data.cart_count > 0 ? 'flex' : 'none';
      });
      showToast('Ajouté au panier !', 'success');
    } else {
      showToast('Erreur lors de l\'ajout', 'error');
    }
  })
  .catch(() => {
    btn.innerHTML = orig;
    btn.style.animation = '';
    showToast('Erreur réseau', 'error');
  });
}

/* ── HERO PARALLAX ── */
(function () {
  const hero = document.querySelector('.hero');
  if (!hero) return;
  const bg = hero.querySelector('.hero-bg');
  if (!bg) return;

  bg.style.transition = 'transform 0.6s ease';

  hero.addEventListener('mousemove', e => {
    const r = hero.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width  - 0.5;
    const y = (e.clientY - r.top)  / r.height - 0.5;
    bg.style.transform = 'translate(' + (x * 20) + 'px, ' + (y * 20) + 'px) scale(1.05)';
  });
  hero.addEventListener('mouseleave', () => {
    bg.style.transform = 'translate(0, 0) scale(1)';
  });
})();

/* ── HERO TITLE — LETTER BY LETTER ── */
(function () {
  const title = document.querySelector('.hero-title[data-animate-chars]');
  if (!title) return;
  const text = title.textContent;
  title.innerHTML = '';
  text.split('').forEach((ch, i) => {
    const s = document.createElement('span');
    s.className = 'char';
    s.textContent = ch === ' ' ? '\u00A0' : ch;
    s.style.animationDelay = (i * 0.04) + 's';
    title.appendChild(s);
  });
})();

/* ── SKELETON → CONTENT ── */
function showContent(skeletonId, contentId) {
  const sk = document.getElementById(skeletonId);
  const ct = document.getElementById(contentId);
  if (sk) sk.style.display = 'none';
  if (ct) ct.style.display = '';
}

/* ── MODAL ── */
function openModal(id) {
  const m = document.getElementById(id);
  if (m) { m.classList.add('open'); document.body.style.overflow = 'hidden'; }
}
function closeModal(id) {
  const m = document.getElementById(id);
  if (m) { m.classList.remove('open'); document.body.style.overflow = ''; }
}
document.querySelectorAll('.modal-overlay').forEach(ov => {
  ov.addEventListener('click', e => { if (e.target === ov) closeModal(ov.id); });
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') document.querySelectorAll('.modal-overlay.open').forEach(m => closeModal(m.id));
});

/* ── MOBILE MENU ── */
function toggleMobileMenu() {
  const m = document.getElementById('mobile-menu');
  if (m) m.classList.toggle('open');
}

/* ── STAR RATING ── */
function setRating(val) {
  const inp = document.getElementById('ratingScore');
  if (inp) inp.value = val;
  document.querySelectorAll('.star-btn').forEach(b => {
    b.classList.toggle('filled', parseInt(b.dataset.val) <= val);
  });
}

/* ── PRICE RANGE SLIDER ── */
(function () {
  const slider  = document.getElementById('priceRange');
  const display = document.getElementById('priceDisplay');
  if (!slider || !display) return;

  function update() {
    const pct = ((slider.value - slider.min) / (slider.max - slider.min)) * 100;
    slider.style.background =
      'linear-gradient(to right, var(--accent) ' + pct + '%, rgba(200,169,110,0.2) ' + pct + '%)';
    display.textContent = Number(slider.value).toLocaleString('fr-FR') + ' FCFA';
  }
  slider.addEventListener('input', update);
  update();
})();

/* ── THEME TOGGLE ── */
(function () {
  const STORAGE_KEY = 'recoshop-theme';
  const html = document.documentElement;

  const ICON_MOON = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
  const ICON_SUN  = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>';

  function applyTheme(theme) {
    html.setAttribute('data-theme', theme);
    document.querySelectorAll('.theme-toggle').forEach(btn => {
      btn.innerHTML = theme === 'dark' ? ICON_SUN : ICON_MOON;
      btn.setAttribute('aria-label', theme === 'dark' ? 'Mode clair' : 'Mode sombre');
    });
  }

  // Appliquer dès le chargement
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved) applyTheme(saved);

  window.toggleTheme = function () {
    const current = html.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    localStorage.setItem(STORAGE_KEY, next);
  };
})();

function openSidebar()  { /* legacy — no-op */ }
function closeSidebar() { /* legacy — no-op */ }

/* ── INJECT SPIN KEYFRAME ── */
(function () {
  const s = document.createElement('style');
  s.textContent = '@keyframes spin { to { transform: rotate(360deg); } }';
  document.head.appendChild(s);
})();
