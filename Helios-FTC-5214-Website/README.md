# HELIOS. — FTC Team 5214 website

An original, responsive, multi-page team website designed for GitHub + Vercel. The site is intentionally built with plain HTML, CSS, and JavaScript: **no frontend framework, build step, or npm dependencies** are needed.

## Pages

- `/` — Home
- `/about/` — About, 16-season history and values
- `/team/` — Bryan Pan, Yuvan Ramesh, Elan Jain, and Damodar Kriplani; portrait placeholders
- `/outreach/` — IntelliKits and community outreach
- `/contact/` — Working email form (after the serverless email integration is configured)
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

## Customize

- Update team members, copy, and seasons in `build_pages.py`, then run `python3 build_pages.py` to regenerate the HTML pages.
- Replace photo placeholders by adding photos under `public/assets/`, then swapping each `.member-photo` placeholder in the team-page generator for an `<img>` (with `alt="Bryan Pan"`, etc.). Keep matching crop via `object-fit: cover; width:100%; height:100%`.
- Edit colors, typography, layout in `public/assets/styles.css` (`:root` CSS variables).
- Edit browser interactions in `public/assets/main.js` and Vercel email logic in `api/contact.js`.
- Future outreach/robot photography can be inserted into the prepared visual areas. No invented community reach totals, sponsor logos, or robot specifications are included.

## Information sources / editorial notes

- Team profile / rookie year / home location / seasons: https://ftc-events.firstinspires.org/team/5214
- DECODE results, 11–7 official match record, four official events, Innovate Award: https://ftc-events.firstinspires.org/2025/team/5214
- CENTERSTAGE Motivate Award: https://ftc-events.firstinspires.org/2023/team/5214
- Season names: https://ftc-events.firstinspires.org/seasons

The official historic FTC record sometimes lists **B.R.O.** as Team 5214's earlier name; the site uses the currently provided Helios name and links to historical FIRST data. BIOBUZZ results are intentionally left as in-progress rather than invented. IntelliKits is based on team-provided context; review the outreach wording before publishing.

This site is an independent team website and is not an official FIRST® website. The FIRST® mark and season names belong to their respective owners.
