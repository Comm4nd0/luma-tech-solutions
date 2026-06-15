/* Cookie consent banner — stores user preference in `lt_consent`.
   Banner shows on first visit (no cookie) or when re-opened via the
   footer "Cookie preferences" link.

   Analytics is Plausible (cookieless) and needs no gating. The "marketing"
   toggle gates Google Ads (gtag.js): the tag library is only injected once
   the visitor opts in — see loadGoogleAds()/applyConsent() below. Until then
   the gtag shim defined in base.html just queues events into the dataLayer
   without setting any cookies or making network calls. */
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

  function loadGoogleAds() {
    if (window.__ltAdsLoaded) return;
    var id = window.LUMA_ADS_ID;
    if (!id) return;
    window.__ltAdsLoaded = true;
    // Injected by cookie-consent.js (a nonce-trusted script), so the CSP's
    // 'strict-dynamic' allows this and gtag.js's own sub-resources to load.
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(id);
    document.head.appendChild(s);
    // The gtag shim already defined window.gtag + dataLayer in base.html.
    // Configuring now lets gtag.js replay any queued events (e.g. the
    // conversion pushed on the thanks pages) once it finishes loading.
    if (typeof window.gtag === 'function') window.gtag('config', id);
  }

  function applyConsent(consent) {
    // Analytics (Plausible) is cookieless and loads unconditionally.
    // Marketing (Google Ads) only loads with explicit opt-in.
    if (consent && consent.marketing) loadGoogleAds();
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
        // Analytics (Plausible) is cookieless and always-on, so the prefs UI
        // has no analytics input — guard the lookup so reading .checked on a
        // missing element can't throw and abort the save (which would lose the
        // marketing opt-in and leave the banner stuck open).
        var analyticsEl = banner.querySelector('[data-consent-cat="analytics"]');
        var marketingEl = banner.querySelector('[data-consent-cat="marketing"]');
        saveConsent({
          strict: true,
          analytics: analyticsEl ? !!analyticsEl.checked : true,
          marketing: marketingEl ? !!marketingEl.checked : false
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
