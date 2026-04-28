"""Seed the 12 launch blog posts.

Idempotent — uses update_or_create on slug, so re-applying on a fresh DB
or after editing copy in this file is safe.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

from django.db import migrations


LONDON = ZoneInfo("Europe/London")


def at(year, month, day, hour=9, minute=0):
    return datetime(year, month, day, hour, minute, tzinfo=LONDON)


# ---------------------------------------------------------------------------
# Post content
# ---------------------------------------------------------------------------

POST_1_CONTENT = """
<p>If I had a pound for every property I've walked into across Berkshire and Buckinghamshire where the homeowner has accepted bad Wi-Fi as "just how it is", I could probably retire early. The truth is, most home Wi-Fi is held back by three specific problems — and once you understand them, you'll never be satisfied with patchy coverage again.</p>

<h2>1. The ISP router is doing too much</h2>
<p>The little white box your provider sent in the post is competent but a generalist. It handles your connection, hands out IP addresses, broadcasts Wi-Fi from a single corner of your house, and tries to do a passable job of all of it. In a small flat, that's fine. In a four-bed house in Beaconsfield with thick walls and a garden office, it was never going to win.</p>
<p>The fix isn't a bigger router. It's separating the jobs: let the ISP gateway handle the internet connection, and let dedicated access points handle the Wi-Fi. Moving Wi-Fi off the gateway and onto purpose-built APs in the right places solves more "my Wi-Fi is rubbish" complaints than any other single change we make.</p>

<h2>2. One radio, expecting full coverage</h2>
<p>A typical home router puts out around 20–30dBm of signal from one spot. Wi-Fi attenuates fast through walls, and faster still through old plaster, lath-and-lath partitions, or the steel-studded walls you find in a lot of newer extensions. By the time the signal reaches the back of the ground floor it's weak. By the time it climbs the stairs to a child's bedroom at the rear, you've got a barely usable trickle.</p>
<p>The fix is multiple access points wired back to a central switch — not a chain of "extenders" that halve your bandwidth at every hop. With three or four properly placed APs you can flood a 3,000 sq ft property with strong, consistent Wi-Fi. We fly a drone survey before drilling, because the obvious spot is surprisingly often the wrong spot.</p>

<h2>3. Channel pollution and 2.4GHz nostalgia</h2>
<p>If you live anywhere remotely populated — and most of Bucks counts — your Wi-Fi is competing with every neighbour's network for airtime. The 2.4GHz band is especially bad: only three non-overlapping channels, used by every cheap IoT device, microwave and baby monitor on the planet. Most routers run on "auto" and pick the worst channel out of inertia.</p>
<p>The fix is split networks: a fast 5GHz (or 6GHz) network for everything modern, and a slower 2.4GHz network reserved for older smart-home devices. Channels are tuned manually after a spectrum scan of the area, and we leave a written record so you can re-check it in a year.</p>

<h2>Why mesh isn't usually the answer</h2>
<p>"Why not just buy a mesh kit from John Lewis?" — fair question. Mesh is fine for small flats. But in any property big enough to actually need help, the mesh radios end up backhauling over Wi-Fi, meaning your "fast" network is sharing airtime with every device that connects to it. The result is better than one router, but nowhere near what a proper wired install delivers.</p>

<h2>What "good" Wi-Fi looks like</h2>
<p>Once it's right you stop noticing it — which is the whole point. No buffering on the upstairs TV. No "I'll just go to the kitchen, the signal's better there" mid-Zoom. No ten-minute reboot ritual when the hub locks up.</p>
<p>A typical Berkshire or Bucks home with three or four UniFi access points, a managed switch and a Cloud Gateway lands somewhere between £800 and £2,000 including cabling and labour. It lasts for years and pays for itself the first time you don't get a "dropping connection" call from a parent working from home.</p>

<h2>If your Wi-Fi is letting you down</h2>
<p>If you're in Berkshire, Buckinghamshire or the surrounding area and tired of patchy coverage, <a href="/contact/">get in touch</a>. We'll walk the property, fly a drone survey and tell you honestly whether it's a £200 fix or a proper rebuild. No pressure, no day rates.</p>
"""

POST_2_CONTENT = """
<p>The pitch around smart home automation usually focuses on convenience — turn on the lights with your voice, never reach for a thermostat again. That's all true, but the most under-sold benefit is unglamorous: a properly automated house can save you real money, every month, with no compromise to comfort.</p>

<p>Here are five automations we install regularly across Berkshire and Bucks that pay for themselves within a year or two.</p>

<h2>1. Per-room heating schedules</h2>
<p>Most homes still heat the whole house to the same setpoint at the same time, regardless of who's where. With smart TRVs (radiator valves) on each radiator and a Home Assistant schedule, every room follows its own routine: kids' bedrooms warm up at 7am, the living room at 5pm, guest rooms stay off unless someone's home.</p>
<p>The savings come from never heating empty space. We've seen 15–25% knocked off gas bills the winter after a proper TRV install — and the comfort improvement is dramatic, because rooms hit the right temperature when you actually want them to.</p>

<h2>2. Presence-based lighting</h2>
<p>Motion-triggered lights aren't new, but most installations are blunt: they turn on full when anyone walks past. A presence-based setup is smarter. Hallway and landing lights ramp to 100% in the day, 30% in the evening, and 5% (just enough to navigate) overnight. Bathrooms turn off automatically thirty seconds after you leave. Outdoor lights only fire if it's actually dark <em>and</em> someone is there.</p>
<p>You stop paying to light empty rooms. Combined with LED bulbs across the house, this typically saves £50–£150 a year for a family home — small, but a clean win you'll never have to think about again.</p>

<h2>3. Energy monitoring on the consumer unit</h2>
<p>You can't manage what you can't measure. A clamp-on monitor (we use Shelly EM or the integrated UniFi power monitoring) on each circuit feeds Home Assistant a live picture of where your electricity is going. The first time it surfaces a dehumidifier left on in a forgotten cupboard, or a freezer that's drawing twice what it should because the seal has gone, the kit has earned its keep.</p>
<p>Quiet observation for a month usually finds two or three "always-on" offenders that knock 5–15% off the bill once they're sorted.</p>

<h2>4. Smart plugs to kill standby</h2>
<p>"Vampire" loads — TVs, set-top boxes, games consoles, kitchen gadgets in standby — typically account for 5–10% of a household's electricity. A handful of smart plugs that cut power to entire AV stacks overnight (or whenever Apple TV reports nothing's playing) is one of the easiest wins in the whole smart-home toolbox.</p>
<p>Pro tip: avoid auto-cutting anything with a clock or firmware that doesn't like rude shutdowns. Stick to TVs, audio, kitchen gadgets and chargers.</p>

<h2>5. EV charging on cheap-rate windows</h2>
<p>If you've got an EV, the single biggest automation win in the country is charging only during your tariff's cheap window. Octopus Go, Intelligent Octopus, Cosy or similar can drop the per-kWh price to a fraction of peak. Home Assistant or the charger itself (Zappi, Ohme, Hypervolt) can be set to only draw power inside that window, and to top up to a target rather than a fixed time.</p>
<p>For a household doing 8,000 EV miles a year, the saving versus charging at peak is typically £400–£700. By far the biggest line item on this list — and the easiest to set up.</p>

<h2>Putting it together</h2>
<p>None of these need an expensive whole-home rebuild. We routinely retrofit them into existing properties — Home Assistant runs on a small mini-PC in your comms cupboard, the rest is sensors, valves and plugs. A typical "save-money" automation package across the five items above runs £1,500–£3,000 installed, including hardware.</p>
<p>If you'd like to see what your house could be doing automatically — and roughly what it would save — <a href="/contact/">drop us a line</a>. We cover Berkshire and Buckinghamshire for on-site work and we're happy to do a quick chat first to see if it's worth a visit.</p>
"""

POST_3_CONTENT = """
<p>Most home break-ins through technology aren't dramatic. They're slow, opportunistic and start with a forgotten setting. Whether you've got a single Wi-Fi router or a full smart-home stack, here's the five-point checklist we run through on every home network audit in Berkshire and Bucks.</p>

<h2>1. Default admin passwords</h2>
<p>Sounds obvious, but it's the single most common issue we find. The router from your ISP, the IP camera you bought on Amazon, the cheap smart plug, the network switch in the garage — many of them ship with a default admin password that's printed on a sticker on the bottom or, worse, the same across every unit.</p>
<p>Change every one. Use a password manager (Bitwarden or 1Password) so you don't have to remember them. While you're there, disable any "remote management" or "cloud login" feature you don't actually use — those are how the bots find their way in.</p>

<h2>2. A separate guest Wi-Fi network</h2>
<p>Your guest Wi-Fi shouldn't see your main network. If a friend joins with a phone that's silently running malware, or your kids' friends bring a compromised laptop to a sleepover, you don't want them in the same broadcast domain as your NAS.</p>
<p>On a UniFi setup it's a couple of clicks to create a guest network with isolation enabled. On consumer routers, look for "guest mode" or "AP isolation" — turn both on. Give it a different SSID and password, and rotate the password every six months.</p>

<h2>3. IoT isolation (VLAN segregation)</h2>
<p>This is the one most home networks get wrong. Smart bulbs, doorbells, robot hoovers and TVs typically have terrible long-term security — manufacturer drops support, firmware stops updating, vulnerabilities pile up. If those devices share a network with your laptop, your photos and your work files, a single compromised IoT device becomes a foothold for everything else.</p>
<p>The fix is a separate VLAN — a virtual network — for IoT. They get internet (where they need it), but can't see anything else. We set this up by default on every install, and retro-fit it into existing networks for £300–£500 depending on hardware.</p>

<h2>4. Firmware updates, set to automatic where you can</h2>
<p>Routers, access points, switches, cameras, the lot. Each has a firmware that ships with known bugs by the time it's a year old. Most modern kit will auto-update if you let it; check that's enabled, then check again in three months that it actually has updated.</p>
<p>For older devices that don't auto-update, calendar a quarterly check. Anything that hasn't had a firmware release in the last 18 months is probably abandoned by the manufacturer — replace it before it becomes a problem.</p>

<h2>5. VPN, not port forwarding</h2>
<p>The dangerous habit we still see in 2026: opening a port on the router so you can reach a home server, NAS or camera from outside. Don't. Every open port is a published invitation for an automated scanner to try every credential they know.</p>
<p>Use a VPN instead. WireGuard built into a UniFi gateway, or Tailscale, or UniFi Site Magic — they all let you reach your home network from outside as if you were on the sofa, without exposing a single port to the open internet. Setup is genuinely an evening's work for someone comfortable with networking, or a couple of hours of our time if you'd rather not.</p>

<h2>The "I'm small, why would they bother?" trap</h2>
<p>Almost no home network is targeted by name. They're caught in mass scans of millions of IPs, looking for the easy ones. The point of these five steps isn't to be unhackable — it's to be enough effort that the bots move on to the next address.</p>

<h2>If you want a second pair of eyes</h2>
<p>Our network security audit (£200) is a 90-minute on-site visit, covering all five points above plus a few we've left off this list, with a written report afterwards. Available across Berkshire and Buckinghamshire — <a href="/contact/?service=security">book one here</a>.</p>
"""

POST_4_CONTENT = """
<p>Hiring a web developer is one of those jobs that goes wrong quietly. The site launches, things look fine, and then a year later you discover that the "developer" has disappeared, the code is locked behind a CMS you can't access, and quotes for any change come back at four times the original price. Here are the questions we'd ask before you sign anything.</p>

<h2>1. Can I see three sites you've built that are still running?</h2>
<p>Anyone can show a portfolio of pretty designs. The harder question is which sites they shipped two or three years ago and still work, still get updated, and still talk to the developer. A site that looks polished on day one and unmaintained on day 365 isn't a win.</p>
<p>Ask for live URLs and feel free to email the businesses behind them. A developer worth hiring will be relaxed about you doing that.</p>

<h2>2. What's the stack — and why did you choose it?</h2>
<p>You don't need to understand the answer in detail, but the developer should be able to explain it without resorting to buzzwords. "We use Django because we know it deeply and most of what you need is built in" is a good answer. "We use [obscure framework] because it's the latest thing" is a warning sign — you don't want your business sitting on someone else's experiment.</p>
<p>Proven tech is good tech. The well-trodden choices are usually still being actively maintained and have a market of developers who can pick up the codebase if your relationship with the original team ever ends.</p>

<h2>3. Who owns the code, the domain and the hosting?</h2>
<p>You should. Always. The contract should state that the source code is yours, the domain is registered in your name (not the agency's), and the hosting account is in your name with you as the admin user.</p>
<p>"We host it for you" is fine as a service offering, but you must be able to walk away with everything if you ever need to. If a developer gets cagey about this, walk away now, not later.</p>

<h2>4. What does ongoing support look like?</h2>
<p>A website is not a one-and-done deliverable. Dependencies need patching, the CMS needs updating, the hosting bill needs paying, the contact form might break, the SSL certificate has to be renewed. Find out before you sign:</p>
<ul>
  <li>Is there a support plan? What's it cost a month?</li>
  <li>How fast do you respond to "the site's down"?</li>
  <li>Who is "you" in twelve months — same engineer or whoever's free?</li>
</ul>
<p>For a small business in Reading or Marlow, expect £30–£100 a month for a support plan that includes hosting, monitoring, security patches and a small bucket of changes. Less than that, and you're probably not getting much. More, and you should be getting proper SLAs in writing.</p>

<h2>5. Fixed-price or day rate?</h2>
<p>Both can work, but they suit different situations. For a defined site with a clear spec, fixed-price is friendlier — you know what it costs, the developer is incentivised to be efficient. For an evolving product where the scope will change, day-rate billing is fairer (you don't want a developer rushing to hit a budget on something half-defined).</p>
<p>Either way, get the rate, the estimate, and the change-order process in writing. "We'll figure it out as we go" is how relationships sour.</p>

<h2>6. What does handover look like if I leave?</h2>
<p>Last question, and the answer reveals more than you'd think. Good developers will say something like: "The repo is yours, the deployment runs from a documented Dockerfile, the runbook lives in the repo, and we'd help your next engineer get started." Bad developers will say: "Why would you leave?"</p>

<h2>Practical sounds like the right word</h2>
<p>Notice that none of these questions are about design. Design matters, but you can usually tell that from a portfolio. The questions above are about whether the relationship will still be working in two years' time.</p>
<p>If you're a small or medium business in Berkshire or Buckinghamshire and you'd like to chat about a build with someone who actually answers their email, <a href="/contact/?service=development">drop us a line</a>. We don't pitch every project — but if we say yes, we mean it.</p>
"""

POST_5_CONTENT = """
<p>UniFi is the brand we install most often. It's also the brand most people have heard of without knowing what it does. So here's the no-nonsense guide — what UniFi actually is, why it beats consumer mesh, what the bits do, and what a typical home install costs in Berkshire or Bucks.</p>

<h2>What is UniFi?</h2>
<p>UniFi is the prosumer line from Ubiquiti — an American networking company. It started as Wi-Fi gear for businesses (the access points you see hanging from the ceilings of hotels, gyms and offices) and grew into a full ecosystem covering routing, switching, Wi-Fi, CCTV, access control and more. All of it is managed through a single dashboard, the UniFi Network controller, that runs locally on a piece of UniFi hardware in your house.</p>
<p>That last bit matters. Your network keeps working if your internet drops, the controller doesn't need a cloud subscription, and you can hand off the whole thing to another engineer if we ever fall out — it's all standards-based.</p>

<h2>Why it beats mesh</h2>
<p>The honest answer: for small flats, a mesh kit is fine. For anything bigger than a two-up two-down, mesh starts to fall over. Reasons:</p>
<ul>
  <li><strong>Wireless backhaul halves your throughput.</strong> Mesh nodes talk to each other over Wi-Fi by default, sharing airtime with everything else.</li>
  <li><strong>No real network management.</strong> No VLANs, limited firewall, opaque updates, weak guest isolation.</li>
  <li><strong>Cheap radios.</strong> Mesh is built to a £300 price point. UniFi APs are built to be screwed to a hotel ceiling and forgotten about.</li>
  <li><strong>Lock-in.</strong> If your mesh vendor goes bust or pulls cloud features, you're stuck.</li>
</ul>

<h2>The bits, explained</h2>

<h3>Cloud Gateway</h3>
<p>Your router, firewall and controller in one box. Plug your fibre or VDSL into one side, plug everything else into the other. The UCG-Ultra (£165) covers most homes; the Dream Machine Special Edition (£495) suits larger properties or anyone wanting Protect CCTV built in.</p>

<h3>Switch (PoE)</h3>
<p>The traffic cop for everything wired. PoE means it sends power down the Ethernet cable to your access points and cameras, so they don't need plug sockets. An 8-port PoE switch is around £170; 24-port for bigger homes around £390.</p>

<h3>Access Points</h3>
<p>The actual Wi-Fi radios. Mounted on the ceiling or high on a wall, fed by a single Ethernet cable. The U7 Pro (£185) is our default for homes — Wi-Fi 7, very fast, sensible coverage. Plan one AP per floor minimum, more for larger or tricky-shaped properties.</p>

<h3>NVR (optional)</h3>
<p>For UniFi Protect CCTV. Cloud Key Gen2 Plus (£200) for a small home camera setup, UNVR Pro (£600) for larger sites or hotels.</p>

<h2>Typical home costs</h2>
<p>For a small home (1–3 access points):</p>
<ul>
  <li>Cloud Gateway, 8-port PoE switch, 2 access points, structured cabling, install and configuration: <strong>£800 – £1,200</strong></li>
</ul>
<p>For a medium home (4–6 access points), typically a 4 or 5-bed property with garden office:</p>
<ul>
  <li>Cloud Gateway, larger switch, 4 access points, garden office cable run, install and configuration: <strong>£1,500 – £2,500</strong></li>
</ul>
<p>For a large home or small office (7+ access points):</p>
<ul>
  <li>Pricing from <strong>£3,000</strong> — depends on the number of APs, cable runs and structured cabling required (typically £60 per drop).</li>
</ul>

<h2>Why we recommend it</h2>
<p>Three reasons. One: it works, year after year, with very little drama. Two: every site we install is documented and we (or the next engineer) can pick it up cold. Three: there's no recurring cost — you own the kit, no monthly cloud subscription. The dashboard runs on hardware in your house and that's the end of it.</p>

<h2>What it doesn't do well</h2>
<p>Worth being honest. UniFi is overkill for a one-bed flat (a £150 mesh kit will do fine), and the controller has a learning curve that's friendlier than most enterprise gear but still not "consumer". If you want to manage it yourself, you'll need to spend an evening or two getting comfortable. If you don't, that's what we're here for.</p>

<h2>Want a UniFi install in Berks or Bucks?</h2>
<p><a href="/contact/?service=networking">Get in touch</a> and we'll come and walk the property. Drone survey, written quote, fixed price. No subscriptions, no day rates.</p>
"""

POST_6_CONTENT = """
<p>"Which smart home platform should I pick?" is the question we get asked more than any other. There's no single right answer — but there are right answers for specific situations. Here's the honest comparison we'd give a friend, with the recommendation we'd actually make.</p>

<h2>The quick verdict</h2>
<ul>
  <li><strong>Home Assistant</strong> — most flexible, local-first, future-proof. Has a learning curve. Best for households who want it to actually do useful things.</li>
  <li><strong>Apple HomeKit</strong> — easiest, prettiest, most private of the cloud options. Limited automation. Best for "I just want it to work" Apple households.</li>
  <li><strong>Samsung SmartThings</strong> — middle ground, but cloud-dependent and has had several rocky years of acquisitions and platform changes. Hard to recommend in 2026.</li>
</ul>

<h2>Apple HomeKit</h2>
<p>HomeKit is the polished one. If you're already on iPhone and Apple TV, adding a few HomeKit-compatible bulbs and plugs is a one-tap experience. The Home app is genuinely good, scenes are easy, and your data mostly stays local — voice commands go via Apple's privacy-respecting servers, but the actual control is on-device.</p>
<p>The catch: HomeKit's automation engine is limited. You can do "if motion then light", but anything more complex — "if motion AND it's after sunset AND the alarm is disarmed AND no one's already in the room" — gets clunky fast. Device support is also narrower than the competition.</p>
<p><strong>Pick HomeKit if:</strong> you're an Apple household, you mostly want voice control and basic scenes, you don't want to think about the platform itself.</p>

<h2>Samsung SmartThings</h2>
<p>SmartThings was the obvious "open" choice for a long time. It was bought by Samsung, then re-architected, then re-architected again. The app has changed three times in five years. Some integrations broke; some came back. Routines that used to run locally now require the cloud.</p>
<p>It still works, and the device support is broad. But the trajectory is towards "Samsung's smart-home platform for Samsung TVs and Samsung fridges", and we'd be reluctant to bet a household on it now.</p>
<p><strong>Pick SmartThings if:</strong> you're already deep in the Samsung ecosystem and accept the cloud dependency.</p>

<h2>Home Assistant</h2>
<p>Home Assistant is the open-source platform that runs the rest of our installs. It's not as instantly pretty as HomeKit, but two things make it different.</p>
<p><strong>Local-first.</strong> The brain runs on a small computer in your house — a mini-PC, a Home Assistant Yellow, or similar. Your scenes work whether your internet is up or down. Your data doesn't leave the house unless you explicitly send it somewhere. If a vendor pulls a cloud API tomorrow, your house carries on.</p>
<p><strong>Anything talks to anything.</strong> Home Assistant has integrations for thousands of devices and protocols — Zigbee, Z-Wave, Matter, Lutron, Hue, plus dozens of one-off integrations for cars, solar inverters, energy meters, even your Octopus tariff. If a device exists, there's a fair chance it can be wired in.</p>
<p>The trade-off is the learning curve. Home Assistant assumes you'll get comfortable editing configuration files eventually. For people who don't want to do that — which is most of our clients — we set it up, write the automations, and leave a friendly dashboard behind.</p>
<p><strong>Pick Home Assistant if:</strong> you want serious automation, local control, no vendor lock-in, and either you're willing to tinker or you have someone who'll do the tinkering for you.</p>

<h2>Our recommendation</h2>
<p>For most clients across Berkshire and Bucks, we install Home Assistant. The local-first, no-cloud-subscription, anything-talks-to-anything model just suits how British houses live. We pair it with HomeKit on top — Home Assistant exposes its devices to Apple, so you still get "Hey Siri, goodnight" voice control, with all the smart logic underneath.</p>
<p>For very simple homes — one phone household, a handful of lights, no climate or security — straight HomeKit is fine and cheaper. We'll happily say so on the consult call.</p>

<h2>What about Google Home / Alexa?</h2>
<p>They're voice front-ends, not platforms. Both can sit on top of Home Assistant if you want a non-Apple voice option. We don't recommend running a smart home from inside the Google or Alexa app — the integrations are shallower and the lock-in is real.</p>

<h2>Want help choosing?</h2>
<p>If you're starting out — or stuck on a SmartThings setup that keeps changing under you — <a href="/contact/?service=automation">drop us a line</a>. We'll talk through what you've got, what you actually want it to do, and whether a switch is worth it. Local visits across Berkshire and Buckinghamshire.</p>
"""

POST_7_CONTENT = """
<p>Most home CCTV systems are overspec'd in some places and useless in others. The cause is almost always the same: cameras chosen first, placement worked out second. Done the other way round — coverage zones first, cameras second — you get a system that actually catches what you need. Here's how we plan installs in Bucks and Berks, the way we'd plan our own.</p>

<h2>Start with what you're trying to see</h2>
<p>"Catch a burglar" is too vague to plan around. Be specific. For a typical home install, we end up with three or four named zones:</p>
<ul>
  <li><strong>Approach zones</strong> — driveway, front gate, alley to the back. The path anyone (welcome or not) takes.</li>
  <li><strong>Access points</strong> — front door, back door, side gate, garage door. Where someone would actually try to get in.</li>
  <li><strong>Vulnerable zones</strong> — ground-floor windows, side returns, the lean-to roof someone could use to reach a first-floor window.</li>
  <li><strong>Asset zones</strong> — the workshop, the garden tools shed, the EV on the drive, anything specifically worth nicking.</li>
</ul>
<p>Each zone wants <strong>identification</strong> footage (clear face, readable plate) at the choke point and <strong>overview</strong> footage of the whole area. Lump the two together and you'll end up with cameras that show you a small grey shape running away.</p>

<h2>Height and angle</h2>
<p>Mounting cameras too high is the most common mistake. A camera 12 feet up gets you the top of a hat. We aim for 8–10 feet for cameras meant to identify people — high enough to be out of casual reach, low enough that the lens is roughly at face height as someone walks past.</p>
<p>Angle matters too. Pointing a camera straight at the front door tells you someone's there but not who they are. Angled across the door, perpendicular to the approach path, you catch the face as they walk towards it. The same logic applies for vehicles — across the drive, not along it.</p>

<h2>Beware the sun</h2>
<p>South-facing cameras get the morning or evening sun straight in the lens. Backlit footage is useless: faces become silhouettes, plates become bright rectangles. Plan camera positions so the sun is behind them, or pick spots under eaves/overhangs that shade the lens during peak hours.</p>
<p>Same goes for porch lights or floodlights mounted next to a camera — they'll wash out the sensor at night. Floodlights belong twenty feet away from the camera that's filming the area they're lighting.</p>

<h2>Night vision: IR or spotlight?</h2>
<p>Most modern cameras do both. Infrared (IR) is invisible to the naked eye and lights the scene up to maybe 30 feet — great for unobtrusive coverage, but everything's monochrome. Spotlight cameras kick out white light when triggered — colour at night, but obvious to anyone in the area. Spotlights also work as a deterrent, which has real value.</p>
<p>We typically use IR for back-of-property cameras (where you don't want to advertise their presence) and spotlight for front-of-house and driveway (where deterrence is part of the job).</p>

<h2>The drone survey</h2>
<p>Once we've got rough zones, we fly an aerial drone survey before drilling anything. Two reasons. First, it surfaces blind spots you can't see from the ground — roof angles, overhanging trees that hide an approach, neighbouring sight-lines. Second, it lets us pre-plan cable routes and PoE distances. By the time install day comes round, we know exactly where every camera goes and how the cable runs.</p>
<p>The aerial imagery is handed over to you with the runbook — useful for insurance, useful if we ever expand the system, useful as a record of the property as it was.</p>

<h2>What about doorbells?</h2>
<p>A video doorbell is a useful supplement, not a replacement. They're great at "person at the door" detection and two-way audio, but the lens position is fixed, the field of view is wide-but-shallow, and most are battery-powered (which means they miss things while waking up). For a serious install, the doorbell sits on top of a proper PoE camera covering the same approach.</p>

<h2>What we'd never do</h2>
<ul>
  <li>Sell you cameras with a mandatory cloud subscription. Footage stays on your kit.</li>
  <li>Mount a camera at a height where you can't physically reach it to clean the lens.</li>
  <li>Skip the cabling and use Wi-Fi cameras for the main install. Fine for sheds; not for the front door.</li>
</ul>

<h2>Want a CCTV plan for your property?</h2>
<p>Our security assessment is £150 — we'll walk the property, fly the drone, talk you through the zones, and write up a plan with hardware costs. Across Berkshire, Buckinghamshire and the surrounding area. <a href="/contact/?service=security">Book one here</a>.</p>
"""

POST_8_CONTENT = """
<p>"It's working, why am I paying you?" is the most reasonable question a support-plan customer can ask. The honest answer: you're paying for the things you'd never know to do, plus the speed at which we can fix the things you do know about. Both matter more than they look.</p>

<h2>Firmware patches close real holes</h2>
<p>Every router, access point, switch, NVR, camera and smart plug runs firmware. Every firmware has bugs. Vendors release updates monthly or quarterly that close known security vulnerabilities — but they only help if someone applies them. The number of homes we audit where the router hasn't been patched in two years is uncomfortable.</p>
<p>On a support plan, we either auto-apply updates (where the kit supports it safely) or check them on a quarterly cycle. You'll never see the work, because the work is preventing problems before they happen.</p>

<h2>Proactive monitoring catches things while they're small</h2>
<p>Networks don't usually fail dramatically. They limp. A single AP starts dropping packets, a switch port starts re-transmitting, a CCTV camera quietly stops recording. By the time a homeowner notices, the underlying issue has been brewing for weeks.</p>
<p>Care-plan customers have their network telemetry watched continuously. We see the AP that's started dropping packets the day it starts. We see the camera that hasn't recorded in 24 hours. We see the WAN that's been throttling for an hour. Most of these get fixed before you notice — which is exactly the point.</p>

<h2>Backups you forgot you needed</h2>
<p>The smart-home brain. The Home Assistant config. The UniFi controller. The media server. All have backups — until they don't. We've turned up to homes where a hard drive failure wiped six months of camera footage, or a botched firmware update bricked the controller and the last backup was from before half the network was added.</p>
<p>On a care plan, your important configs are backed up to encrypted off-site storage automatically. When something fails, the recovery is an hour, not a weekend.</p>

<h2>The cost of "I'll just figure it out"</h2>
<p>You can DIY most of this. Honestly, you can. The question is whether you'll <em>actually</em> do it. The pattern we see is: "I'll handle it myself" → six months of intent → first failure → no backup, no recent firmware, no documentation → £600 of emergency labour to rebuild what could have been £29 a month of preventative care.</p>
<p>Even if you're technically capable, a support plan is buying back your weekends.</p>

<h2>Quick response when something does go wrong</h2>
<p>Stuff breaks. WAN goes down, a switch fails, lightning takes out a PoE injector. Without a plan, you call around, find an engineer, explain everything from scratch, schedule a visit. With one, you message the same engineer who already knows your setup, has the runbook open, and is on the case within hours.</p>
<p>For a household running a business from home, or a small business itself, the difference between "back online by lunch" and "back online next Tuesday" is the entire value of the plan.</p>

<h2>What our plans look like</h2>
<p>We keep this deliberately simple — three tiers, monthly billed:</p>
<ul>
  <li><strong>Essential — £29/month.</strong> Automated monitoring, email support, quarterly health-check, firmware managed. Right for most homes.</li>
  <li><strong>Professional — £59/month.</strong> Adds same-day response, quarterly check-in call, an annual on-site visit, smart-home tweaks included. Right for households or small businesses that depend on the tech.</li>
  <li><strong>Enterprise — £149/month.</strong> Priority response, monthly check-in, quarterly on-site visit, full documentation kept up to date. Right for businesses or larger residential installs.</li>
</ul>
<p>All cancellable with 30 days' notice. Annual prepay knocks 10% off.</p>

<h2>"Won't it be working without you, eventually?"</h2>
<p>Yes — and we'll never sell anyone a care plan we don't think they need. If your network is small, simple, and you genuinely don't mind doing the four times a year of housekeeping, we'll say so on the call.</p>
<p>What we want to avoid is the situation where a homeowner who could clearly benefit doesn't, because nobody told them what they were missing. If you'd like a 15-minute chat about whether a plan makes sense for your setup in Berkshire or Bucks, <a href="/contact/?service=support">drop us a line</a>.</p>
"""

POST_9_CONTENT = """
<p>"VLAN" is one of those words that makes people glaze over. It sounds technical, it sounds optional, and most home networks live without one. But the moment you've got more than a couple of smart devices in your house, you're better off with one. Here's the plain-English version.</p>

<h2>What a VLAN actually is</h2>
<p>A VLAN — Virtual Local Area Network — is a way to slice a single physical network into multiple logical networks. Same Ethernet cables, same switches, same access points. But the devices on one VLAN can't see the devices on another, even though they're sharing the wires.</p>
<p>Imagine your house has one big shared wardrobe, where everyone keeps everything. That's a flat network. Now imagine you give each person their own labelled drawer, and only their key opens it. Same wardrobe, same shelves — but separated. That's VLANs.</p>

<h2>Why your home needs one</h2>
<p>The problem with a flat network is that any compromised device can talk to every other device. Your smart bulb from a no-name vendor, running 18-month-old firmware, is on the same network as your laptop, your NAS, your printer, your work files. If that bulb is compromised — and IoT devices get compromised constantly — the attacker is now inside your network.</p>
<p>VLANs limit the blast radius. Each device only sees what it needs to see. The bulb gets internet, but it can't see your laptop. The kids' Switch can play games, but can't browse your filing share. The work-from-home laptop is on its own network entirely.</p>

<h2>The VLANs we typically set up</h2>

<h3>1. Trusted (you and your family)</h3>
<p>Phones, laptops, tablets, work computers. The devices that handle sensitive data and that you trust to behave themselves. This is the only VLAN that can talk to the others.</p>

<h3>2. IoT</h3>
<p>Smart bulbs, smart plugs, robot vacuums, the TV, the speakers. Internet access yes; visibility into anything else, no. If any of them get compromised, they're contained.</p>

<h3>3. CCTV</h3>
<p>The cameras and the NVR. Heavily restricted — the cameras can talk to the NVR, the NVR can talk out for firmware updates, that's it. Camera traffic stays off your main network so it doesn't crowd your Zoom call.</p>

<h3>4. Guest</h3>
<p>The Wi-Fi password you give to friends and tradespeople. Internet only. No visibility into anything else — not even other guests.</p>

<h3>5. Work-from-home (optional)</h3>
<p>For households where someone runs a business or handles client data. Their laptop and printer get a VLAN of their own, isolated from kids' devices and IoT.</p>

<h2>Doesn't this make everything more complicated?</h2>
<p>For you? No — once it's set up, you don't see it. The Wi-Fi networks just look like normal SSIDs ("Home", "Home-IoT", "Home-Guest"). You connect a phone to the right one and it works. Same for plugged-in devices.</p>
<p>For us, setting it up is a couple of hours of upfront work and pays off forever. Adding a new IoT device is a one-tap operation rather than "should I really put this on my main network?".</p>

<h2>What about consumer routers?</h2>
<p>Most consumer routers don't really do VLANs. Some have a "guest network" option, which is a single primitive form of segmentation — fine as far as it goes, but not enough for a serious smart home. For proper VLANs you need a router/firewall and access points that support them, which in practice means a UniFi setup, a pfSense/OPNsense build, or similar.</p>

<h2>How we actually deploy them</h2>
<p>On a UniFi network, VLANs are set up in the controller. Each VLAN gets its own subnet, its own DHCP pool, and firewall rules controlling what can talk to what. Wi-Fi networks are bound to their VLANs at the SSID level. Wired ports can be locked to a specific VLAN, or trunked to support multiple.</p>
<p>The result, day to day: you've got four or five Wi-Fi names, all backed by the same access points, but each one is an isolated network. Bring a new IoT device home? Connect it to "Home-IoT". Job done.</p>

<h2>What if I've already got a flat network?</h2>
<p>Migrating an existing flat network to VLANs is a few hours of work, plus a brief outage as devices reconnect to their new SSIDs. We do this regularly — bring an existing UniFi or other prosumer network in line with proper segmentation. Typical job: £300–£500 depending on size.</p>

<h2>Want a VLAN setup in Berks or Bucks?</h2>
<p>If you've got a smart home that's grown organically and you'd like to tidy it up safely, <a href="/contact/?service=networking">drop us a line</a>. The audit is £200, the migration is usually £300–£500, and you'll never look at your network the same way again.</p>
"""

POST_10_CONTENT = """
<p>"Should we build an app or a website?" — the most common question we get from small businesses looking to invest in something digital. The honest answer in 2026 is "almost always a website first", but the genuinely useful answer needs more nuance. Here's how we'd talk it through with a client over coffee.</p>

<h2>Website: the default</h2>
<p>Almost every small business in Berkshire or Bucks needs a website before they need an app. A few reasons:</p>
<ul>
  <li>It's the front door. Customers Google you, click through, and decide whether to bother in seconds.</li>
  <li>It's accessible everywhere — phone, laptop, tablet, work computer. No download required.</li>
  <li>It's findable. SEO, Google Business, Maps integration — none of which apps get for free.</li>
  <li>It's cheaper. A polished marketing site for a tradesperson, gym or shop is £1,500 – £6,000. A mobile-app MVP starts at £8,000 — a full production app, £20,000+.</li>
</ul>
<p>If your problem is "people can't find us, and when they do they can't tell what we do" — you need a website, not an app.</p>

<h2>When mobile app actually wins</h2>
<p>An app is the right answer when:</p>
<ul>
  <li><strong>The user comes back daily or weekly.</strong> Booking apps, fitness apps, dog-walker tracking apps — repeated use justifies the friction of installing.</li>
  <li><strong>You need device features.</strong> Camera with GPS for property listings. Push notifications for time-critical alerts. Offline mode for use in poor-signal areas.</li>
  <li><strong>The user is captive and motivated.</strong> Your existing customers will install the app because it makes their life easier, not because they're browsing the App Store.</li>
</ul>
<p>If "How do I get people to install it?" is your hardest unsolved problem, you probably don't have an app problem yet — you've got a marketing problem.</p>

<h2>The middle ground: PWA</h2>
<p>Progressive Web Apps are websites that behave like apps. They install to your phone's home screen, work offline, can fire push notifications, and use camera/GPS. Crucially, they work cross-platform from a single codebase, and they cost a fraction of a native app.</p>
<p>For a lot of small businesses we end up here: a website-first build that adds PWA features for the small subset of users who want app-like behaviour. You get the SEO and findability of a website with the on-phone convenience of an app, for not much more than the website alone.</p>
<p>A PWA does not work for: complex apps that need deep iOS/Android integration, anything that has to be in the App Store for credibility (banking, regulated industries), or anything where you genuinely need top-tier performance for graphics.</p>

<h2>Costs in plain numbers (2026 prices)</h2>
<ul>
  <li><strong>Simple website (5–8 pages, CMS, contact form, SEO):</strong> £1,500 – £3,000.</li>
  <li><strong>Business website (10–20 pages, more complex CMS / integrations):</strong> £3,000 – £6,000.</li>
  <li><strong>Web application (e-commerce, customer portal, internal tools):</strong> £5,000 – £25,000+.</li>
  <li><strong>Mobile app, MVP (iOS + Android, cross-platform via React Native):</strong> £8,000 – £20,000.</li>
  <li><strong>Mobile app, full production:</strong> £20,000 – £50,000+.</li>
  <li><strong>SEO audit:</strong> £300 standalone. <strong>Ongoing retainer:</strong> £75/hour.</li>
</ul>
<p>Plus ongoing: hosting + support is £30–£100/month for a website, £100–£300/month for an app (App Store accounts, push services, crash monitoring, occasional iOS/Android update releases).</p>

<h2>Our default approach</h2>
<p>For most small Berkshire and Bucks businesses we'll recommend: <strong>start with a great website</strong>, designed to make money on day one (clear positioning, good SEO, easy contact). Six to twelve months in, look at the numbers — repeat visits, average session, what people came back for. <em>Then</em> decide whether an app would genuinely make their lives easier, or whether a PWA layer on top of the existing site would do the job.</p>
<p>We've turned down app projects where a website would clearly have done. We've also pushed clients to build apps where the use case was right. The honest answer depends on the actual users.</p>

<h2>Want to talk it through?</h2>
<p>If you're a Berks or Bucks business looking at something digital and you'd like a 30-minute call (no slide deck, no obligation) — <a href="/contact/?service=development">drop us a line</a>. The most useful conversation is usually the one before any quote gets written.</p>
"""

POST_11_CONTENT = """
<p>I served in the Royal Marines Information Systems branch — RMIS — for the better part of a decade, building and maintaining the networks and comms that the rest of the unit relied on. The kit was different from a UniFi rack in a Bucks loft, the consequences of failure considerably more serious. But the engineering instincts you pick up in that environment carry across straight into civilian work, and I think about them every time I plan a network for a family or a business.</p>

<p>Here's what stuck.</p>

<h2>Plan for the worst case, not the average case</h2>
<p>In a military context, "what happens if the link goes down" is a question you ask before, not after. Redundancy isn't a luxury, it's the default. You assume the bit you depend on will fail, and you design so that the system limps usefully along when it does.</p>
<p>That mentality changes how you plan a home install. We don't size a network to handle "everyone watching Netflix at 8pm on a normal Tuesday". We size it to handle "the kids' games console is downloading a 200GB update, the cleaner is on a video call, the camera system is uploading footage, and there's a router firmware update mid-process". The easy case looks comfortable; the awkward one is what tells you whether the kit is right.</p>

<h2>Document everything, because the next person isn't you</h2>
<p>In the field, you might hand off a system to someone who's never seen it before, in conditions where they can't ask you questions. So everything is documented — runbooks, network diagrams, credentials, the lot — and you assume the person reading it doesn't have the context you do.</p>
<p>Civilian tech is no different. Every install we do leaves the customer with a runbook. What's plugged into what. Where the cabling runs. Which credentials are stored in which password vault. What to do if the WAN drops. If our van went off the road tomorrow, the next engineer could pick up the customer's setup cold. That's not a nice-to-have. That's the deliverable.</p>

<h2>Train as you fight, sell what you use</h2>
<p>You don't introduce kit on the day of a deployment. You train on it, in conditions that approximate the real thing, until the muscle memory is there. The Marines call it "train as you fight, fight as you train". Civilian translation: don't sell a customer kit you haven't lived with yourself.</p>
<p>Every product we recommend is running in our own home, day in, day out. Every UniFi access point. Every Home Assistant integration. Every smart lock. If we wouldn't trust it for our own family, it doesn't get on a quote.</p>

<h2>Communicate up, not just down</h2>
<p>The military teaches you to keep the people who depend on you informed, even — especially — when something's going wrong. The instinct to hide problems while you fix them is human, and corrosive. Far better to say "this has gone wrong, here's what we're doing, here's the timeline" than to go quiet for a day and reappear with a fix.</p>
<p>I bring that into how we run support. If a customer's network has had a wobble overnight, they'll get a message before the kettle's on the next morning. Not because they asked. Because they shouldn't have to.</p>

<h2>Proven kit is good kit</h2>
<p>The flashy gear is rarely the dependable gear. In a military environment, you want the radio that's been in service for ten years, that engineers have rebuilt a hundred times, that has a known failure mode. Not the cutting-edge thing that nobody quite trusts yet.</p>
<p>The same applies to a home network. UniFi has been around. Home Assistant has been around. Cat6 has been around. Proven, well-understood, predictable. The reason we use these tools — instead of whatever was launched at IFA last September — is the same reason the Marines stuck with kit a decade old: <em>it works, and we know how it fails</em>.</p>

<h2>Standards survive when individuals don't</h2>
<p>This is the one I think about most. Personnel rotate. The unit's standards don't. The reason a system stays high-quality after handover is that the standard is institutional, not personal.</p>
<p>For a tiny business like Luma Tech, that translation is: write the standards down. Make them testable. Make them part of the deliverable. So that if Luma Tech grew to ten engineers tomorrow, the customer's experience would be the same on visit eleven as on visit one.</p>

<h2>Why I'm telling you this</h2>
<p>Because when people ask "why should I trust your install?", the honest answer isn't a portfolio. It's a way of working. The instincts above don't cost extra; they're just baked into how the job gets done. If you're looking at networks, smart home, or security in Berkshire and Buckinghamshire and you'd like that approach on your project, <a href="/contact/">get in touch</a>.</p>
"""

POST_12_CONTENT = """
<p>Smart locks are one of those product categories where the marketing has run ahead of the engineering. The pitch — keyless entry, audit trail, time-limited guest codes — is genuinely useful. The execution, on the cheap end of the market, is sometimes worse than the lock you'd be replacing. Here's the honest assessment.</p>

<h2>The honest answer</h2>
<p>Are smart locks secure? <strong>The good ones, yes — at least as secure as a decent traditional lock, and often more so.</strong> The bad ones can be defeated with a £20 gadget from Amazon. The difference is almost always price and brand, with very little middle ground.</p>

<h2>The four types of smart lock</h2>
<ul>
  <li><strong>Smart deadbolts.</strong> Replace the deadbolt entirely. Most secure form factor. American doors mostly use these.</li>
  <li><strong>Smart knobs / handles.</strong> Replace the handle and lock. Less common in the UK.</li>
  <li><strong>Retrofit smart locks.</strong> Sit over your existing internal thumb-turn and motorise it. Yale Linus and the August lock are this type. Popular in the UK because they don't change the door's external appearance and they keep your existing key for backup.</li>
  <li><strong>Full electronic locksets.</strong> Commercial-grade. Salto, Igloohome, Aqara. Designed for offices, Airbnbs, multi-occupancy.</li>
</ul>

<h2>What "secure" actually means here</h2>
<p>There are three threat models, and they want different things from a lock.</p>
<p><strong>Threat 1: opportunist physical attack.</strong> Someone trying to kick the door in, or pry it. The lock is rarely the weak point — the door, frame and strike plate are. A smart lock here is no worse than a traditional one, sometimes better (some retrofit locks lock the door faster than humans do).</p>
<p><strong>Threat 2: lock-picking / bumping.</strong> Old-school skilled attack. Many UK doors have euro-cylinder locks that can be snapped or picked. A retrofit smart lock that sits on top of an existing high-security cylinder (TS007 3-star) inherits the cylinder's security. A smart lock that <em>replaces</em> the cylinder needs to come with its own certification.</p>
<p><strong>Threat 3: digital attack.</strong> The new threat model. Bluetooth replay attacks, Wi-Fi MITM, default credentials, weak APIs. This is where the cheap end of the market falls down. We've seen budget smart locks unlocked with a £30 software-defined radio.</p>

<h2>What to look for</h2>
<ul>
  <li><strong>BSI / TS621 / Sold Secure rating</strong> — the UK certifications. If a smart lock isn't tested to one of these, it isn't insurance-rated.</li>
  <li><strong>Manual key fallback.</strong> Battery dies, internet drops, app crashes — you should still be able to get in with a key. This rules out a lot of "look, no keyhole!" marketing-led designs.</li>
  <li><strong>Auto-lock.</strong> Most break-ins via smart locks happen because the lock didn't engage when the door closed. Pick one that auto-locks 30 seconds after closing, every time, no exceptions.</li>
  <li><strong>Local control.</strong> The lock should work without needing to phone home. If the manufacturer's cloud goes down, you should still be able to use it. Bluetooth + local hub beats cloud-only every time.</li>
  <li><strong>Certificates / firmware updates.</strong> Look for a vendor with a track record of patching, not one whose product launched on Kickstarter and last shipped firmware in 2023.</li>
  <li><strong>Audit trail.</strong> A useful side effect of doing it right — you can see exactly when each code was used.</li>
</ul>

<h2>Models we'd actually fit</h2>
<ul>
  <li><strong>Yale Linus L2.</strong> The default residential retrofit choice in the UK. Sits over your existing thumb-turn, keeps your key, integrates with HomeKit, Alexa, Google, Home Assistant. £230ish installed.</li>
  <li><strong>Aqara U200 / U300.</strong> Newer Matter-compatible options, integrate cleanly with Home Assistant. Watch for firmware-update track record over the next year.</li>
  <li><strong>Igloohome.</strong> For Airbnb / short-let. Generates time-limited codes that work without internet. Useful when guests check in while you're abroad.</li>
  <li><strong>Salto.</strong> Commercial. The default for offices, gyms, multi-tenant buildings. Audit trail and integration is enterprise-grade.</li>
</ul>

<h2>What we'd avoid</h2>
<p>Anything from a brand you've never heard of, anything cloud-only, anything that's removed the keyhole entirely, anything that doesn't show a clear firmware update history on its support page. Cheap on Amazon Prime Day is a red flag, not a feature.</p>

<h2>Real-world use cases</h2>
<ul>
  <li>Holiday let in the Chilterns — guest codes that auto-expire, no key handover.</li>
  <li>Shared family home — kids each get their own code, you can see who came in when.</li>
  <li>Cleaner / dog-walker — code valid 8–11am Mondays only, automatically.</li>
  <li>Self-managed Airbnb — full audit trail, codes generated from your phone.</li>
</ul>
<p>Each of these justifies the price by themselves; together, the convenience is significant.</p>

<h2>Want a smart lock fitted in Berks or Bucks?</h2>
<p>We fit Yale Linus, Aqara, Salto and Igloohome — full install, integration with your existing smart home and security setup, manual key backup tested and handed over. <a href="/contact/?service=security">Drop us a line</a> for a fixed-price quote.</p>
"""


# ---------------------------------------------------------------------------
# Post metadata
# ---------------------------------------------------------------------------

POSTS = [
    {
        "slug": "why-your-home-wifi-isnt-as-good-as-it-could-be",
        "title": "Why Your Home Wi-Fi Isn't as Good as It Could Be",
        "pillar": "networking",
        "excerpt": (
            "Three reasons most home Wi-Fi underdelivers — and why a £20 mesh kit "
            "won't fix it for a Berkshire or Bucks family home."
        ),
        "meta_description": (
            "ISP routers, dead spots and channel pollution: the three reasons most "
            "home Wi-Fi disappoints, and what to do about it. Berkshire & Bucks."
        ),
        "content": POST_1_CONTENT,
        "published_at": at(2026, 4, 28),
    },
    {
        "slug": "smart-home-automations-that-save-money",
        "title": "5 Smart Home Automations That Actually Save You Money",
        "pillar": "automation",
        "excerpt": (
            "The under-sold benefit of a properly automated house: it saves you real "
            "money every month. Five automations that pay for themselves."
        ),
        "meta_description": (
            "Per-room heating, presence-based lighting, energy monitoring, smart "
            "plugs and EV charging — five automations that pay for themselves."
        ),
        "content": POST_2_CONTENT,
        "published_at": at(2026, 5, 5),
    },
    {
        "slug": "is-your-home-network-secure-checklist",
        "title": "Is Your Home Network Secure? A 5-Point Checklist",
        "pillar": "security",
        "excerpt": (
            "Default passwords, guest networks, IoT isolation, firmware updates and "
            "VPNs — the five-point audit we run on every home in Berks and Bucks."
        ),
        "meta_description": (
            "Five checks every home network should pass: default passwords, guest "
            "Wi-Fi, IoT isolation, firmware updates, VPN over port forwarding."
        ),
        "content": POST_3_CONTENT,
        "published_at": at(2026, 5, 12),
    },
    {
        "slug": "what-to-ask-before-hiring-a-web-developer",
        "title": "What to Ask Before Hiring a Web Developer",
        "pillar": "development",
        "excerpt": (
            "Six questions to ask before signing a web-dev contract — and the "
            "answers that should make you walk away."
        ),
        "meta_description": (
            "Six honest questions to ask any web developer before you sign — "
            "ownership, stack, support, pricing and handover."
        ),
        "content": POST_4_CONTENT,
        "published_at": at(2026, 5, 19),
    },
    {
        "slug": "complete-guide-to-unifi-for-homes",
        "title": "The Complete Guide to UniFi for Homes",
        "pillar": "networking",
        "excerpt": (
            "What UniFi is, why it beats consumer mesh, what each component does, "
            "and what a typical home install costs in 2026."
        ),
        "meta_description": (
            "A plain-English guide to UniFi for homes: what it is, why it beats "
            "mesh, what each component does, and 2026 pricing."
        ),
        "content": POST_5_CONTENT,
        "published_at": at(2026, 5, 26),
    },
    {
        "slug": "home-assistant-vs-smartthings-vs-homekit",
        "title": "Home Assistant vs SmartThings vs Apple HomeKit — Which Should You Choose?",
        "pillar": "automation",
        "excerpt": (
            "An honest comparison of the three smart-home platforms most homes end "
            "up choosing between — and the one we install most often."
        ),
        "meta_description": (
            "Home Assistant, SmartThings and Apple HomeKit compared: local vs "
            "cloud, device support, learning curve, and our honest pick."
        ),
        "content": POST_6_CONTENT,
        "published_at": at(2026, 6, 2),
    },
    {
        "slug": "home-cctv-camera-placement-tips",
        "title": "Planning Your Home CCTV System: Camera Placement Tips From a Professional Installer",
        "pillar": "security",
        "excerpt": (
            "Coverage zones, height, angle, sun, night vision and the drone "
            "survey — how we plan CCTV installs across Berks and Bucks."
        ),
        "meta_description": (
            "How to plan home CCTV that actually catches what matters: coverage "
            "zones, height, angles, sun, night vision and aerial surveys."
        ),
        "content": POST_7_CONTENT,
        "published_at": at(2026, 6, 9),
    },
    {
        "slug": "why-your-tech-needs-a-support-plan",
        "title": "Why Your Technology Needs a Support Plan (Even When Everything's Working)",
        "pillar": "support",
        "excerpt": (
            "What you actually pay for on a tech support plan — and why it costs "
            "more to skip one than to keep one."
        ),
        "meta_description": (
            "Firmware patches, monitoring, backups and quick response — the four "
            "things a tech support plan is really paying for."
        ),
        "content": POST_8_CONTENT,
        "published_at": at(2026, 6, 16),
    },
    {
        "slug": "what-is-a-vlan-and-why-your-home-needs-one",
        "title": "What Is a VLAN and Why Does Your Home Network Need One?",
        "pillar": "networking",
        "excerpt": (
            "VLANs in plain English — and why every smart home with more than a "
            "handful of devices is better off with them."
        ),
        "meta_description": (
            "A plain-English explanation of VLANs, why home networks need them, "
            "and how we deploy them on UniFi installs."
        ),
        "content": POST_9_CONTENT,
        "published_at": at(2026, 6, 23),
    },
    {
        "slug": "mobile-app-vs-website-which-do-you-need",
        "title": "Mobile App vs Website — Which Does Your Business Need?",
        "pillar": "development",
        "excerpt": (
            "When a website wins, when a mobile app wins, and the PWA middle "
            "ground that fits a lot of small Berks and Bucks businesses."
        ),
        "meta_description": (
            "Honest 2026 comparison: when small businesses need a website, when "
            "they need a mobile app, and when a PWA is the right middle ground."
        ),
        "content": POST_10_CONTENT,
        "published_at": at(2026, 6, 30),
    },
    {
        "slug": "what-the-royal-marines-taught-me-about-reliable-networks",
        "title": "What the Royal Marines Taught Me About Building Reliable Networks",
        "pillar": "general",
        "excerpt": (
            "Six engineering instincts I picked up in the Royal Marines that "
            "shape how Luma Tech does civilian network and smart-home work."
        ),
        "meta_description": (
            "Six lessons from a decade in the Royal Marines RMIS branch that "
            "carry straight into how we build reliable civilian networks."
        ),
        "content": POST_11_CONTENT,
        "published_at": at(2026, 7, 7),
    },
    {
        "slug": "smart-locks-are-they-actually-secure",
        "title": "Smart Locks: Are They Actually Secure?",
        "pillar": "security",
        "excerpt": (
            "An honest look at smart locks in 2026 — what makes a good one, what "
            "to avoid, and the four models we'd actually fit."
        ),
        "meta_description": (
            "Are smart locks secure? An honest 2026 assessment, the four "
            "threat models, what to look for, and the models we'd fit."
        ),
        "content": POST_12_CONTENT,
        "published_at": at(2026, 7, 14),
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
        ("core", "0002_blogpost"),
    ]

    operations = [
        migrations.RunPython(seed_posts, reverse_code=remove_posts),
    ]
