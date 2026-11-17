# TO DO's

Backend and logic tasks that come out of the frontend changes.

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
- Replace the placeholder support address: change `SITE.supportEmail` in `frontend/lib/site.ts`.

## Credits
- Credits must reset monthly for every plan, including Hobby and annual plans (the site says "Credits reset monthly").
- Current state: there is no scheduler. Credits are refilled only when Stripe sends a `subscription_cycle` invoice (`services/stripeService.js`, around line 173), so Hobby is never refilled and an annual plan is refilled once a year.
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
- Existing blog posts (database and `seedBlogs.js`) still say Veritas. `seedBlogs.js` (around line 59) also names a detector model ("BERT architecture") and describes internal features. Edit titles, slugs and text.
- Check published posts for claims that have no source. Blog text supports links written as `[text](https://...)`.

## SEO and deployment
- Set `NEXT_PUBLIC_SITE_URL` in the production environment to the final domain (canonical links, sitemap and share images use it). The fallback `https://humoro.io` is a placeholder.
- The blog list and blog posts are fetched on the Next.js server, so `NEXT_PUBLIC_NODE_API_URL` must be reachable from the server, not only from the browser.
- Restart the Next.js server after pulling: `next.config.js` now sends a `noindex` header for the dashboard, admin, profile, login and signup pages.
- After launch: verify the domain in Google Search Console and Bing Webmaster Tools and submit `/sitemap.xml`.

## Social profiles
- Provide the real social profile links (LinkedIn, X, GitHub or others). The four footer icons in `frontend/components/landing/footer.tsx` still go nowhere (`href="#"`).
- When the links exist, add them as `sameAs` in the Organization data in `frontend/app/page.tsx`.

## Logo (new kit)
- Email template (`utils/emailService.js`): the sign-up code email shows only the word Humoro; add the new logo (needs a hosted image address).
- Stripe: upload the logo and icon in the Stripe branding settings (checkout page and receipts).
- Google sign-in: upload the logo in the Google Cloud OAuth consent screen.
