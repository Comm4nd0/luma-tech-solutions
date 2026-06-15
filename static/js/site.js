// Respect the user's reduced-motion preference for JS-driven animation.
function prefersReducedMotion() {
  return !!(window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches);
}

// Theme toggle (light / dark). Light is the default; dark is opt-in via
// [data-theme="dark"] on <html>, persisted in localStorage as 'luma-theme'.
(function () {
  var btn = document.querySelector('[data-theme-toggle]');
  if (!btn) return;
  var SWEEP_MS = 600;
  var sweeping = false;
  function apply(theme) {
    if (theme === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
    btn.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
  }
  // Initialise aria-pressed from whatever the inline head script applied.
  apply(document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light');
  function buttonCircleCoords() {
    var rect = btn.getBoundingClientRect();
    var x = rect.left + rect.width / 2;
    var y = rect.top + rect.height / 2;
    var w = window.innerWidth;
    var h = window.innerHeight;
    return { x: x, y: y, maxR: Math.hypot(Math.max(x, w - x), Math.max(y, h - y)) };
  }

  btn.addEventListener('click', function () {
    if (sweeping) return;
    var current = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
    var next = current === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem('luma-theme', next); } catch (e) {}
    // Reduced motion: swap instantly, skip the radial-reveal animation.
    if (prefersReducedMotion()) { apply(next); return; }
    // Radial reveal: a circle of the destination colour grows from the toggle
    // button's centre out to the farthest viewport corner. When it covers the
    // viewport, swap the theme attribute and remove the overlay — the colour
    // beneath now matches what was visible.
    sweeping = true;
    var c = buttonCircleCoords();
    var overlay = document.createElement('div');
    overlay.className = 'theme-sweep theme-sweep--to-' + next;
    overlay.style.clipPath = 'circle(0px at ' + c.x + 'px ' + c.y + 'px)';
    overlay.style.transition = 'clip-path ' + SWEEP_MS + 'ms cubic-bezier(0.4, 0, 0.2, 1)';
    document.body.appendChild(overlay);
    void overlay.offsetHeight;
    overlay.style.clipPath = 'circle(' + c.maxR + 'px at ' + c.x + 'px ' + c.y + 'px)';
    setTimeout(function () {
      apply(next);
      overlay.remove();
      sweeping = false;
    }, SWEEP_MS);
  });
})();

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

// Inline form validation: highlight required fields that are empty/invalid on
// submit, and clear the highlight as soon as the user fixes them. Native
// validation messages are suppressed by `novalidate`; this restores a visible
// cue without blocking the reCAPTCHA submit flow.
(function () {
  var form = document.querySelector('[data-contact-form]');
  if (!form) return;

  function fieldWrap(el) { return el.closest('div') || el; }

  function setError(el, on) {
    el.classList.toggle('field-error', on);
    var wrap = fieldWrap(el);
    var msg = wrap.querySelector('.field-error-msg');
    if (on && !msg) {
      msg = document.createElement('p');
      msg.className = 'field-error-msg';
      msg.textContent = el.type === 'email'
        ? 'Please enter a valid email address.'
        : 'Please fill in this field.';
      wrap.appendChild(msg);
    } else if (!on && msg) {
      msg.remove();
    }
  }

  function validate(el) {
    var bad = !el.checkValidity();
    setError(el, bad);
    return !bad;
  }

  var fields = Array.prototype.slice.call(
    form.querySelectorAll('input[required], textarea[required], select[required]')
  );
  fields.forEach(function (el) {
    el.addEventListener('input', function () { if (el.classList.contains('field-error')) validate(el); });
    el.addEventListener('blur', function () { if (el.value !== '') validate(el); });
  });

  form.addEventListener('submit', function (e) {
    var firstBad = null;
    fields.forEach(function (el) {
      if (!validate(el) && !firstBad) firstBad = el;
    });
    if (firstBad) {
      e.preventDefault();
      e.stopImmediatePropagation(); // don't run the reCAPTCHA submit handler
      firstBad.focus();
      firstBad.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }, true); // capture so this runs before the reCAPTCHA handler
})();
