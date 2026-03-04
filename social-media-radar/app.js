import emailData from './emailData.js';

(() => {
  'use strict';

  const API_BASE = 'http://localhost:8000';

  let democrats = [];
  let republicans = [];
  let searchQuery = '';
  let currentPerson = null;
  let currentSide = null;

  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  async function loadData() {
    const [demRes, repRes] = await Promise.all([
      fetch('data/democrats.json'),
      fetch('data/republicans.json'),
    ]);
    democrats = await demRes.json();
    republicans = await repRes.json();
    renderAll();
  }

  function getInitials(name) {
    return name
      .split(' ')
      .map((w) => w[0])
      .filter(Boolean)
      .slice(0, 2)
      .join('')
      .toUpperCase();
  }

  function getInfluenceScore(person) {
    const scores = { high: 9.0, medium: 7.5, low: 5.0 };
    const base = scores[person.priority] || 5.0;
    const hash = person.name.length * 0.1;
    return (base + (hash % 1)).toFixed(1);
  }

  function getInstagramHandle(person) {
    return person.x_handle.replace('@', '').toLowerCase();
  }

  function filterList(list) {
    if (!searchQuery) return list;
    const q = searchQuery.toLowerCase();
    return list.filter(
      (p) =>
        p.name.toLowerCase().includes(q) ||
        p.role.toLowerCase().includes(q) ||
        p.x_handle.toLowerCase().includes(q)
    );
  }

  function getPhotoUrl(person) {
    const handle = person.x_handle.replace('@', '');
    return `https://unavatar.io/x/${handle}`;
  }

  function createAvatarItem(person, side) {
    const item = document.createElement('div');
    item.className = 'avatar-item';

    const showBadge = person.priority === 'high';
    const photoUrl = getPhotoUrl(person);

    item.innerHTML = `
      ${showBadge ? '<span class="badge-priority">Top Priority</span>' : ''}
      <div class="avatar-circle">
        <img
          src="${photoUrl}"
          alt="${person.name}"
          class="avatar-photo"
          onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';"
          loading="lazy"
        />
        <span class="avatar-fallback" style="display:none;">${getInitials(person.name)}</span>
      </div>
      <span class="avatar-name">${person.name}</span>
    `;

    item.addEventListener('click', () => openPersonModal(person, side));
    return item;
  }

  function renderAll() {
    renderGrid('grid-antiwar', filterList(democrats), 'antiwar');
    renderGrid('grid-prowar', filterList(republicans), 'prowar');
  }

  function renderGrid(gridId, list, side) {
    const grid = $(`#${gridId}`);
    grid.innerHTML = '';

    if (list.length === 0) {
      grid.innerHTML = '<p style="color:#999;text-align:center;padding:20px;">No results</p>';
      return;
    }

    const highPriority = list.filter((p) => p.priority === 'high');
    const rest = list.filter((p) => p.priority !== 'high');
    const sorted = [...highPriority, ...rest];

    const fragment = document.createDocumentFragment();
    sorted.forEach((person) => {
      fragment.appendChild(createAvatarItem(person, side));
    });
    grid.appendChild(fragment);
  }

  // Search
  let searchTimeout;
  $('#search-input').addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      searchQuery = e.target.value.trim();
      renderAll();
    }, 200);
  });

  // ============ Person Modal ============

  function openPersonModal(person, side) {
    currentPerson = person;
    currentSide = side;

    const overlay = $('#modal-overlay');
    const colorClass = side === 'antiwar' ? 'green' : 'red';

    const avatar = $('#modal-avatar');
    avatar.className = `modal-avatar ${colorClass}`;
    const photoUrl = getPhotoUrl(person);
    avatar.innerHTML = `
      <img
        src="${photoUrl}"
        alt="${person.name}"
        class="modal-photo"
        onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';"
      />
      <span class="modal-initials-fallback" style="display:none;">${getInitials(person.name)}</span>
    `;
    $('#modal-name').textContent = person.name;
    $('#modal-score').textContent = `Influence Score: ${getInfluenceScore(person)}`;

    const xHandle = person.x_handle;
    const xUrl = `https://x.com/${xHandle.replace('@', '')}`;
    $('#modal-x-link').href = xUrl;
    $('#modal-x-handle').textContent = xHandle;

    const instaHandle = `@${getInstagramHandle(person)}`;
    const instaUrl = `https://instagram.com/${instaHandle.replace('@', '')}`;
    $('#modal-insta-link').href = instaUrl;
    $('#modal-insta-handle').textContent = instaHandle;

    $('#modal-status').textContent = '';

    overlay.classList.add('active');
  }

  function closePersonModal() {
    $('#modal-overlay').classList.remove('active');
  }

  $('#modal-overlay').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) closePersonModal();
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closePersonModal();
      closeEmailModal();
    }
  });

  // X link click status
  $('#modal-x-link').addEventListener('click', () => {
    $('#modal-status').textContent = 'Redirecting to external account...';
  });

  $('#modal-insta-link').addEventListener('click', () => {
    $('#modal-status').textContent = 'Redirecting to external account...';
  });

  // Email button -> open email modal
  $('#modal-email-btn').addEventListener('click', () => {
    closePersonModal();
    openEmailModal();
  });

  // ============ Email Modal ============

  function openEmailModal() {
    if (!currentPerson) return;
    if (currentSide === 'prowar') {
      $('#email-topic').value = 'regime_change';
    } else {
      $('#email-topic').value = 'no_war';
    }
    $('#email-subject-box').style.display = 'none';
    $('#email-body-text').style.display = 'none';
    $('#email-actions').style.display = 'none';
    $('#regenerate-btn').textContent = 'Generate Email';
    $('#email-modal-overlay').classList.add('active');
  }

  function closeEmailModal() {
    $('#email-modal-overlay').classList.remove('active');
  }

  $('#email-modal-overlay').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) closeEmailModal();
  });

  async function generateAndShowEmail() {
    if (!currentPerson) return;

    const topic = $('#email-topic').value;
    const userName = $('#user-name').value.trim();
    const userCity = $('#user-city').value.trim();
    const genBtn = $('#regenerate-btn');
    const bodyBox = $('#email-body-text');
    const subjectBox = $('#email-subject-text');
    const subjectBoxWrap = $('#email-subject-box');
    const actionsBox = $('#email-actions');

    const gmailBtn = $('#gmail-btn');
    const outlookBtn = $('#outlook-btn');
    const defaultEmailBtn = $('#default-email-btn');

    genBtn.disabled = true;
    genBtn.textContent = 'Generating...';
    subjectBoxWrap.style.display = 'block';
    bodyBox.style.display = 'block';
    bodyBox.textContent = 'Generating a unique email...';
    subjectBox.textContent = '';
    actionsBox.style.display = 'none';

    setTimeout(() => {
      try {
        const currentType = currentSide === 'prowar' ? 'supporters' : 'opponents';
        const data = emailData[currentType] || emailData['supporters'];

        const getRandom = (arr) => arr[Math.floor(Math.random() * arr.length)];
        const subject = getRandom(data.subjects);
        const greeting = getRandom(data.greetings);
        const opening = getRandom(data.openings);
        const context = getRandom(data.contexts);
        const ask = getRandom(data.asks);
        const closing = getRandom(data.closings);

        let identityString = "";
        if (userName && userCity) {
          identityString = `\n\n- ${userName}, from ${userCity}`;
        } else if (userName) {
          identityString = `\n\n- ${userName}`;
        } else if (userCity) {
          identityString = `\n\n- A concerned resident of ${userCity}`;
        }

        const body = `${greeting}\n\n${opening} ${context} ${ask}\n\n${closing}${identityString}`;

        subjectBox.textContent = subject;
        bodyBox.textContent = body;

        const encodedSubject = encodeURIComponent(subject);
        const encodedBody = encodeURIComponent(body);
        const encodedTo = encodeURIComponent(currentPerson.email || '');

        gmailBtn.href = `https://mail.google.com/mail/?view=cm&fs=1&to=${encodedTo}&su=${encodedSubject}&body=${encodedBody}`;
        outlookBtn.href = `https://outlook.office.com/mail/deeplink/compose?to=${encodedTo}&subject=${encodedSubject}&body=${encodedBody}`;
        defaultEmailBtn.href = `mailto:${currentPerson.email || ''}?subject=${encodedSubject}&body=${encodedBody}`;

        actionsBox.style.display = 'flex';
      } catch (e) {
        subjectBox.textContent = 'Generation Error';
        bodyBox.textContent = 'Could not generate email.';
      } finally {
        genBtn.disabled = false;
        genBtn.textContent = 'Regenerate';
      }
    }, 400);
  }

  // Email generation is 100% server-side via LLM — no local templates

  // Copy email
  $('#copy-email-btn').addEventListener('click', async () => {
    const subject = $('#email-subject-text').textContent;
    const body = $('#email-body-text').textContent;
    const fullText = `Subject: ${subject}\n\n${body}`;

    try {
      await navigator.clipboard.writeText(fullText);
      const btn = $('#copy-email-btn');
      btn.textContent = 'Copied!';
      setTimeout(() => {
        btn.textContent = 'Copy to Clipboard';
      }, 2000);
    } catch {
      showToast('Copy failed — select and copy manually');
    }
  });



  // Regenerate
  $('#regenerate-btn').addEventListener('click', () => {
    generateAndShowEmail();
  });

  function showToast(message) {
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
      toast.classList.add('fade-out');
      setTimeout(() => toast.remove(), 300);
    }, 2500);
  }

  loadData();
})();
