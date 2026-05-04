/* Cookie consent banner — stores user preference in `lt_consent`.
   Banner shows on first visit (no cookie) or when re-opened via the
   footer "Cookie preferences" link.

   Currently the site loads no analytics or marketing scripts, so the
   non-essential toggles don't gate anything yet. They're here so the
   framework is in place when (if) such tools are added later — at which
   point the corresponding loaders should be wired into applyConsent(). */
(function () {
  'use strict';

  var CONSENT_COOKIE = 'lt_consent';
  var CONSENT_VERSION = 1;
  var COOKIE_DAYS = 365;

  function readCookie(name) {
    var match = document.cookie.match(new RegExp('(?:^|;\\s*)' + name + '=([^;]+)'));
    if (!match) return null;
    try {
      return JSON.parse(decodeURIComponent(match[1]));
    } catch (e) {
      return null;
    }
  }

  function writeCookie(name, value, days) {
    var date = new Date();
    date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000);
    var encoded = encodeURIComponent(JSON.stringify(value));
    var secure = window.location.protocol === 'https:' ? '; Secure' : '';
    document.cookie = name + '=' + encoded + '; expires=' + date.toUTCString() +
      '; path=/; SameSite=Lax' + secure;
  }

  function getConsent() {
    var stored = readCookie(CONSENT_COOKIE);
    if (!stored || stored.version !== CONSENT_VERSION) return null;
    return stored;
  }

  function saveConsent(consent) {
    var record = {
      version: CONSENT_VERSION,
      timestamp: new Date().toISOString(),
      consent: consent
    };
    writeCookie(CONSENT_COOKIE, record, COOKIE_DAYS);
    applyConsent(consent);
  }

  function applyConsent(consent) {
    // No analytics/marketing scripts loaded yet. When added, gate them
    // behind the relevant flags here:
    //   if (consent.analytics) { /* load Plausible / GA4 / etc. */ }
    //   if (consent.marketing) { /* load remarketing pixels */ }
    document.dispatchEvent(new CustomEvent('lt:consent-applied', { detail: consent }));
  }

  function setStage(banner, stage) {
    banner.querySelector('[data-consent-stage="notice"]').hidden = stage !== 'notice';
    banner.querySelector('[data-consent-stage="preferences"]').hidden = stage !== 'preferences';
  }

  function syncToggles(banner) {
    var current = getConsent();
    if (!current) return;
    var analytics = banner.querySelector('[data-consent-cat="analytics"]');
    var marketing = banner.querySelector('[data-consent-cat="marketing"]');
    if (analytics) analytics.checked = !!current.consent.analytics;
    if (marketing) marketing.checked = !!current.consent.marketing;
  }

  function showBanner(banner, stage) {
    setStage(banner, stage || 'notice');
    banner.hidden = false;
  }

  function hideBanner(banner) {
    banner.hidden = true;
  }

  function init() {
    var banner = document.querySelector('[data-cookie-consent]');
    if (!banner) return;

    var existing = getConsent();
    if (existing) {
      applyConsent(existing.consent);
    } else {
      showBanner(banner, 'notice');
    }

    banner.addEventListener('click', function (event) {
      var btn = event.target.closest('[data-consent-action]');
      if (!btn) return;
      var action = btn.getAttribute('data-consent-action');

      if (action === 'accept') {
        saveConsent({ strict: true, analytics: true, marketing: true });
        hideBanner(banner);
      } else if (action === 'reject') {
        saveConsent({ strict: true, analytics: false, marketing: false });
        hideBanner(banner);
      } else if (action === 'customize') {
        syncToggles(banner);
        showBanner(banner, 'preferences');
      } else if (action === 'back') {
        showBanner(banner, 'notice');
      } else if (action === 'save') {
        saveConsent({
          strict: true,
          analytics: !!banner.querySelector('[data-consent-cat="analytics"]').checked,
          marketing: !!banner.querySelector('[data-consent-cat="marketing"]').checked
        });
        hideBanner(banner);
      }
    });

    // Footer "Cookie preferences" trigger
    var triggers = document.querySelectorAll('[data-cookie-prefs-trigger]');
    Array.prototype.forEach.call(triggers, function (el) {
      el.addEventListener('click', function (event) {
        event.preventDefault();
        syncToggles(banner);
        showBanner(banner, 'preferences');
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
}());
