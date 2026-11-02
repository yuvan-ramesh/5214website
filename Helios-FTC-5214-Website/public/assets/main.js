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
  // Featured photos are links to the outreach story, not decorative slides.
  const gallery = document.querySelector('[data-hero-gallery]');
  if (gallery) {
    const slides = [...gallery.querySelectorAll('[data-slide]')];
    const dots = [...gallery.querySelectorAll('[data-gallery-dot]')];
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    let active = 0;
    let interval;
    const show = (next) => {
      active = (next + slides.length) % slides.length;
      slides.forEach((slide, index) => {
        const selected = index === active;
        slide.hidden = !selected;
        slide.classList.toggle('is-active', selected);
      });
      const captionLink = gallery.querySelector('[data-gallery-caption-link]');
      const captionTitle = gallery.querySelector('[data-gallery-caption-title]');
      const captionSubtitle = gallery.querySelector('[data-gallery-caption-subtitle]');
      if (slides[active] && captionLink) {
        captionLink.href = slides[active].getAttribute('href');
        if (captionTitle) captionTitle.textContent = slides[active].dataset.title || '';
        if (captionSubtitle) captionSubtitle.textContent = slides[active].dataset.subtitle || '';
      }
      dots.forEach((dot, index) => {
        const selected = index === active;
        dot.classList.toggle('is-active', selected);
        if (selected) dot.setAttribute('aria-current', 'true');
        else dot.removeAttribute('aria-current');
      });
    };
    const pause = () => { if (interval) clearInterval(interval); interval = undefined; };
    const play = () => {
      pause();
      if (!prefersReducedMotion.matches && !document.hidden && !gallery.matches(':hover') && !gallery.contains(document.activeElement)) {
        interval = setInterval(() => show(active + 1), 5500);
      }
    };
    gallery.querySelector('[data-gallery-previous]')?.addEventListener('click', () => { show(active - 1); play(); });
    gallery.querySelector('[data-gallery-next]')?.addEventListener('click', () => { show(active + 1); play(); });
    dots.forEach((dot, index) => dot.addEventListener('click', () => { show(index); play(); }));
    gallery.addEventListener('mouseenter', pause);
    gallery.addEventListener('mouseleave', play);
    gallery.addEventListener('focusin', pause);
    gallery.addEventListener('focusout', () => requestAnimationFrame(play));
    document.addEventListener('visibilitychange', play);
    if (prefersReducedMotion.addEventListener) prefersReducedMotion.addEventListener('change', play);
    show(0);
    play();
  }
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
