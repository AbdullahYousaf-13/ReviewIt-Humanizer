# Colleague to-do

Backend and logic tasks that come out of the frontend changes. Frontend text and layout are done by Abdullah. Add new items at the bottom.

Frontend changes are on branch `abdullah/frontend-updates` (a pull request is not open yet). Items below that mention frontend files refer to that branch. Last updated: 17 Nov 2026.

## Contact form
- Build `POST /api/contact` in nodeBackend.
- Body: `name`, `email`, `topic`, `message`, `website`.
- If `website` is not empty, return success and send nothing (spam trap).
- Check: name, valid email, message 10 to 2000 characters.
- Email the support address with the visitor's email as reply-to.
- Return `200 { success: true }`, `400` invalid input, `429` too many messages.
- Rate limit: a few messages per hour per person.

## Email
- Verify the `humoro.io` domain with the email service (sender is `onboarding@resend.dev` now).
- Create and monitor the support mailbox.
- Real support address replaces the placeholder: change `SITE.supportEmail` in `frontend/lib/site.ts`.

## Credits
- Credits must reset monthly for Hobby and for annual plans (the site says "Credits reset monthly").
- Status checked on main (17 Nov 2026): not implemented. There is no scheduler. Credits are refilled only when Stripe sends a `subscription_cycle` invoice (`services/stripeService.js`, around line 173). Hobby is never refilled, and an annual plan gets one refill a year.
- Hobby image check: confirm whether the 1 free check resets monthly or is one time.

## Stripe
- Rename the products and descriptions: "Veritas AI Pro" and "Veritas AI Unlimited" become Humoro Pro and Humoro Max.
- Remove old claims from the descriptions: "Unlimited words", "Up to 50k words", "Up to 10k words", "2 layer humanization".
- Update the `app: 'veritas_ai'` metadata value if anything reads it.

## Rename Veritas to Humoro in nodeBackend
- `utils/emailService.js`: sign-up code email text, sender name, subject.
- `utils/stripeInit.js`, `server.js`, `middlewares/authMiddleware.js`, `models/blogModel.js`.
- `controllers/admin/adminBlogController.js`, `seedBlogs.js`, `README.md`, `package.json`, `.env.example`.
- `utils/generateToken.js`: the fallback secret text contains the old name (changing a secret signs everyone out).

## Browser storage keys
- Rename `veritas_token` and `veritas_user` in `frontend/lib/nodeApi.ts`. Everyone is signed out once.

## Blog content
- The real blog posts live in the database (seeded by `seedBlogs.js`, edited in the admin editor). They still say Veritas, and `seedBlogs.js` (around line 59) names a detector model ("BERT architecture") and describes internal features. Edit titles, slugs and text in the database and in `seedBlogs.js`.
- Check the published posts for claims that have no source. Blog text now supports links written as `[text](https://...)`.
- The sample articles in `frontend/lib/blogApi.ts` (shown only when the blog service returns nothing) are a separate set, already updated by Abdullah.

## SEO and deployment
- Set `NEXT_PUBLIC_SITE_URL` in the production environment to the final domain (canonical links, sitemap, share images use it). The fallback `https://humoro.io` is a placeholder.
- The blog list and blog posts are now fetched on the Next.js server. `NEXT_PUBLIC_NODE_API_URL` must be reachable from the server, not only from the browser.
- Restart the Next.js server after pulling: `next.config.js` now sends a `noindex` header for the dashboard, admin, profile, login and signup pages.
- After launch: verify the domain in Google Search Console and Bing Webmaster Tools and submit `/sitemap.xml`.

## Social profiles
- Provide the real social profile links (LinkedIn, X, GitHub or others). The four footer icons in `frontend/components/landing/footer.tsx` still go nowhere (`href="#"`).
- When the links exist, add them as `sameAs` in the Organization data in `frontend/app/page.tsx`.

## Logo (new kit)
- Email template (`utils/emailService.js`): the sign-up code email shows only the word Humoro; add the new logo (needs a hosted image address).
- Stripe: upload the logo and icon in the Stripe branding settings (checkout page and receipts).
- Google sign-in: upload the logo in the Google Cloud OAuth consent screen.
