"""Static build for the Teleminds website.

    python3 build.py          # writes dist/
    python3 -m http.server 8080 --directory dist

Content lives in src/data/*.json (site details, offices, jobs) and src/blog/*.json.
Page markup is in this file so every page shares one header, footer and head.
"""
from __future__ import annotations

import html
import json
import shutil
from datetime import date
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).parent
SRC = ROOT / "src"
DIST = ROOT / "dist"

SITE = json.loads((SRC / "data/site.json").read_text())
JOBS = json.loads((SRC / "data/jobs.json").read_text())["jobs"]
POSTS = [json.loads(p.read_text()) for p in sorted((SRC / "blog").glob("*.json"))]
OFFICES = {o["id"]: o for o in SITE["offices"]}
YEAR = date.today().year

e = html.escape

# The original Teleminds logo, unchanged.
LOGO = f'<img src="/assets/img/logo.png" alt="{e(SITE["legalName"])}" width="190" height="84">'
DOTS = '<span class="dots" aria-hidden="true"><i></i><i></i><i></i></span>'
LIVE_DOTS = '<span class="dots live" aria-hidden="true"><i></i><i></i><i></i></span>'


def icon(name: str, tint: str = "blue", size: str = "", alt: str = "") -> str:
    cls = f"well t-{tint} {size}".strip()
    return f'<span class="{cls}"><img src="/assets/3d/{name}.png" alt="{e(alt)}" width="256" height="256" loading="lazy"></span>'


def img3d(name: str) -> str:
    return f'<img src="/assets/3d/{name}.png" alt="" width="256" height="256" loading="lazy">'


def maps_url(q: str) -> str:
    return f"https://www.google.com/maps/search/?api=1&query={quote(q)}"


def tel(phone: str) -> str:
    return "tel:" + phone.replace(" ", "")


NAV = [("Services", "/services/"), ("Careers", "/careers/"), ("Blog", "/blog/")]


def layout(path: str, title: str, description: str, body: str, *, noindex: bool = False, jsonld: str = "", preload: str = "") -> str:
    url = SITE["domain"] + path
    nav = "".join(
        f'<li><a href="{href}"{" aria-current=\"page\"" if path.startswith(href) else ""}>{label}</a></li>'
        for label, href in NAV
    )
    full_title = title if title.startswith(SITE["legalName"]) else f"{title} | {SITE['legalName']}"
    offices_foot = "".join(
        f'<li><a href="{tel(o["phone"]) if o.get("phone") else maps_url(o["maps"])}">{e(o["name"].split(" (")[0])}, {e(o["city"])}</a></li>' for o in SITE["offices"]
    )
    return f"""<!doctype html>
<html lang="en-IN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{url}">
{'<meta name="robots" content="noindex">' if noindex else ''}
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(SITE['legalName'])}">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{url}">
<meta name="theme-color" content="#0072b8">
<link rel="icon" href="/assets/img/favicon.ico">
<link rel="preload" href="/assets/fonts/bricolage-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/figtree-var.woff2" as="font" type="font/woff2" crossorigin>
{preload}
<link rel="stylesheet" href="/assets/css/styles.css">
{jsonld}
</head>
<body>
<div class="progress" aria-hidden="true"></div>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <nav class="wrap nav" aria-label="Main">
    <a class="brand" href="/" aria-label="{e(SITE['legalName'])} home">{LOGO}</a>
    <button class="nav-toggle" aria-label="Menu" aria-expanded="false" aria-controls="nav-links"><span></span><span></span><span></span></button>
    <ul class="nav-links" id="nav-links">{nav}<li><a class="btn btn-primary" href="/contact-us/">Talk to us</a></li></ul>
  </nav>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="foot">
      <div>
        <a class="brand" href="/">{LOGO}</a>
        <p>{e(SITE['description'])}</p>
      </div>
      <div><h4>Company</h4><ul>
        <li><a href="/services/">Services</a></li>
        <li><a href="/careers/">Careers</a></li>
        <li><a href="/blog/">Blog</a></li>
        <li><a href="/contact-us/">Contact</a></li>
      </ul></div>
      <div><h4>Our offices</h4><ul>{offices_foot}</ul></div>
      <div><h4>Jobs</h4><ul>
        <li><a href="/careers/">Open roles</a></li>
        <li><a href="{SITE['naukriCompanyUrl']}" target="_blank" rel="noopener">Teleminds on Naukri</a></li>
      </ul></div>
    </div>
    <div class="legal"><span>&copy; {YEAR} {e(SITE['legalName'])}. All rights reserved.</span><span>Kolkata and New Delhi, India</span></div>
  </div>
</footer>
<script src="/assets/js/main.js" defer></script>
</body>
</html>
"""


def office_cards() -> str:
    out = []
    for i, o in enumerate(SITE["offices"]):
        tint = ["blue", "mint", "peach"][i % 3]
        note = '<span class="note">Street address to be confirmed</span>' if o.get("unconfirmed") else ""
        out.append(f"""<article class="office reveal" style="--i:{i}">
  {icon("office" if i == 0 else "pin", tint)}
  <div><div class="city">{e(o['city'])}</div><h3>{e(o['name'])}</h3></div>
  <address>{'<br>'.join(e(l) for l in o['lines'])}</address>{note}
  <div class="row">
    {f'<a class="btn btn-ghost" href="{tel(o["phone"])}">{e(o["phone"])}</a>' if o.get("phone") else ""}
    <a class="btn btn-ghost" href="{maps_url(o['maps'])}" target="_blank" rel="noopener">Directions</a>
  </div>
</article>""")
    return "\n".join(out)


SERVICES = [
    {
        "id": "customer-support", "icon": "headset", "tint": "blue",
        "title": "Customer support",
        "short": "Inbound voice, chat and email teams who answer as your brand, resolve on first contact where they can, and escalate cleanly when they can't.",
        "points": ["Inbound calls, live chat and email", "Order, billing and account queries", "Complaint handling and escalation", "Cover across Indian and Australian business hours"],
    },
    {
        "id": "telemarketing", "icon": "phone", "tint": "mint",
        "title": "Telemarketing and sales",
        "short": "Outbound campaigns run by trained callers who follow your script and compliance rules.",
        "points": ["Outbound sales and upsell campaigns", "Renewals and win-back calls", "Script and compliance adherence", "Daily call outcome reporting"],
    },
    {
        "id": "lead-generation", "icon": "target", "tint": "peach",
        "title": "Lead generation",
        "short": "Prospecting and qualification that hands your sales team warm, booked conversations.",
        "points": ["Prospect research and list building", "Lead qualification calls", "Appointment setting into your calendar", "CRM updates after every call"],
    },
    {
        "id": "business-development", "icon": "growth", "tint": "butter",
        "title": "Business development support",
        "short": "A dedicated team that follows up, nurtures and keeps your pipeline moving.",
        "points": ["Follow-up and nurture calling", "Market and customer surveys", "Customer feedback collection", "Pipeline and data hygiene"],
    },
]

VALUES = [
    ("heart", "peach", "Compassion and understanding", "Life throws hard moments at everyone. We give our people the support and flexibility to get through them."),
    ("seedling", "mint", "Health, family and balance", "Family-friendly policies and a healthy work-life balance keep our teams steady and productive."),
    ("bulb", "butter", "Flexibility", "We adopt new tools and ways of working early, and train our teams so change never catches them out."),
    ("shield", "blue", "Positive values", "Reliability, honesty and accountability, practised by managers first so teams follow."),
]

WORKING = [
    ("rocket", "blue", "Multiple growth opportunities", "Room to move up to team leader and beyond as you build skill and experience."),
    ("money", "mint", "Industry-benchmarked pay", "Salaries measured against the industry, so good work is paid fairly."),
    ("trophy", "butter", "Performance and attendance incentives", "Extra earnings for strong results and for turning up, every month."),
    ("seedling", "peach", "Family-friendly policies", "A healthy work-life balance and support when home life needs you."),
]

PERKS = [("rocket", "Multiple growth opportunities"), ("money", "Industry-benchmarked pay"), ("trophy", "Performance and attendance incentives")]

MARQUEE = ["Customer support", "Telemarketing", "Lead generation", "Appointment setting", "Customer surveys", "Sales follow-up"]


def svc_index(link: bool) -> str:
    rows = []
    for s_ in SERVICES:
        tag, attrs = ("a", f' href="/services/#{s_["id"]}"') if link else ("article", f' id="{s_["id"]}"')
        points = "".join(f"<li>{e(x)}</li>" for x in s_["points"])
        rows.append(f"""<li><{tag} class="svc-row"{attrs}>
  <div class="svc-head">{icon(s_['icon'], s_['tint'])}<h3>{e(s_['title'])}</h3></div>
  <p>{e(s_['short'])}</p>
  <ul>{points}</ul>
</{tag}></li>""")
    return f'<ul class="svc-index">{"".join(rows)}</ul>'


# ---------------------------------------------------------------- pages
def home() -> str:
    steps = [
        ("clipboard", "blue", "Understand", "We learn your product, customers, scripts and the numbers you care about."),
        ("gradcap", "mint", "Hire and train", "We recruit for your campaign and train the team on your process before day one."),
        ("headset", "peach", "Go live", "Your team starts taking or making calls, with a team leader on the floor."),
        ("growth", "butter", "Report and improve", "Regular reporting and call reviews, so quality keeps improving month to month."),
    ]
    track = '<span class="line" aria-hidden="true"></span>' + "".join(
        f'<div class="step" style="--i:{i}">{icon(n, t)}<h3><b>{i + 1}</b>{h}</h3><p>{p}</p></div>' for i, (n, t, h, p) in enumerate(steps)
    )
    values = "".join(
        f'<article class="pcard">{icon(n, t)}<h3>{h}</h3><p>{p}</p></article>' for n, t, h, p in VALUES
    )
    working = "".join(
        f'<article class="pcard">{icon(n, t)}<h3>{h}</h3><p>{p}</p></article>' for n, t, h, p in WORKING
    )
    perks = "".join(f'<li>{img3d(n)}{t}</li>' for n, t in PERKS)
    items = "".join(f"<li>{e(w)}{DOTS}</li>" for w in MARQUEE)
    bars = "<i></i>" * 14
    hellos = json.dumps(["Hello!", "Namaste!", "Nomoshkar!", "G'day!"])

    body = f"""
<section class="hero">
  <div class="wrap hero-grid">
    <div class="intro">
      <h1>Every <span class="rot"><span>call</span><span>chat</span><span>email</span><span>lead</span></span><br>answered like it matters.</h1>
      <p class="lede">Support, sales and lead generation teams in Kolkata and New Delhi, working for businesses across India and Australia.</p>
      <div class="ctas">
        <a class="btn btn-primary" href="/contact-us/">Talk to us</a>
        <a class="btn btn-ghost" href="/careers/">See open roles</a>
      </div>
    </div>
    <div class="stage" aria-hidden="true">
      <span class="ring"></span>
      <div class="disc intro-mask"><img src="/assets/photos/agent.jpg" alt="" width="900" height="900" fetchpriority="high"></div>
      <span class="dot2">{img3d('phone')}</span>
      <span class="dot3"></span>
      <div class="wave">{img3d('headset')}<span class="bars">{bars}</span></div>
      <div class="bubble">{img3d('chat')}<span class="say" data-words="{e(hellos)}">Hello!</span><span class="typing" hidden><i></i><i></i><i></i></span></div>
    </div>
  </div>
</section>

<div class="band-marquee" aria-label="Services: {e(', '.join(MARQUEE))}">
  <div class="track-m" aria-hidden="true"><ul>{items}</ul><ul>{items}</ul></div>
</div>

<div class="facts"><div class="wrap"><div class="facts-row reveal">
  <div class="fact">{icon('office', 'blue')}<div><strong>3 offices</strong><span>Two in Kolkata, one in New Delhi</span></div></div>
  <div class="fact">{icon('calendar', 'mint')}<div><strong>India and Australia</strong><span>Shifts that match your hours</span></div></div>
  <div class="fact">{icon('gradcap', 'peach')}<div><strong>Teams built for you</strong><span>Hired and trained per campaign</span></div></div>
</div></div></div>

<section id="services">
  <div class="wrap">
    <div class="section-head reveal"><h2>Every conversation your customers have with you.</h2></div>
    {svc_index(link=True)}
  </div>
</section>

<section class="process">
  <div class="wrap">
    <div class="section-head reveal"><h2>From first call to a team on the floor.</h2><p>A clear setup process, so you know who is speaking for your brand and how they are doing.</p></div>
    <div class="track">{track}</div>
  </div>
</section>

<section style="padding-top:0;padding-bottom:40px">
  <div class="wrap">
    <figure class="quote reveal">
      <blockquote>&ldquo;Good communication between the management and the employees is the key.&rdquo;</blockquote>
      <cite>What we believe at Teleminds</cite>
    </figure>
  </div>
</section>

<section style="padding-top:0">
  <div class="wrap">
    <div class="why">
      <div class="section-head"><h2>Happy teams give better service.</h2><p>Our clients get consistent, experienced callers because our people stay. Here is why.</p></div>
      <div class="tabs" role="tablist" aria-label="Why Teleminds">
        <button class="tab" role="tab" id="tab-values" aria-controls="panel-values" aria-selected="true">Our values</button>
        <button class="tab" role="tab" id="tab-working" aria-controls="panel-working" aria-selected="false" tabindex="-1">Working here</button>
      </div>
      <div class="pcards" role="tabpanel" id="panel-values" aria-labelledby="tab-values">{values}</div>
      <div class="pcards" role="tabpanel" id="panel-working" aria-labelledby="tab-working" hidden>{working}</div>
    </div>
  </div>
</section>

<section id="careers" class="bleed">
  <div class="wrap">
    <div class="cband">
      <div>
        <h2>Start your career in customer experience.</h2>
        <p>We hire freshers and experienced callers in Kolkata and New Delhi, and train you on the job.</p>
        <ul class="perks">{perks}</ul>
        <a class="btn btn-primary" href="/careers/">See open roles</a>
      </div>
      <div class="pic" aria-hidden="true">
        <span class="ring"></span>
        <div class="ph"><img src="/assets/photos/coworkers.jpg" alt="" width="1400" height="933" loading="lazy" style="object-position:60% 50%"></div>
        <span class="sat s1">{img3d('briefcase')}</span><span class="sat s2">{img3d('rocket')}</span>
      </div>
    </div>
    <div class="abroad">
      <div class="text">
        <h3>Our best people go on to work in Australia.</h3>
        <p>With offices in India and Australia, there is real room to grow. Determined, skilful people from our Indian teams are sent to work in our Australian branches.</p>
        <a href="/careers/">How careers grow here</a>
      </div>
      <figure><img src="/assets/photos/team.jpg" alt="Colleagues working together at their desks" width="1400" height="933" loading="lazy"><div class="chip2"><b>2 countries</b>India and Australia</div></figure>
    </div>
  </div>
</section>

<section id="locations">
  <div class="wrap">
    <div class="section-head reveal"><h2>Visit us in Kolkata or New Delhi.</h2></div>
    <div class="offices">{office_cards()}</div>
  </div>
</section>

<section class="closing bleed">
  <div class="wrap"><div class="closing-inner">
    <div><h2>Need a team to talk to your customers?</h2><p>Tell us what your customers need and we will talk through how our teams in Kolkata and New Delhi can help.</p></div>
    <a class="btn btn-primary" href="/contact-us/">Talk to us</a>
  </div></div>
</section>
"""
    org = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": SITE["legalName"],
        "url": SITE["domain"],
        "logo": SITE["domain"] + "/assets/img/logo.png",
        "description": SITE["description"],
        "location": [
            {"@type": "Place", "name": f"{SITE['legalName']} {o['name']}", **({"telephone": o["phone"]} if o.get("phone") else {}),
             "address": {"@type": "PostalAddress", "streetAddress": ", ".join(o["lines"][:-1]), "addressLocality": o["city"], "addressCountry": "IN"}}
            for o in SITE["offices"]
        ],
    }
    ld = f'<script type="application/ld+json">{json.dumps(org)}</script>'
    pre = '<link rel="preload" href="/assets/photos/agent.jpg" as="image">'
    return layout("/", f"{SITE['legalName']} | Customer support, telemarketing and lead generation", SITE["description"], body, jsonld=ld, preload=pre)


def services() -> str:
    body = f"""
<section class="page-hero">
  <div class="wrap page-hero-grid">
    <div class="reveal"><h1>Services</h1><p>Trained teams that handle your inbound support, outbound sales and lead generation from our offices in Kolkata and New Delhi.</p></div>
    <div class="art" aria-hidden="true">{icon('headset', 'blue', 'lg')}{icon('phone', 'mint', 'lg')}{icon('target', 'peach', 'lg')}</div>
  </div>
</section>
<section style="padding-top:24px"><div class="wrap">{svc_index(link=False)}</div></section>
<section class="closing" style="padding-top:24px">
  <div class="wrap"><div class="closing-inner reveal">
    <h2>Tell us about your campaign.</h2>
    <a class="btn btn-primary" href="/contact-us/">Talk to us</a>
  </div></div>
</section>"""
    return layout("/services/", "Services", "Customer support, telemarketing, lead generation and business development teams in Kolkata and New Delhi.", body)


def careers() -> str:
    if JOBS:
        chips = '<button class="chip-btn" data-filter="all" aria-pressed="true">All offices</button>' + "".join(
            f'<button class="chip-btn" data-filter="{o["id"]}" aria-pressed="false">{e(o["name"].split(" (")[0])}</button>'
            for o in SITE["offices"]
        )
        rows = []
        for i, j in enumerate(JOBS):
            o = OFFICES.get(j.get("office", ""), {})
            meta = [x for x in [(o.get("name", "").split(" (")[0] + ", " + o["city"]) if o else "", j.get("type"), j.get("experience"), j.get("shift")] if x]
            rows.append(f"""<a class="job reveal" style="--i:{i % 6}" data-office="{e(j.get('office', ''))}" href="{e(j['naukriUrl'])}" target="_blank" rel="noopener">
  {icon('briefcase', ['blue', 'mint', 'peach'][i % 3])}
  <div><h3>{e(j['title'])}</h3><div class="meta">{''.join(f'<span>{e(m)}</span>' for m in meta)}</div></div>
  <span class="go">Apply on Naukri</span>
</a>""")
        listing = f"""<div class="filters" role="group" aria-label="Filter by office">{chips}</div>
<div class="jobs">{''.join(rows)}</div>
<div class="empty" id="no-match" hidden>{icon('clipboard', 'blue', 'lg')}<div><h3>No openings at this office right now.</h3><p>Try another office, or check our Naukri page for the latest roles.</p><a class="btn btn-ghost" href="{SITE['naukriCompanyUrl']}" target="_blank" rel="noopener">Teleminds on Naukri</a></div></div>"""
    else:
        listing = f"""<div class="empty reveal">{icon('clipboard', 'blue', 'lg')}<div>
  <h3>Our current openings are listed on Naukri.</h3>
  <p>We post every new role there first. Open our company page to see positions in Kolkata and New Delhi and apply in a couple of minutes.</p>
  <a class="btn btn-primary" href="{SITE['naukriCompanyUrl']}" target="_blank" rel="noopener">View openings on Naukri</a>
</div></div>"""

    perks = "".join(
        f'<div class="fact">{icon(n, t)}<div><strong>{p}</strong></div></div>'
        for (n, p), t in zip(PERKS, ["blue", "mint", "peach"])
    )
    hire = [
        ("laptop", "blue", "Apply", "Find a role on Naukri and send your application."),
        ("phone", "mint", "Phone screen", "A short call with our recruitment team about the role and shift."),
        ("office", "peach", "Interview", "Meet the team leader at the office you applied to."),
        ("rocket", "butter", "Training", "Paid training on the campaign before you go live."),
    ]
    hire_html = "".join(f'<li class="reveal" style="--i:{i}">{icon(n, t)}<h3>{h}</h3><p>{p}</p></li>' for i, (n, t, h, p) in enumerate(hire))
    culture = "".join(f'<div class="reveal" style="--i:{i}"><h3>{img3d(n)}{h}</h3><p>{p}</p></div>' for i, (n, _, h, p) in enumerate(VALUES))
    body = f"""
<section class="page-hero">
  <div class="wrap page-hero-grid">
    <div class="reveal"><h1>Careers at Teleminds</h1><p>Customer support and sales roles in Kolkata and New Delhi, for freshers and experienced callers.</p></div>
    <div class="round mask-in"><img src="/assets/photos/coworkers.jpg" alt="Two Teleminds colleagues at work" width="1400" height="933" style="object-position:60% 50%"></div>
  </div>
</section>
<div class="facts" style="padding-top:8px"><div class="wrap"><div class="facts-row reveal">{perks}</div></div></div>
<section id="openings">
  <div class="wrap">
    <div class="section-head reveal"><h2>Open roles</h2></div>
    {listing}
  </div>
</section>
<section style="padding-top:0">
  <div class="wrap">
    <div class="section-head reveal"><h2>How hiring works</h2></div>
    <ol class="hire">{hire_html}</ol>
  </div>
</section>
<section class="process">
  <div class="wrap">
    <div class="section-head reveal"><h2>Life at Teleminds</h2><p>Good communication between managers and teams is how we work. These values guide it.</p></div>
    <div class="culture">{culture}</div>
  </div>
</section>
<section>
  <div class="wrap">
    <div class="section-head reveal"><h2>Where you could work</h2></div>
    <div class="offices">{office_cards()}</div>
  </div>
</section>"""
    return layout("/careers/", "Careers", "Customer support and telemarketing jobs at Teleminds in Kolkata (two offices in Salt Lake Sector V) and New Delhi.", body)


def contact() -> str:
    body = f"""
<section class="page-hero">
  <div class="wrap page-hero-grid">
    <div class="reveal"><h1>Talk to us</h1><p>Tell us what you need and we will call you back within one working day. Or call the office nearest to you.</p></div>
    <div class="art" aria-hidden="true">{icon('chat', 'blue', 'lg')}{icon('envelope', 'peach', 'lg')}</div>
  </div>
</section>
<section style="padding-top:16px">
  <div class="wrap contact-grid">
    <form class="form reveal" id="enquiry" novalidate data-endpoint="{e(SITE['formEndpoint'])}" data-email="{e(SITE['enquiryEmail'])}">
      <h2>Send an enquiry</h2>
      <div class="two">
        <div class="field"><label for="userName">Full name</label><input id="userName" name="userName" autocomplete="name" required><span class="err">Please enter your name.</span></div>
        <div class="field"><label for="userNumber">Phone</label><input id="userNumber" name="userNumber" type="tel" autocomplete="tel" required pattern="[\\d\\s+\\-\\(\\)]{{8,}}"><span class="err">Please enter a phone number we can call.</span></div>
      </div>
      <div class="field"><label for="userEmail">Email</label><input id="userEmail" name="userEmail" type="email" autocomplete="email" required><span class="err">Please enter a valid email address.</span></div>
      <div class="field"><label for="userSelect">I'm interested in</label>
        <select id="userSelect" name="userSelect" required>
          <option value="Services">Services for my business</option>
          <option value="Careers">A job at Teleminds</option>
        </select><span class="err">Please choose one.</span></div>
      <div class="field"><label for="userMessage">Message</label><textarea id="userMessage" name="userMessage" required></textarea><span class="err">Please add a short message.</span></div>
      <div class="form-status" role="status" aria-live="polite"></div>
      <button class="btn btn-primary" type="submit">Send message</button>
    </form>
    <div class="contact-offices">{office_cards()}</div>
  </div>
</section>"""
    return layout("/contact-us/", "Contact us", "Call or message Teleminds in Kolkata (two offices in Salt Lake Sector V) or New Delhi (Tilak Nagar).", body)


def excerpt(p: dict, n: int = 170) -> str:
    t = p["paragraphs"][0]
    return t if len(t) <= n else t[:n].rsplit(" ", 1)[0] + "..."


def blog_index(path: str = "/blog/") -> str:
    cards = "".join(
        f'<a class="post-card reveal" style="--i:{i}" href="/blog/{p["slug"]}/"><h2>{e(p["title"])}</h2><p>{e(excerpt(p))}</p><span class="more">Read article</span></a>'
        for i, p in enumerate(POSTS)
    )
    body = f"""
<section class="page-hero">
  <div class="wrap page-hero-grid">
    <div class="reveal"><h1>Blog</h1><p>Notes on workplace culture and looking after the people who look after your customers.</p></div>
    <div class="art" aria-hidden="true">{icon('bulb', 'butter', 'lg')}{icon('laptop', 'blue', 'lg')}</div>
  </div>
</section>
<section style="padding-top:16px"><div class="wrap"><div class="posts">{cards}</div></div></section>"""
    return layout(path, "Blog", "Articles from Teleminds on workplace culture, motivation and employee wellbeing.", body)


def blog_post(p: dict) -> str:
    paras = "".join(f"<p>{e(x)}</p>" for x in p["paragraphs"])
    body = f"""
<section class="page-hero"><div class="wrap"><article class="article">
  <a class="back" href="/blog/">&larr; All articles</a>
  <h1>{e(p['title'])}</h1>
  <div class="body">{paras}</div>
</article></div></section>"""
    return layout(f"/blog/{p['slug']}/", p["title"], excerpt(p, 155), body)


def brand() -> str:
    sw = [
        ("#0072b8", "Deep blue", "From the logo. Links, headings accents, careers band."),
        ("#00b8f0", "Cyan", "From the logo. Decorative shapes, dots, progress."),
        ("#98d8f8", "Sky", "From the logo wordmark. Orbs, highlights."),
        ("#ff9a3c", "Saffron", "Primary buttons only, with dark text."),
        ("#0b2239", "Ink navy", "Text and the marquee band."),
        ("#f3f8fc", "Mist", "Page background."),
        ("#e1f2fc", "Sky tint", "Icon wells, soft panels."),
        ("#ffeedd", "Peach tint", "Icon wells, soft panels."),
    ]
    swatches = "".join(
        f'<div class="swatch reveal" style="--i:{i % 4}"><div style="background:{h}"></div><p><strong>{n}</strong>{h}<br><span class="muted">{d}</span></p></div>'
        for i, (h, n, d) in enumerate(sw)
    )
    icons = sorted(p.stem for p in (ROOT / "assets/3d").glob("*.png"))
    tints = ["blue", "mint", "peach", "butter"]
    grid = "".join(f'<span class="well t-{tints[i % 4]}" title="{n}"><img src="/assets/3d/{n}.png" alt="{n}" width="256" height="256" loading="lazy"></span>' for i, n in enumerate(icons))
    body = f"""
<section class="page-hero"><div class="wrap">
  <div class="reveal"><h1>Brand guide</h1><p>How the Teleminds logo, colours, type, photos and motion fit together. Internal reference, not linked from the site.</p></div>
</div></section>
<section style="padding-top:16px"><div class="wrap">
  <div class="section-head"><h2>Logo</h2><p>The original Teleminds Infotech logo is kept unchanged. Its three rising dots are the site's signature shape: they appear as loaders, separators, and the circle and arch masks on photos.</p></div>
  <div class="logo-tiles">
    <div style="background:#fff"><img src="/assets/img/logo.png" alt="Teleminds logo on white" width="190" height="84"></div>
    <div style="background:#0b2239"><img src="/assets/img/logo.png" alt="Teleminds logo on navy" width="190" height="84"></div>
    <div style="background:var(--tint-blue)"><span class="dots live" style="transform:scale(3)"><i></i><i></i><i></i></span></div>
  </div>
</div></section>
<section><div class="wrap">
  <div class="section-head"><h2>Colour</h2><p>Three blues taken from the logo, plus saffron for the main action on each page. Dark mode uses a deep navy base and a lighter blue.</p></div>
  <div class="swatches">{swatches}</div>
</div></section>
<section><div class="wrap">
  <div class="section-head"><h2>Type</h2><p>Bricolage Grotesque for headlines, Outfit for body text. Both self-hosted.</p></div>
  <div class="card"><p style="font-family:Bricolage,sans-serif;font-size:60px;font-weight:700;letter-spacing:-.04em;line-height:1;color:var(--ink)">Every call answered like it matters.</p><p style="font-size:19px">Body copy at 17px with 1.6 line height. Keep sentences short and plain, and never use em dashes.</p></div>
</div></section>
<section><div class="wrap">
  <div class="section-head"><h2>Motion</h2><p>Rotating headline word, a typing greeting bubble, a voice-wave meter, photos that unmask on scroll, a process line that draws itself, a single services marquee, and soft page-to-page transitions. All of it switches off for visitors who ask their device for reduced motion.</p></div>
</div></section>
<section><div class="wrap">
  <div class="section-head"><h2>3D icons</h2><p>Microsoft Fluent 3D emoji (MIT licence), always placed on a rounded tint well. Add more from github.com/microsoft/fluentui-emoji. Photos are from Pexels (free licence); replace them with real Teleminds office photos when available.</p></div>
  <div class="icons-grid">{grid}</div>
</div></section>"""
    return layout("/brand/", "Brand guide", "Teleminds brand guide.", body, noindex=True)


# ---------------------------------------------------------------- build
def write(path: str, content: str) -> None:
    out = DIST / path.strip("/") / "index.html" if path != "/" else DIST / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(ROOT / "assets", DIST / "assets")

    pages = {"/": home(), "/services/": services(), "/careers/": careers(), "/contact-us/": contact(), "/blog/": blog_index(), "/brand/": brand()}
    for p in POSTS:
        pages[f"/blog/{p['slug']}/"] = blog_post(p)
    # The old WordPress category archive pointed at the blog list; keep the URL alive.
    pages["/blog/category/blog-posts-category/"] = blog_index("/blog/").replace('<meta name="robots"', '<meta name="robots"')
    for path, html_ in pages.items():
        write(path, html_)

    urls = [p for p in pages if p not in ("/brand/", "/blog/category/blog-posts-category/")]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
        f"  <url><loc>{SITE['domain']}{u}</loc></url>\n" for u in urls) + "</urlset>\n"
    (DIST / "sitemap.xml").write_text(sitemap)
    (DIST / "robots.txt").write_text(f"User-agent: *\nDisallow: /brand/\nSitemap: {SITE['domain']}/sitemap.xml\n")
    print(f"built {len(pages)} pages into {DIST}")


if __name__ == "__main__":
    main()
