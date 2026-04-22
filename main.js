/* ============================================
   Strong Tower AI — Main JS
   ============================================ */

// ── Navbar scroll effect ──────────────────────
const navbar = document.getElementById('navbar');
if (navbar) {
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 20);
  });
}

// ── Mobile nav toggle ─────────────────────────
const navToggle = document.getElementById('navToggle');
const mobileMenu = document.getElementById('mobileMenu');
if (navToggle && mobileMenu) {
  navToggle.addEventListener('click', () => {
    const open = mobileMenu.classList.toggle('open');
    navToggle.setAttribute('aria-expanded', open);
    const spans = navToggle.querySelectorAll('span');
    if (open) {
      spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
      spans[1].style.opacity = '0';
      spans[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
    } else {
      spans[0].style.transform = '';
      spans[1].style.opacity = '';
      spans[2].style.transform = '';
    }
  });
  document.addEventListener('click', (e) => {
    if (!navbar.contains(e.target) && !mobileMenu.contains(e.target)) {
      mobileMenu.classList.remove('open');
    }
  });
}

// ── Scroll-triggered fade-up animations ──────
const fadeEls = document.querySelectorAll('.fade-up');
if (fadeEls.length) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        const delay = entry.target.dataset.delay || 0;
        setTimeout(() => entry.target.classList.add('visible'), delay);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  // Stagger cards in the same grid
  document.querySelectorAll('.services-grid, .testimonials-grid, .values-grid, .team-grid, .why-visual, .process-steps').forEach(grid => {
    grid.querySelectorAll('.fade-up').forEach((el, i) => {
      el.dataset.delay = i * 80;
    });
  });

  fadeEls.forEach(el => observer.observe(el));
}

// ── Lead capture form ─────────────────────────
const leadForm = document.getElementById('leadForm');
const formSuccess = document.getElementById('formSuccess');
if (leadForm) {
  leadForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const required = leadForm.querySelectorAll('[required]');
    let valid = true;
    required.forEach(field => {
      if (!field.value.trim()) {
        valid = false;
        field.style.borderColor = '#E53935';
        field.addEventListener('input', () => field.style.borderColor = '', { once: true });
      }
    });
    if (!valid) return;

    // Simulate form submission
    const btn = leadForm.querySelector('.form-submit');
    btn.textContent = 'Sending...';
    btn.disabled = true;

    setTimeout(() => {
      leadForm.style.display = 'none';
      if (formSuccess) formSuccess.style.display = 'block';
    }, 1000);
  });
}

// ── Calendar booking widget ───────────────────
const bookingTimes = document.getElementById('bookingTimes');
const confirmBooking = document.getElementById('confirmBooking');
const bookingStep1 = document.getElementById('bookingStep1');
const bookingStep2 = document.getElementById('bookingStep2');
const bookingStep3 = document.getElementById('bookingStep3');
const selectedTimeDisplay = document.getElementById('selectedTimeDisplay');
const submitBooking = document.getElementById('submitBooking');
const backToTimes = document.getElementById('backToTimes');
const bookingConfirmTime = document.getElementById('bookingConfirmTime');

let selectedTime = null;

if (bookingTimes) {
  bookingTimes.querySelectorAll('.booking-time-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      bookingTimes.querySelectorAll('.booking-time-btn').forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
      selectedTime = btn.dataset.time;
      confirmBooking.style.display = 'flex';
    });
  });
}

if (confirmBooking) {
  confirmBooking.addEventListener('click', () => {
    if (!selectedTime) return;
    bookingStep1.style.display = 'none';
    bookingStep2.style.display = 'block';
    selectedTimeDisplay.textContent = selectedTime;
  });
}

if (backToTimes) {
  backToTimes.addEventListener('click', () => {
    bookingStep2.style.display = 'none';
    bookingStep1.style.display = 'block';
  });
}

if (submitBooking) {
  submitBooking.addEventListener('click', () => {
    const name = document.getElementById('bookingName');
    const email = document.getElementById('bookingEmail');
    if (!name.value.trim() || !email.value.trim()) {
      if (!name.value.trim()) name.style.borderColor = '#E53935';
      if (!email.value.trim()) email.style.borderColor = '#E53935';
      return;
    }
    submitBooking.textContent = 'Confirming...';
    submitBooking.disabled = true;
    setTimeout(() => {
      bookingStep2.style.display = 'none';
      bookingStep3.style.display = 'block';
      if (bookingConfirmTime) bookingConfirmTime.textContent = selectedTime;
    }, 900);
  });
}

// ── FAQ accordion arrow rotation ─────────────
document.querySelectorAll('details').forEach(detail => {
  detail.addEventListener('toggle', () => {
    const arrow = detail.querySelector('summary svg');
    if (arrow) {
      arrow.style.transform = detail.open ? 'rotate(180deg)' : '';
      arrow.style.transition = 'transform 0.25s ease';
    }
  });
});
