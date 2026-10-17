(() => {
  const menuButton = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.main-nav');
  if (menuButton && nav) {
    const closeMenu = () => { nav.classList.remove('is-open'); menuButton.setAttribute('aria-expanded', 'false'); menuButton.setAttribute('aria-label', 'Open navigation'); };
    menuButton.addEventListener('click', () => {
      const open = !nav.classList.contains('is-open');
      nav.classList.toggle('is-open', open);
      menuButton.setAttribute('aria-expanded', String(open));
      menuButton.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
    });
    nav.querySelectorAll('a').forEach(anchor => anchor.addEventListener('click', closeMenu));
    document.addEventListener('keydown', e => { if (e.key === 'Escape') {closeMenu(); document.querySelectorAll('.season-menu[open]').forEach(d => d.open = false); }});
  }
  const seasonMenu = document.querySelector('.season-menu');
  if (seasonMenu) document.addEventListener('click', e => { if (!seasonMenu.contains(e.target)) seasonMenu.open = false; });
  document.querySelectorAll('[data-year]').forEach(el => el.textContent = new Date().getFullYear());
  const form = document.getElementById('contact-form');
  if (!form) return;
  const feedback = document.getElementById('form-feedback');
  const submitButton = form.querySelector('button[type="submit"]');
  const submitLabel = submitButton.querySelector('.submit-label');
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    feedback.textContent = '';
    feedback.className = 'form-feedback';
    if (!form.reportValidity()) return;
    const fd = new FormData(form);
    const payload = Object.fromEntries(fd.entries());
    submitButton.disabled = true;
    submitLabel.textContent = 'Sending…';
    try {
      const response = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const result = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(result.error || 'Message could not be delivered. Please email us directly.');
      feedback.classList.add('success');
      feedback.textContent = 'Thank you! Your message was sent to the Helios inbox.';
      form.reset();
    } catch (error) {
      feedback.textContent = error.message || 'Something went wrong. Please email us at 5214.helios@gmail.com.';
    } finally {
      submitButton.disabled = false;
      submitLabel.textContent = 'Send message';
    }
  });
})();
