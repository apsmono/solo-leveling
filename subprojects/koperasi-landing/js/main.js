/**
 * Koperasi KKS Landing Page — Main JavaScript
 * Handles mobile navigation toggle and smooth scroll.
 */

(function () {
  'use strict';

  // === Mobile Navigation Toggle ===
  const navToggle = document.getElementById('nav-toggle');
  const navMenu = document.getElementById('nav-menu');

  if (navToggle && navMenu) {
    navToggle.addEventListener('click', function () {
      navMenu.classList.toggle('active');
    });

    // Close menu when a link is clicked
    navMenu.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        navMenu.classList.remove('active');
      });
    });
  }

  // === Navbar Scroll Effect ===
  const navbar = document.getElementById('navbar');

  function onScroll() {
    if (window.scrollY > 10) {
      navbar.style.boxShadow = '0 2px 8px rgba(0,0,0,0.06)';
    } else {
      navbar.style.boxShadow = 'none';
    }
  }

  window.addEventListener('scroll', onScroll);
  onScroll();

  // === Contact Form Handler (uncomment if using custom form) ===
  /*
  const contactForm = document.getElementById('contact-form');
  const contactStatus = document.getElementById('contact-status');

  if (contactForm) {
    contactForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      contactStatus.textContent = 'Mengirim...';
      contactStatus.className = 'form-status';

      const formData = new FormData(contactForm);
      const data = Object.fromEntries(formData.entries());

      try {
        const response = await fetch(contactForm.action, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        });

        if (response.ok) {
          contactStatus.textContent = 'Pesan terkirim! Kami akan menghubungi Anda segera.';
          contactStatus.className = 'form-status success';
          contactForm.reset();
        } else {
          throw new Error('Server error');
        }
      } catch (err) {
        contactStatus.textContent = 'Gagal mengirim. Silakan coba lagi atau hubungi kami langsung.';
        contactStatus.className = 'form-status error';
      }
    });
  }
  */
})();
