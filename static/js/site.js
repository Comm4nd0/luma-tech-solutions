// Respect reduced motion when moving focus after form validation.
function prefersReducedMotion() {
  return !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
}

(function () {
  var btn = document.querySelector('[data-theme-toggle]');
  if (!btn) return;
  function apply(theme) {
    if (theme === 'dark') document.documentElement.setAttribute('data-theme', 'dark');
    else document.documentElement.removeAttribute('data-theme');
    btn.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = theme === 'dark' ? '#0f172a' : '#f7f9fc';
  }
  apply(document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light');
  btn.addEventListener('click', function () {
    var next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem('luma-theme', next); } catch (_) {}
    apply(next);
  });
})();

// Enhance an otherwise fully visible navigation. Hidden removes closed links
// from both the tab order and accessibility tree; desktop always restores them.
(function () {
  var toggle = document.querySelector('[data-nav-toggle]');
  var links = document.querySelector('[data-nav-links]');
  if (!toggle || !links || !window.matchMedia) return;
  var mobile = window.matchMedia('(max-width: 1040px)');
  var open = false;
  function setOpen(value, returnFocus) {
    open = mobile.matches && value;
    if (returnFocus) toggle.focus();
    links.hidden = mobile.matches && !open;
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (open) {
      var first = links.querySelector('a');
      if (first) first.focus();
    }
  }
  toggle.closest('nav').classList.add('nav-enhanced');
  setOpen(false, false);
  toggle.addEventListener('click', function () { setOpen(!open, false); });
  links.addEventListener('click', function (event) {
    if (event.target.closest('a')) setOpen(false, false);
  });
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && open) { event.preventDefault(); setOpen(false, true); }
  });
  document.addEventListener('focusin', function (event) {
    if (open && !links.contains(event.target) && event.target !== toggle) setOpen(false, false);
  });
  function resize() { setOpen(false, mobile.matches && links.contains(document.activeElement)); }
  if (mobile.addEventListener) mobile.addEventListener('change', resize);
  else mobile.addListener(resize);
})();

(function () {
  var year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();
})();

// Accessible validation and a single, recoverable submission attempt.
(function () {
  var form = document.querySelector('[data-contact-form]');
  if (!form) return;
  var fields = Array.prototype.slice.call(form.querySelectorAll('input[required], textarea[required], select[required]'));
  var serviceGroup = form.querySelector('[data-service-choices]');
  var submit = form.querySelector('button[type="submit"]');
  var originalButton = submit ? submit.innerHTML : '';
  var status = document.createElement('p');
  status.className = 'form-status field-help';
  status.setAttribute('role', 'status');
  status.setAttribute('aria-live', 'polite');
  form.insertAdjacentElement('afterend', status);
  var pending = false;
  var attempt = 0;
  var timer;

  function setError(el, message) {
    var id = el.id + '-client-error';
    var msg = document.getElementById(id);
    // Only own our client-error token. Keep help text and server errors intact.
    var descriptions = (el.getAttribute('aria-describedby') || '').split(/\s+/).filter(function (token) { return token && token !== id; });
    el.classList.toggle('field-error', !!message);
    if (message) {
      if (!msg) {
        msg = document.createElement('p');
        msg.id = id;
        msg.className = 'field-error-msg';
        msg.setAttribute('role', 'alert');
        (el.tagName === 'FIELDSET' ? el : el.closest('div')).appendChild(msg);
      }
      msg.textContent = message;
      descriptions.push(id);
      el.setAttribute('aria-invalid', 'true');
    } else {
      if (msg) msg.remove();
      var hasServerError = descriptions.some(function (token) {
        var target = document.getElementById(token);
        return target && target.classList.contains('errorlist');
      });
      if (!hasServerError) el.removeAttribute('aria-invalid');
    }
    if (descriptions.length) el.setAttribute('aria-describedby', descriptions.join(' '));
    else el.removeAttribute('aria-describedby');
  }

  function validate(el) {
    var valid = el.checkValidity();
    setError(el, valid ? '' : (el.type === 'email' ? 'Please enter a valid email address.' : 'Please fill in this field.'));
    return valid;
  }
  function validateServices() {
    if (!serviceGroup) return true;
    var valid = !!serviceGroup.querySelector('input:checked');
    setError(serviceGroup, valid ? '' : 'Pick at least one service so we know what to quote.');
    return valid;
  }
  fields.forEach(function (el) {
    el.addEventListener('input', function () { if (el.classList.contains('field-error')) validate(el); });
    el.addEventListener('blur', function () { if (el.value !== '') validate(el); });
  });
  if (serviceGroup) serviceGroup.addEventListener('change', function () {
    if (serviceGroup.classList.contains('field-error')) validateServices();
  });

  function reset(message) {
    pending = false;
    attempt += 1;
    clearTimeout(timer);
    form.removeAttribute('aria-busy');
    if (submit) { submit.disabled = false; submit.innerHTML = originalButton; }
    status.textContent = message || '';
  }
  // The back/forward cache may restore the button in its sending state.
  window.addEventListener('pageshow', function () { reset(); });

  form.addEventListener('submit', function (event) {
    if (pending) { event.preventDefault(); return; }
    var firstBad = validateServices() ? null : serviceGroup.querySelector('input');
    fields.forEach(function (el) { if (!validate(el) && !firstBad) firstBad = el; });
    if (firstBad) {
      event.preventDefault();
      var details = firstBad.closest('details');
      if (details) details.open = true;
      firstBad.focus();
      firstBad.scrollIntoView({ behavior: prefersReducedMotion() ? 'auto' : 'smooth', block: 'center' });
      return;
    }
    pending = true;
    form.setAttribute('aria-busy', 'true');
    if (submit) { submit.disabled = true; submit.textContent = 'Sending…'; }
    status.textContent = 'Sending your details…';
    var key = form.dataset.recaptchaKey;
    var tokenInput = form.querySelector('input[name="g-recaptcha-response"]');
    // Preserve the server fallback when the API is unavailable. The server
    // still enforces verification whenever a production secret is configured.
    if (!key || typeof grecaptcha === 'undefined' || !grecaptcha.execute) return;
    event.preventDefault();
    var currentAttempt = ++attempt;
    function failed() {
      if (currentAttempt !== attempt) return;
      reset('The security check did not complete. Please try again, or use the contact details on this page.');
    }
    timer = setTimeout(failed, 12000);
    try {
      grecaptcha.ready(function () {
        if (currentAttempt !== attempt) return;
        try {
          grecaptcha.execute(key, { action: 'contact' }).then(function (token) {
            if (currentAttempt !== attempt) return;
            clearTimeout(timer);
            if (tokenInput) tokenInput.value = token;
            form.submit();
          }).catch(failed);
        } catch (_) { failed(); }
      });
    } catch (_) { failed(); }
  });
})();

// Keep explicitly supplied campaign tags on internal navigation. No cookies,
// localStorage, full referrer URLs or personal information are collected here.
(function () {
  var keys = ['utm_source', 'utm_medium', 'utm_campaign'];
  var current = new URL(window.location.href);
  var tags = {};
  keys.forEach(function (key) {
    var value = current.searchParams.get(key);
    if (value) tags[key] = value.trim().slice(0, 100);
  });
  if (Object.keys(tags).length) {
    document.querySelectorAll('a[href]').forEach(function (link) {
      var raw = link.getAttribute('href');
      if (!raw || raw.charAt(0) === '#') return;
      var target;
      try { target = new URL(raw, window.location.href); } catch (_) { return; }
      if (target.origin !== current.origin || !/^https?:$/.test(target.protocol)) return;
      if (/^\/(admin|api|static|media)(\/|$)/.test(target.pathname)) return;
      if (/\.(xml|txt|pdf)$/.test(target.pathname)) return;
      Object.keys(tags).forEach(function (key) {
        if (!target.searchParams.has(key)) target.searchParams.set(key, tags[key]);
      });
      link.href = target.href;
    });
  }
  var form = document.querySelector('[data-lead-form]');
  if (!form) return;
  var started = false;
  form.addEventListener('input', function () {
    if (started) return;
    started = true;
    window.plausible = window.plausible || function () { (window.plausible.q = window.plausible.q || []).push(arguments); };
    window.plausible('Enquiry started', {props: {form: form.dataset.leadForm}});
  });
})();
