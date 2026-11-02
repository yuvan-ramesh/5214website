# Helios, FTC Team 5214 website

A multi-page team website for GitHub + Vercel, built with plain HTML, CSS and JavaScript. There is **no framework and no build step on Vercel**. Pages are generated locally by `build_pages.py` and the output in `public/` is committed.

## Pages

- `/` Home: robot hero with the CAD X-ray effect, scroll-scrubbed robot turntable, Meet One photo track, seasons, team, outreach
- `/about/` About, timeline and how the team is organized
- `/team/` 2026–27 team by group, with portrait placeholders
- `/outreach/` October 16, 2026 IntelliKits event at Lakeside Apartments in Concord
- `/contact/` Email, Instagram and the contact form
- `/seasons/` This season, last season, and links to official FIRST results for earlier seasons
- `/seasons/biobuzz/` 2026–27 BIOBUZZ with the Eclipse robot viewer and events
- `/seasons/biobuzz/east-bay-meet-one/` November 1, 2026 recap with scores and nine photos
- `/seasons/decode/` 2025–26 DECODE record, events and Innovate Award

## Preview locally

```bash
cd public
python3 -m http.server 8000
```

Open `http://localhost:8000`. The contact form **will not send email on the local static server**; `/api/contact` only runs on Vercel (or with the Vercel CLI).

## Edit the site

- Copy, team members, seasons and page layout: `build_pages.py`, then run `python3 build_pages.py` to regenerate every page in `public/`.
- Styles: `public/assets/styles.css`. Colors and fonts are CSS variables in `:root`.
- Behavior and animations: `public/assets/main.js`.
- Contact email delivery: `api/contact.js`.
- Team portraits: add photos under `public/assets/`, then replace the initials in `member_card()` in `build_pages.py` with an `<img>` (use `alt="Bryan Pan"` etc.).

## Design

- **Logo**: `public/assets/logo/helios-logo.svg` is a vector trace of the team logo. The wordmark uses `currentColor`, so it turns light on dark backgrounds. `helios-logo-black.svg` is the fixed-color version, `helios-mark.svg` is the sun alone, and `favicon.svg` is the browser icon.
- **Colors** come from the logo: sun orange `#F6A32C`, flare red `#E0441F`, core cream `#FDE9BD`, plus paper `#F2F0EB` and night `#121010` for light and dark sections.
- **Type**: Mona Sans (variable weight and width) for everything, with Gloock for a few serif accents. Both are self-hosted in `public/assets/fonts/` under the SIL Open Font License.
- **Smooth scrolling**: Lenis 1.3.27 (MIT), vendored at `public/assets/vendor/lenis.min.js`. It only runs on mouse and trackpad devices.
- **Motion**: first-visit loader, page transition curtain, headings that rise in, the robot X-ray lens in the hero, a scroll-scrubbed 360° turntable that switches to the CAD, marquee text that reacts to scroll speed, a sideways-scrolling photo track, image reveals, count-up numbers, and hover effects on buttons, cards and links.
- **Accessibility**: when a visitor has reduced motion turned on, the loader, transitions, smooth scrolling, pinned scroll scenes and auto-moving effects are switched off and everything is shown in place. Every image has alt text, the menu and photo viewer trap focus and close with Escape, and the site works without JavaScript (content is all in the HTML).

## Robot renders

`public/assets/robot/` holds images rendered from our Onshape CAD (Assembly 1 in the FTC 5214 document):

- `hero-render.webp`: the robot render (transparent background)
- `hero-cad.webp`: the CAD skeleton from the same camera, shown inside the X-ray lens
- `hero-cad-light.webp`: a line drawing of the CAD, shown when someone presses "Show the CAD"
- `spin/` and `spin-sm/`: 48 frames each of the render and the CAD for the home page turntable (`spin-sm` is used on phones)

The tools that made them are in `tools/robot-render/`. To re-render after the robot changes, export the assembly from Onshape as glTF and follow `tools/robot-render/README.md`.

## Deploy with GitHub + Vercel

1. Import the repository in [Vercel](https://vercel.com) with **Add New → Project → Import Git Repository**.
2. Vercel should detect `Other` (no framework). `vercel.json` sets the output directory to `public`; no build command is needed.
3. Deploy, then check that `/about/`, `/team/`, `/seasons/` and `/contact/` load.
4. Optional: connect a custom domain in Vercel → Project → Settings → Domains.

Every push to the production branch redeploys automatically once GitHub is connected.

## Make the contact form deliver email

The contact form posts to a serverless function that sends messages to **5214.helios@gmail.com** through [Resend](https://resend.com). It does not pretend to send anything before an email provider is set up.

1. Sign up for Resend, preferably with `5214.helios@gmail.com`, and create an API key with sending permission.
2. In Vercel → Project → Settings → Environment Variables, add:

   ```
   RESEND_API_KEY=re_your_key_here
   RESEND_FROM=Helios Website <hello@your-verified-domain.com>
   ```

3. Verify the sender domain in Resend. Without a domain, `RESEND_FROM=Helios Website <onboarding@resend.dev>` works for testing, but only to the email on your Resend account.
4. Redeploy (new environment variables need a deployment), send a test message from `/contact/`, and confirm it arrives and that Reply goes to the sender.

The form validates fields, has a hidden spam trap, escapes user-submitted HTML, uses a fixed destination inbox and never exposes the API key. If sending fails it shows an error and the email address. For high traffic, add a persistent rate limiter and a CAPTCHA to the API.

## Vercel Web Analytics

Each page loads Vercel's Web Analytics script (`/_vercel/insights/script.js`). Turn it on in Vercel → Project → **Analytics** → **Enable**, then redeploy. A 404 for that script means Analytics isn't enabled yet.

## School affiliation

Team 5214 is based at **The Quarry Lane School**, Dublin, California (https://www.quarrylane.org/). The school is linked from the home page, About, Contact and the footer.

## Information sources

- Team profile, rookie year, location and seasons: https://ftc-events.firstinspires.org/team/5214
- DECODE results, 11–7 official record, four official events, Innovate Award: https://ftc-events.firstinspires.org/2025/team/5214
- CENTERSTAGE Motivate Award: https://ftc-events.firstinspires.org/2023/team/5214
- Meet One results: https://ftc-events.firstinspires.org/2026/USCANOEBM1
- Season names: https://ftc-events.firstinspires.org/seasons

The official FTC record sometimes lists **B.R.O.** as Team 5214's earlier name; the site uses the Helios name and links to the historical FIRST data. Lakeside event details and photos were provided by the team. Photos of children are not used on the public site, and `photo-archive/` (outside `public/`) is not served.

This is an independent student team website, not an official FIRST® website. The FIRST® mark and season names belong to their owners.
