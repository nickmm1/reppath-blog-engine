# RepPath Blog Engine

Turns Joe Licata's RepPath podcast episodes into E-E-A-T blog posts for reppath.com and
schedules them to publish Monday / Wednesday / Friday. Runs as a scheduled Claude Code cloud
routine. See `AGENT.md` for the runbook the agent follows each run.

## How it works
- `queue.json` holds every podcast episode, prioritized best-topics-first.
- `transcripts/<video_id>.txt` holds the transcript for every episode (pre-loaded, so no scraping).
- `anchor.html` is the approved gold-standard blog. `RULES.md` is the writing spec.
- `pick.py` reads live state from Shopify and returns the next episodes + MWF publish slots. It is
  idempotent: it skips any episode already built, so runs never double-post.
- The agent writes each blog into `blogs/`, then `build_one.py` makes the text-only thumbnail,
  creates the unpublished draft, and schedules it via Shopify GraphQL (`isPublished:false` +
  future `publishDate`).

## State
State lives in Shopify, not in this repo. Each article carries a `reppath.source_video_id`
metafield; `pick.py` uses it to know what is done and what the next open MWF slot is. Nothing is
committed back, so the routine needs no write access to this repo.

## Secrets
No secrets in this repo. The Shopify Admin token is provided at runtime via the
`SHOPIFY_ADMIN_TOKEN` environment variable set in the routine config.

## Scope
This engine covers the episodes captured in `queue.json`. When Joe records new episodes beyond
that set, refresh `queue.json` and add the new `transcripts/*.txt`, then the routine picks them up
automatically.
