"""Generate every page of the Helios FTC 5214 website into ./public.

Edit content here, then run:  python3 build_pages.py
Styles: public/assets/styles.css   Behaviour: public/assets/main.js
Robot images: public/assets/robot/ (photo of Eclipse + our Onshape CAD from the same angle, see README)
"""
from pathlib import Path
from html import escape
import json
import re

P = Path(__file__).parent / 'public'
A = P / 'assets'
TEAM_SOURCE = 'https://ftc-events.firstinspires.org/team/5214'
SCHOOL_URL = 'https://www.quarrylane.org/'
INSTAGRAM = 'https://www.instagram.com/ftc5214helios/'
EMAIL = '5214.helios@gmail.com'
MEET1 = '/seasons/biobuzz/east-bay-meet-one/'
EXT = ' target="_blank" rel="noopener noreferrer"'

# Robot images. Front = real photo of Eclipse (cut out), back = the CAD from the exact same camera angle.
ROBOT = {
    'w': 1530, 'h': 1030,
    'render': '/assets/robot/hero-photo.webp',   # photo from the Meet One pits, background removed
    'cad': '/assets/robot/hero-cad.webp',        # Onshape CAD lined up with the photo, shown inside the lens
    'cad_light': '/assets/robot/hero-cad.webp',  # same CAD, shown in full by the "Show the CAD" button
    'spin_frames': 48,
    'spin_kinds': 'cad',
    'spin': '/assets/robot/spin/{kind}-{i}.webp',        # i = 000..047
    'spin_small': '/assets/robot/spin-sm/{kind}-{i}.webp',
}

seasons = [
    ('2026–27', 'BIOBUZZ', '/seasons/biobuzz/'),
    ('2025–26', 'DECODE', '/seasons/decode/'),
    ('2024–25', 'INTO THE DEEP', 'https://ftc-events.firstinspires.org/2024/team/5214'),
    ('2023–24', 'CENTERSTAGE', 'https://ftc-events.firstinspires.org/2023/team/5214'),
    ('2022–23', 'POWERPLAY', 'https://ftc-events.firstinspires.org/2022/team/5214'),
    ('2021–22', 'FREIGHT FRENZY', 'https://ftc-events.firstinspires.org/2021/team/5214'),
    ('2020–21', 'ULTIMATE GOAL', 'https://ftc-events.firstinspires.org/2020/team/5214'),
    ('2019–20', 'SKYSTONE', 'https://ftc-events.firstinspires.org/2019/team/5214'),
]

team_groups = [
    ['Leadership', 'Runs the team', [['Bryan Pan', 'Captain', 'BP']]],
    ['Software', 'Programs the robot', [['Yuvan Ramesh', 'Software Lead', 'YR'], ['Azaan Raza', 'Software Member', 'AR']]],
    ['Hardware, Electrical & Design', 'Designs, wires, builds and fixes the robot', [['Arhaan Reddy', 'Hardware Member', 'AR'], ['Rishi Mamdur', 'Electrical Lead', 'RM'], ['Neel Gupta', 'Design Lead', 'NG'], ['Nyles Han', 'Hardware Member', 'NH']]],
    ['Business, Outreach & Media', 'Handles business, outreach events and media', [['Elan Jain', 'Business Lead', 'EJ'], ['Kaveesh Chaturvedi', 'Media Lead', 'KC']]],
    ['Drive Team', 'Drives in matches and plans strategy', [['Damodar Kriplani', 'Driver & Fabrication Lead', 'DK'], ['Ronav Gupta', 'Drive Coach / Youth Mentor', 'RG']]],
    ['Mentors', 'Help and advise the team', [['Lina Tannous', 'Mentor', 'LT'], ['Leon Cox', 'Mentor', 'LC'], ['Ramana Cherukuri', 'Mentor', 'RC']]],
]



def is_lead(role):
    return role == 'Captain' or 'Lead' in role


# leads before members inside every group
for _g in team_groups:
    _g[2].sort(key=lambda p: not is_lead(p[1]))

# ---------------------------------------------------------------- svg assets
def _svg(path, cls):
    s = (A / path).read_text(encoding='utf-8')
    # inline copies don't need file metadata (the .svg files keep theirs)
    s = re.sub(r'<metadata>.*?</metadata>', '', s, flags=re.S)
    s = re.sub(r'\sxmlns:\w+="[^"]*"', '', s)
    s = re.sub(r'\s(role|aria-label)="[^"]*"', '', s)
    return s.replace('<svg ', f'<svg class="{cls}" aria-hidden="true" focusable="false" ', 1)


LOGO = _svg('logo/helios-logo.svg', 'logo')
SUN = _svg('logo/helios-mark.svg', 'sun')

arrow = '<svg class="icon" viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M4 10h11m-4.5-4.5L15 10l-4.5 4.5" stroke="currentColor" stroke-width="1.9"/></svg>'
arrow_diag = '<svg class="icon icon--diag" viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M6 14 14 6M7.5 6H14v6.5" stroke="currentColor" stroke-width="1.9"/></svg>'
arrow_back = '<svg class="icon" viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M16 10H5m4.5-4.5L5 10l4.5 4.5" stroke="currentColor" stroke-width="1.9"/></svg>'
expand = '<svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M12 3h5v5M8 17H3v-5M17 3l-6 6M3 17l6-6" stroke="currentColor" stroke-width="1.7"/></svg>'
copy_icon = '<svg class="icon" viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2" stroke="currentColor" stroke-width="1.7"/><path d="M13 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2" stroke="currentColor" stroke-width="1.7"/></svg>'
xray_icon = '<svg class="icon" viewBox="0 0 20 20" fill="none" aria-hidden="true"><circle cx="10" cy="10" r="7" stroke="currentColor" stroke-width="1.7"/><path d="M10 3v14M3 10h14" stroke="currentColor" stroke-width="1.2" stroke-dasharray="2 2"/></svg>'


# ---------------------------------------------------------------- text helpers
def split(text, start=0):
    """Wrap each word for the rise-in animation. *word* = serif accent."""
    out, i = [], start
    for tok in text.split(' '):
        if not tok:
            continue
        serif = tok.startswith('*') and tok.endswith('*')
        word = tok.strip('*')
        cls = ' class="serif"' if serif else ''
        out.append(f'<span class="w"><span{cls} style="--i:{i}">{word}</span></span>')
        i += 1
    return ' '.join(out)


def lit_words(text):
    """Words that light up one by one as you scroll."""
    return ' '.join(f'<span class="lw">{w}</span>' for w in text.split(' ') if w)


def btn(href, text, kind='sun', external=False, icon=None, attrs=''):
    ic = icon or (arrow_diag if external else arrow)
    ext = EXT if external else ''
    return (f'<a class="btn btn--{kind}" href="{href}"{ext}{attrs}><span class="btn-label"><span>{text}</span>'
            f'<span aria-hidden="true">{text}</span></span><span class="btn-icon">{ic}</span></a>')


def tlink(href, text, external=False, cls=''):
    ic = arrow_diag if external else arrow
    return f'<a class="tlink {cls}" href="{href}"{EXT if external else ""}><span>{text}</span>{ic}</a>'


def school_link():
    return f'<a class="inline-link" href="{SCHOOL_URL}"{EXT}>The Quarry Lane School</a>'


def marquee(items, direction=1, speed=1):
    sep = f'<span class="mq-sun">{SUN}</span>'
    row = ''.join(f'<span class="mq-item{" serif" if s else ""}">{t}</span>{sep}' for t, s in items)
    return (f'<div class="marquee" data-marquee data-dir="{direction}" data-speed="{speed}"><div class="marquee-track">'
            f'<div class="marquee-copy">{row}</div><div class="marquee-copy" aria-hidden="true">{row}</div></div></div>')


def xray(cls='', label='Eclipse, the Helios 2026–27 robot', priority=False, light_cad=False):
    load = 'fetchpriority="high"' if priority else 'loading="lazy"'
    alt_img = (f'<img class="xray-alt" src="{ROBOT["cad_light"]}" width="{ROBOT["w"]}" height="{ROBOT["h"]}" loading="lazy" decoding="async" alt="CAD model of Eclipse from the same angle">'
               if light_cad else '')
    return (f'<div class="xray {cls}" data-xray data-cad="{ROBOT["cad"]}" style="--ar:{ROBOT["w"]}/{ROBOT["h"]}">'
            f'<img class="xray-front" src="{ROBOT["render"]}" width="{ROBOT["w"]}" height="{ROBOT["h"]}" {load} decoding="async" alt="{label}">'
            f'{alt_img}<canvas class="xray-canvas" aria-hidden="true"></canvas></div>')


# ---------------------------------------------------------------- layout
NAV = [('Home', '/', 'home', 'meet1-team-robot.webp'), ('About', '/about/', 'about', 'meet1-team-hands.webp'),
       ('Team', '/team/', 'team', 'meet1-teammates-strategy.webp'), ('Outreach', '/outreach/', 'outreach', 'lakeside-team-workshop.webp'),
       ('Seasons', '/seasons/', 'seasons', 'meet1-robot-game.webp'), ('Sponsor', '/sponsor/', 'sponsor', 'sponsor-award.webp'),
       ('Contact', '/contact/', 'contact', 'meet1-robot-workbench.webp')]


def header():
    return f'''<header class="site-header" data-header>
<a href="/" class="site-logo" aria-label="Helios, FTC Team 5214, home">{LOGO}</a>
<div class="header-actions">{btn('/contact/', 'Contact', 'sun', attrs=' data-magnetic')}
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-menu" data-menu-btn><span class="menu-btn-lines" aria-hidden="true"><i></i><i></i></span><span class="sr-only">Menu</span></button></div>
</header>'''


def menu(active):
    links = ''
    for n, (title, url, key, img) in enumerate(NAV):
        cur = ' aria-current="page"' if key == active else ''
        links += (f'<li style="--n:{n}"><a class="menu-link{" is-active" if key == active else ""}" href="{url}" data-img="/assets/{img}"{cur}>'
                  f'<span class="menu-link-text"><span>{title}</span><span aria-hidden="true">{title}</span></span></a></li>')
    season_links = ''.join(f'<a href="{url}"{EXT if url.startswith("http") else ""}><span>{year}</span>{name}</a>' for year, name, url in seasons[:4])
    return f'''<div class="menu" id="site-menu" data-menu aria-label="Site menu">
<div class="menu-inner">
<nav aria-label="Main"><ul class="menu-list">{links}</ul></nav>
<div class="menu-side">
<div class="menu-block"><span class="menu-label">Seasons</span>{season_links}<a href="/seasons/">All seasons</a></div>
<div class="menu-block"><span class="menu-label">Say hi</span><a href="mailto:{EMAIL}">{EMAIL}</a><a href="{INSTAGRAM}"{EXT}>Instagram</a></div>
</div>
</div>
<div class="menu-preview" aria-hidden="true"><img alt="" src="/assets/meet1-team-robot.webp"></div>
</div>'''


def footer():
    return f'''<footer class="site-footer" data-theme="dark">
<div class="footer-panel">
<div class="footer-top">
<div class="footer-cta">
<h2 class="footer-title">{split('Get in touch')}</h2>
<p>Questions about the team, sponsorship, or having us at your event? Email us.</p>
<div class="copy-row"><a class="footer-email" href="mailto:{EMAIL}">{EMAIL}</a><button class="copy-btn" type="button" data-copy="{EMAIL}">{copy_icon}<span>Copy</span></button></div>
</div>
<div class="footer-cols">
<div class="footer-col"><span class="footer-label">Pages</span><a href="/about/">About</a><a href="/team/">Team</a><a href="/outreach/">Outreach</a><a href="/seasons/">Seasons</a><a href="/sponsor/">Sponsor</a><a href="/contact/">Contact</a></div>
<div class="footer-col"><span class="footer-label">Follow</span><a href="{INSTAGRAM}"{EXT}>Instagram</a><a href="{TEAM_SOURCE}"{EXT}>FIRST team profile</a><a href="{SCHOOL_URL}"{EXT}>The Quarry Lane School</a></div>
</div>
</div>
<div class="footer-sun" data-footer-sun aria-hidden="true">{SUN}</div>
<a class="footer-logo" href="/" aria-label="Helios home">{LOGO}</a>
<div class="footer-bottom"><span>© <span data-year>2026</span> Helios, FTC Team 5214, Dublin, California</span><span>Student team website. Not an official FIRST site.</span></div>
</div>
</footer>'''


def page(title, desc, active, content, path='/', loader=False):
    t = escape(title, quote=True)
    d = escape(desc, quote=True)
    loader_html = ''
    if loader:
        loader_html = f'<div class="loader" aria-hidden="true"><div class="loader-sun">{SUN}</div><div class="loader-count"><span data-loader-count>0</span>%</div><div class="loader-word">Helios</div></div>'
    head_js = ("document.documentElement.classList.add('js');try{var s=sessionStorage;"
               "if(s.getItem('helios-nav')==='1'){document.documentElement.classList.add('is-entering');}"
               + ("if(!s.getItem('helios-seen')){document.documentElement.classList.add('is-loading');}" if loader else '')
               + "}catch(e){}")
    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><meta name="theme-color" content="#F2F0EB"><meta name="description" content="{d}"><meta property="og:type" content="website"><meta property="og:title" content="{t} | Helios FTC 5214"><meta property="og:description" content="{d}"><meta property="og:image" content="/assets/social-card.png"><meta name="twitter:card" content="summary_large_image"><title>{escape(title)} | Helios FTC 5214</title><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="preload" href="/assets/fonts/mona-sans-latin-variable.woff2" as="font" type="font/woff2" crossorigin><link rel="preload" href="/assets/fonts/gloock-latin-400.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="/assets/styles.css"><script>{head_js}</script><script src="/assets/vendor/lenis.min.js" defer></script><script src="/assets/main.js" defer></script><!-- Vercel Web Analytics: activate from the Vercel project Analytics tab. --><script>window.va = window.va || function () {{ (window.vaq = window.vaq || []).push(arguments); }};</script><script defer src="/_vercel/insights/script.js"></script></head><body data-page="{active}"><a class="skip-link" href="#main">Skip to content</a>{loader_html}<div class="curtain" aria-hidden="true"><div class="curtain-sun">{SUN}</div></div>{header()}{menu(active)}<main id="main">{content}</main>{footer()}</body></html>'''
    dest = P / path.strip('/') / 'index.html' if path != '/' else P / 'index.html'
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding='utf-8')


def page_hero(title, lead, meta='', extra='', top='', theme='light', cls=''):
    meta_html = f'<p class="page-meta">{meta}</p>' if meta else ''
    lead_html = f'<p class="page-lead">{lead}</p>' if lead else ''
    return (f'<section class="page-hero {cls}" data-theme="{theme}"><div class="container">{top}{meta_html}'
            f'<h1 class="page-title" data-split>{split(title)}</h1>{lead_html}{extra}</div></section>')


def section_head(title, lead='', action='', cls=''):
    lead_html = f'<p class="section-lead">{lead}</p>' if lead else ''
    return f'<div class="section-head {cls}"><div><h2 class="h2" data-split>{split(title)}</h2>{lead_html}</div>{action}</div>'


def img_reveal(src, w, h, alt, cls='', loading='lazy', parallax=''):
    px = f' data-parallax="{parallax}"' if parallax else ''
    return (f'<figure class="reveal-img {cls}" data-reveal-img><div class="reveal-img-inner"{px}>'
            f'<img src="{src}" width="{w}" height="{h}" loading="{loading}" decoding="async" alt="{alt}"></div></figure>')


# ================================================================ HOME
home_hero = f'''<section class="hero" data-theme="dark" data-hero>
<div class="hero-rings" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
<p class="hero-word" aria-hidden="true" data-hero-word>Eclipse</p>
<div class="hero-stage">{xray('xray--hero', priority=True, light_cad=True)}</div>
<p class="hero-word hero-word--outline" aria-hidden="true">Eclipse</p>
<div class="hero-bottom">
<div class="hero-intro">
<h1 class="hero-title" data-split>{split("We’re Helios, FTC Team 5214.")}</h1>
<p class="hero-text">FIRST Tech Challenge team from {school_link()} in Dublin, CA. This is Eclipse, our 2026–27 robot.</p>
<div class="hero-actions">{btn('/seasons/biobuzz/', 'This season', 'sun', attrs=' data-magnetic')}{btn('/team/', 'Meet the team', 'line', attrs=' data-magnetic')}</div>
</div>
<div class="hero-side">
<button class="xray-toggle xray-toggle--dark" type="button" data-xray-toggle aria-pressed="false">{xray_icon}<span class="xray-toggle-text" data-on="Show the robot" data-off="Show the CAD">Show the CAD</span></button>
<p class="xray-hint">Move your mouse over Eclipse to see the CAD underneath.</p>
<a class="latest" href="{MEET1}"><img src="/assets/meet1-score-118.webp" width="1024" height="768" alt="" loading="lazy"><span><small>Latest</small><strong>East Bay League Meet One</strong><span>Nov 1 · 118-point alliance high score</span></span>{arrow}</a>
</div>
</div>
</section>'''

marquee_band = f'''<section class="marquee-band" data-theme="dark" aria-label="Team facts">
{marquee([('Helios', False), ('FTC Team 5214', True), ('Dublin, California', False), ('Since 2010', True)], 1, 1)}
{marquee([('BIOBUZZ 2026–27', False), ('Innovate Award, DECODE', True), ('Motivate Award, CENTERSTAGE', False), ('East Bay League', True)], -1, 0.8)}
</section>'''

intro = f'''<section class="intro" data-theme="dark"><div class="container">
<p class="intro-text" data-lit>{lit_words("We’ve been an FTC team since 2010. Every season FIRST puts out a new game, and we design, build and program a robot to play it. We also run STEM workshops for younger kids, like our IntelliKits event in Concord this October.")}</p>
<dl class="stats">
<div><dt>Seasons in FTC</dt><dd data-count="16">16</dd></div>
<div><dt>Rookie season</dt><dd>2010</dd></div>
<div><dt>DECODE match record</dt><dd>11–7</dd></div>
<div><dt>Meet One high score</dt><dd data-count="118">118</dd></div>
</dl></div></section>'''

spin_notes = [
    (0.06, 0.28, 'Drive', 'Four 104 mm mecanum wheels, so Eclipse can drive and strafe in any direction.'),
    (0.30, 0.52, 'Intake', 'Game pieces come in at the front and ride up the intake ramp.'),
    (0.54, 0.76, 'Shooter', 'A transfer ramp feeds the shooter on top of the robot.'),
    (0.78, 1.01, 'Onshape', 'Every part here comes from our real CAD model of Eclipse.'),
]
notes_html = ''.join(f'<li class="spin-note" data-from="{a}" data-to="{b}"><strong>{t}</strong><span>{d}</span></li>' for a, b, t, d in spin_notes)
spin = f'''<section class="spin" data-theme="dark" data-spin data-frames="{ROBOT['spin_frames']}" data-kinds="{ROBOT['spin_kinds']}" data-src="{ROBOT['spin']}" data-src-small="{ROBOT['spin_small']}" aria-label="Eclipse, our 2026–27 robot, turning 360 degrees">
<div class="spin-sticky">
<p class="spin-ghost" aria-hidden="true" data-spin-ghost>Eclipse</p>
<div class="spin-head"><p class="spin-kicker">Our 2026–27 robot</p><h2 class="spin-title" data-split>{split('Eclipse')}</h2></div>
<div class="spin-stage"><canvas class="spin-canvas" role="img" aria-label="The CAD model of Eclipse rotating 360 degrees"></canvas></div>
<ul class="spin-notes">{notes_html}</ul>
<div class="spin-meter" aria-hidden="true"><span data-spin-deg>000°</span><i><b data-spin-bar></b></i><span data-spin-mode>CAD</span></div>
</div>
</section>'''

track_items = [
    ('meet1-team-robot.webp', 1024, 768, 'The team with Eclipse at Meet One', 'The team with Eclipse', 34, 4, 0.6),
    ('meet1-robot-field.webp', 1120, 1680, 'Eclipse on the competition floor', 'Ready for a match', 20, 18, -0.8),
    ('meet1-score-118.webp', 1024, 768, 'Match results showing a 118 to 49 win in Qualification 17', 'Q17: 118 to 49', 28, 46, 1.0),
    ('meet1-robot-game.webp', 1680, 1120, 'Eclipse on the field during a match', 'On the field', 36, 10, -0.5),
    ('meet1-team-hands.webp', 1680, 1120, 'Helios team members at the event', 'Between matches', 26, 40, 0.9),
    ('meet1-teammates-strategy.webp', 1120, 1680, 'Two team members talking strategy beside the field', 'Planning the next match', 18, 8, -0.7),
    ('meet1-robot-workbench.webp', 1680, 1120, 'Eclipse on the workbench in the pits', 'In the pits', 32, 34, 0.5),
]
track_html = ''.join(
    f'<figure class="track-item" style="--w:{w}vw;--y:{y}vh" data-drift="{dr}"><div class="track-img"><img src="/assets/{f}" width="{iw}" height="{ih}" loading="lazy" decoding="async" alt="{alt}"></div><figcaption>{cap}</figcaption></figure>'
    for f, iw, ih, alt, cap, w, y, dr in track_items)
track = f'''<section class="track" data-theme="light" data-track aria-labelledby="track-title">
<div class="track-sticky">
<p class="track-ghost" aria-hidden="true" data-track-ghost>Meet One</p>
<div class="track-rail" data-track-rail>
<div class="track-intro"><p class="page-meta">East Bay League · Nov 1, 2026</p><h2 class="h2" id="track-title" data-split>{split('Meet *One*')}</h2><p>Our first league meet of the season, at Quarry Lane. In Qualification 17 our alliance won 118 to 49, the highest score of the event.</p></div>
{track_html}
<a class="track-end" href="{MEET1}"><span>See all 9 photos</span>{arrow}</a>
</div>
</div>
</section>'''

season_split = f'''<section class="section seasons-home" data-theme="light"><div class="container">
{section_head('Seasons', "Every season is a new game. Here’s this one and the last one.", tlink('/seasons/', 'All seasons'))}
<div class="season-duo">
<a class="season-big" href="/seasons/biobuzz/"><span class="season-big-meta"><span class="serif">This season</span>2026–27</span><span class="season-big-name">Biobuzz</span><span class="season-big-go">{arrow}</span></a>
<a class="season-big" href="/seasons/decode/"><span class="season-big-meta"><span class="serif">Last season</span>2025–26 · Innovate Award</span><span class="season-big-name">Decode</span><span class="season-big-go">{arrow}</span></a>
</div></div>
</section>'''

# leads first (in team order), then Azaan Raza, then the other members, then mentors
_everyone = [(name, role) for _, _, people in team_groups for name, role, _ in people]
_leads = [p for p in _everyone if is_lead(p[1])]
_mentors = [p for p in _everyone if p[1] == 'Mentor']
_members = [p for p in _everyone if p not in _leads and p not in _mentors]
_members.sort(key=lambda p: p[0] != 'Azaan Raza')
all_people = _leads + _members + _mentors
wall = ''.join(f'<li><span class="wall-name">{n}</span><span class="wall-role">{r}</span></li>' for n, r in all_people)
team_wall = f'''<section class="section team-wall" data-theme="dark"><div class="container">
{section_head('The team', '10 students and 4 mentors this season.', btn('/team/', 'Meet the team', 'sun', attrs=' data-magnetic'))}
<ul class="wall">{wall}</ul>
</div></section>'''

outreach_home = f'''<section class="section outreach-home" data-theme="light"><div class="container outreach-grid">
{img_reveal('/assets/lakeside-team-workshop.webp', 1050, 551, 'Helios members showing an IntelliKits model at the Lakeside workshop', 'outreach-photo', parallax='0.08')}
<div class="outreach-copy">
<p class="page-meta">October 16, 2026 · Concord, CA</p>
<h2 class="h2" data-split>{split('Outreach')}</h2>
<p>We ran a STEM event at the Lakeside Apartments community center in Concord. We showed the kids our competition robot, ran a programming activity, and helped them build model cars from our IntelliKits.</p>
{btn('/outreach/', 'Read about it', 'ink', attrs=' data-magnetic')}
</div>
</div></section>'''

home = home_hero + marquee_band + intro + spin + track + season_split + team_wall + outreach_home
page('Home', 'Helios is FTC Team 5214 from The Quarry Lane School in Dublin, California. See our robot, our seasons, our team and our outreach.', 'home', home, loader=True)

# ================================================================ ABOUT
milestones = [
    ('2010', 'Rookie season', 'Team 5214 competes in FIRST Tech Challenge for the first time.'),
    ('2023–24', 'CENTERSTAGE', 'Motivate Award at the East Bay League Tournament.'),
    ('2025–26', 'DECODE', 'Innovate Award, sponsored by RTX, at the East Bay League Tournament.'),
    ('2026–27', 'BIOBUZZ', 'This season. Our robot is Eclipse.'),
]
timeline = ''.join(f'<li class="tl-item" data-tl-item><span class="tl-year">{y}</span><div><h3>{t}</h3><p>{d}</p></div></li>' for y, t, d in milestones)
subteams = ''.join(f'<li><h3>{name}</h3><p>{sub}</p></li>' for name, sub, _ in team_groups)

about = page_hero('About Helios', 'We’re FTC Team 5214 from The Quarry Lane School in Dublin, California. We’ve competed in FIRST Tech Challenge since 2010.', 'Since 2010') + f'''
<section class="section" data-theme="light"><div class="container two-col">
{img_reveal('/assets/meet1-team-hands.webp', 1680, 1120, 'Helios team members at East Bay League Meet One', parallax='0.06')}
<div class="prose">
<h2 class="h3">What we do</h2>
<p>Every season starts with a new game from FIRST. We design the robot in CAD, build it, program it, and test it until it’s ready for East Bay League meets.</p>
<p>We also run outreach events for younger kids. In October we brought our robot and our IntelliKits to a community center in Concord.</p>
<p>Our official results are on the FIRST events site. Older records may list the team under a previous name.</p>
{tlink(TEAM_SOURCE, 'Our FIRST team record', True)}
</div>
</div></section>
<section class="section" data-theme="dark"><div class="container">
{section_head('Timeline')}
<ol class="timeline" data-timeline><span class="tl-line" aria-hidden="true"><i></i></span>{timeline}</ol>
</div></section>
<section class="section" data-theme="light"><div class="container">
{section_head('Who does what', 'The six groups on the team this season.')}
<ul class="subteams">{subteams}</ul>
<div class="cta-row">{btn('/team/', 'Meet the team', 'sun', attrs=' data-magnetic')}</div>
</div></section>'''
page('About', 'Helios is FTC Team 5214 from The Quarry Lane School in Dublin, California, competing in FIRST Tech Challenge since 2010.', 'about', about, '/about/')


# ================================================================ TEAM
def member_card(name, role, initials):
    return (f'<li class="member" data-tilt><div class="member-face" role="img" aria-label="Photo coming soon for {name}">'
            f'<span class="member-initials" aria-hidden="true">{initials}</span><span class="member-rays" aria-hidden="true"></span></div>'
            f'<div class="member-meta"><h3>{name}</h3><p>{role}</p></div></li>')


divisions = ''.join(
    f'<section class="division" aria-labelledby="div-{n}"><div class="division-head"><h2 id="div-{n}">{division}</h2><p>{sub}</p></div>'
    f'<ul class="members">{"".join(member_card(nm, rl, ini) for nm, rl, ini in people)}</ul></section>'
    for n, (division, sub, people) in enumerate(team_groups, start=1))
team = page_hero('The team', '10 students and 4 mentors for the 2026–27 season.', 'Helios 2026–27',
                 extra=img_reveal('/assets/meet1-team-robot.webp', 1024, 768, 'Helios team members with Eclipse at East Bay League Meet One', 'page-hero-img', 'eager')) + f'''
<section class="section" data-theme="light"><div class="container">{divisions}<p class="small-note">Photos coming soon.</p></div></section>'''
page('Team', 'Meet the 2026–27 Helios FTC 5214 team: leadership, software, hardware, electrical, design, business, outreach, drive team and mentors.', 'team', team, '/team/')

# ================================================================ OUTREACH
outreach_photos = [
    ('lakeside-team-presentation.webp', 1050, 433, 'Helios members talking about robotics at Lakeside', 'Talking about how we build the robot'),
    ('lakeside-programming-group.webp', 2048, 1134, 'Helios members with the robot during the programming activity', 'The programming activity'),
    ('lakeside-intellikits-demo.webp', 958, 900, 'A Helios member holding an IntelliKits model', 'Showing how the model works'),
    ('lakeside-kit-parts.webp', 993, 900, 'IntelliKits parts on a table', 'Parts from one of our kits'),
    ('intellikits-rubber-band-car.webp', 631, 581, 'A blue rubber-band-powered model car', 'A finished rubber band car'),
]
photo_grid = ''.join(f'<figure class="photo-card"><div class="photo-card-img" data-reveal-img><div class="reveal-img-inner"><img src="/assets/{f}" width="{w}" height="{h}" loading="lazy" decoding="async" alt="{a}"></div></div><figcaption>{c}</figcaption></figure>' for f, w, h, a, c in outreach_photos)
outreach = page_hero('Outreach', 'We run hands-on STEM events for younger kids.', 'Community') + f'''
<section class="section" data-theme="light" id="lakeside-2026"><div class="container">
<div class="story">
<div class="story-copy">
<p class="page-meta">October 16, 2026 · Concord, CA</p>
<h2 class="h2" data-split>{split('IntelliKits at *Lakeside*')}</h2>
<div class="prose">
<p>We ran a STEM event for kids in the youth program at the Lakeside Apartments community center in Concord.</p>
<p>First we showed them our competition robot and explained how we designed and programmed it. Then the kids tried a programming activity and built model cars from our IntelliKits.</p>
<p>IntelliKits are simple engineering kits we put together so kids can build something themselves. We want more kids to get to try robotics, especially in places where programs and equipment are harder to find.</p>
</div>
</div>
{img_reveal('/assets/lakeside-team-workshop.webp', 1050, 551, 'Helios members showing engineering models at the Lakeside community center', 'story-photo', 'eager', '0.06')}
</div>
<div class="photo-grid">{photo_grid}</div>
</div></section>
<section class="section callout-sec" data-theme="dark"><div class="container callout">
<h2 class="h2" data-split>{split('Want us at your event?')}</h2>
<p>We can bring the robot and a set of IntelliKits to schools, libraries and community centers. Email us and tell us about your event.</p>
{btn('/contact/', 'Contact us', 'sun', attrs=' data-magnetic')}
</div></section>'''
page('Outreach', 'Helios FTC 5214 brought our robot, a programming activity and IntelliKits to kids at the Lakeside community center in Concord.', 'outreach', outreach, '/outreach/')

# ================================================================ SEASONS
archive = ''.join(f'<li><a href="{url}"{EXT}><span class="arc-year">{year}</span><strong>{name}</strong><span class="arc-tag">FIRST results</span>{arrow_diag}</a></li>' for year, name, url in seasons[2:])
seasons_page = page_hero('Seasons', 'We’ve competed in FTC since 2010. Here’s this season, last season, and our official results from earlier years.', '16 seasons') + f'''
<section class="section" data-theme="light"><div class="container">
<div class="season-cards">
<a class="season-card" href="/seasons/biobuzz/"><div class="season-card-img">{xray('xray--card', 'Eclipse, our 2026–27 robot')}</div><div class="season-card-body"><span>2026–27 · This season</span><h2>BIOBUZZ</h2><p>Our robot is Eclipse. Updates through the season.</p></div></a>
<a class="season-card season-card--award" href="/seasons/decode/"><div class="season-card-img award"><span>East Bay League Tournament</span><strong>Innovate Award</strong><span>February 8, 2026</span></div><div class="season-card-body"><span>2025–26 · Last season</span><h2>DECODE</h2><p>11–7 across four official events.</p></div></a>
</div></div></section>
<section class="section" data-theme="dark"><div class="container">
{section_head('Earlier seasons', 'These link to our official results on the FIRST events site. Some older records list the team under a previous name.')}
<ul class="archive">{archive}</ul>
</div></section>'''
page('Seasons', 'Helios FTC Team 5214 seasons: 2026–27 BIOBUZZ, 2025–26 DECODE, and official FIRST results from earlier years.', 'seasons', seasons_page, '/seasons/')

# ================================================================ BIOBUZZ
back_seasons = f'<a href="/seasons/" class="back-link">{arrow_back}<span>All seasons</span></a>'
biobuzz = page_hero('BIOBUZZ', 'BIOBUZZ is this year’s FTC game. Our robot is Eclipse, and we’ll post updates here as the season goes on.', '2026–27 season', top=back_seasons, cls='page-hero--season') + f'''
<section class="section robot-sec" data-theme="dark"><div class="container">
<div class="robot-head"><h2 class="h2" data-split>{split('Eclipse')}</h2><p>Hover over the robot, or tap the button, to see the CAD.</p></div>
<div class="robot-stage">{xray('xray--dark', 'Eclipse, our 2026–27 robot')}<button class="xray-toggle xray-toggle--dark" type="button" data-xray-toggle aria-pressed="false">{xray_icon}<span class="xray-toggle-text" data-on="Show the robot" data-off="Show the CAD">Show the CAD</span></button></div>
</div></section>
<section class="section" data-theme="light"><div class="container">
{section_head('Events', 'East Bay League meets this season.', tlink('https://ftc-resources.firstinspires.org/ftc/game', 'Official game info', True))}
<a class="event-card" href="{MEET1}">
{img_reveal('/assets/meet1-team-robot.webp', 1024, 768, 'Helios team members with Eclipse at East Bay League Meet One', 'event-card-img')}
<div class="event-card-body"><p class="page-meta">November 1, 2026 · Dublin, CA</p><h3>East Bay League Meet One</h3><p>Our first meet of the season. In Qualification 17 our alliance scored 118, the high score of the event.</p><span class="tlink"><span>Photos and results</span>{arrow}</span></div>
</a>
</div></section>
<div class="container next-wrap"><a class="next-link" href="/seasons/decode/"><span>Last season</span><strong>DECODE</strong>{arrow}</a></div>'''
page('BIOBUZZ 2026–27', 'Helios FTC 5214 in the 2026–27 BIOBUZZ season: our robot Eclipse and our event results.', 'seasons', biobuzz, '/seasons/biobuzz/')

# ================================================================ DECODE
decode_events = [('East Bay League Meet 1', 'November 9, 2025', ''), ('East Bay League Meet 2', 'December 7, 2025', ''), ('East Bay League Meet 3', 'January 18, 2026', ''), ('East Bay League Tournament', 'February 8, 2026', 'Innovate Award')]
event_rows = ''.join(f'<li><span class="ev-num">{i + 1}</span><strong>{n}</strong>{"<b class=" + chr(34) + "award" + chr(34) + ">" + a + "</b>" if a else ""}<span class="ev-date">{d}</span></li>' for i, (n, d, a) in enumerate(decode_events))
decode = page_hero('DECODE', 'We finished DECODE 11–7 across four official events and won the Innovate Award, sponsored by RTX, at the East Bay League Tournament.', '2025–26 season', top=back_seasons, cls='page-hero--season') + f'''
<section class="stat-band" data-theme="dark"><div class="container stat-grid">
<div><strong>11–7</strong><span>Official match record</span></div><div><strong data-count="4">4</strong><span>Official events</span></div><div><strong data-count="1">1</strong><span>Innovate Award</span></div>
</div></section>
<section class="section" data-theme="light"><div class="container">
{section_head('Events', 'Three East Bay League meets, then the league tournament.', tlink('https://ftc-events.firstinspires.org/2025/team/5214', 'Results on FIRST', True))}
<ol class="events">{event_rows}</ol>
<p class="small-note">We also played the Lobster Cup in August 2026. It was an off-season event, so it isn’t counted here.</p>
</div></section>
<div class="container next-wrap"><a class="next-link" href="/seasons/biobuzz/"><span>This season</span><strong>BIOBUZZ</strong>{arrow}</a></div>'''
page('DECODE 2025–26', 'Helios FTC 5214 in the 2025–26 DECODE season: 11–7 record, four official events and the Innovate Award.', 'seasons', decode, '/seasons/decode/')

# ================================================================ CONTACT
topics = ['General inquiry', 'Outreach collaboration', 'Sponsorship or support', 'Competition or robotics', 'Other']
topic_pills = ''.join(f'<label class="pill"><input type="radio" name="subject" value="{t}"{" required" if i == 0 else ""}><span>{t}</span></label>' for i, t in enumerate(topics))
contact = f'''<section class="contact-hero" data-theme="light"><div class="container">
<h1 class="page-title" data-split>{split('Contact')}</h1>
<div class="contact-grid">
<div class="contact-info">
<p class="page-lead">Questions about the team, sponsorship or outreach? Email us or send a message with the form.</p>
<p class="contact-sponsor">Thinking about sponsoring us? {tlink('/sponsor/', 'See our sponsorship tiers')}</p>
<div class="contact-cards">
<div class="contact-card contact-card--dark"><span class="contact-label">Email</span><a class="contact-big" href="mailto:{EMAIL}">{EMAIL}</a><button class="copy-btn" type="button" data-copy="{EMAIL}">{copy_icon}<span>Copy</span></button></div>
<div class="contact-card"><span class="contact-label">Instagram</span><a class="contact-big" href="{INSTAGRAM}"{EXT}>@ftc5214helios</a></div>
<div class="contact-card"><span class="contact-label">Where we are</span><p>{school_link()}<br>Dublin, California</p></div>
</div>
</div>
<form id="contact-form" class="contact-form" novalidate>
<h2 class="form-title">Send a message</h2>
<fieldset class="form-field"><legend>What’s it about? <span>*</span></legend><div class="pills">{topic_pills}</div></fieldset>
<div class="form-row"><div class="form-field"><label for="contact-name">Name <span>*</span></label><input id="contact-name" name="name" type="text" autocomplete="name" maxlength="120" required></div>
<div class="form-field"><label for="contact-email">Email <span>*</span></label><input id="contact-email" name="email" type="email" autocomplete="email" maxlength="200" required></div></div>
<div class="form-field"><label for="contact-message">Message <span>*</span></label><textarea id="contact-message" name="message" rows="6" minlength="10" maxlength="5000" required></textarea></div>
<div class="hidden-field" aria-hidden="true"><label for="contact-company">Company website (leave blank)</label><input id="contact-company" name="company" type="text" tabindex="-1" autocomplete="off"></div>
<div id="form-feedback" class="form-feedback" aria-live="polite" role="status"></div>
<button class="btn btn--sun submit-button" type="submit"><span class="btn-label"><span class="submit-label">Send message</span><span aria-hidden="true">Send message</span></span><span class="btn-icon">{arrow}</span></button>
</form>
</div></div></section>'''
page('Contact', f'Contact Helios FTC Team 5214. Email {EMAIL} or send us a message.', 'contact', contact, '/contact/')

# ================================================================ EAST BAY LEAGUE MEET ONE
meet_photos = [
    ('meet1-team-robot.webp', 1024, 768, 'The team with Eclipse', 'The team gathered around Eclipse before matches.'),
    ('meet1-score-118.webp', 1024, 768, '118 to 49', 'Qualification 17. We were on the red alliance.'),
    ('meet1-score-99.webp', 1024, 768, '99 to 9', 'Qualification 9. We were on the blue alliance.'),
    ('meet1-robot-workbench.webp', 1680, 1120, 'Eclipse in the pits', 'A close look at the robot before competing.'),
    ('meet1-robot-field.webp', 1120, 1680, 'Ready for a match', 'Eclipse on the competition floor.'),
    ('meet1-team-hands.webp', 1680, 1120, 'Between matches', 'Team members at the event.'),
    ('meet1-robot-game.webp', 1680, 1120, 'On the field', 'Eclipse during a match.'),
    ('meet1-robot-match.webp', 1680, 1120, 'Near the game elements', 'Eclipse lining up during a match.'),
    ('meet1-teammates-strategy.webp', 1120, 1680, 'Planning', 'Talking strategy beside the field.'),
]
gallery = ''.join(
    f'<figure class="gallery-item"><a href="/assets/{f}" target="_blank" rel="noopener noreferrer" data-lightbox-item aria-label="Open full photo: {t}">'
    f'<img src="/assets/{f}" width="{w}" height="{h}" {"loading=" + chr(34) + "eager" + chr(34) if i == 0 else "loading=" + chr(34) + "lazy" + chr(34)} decoding="async" alt="{t}"><span class="gallery-zoom">{expand}</span></a>'
    f'<figcaption><strong>{t}</strong><span>{c}</span></figcaption></figure>'
    for i, (f, w, h, t, c) in enumerate(meet_photos))
back_biobuzz = f'<a class="back-link" href="/seasons/biobuzz/">{arrow_back}<span>BIOBUZZ season</span></a>'
event_page = page_hero('Meet One', 'Our first East Bay League meet of BIOBUZZ. In Qualification 17 our red alliance won 118 to 49, the highest score at the event.', 'November 1, 2026 · Quarry Lane School, Dublin, CA', top=back_biobuzz) + f'''
<section class="section" data-theme="dark"><div class="container">
<div class="scores">
<div class="score score--red"><span>Qualification 17 · Red alliance</span><strong data-count="118">118</strong><em>to 49</em></div>
<div class="score score--blue"><span>Qualification 9 · Blue alliance</span><strong data-count="99">99</strong><em>to 9</em></div>
</div>
<p class="scores-note">Both were wins. {tlink('https://ftc-events.firstinspires.org/2026/USCANOEBM1', 'Full results on FIRST', True)}</p>
</div></section>
<section class="section" data-theme="light" id="photos"><div class="container">
{section_head('Photos', 'Select any photo to see it full size.')}
<div class="gallery" data-lightbox>{gallery}</div>
</div></section>
<div class="container next-wrap"><a class="next-link" href="/seasons/biobuzz/"><span>Back to</span><strong>BIOBUZZ</strong>{arrow}</a></div>'''
page('East Bay League Meet One', 'Helios FTC 5214 at East Bay League Meet One on November 1, 2026: photos and our 118-point match.', 'seasons', event_page, MEET1)

# ================================================================ SPONSOR
TIERS = [  # key, name, min, max (None = no cap), label
    ('core', 'Core', 0, 299, 'Up to $299'),
    ('radiance', 'Radiance', 300, 499, '$300–$499'),
    ('plasma', 'Plasma', 500, 999, '$500–$999'),
    ('flare', 'Flare', 1000, 1999, '$1,000–$1,999'),
    ('corona', 'Corona', 2000, None, '$2,000+'),
]
PERKS = [  # perk, first tier index that gets it
    ('Sponsor sticker on our robot', 0),
    ('Your logo on our team hoodie', 1),
    ('A video made just for you', 2),
    ('Shoutouts during alliance selection', 3),
    ('Thanked during our presentations', 3),
    ('Your own Presenting Sponsor page on our website and all our social media', 4),
    ('Highlighted in our Team Engineering Portfolio', 4),
]
BUDGET = [  # category, dollars, what it pays for
    ('Event Registration', 1500, 'Entry fees for league meets and tournaments.'),
    ('Travel', 1000, 'Getting the team and the robot to events.'),
    ('Robot Electrical', 700, 'Motors, servos, sensors and wiring.'),
    ('Practice Half Field', 700, 'A half field of our own, so our drivers can practice more. The field we use now has limited access.'),
    ('Outreach', 500, 'Supplies for outreach, like the filament we use to 3D print IntelliKits.'),
    ('Tools and Equipment', 500, 'The tools we use to build and fix the robot.'),
    ('Raw Materials', 500, 'Raw materials for building robot parts.'),
    ('Robot Mechanical', 300, 'Mechanical robot parts.'),
    ('Team Apparel', 300, 'Team shirts and hoodies. Radiance sponsors and up get their logo on the hoodie.'),
]
BUDGET_TOTAL = sum(b[1] for b in BUDGET)
BUDGET_COLORS = ['#E0441F', '#EA6328', '#F08532', '#F6A32C', '#F7C04E', '#F3D58A', '#C29A62', '#7E6650', '#33302C']
TIER_ICONS = {
    'core': '<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="12" cy="12" r="4.2" fill="currentColor"/>',
    'radiance': '<circle cx="12" cy="12" r="4.2" fill="currentColor"/>' + ''.join(
        f'<path d="M12 {1.8} V{5.2}" stroke="currentColor" stroke-width="2" stroke-linecap="round" transform="rotate({a} 12 12)"/>' for a in range(0, 360, 45)),
    'plasma': ''.join(f'<path d="M3 {y}c2.2-2.6 4.3-2.6 6.5 0s4.3 2.6 6.5 0 3.7-2.2 5-.6" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/>' for y in (7.5, 12.5, 17.5)),
    'flare': '<path d="M12 2.8c.6 3.2 4.6 5.4 4.6 10.1A4.6 4.6 0 0 1 12 17.5a4.6 4.6 0 0 1-4.6-4.6c0-2 1-3.4 2-4.4.2 1.4.9 2.4 1.9 2.8-.4-3.1.4-6.1.7-8.5Z" fill="currentColor"/><path d="M8.5 20.6h7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
    'corona': '<circle cx="12" cy="12" r="5.2" fill="currentColor"/>' + ''.join(
        f'<path d="M12 {1.6} V{4.4}" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" transform="rotate({a} 12 12)"/>' for a in range(0, 360, 30)),
}
def tier_icon(key):
    return f'<svg class="tier-icon" viewBox="0 0 24 24" aria-hidden="true">{TIER_ICONS[key]}</svg>'
check = '<svg class="icon" viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="m4.5 10.5 3.6 3.6 7.4-8" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
lock = '<svg class="icon" viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="4.5" y="9" width="11" height="8" rx="2" stroke="currentColor" stroke-width="1.6"/><path d="M7 9V6.8a3 3 0 0 1 6 0V9" stroke="currentColor" stroke-width="1.6"/></svg>'
download = '<svg class="icon" viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M10 3v10m-4.5-4.5L10 13l4.5-4.5M4 16.5h12" stroke="currentColor" stroke-width="1.9"/></svg>'

def money(n):
    return f'${n:,}'

sponsor_data = json.dumps({
    'tiers': [{'key': k, 'name': n, 'min': lo, 'max': hi, 'label': lab} for k, n, lo, hi, lab in TIERS],
    'perks': [{'text': t, 'tier': i} for t, i in PERKS],
    'budget': [{'name': n, 'cost': c} for n, c, _ in BUDGET],
    'total': BUDGET_TOTAL, 'email': EMAIL,
}, ensure_ascii=False)

# ---- hero
sp_hero = f'''<section class="sp-hero" data-theme="dark"><div class="container sp-hero-grid">
<div class="sp-hero-copy">
<p class="page-meta">Sponsorship · 2026–27</p>
<h1 class="page-title" data-split>{split('Sponsor Helios')}</h1>
<p class="page-lead">We’re trying to make STEM accessible to everyone. It costs about $6,000 to run Helios for a year: robot parts, event fees, tools, travel and the outreach we run for younger kids. Every sponsor helps.</p>
<div class="sp-hero-actions">{btn('#build', 'Pick your tier', 'sun', attrs=' data-magnetic')}{btn('/assets/helios-sponsorship-package.pdf', 'Download the PDF', 'line', icon=download, attrs=' download data-magnetic')}</div>
</div>
<div class="sp-hero-goal" aria-label="$6,000 to run Helios for one year">
<span class="sp-hero-label">To run Helios for one year</span>
<strong>$<span data-count="{BUDGET_TOTAL}">{BUDGET_TOTAL:,}</span></strong>
<div class="sp-hero-tiers" aria-hidden="true">{"".join(f'<span class="tier--{k}">{tier_icon(k)}</span>' for k, *_ in TIERS)}</div>
</div>
</div></section>'''

# ---- impact numbers
impact_stats = [(15, '+', 'teams mentored in the US, Canada, India and Romania'), (500, '+', 'students at our camps and workshops'),
                (17, '', 'FTC and FLL events hosted'), (3000, '+', 'people reached at outreach events'),
                (1200, '', 'volunteer hours'), (200, '+', 'IntelliKits given out')]
impact = f'''<section class="section sp-impact" data-theme="light"><div class="container">
{section_head('What your money *backs*', 'We’re a FIRST Tech Challenge team from The Quarry Lane School in Dublin. Beyond competing, we run outreach, teach classes and build kits so more kids can get hands-on with engineering.')}
<dl class="sp-stats">{"".join(f'<div><dt>{d}</dt><dd><span data-count="{n}">{n:,}</span>{s}</dd></div>' for n, s, d in impact_stats)}</dl>
</div></section>'''

# ---- interactive builder
presets = [150, 300, 500, 1000, 2000]
tier_btns = ''.join(f'<button type="button" class="sp-preset" data-amount="{a}">{money(a)}</button>' for a in presets)
perk_items = ''.join(f'<li class="sp-perk" data-perk-tier="{i}"><span class="sp-perk-mark sp-perk-yes">{check}</span><span class="sp-perk-mark sp-perk-no">{lock}</span><span class="sp-perk-text">{t}</span><span class="sp-perk-unlock">{TIERS[i][4].replace("Up to $299", "Any amount")}</span></li>' for t, i in PERKS)
track_ticks = ''.join(f'<span class="sp-tick tier--{k}" style="--at:{i / len(TIERS):.4f}"><b>{n}</b><small>{money(lo) if lo else "$50"}</small></span>' for i, (k, n, lo, _, _) in enumerate(TIERS))
builder = f'''<section class="section sp-build" id="build" data-theme="dark" data-sponsor><div class="container">
{section_head('Build your *sponsorship*', 'Slide to an amount and see which tier it lands in, what you get, and what it pays for. Each tier includes everything in the tiers below it.')}
<div class="sp-build-grid">
<div class="sp-panel sp-amount-panel">
<label class="sp-amount-label" for="sp-amount">Your gift</label>
<div class="sp-amount-row"><span class="sp-dollar">$</span><input id="sp-amount" class="sp-amount-input" type="text" inputmode="numeric" value="500" aria-describedby="sp-tier-name" data-sp-input></div>
<div class="sp-slider-wrap">
<input class="sp-slider" type="range" min="0" max="100" step="0.1" value="40" aria-label="Sponsorship amount" aria-valuetext="$500" data-sp-slider>
<div class="sp-ticks" aria-hidden="true">{track_ticks}</div>
</div>
<div class="sp-presets" role="group" aria-label="Quick amounts">{tier_btns}</div>
<div class="sp-cover">
<div class="sp-cover-top"><span>Share of our $6,000 year</span><strong data-sp-pct>8%</strong></div>
<div class="sp-cover-bar"><i data-sp-bar></i></div>
<p class="sp-cover-text" data-sp-covers>Enough to cover our Outreach budget for the year.</p>
</div>
</div>
<div class="sp-panel sp-tier-panel" data-sp-tier="plasma" aria-live="polite">
<div class="sp-tier-head">
<span class="sp-tier-badge" data-sp-icon>{tier_icon('plasma')}</span>
<div><span class="sp-tier-num" data-sp-num>Tier 3</span><h3 class="sp-tier-name" id="sp-tier-name" data-sp-name>Plasma</h3><span class="sp-tier-range" data-sp-range>$500–$999</span></div>
</div>
<ul class="sp-perks">{perk_items}</ul>
<p class="sp-next" data-sp-next>Add $500 to reach Flare: shoutouts during alliance selection.</p>
<div class="sp-tier-actions">{btn('#sponsor-form', 'Sponsor at this level', 'sun', attrs=' data-sp-go data-magnetic')}<a class="tlink sp-mail" href="mailto:{EMAIL}" data-sp-mail><span>Or email us</span></a></div>
</div>
</div>
</div></section>'''

# ---- tier table
th = ''.join(f'<th scope="col" class="tier--{k}" data-col="{i}"><button type="button" class="sp-col-btn" data-amount="{max(lo, 150)}">{tier_icon(k)}<span class="sp-col-name">{n}</span><span class="sp-col-num">Tier {i + 1}</span><span class="sp-col-range">{lab}</span></button></th>'
             for i, (k, n, lo, hi, lab) in enumerate(TIERS))
rows = ''.join('<tr><th scope="row">' + t + '</th>' + ''.join(
    f'<td class="tier--{TIERS[j][0]}" data-col="{j}">' + (f'{check}<span class="sr-only">Included</span>' if j >= i else '<span class="sp-dash" aria-hidden="true">–</span><span class="sr-only">Not included</span>') + '</td>'
    for j in range(len(TIERS))) + '</tr>' for t, i in PERKS)
tier_table = f'''<section class="section sp-tiers" id="tiers" data-theme="light"><div class="container">
{section_head('All five *tiers*', 'Named after the parts of the sun. Pick a tier to load it into the builder.')}
<div class="sp-table-wrap" data-sp-table><table class="sp-table">
<thead><tr><td class="sp-corner">Each tier includes everything in the tiers below it.</td>{th}</tr></thead>
<tbody>{rows}</tbody></table></div>
</div></section>'''

# ---- budget
seg = ''.join(f'<button type="button" class="sp-seg" style="--w:{c / BUDGET_TOTAL:.4f};--i:{i};--c:{BUDGET_COLORS[i]}" data-seg="{i}" aria-label="{n}, {money(c)}"></button>' for i, (n, c, _) in enumerate(BUDGET))
legend = ''.join(f'<li><button type="button" class="sp-leg" data-seg="{i}" style="--i:{i};--c:{BUDGET_COLORS[i]}"><span class="sp-leg-dot"></span><span class="sp-leg-name">{n}</span><span class="sp-leg-cost">{money(c)}</span><span class="sp-leg-desc">{d}</span></button></li>' for i, (n, c, d) in enumerate(BUDGET))
budget = f'''<section class="section sp-budget" data-theme="light"><div class="container">
{section_head('Where the *$6,000* goes', 'Our estimated costs for one year. Tap a category to see what it pays for.')}
<div class="sp-budget-card" data-sp-budget>
<div class="sp-bar" data-reveal-bar>{seg}</div>
<div class="sp-budget-grid">
<ul class="sp-legend">{legend}</ul>
<div class="sp-budget-detail"><span class="sp-detail-label">Selected</span><strong class="sp-detail-name" data-sp-dname>Event Registration</strong><span class="sp-detail-cost" data-sp-dcost>$1,500 · 25% of the year</span><p data-sp-ddesc>{BUDGET[0][2]}</p></div>
</div>
<div class="sp-total"><span>Total budget</span><strong>{money(BUDGET_TOTAL)}</strong></div>
</div>
</div></section>'''

# ---- record + where we're going
going = [('Adaptive technology workshops', 'For people with autism and Down syndrome, through FCSN.'),
         ('e-NABLE prosthetic hands', 'Building 3D printed prosthetic hands with the e-NABLE community.'),
         ('Starter parts for new teams', 'For new FLL and FTC teams at Title 1 schools in Oakland. We’re already talking with them.'),
         ('A practice half field', 'So our drivers can train more. The field we use now has limited access.')]
success = f'''<section class="section sp-success" data-theme="dark"><div class="container">
<div class="sp-success-grid">
<div>
<h2 class="h2" data-split>{split('A top team in our *league*')}</h2>
<p class="sp-success-text">We’re ranked 2nd in the East Bay League so far this season with a 4-1-0 record. Our awards include the Innovate, Motivate and Judges’ Choice Awards.</p>
<dl class="sp-record"><div><dt>League rank</dt><dd>2nd</dd></div><div><dt>W-L-T this season</dt><dd>4-1-0</dd></div></dl>
</div>
{img_reveal('/assets/sponsor-award.webp', 1000, 803, 'Last season’s robot with the East Bay League Tournament Innovate Award', 'sp-award')}
</div>
<div class="sp-going">
<h3 class="sp-going-title">With your support, here’s what’s next</h3>
<ol class="sp-going-list">{"".join(f'<li><span class="sp-going-n">{i + 1:02d}</span><strong>{t}</strong><p>{d}</p></li>' for i, (t, d) in enumerate(going))}</ol>
<figure class="sp-field"><img src="/assets/sponsor-half-field.webp" width="971" height="971" loading="lazy" decoding="async" alt="The BIOBUZZ half field we want to buy: a goal frame, four ball holders, two trays, and 40 yellow, 8 red and 8 blue balls"><figcaption>The half field we’re raising money for</figcaption></figure>
</div>
</div></section>'''

# ---- community accordion
mentored = [('FLL', '65169', 'Terrace Tech Titans'), ('FTC', '14770', 'Control+Q'), ('FTC', '26586', 'Argobots'), ('FTC', '25707', 'Solar Flare'),
            ('FTC', '18466', 'Mastermindz'), ('FTC', '6134', 'Black Frogs'), ('FTC', '11920', 'RaD'), ('FTC', '19071', 'Smart Cluster')]
chips = ''.join(f'<li><span>{p} #{num}</span>{nm}</li>' for p, num, nm in mentored)
community_items = [
    ('Starting new teams', '<p>Our program founded FTC teams 15034, 23836 and 23808 and FLL teams 64080, 63582, 63583 and 63308, including four all-girls teams. We’ve helped families start three more teams after meeting them at events, and we help Girl Scouts earn three robotics badges.</p>'),
    ('Mentoring 15+ teams', f'<p>We mentor teams in the US, Canada, India and Romania. Our belted drivetrain advice helped the Argobots double their OPR.</p><ul class="sp-chips">{chips}</ul>'),
    ('Our school’s FIRST pipeline', '<p>Quarry Lane runs 7 FLL teams and 6 FTC teams that feed into FRC 7419. Students start in FLL, move up to FTC teams like Helios, then lead on 7419, and many come back to mentor the younger teams. We also help run four admissions events a year with live robot demos.</p>'),
    ('Workshops and events', '<p>Our camps and workshops with IGNITE Pathways in CAD, Java, Python, Scratch and robotics have reached 500+ students, about 50 per camp. We’ve hosted 13 FTC and 4 FLL events in four years, including four East Bay League meets for 30+ teams in 2023. In summer 2023 we taught kids 9 and up Python with Turtle at Dublin Library.</p>'),
    ('IntelliKits', '<p>IntelliKits are simple engineering kits we put together so kids can build something themselves, especially where programs and equipment are hard to find. We’ve given out 200+ 3D printed physics kits to John Green Elementary School, and we partner with HOPE Solutions to run IntelliKits events for kids facing housing insecurity.</p>'),
    ('Supporting kids who need it most', '<p>We’ve taught kids at Shepherd’s Gate, a Livermore shelter for women and children, every Tuesday since August 2022, and we run a December food drive for its residents.</p>'),
    ('Workshops in India', '<p>In summer 2024 we ran a two-day M-Bot workshop at government-funded schools and brought books, shoes, uniforms and stationery. We still meet the same students every two months as they learn Java and Python.</p>'),
    ('Reaching people online', '<p>Our free educational blog at ignitepathways.org has 150+ posts and 73,000+ views. FTC Bonfire, our free scouting and strategy platform for the FTC community, is used by 1,000+ people on 500+ teams on the web, iOS and Android. 1,150+ students in 100 countries have taken our STEAMBOT course.</p>'),
    ('Coral cleanup', '<p>With Team 1086 Blue Cheese from Virginia, we turned retired REEFSCAPE field elements into birdhouses for local wildlife and to raise awareness about ocean conservation.</p>'),
]
acc = ''.join(f'<details class="sp-acc"{" open" if i == 0 else ""}><summary><span class="sp-acc-n">{i + 1:02d}</span><span class="sp-acc-title">{t}</span><span class="sp-acc-plus" aria-hidden="true"></span></summary><div class="sp-acc-body">{b}</div></details>' for i, (t, b) in enumerate(community_items))
community = f'''<section class="section sp-community" data-theme="light"><div class="container sp-community-grid">
<div class="sp-community-head">
{section_head('Our *community*', 'What sponsors help us keep doing.')}
{img_reveal('/assets/sponsor-build.webp', 996, 1472, 'Two Helios members working on Eclipse in the pits', 'sp-community-photo', parallax='0.06')}
</div>
<div class="sp-accs">{acc}</div>
</div></section>'''

# ---- form
tier_pills = ''.join(f'<label class="pill sp-tier-pill tier--{k}"><input type="radio" name="tier" value="{n}"{" checked" if k == "plasma" else ""}><span>{tier_icon(k)}{n}</span></label>' for k, n, *_ in TIERS)
sp_form = f'''<section class="section sp-contact" id="sponsor-form" data-theme="light"><div class="container sp-contact-grid">
<div class="sp-contact-copy">
<h2 class="h2" data-split>{split('Let’s *talk*')}</h2>
<p class="section-lead">Tell us how you’d like to help. We’ll reply with our thanks and how to send your sponsorship. We appreciate any help, including in-kind support like parts, tools or materials.</p>
<div class="contact-card contact-card--dark"><span class="contact-label">Email</span><a class="contact-big" href="mailto:{EMAIL}">{EMAIL}</a><button class="copy-btn" type="button" data-copy="{EMAIL}">{copy_icon}<span>Copy</span></button></div>
</div>
<form class="contact-form" id="sponsor-inquiry" data-contact-form data-subject="Sponsorship or support" data-sponsor-form novalidate>
<h3 class="form-title">Sponsorship inquiry</h3>
<fieldset class="form-field"><legend>Tier</legend><div class="pills">{tier_pills}</div></fieldset>
<div class="form-row"><div class="form-field"><label for="sp-name">Your name <span>*</span></label><input id="sp-name" name="name" type="text" autocomplete="name" maxlength="120" required></div>
<div class="form-field"><label for="sp-email">Email <span>*</span></label><input id="sp-email" name="email" type="email" autocomplete="email" maxlength="200" required></div></div>
<div class="form-row"><div class="form-field"><label for="sp-org">Business or organization</label><input id="sp-org" name="org" type="text" autocomplete="organization" maxlength="160"></div>
<div class="form-field"><label for="sp-amt">Amount (USD)</label><input id="sp-amt" name="amount" type="text" inputmode="numeric" maxlength="12" value="500" data-sp-form-amount></div></div>
<div class="form-field"><label for="sp-message">Message <span>*</span></label><textarea id="sp-message" name="message" rows="5" minlength="10" maxlength="4500" required placeholder="Anything we should know, like in-kind support or how you heard about us."></textarea></div>
<div class="hidden-field" aria-hidden="true"><label for="sp-company">Company website (leave blank)</label><input id="sp-company" name="company" type="text" tabindex="-1" autocomplete="off"></div>
<div class="form-feedback" aria-live="polite" role="status" data-form-feedback></div>
<button class="btn btn--sun submit-button" type="submit"><span class="btn-label"><span class="submit-label">Send inquiry</span><span aria-hidden="true">Send inquiry</span></span><span class="btn-icon">{arrow}</span></button>
</form>
</div></section>'''

sponsor = sp_hero + impact + builder + tier_table + budget + success + community + sp_form + f'<script type="application/json" id="sponsor-data">{sponsor_data}</script>'
page('Sponsor', 'Sponsor Helios FTC 5214. It costs about $6,000 to run the team for a year. See our five sponsorship tiers, what each one includes and where the money goes.', 'sponsor', sponsor, '/sponsor/')


print('Generated', len(list(P.rglob('index.html'))), 'pages')
