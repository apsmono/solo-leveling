/**
 * Wedding Invitation — Main JavaScript
 * Handles countdown, mobile navigation, RSVP form, and summary display.
 */

(function () {
  'use strict';

  // === Configuration ===
  const WEDDING_DATE = new Date('2026-06-01T00:00:00+07:00');
  const RSVP_DRAFT_KEY = 'wedding-invitation.rsvp-draft';
  const RSVP_SUBMITTED_KEY = 'wedding-invitation.rsvp-submitted';

  const defaultRsvpForm = {
    guestName: '',
    email: '',
    attendance: 'joyfully-accepts',
    guestCount: '1',
    mealPreference: 'chef-selection',
    dietaryNotes: '',
    songRequest: '',
  };

  const attendanceLabels = {
    'joyfully-accepts': 'InsyaAllah hadir',
    'regretfully-declines': 'Dengan hormat berhalangan hadir',
  };

  const mealLabels = {
    'chef-selection': 'Menu pilihan panitia',
    vegetarian: 'Menu vegetarian',
    vegan: 'Menu vegan',
  };

  // === Utilities ===
  function pad(n) {
    return String(n).padStart(2, '0');
  }

  function readStoredRsvp() {
    try {
      const raw = localStorage.getItem(RSVP_DRAFT_KEY);
      return raw ? { ...defaultRsvpForm, ...JSON.parse(raw) } : null;
    } catch {
      return null;
    }
  }

  function readStoredSubmission() {
    try {
      const raw = localStorage.getItem(RSVP_SUBMITTED_KEY);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      return {
        formData: { ...defaultRsvpForm, ...(parsed.formData || parsed) },
        submissionMode: parsed.submissionMode || 'local',
      };
    } catch {
      return null;
    }
  }

  // === Countdown Timer ===
  const els = {
    days: document.getElementById('days'),
    hours: document.getElementById('hours'),
    minutes: document.getElementById('minutes'),
    seconds: document.getElementById('seconds'),
  };

  function updateCountdown() {
    const now = Date.now();
    const diff = Math.max(WEDDING_DATE.getTime() - now, 0);
    const totalSeconds = Math.floor(diff / 1000);

    const days = Math.floor(totalSeconds / 86400);
    const hours = Math.floor((totalSeconds % 86400) / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;

    if (els.days) els.days.textContent = pad(days);
    if (els.hours) els.hours.textContent = pad(hours);
    if (els.minutes) els.minutes.textContent = pad(minutes);
    if (els.seconds) els.seconds.textContent = pad(seconds);
  }

  updateCountdown();
  setInterval(updateCountdown, 1000);

  // === Mobile Navigation ===
  const navToggle = document.getElementById('nav-toggle');
  const navMenu = document.getElementById('nav-menu');

  if (navToggle && navMenu) {
    navToggle.addEventListener('click', function () {
      navMenu.classList.toggle('active');
    });

    navMenu.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        navMenu.classList.remove('active');
      });
    });
  }

  // === Navbar Scroll Shadow ===
  const navbar = document.getElementById('navbar');
  function onScroll() {
    if (!navbar) return;
    if (window.scrollY > 10) {
      navbar.style.boxShadow = '0 2px 12px rgba(55,41,24,0.08)';
    } else {
      navbar.style.boxShadow = 'none';
    }
  }
  window.addEventListener('scroll', onScroll);
  onScroll();

  // === RSVP Form ===
  const rsvpForm = document.getElementById('rsvp-form');
  const thanksSection = document.getElementById('thanks');
  const summaryGrid = document.getElementById('summary-grid');
  const rsvpSection = document.getElementById('rsvp');

  // Populate form from draft
  const draft = readStoredRsvp();
  if (draft) {
    Object.keys(draft).forEach(function (key) {
      const el = document.getElementById(key);
      if (el) el.value = draft[key];
    });
  }

  // Auto-save draft on input
  if (rsvpForm) {
    rsvpForm.addEventListener('input', function () {
      const data = {};
      const formData = new FormData(rsvpForm);
      formData.forEach(function (value, key) {
        data[key] = value;
      });
      localStorage.setItem(RSVP_DRAFT_KEY, JSON.stringify(data));
    });

    rsvpForm.addEventListener('submit', function (e) {
      e.preventDefault();

      const formData = new FormData(rsvpForm);
      const data = Object.fromEntries(formData.entries());

      // Validation
      const errors = {};
      if (!data.guestName || !data.guestName.trim()) {
        errors.guestName = 'Mohon isi nama lengkap Anda.';
      }
      if (!data.email || !data.email.trim() || !data.email.includes('@')) {
        errors.email = 'Mohon isi alamat email yang valid.';
      }

      // Clear previous errors
      document.querySelectorAll('.error-msg').forEach(function (el) {
        el.textContent = '';
      });

      if (Object.keys(errors).length > 0) {
        Object.keys(errors).forEach(function (key) {
          const errorEl = document.getElementById('error-' + key);
          if (errorEl) errorEl.textContent = errors[key];
        });
        return;
      }

      // Normalize guest count if declining
      if (data.attendance === 'regretfully-declines') {
        data.guestCount = '0';
      }

      // Save submission
      const submission = {
        formData: data,
        submissionMode: 'local',
      };
      localStorage.setItem(RSVP_SUBMITTED_KEY, JSON.stringify(submission));
      localStorage.removeItem(RSVP_DRAFT_KEY);

      // Show thanks
      if (rsvpSection) rsvpSection.style.display = 'none';
      if (thanksSection) {
        thanksSection.style.display = 'block';
        thanksSection.scrollIntoView({ behavior: 'smooth' });
      }
      renderSummary(data);
    });
  }

  function renderSummary(data) {
    if (!summaryGrid) return;
    summaryGrid.innerHTML = [
      { label: 'Nama', value: data.guestName },
      { label: 'Email', value: data.email },
      { label: 'Kehadiran', value: attendanceLabels[data.attendance] || data.attendance },
      { label: 'Jumlah Tamu', value: data.guestCount },
      { label: 'Menu', value: mealLabels[data.mealPreference] || data.mealPreference },
      { label: 'Catatan Makanan', value: data.dietaryNotes || 'Tidak ada catatan' },
      { label: 'Permintaan Lagu', value: data.songRequest || 'Tidak ada' },
    ]
      .map(function (item) {
        return (
          '<article>' +
          '<span>' + escapeHtml(item.label) + '</span>' +
          '<strong>' + escapeHtml(item.value) + '</strong>' +
          '</article>'
        );
      })
      .join('');
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // If already submitted, show thanks
  const existingSubmission = readStoredSubmission();
  if (existingSubmission && rsvpSection && thanksSection) {
    rsvpSection.style.display = 'none';
    thanksSection.style.display = 'block';
    renderSummary(existingSubmission.formData);
  }
})();
