"""Seed three construction-focused blog posts.

Part of the builders & developers lead-gen push: each post targets a
construction search intent nothing else in the Thames Valley ranks for,
and funnels readers to /construction/.

Idempotent — uses update_or_create on slug, so re-applying on a fresh DB
or after editing copy in this file is safe. The second and third posts
are given future publish dates at the time of writing so they roll out
on a weekly cadence; if this migration is applied after those dates they
simply publish immediately, which is also fine.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

from django.db import migrations


LONDON = ZoneInfo("Europe/London")


def at(year, month, day, hour=9, minute=0):
    return datetime(year, month, day, hour, minute, tzinfo=LONDON)


POST_HIRE_VS_BUY = """
<p>Every builder running a compound in the Thames Valley has had the same two phone calls: the hire company chasing a renewal on the site camera tower, and a site manager reporting something walked off the yard overnight anyway. So it's worth asking the question properly: for a typical site in Marlow, Maidenhead or High Wycombe, should you hire site CCTV or have it installed?</p>

<h2>What site CCTV hire actually costs</h2>
<p>A single hired CCTV tower typically runs £250–£450 per week depending on spec and monitoring, plus delivery, collection and a setup charge. On a 12-month programme that's £13,000–£23,000 for one camera position — and most compounds need the gate <em>and</em> the yard <em>and</em> at least a stretch of perimeter.</p>
<p>Hire has real advantages — no capital outlay, maintenance included, easy to specify. But you hand the kit back at the end with nothing to show for the spend, and the footage usually lives on the hire company's platform, not yours.</p>

<h2>What an installed site CCTV system costs</h2>
<p>An installed system — gate ANPR cameras, a panoramic camera over the material yard, bullet cameras on the perimeter, recording to a unit in a lockable site cabinet — is a one-off install cost plus a modest monthly support fee. Over a six-month groundworks programme it's usually comparable to hiring a single tower. Over a multi-year development, or across several sites, it's dramatically cheaper, because:</p>
<ul>
<li><strong>You keep the kit.</strong> At the end of the programme it moves to your next compound — the second site's security costs a fraction of the first.</li>
<li><strong>The footage is yours.</strong> Recorded on site, on your hardware. No per-clip retrieval fees, no third-party platform between you and the evidence.</li>
<li><strong>ANPR comes included.</strong> Gate cameras with number-plate recognition give you a searchable log of every vehicle in and out — which is attendance evidence, not just security.</li>
</ul>

<h2>The hidden line item: sub-contractor disputes</h2>
<p>Ask any QS what disputed sub-contractor invoices cost across a programme and the CCTV question changes shape. On a Maidenhead compound we equipped, <a href="/portfolio/chiltern-yard-anpr/">two billing disputes were resolved in a single afternoon</a> by pulling timestamped gate footage, and the site manager reports around three hours a week saved on attendance reconciliation. That's the return — the burglary deterrent is almost a side benefit.</p>

<h2>When hire still makes sense</h2>
<p>We'll be honest: hire wins for very short programmes (under ~8 weeks), for sites with no power whatsoever, or where your insurer specifically mandates a monitored tower with guard response. For everything else — especially if you run more than one site a year in Buckinghamshire or Berkshire — installed kit that follows you from compound to compound wins on cost and gives you the vehicle log hire towers don't.</p>

<h2>What we install on Thames Valley sites</h2>
<ul>
<li>UniFi AI LPR cameras at the gate — every plate, both directions, timestamped</li>
<li>Panoramic AI 360 coverage over the yard and material storage</li>
<li>Weatherproof bullets on the perimeter, mounted high enough to survive site life</li>
<li>Recording on a UDM Pro in a lockable cabinet — with 4G failover until your fixed line goes in</li>
<li>The DPIA, ICO signage and retention policy drafted for you</li>
</ul>
<p>If you're pricing security for a site in Marlow, Maidenhead, Henley or anywhere across the Thames Valley, <a href="/construction/">see how our site security packages work</a> or <a href="/quote/?service=site_security&amp;property=construction_site&amp;source=blog-hire-vs-buy">get a fixed monthly figure for your compound</a>.</p>
"""


POST_ANPR_ICO = """
<p>Number-plate recognition at the site gate is the single most useful camera a builder's compound can have — and it's also the one that creates legal obligations most site managers have never been told about. Here's the plain-English version of what UK law requires when you run ANPR on a construction site, and who should be doing the paperwork.</p>

<h2>Why ANPR on a building site counts as personal data</h2>
<p>A registration plate identifies a person (the registered keeper), so under UK GDPR, capturing and storing plates is processing personal data. The moment your gate camera logs plates — even just for attendance records — you're a data controller with real obligations. The same applies to ordinary workplace CCTV; ANPR just makes it unambiguous.</p>

<h2>The five things the ICO expects</h2>
<ul>
<li><strong>ICO registration.</strong> Almost every business processing personal data must be registered with the Information Commissioner's Office and pay the data protection fee. If your firm isn't registered, that comes first.</li>
<li><strong>A lawful basis.</strong> For site security and attendance evidence this is usually "legitimate interests" — but it has to be identified and written down, not assumed.</li>
<li><strong>A Data Protection Impact Assessment (DPIA).</strong> ANPR is exactly the kind of systematic monitoring the ICO says needs a DPIA before you switch it on: what's captured, why, the risks, and how they're mitigated.</li>
<li><strong>Compliant signage.</strong> Clear signs at every entrance telling people CCTV and ANPR are in operation, who runs it, and how to contact them. A faded generic "CCTV in operation" sticker doesn't meet the standard.</li>
<li><strong>A retention policy you can point at.</strong> Keep footage only as long as you can justify — and be able to say what that period is when a sub-contractor, employee or the ICO asks.</li>
</ul>

<h2>Who actually does all this?</h2>
<p>On most sites, nobody — which is the problem. The camera installer says it's the client's responsibility, the client assumes the installer handled it, and the paperwork doesn't exist until there's a subject-access request or a complaint.</p>
<p>Our position is simpler: if we install ANPR on your site, the paperwork is part of the install. We draft the DPIA, supply compliant signage for every entrance, and hand over a one-page record of what's recorded, for how long, and who can see it — ready for your H&amp;S file. <a href="/construction/">That's baked into our construction packages</a>, not sold as an extra.</p>

<h2>Done right, it's an asset, not a liability</h2>
<p>A compliant ANPR setup gives a Thames Valley site manager a searchable, timestamped log of every vehicle through the gate — attendance evidence for sub-contractor invoicing, an audit trail for H&amp;S, and out-of-hours intrusion alerts, all recorded on your own kit in the site cabinet rather than someone else's cloud. On <a href="/portfolio/chiltern-yard-anpr/">a working compound in Maidenhead</a> that log resolved two billing disputes in an afternoon.</p>
<p>Running a site in Marlow, Maidenhead, High Wycombe or anywhere across Buckinghamshire and Berkshire? <a href="/services/ai-cameras/">Read how our AI camera systems work</a>, or <a href="/quote/?service=site_security&amp;property=construction_site&amp;source=blog-anpr-ico">get a quote with the compliance paperwork included</a>.</p>
"""


POST_PREWIRE = """
<p>There is a two-week window in every new build when whole-home connectivity costs almost nothing to get right — after first-fix electrics start and before the plasterboard goes up. Miss it, and the same capability costs three to five times as much to retrofit, with cable trunking down freshly decorated walls. Here's the checklist we work to on plots across Marlow, Maidenhead and the Thames Valley.</p>

<h2>The new-build pre-wire checklist</h2>
<h3>1. Cat6 to every access-point position</h3>
<p>Wi-Fi that reaches every room of a modern family home comes from wired access points in the right ceilings — not from one router in the hallway cupboard. For a typical 4–5 bed house that means two to four ceiling positions, each with a Cat6 run back to the comms enclosure. The AP itself can be fitted at completion or by the purchaser later; the cable has to go in now.</p>
<h3>2. Data to the TV points, office and garage</h3>
<p>Anything that streams or works for a living deserves a wired point: main TV wall, study, and increasingly the garage — EV chargers and their load-management kit are network devices now.</p>
<h3>3. CCTV and doorbell positions</h3>
<p>Run Cat6 to the front-door soffit, drive-facing corners and any gate or outbuilding position. PoE cameras take power down the same cable, so there's no second circuit to add later.</p>
<h3>4. Door entry and gate pre-wire</h3>
<p>Plots with gated drives need containment to the gate line before the driveway is laid. This is the single most expensive thing to retrofit on the list.</p>
<h3>5. A real comms enclosure</h3>
<p>Not a consumer-unit afterthought: a ventilated enclosure with power, sized for a patch panel, a small switch and the broadband termination, somewhere that isn't the master bedroom wardrobe.</p>
<h3>6. Test, label, document</h3>
<p>Every run tested and labelled at both ends, with a per-plot as-built sheet. It's the difference between "pre-wired" as a sales line and pre-wired as something the purchaser's installer can actually use.</p>

<h2>Why builders bother: the sales-particulars line</h2>
<p>"Wired for whole-home Wi-Fi, CCTV and EV charging" is a differentiator that costs hundreds per plot, not thousands — and it kills the number-one post-completion tech complaint in larger new-builds, which is Wi-Fi that doesn't reach the back bedrooms. For developments around Marlow, Henley and Beaconsfield, where buyers expect to work from home properly, it earns its line on the brochure.</p>

<h2>How the trade arrangement works</h2>
<ul>
<li>We mark up AP, data, CCTV and door-entry positions on your drawings, per house type</li>
<li>Your electrician pulls alongside their own first fix using our containment spec — or we do the pull ourselves</li>
<li>We terminate, test, label and commission at second fix, to your programme</li>
<li>You get one fixed price per plot type, repeatable across the development</li>
</ul>
<p>If you're building in Buckinghamshire or Berkshire — a one-off self-build or a multi-plot development — <a href="/construction/">see our per-plot pre-wire packages</a>, read <a href="/services/networking/">how we design networks</a>, or <a href="/quote/?service=prewire&amp;property=new_build_dev&amp;source=blog-prewire-checklist">price your plots from the drawings</a>.</p>
"""


POSTS = [
    {
        "slug": "construction-site-cctv-hire-vs-buy",
        "title": "Construction Site CCTV: Hire or Buy? A Builder's Guide",
        "pillar": "security",
        "excerpt": (
            "What site CCTV hire really costs over a programme, when installed "
            "kit with gate ANPR wins, and the honest cases where hire still "
            "makes sense for Thames Valley builders."
        ),
        "meta_description": (
            "Site CCTV hire vs installed cameras for UK builders: real costs "
            "over a programme, gate ANPR benefits, and when hire still wins. "
            "Thames Valley guide."
        ),
        "content": POST_HIRE_VS_BUY,
        "published_at": at(2026, 7, 6),
    },
    {
        "slug": "anpr-building-sites-ico-obligations",
        "title": "ANPR on Building Sites: Your ICO Obligations, Explained",
        "pillar": "security",
        "excerpt": (
            "Gate ANPR counts as processing personal data. The five things the "
            "ICO expects from a construction site running number-plate "
            "recognition — and who should do the paperwork."
        ),
        "meta_description": (
            "Running ANPR on a construction site? ICO registration, DPIA, "
            "signage and retention rules explained in plain English for UK "
            "builders and site managers."
        ),
        "content": POST_ANPR_ICO,
        "published_at": at(2026, 7, 13),
    },
    {
        "slug": "new-build-pre-wire-checklist",
        "title": "New-Build Pre-Wire: What to Run Before the Plasterboard",
        "pillar": "networking",
        "excerpt": (
            "The six-point structured cabling checklist for new-build plots — "
            "access points, CCTV, door entry and comms enclosure — and why "
            "first fix is the only cheap moment to do it."
        ),
        "meta_description": (
            "New-build pre-wire checklist for builders: Cat6 to APs, CCTV and "
            "door entry before plasterboard. Per-plot structured cabling for "
            "Thames Valley developments."
        ),
        "content": POST_PREWIRE,
        "published_at": at(2026, 7, 20),
    },
]


def seed_posts(apps, schema_editor):
    BlogPost = apps.get_model("core", "BlogPost")
    for data in POSTS:
        defaults = {k: v for k, v in data.items() if k != "slug"}
        defaults.setdefault("author", "Marco Baldanza")
        BlogPost.objects.update_or_create(slug=data["slug"], defaults=defaults)


def remove_posts(apps, schema_editor):
    BlogPost = apps.get_model("core", "BlogPost")
    BlogPost.objects.filter(slug__in=[p["slug"] for p in POSTS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0014_construction_lead_choices"),
    ]

    operations = [
        migrations.RunPython(seed_posts, reverse_code=remove_posts),
    ]
