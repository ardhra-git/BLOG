const API = window.location.origin;
let pendingDeleteId = null;

// ── LOAD POSTS ────────────────────────────────────────────────
async function loadPosts() {
  try {
    const res  = await fetch(`${API}/posts`);
    const data = await res.json();
    renderPosts(data.posts);
  } catch {
    document.getElementById('postsGrid').innerHTML =
      '<p class="state-msg">⚠️ Cannot connect to server. Start the backend first.</p>';
  }
}

// ── RENDER POSTS ──────────────────────────────────────────────
function renderPosts(posts) {
  const grid  = document.getElementById('postsGrid');
  const count = document.getElementById('postCount');
  count.textContent = `${posts.length} post${posts.length !== 1 ? 's' : ''}`;

  if (!posts.length) {
    grid.innerHTML = '<p class="state-msg">No posts yet — click the <strong>+</strong> button to write your first one!</p>';
    return;
  }

  grid.innerHTML = posts.map((p, i) => `
    <div class="post-card" style="animation-delay:${i * 0.06}s" id="card-${p.id}">
      <span class="card-tag">${p.tag}</span>
      <h3 class="card-title" onclick="openModal(${p.id})">${p.title}</h3>
      <p class="card-excerpt">${p.excerpt}</p>
      <p class="card-meta">${formatDate(p.created_at)} &nbsp;·&nbsp; ${p.read_time}</p>
      <div class="card-actions">
        <button class="btn-read" onclick="openModal(${p.id})">Read →</button>
        <button class="btn-icon edit" onclick="editPost(${p.id})" title="Edit post">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
        </button>
        <button class="btn-icon delete" onclick="confirmDelete(${p.id})" title="Delete post">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
            <path d="M10 11v6M14 11v6"/>
            <path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>
          </svg>
        </button>
      </div>
    </div>
  `).join('');
}

// ── FORMAT DATE ───────────────────────────────────────────────
function formatDate(str) {
  if (!str) return '';
  return new Date(str).toLocaleDateString('en-US', { year:'numeric', month:'short', day:'numeric' });
}

// ── OPEN DRAWER (NEW POST) ────────────────────────────────────
function openDrawer() {
  resetDrawer();
  document.getElementById('drawerTitle').textContent = 'New Post';
  document.getElementById('drawer').classList.add('open');
  document.getElementById('drawerOverlay').classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeDrawer() {
  document.getElementById('drawer').classList.remove('open');
  document.getElementById('drawerOverlay').classList.remove('active');
  document.body.style.overflow = '';
  resetDrawer();
}

function resetDrawer() {
  document.getElementById('editId').value       = '';
  document.getElementById('postTag').value      = '';
  document.getElementById('postTitle').value    = '';
  document.getElementById('postExcerpt').value  = '';
  document.getElementById('postBody').value     = '';
  document.getElementById('postReadTime').value = '';
  document.getElementById('drawerStatus').textContent = '';
  document.querySelector('.btn-save').textContent = 'Publish Post';
}

// ── EDIT POST (fill drawer with existing data) ─────────────────
async function editPost(id) {
  try {
    const res  = await fetch(`${API}/posts/${id}`);
    const post = await res.json();

    document.getElementById('editId').value          = post.id;
    document.getElementById('postTag').value         = post.tag;
    document.getElementById('postTitle').value       = post.title;
    document.getElementById('postExcerpt').value     = post.excerpt;
    document.getElementById('postBody').value        = post.body;
    document.getElementById('postReadTime').value    = post.read_time;
    document.getElementById('drawerTitle').textContent = 'Edit Post';
    document.querySelector('.btn-save').textContent    = 'Update Post';

    document.getElementById('drawer').classList.add('open');
    document.getElementById('drawerOverlay').classList.add('active');
    document.body.style.overflow = 'hidden';
  } catch {
    alert('Could not load post.');
  }
}

// ── SAVE POST (create or update) ──────────────────────────────
async function savePost() {
  const id       = document.getElementById('editId').value;
  const tag      = document.getElementById('postTag').value.trim();
  const title    = document.getElementById('postTitle').value.trim();
  const excerpt  = document.getElementById('postExcerpt').value.trim();
  const body     = document.getElementById('postBody').value.trim();
  const readTime = document.getElementById('postReadTime').value.trim() || '3 min read';
  const status   = document.getElementById('drawerStatus');

  if (!tag || !title || !excerpt || !body) {
    status.textContent = '⚠️ Please fill in all fields.';
    status.style.color = '#dc2626';
    return;
  }

  const payload = { tag, title, excerpt, body, read_time: readTime };
  const url     = id ? `${API}/posts/${id}` : `${API}/posts`;
  const method  = id ? 'PUT' : 'POST';

  try {
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      closeDrawer();
      loadPosts();
    } else {
      const err = await res.json();
      status.textContent = '✗ ' + (err.detail || 'Error saving post.');
      status.style.color = '#dc2626';
    }
  } catch {
    status.textContent = '✗ Cannot reach server.';
    status.style.color = '#dc2626';
  }
}

// ── DELETE FLOW ───────────────────────────────────────────────
function confirmDelete(id) {
  pendingDeleteId = id;
  document.getElementById('confirmOverlay').classList.add('active');
}

function closeConfirm() {
  pendingDeleteId = null;
  document.getElementById('confirmOverlay').classList.remove('active');
}

document.getElementById('confirmYes').addEventListener('click', async () => {
  if (!pendingDeleteId) return;
  try {
    await fetch(`${API}/posts/${pendingDeleteId}`, { method: 'DELETE' });
    closeConfirm();
    loadPosts();
  } catch {
    alert('Could not delete post.');
  }
});

// ── READ MODAL ────────────────────────────────────────────────
async function openModal(id) {
  try {
    const res  = await fetch(`${API}/posts/${id}`);
    const post = await res.json();
    const paras = post.body.split('\n').filter(p => p.trim()).map(p => `<p>${p}</p>`).join('');

    document.getElementById('modalContent').innerHTML = `
      <p class="modal-tag">${post.tag}</p>
      <h2>${post.title}</h2>
      <p class="modal-meta">${formatDate(post.created_at)} &nbsp;·&nbsp; ${post.read_time}</p>
      ${paras}
    `;
    document.getElementById('modalOverlay').classList.add('active');
    document.body.style.overflow = 'hidden';
  } catch {
    alert('Could not load post.');
  }
}

function closeModal() {
  document.getElementById('modalOverlay').classList.remove('active');
  document.body.style.overflow = '';
}

// ── CONTACT FORM ──────────────────────────────────────────────
document.getElementById('contactForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  const status = document.getElementById('contactStatus');
  const btn    = this.querySelector('.btn-send');
  const data   = new FormData();
  data.append('name',    document.getElementById('cName').value);
  data.append('email',   document.getElementById('cEmail').value);
  data.append('message', document.getElementById('cMessage').value);

  btn.textContent = 'Sending…';
  btn.disabled = true;

  try {
    const res = await fetch(`${API}/contact`, { method: 'POST', body: data });
    const out = await res.json();
    if (res.ok) {
      status.textContent = '✓ Message sent!';
      status.style.color = '#4ade80';
      this.reset();
    } else {
      status.textContent = '✗ ' + (out.detail || 'Failed to send.');
      status.style.color = '#f87171';
    }
  } catch {
    status.textContent = '✗ Cannot reach server.';
    status.style.color = '#f87171';
  } finally {
    btn.textContent = 'Send Message';
    btn.disabled = false;
  }
});

// ── KEYBOARD ─────────────────────────────────────────────────
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') { closeModal(); closeDrawer(); closeConfirm(); }
});

// ── INIT ──────────────────────────────────────────────────────
loadPosts();
