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
  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var current = 0;
  var timerId = null;
  var paused = false;
  var hidden = false;

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
  }
  function next() { go(current + 1); }
  function start() {
    if (reduceMotion || paused || hidden || timerId) return;
    timerId = setInterval(next, autoplayMs);
  }
  function stop() {
    if (timerId) { clearInterval(timerId); timerId = null; }
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
