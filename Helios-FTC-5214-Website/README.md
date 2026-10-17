# HELIOS. — FTC Team 5214 website

An original, responsive, multi-page team website designed for GitHub + Vercel. The site is intentionally built with plain HTML, CSS, and JavaScript: **no frontend framework, build step, or npm dependencies** are needed.

## Pages

- `/` — Home
- `/about/` — About, 16-season history and values
- `/team/` — Bryan Pan, Yuvan Ramesh, Elan Jain, and Damodar Kriplani; portrait placeholders
- `/outreach/` — October 16, 2026 Lakeside Apartments STEM event (photo and details) plus IntelliKits
- `/contact/` — Instagram @ftc5214helios, direct email and email form (after serverless delivery is configured)
- `/seasons/` — Season landing page and earlier FIRST records
- `/seasons/biobuzz/` — 2026–27 BIOBUZZ
- `/seasons/decode/` — 2025–26 DECODE (verified award and event history)

## Preview locally

From this folder, run:

```bash
cd public
python3 -m http.server 8000
```

Open `http://localhost:8000`. Other routes such as `/team/` also work. The contact form **will not send email on the local static server**; the `/api/contact` endpoint only runs on Vercel (or with the Vercel CLI).

## Deploy with GitHub + Vercel

1. Create a GitHub repository, e.g. `helios-5214-website`.
2. Upload the **contents of this folder**, including `public/`, `api/`, and `vercel.json`, to the repository root. Do not upload only the `public` folder.
3. In [Vercel](https://vercel.com), select **Add New → Project → Import Git Repository** and select that repo.
4. Vercel should detect `Other` (no framework). `vercel.json` sets the output directory to `public`; no build command is required.
5. Deploy. Visit the Vercel-generated `.vercel.app` URL and confirm `/about/`, `/team/`, `/seasons/`, and `/contact/` work.
6. Optional: In Vercel → Project → Settings → Domains, connect a custom domain by following Vercel's DNS instructions. The same repo still works.

Every new push to your production branch will automatically redeploy after the GitHub integration is connected.

## Make the contact form deliver email

**The contact form has a real serverless API; it intentionally does not claim to send anything before you configure an email provider.** The API securely receives messages on Vercel and sends them to **5214.helios@gmail.com** through [Resend](https://resend.com). This avoids exposing credentials to the public browser.

1. Sign up for Resend, preferably using `5214.helios@gmail.com`. Create an API key with sending permission.
2. In Vercel → Project → Settings → Environment Variables, add:

   ```
   RESEND_API_KEY=re_your_key_here
   RESEND_FROM=Helios Website <hello@your-verified-domain.com>
   ```

3. Verify the sender domain in Resend before using its address. If you do not have a domain, Resend's `onboarding@resend.dev` sender may be used for testing **only to the email verified on your Resend account** (not unrestricted public sending). Use `RESEND_FROM=Helios Website <onboarding@resend.dev>` for such a restricted test.
4. Redeploy in Vercel (new environment variables need a deployment). Open `/contact/` and submit a real test message. Confirm it arrives at `5214.helios@gmail.com` and that Reply goes to the message sender.

The form validates fields, has a hidden spam trap, escapes user-submitted HTML, uses a fixed destination inbox, and never includes the API key in public files. If the provider is unconfigured or fails, it shows an error and offers direct email. For high traffic, add a persistent rate limiter and CAPTCHA in the API.


## Vercel Web Analytics

Each generated HTML page includes Vercel's lightweight **Web Analytics** loader (`/_vercel/insights/script.js`). No new npm packages or environment variables are needed for this static site.

**Required Vercel dashboard step:** select this project in Vercel → **Analytics** → **Enable**. Enable the feature and redeploy the latest commit to ensure the analytics endpoint is created. Visits should then appear under Analytics; allow time for data to arrive. If you see a 404 for `/_vercel/insights/script.js`, ensure Analytics is enabled and redeploy. Analytics only records page views after activation. This is **Web Analytics**, not Speed Insights.

## School affiliation

Team 5214 is based at **The Quarry Lane School**, Dublin, California. Its official site is https://www.quarrylane.org/ and is linked from the homepage, About, Contact and footer. The affiliation text is team-provided.

## Customize

- Update team members, copy, and seasons in `build_pages.py`, then run `python3 build_pages.py` to regenerate the HTML pages.
- Replace photo placeholders by adding photos under `public/assets/`, then swapping each `.member-photo` placeholder in the team-page generator for an `<img>` (with `alt="Bryan Pan"`, etc.). Keep matching crop via `object-fit: cover; width:100%; height:100%`.
- Edit colors, typography, layout in `public/assets/styles.css` (`:root` CSS variables).
- Edit browser interactions in `public/assets/main.js` and Vercel email logic in `api/contact.js`.
- Lakeside and IntelliKits are presented as one outreach event, with an anchored story at `/outreach/#lakeside-2026`. The supplied Nikon camera photos were converted into optimized, privacy-reviewed WebP crops: `lakeside-team-workshop.webp`, `lakeside-team-presentation.webp`, `lakeside-intellikits-demo.webp`, and `lakeside-kit-parts.webp`; the existing `intellikits-rubber-band-car.webp` is retained. The earlier photos featuring children have been removed from the public site. The homepage has a rotating five-photo carousel; clicking any picture goes to that event. To feature future event photos, add new slides and their destination links in `build_pages.py`, then regenerate the pages. The carousel pauses on hover and focus, supports arrows and photo dots, and respects reduced-motion preferences. No invented attendee counts, sponsor logos, or robot specifications are included.

## Information sources / editorial notes

- Team profile / rookie year / home location / seasons: https://ftc-events.firstinspires.org/team/5214
- DECODE results, 11–7 official match record, four official events, Innovate Award: https://ftc-events.firstinspires.org/2025/team/5214
- CENTERSTAGE Motivate Award: https://ftc-events.firstinspires.org/2023/team/5214
- Season names: https://ftc-events.firstinspires.org/seasons

The official historic FTC record sometimes lists **B.R.O.** as Team 5214's earlier name; the site uses the currently provided Helios name and links to historical FIRST data. BIOBUZZ results are intentionally left as in-progress rather than invented. Lakeside event details and the photo were provided by the team on October 16, 2026. IntelliKits is based on team-provided context.

This site is an independent team website and is not an official FIRST® website. The FIRST® mark and season names belong to their respective owners.
