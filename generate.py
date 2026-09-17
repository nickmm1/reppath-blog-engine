"""One-shot: build and schedule the next N RepPath posts (default 1). Fully API-driven.

Runs in GitHub Actions on a Mon/Wed/Fri cron. Idempotent: reads state from Shopify,
so it never double-posts. Env: ANTHROPIC_API_KEY, SHOPIFY_ADMIN_TOKEN, MODEL (optional).
"""
import os, sys, json, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import shopify_ops, make_thumb, write_blog

def slugify(t):
    t = re.sub(r"[’']", "", t.lower())
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:70]

def main(count=1):
    q = json.load(open(os.path.join(HERE, "queue.json"), encoding="utf-8"))
    state = shopify_ops.get_state(n_slots=count)
    done, done_handles = set(state["done_video_ids"]), set(state["done_handles"])
    base = len(done_handles)
    built = 0
    for e in q["remaining_prioritized"]:
        if built >= count:
            break
        if e["video_id"] in done:
            continue
        tp = os.path.join(HERE, "transcripts", e["video_id"] + ".txt")
        if not os.path.exists(tp):
            continue
        sh = slugify(e["title"])
        if sh in done_handles:
            continue
        publish_date = state["next_slots"][built]
        theme = "dark" if (base + built) % 2 == 0 else "light"
        print(f"[build] {e['video_id']} -> {sh} | {publish_date} | {theme}")
        chk = write_blog.write(tp, e["title"], sh)
        print("  written:", chk)
        if chk["has_dash"] or chk["banned"] or chk["words"] < 1500 or chk["schema_blocks"] != 2:
            print("  WARN validation flags; scheduling anyway (dashes already stripped).")
        handle = chk["handle"]
        meta = json.load(open(os.path.join(HERE, "blogs", handle + ".meta.json"), encoding="utf-8"))
        html = open(os.path.join(HERE, "blogs", handle + ".html"), encoding="utf-8").read()
        os.makedirs(os.path.join(HERE, "thumbnails"), exist_ok=True)
        thumb = os.path.join(HERE, "thumbnails", handle + ".png")
        make_thumb.make(meta.get("thumbnail_headline") or meta["title"], "", thumb, theme)
        aid = shopify_ops.create_draft(meta, html, thumb, e["video_id"])
        res = shopify_ops.schedule(aid, shopify_ops.publish_datetime(publish_date))
        art = res.get("data", {}).get("articleUpdate", {}).get("article")
        errs = res.get("data", {}).get("articleUpdate", {}).get("userErrors")
        print(f"  scheduled id={aid} at {art['publishedAt'] if art else None} errors={errs}")
        built += 1
    if built == 0:
        print("No episodes to build (backlog complete or all next items already built).")

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
