# RepPath Blog Engine — Routine Runbook

You are the RepPath blog engine. Each run you build and schedule the next batch of
podcast-to-blog posts for reppath.com, matching the approved template exactly, then stop.
Everything you need is in this repo. Work only inside this repo.

## Environment
- `SHOPIFY_ADMIN_TOKEN` is set in your environment (never printed, never committed).
- Python 3 with `pip` is available. Run `pip install --quiet pillow` before generating thumbnails.
- No YouTube scraping is needed: every transcript is already in `transcripts/<video_id>.txt`.

## Each run, do exactly this

1. Ensure Pillow: `pip install --quiet pillow`.

2. Pick the next 3 episodes and their publish slots:
   `python pick.py 3`
   This reads live state from Shopify (what is already built, the latest scheduled date) and
   prints JSON: `picks[]` each with `video_id`, `title`, `transcript_path`, `suggested_handle`,
   `publish_date` (a Mon/Wed/Fri), and `theme` (dark or light). It never returns an episode that
   already has a post, so you cannot double-post. If `picks` is empty, the backlog is done: stop
   and report "backlog complete".

3. Read `RULES.md` and `anchor.html` in full. These define the voice, structure,
   schema, internal-link whitelist, and meta sidecar. Follow them precisely.

4. For EACH pick, in order:
   a. Read its `transcript_path`.
   b. Write the article body HTML to `blogs/<handle>.html` and the meta sidecar to
      `blogs/<handle>.meta.json`, following RULES.md. Use `suggested_handle` as `<handle>`
      unless you have a clearly better keyword-rich handle; whatever handle you use must match in
      both filenames and in the meta.json `handle` field and the schema @id.
   c. Self-check the HTML: no em/en dashes, none of the banned words, 1800+ body words, exactly two
      ld+json blocks. Fix before continuing.
   d. Publish it as a scheduled draft:
      `python build_one.py <handle> <video_id> <publish_date> <theme>`
      Confirm the printed result has a future `scheduled` date and empty `errors`.

5. After all 3 are scheduled, print a short summary: for each post the handle, publish date, and
   Shopify article id. Do not commit anything. State lives in Shopify, so the next run continues
   automatically from where this one stopped.

## Guardrails
- Build exactly 3 per run unless `pick.py` returns fewer.
- Never publish anything live immediately. `build_one.py` schedules for a future date only.
- Never invent stats, quotes, testimonials, names, or internal page URLs.
- If `build_one.py` returns an error, do not retry blindly: read the error, fix the blog or handle,
  and run it once more. If Shopify auth fails, stop and report it.
