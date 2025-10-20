document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('mh-form');
  if (!form) return;

  form.addEventListener('submit', (e) => {
    const requiredIds = ['name', 'age', 'mood', 'sleep', 'stress',
      ...Array.from({length:9}, (_,i)=>`phq9_${i+1}`),
      ...Array.from({length:7}, (_,i)=>`gad7_${i+1}`),
      'exercise_days','caffeine_cups','screen_hours','support_level'];
    let valid = true;
    let firstInvalid = null;
    const banner = document.getElementById('errorBanner');
    requiredIds.forEach((id) => {
      const el = document.getElementById(id) || document.querySelector(`[name="${id}"]`);
      if (!el) return;
      const value = (el.value || '').trim();
      if (!value) {
        el.setAttribute('aria-invalid', 'true');
        el.classList.add('invalid');
        if (!firstInvalid) firstInvalid = el;
        valid = false;
      } else {
        el.removeAttribute('aria-invalid');
        el.classList.remove('invalid');
      }
    });
    const submitBtn = document.getElementById('submitBtn');
    if (!valid) {
      e.preventDefault();
      if (banner) banner.classList.add('show');
      if (firstInvalid && typeof firstInvalid.focus === 'function') firstInvalid.focus();
      return;
    }
    if (banner) banner.classList.remove('show');
    if (submitBtn) {
      submitBtn.classList.add('loading');
    }
  });
});


