(() => {
  const html = document.documentElement;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const smoothstep = (e0, e1, x) => { const t = clamp((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t); };
  const store = { get: (k) => { try { return sessionStorage.getItem(k); } catch (_) { return null; } }, set: (k, v) => { try { sessionStorage.setItem(k, v); } catch (_) {} } };
  let vh = window.innerHeight;
  let vw = window.innerWidth;
  window.addEventListener('resize', () => { vh = window.innerHeight; vw = window.innerWidth; });

  /* ------------------------------------------------------------ smooth scroll + frame loop */
  let lenis = null;
  if (!reduce && finePointer && window.Lenis) {
    lenis = new window.Lenis({ lerp: 0.095, wheelMultiplier: 1, smoothWheel: true });
    html.classList.add('lenis');
  }
  const ticks = new Set();
  let scrollY = window.scrollY;
  let lastScrollY = scrollY;
  let velocity = 0;
  let lastTime = performance.now();
  const loop = (t) => {
    if (lenis) lenis.raf(t);
    const dt = Math.min(64, t - lastTime) / 1000;
    lastTime = t;
    scrollY = window.scrollY;
    velocity = lerp(velocity, scrollY - lastScrollY, 0.18);
    lastScrollY = scrollY;
    ticks.forEach((fn) => fn(t, dt));
    requestAnimationFrame(loop);
  };
  requestAnimationFrame(loop);

  // run a tick only while its element is near the viewport
  const whenVisible = (el, fn, margin = '20%') => {
    if (!el) return;
    const io = new IntersectionObserver((entries) => entries.forEach((e) => { if (e.isIntersecting) ticks.add(fn); else ticks.delete(fn); }), { rootMargin: `${margin} 0px ${margin} 0px` });
    io.observe(el);
  };

  /* ------------------------------------------------------------ intro (after loader / page transition) */
  let introStarted = false;
  const introQueue = [];
  const startIntro = (delay = 0) => {
    if (introStarted) return;
    introStarted = true;
    setTimeout(() => {
      html.classList.add('is-ready');
      introQueue.splice(0).forEach((fn) => fn());
    }, delay);
  };
  const afterIntro = (fn) => (introStarted && html.classList.contains('is-ready') ? fn() : introQueue.push(fn));

  /* ------------------------------------------------------------ loader (first visit to home) */
  const loader = document.querySelector('.loader');
  const entering = html.classList.contains('is-entering');
  if (loader && html.classList.contains('is-loading') && !reduce) {
    const count = loader.querySelector('[data-loader-count]');
    const imgs = [...document.querySelectorAll('.hero img:not([loading="lazy"])')];
    const total = imgs.length + 1;
    let loaded = 0;
    const bump = () => { loaded += 1; };
    imgs.forEach((img) => { if (img.complete) bump(); else { img.addEventListener('load', bump, { once: true }); img.addEventListener('error', bump, { once: true }); } });
    (document.fonts ? document.fonts.ready : Promise.resolve()).then(bump);
    const start = performance.now();
    let shown = 0;
    const step = (t) => {
      const elapsed = t - start;
      const target = elapsed > 3500 ? 100 : (loaded / total) * 100;
      shown = Math.min(target, (elapsed / 1500) * 100, shown + 2.6);
      count.textContent = Math.round(shown);
      if (shown >= 100) {
        store.set('helios-seen', '1');
        html.classList.add('loader-done');
        startIntro(380);
        setTimeout(() => html.classList.remove('is-loading', 'loader-done'), 1100);
        return;
      }
      requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  } else {
    html.classList.remove('is-loading');
    store.set('helios-seen', '1');
    if (entering && !reduce) {
      try { sessionStorage.removeItem('helios-nav'); } catch (_) {}
      const reveal = () => requestAnimationFrame(() => {
        html.classList.add('is-entered');
        startIntro(250);
        setTimeout(() => html.classList.remove('is-entering', 'is-entered'), 1000);
      });
      Promise.race([document.fonts ? document.fonts.ready : Promise.resolve(), new Promise((r) => setTimeout(r, 700))]).then(reveal);
    } else {
      html.classList.remove('is-entering');
      startIntro(60);
    }
  }

  /* ------------------------------------------------------------ page transitions */
  document.addEventListener('click', (e) => {
    const a = e.target.closest('a');
    if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    if ((a.target && a.target !== '_self') || a.hasAttribute('download')) return;
    const url = new URL(a.href, location.href);
    if (url.origin !== location.origin) return;
    if (/\.(webp|png|jpe?g|svg|pdf)$/i.test(url.pathname)) return;
    if (url.pathname === location.pathname && url.hash) {
      if (lenis) { e.preventDefault(); lenis.scrollTo(url.hash, { offset: -90 }); }
      return;
    }
    if (reduce) return;
    e.preventDefault();
    store.set('helios-nav', '1');
    html.classList.remove('menu-open');
    html.classList.add('is-leaving');
    setTimeout(() => { location.href = url.href; }, 680);
  });
  window.addEventListener('pageshow', (e) => {
    if (e.persisted) html.classList.remove('is-leaving', 'is-entering', 'is-entered', 'menu-open');
  });

  /* ------------------------------------------------------------ header */
  const header = document.querySelector('[data-header]');
  const themed = [...document.querySelectorAll('main [data-theme], .site-footer')];
  let headerY = window.scrollY;
  ticks.add(() => {
    if (!header) return;
    const probe = 34;
    let theme = 'light';
    for (const s of themed) {
      const r = s.getBoundingClientRect();
      if (r.top <= probe && r.bottom > probe) theme = s.classList.contains('site-footer') ? 'dark' : s.dataset.theme;
    }
    header.classList.toggle('on-dark', theme === 'dark');
    header.classList.toggle('is-scrolled', scrollY > 12);
    const dy = scrollY - headerY;
    if (Math.abs(dy) > 4) {
      if (!html.classList.contains('menu-open')) header.classList.toggle('is-hidden', dy > 0 && scrollY > 240);
      headerY = scrollY;
    }
  });

  /* ------------------------------------------------------------ menu */
  const menuBtn = document.querySelector('[data-menu-btn]');
  const menu = document.querySelector('[data-menu]');
  if (menuBtn && menu) {
    menu.setAttribute('inert', '');
    const preview = menu.querySelector('.menu-preview');
    const previewImg = preview && preview.querySelector('img');
    const setMenu = (open) => {
      const r = menuBtn.getBoundingClientRect();
      menu.style.setProperty('--mx', `${r.left + r.width / 2}px`);
      menu.style.setProperty('--my', `${r.top + r.height / 2}px`);
      html.classList.toggle('menu-open', open);
      menuBtn.setAttribute('aria-expanded', String(open));
      if (open) {
        menu.removeAttribute('inert');
        if (lenis) lenis.stop();
        setTimeout(() => { const first = menu.querySelector('.menu-link'); if (first) first.focus({ preventScroll: true }); }, 450);
      } else {
        menu.setAttribute('inert', '');
        if (lenis) lenis.start();
      }
    };
    menuBtn.addEventListener('click', () => setMenu(!html.classList.contains('menu-open')));
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && html.classList.contains('menu-open')) { setMenu(false); menuBtn.focus(); } });
    if (preview && finePointer) {
      let px = vw / 2, py = vh / 2, tx = px, ty = py;
      menu.addEventListener('pointermove', (e) => { tx = e.clientX; ty = e.clientY; });
      menu.querySelectorAll('.menu-link').forEach((link) => {
        const src = link.dataset.img;
        if (src) { const pre = new Image(); pre.src = src; }
        link.addEventListener('pointerenter', () => { if (src) previewImg.src = src; preview.classList.add('is-on'); });
        link.addEventListener('pointerleave', () => preview.classList.remove('is-on'));
      });
      ticks.add(() => {
        if (!html.classList.contains('menu-open')) return;
        px = lerp(px, tx, 0.14); py = lerp(py, ty, 0.14);
        preview.style.setProperty('--px', `${px}px`);
        preview.style.setProperty('--py', `${py}px`);
      });
    }
  }

  /* ------------------------------------------------------------ split headings + image reveals */
  const revealIO = new IntersectionObserver((entries) => entries.forEach((e) => {
    if (!e.isIntersecting) return;
    revealIO.unobserve(e.target);
    afterIntro(() => e.target.classList.add('is-in'));
  }), { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
  document.querySelectorAll('[data-split], [data-reveal-img]').forEach((el) => {
    if (reduce) el.classList.add('is-in'); else revealIO.observe(el);
  });

  /* ------------------------------------------------------------ parallax */
  document.querySelectorAll('[data-parallax]').forEach((el) => {
    if (reduce) return;
    const speed = parseFloat(el.dataset.parallax) || 0.1;
    const host = el.parentElement;
    whenVisible(host, () => {
      const r = host.getBoundingClientRect();
      const off = (r.top + r.height / 2 - vh / 2) * -speed;
      el.style.transform = `translate3d(0, ${off.toFixed(1)}px, 0)`;
    });
  });

  /* ------------------------------------------------------------ count-up numbers */
  const counters = document.querySelectorAll('[data-count]');
  if (counters.length && !reduce) {
    const run = (el) => {
      const target = Number(el.dataset.count);
      const start = performance.now();
      const dur = 1600;
      const step = (now) => {
        const t = clamp((now - start) / dur, 0, 1);
        el.textContent = Math.round(target * (1 - Math.pow(1 - t, 4)));
        if (t < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    };
    const io = new IntersectionObserver((entries) => entries.forEach((e) => {
      if (!e.isIntersecting) return;
      io.unobserve(e.target);
      e.target.textContent = '0';
      run(e.target);
    }), { threshold: 0.6 });
    counters.forEach((el) => io.observe(el));
  }

  /* ------------------------------------------------------------ words that light up on scroll */
  document.querySelectorAll('[data-lit]').forEach((el) => {
    const words = [...el.querySelectorAll('.lw')];
    if (reduce) { el.classList.add('no-scrub'); return; }
    whenVisible(el, () => {
      const r = el.getBoundingClientRect();
      const p = clamp((vh * 0.86 - r.top) / (r.height * 0.85 + vh * 0.32), 0, 1);
      const lit = p * (words.length + 2);
      words.forEach((w, i) => { w.style.opacity = (0.16 + 0.84 * clamp(lit - i, 0, 1)).toFixed(3); });
    });
  });

  /* ------------------------------------------------------------ marquees */
  let scrollDir = 1;
  ticks.add(() => { if (Math.abs(velocity) > 0.4) scrollDir = velocity > 0 ? 1 : -1; });
  document.querySelectorAll('[data-marquee]').forEach((m) => {
    if (reduce) return;
    const track = m.querySelector('.marquee-track');
    const copy = m.querySelector('.marquee-copy');
    const dir = Number(m.dataset.dir) || 1;
    const base = 70 * (Number(m.dataset.speed) || 1);
    let width = copy.offsetWidth;
    let x = 0;
    let rot = 0;
    new ResizeObserver(() => { width = copy.offsetWidth; }).observe(copy);
    whenVisible(m, (t, dt) => {
      const boost = Math.min(Math.abs(velocity) * 22, 1400);
      const speed = (base + boost) * dir * scrollDir;
      x -= speed * dt;
      if (x <= -width) x += width;
      if (x > 0) x -= width;
      rot += speed * dt * 0.25;
      const skew = clamp(-velocity * 0.22, -9, 9);
      track.style.transform = `translate3d(${x.toFixed(1)}px,0,0) skewX(${skew.toFixed(2)}deg)`;
      m.style.setProperty('--rot', `${rot.toFixed(1)}deg`);
    });
  });

  /* ------------------------------------------------------------ x-ray: photo in front, CAD behind */
  const xrays = [];
  document.querySelectorAll('[data-xray]').forEach((el) => {
    const canvas = el.querySelector('.xray-canvas');
    const ctx = canvas.getContext('2d');
    let W = 0, H = 0;
    const cad = new Image();
    cad.decoding = 'async';
    let cadReady = false;
    const layer = document.createElement('canvas');
    const lctx = layer.getContext('2d');
    // the lens shows the CAD on the section's own colour with a faint grid, like a CAD viewport
    let bgColor = 'rgb(18, 16, 16)';
    for (let n = el.parentElement; n; n = n.parentElement) {
      const c = getComputedStyle(n).backgroundColor;
      if (c && c !== 'transparent' && !/rgba\(.*,\s*0\)$/.test(c)) { bgColor = c; break; }
    }
    const rgb = (bgColor.match(/\d+/g) || [18, 16, 16]).map(Number);
    const darkBg = (rgb[0] * 0.3 + rgb[1] * 0.59 + rgb[2] * 0.11) < 128;
    const buildLayer = () => {
      if (!cadReady || !W) return;
      layer.width = W; layer.height = H;
      lctx.fillStyle = bgColor; lctx.fillRect(0, 0, W, H);
      const step = Math.max(14, Math.round(W / 46));
      for (let x = (W / 2) % step, n = 0; x < W; x += step, n++) {
        lctx.fillStyle = darkBg ? 'rgba(242,240,235,.05)' : 'rgba(14,13,12,.06)';
        lctx.fillRect(Math.round(x), 0, 1, H);
      }
      for (let y = (H / 2) % step; y < H; y += step) {
        lctx.fillStyle = darkBg ? 'rgba(242,240,235,.05)' : 'rgba(14,13,12,.06)';
        lctx.fillRect(0, Math.round(y), W, 1);
      }
      lctx.drawImage(cad, 0, 0, W, H);
    };
    cad.onload = () => { cadReady = true; buildLayer(); };
    const startLoad = () => { if (!cad.src) cad.src = el.dataset.cad; };
    const mask = document.createElement('canvas');
    const mctx = mask.getContext('2d');
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const size = () => {
      const r = el.getBoundingClientRect();
      W = Math.max(1, Math.round(r.width * dpr)); H = Math.max(1, Math.round(r.height * dpr));
      canvas.width = mask.width = W; canvas.height = mask.height = H;
      buildLayer();
    };
    size();
    new ResizeObserver(size).observe(el);
    const st = { x: 0.5, y: 0.5, tx: 0.5, ty: 0.5, px: 0.5, py: 0.5, r: 0, inside: false, full: false, auto: !finePointer && !reduce, t: Math.random() * 10, idle: 0 };
    el.addEventListener('pointermove', (e) => {
      const r = el.getBoundingClientRect();
      st.tx = (e.clientX - r.left) / r.width; st.ty = (e.clientY - r.top) / r.height;
      st.inside = true;
      if (e.pointerType !== 'mouse') st.auto = false;
      if (reduce) { st.x = st.tx; st.y = st.ty; }
    });
    el.addEventListener('pointerenter', startLoad);
    el.addEventListener('pointerleave', () => { st.inside = false; if (!finePointer && !reduce) st.auto = true; });
    const stamp = (x, y, r) => {
      const g = mctx.createRadialGradient(x, y, 0, x, y, r);
      g.addColorStop(0, 'rgba(0,0,0,1)'); g.addColorStop(0.78, 'rgba(0,0,0,1)'); g.addColorStop(1, 'rgba(0,0,0,0)');
      mctx.fillStyle = g; mctx.beginPath(); mctx.arc(x, y, r, 0, Math.PI * 2); mctx.fill();
    };
    const tick = (t, dt) => {
      if (st.auto && !st.full) {
        st.t += dt;
        const amp = vw < 760 ? 0.2 : 0.3;
        st.tx = 0.5 + amp * Math.sin(st.t * 0.62);
        st.ty = 0.5 + 0.18 * Math.sin(st.t * 0.97 + 1.3);
      }
      const ease = reduce ? 1 : 0.16;
      st.x = lerp(st.x, st.tx, ease); st.y = lerp(st.y, st.ty, ease);
      const speed = Math.hypot(st.x - st.px, st.y - st.py);
      const base = Math.min(W, H) * (finePointer ? 0.24 : 0.3);
      const active = st.inside || st.auto;
      if (!active && !st.full && st.r < 1 && st.idle > 50) return;
      const targetR = st.full ? Math.hypot(W, H) : active ? base * (1 + Math.min(speed * 9, 0.45)) : 0;
      st.r = lerp(st.r, targetR, reduce ? 1 : st.full ? 0.07 : 0.12);
      if (active || st.full) startLoad();
      // fade the trail, then stamp the lens along the path travelled this frame
      mctx.globalCompositeOperation = 'destination-out';
      mctx.fillStyle = `rgba(0,0,0,${reduce ? 1 : 0.16})`;
      mctx.fillRect(0, 0, W, H);
      mctx.globalCompositeOperation = 'source-over';
      if (st.r > 1) {
        const steps = Math.max(1, Math.ceil((speed * W) / (st.r * 0.25)));
        for (let i = 1; i <= steps; i++) {
          const k = i / steps;
          stamp(lerp(st.px, st.x, k) * W, lerp(st.py, st.y, k) * H, st.r);
        }
        st.idle = 0;
      } else {
        st.idle += 1;
      }
      st.px = st.x; st.py = st.y;
      ctx.clearRect(0, 0, W, H);
      if (cadReady && st.idle < 40) {
        ctx.globalCompositeOperation = 'source-over';
        ctx.drawImage(layer, 0, 0);
        ctx.globalCompositeOperation = 'destination-in';
        ctx.drawImage(mask, 0, 0);
        ctx.globalCompositeOperation = 'source-over';
        if (st.r > 4 && !st.full) {
          ctx.strokeStyle = 'rgba(246,163,44,.75)';
          ctx.lineWidth = 1.5 * dpr;
          ctx.beginPath(); ctx.arc(st.x * W, st.y * H, st.r * 0.9, 0, Math.PI * 2); ctx.stroke();
        }
      }
    };
    whenVisible(el, tick, '10%');
    const alt = el.querySelector('.xray-alt');
    let altOn = false;
    const api = {
      el,
      toggle(on) {
        if (alt) { altOn = on; el.classList.toggle('is-full', on); st.inside = false; return; }
        st.full = on; startLoad(); if (on) { st.tx = 0.5; st.ty = 0.5; }
      },
      get full() { return alt ? altOn : st.full; },
    };
    xrays.push(api);
    if (st.auto) setTimeout(startLoad, 1200);
  });
  document.querySelectorAll('[data-xray-toggle]').forEach((btn) => {
    const scope = btn.closest('section') || document;
    const target = xrays.find((x) => scope.contains(x.el));
    if (!target) return;
    const label = btn.querySelector('.xray-toggle-text');
    btn.addEventListener('click', () => {
      const on = !target.full;
      target.toggle(on);
      btn.setAttribute('aria-pressed', String(on));
      if (label) label.textContent = on ? label.dataset.on : label.dataset.off;
    });
  });

  /* ------------------------------------------------------------ spin: scroll-scrubbed turntable */
  document.querySelectorAll('[data-spin]').forEach((sec) => {
    const N = Number(sec.dataset.frames) || 60;
    const small = Math.min(vw, vh * 1.6) < 820;
    const pattern = small ? sec.dataset.srcSmall : sec.dataset.src;
    const canvas = sec.querySelector('.spin-canvas');
    const ctx = canvas.getContext('2d');
    const stage = sec.querySelector('.spin-stage');
    const notes = [...sec.querySelectorAll('.spin-note')];
    const deg = sec.querySelector('[data-spin-deg]');
    const mode = sec.querySelector('[data-spin-mode]');
    const bar = sec.querySelector('[data-spin-bar]');
    const ghost = sec.querySelector('[data-spin-ghost]');
    const kinds = (sec.dataset.kinds || 'render,cad').split(',');
    const frames = {}; kinds.forEach((k) => { frames[k] = new Array(N); });
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    let W = 0, H = 0, started = false, dirty = true;
    const src = (kind, i) => pattern.replace('{kind}', kind).replace('{i}', String(i).padStart(3, '0'));
    const load = () => {
      if (started) return;
      started = true;
      // coarse pass first so scrubbing works right away, then fill in the gaps
      const order = [];
      for (let step of [12, 4, 2, 1]) for (let i = 0; i < N; i += step) if (!order.includes(i)) order.push(i);
      order.forEach((i) => kinds.forEach((kind) => {
        const im = new Image(); im.decoding = 'async'; im.src = src(kind, i); im.onload = () => { im.ok = true; dirty = true; };
        frames[kind][i] = im;
      }));
    };
    new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) load(); }), { rootMargin: '150% 0px 150% 0px' }).observe(sec);
    const size = () => { const r = stage.getBoundingClientRect(); W = Math.round(r.width * dpr); H = Math.round(r.height * dpr); canvas.width = W; canvas.height = H; dirty = true; };
    size();
    new ResizeObserver(size).observe(stage);
    const nearest = (kind, i) => {
      for (let d = 0; d < N / 2; d++) {
        const a = frames[kind][(i + d) % N]; if (a && a.ok) return a;
        const b = frames[kind][(i - d + N) % N]; if (b && b.ok) return b;
      }
      return null;
    };
    const draw = (p) => {
      const idx = Math.round(p * N) % N;
      const scan = kinds.length > 1 ? smoothstep(0.6, 0.86, p) : 0;
      ctx.clearRect(0, 0, W, H);
      const r = nearest(kinds[0], idx);
      if (r) ctx.drawImage(r, 0, 0, W, H);
      if (scan > 0) {
        const c = nearest(kinds[1], idx);
        if (c) { ctx.save(); ctx.beginPath(); ctx.rect(0, 0, W * scan, H); ctx.clip(); ctx.drawImage(c, 0, 0, W, H); ctx.restore(); }
      }
      sec.style.setProperty('--scan', scan.toFixed(4));
      sec.style.setProperty('--scan-on', scan > 0 && scan < 1 ? '1' : '0');
      notes.forEach((n) => n.classList.toggle('is-active', p >= Number(n.dataset.from) && p < Number(n.dataset.to)));
      if (deg) deg.textContent = `${String(Math.round(p * 360) % 361).padStart(3, '0')}°`;
      if (bar) bar.parentElement.style.setProperty('--p', p.toFixed(4));
      if (mode && kinds.length > 1) mode.textContent = scan > 0.5 ? 'CAD' : 'Render';
      if (ghost) ghost.style.setProperty('--gx', `${(-p * vw * 0.55).toFixed(1)}px`);
    };
    if (reduce) {
      sec.classList.add('is-static');
      load();
      const once = () => { const f = frames[kinds[0]][0]; if (f && f.ok) { size(); draw(0); } else setTimeout(once, 200); };
      once();
      return;
    }
    let lastP = -1;
    whenVisible(sec, () => {
      const r = sec.getBoundingClientRect();
      const p = clamp(-r.top / Math.max(1, r.height - vh), 0, 1);
      if (Math.abs(p - lastP) > 0.0004 || dirty) { dirty = false; draw(p); lastP = p; }
    }, '5%');
  });

  /* ------------------------------------------------------------ horizontal photo track */
  document.querySelectorAll('[data-track]').forEach((sec) => {
    const rail = sec.querySelector('[data-track-rail]');
    const items = [...rail.querySelectorAll('[data-drift]')];
    const ghost = sec.querySelector('[data-track-ghost]');
    if (reduce) { sec.classList.add('is-static'); return; }
    let dist = 0;
    const size = () => { dist = Math.max(0, rail.scrollWidth - vw); sec.style.height = `${dist + vh}px`; };
    size();
    window.addEventListener('resize', size);
    window.addEventListener('load', size);
    new ResizeObserver(size).observe(rail);
    whenVisible(sec, () => {
      const r = sec.getBoundingClientRect();
      const p = clamp(-r.top / Math.max(1, r.height - vh), 0, 1);
      rail.style.transform = `translate3d(${(-p * dist).toFixed(1)}px,0,0)`;
      items.forEach((it) => { it.style.transform = `translate3d(0,${((p - 0.5) * Number(it.dataset.drift) * 140).toFixed(1)}px,0)`; });
      if (ghost) ghost.style.setProperty('--gx', `${(-p * vw * 0.35).toFixed(1)}px`);
    }, '5%');
  });

  /* ------------------------------------------------------------ hover image (seasons) */
  const hoverEl = document.querySelector('[data-hover-img-el]');
  if (hoverEl && finePointer && !reduce) {
    const img = hoverEl.querySelector('img');
    let x = 0, y = 0, tx = 0, ty = 0, rot = 0;
    document.querySelectorAll('[data-hover-img]').forEach((a) => {
      const pre = new Image(); pre.src = a.dataset.hoverImg;
      a.addEventListener('pointerenter', (e) => { img.src = a.dataset.hoverImg; x = tx = e.clientX; y = ty = e.clientY; hoverEl.classList.add('is-on'); ticks.add(follow); });
      a.addEventListener('pointerleave', () => { hoverEl.classList.remove('is-on'); setTimeout(() => ticks.delete(follow), 400); });
      a.addEventListener('pointermove', (e) => { tx = e.clientX; ty = e.clientY; });
    });
    const follow = () => {
      const nx = lerp(x, tx, 0.16), ny = lerp(y, ty, 0.16);
      rot = lerp(rot, clamp((nx - x) * 0.6, -12, 12), 0.2);
      x = nx; y = ny;
      hoverEl.style.setProperty('--px', `${x}px`); hoverEl.style.setProperty('--py', `${y}px`); hoverEl.style.setProperty('--rot', `${rot.toFixed(2)}deg`);
    };
  }

  /* ------------------------------------------------------------ timeline fill */
  const timeline = document.querySelector('[data-timeline]');
  if (timeline) {
    const items = [...timeline.querySelectorAll('[data-tl-item]')];
    const line = timeline.querySelector('.tl-line');
    if (reduce) { items.forEach((i) => i.classList.add('is-lit')); }
    else whenVisible(timeline, () => {
      const r = timeline.getBoundingClientRect();
      const mark = vh * 0.62;
      line.style.setProperty('--t', clamp((mark - r.top) / r.height, 0, 1).toFixed(4));
      items.forEach((it) => it.classList.toggle('is-lit', it.getBoundingClientRect().top + 20 < mark));
    });
  }

  /* ------------------------------------------------------------ footer sun */
  const footerSun = document.querySelector('[data-footer-sun]');
  if (footerSun && !reduce) whenVisible(footerSun.parentElement, () => footerSun.style.setProperty('--rot', `${(scrollY * 0.06).toFixed(1)}deg`));

  /* ------------------------------------------------------------ magnetic buttons + tilt cards */
  if (finePointer && !reduce) {
    document.querySelectorAll('[data-magnetic]').forEach((b) => {
      b.addEventListener('pointermove', (e) => {
        const r = b.getBoundingClientRect();
        const dx = e.clientX - (r.left + r.width / 2), dy = e.clientY - (r.top + r.height / 2);
        b.style.transform = `translate(${(dx * 0.22).toFixed(1)}px, ${(dy * 0.32).toFixed(1)}px)`;
      });
      b.addEventListener('pointerleave', () => { b.style.transform = ''; });
    });
    document.querySelectorAll('[data-tilt]').forEach((card) => {
      const face = card.querySelector('.member-face');
      card.addEventListener('pointermove', (e) => {
        const r = face.getBoundingClientRect();
        const nx = (e.clientX - r.left) / r.width - 0.5, ny = (e.clientY - r.top) / r.height - 0.5;
        face.style.setProperty('--ry', `${(nx * 16).toFixed(2)}deg`);
        face.style.setProperty('--rx', `${(-ny * 16).toFixed(2)}deg`);
      });
      card.addEventListener('pointerleave', () => { face.style.setProperty('--ry', '0deg'); face.style.setProperty('--rx', '0deg'); });
    });
  }

  /* ------------------------------------------------------------ copy email */
  document.querySelectorAll('[data-copy]').forEach((b) => {
    const label = b.querySelector('span');
    b.addEventListener('click', async () => {
      try { await navigator.clipboard.writeText(b.dataset.copy); } catch (_) { return; }
      b.classList.add('is-copied');
      if (label) label.textContent = 'Copied';
      setTimeout(() => { b.classList.remove('is-copied'); if (label) label.textContent = 'Copy'; }, 1800);
    });
  });

  document.querySelectorAll('[data-year]').forEach((el) => { el.textContent = new Date().getFullYear(); });

  /* ------------------------------------------------------------ lightbox */
  const gallery = document.querySelector('[data-lightbox]');
  if (gallery) {
    const items = [...gallery.querySelectorAll('[data-lightbox-item]')];
    const icon = (d) => `<svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="${d}" stroke="currentColor" stroke-width="1.9"/></svg>`;
    const box = document.createElement('div');
    box.className = 'lightbox';
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-modal', 'true');
    box.setAttribute('aria-label', 'Photo viewer');
    box.innerHTML = `<div class="lightbox-stage"><img alt=""></div>
      <div class="lightbox-caption"><div><strong></strong> <span></span></div><span class="lightbox-count"></span></div>
      <button type="button" class="lb-btn lb-close" aria-label="Close photo viewer">${icon('M5 5l10 10M15 5 5 15')}</button>
      <button type="button" class="lb-btn lb-prev" aria-label="Previous photo">${icon('M16 10H4m5-5-5 5 5 5')}</button>
      <button type="button" class="lb-btn lb-next" aria-label="Next photo">${icon('M4 10h12m-5-5 5 5-5 5')}</button>`;
    document.body.appendChild(box);
    const img = box.querySelector('img');
    const capTitle = box.querySelector('.lightbox-caption strong');
    const capText = box.querySelector('.lightbox-caption span');
    const count = box.querySelector('.lightbox-count');
    let current = 0;
    let opener = null;
    const render = (i) => {
      current = (i + items.length) % items.length;
      const a = items[current];
      const fig = a.closest('figure');
      img.classList.remove('is-ready');
      img.onload = () => img.classList.add('is-ready');
      img.src = a.getAttribute('href');
      img.alt = a.querySelector('img').alt;
      if (img.complete) requestAnimationFrame(() => img.classList.add('is-ready'));
      capTitle.textContent = fig.querySelector('figcaption strong').textContent;
      capText.textContent = fig.querySelector('figcaption span').textContent;
      count.textContent = `${current + 1} / ${items.length}`;
    };
    const open = (i) => { opener = document.activeElement; render(i); box.classList.add('is-open'); if (lenis) lenis.stop(); box.querySelector('.lb-close').focus(); };
    const close = () => { box.classList.remove('is-open'); if (lenis) lenis.start(); if (opener) opener.focus(); };
    items.forEach((a, i) => a.addEventListener('click', (e) => {
      if (e.metaKey || e.ctrlKey || e.shiftKey) return;
      e.preventDefault();
      open(i);
    }));
    box.querySelector('.lb-close').addEventListener('click', close);
    box.querySelector('.lb-prev').addEventListener('click', () => render(current - 1));
    box.querySelector('.lb-next').addEventListener('click', () => render(current + 1));
    box.addEventListener('click', (e) => { if (e.target === box || e.target.classList.contains('lightbox-stage')) close(); });
    document.addEventListener('keydown', (e) => {
      if (!box.classList.contains('is-open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') render(current - 1);
      if (e.key === 'ArrowRight') render(current + 1);
      if (e.key === 'Tab') {
        const f = [...box.querySelectorAll('button')];
        if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
        else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
      }
    });
  }

  /* ------------------------------------------------------------ contact form */
  const form = document.getElementById('contact-form');
  if (!form) return;
  const feedback = document.getElementById('form-feedback');
  const submitButton = form.querySelector('button[type="submit"]');
  const submitLabels = submitButton.querySelectorAll('.btn-label > span');
  const setLabel = (t) => submitLabels.forEach((s) => { s.textContent = t; });
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    feedback.textContent = '';
    feedback.className = 'form-feedback';
    if (!form.reportValidity()) return;
    const payload = Object.fromEntries(new FormData(form).entries());
    submitButton.disabled = true;
    setLabel('Sending…');
    try {
      const response = await fetch('/api/contact', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      const result = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(result.error || `Your message didn’t send. Email us at ${'5214.helios@gmail.com'} instead.`);
      feedback.classList.add('success');
      feedback.textContent = 'Sent. Thanks for writing to us.';
      form.reset();
    } catch (error) {
      feedback.textContent = error.message || 'Your message didn’t send. Email us at 5214.helios@gmail.com instead.';
    } finally {
      submitButton.disabled = false;
      setLabel('Send message');
    }
  });
})();
