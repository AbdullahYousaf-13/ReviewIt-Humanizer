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
- Verify the `humoro.io` domain and the sender address with Amazon SES (sign-up emails now go through SES; without AWS credentials the code is only printed in the terminal).
- Create and monitor the support mailbox.
- Replace the placeholder support address: change `SITE.supportEmail` in `frontend/lib/site.ts`.

## Credits
- Monthly reset is implemented (`services/creditResetService.js`). Confirm it behaves as intended: it uses a 30-day cycle from the last reset, not a calendar month.
- Plan allowances are written in several places (`PLAN_LIMITS` in that file, `services/stripeService.js`, `frontend/store/index.ts`). Keep them in sync when plans change.

## Stripe
- Product names and the `app: 'humoro'` metadata are done (`utils/stripeInit.js`).
- Remove old claims from the product descriptions in that file: "Unlimited words", "Up to 50k words", "Up to 10k words", "2 layer humanization", "Bypass AI detectors". Existing Stripe products keep the old text until their descriptions are updated.

## Rename Veritas to Humoro in nodeBackend
- Still to do: `package.json` (name and keyword), `README.md`, `seedBlogs.js` (text, admin name and email).
- Secret text with the old name: `.env.example`, `README.md`, and the fallback secret in `middlewares/authMiddleware.js` and `utils/generateToken.js` (changing a secret signs everyone out).

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

## API paths
- The Python backend now answers every route on both `/api/...` and `/ai/api/...`. The frontend still calls `/api/...` (`frontend/lib/api.ts`).
- Decide when to switch the frontend to `/ai/api/...`, then remove the old paths from `backend/app.py`.
- Update the API docs (`API_FLOW.md`, `CODE_FLOW.md`, `PROJECT_WALKTHROUGH.md`, `IMAGE_API.md`) to list the new paths.
- The tests that call the API with no sign-in (11 failing in `backend/tests`) need a signed-in test user.

## Image Detector page
- Check the licence and author of the two real example photos in `frontend/public/image-detector-examples/` (they come from Open Images) and add a credit line if one is required.
- Keep the source of the 93% image accuracy figure on record.

## Public claims to review
- AI Detector page: "< 0.82%" false positive rate, "Most Reliable" heading, model version names, "Sub-1% False Positive Rate Guarantee".
- Humanizer page: "Bypasses Turnitin AI & GPTZero", "Guaranteed Turnitin & GPTZero clean threshold", "100% Citation Safety".
- Pricing: "Bypass AI detectors (Turnitin…)", "Advanced ML models".
- Home FAQ: "typically reducing AI detection scores by 60-80%".

## Social profiles
- Provide the real social profile links (LinkedIn, X, GitHub or others). The four footer icons in `frontend/components/landing/footer.tsx` still go nowhere (`href="#"`).
- When the links exist, add them as `sameAs` in the Organization data in `frontend/app/page.tsx`.

## Logo (new kit)
- Email template (`utils/emailService.js`): the sign-up code email shows only the word Humoro; add the new logo (needs a hosted image address).
- Stripe: upload the logo and icon in the Stripe branding settings (checkout page and receipts).
- Google sign-in: upload the logo in the Google Cloud OAuth consent screen.
