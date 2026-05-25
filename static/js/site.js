// Mobile nav toggle
(function () {
  var toggle = document.querySelector('[data-nav-toggle]');
  var links = document.querySelector('[data-nav-links]');
  if (toggle && links) {
    toggle.addEventListener('click', function () {
      var open = links.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    links.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') links.classList.remove('open');
    });
  }

  // Reveal on scroll
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
    document.querySelectorAll('.fade-in').forEach(function (el) { io.observe(el); });
  } else {
    document.querySelectorAll('.fade-in').forEach(function (el) { el.classList.add('visible'); });
  }

  // Footer year
  var y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();

  // reCAPTCHA v3: fetch a token on submit, inject into hidden input, then submit.
  // Falls through silently if grecaptcha didn't load — server treats missing
  // token as a fail, which is the correct behaviour in production. In dev with
  // no secret configured, the server skips verification anyway.
  var contactForm = document.querySelector('[data-contact-form]');
  if (contactForm) {
    var recaptchaKey = contactForm.dataset.recaptchaKey;
    var tokenInput = contactForm.querySelector('input[name="g-recaptcha-response"]');
    var submitted = false;
    contactForm.addEventListener('submit', function (e) {
      if (submitted) return; // already got a token, let it through
      if (!recaptchaKey || typeof grecaptcha === 'undefined' || !grecaptcha.execute) return;
      e.preventDefault();
      grecaptcha.ready(function () {
        grecaptcha.execute(recaptchaKey, { action: 'contact' }).then(function (token) {
          if (tokenInput) tokenInput.value = token;
          submitted = true;
          contactForm.submit();
        }).catch(function () {
          // If reCAPTCHA fails for any reason, submit without a token; server
          // will reject in prod (where the secret is set) and the user sees
          // the "couldn't verify" error.
          submitted = true;
          contactForm.submit();
        });
      });
    });
  }
})();

// Hero slider (per-service rotation)
(function () {
  var slider = document.querySelector('[data-hero-slider]');
  if (!slider) return;

  var slides = Array.prototype.slice.call(slider.querySelectorAll('[data-slide-index]'));
  var dots = Array.prototype.slice.call(slider.querySelectorAll('[data-slide-to]'));
  if (slides.length < 2) return;

  var autoplayMs = parseInt(slider.getAttribute('data-autoplay-ms'), 10) || 3000;
  slider.style.setProperty('--hero-progress-duration', autoplayMs + 'ms');
  var progressBar = slider.querySelector('[data-hero-progress]');

  var current = 0;
  var timerId = null;
  var paused = false;
  var hidden = false;

  function resetProgress() {
    if (!progressBar) return;
    // Restart the CSS animation by toggling animation: none, forcing a reflow,
    // then letting it pick up the class-driven animation again.
    progressBar.style.animation = 'none';
    // eslint-disable-next-line no-unused-expressions
    progressBar.offsetHeight;
    progressBar.style.animation = '';
  }

  function go(n) {
    n = ((n % slides.length) + slides.length) % slides.length;
    slides.forEach(function (s, i) {
      var active = i === n;
      s.classList.toggle('is-active', active);
      if (active) s.removeAttribute('aria-hidden');
      else s.setAttribute('aria-hidden', 'true');
    });
    dots.forEach(function (d, i) {
      var active = i === n;
      d.classList.toggle('is-active', active);
      d.setAttribute('aria-selected', active ? 'true' : 'false');
    });
    current = n;
    resetProgress();
  }
  function next() { go(current + 1); }
  function start() {
    if (paused || hidden || timerId) return;
    timerId = setInterval(next, autoplayMs);
    slider.classList.add('is-playing');
    slider.classList.remove('is-paused');
  }
  function stop() {
    if (timerId) { clearInterval(timerId); timerId = null; }
    slider.classList.add('is-paused');
  }
  function restart() { stop(); start(); }

  slider.addEventListener('mouseenter', function () { paused = true; stop(); });
  slider.addEventListener('mouseleave', function () { paused = false; start(); });
  slider.addEventListener('focusin', function () { paused = true; stop(); });
  slider.addEventListener('focusout', function (e) {
    if (!slider.contains(e.relatedTarget)) { paused = false; start(); }
  });
  document.addEventListener('visibilitychange', function () {
    hidden = document.hidden;
    if (hidden) stop(); else start();
  });

  dots.forEach(function (d, i) {
    d.addEventListener('click', function () { go(i); restart(); });
  });

  var dotsRow = slider.querySelector('.hero-dots');
  if (dotsRow) {
    dotsRow.addEventListener('keydown', function (e) {
      if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
      e.preventDefault();
      var delta = e.key === 'ArrowRight' ? 1 : -1;
      var nextIdx = ((current + delta) % slides.length + slides.length) % slides.length;
      go(nextIdx); restart();
      dots[nextIdx].focus();
    });
  }

  start();
})();

// Cursor-attracted ambient orbs
(function () {
  if (!window.matchMedia) return;
  if (window.matchMedia('(hover: none)').matches) return;

  var ORB_COUNT = 14;
  var ATTRACT_RADIUS = 260;
  var PULL_STRENGTH = 0.55;
  var EASE = 0.08;

  var container = document.createElement('div');
  container.className = 'cursor-orbs';
  container.setAttribute('aria-hidden', 'true');
  document.body.appendChild(container);

  var orbs = [];
  for (var i = 0; i < ORB_COUNT; i++) {
    var el = document.createElement('span');
    el.className = 'cursor-orb';
    var size = (3 + Math.random() * 6).toFixed(1);
    el.style.width = size + 'px';
    el.style.height = size + 'px';
    el.style.opacity = (0.18 + Math.random() * 0.28).toFixed(2);
    container.appendChild(el);
    orbs.push({
      el: el,
      bx: 0.05 + Math.random() * 0.9,
      by: 0.05 + Math.random() * 0.9,
      ox: 0, oy: 0,
      tx: 0, ty: 0,
    });
  }

  var mx = -9999, my = -9999, hasMouse = false;
  document.addEventListener('mousemove', function (e) {
    mx = e.clientX;
    my = e.clientY;
    hasMouse = true;
  }, { passive: true });
  document.addEventListener('mouseleave', function () { hasMouse = false; });

  var vw = window.innerWidth, vh = window.innerHeight;
  window.addEventListener('resize', function () {
    vw = window.innerWidth; vh = window.innerHeight;
  });

  function tick() {
    for (var i = 0; i < orbs.length; i++) {
      var o = orbs[i];
      var px = o.bx * vw;
      var py = o.by * vh;
      if (hasMouse) {
        var dx = mx - px;
        var dy = my - py;
        var dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < ATTRACT_RADIUS) {
          var strength = 1 - (dist / ATTRACT_RADIUS);
          o.tx = dx * strength * PULL_STRENGTH;
          o.ty = dy * strength * PULL_STRENGTH;
        } else {
          o.tx = 0; o.ty = 0;
        }
      } else {
        o.tx = 0; o.ty = 0;
      }
      o.ox += (o.tx - o.ox) * EASE;
      o.oy += (o.ty - o.oy) * EASE;
      o.el.style.transform = 'translate3d(' + (px + o.ox).toFixed(1) + 'px,' + (py + o.oy).toFixed(1) + 'px,0)';
    }
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
})();
