// Progressive enhancement for score cards
function initScoreCards() {
  const cards = document.querySelectorAll('.score-card');
  cards.forEach(card => {
    const score = card.querySelector('.score');
    if (score) {
      const finalScore = parseInt(score.textContent);
      score.textContent = '0';
      let currentScore = 0;

      const interval = setInterval(() => {
        currentScore++;
        score.textContent = currentScore;
        if (currentScore >= finalScore) {
          clearInterval(interval);
        }
      }, 30);
    }
  });
}

// Smooth scroll for anchor links
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      document.querySelector(this.getAttribute('href'))?.scrollIntoView({
        behavior: 'smooth'
      });
    });
  });
}

// Initialize intersection observer for animations
function initIntersectionObserver() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate');
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.score-card, .card').forEach(element => {
    observer.observe(element);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  // Initialize enhanced features
  initSmoothScroll();
  initIntersectionObserver();

  // Initialize score cards if we're on a results page
  if (document.querySelector('.score-card')) {
    initScoreCards();
  }
  const form = document.getElementById('mh-form');
  // Apply progress widths set in templates using data-width so
  // progress bars render correctly on pages without the form
  // (for example the results page).
  document.querySelectorAll('.progress-fill[data-width]').forEach((el) => {
    const w = el.getAttribute('data-width');
    if (!w) return;
    el.style.width = w + '%';
  });
  if (!form) return;

  form.addEventListener('submit', (e) => {
    const requiredFields = [
      'name', 'age', 'mood', 'sleep', 'stress',
      ...Array.from({ length: 9 }, (_, i) => `phq9_${i + 1}`),
      ...Array.from({ length: 7 }, (_, i) => `gad7_${i + 1}`),
      'exercise_days', 'caffeine_cups', 'screen_hours', 'support_level'
    ];
    let valid = true;
    let firstInvalid = null;
    const banner = document.getElementById('errorBanner');

    requiredFields.forEach((name) => {
      const el = document.querySelector(`[name="${name}"]`);
      if (!el) return;
      const value = (el.value || '').trim();
      // simple emptiness check
      if (!value) {
        el.setAttribute('aria-invalid', 'true');
        el.classList.add('invalid');
        if (!firstInvalid) firstInvalid = el;
        valid = false;
        return;
      }
      // numeric range checks for specific fields
      if (['age', 'sleep', 'stress', 'exercise_days', 'caffeine_cups', 'screen_hours', 'support_level'].includes(name)) {
        const num = Number(value);
        if (Number.isNaN(num)) {
          el.setAttribute('aria-invalid', 'true');
          el.classList.add('invalid');
          if (!firstInvalid) firstInvalid = el;
          valid = false;
          return;
        }
      }
      el.removeAttribute('aria-invalid');
      el.classList.remove('invalid');
    });

    const submitBtn = document.getElementById('submitBtn');
    if (!valid) {
      e.preventDefault();
      if (banner) {
        banner.textContent = 'Please complete all required fields using the provided response options.';
        banner.classList.add('show');
      }
      if (firstInvalid && typeof firstInvalid.focus === 'function') firstInvalid.focus();
      return;
    }
    if (banner) banner.classList.remove('show');
    if (submitBtn) {
      submitBtn.classList.add('loading');
      submitBtn.setAttribute('disabled', 'disabled');
    }
  });
});


