/**
 * Wedding Invitation — Main JavaScript
 * Handles countdown timer and simple interactions.
 */

(function () {
  'use strict';

  // === Configuration ===
  // Ganti tanggal pernikahan Anda di sini (format: YYYY-MM-DDTHH:MM:SS)
  const WEDDING_DATE = new Date('2027-01-01T08:00:00');

  // === Countdown Timer ===
  const els = {
    days: document.getElementById('days'),
    hours: document.getElementById('hours'),
    minutes: document.getElementById('minutes'),
    seconds: document.getElementById('seconds'),
  };

  function pad(n) {
    return String(n).padStart(2, '0');
  }

  function updateCountdown() {
    const now = new Date();
    const diff = WEDDING_DATE - now;

    if (diff <= 0) {
      // Hari H!
      if (els.days) els.days.textContent = '00';
      if (els.hours) els.hours.textContent = '00';
      if (els.minutes) els.minutes.textContent = '00';
      if (els.seconds) els.seconds.textContent = '00';
      return;
    }

    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
    const minutes = Math.floor((diff / (1000 * 60)) % 60);
    const seconds = Math.floor((diff / 1000) % 60);

    if (els.days) els.days.textContent = pad(days);
    if (els.hours) els.hours.textContent = pad(hours);
    if (els.minutes) els.minutes.textContent = pad(minutes);
    if (els.seconds) els.seconds.textContent = pad(seconds);
  }

  // Update immediately and then every second
  updateCountdown();
  setInterval(updateCountdown, 1000);

  // === RSVP Form Handler (uncomment if using custom form) ===
  /*
  const rsvpForm = document.getElementById('rsvp-form');
  const rsvpStatus = document.getElementById('rsvp-status');

  if (rsvpForm) {
    rsvpForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      rsvpStatus.textContent = 'Mengirim...';
      rsvpStatus.className = 'form-status';

      const formData = new FormData(rsvpForm);
      const data = Object.fromEntries(formData.entries());

      try {
        const response = await fetch(rsvpForm.action, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        });

        if (response.ok) {
          rsvpStatus.textContent = 'Terima kasih! Konfirmasi Anda telah tersimpan.';
          rsvpStatus.className = 'form-status success';
          rsvpForm.reset();
        } else {
          throw new Error('Server error');
        }
      } catch (err) {
        rsvpStatus.textContent = 'Gagal mengirim. Silakan coba lagi.';
        rsvpStatus.className = 'form-status error';
      }
    });
  }
  */
})();
