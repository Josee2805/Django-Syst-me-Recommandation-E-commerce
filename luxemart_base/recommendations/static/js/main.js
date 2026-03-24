/*
  LuxeMart — main.js
  Scripts de base partagés. Personne B complètera ce fichier.
*/

/* ── Thème clair / sombre ── */
(function () {
  const saved = localStorage.getItem('luxemart-theme');
  if (saved === 'dark') {
    document.documentElement.dataset.theme = 'dark';
    const icon = document.getElementById('themeIcon');
    if (icon) icon.className = 'fas fa-sun';
  }
})();

/* ── Fermer automatiquement les messages après 4s ── */
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.msg-toast').forEach(function (el, i) {
    setTimeout(function () {
      el.style.opacity = '0';
      el.style.transform = 'translateX(100%)';
      el.style.transition = 'all 0.4s ease';
      setTimeout(function () { el.remove(); }, 400);
    }, 4000 + i * 600);
  });
});

/* ── Sidebar mobile ── */
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}

/* ── Toggle thème ── */
function toggleTheme() {
  const html  = document.documentElement;
  const icon  = document.getElementById('themeIcon');
  const isDark = html.dataset.theme === 'dark';
  html.dataset.theme = isDark ? 'light' : 'dark';
  if (icon) icon.className = isDark ? 'fas fa-moon' : 'fas fa-sun';
  localStorage.setItem('luxemart-theme', html.dataset.theme);
}

/* ── AJAX : ajouter au panier ── */
function addToCartAjax(slug, quantity) {
  quantity = quantity || 1;
  fetch('/cart/add/' + slug + '/', {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
      'X-Requested-With': 'XMLHttpRequest',
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: 'quantity=' + quantity,
  })
    .then(function (r) { return r.json(); })
    .then(function (data) {
      if (data.success) {
        /* Mettre à jour le badge panier */
        document.querySelectorAll('.badge-cart').forEach(function (b) {
          b.textContent = data.cart_count;
          b.style.display = data.cart_count > 0 ? 'flex' : 'none';
        });
        showToast(data.message || 'Ajouté au panier !', 'success');
      }
    })
    .catch(function () { showToast('Erreur réseau', 'danger'); });
}

/* ── Toast JS ── */
function showToast(message, type) {
  type = type || 'info';
  const container = document.querySelector('.django-messages');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = 'msg-toast ' + type;
  toast.innerHTML =
    '<span>' + message + '</span>' +
    '<button onclick="this.parentElement.remove()" ' +
    'style="margin-left:auto;background:none;border:none;cursor:pointer;color:var(--text-muted);">✕</button>';
  container.appendChild(toast);
  setTimeout(function () {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.4s';
    setTimeout(function () { toast.remove(); }, 400);
  }, 3500);
}

/* ── Cookie CSRF ── */
function getCookie(name) {
  var value = '; ' + document.cookie;
  var parts = value.split('; ' + name + '=');
  if (parts.length === 2) return parts.pop().split(';').shift();
  return '';
}
