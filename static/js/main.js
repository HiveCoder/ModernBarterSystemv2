// ============================================================
// SilkTrade — Main JavaScript
// Adapted for Shuup-style UI + Bootstrap 5
// ============================================================

document.addEventListener('DOMContentLoaded', function () {

  // ---- Navbar Search ----
  const searchInput = document.getElementById('navSearchInput');
  const searchDropdown = document.getElementById('searchDropdown');
  let searchTimeout;

  if (searchInput && searchDropdown) {
    searchInput.addEventListener('input', function () {
      clearTimeout(searchTimeout);
      const q = this.value.trim();
      if (q.length < 2) {
        searchDropdown.innerHTML = '';
        searchDropdown.classList.remove('active');
        return;
      }
      searchTimeout = setTimeout(() => {
        fetch('/api/search?q=' + encodeURIComponent(q))
          .then(r => r.json())
          .then(results => {
            if (results.length === 0) {
              searchDropdown.classList.remove('active');
              return;
            }
            searchDropdown.innerHTML = results.map(item => `
              <a href="/items/${item.id}" class="search-result-item">
                <img src="/static/uploads/${item.image}" alt="" onerror="this.src='/static/uploads/no_image.png'"/>
                <div class="result-info">
                  <div class="result-title">${escapeHtml(item.title)}</div>
                  <div class="result-meta">${escapeHtml(item.condition)} &middot; by ${escapeHtml(item.owner)}</div>
                </div>
              </a>
            `).join('');
            searchDropdown.classList.add('active');
          })
          .catch(() => {});
      }, 300);
    });

    searchInput.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') {
        window.location.href = '/marketplace?q=' + encodeURIComponent(this.value);
      }
    });

    document.addEventListener('click', function (e) {
      if (!document.getElementById('navSearchWrapper').contains(e.target)) {
        searchDropdown.classList.remove('active');
      }
    });
  }

  // ---- Notification Badge ----
  const notifBadge = document.getElementById('notifBadge');
  if (notifBadge) {
    function refreshNotifCount() {
      fetch('/api/notifications/count')
        .then(r => r.json())
        .then(data => {
          if (data.count > 0) {
            notifBadge.textContent = data.count > 99 ? '99+' : data.count;
            notifBadge.style.display = 'flex';
          } else {
            notifBadge.style.display = 'none';
          }
        })
        .catch(() => {});
    }
    refreshNotifCount();
    setInterval(refreshNotifCount, 30000);
  }

  // ---- Flash Auto-Dismiss (Bootstrap alerts) ----
  document.querySelectorAll('.flash-msg').forEach(el => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });

  // ---- Wishlist toggle ----
  window.toggleWishlist = function (btn) {
    const itemId = btn.dataset.itemId;
    fetch('/api/wishlist/toggle/' + itemId, { method: 'POST' })
      .then(r => r.json())
      .then(data => {
        const icon = btn.querySelector('i');
        if (data.wishlisted) {
          icon.className = 'fa-solid fa-heart';
          btn.classList.add('wishlisted');
        } else {
          icon.className = 'fa-regular fa-heart';
          btn.classList.remove('wishlisted');
        }
      })
      .catch(() => {});
  };

  // ---- Hamburger (main-nav cats) ----
  const hamburger = document.getElementById('hamburger');
  const mainNavCats = document.querySelector('.main-nav-cats');
  if (hamburger && mainNavCats) {
    hamburger.addEventListener('click', () => {
      mainNavCats.classList.toggle('open');
    });
  }

  // ---- Image gallery thumbs (item detail) ----
  document.querySelectorAll('.item-gallery-thumb').forEach(thumb => {
    thumb.addEventListener('click', function () {
      const mainImg = document.getElementById('galleryMain');
      if (mainImg) {
        mainImg.src = this.dataset.src;
        document.querySelectorAll('.item-gallery-thumb').forEach(t => t.classList.remove('active'));
        this.classList.add('active');
      }
    });
  });

  // ---- Trade tab switcher ----
  document.querySelectorAll('.trade-tab-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const target = this.dataset.tab;
      document.querySelectorAll('.trade-tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.trade-tab-pane').forEach(p => p.style.display = 'none');
      this.classList.add('active');
      const pane = document.getElementById(target);
      if (pane) pane.style.display = 'block';
    });
  });

  // ---- Chat: Enter to send ----
  const chatInput = document.getElementById('chatInput');
  if (chatInput) {
    chatInput.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.closest('form').submit();
      }
    });
  }

  // ---- Scroll chat to bottom ----
  const chatMessages = document.querySelector('.chat-messages');
  if (chatMessages) {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // ---- Upload preview ----
  const photoInput = document.getElementById('photoInput');
  const uploadPreview = document.getElementById('uploadPreview');
  const uploadZone = document.getElementById('uploadZone');

  if (photoInput && uploadPreview) {
    photoInput.addEventListener('change', function () {
      showPreviews(this.files);
    });
  }

  if (uploadZone) {
    uploadZone.addEventListener('click', () => photoInput && photoInput.click());
    uploadZone.addEventListener('dragover', e => { e.preventDefault(); uploadZone.classList.add('drag-over'); });
    uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('drag-over'));
    uploadZone.addEventListener('drop', e => {
      e.preventDefault();
      uploadZone.classList.remove('drag-over');
      if (photoInput && e.dataTransfer.files.length) {
        photoInput.files = e.dataTransfer.files;
        showPreviews(e.dataTransfer.files);
      }
    });
  }

  function showPreviews(files) {
    if (!uploadPreview) return;
    uploadPreview.innerHTML = '';
    Array.from(files).forEach(file => {
      if (!file.type.startsWith('image/')) return;
      const reader = new FileReader();
      reader.onload = e => {
        const div = document.createElement('div');
        div.className = 'upload-preview-item';
        div.innerHTML = '<img src="' + e.target.result + '" alt=""/>';
        uploadPreview.appendChild(div);
      };
      reader.readAsDataURL(file);
    });
  }

  // ---- Avatar preview on edit profile ----
  const avatarInput = document.getElementById('avatarInput');
  const avatarPreview = document.getElementById('avatarPreview');
  if (avatarInput && avatarPreview) {
    avatarInput.addEventListener('change', function () {
      const file = this.files[0];
      if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = e => avatarPreview.src = e.target.result;
        reader.readAsDataURL(file);
      }
    });
  }

});

function escapeHtml(str) {
  const d = document.createElement('div');
  d.appendChild(document.createTextNode(str));
  return d.innerHTML;
}
