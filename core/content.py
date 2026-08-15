"""Marketing page content.

Pure data, deliberately dependency-free: no Django imports, no reverse(), no
models. ``core.urls`` imports ``core.views`` which imports this module, and
``core.sitemaps`` imports it directly — a module-level reverse() here would
raise AppRegistryNotReady at import time, and importing views would make the
cycle real. Store URL *names* and reverse them in the view.

Moving any of this to the database is the right call the moment it needs to be
edited by a non-developer.
"""

PILLARS = [
    {
        "key": "networking",
        "title": "Wi-Fi & Networking",
        "tagline": "Properly engineered Wi-Fi and network design — no more dead-spots, no more rebooting the router.",
        "url_name": "service_networking",
        "icon": "wifi",
    },
    {
        "key": "security",
        "title": "Physical Security",
        "tagline": "CCTV, access control and alarms — professionally installed and integrated with your network.",
        "url_name": "service_security",
        "icon": "lock",
    },
    {
        "key": "development",
        "title": "App & Web Development",
        "tagline": "Custom websites, web applications and mobile apps — built and supported by the same engineer.",
        "url_name": "service_development",
        "icon": "code",
    },
    {
        "key": "automation",
        "title": "Home Automation",
        "tagline": "Smart homes that are private, fast and keep working when the internet doesn't.",
        "url_name": "service_automation",
        "icon": "home",
    },
    {
        "key": "support",
        "title": "Support & Maintenance",
        "tagline": "Ongoing care so you never have to troubleshoot your own house alone.",
        "url_name": "service_support",
        "icon": "shield",
    },
]


TESTIMONIALS = [
    {
        "name": "Helen R.",
        "role": "Owner, Chiltern View",
        "rating": 5,
        "quote": (
            "Marco redesigned our Wi-Fi and built a full smart home setup. "
            "Everything just works — and when we need a tweak he's a message away."
        ),
    },
    {
        "name": "James T.",
        "role": "Co-founder, For Sale By Owner",
        "rating": 5,
        "quote": (
            "Luma Tech delivered our mobile app on time and on budget. "
            "Clean code, sensible advice, and a partner who actually understands the business."
        ),
    },
    {
        "name": "Claire M.",
        "role": "Paws 4 Thought Dogs",
        "rating": 5,
        "quote": (
            "Beautiful website, fast turnaround, and ongoing support. "
            "I never feel like I'm bothering them — they treat the site like it's their own."
        ),
    },
]


# --- Care plans -----------------------------------------------------------
#
# HOME_CARE_PLANS and BUSINESS_CARE_PLANS were near-clones: the Essential
# feature list was byte-identical between them, and name/min_term/highlighted
# are the same across both audiences. Those live in CARE_TIERS once.
#
# Everything that genuinely differs — price, suffixes, tagline, and the
# Professional/Concierge feature copy — stays verbatim per audience. The
# differences are marketing claims ("smart-home product in the house" vs
# "networked product on the premises"), not mechanical noun swaps, so they
# are not generated.

_ESSENTIAL_FEATURES = [
    '24/7 automated network monitoring with alerts to us',
    'Firmware, security patches and daily config backups managed for you',
    'Email support — next business day for routine, same business day (best effort) for service-down',
    'Quarterly health-check report',
    'One-page network diagram, kept current with any changes we make',
    '20% off our standard hourly rate for work outside the plan',
    'Internet provider liaison when your line goes down — we make the calls',
]


CARE_TIERS = [
    {
        "key": 'essential',
        "name": 'Essential',
        "highlighted": False,
        "min_term": '3-month rolling',
    },
    {
        "key": 'professional',
        "name": 'Professional',
        "highlighted": True,
        "min_term": '6-month rolling',
    },
    {
        "key": 'concierge',
        "name": 'Concierge',
        "highlighted": False,
        "min_term": '12-month',
    },
]


CARE_PLAN_AUDIENCES = {
    'home': {
        'essential': {
            'price': '£75',
            'price_suffix': '/mo +VAT',
            'annual_price': '£810',
            'annual_suffix': '/yr',
            'tagline': 'Quiet, reliable IT — we watch it, you forget about it.',
            "features": _ESSENTIAL_FEATURES,
        },
        'professional': {
            'price': '£165',
            'price_suffix': '/mo +VAT',
            'annual_price': '£1,780',
            'annual_suffix': '/yr',
            'tagline': 'Hands-on support for everything Luma installed — same engineer who built it.',
            "features": [
                'Everything in Essential',
                'Reactive support for any kit, app or integration we supplied or installed — networking, CCTV, smart-home, custom apps',
                'Same business day for routine; target within 4 working hours for service-down',
                'Phone, video and WhatsApp support',
                '2 hours of remote moves-and-changes per year (rolls over up to 4)',
                'One on-site visit per year included (tune-up, cable check, hardware audit)',
                'Warranty management on hardware we supply — UI Care registered, RMAs handled by us',
                '5% loyalty discount from year 2',
            ],
        },
        'concierge': {
            'price': '£325',
            'price_suffix': '/mo +VAT',
            'annual_price': '£3,510',
            'annual_suffix': '/yr',
            'tagline': 'The whole smart home, whoever installed it — one engineer, one number, one bill.',
            "features": [
                'Everything in Professional',
                ("We'll take a look at any smart-home product in the house, whoever installed it — Sonos, Lutron, Ring, Nest, Hue, legacy integrations. Diagnose, advise and escalate to the manufacturer; we don't "
 "warrant kit we didn't supply, but you've got one number to call."),
                'Front of queue; target within 2 working hours for service-down',
                'Best-effort out-of-hours for genuine emergencies',
                'One on-site visit per quarter + monthly check-in call',
                '6 hours of remote moves-and-changes per year (rolls over up to 12)',
                'Full living documentation — network map, device inventory, credentials vault, runbook',
                'Loaner hardware where we have stock; otherwise we expedite the RMA on your behalf',
                'Multi-site coverage — main home plus a holiday let or small office under one plan',
                '10% loyalty discount from year 2',
            ],
        },
    },
    'business': {
        'essential': {
            'price': '£25',
            'price_suffix': '/user/mo +VAT',
            'annual_price': '£270',
            'annual_suffix': '/user/yr',
            'tagline': 'Quiet, reliable IT for small teams — we watch it, you focus on the work.',
            "features": _ESSENTIAL_FEATURES,
        },
        'professional': {
            'price': '£55',
            'price_suffix': '/user/mo +VAT',
            'annual_price': '£595',
            'annual_suffix': '/user/yr',
            'tagline': 'Hands-on support for everything Luma installed — same engineer who built it.',
            "features": [
                'Everything in Essential',
                'Reactive support for any kit, app or integration we supplied or installed — networking, CCTV, point-of-sale, custom apps',
                'Same business day for routine; target within 4 working hours for service-down',
                'Phone, video and WhatsApp support',
                '2 hours of remote moves-and-changes per user per year (rolls over up to 4)',
                'One on-site visit per quarter (cable check, hardware audit, team Q&A)',
                'Warranty management on hardware we supply — UI Care registered, RMAs handled by us',
                '5% loyalty discount from year 2',
            ],
        },
        'concierge': {
            'price': '£110',
            'price_suffix': '/user/mo +VAT',
            'annual_price': '£1,190',
            'annual_suffix': '/user/yr',
            'tagline': 'The whole office, whoever installed it — one engineer, one number, one bill.',
            "features": [
                'Everything in Professional',
                ("We'll take a look at any networked product on the premises, whoever installed it — printers, NAS, VOIP, point-of-sale, legacy kit from a previous IT company. Diagnose, advise and escalate to the "
 "manufacturer; we don't warrant kit we didn't supply, but you've got one number to call."),
                'Front of queue; target within 2 working hours for service-down',
                'Best-effort out-of-hours for genuine emergencies',
                'One on-site visit per month + monthly check-in call',
                '6 hours of remote moves-and-changes per user per year (rolls over up to 12)',
                'Full living documentation — network map, device inventory, credentials vault, runbook',
                'Loaner hardware where we have stock; otherwise we expedite the RMA on your behalf',
                'Multi-site coverage — main office plus a satellite or warehouse under one plan',
                '10% loyalty discount from year 2',
            ],
        },
    },
}


def care_plans(audience):
    """Tier definitions merged with one audience's pricing and copy.

    Returns the same dict shape templates/services/support.html already
    reads, in canonical tier order (order is load-bearing on the page).
    """
    overlay = CARE_PLAN_AUDIENCES[audience]
    return [{**tier, **overlay[tier["key"]]} for tier in CARE_TIERS]


CASE_STUDIES = [
    {
        "slug": "chiltern-view",
        "title": "Chiltern View — full smart home and UniFi network",
        "tag": "Smart home + networking",
        "illustration": "automation",
        "summary": (
            "A complete residential rebuild: fast Wi-Fi everywhere, Protect "
            "CCTV recording at the property, and Home Assistant running "
            "scenes, climate, lighting and access — all on a single dashboard "
            "that doesn't depend on anyone's cloud."
        ),
        "stack": ["UniFi Dream Machine Pro", "UniFi APs & Switches", "UniFi Protect", "Home Assistant", "Zigbee"],
        "outcome": "Whole-home coverage, automations that work without the internet, no cloud lock-in.",
        "featured": False,
    },
    {
        "slug": "for-sale-by-owner",
        "title": "For Sale By Owner — property listings mobile app",
        "tag": "Mobile app",
        "illustration": "development",
        "summary": (
            "A polished cross-platform mobile app for a UK property listings "
            "business, with photo uploads, map-based search and a back-office "
            "for the team to moderate listings."
        ),
        "stack": ["React Native (Expo)", "Django REST Framework", "PostgreSQL", "S3-compatible storage"],
        "outcome": "Shipped on iOS and Android in under 12 weeks. Live and supported.",
        "featured": False,
    },
    {
        "slug": "chiltern-yard-anpr",
        "title": "Chiltern Yard, Maidenhead — ANPR & site CCTV",
        "tag": "Construction · ANPR",
        "illustration": "security",
        "summary": (
            "A working builder's compound in Maidenhead — 0.8 acres, "
            "gated entrance, mixed sub-contractor traffic across a "
            "six-month groundworks programme. Two UniFi AI LPR cameras "
            "at the gate log every vehicle in and out; an AI 360 covers "
            "the material yard; four G5 Bullets cover the perimeter. "
            "Recording stays on a UDM Pro in a lockable site cabinet, "
            "with 4G failover during the first six weeks before the "
            "fixed line went in."
        ),
        "stack": [
            "UniFi Dream Machine Pro",
            "2× AI LPR (gate ANPR)",
            "AI 360 (yard)",
            "4× G5 Bullet (perimeter)",
            "PoE Switch + 4G failover",
            "DPIA + signage pack",
        ],
        "outcome": (
            "Sub-contractor billing disputes resolved in an afternoon from "
            "timestamped gate footage. Site manager reports ~3 hours/week "
            "saved on attendance reconciliation. Zero out-of-hours "
            "intrusions over the install period."
        ),
        "featured": False,
        "detail": [
            (
                "The brief was blunt: the site manager was spending chunks of "
                "every Friday arguing about who was on site, when, and for how "
                "long. Sub-contractor invoices claimed days the gate log "
                "didn't show; the gate log was a clipboard in a portacabin "
                "that got filled in when someone remembered. Materials had "
                "started disappearing from the yard, and the compound had "
                "been walked twice out of hours in the month before we were "
                "called."
            ),
            (
                "We designed the system around the gate. Two UniFi AI LPR "
                "cameras — one facing in, one facing out — capture every "
                "plate in both directions at site-traffic speeds, with the "
                "mounting angle and stand-off distance set during the survey "
                "so plate captures stay readable in headlight glare and rain. "
                "An AI 360 covers the material yard from a single ceiling "
                "mount on the storage barn, and four G5 Bullets cover the "
                "perimeter fencing. Everything records to a Dream Machine "
                "Pro in a lockable comms cabinet inside the compound — "
                "footage never leaves the site, and there is no monthly "
                "cloud subscription."
            ),
            (
                "The first six weeks ran entirely on 4G failover because the "
                "fixed line hadn't been installed yet — recording is local, "
                "so the cameras don't care, and alerts still reached the "
                "site manager's phone over cellular. When the line went in, "
                "the system switched over without a visit."
            ),
            (
                "Because workplace ANPR is personal-data processing, the "
                "install shipped with the paperwork done: a drafted Data "
                "Protection Impact Assessment, compliant signage at the "
                "gate, and a one-page summary of what is recorded, for how "
                "long, and who can view it — filed with the site's H&S "
                "documentation."
            ),
        ],
    },
    {
        "slug": "littlewick-house",
        "title": "LittleWick House — whole-property UniFi network",
        "tag": "Networking",
        "illustration": "networking",
        "summary": (
            "A large residential property in Maidenhead across four floors, "
            "plus a cellar, garage and separate annex. Eleven access points, "
            "three distribution switches, a Dream Machine Pro at the core, "
            "and three VLANs separating home, IoT and guest traffic — all "
            "on a single managed network with no dead spots."
        ),
        "stack": [
            "UniFi Dream Machine Pro",
            "Pro Max 24 PoE Switch",
            "11× U7-Pro / U7-Pro-Wall APs",
            "3× PoE Switches",
            "VLAN segmentation",
        ],
        "outcome": "Rock-solid Wi-Fi from loft to cellar to annex, with proper network segmentation and room to grow.",
        "featured": True,
        "detail": [
            (
                "Four floors of solid-wall construction, a cellar, a garage "
                "and a separate annex — the classic large-property problem. "
                "The owners had been through two mesh systems, both of which "
                "promised whole-home coverage and delivered a strong signal "
                "in the rooms that already had it."
            ),
            (
                "The survey drove the design: eleven access points (a mix of "
                "ceiling-mount U7-Pros and in-wall U7-Pro-Walls), each fed "
                "by its own Cat6 run back to one of three PoE distribution "
                "switches, with a Dream Machine Pro at the core. Three VLANs "
                "separate the family's devices, the smart-home kit and guest "
                "traffic, so a compromised IoT gadget can't see a laptop."
            ),
            (
                "Every run is labelled at both ends, the patch panel matches "
                "the as-built diagram, and the handover pack documents every "
                "AP location, VLAN and credential — so any competent "
                "engineer could pick the system up cold."
            ),
        ],
    },
    {
        "slug": "paws-4-thought-dogs",
        "title": "Paws 4 Thought Dogs — small business website",
        "tag": "Marketing site",
        "illustration": "development",
        "summary": (
            "A polished, SEO-friendly website for a local dog-walking business, "
            "with booking enquiries, gallery and Google Business integration."
        ),
        "stack": ["Static site", "Custom CSS", "Caddy + Docker", "Hetzner VPS"],
        "outcome": "First-page Google ranking for local search within 6 weeks.",
        "featured": False,
    },
    {
        "slug": "paws-4-thought-dogs-app",
        "title": "Paws 4 Thought Dogs — mobile app",
        "tag": "Mobile app",
        "illustration": "development",
        "summary": (
            "A two-sided iOS app for the same Berkshire dog-daycare business. "
            "Owners get a daily photo and video feed of their dogs, book "
            "boarding, manage dog profiles and message staff directly. Staff "
            "get a dashboard for daily assignments, request approvals, "
            "transport tracking and compatibility notes — all synced to a "
            "Django backend with offline-first caching for use in the field."
        ),
        "stack": [
            "Flutter",
            "Django REST Framework",
            "PostgreSQL",
            "Push notifications",
            "Offline cache (Hive)",
        ],
        "outcome": "Live on the App Store. iPhone, iPad, Mac (M1+) and Apple Vision supported.",
        "featured": False,
    },
]


# --- Website demos ---
# Standalone, fully-designed one-page demo sites for fictional local businesses,
# shown on /portfolio/ so prospects can click through and experience the kind of
# website we'd build for them. Each "template" is a self-contained HTML document
# (it does NOT extend base.html and does NOT load site.css) so every demo can look
# genuinely different. The businesses are fictional and the pages are noindex.

WEBSITE_DEMOS = [
    {
        "slug": "maple-and-vine",
        "name": "The Maple & Vine",
        "industry": "Restaurant · Marlow",
        "tagline": "Seasonal British bistro on the high street — menus, story and table bookings.",
        "accent": "#9a3b2e",
        "thumb": "https://images.pexels.com/photos/31517300/pexels-photo-31517300.jpeg?auto=compress&cs=tinysrgb&w=800",
        "template": "showcase/maple_and_vine.html",
    },
    {
        "slug": "riverside-strength",
        "name": "Riverside Strength",
        "industry": "Fitness studio · Maidenhead",
        "tagline": "Bold strength-and-conditioning gym with class timetable and membership pricing.",
        "accent": "#e4572e",
        "thumb": "https://images.pexels.com/photos/3837781/pexels-photo-3837781.jpeg?auto=compress&cs=tinysrgb&w=800",
        "template": "showcase/riverside_strength.html",
    },
    {
        "slug": "thames-valley-gardens",
        "name": "Thames Valley Gardens",
        "industry": "Landscaping · Henley",
        "tagline": "Garden design and grounds care — services, planting gallery and free site visits.",
        "accent": "#3f7d4e",
        "thumb": "https://images.pexels.com/photos/7174105/pexels-photo-7174105.jpeg?auto=compress&cs=tinysrgb&w=800",
        "template": "showcase/thames_valley_gardens.html",
    },
    {
        "slug": "marlow-dental-care",
        "name": "Marlow Dental Care",
        "industry": "Dental practice · Marlow",
        "tagline": "Calm, modern dentistry — treatments, plans and online appointment requests.",
        "accent": "#2f80c2",
        "thumb": "https://images.pexels.com/photos/3845553/pexels-photo-3845553.jpeg?auto=compress&cs=tinysrgb&w=800",
        "template": "showcase/marlow_dental_care.html",
    },
    {
        "slug": "frame-and-field",
        "name": "Frame & Field",
        "industry": "Photographer · Thames Valley",
        "tagline": "Minimal monochrome portfolio for a wedding and portrait photographer.",
        "accent": "#111111",
        "thumb": "https://images.pexels.com/photos/18398510/pexels-photo-18398510.jpeg?auto=compress&cs=tinysrgb&w=800",
        "template": "showcase/frame_and_field.html",
    },
]


# --- FAQ data ---
# Shown on the home page and (subset) on service pages. Also rendered into
# FAQPage JSON-LD so Google can show them as rich results / featured snippets.
# Keep answers short, plain-English, keyword-rich without keyword stuffing.

FAQS_GENERAL = [
    {
        "q": "What areas do you cover?",
        "a": (
            "We're based in Marlow and cover the Thames Valley — Marlow, "
            "Maidenhead, Henley-on-Thames, Beaconsfield, Bourne End, "
            "Cookham and High Wycombe. We'll travel further across "
            "Buckinghamshire and Berkshire by arrangement."
        ),
    },
    {
        "q": "How much does a Wi-Fi installation cost?",
        "a": (
            "Every property is different — the honest answer is we'll quote "
            "after a site survey. A typical large-home UniFi install (4–6 "
            "access points, switching, cabling) runs from around £3,000; "
            "bigger properties with 8+ APs, multiple VLANs and CCTV usually "
            "fall between £8,000 and £20,000. Every quote is fixed-price and "
            "written down — no day rates, no surprise add-ons."
        ),
    },
    {
        "q": "How long does an installation take?",
        "a": (
            "A standard home Wi-Fi install is usually 1–2 days on site once "
            "we've finished the survey and ordered kit. Whole-property "
            "networks with structured cabling can run to 5–10 days, often "
            "split across visits so we work around your routine. We agree "
            "the schedule up-front and stick to it."
        ),
    },
    {
        "q": "Do I have to sign up to a care plan?",
        "a": (
            "No. Every install comes with 30 days of post-install support "
            "as standard. Care plans are optional from there — they're for "
            "clients who want monitoring, faster response, and one engineer "
            "who knows the system on call. From £75/month + VAT for homes "
            "or £25/user/month for small businesses."
        ),
    },
    {
        "q": "Why UniFi instead of consumer mesh kit?",
        "a": (
            "Consumer mesh and powerline kit are designed for small flats "
            "with thin walls. Once you add a second storey, thick masonry, "
            "or 200+ m² of floorspace, the physics catch up. UniFi gives "
            "you wired access points (no halving bandwidth every hop), "
            "real diagnostics, and one dashboard for Wi-Fi, switching and "
            "CCTV — the same kit that runs in offices and hotels."
        ),
    },
    {
        "q": "Will my CCTV footage be stored in the cloud?",
        "a": (
            "Not unless you specifically want it to be. We default to "
            "UniFi Protect, which records to a small NVR at your house. "
            "No monthly subscription, no third-party AI looking through "
            "your footage, and it keeps working when your broadband doesn't."
        ),
    },
]


# Networking-specific FAQs, used on the Wi-Fi service page.
FAQS_NETWORKING = [
    {
        "q": "Will UniFi work in my period property?",
        "a": (
            "Yes — and we design specifically for older houses. Lath-and-"
            "plaster walls, foil-backed insulation and thick masonry "
            "absorb Wi-Fi, so the answer is more access points placed "
            "correctly, fed by wired Cat6 — not a bigger mesh kit. We've "
            "done Georgian, Victorian and listed properties around Marlow "
            "and Henley."
        ),
    },
    {
        "q": "Do I need to run cables everywhere?",
        "a": (
            "We run Cat6 from a central comms cupboard to each access "
            "point and camera. Where the loft is accessible we drop down "
            "the walls; where it isn't, we use existing voids, conduits, "
            "or surface-mount trunking discreetly. We plan all the runs "
            "in the site survey so you see exactly what's going where "
            "before we drill anything."
        ),
    },
    {
        "q": "Can you cover the garden and outbuildings?",
        "a": (
            "Yes. Outdoor APs, point-to-point links to garden offices and "
            "annexes, and weatherproof CCTV coverage are part of what we "
            "design. We've done pool houses, stable blocks, garden offices "
            "and large gardens across the Thames Valley."
        ),
    },
]


# Security-specific FAQs, used on the Physical Security service page.
FAQS_SECURITY = [
    {
        "q": "Is the CCTV recorded in the cloud?",
        "a": (
            "Not by default. UniFi Protect records to an NVR at your "
            "property, so footage stays with you. No monthly subscription "
            "and no third-party AI rifling through your footage. We can "
            "add encrypted off-site backup as an option if you want it."
        ),
    },
    {
        "q": "Do the cameras work in the dark?",
        "a": (
            "Yes. The cameras we install have high-quality infrared night vision "
            "and (on most models) low-light colour modes. On-device AI "
            "tells person from vehicle from package, so your phone only "
            "buzzes for things that matter."
        ),
    },
    {
        "q": "Can I view it on my phone?",
        "a": (
            "Yes — secure remote viewing through the UniFi Protect app on "
            "iOS and Android. Two-factor authentication, end-to-end "
            "encrypted, and no public ports opened on your router."
        ),
    },
]


# AI-cameras FAQs, used on the AI camera systems service page.
FAQS_AI_CAMERAS = [
    {
        "q": "Does the AI run in the cloud?",
        "a": (
            "No. The cameras we install carry their own neural-processing "
            "hardware — person, vehicle, package, animal and number-plate "
            "detection all run on the camera itself. Your video stream is "
            "never shipped to a third party for analysis, and the system "
            "works fully even when your broadband is down."
        ),
    },
    {
        "q": "How accurate is the number plate recognition (ANPR)?",
        "a": (
            "On UniFi AI Pro and AI LPR cameras, plate capture is reliable "
            "for typical UK gate speeds (under ~30 mph) with the camera "
            "positioned and aimed correctly during the site survey. We "
            "design the install around the angle and distance the model "
            "needs, not the convenience of an existing mounting point — "
            "which is the difference between 95%+ readable captures and "
            "the cheap kit that misses half the plates."
        ),
    },
    {
        "q": "Can the cameras be set to only record at certain times?",
        "a": (
            "Yes — every install ships with recording schedules and "
            "geofence arming configured before handover, per camera. "
            "Site cameras can be off during the working day and on "
            "out-of-hours; internal cameras can be off when family or "
            "staff phones are inside the geofence and on automatically "
            "when everyone has left. We agree the pattern with you up "
            "front and document it in the handover pack."
        ),
    },
    {
        "q": "Do I need an ICO registration for ANPR on a building site?",
        "a": (
            "If you're processing personal data via CCTV in a workplace "
            "or commercial setting — which ANPR is — yes, you should be "
            "registered with the ICO, have a Data Protection Impact "
            "Assessment, and display compliant signage. We draft the "
            "DPIA, supply the signage and hand over a one-page summary "
            "of what's recorded, for how long, and who can see it as "
            "part of the install package."
        ),
    },
    {
        "q": "Can family members watch the cameras from their phones?",
        "a": (
            "Yes — we set up the UniFi Protect app on each authorised "
            "phone with two-factor authentication mandatory, and each "
            "viewer gets their own named login (not a shared password). "
            "Remote viewing goes through the vendor's encrypted relay or "
            "your own VPN — we never open ports on your firewall."
        ),
    },
    {
        "q": "Will the cameras work if the internet goes down?",
        "a": (
            "Yes. Recording happens locally on a Network Video Recorder "
            "at your property, not in the cloud, so footage keeps being "
            "captured even when the WAN is offline. On sites with poor "
            "broadband we add a 4G failover so remote alerts still get "
            "through; the recording itself never stops."
        ),
    },
    {
        "q": "Can you do fall detection or medical alerts?",
        "a": (
            "Honestly — no, not as a medical-grade product. AI cameras "
            "can flag unusual events like a person remaining motionless, "
            "but a camera is not a medical alarm and shouldn't be sold as "
            "one. For households where someone needs reliable fall or "
            "medical-emergency response, we'll happily build a "
            "monitoring system for peace of mind — and we'll insist you "
            "pair it with a dedicated telecare device (a Lifeline pendant "
            "or equivalent) for the medical side."
        ),
    },
]



# Construction / trade FAQs, used on the builders & construction page.
# NOTE for Marco: the insurance answer deliberately doesn't state a cover
# figure — add the £ amount once you've confirmed it with the policy.
FAQS_CONSTRUCTION = [
    {
        "q": "Can you install site cameras for just the duration of the build?",
        "a": (
            "Yes — that's the normal arrangement. We install at site "
            "set-up, you pay a fixed monthly price for the duration of "
            "the programme, and at the end we either decommission the "
            "kit or move it straight to your next site. Multi-site "
            "builders run the same system from compound to compound."
        ),
    },
    {
        "q": "Do you work alongside our electrician and other trades?",
        "a": (
            "All the time. On pre-wire jobs we issue first-fix drawings "
            "and containment requirements so your electrician can pull "
            "alongside their own runs if preferred, or we do the pull "
            "ourselves and stay out of their way. Either way we "
            "terminate, test and certify every run, and we fit around "
            "the build programme — first fix before plasterboard, "
            "second fix at decoration."
        ),
    },
    {
        "q": "How does per-plot pricing work on a development?",
        "a": (
            "We quote a fixed price per plot type from your drawings — "
            "one figure for each house type covering cabling, "
            "containment, comms enclosure, access points and any CCTV "
            "or door-entry pre-wire. The same figure then repeats "
            "across every plot of that type, so your QS can put a "
            "clean number in the cost plan without re-quoting each unit."
        ),
    },
    {
        "q": "Who handles the ICO and DPIA paperwork for site ANPR?",
        "a": (
            "We do, as part of the install package. Workplace CCTV with "
            "ANPR needs ICO registration, a Data Protection Impact "
            "Assessment, compliant signage and a retention policy. We "
            "draft the DPIA, supply the signage, and hand over a "
            "one-page record of what's recorded, for how long, and who "
            "can see it — ready for your H&S file."
        ),
    },
    {
        "q": "What do we get at handover?",
        "a": (
            "As-built documentation: labelled and tested cable runs, a "
            "network diagram, camera schedules, credentials, and a "
            "plain-English handover pack — per plot on developments. "
            "Nothing is locked to us; any competent engineer could pick "
            "the system up from the pack alone."
        ),
    },
    {
        "q": "Can you provide RAMS and proof of insurance?",
        "a": (
            "Yes. We produce site-specific risk assessments and method "
            "statements for every job, and we carry public liability "
            "insurance — certificates and RAMS are available for your "
            "records before we arrive on site. If your procurement "
            "process needs anything else, ask and we'll sort it."
        ),
    },
]


JOB_ROLES = [
    {
        "key": "network",
        "title": "UniFi Network Engineer",
        "summary": "Design and deploy UniFi networks for homes and small businesses across the Thames Valley.",
        "responsibilities": [
            "Plan and install UniFi Wi-Fi, switching and gateway kit on residential and small-business sites",
            "Configure VLANs, firewall rules, guest networks and Protect CCTV — carefully segmented, thoroughly documented",
            "Commission, label and hand-over networks with clean as-built documentation",
            "Triage and resolve client issues remotely (UniFi Site Manager) and on-site",
        ],
        "ideal": [
            "Hands-on UniFi experience — Dream Machines, switches, APs, Protect",
            "Comfortable reading floor plans and planning AP placement for coverage",
            "Working knowledge of VLANs, DHCP, DNS and basic firewall rules",
            "Tidy worker — cable management is a craft, not an afterthought",
        ],
        "logistics": "Based in Marlow / Maidenhead. Driving licence and own transport essential. Mix of on-site and remote work.",
    },
    {
        "key": "infrastructure",
        "title": "Infrastructure Engineer — Cable Installations",
        "summary": "First-fix and second-fix structured cabling for residential and small-commercial UniFi installations.",
        "responsibilities": [
            "Pull and terminate Cat6/Cat6a runs through lofts, voids, conduit and trunking",
            "Install and patch keystones, faceplates and patch panels — labelled and tested",
            "Mount APs, CCTV cameras, switches and small comms cabinets",
            "Work alongside the network engineer to turn a design into a clean, working install",
        ],
        "ideal": [
            "Proven structured-cabling experience (Cat5e/Cat6/Cat6a) and confident with a Fluke or similar tester",
            "Good with power tools, ladders and access equipment — H&S aware",
            "ECS / CSCS / IPAF tickets a bonus, not essential",
            "Pride in finished work and a willingness to do it right the first time",
        ],
        "logistics": "Field-based across Marlow, Maidenhead, Henley and the Thames Valley. Driving licence and own transport essential.",
    },
    {
        "key": "cyber",
        "title": "Cyber Security Engineer",
        "summary": "Harden the networks we build and help small-business clients reach Cyber Essentials and beyond.",
        "responsibilities": [
            "Design and review firewall, VLAN and remote-access policies on UniFi gateways and cloud services",
            "Run vulnerability scans, patch reviews and config audits for client networks and endpoints",
            "Support clients through Cyber Essentials and Cyber Essentials Plus certification",
            "Investigate and triage incidents — phishing, account compromise, suspicious traffic — and lead the response",
            "Tighten Microsoft 365 / Google Workspace tenants: MFA, conditional access, mailbox rules, retention",
        ],
        "ideal": [
            "Solid grounding in network security fundamentals (firewalls, segmentation, IDS/IPS, VPNs)",
            "Hands-on with at least one EDR / endpoint suite and one cloud-identity platform (Entra ID, Google Workspace)",
            "Comfortable explaining risk in plain English to non-technical business owners",
            "Relevant cert (CompTIA Security+, BTL1, SC-200, OSCP) helpful but practical experience matters more",
            "DBS-friendly — some clients require it",
        ],
        "logistics": "Hybrid — mostly remote with site visits across Marlow, Maidenhead, Henley and the Thames Valley. Driving licence preferred.",
    },
]


# --- Page tables -----------------------------------------------------------
#
# The service, area and thanks pages were six, four and three near-identical
# view functions. They are described here as data and rendered by the generic
# helpers in views.py.
#
# Values that look derivable but are NOT:
#   * "active" — service_security has its own top-level nav slot ("security"),
#     every other service page is "services".
#   * "service_type" — ai_cameras and security both use "CCTV Installation".
#   * "template" — services/overview.html doesn't fit services/<key>.html.
#   * "faqs" — three service pages deliberately have none. Omit the key; do not
#     default it, or those pages grow a visible FAQ block and a FAQPage
#     JSON-LD node.
#
# URL names, not paths: views.py reverses them at request time.

SERVICE_PAGES = {
    "networking": {
        "template": "services/networking.html",
        "active": "services",
        "url_name": "service_networking",
        "crumb": "Wi-Fi & Networking",
        "page_title": "UniFi Wi-Fi Installation, Marlow & Henley | Luma Tech",
        "page_description": (
            "Professionally engineered UniFi Wi-Fi for large and period "
            "homes — Marlow, Maidenhead, Henley-on-Thames and the Thames "
            "Valley. Wired access points, fixed-price quotes, no mesh."
        ),
        "service_name": "Wi-Fi & Networking",
        "service_type": "Wi-Fi Installation",
        "service_description": (
            "UniFi Wi-Fi and network design, installation and management "
            "for homes and small businesses across Marlow, Maidenhead, "
            "Henley-on-Thames and the wider Thames Valley."
        ),
        "area_anchor": "Wi-Fi installation in {town}",
        "faqs": FAQS_NETWORKING,
    },
    "security": {
        "template": "services/security.html",
        # Physical Security has its own nav entry — not the "services" slot.
        "active": "security",
        "url_name": "service_security",
        "crumb": "Physical Security",
        "page_title": "CCTV Installation Marlow, Maidenhead & Henley | Luma Tech",
        "page_description": (
            "UniFi Protect CCTV, access control and alarms across Marlow, "
            "Maidenhead, Henley-on-Thames and the Thames Valley. Footage "
            "stays on your kit — no cloud subscription required."
        ),
        "service_name": "Physical Security",
        "service_type": "CCTV Installation",
        "service_description": (
            "UniFi Protect CCTV, access control, alarms and "
            "network hardening for homes and businesses across Marlow, "
            "Maidenhead, Beaconsfield and the Thames Valley."
        ),
        "area_anchor": "CCTV installation in {town}",
        "faqs": FAQS_SECURITY,
    },
    "development": {
        "template": "services/development.html",
        "active": "services",
        "url_name": "service_development",
        "crumb": "App & Web Development",
        "page_title": "Mobile App & Website Development | Luma Tech",
        "page_description": (
            "Custom websites, web apps and iOS/Android apps built and "
            "supported by one engineer in Marlow, Buckinghamshire."
        ),
        "service_name": "App & Web Development",
        "service_type": "Software Development",
        "service_description": (
            "Custom websites, web applications and mobile apps built and "
            "supported by an engineer in Marlow, Buckinghamshire."
        ),
        "area_anchor": "Website and app development in {town}",
    },
    "automation": {
        "template": "services/automation.html",
        "active": "services",
        "url_name": "service_automation",
        "crumb": "Home Automation",
        "page_title": "Smart Home Installer — Marlow, Henley, Maidenhead | Luma Tech",
        "page_description": (
            "Local-first Home Assistant smart-home installation. Lighting, "
            "climate, scenes and security across Marlow, Henley-on-Thames, "
            "Maidenhead and the Thames Valley. No cloud lock-in."
        ),
        "service_name": "Home Automation",
        "service_type": "Home Automation",
        "service_description": (
            "Local-first smart-home design with Home Assistant — lighting, "
            "climate, security and scenes across Marlow, Henley-on-Thames "
            "and the Thames Valley."
        ),
        "area_anchor": "Smart home installation in {town}",
    },
    "ai_cameras": {
        "template": "services/ai_cameras.html",
        "active": "services",
        "url_name": "service_ai_cameras",
        "crumb": "AI Camera Systems",
        "page_title": "AI Camera Systems — ANPR, Smart CCTV, Privacy-First | Luma Tech",
        "page_description": (
            "AI cameras done right across Marlow, Maidenhead, "
            "Henley and the Thames Valley. ANPR for construction "
            "sites, smart home & family monitoring, scheduled and "
            "geofenced recording. Footage stays on your kit."
        ),
        "service_name": "AI Camera Systems",
        "service_type": "CCTV Installation",
        "service_description": (
            "AI camera systems with on-device person, vehicle, package, "
            "animal and number-plate recognition. Designed for "
            "construction sites, homes and small businesses across "
            "Marlow, Maidenhead, Henley and the Thames Valley. "
            "Scheduled recording, geofenced arming, on-site storage — "
            "no third-party cloud."
        ),
        "area_anchor": "AI cameras and ANPR in {town}",
        "faqs": FAQS_AI_CAMERAS,
    },
    "support": {
        "template": "services/support.html",
        "active": "services",
        "url_name": "service_support",
        "crumb": "Support & Maintenance",
        "page_title": "IT Support & Care Plans, Bucks & Berks | Luma Tech",
        "page_description": (
            "Three care-plan tiers with monitoring, response SLAs and a "
            "real human. Serving homes and businesses across the Thames Valley."
        ),
        "service_name": "Support & Maintenance",
        "service_type": "IT Support",
        "service_description": (
            "Ongoing IT support and care plans for homes and small "
            "businesses across Marlow, Maidenhead and the Thames Valley."
        ),
        "area_anchor": "IT support in {town}",
    },
}


AREA_PAGES = {
    "marlow": {
        "template": "areas/marlow.html",
        "url_name": "area_marlow",
        "source": "area-marlow",
        "quote_label": "Marlow",
        "engineer_note": "based in Marlow",
        "survey_note": (
            "Site surveys typically within 5 working days for Marlow postcodes."
        ),
        "included": [
            "On-site survey",
            "Fixed-price proposal",
            "Plain-English documentation",
            "30 days post-install support",
        ],
        "also_serving": [
            {"url_name": "area_maidenhead", "label": "Maidenhead"},
            {"url_name": "area_henley", "label": "Henley-on-Thames"},
            {"url_name": "area_beaconsfield", "label": "Beaconsfield"},
        ],
        "also_serving_tail": "Bourne End, Cookham, High Wycombe.",
        "schema_name": "Wi-Fi, CCTV and IT Support in Marlow",
        "schema_description": (
            "Local Marlow engineer for Wi-Fi installation, CCTV, smart-home "
            "design and ongoing IT support — for homes and small businesses "
            "across Marlow and Marlow Bottom."
        ),
        "town": "Marlow",
        "page_title": "Wi-Fi, CCTV & IT Support in Marlow | Luma Tech",
        "page_description": (
            "Marlow-based engineer for Wi-Fi installation, CCTV, smart-home "
            "and IT support. Local response, fixed-price proposals."
        ),
    },
    "maidenhead": {
        "template": "areas/maidenhead.html",
        "url_name": "area_maidenhead",
        "source": "area-maidenhead",
        "quote_label": "Maidenhead",
        "engineer_note": "based 15 minutes away in Marlow",
        "survey_note": (
            "Site surveys typically within 5 working days for Maidenhead postcodes."
        ),
        "included": [
            "On-site survey",
            "Fixed-price proposal",
            "Plain-English documentation",
            "30 days post-install support",
        ],
        "also_serving": [
            {"url_name": "area_marlow", "label": "Marlow"},
            {"url_name": "area_henley", "label": "Henley-on-Thames"},
            {"url_name": "area_beaconsfield", "label": "Beaconsfield"},
        ],
        "also_serving_tail": "Cookham, Bourne End, High Wycombe.",
        "schema_name": "Wi-Fi, CCTV and IT Support in Maidenhead",
        "schema_description": (
            "Whole-property UniFi networks, CCTV and smart-home design for "
            "larger homes in Maidenhead — Furze Platt, Boyn Hill, Cox Green, "
            "Bray and Holyport."
        ),
        "town": "Maidenhead",
        "page_title": "Wi-Fi, CCTV & IT Support in Maidenhead | Luma Tech",
        "page_description": (
            "Whole-property UniFi networks, CCTV and smart-home design "
            "for larger homes in Maidenhead, Bray, Furze Platt and Cox Green."
        ),
        # The only area page with a case study.
        "featured_case_slug": "littlewick-house",
    },
    "henley": {
        "template": "areas/henley.html",
        "url_name": "area_henley",
        "source": "area-henley",
        "quote_label": "Henley",
        "engineer_note": "based 15 minutes away in Marlow",
        "survey_note": (
            "Site surveys typically within 5 working days for Henley "
            "postcodes (RG9 and surrounding)."
        ),
        "included": [
            "On-site survey",
            "Fixed-price proposal",
            "Plain-English documentation",
            "30 days post-install support",
        ],
        "also_serving": [
            {"url_name": "area_marlow", "label": "Marlow"},
            {"url_name": "area_maidenhead", "label": "Maidenhead"},
            {"url_name": "area_beaconsfield", "label": "Beaconsfield"},
        ],
        "also_serving_tail": "Cookham, Bourne End, High Wycombe.",
        "schema_name": "Wi-Fi, CCTV and IT Support in Henley-on-Thames",
        "schema_description": (
            "Wi-Fi, CCTV and smart-home design for period homes and riverside "
            "properties across Henley-on-Thames, Remenham, Hambleden and "
            "Mill End."
        ),
        "town": "Henley-on-Thames",
        "page_title": (
            "Wi-Fi, CCTV & Smart Home Installation in Henley-on-Thames | Luma Tech"
        ),
        "page_description": (
            "UniFi Wi-Fi, CCTV and smart-home installation for period homes "
            "and riverside properties in Henley-on-Thames, Remenham, "
            "Hambleden and Mill End. Local Marlow engineer."
        ),
    },
    "beaconsfield": {
        "template": "areas/beaconsfield.html",
        "url_name": "area_beaconsfield",
        "source": "area-beaconsfield",
        "quote_label": "Beaconsfield",
        "engineer_note": "based 15 minutes away in Marlow",
        "survey_note": (
            "Site surveys typically within 5 working days for Beaconsfield "
            "postcodes (HP9 and surrounding)."
        ),
        # Beaconsfield alone promises a free survey and a 48h proposal.
        "included": [
            "Free on-site survey",
            "Fixed-price proposal in 48h",
            "Plain-English documentation",
            "30 days post-install support",
        ],
        "also_serving": [
            {"url_name": "area_marlow", "label": "Marlow"},
            {"url_name": "area_maidenhead", "label": "Maidenhead"},
            {"url_name": "area_henley", "label": "Henley-on-Thames"},
        ],
        "also_serving_tail": "Bourne End, Cookham, High Wycombe.",
        "schema_name": "Wi-Fi, CCTV and IT Support in Beaconsfield",
        "schema_description": (
            "UniFi Wi-Fi, CCTV and smart-home installation for the larger "
            "homes and small businesses around Beaconsfield, Knotty Green, "
            "Holtspur and Forty Green."
        ),
        "town": "Beaconsfield",
        "page_title": "Wi-Fi, CCTV & Smart Home Installation in Beaconsfield | Luma Tech",
        "page_description": (
            "UniFi Wi-Fi, CCTV and smart-home installation for the larger "
            "homes and businesses around Beaconsfield, Knotty Green and "
            "Holtspur. Local Marlow engineer, fixed-price quotes."
        ),
    },
}


# Confirmation pages: no breadcrumbs, no schema, just a title and a nav slot.
THANKS_PAGES = {
    "contact_thanks": {
        "template": "contact_thanks.html",
        "active": "contact",
        "page_title": "Thanks — we'll be in touch | Luma Tech",
        "page_description": 'Your enquiry has been received. We reply within one working day.',
    },
    "quote_thanks": {
        "template": "quote_thanks.html",
        "active": "quote",
        "page_title": 'Quote request received — thanks | Luma Tech',
        "page_description": "Your quote request has been received. We'll be in touch within one working day to book your free site survey.",
    },
    "careers_thanks": {
        "template": "careers_thanks.html",
        "active": "careers",
        "page_title": 'Application received — thanks | Luma Tech',
        "page_description": "Your job application has been received. We'll be in touch shortly.",
    },
}
