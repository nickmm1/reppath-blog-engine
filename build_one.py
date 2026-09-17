"""Generate the thumbnail, create the draft, and schedule one built blog.

The blog HTML + meta.json must already exist in engine/blogs/ (the agent writes them).
Usage: python engine/build_one.py <handle> <video_id> <publish_date YYYY-MM-DD> <theme dark|light>
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_thumb, shopify_ops

def main(handle, video_id, publish_date, theme):
    here = os.path.dirname(os.path.abspath(__file__))
    html = open(os.path.join(here, "blogs", handle + ".html"), encoding="utf-8").read()
    meta = json.load(open(os.path.join(here, "blogs", handle + ".meta.json"), encoding="utf-8"))
    os.makedirs(os.path.join(here, "thumbnails"), exist_ok=True)
    thumb = os.path.join(here, "thumbnails", handle + ".png")
    make_thumb.make(meta.get("thumbnail_headline") or meta["title"], "", thumb, theme)
    aid = shopify_ops.create_draft(meta, html, thumb, video_id)
    res = shopify_ops.schedule(aid, shopify_ops.publish_datetime(publish_date))
    art = res.get("data", {}).get("articleUpdate", {}).get("article")
    errs = res.get("data", {}).get("articleUpdate", {}).get("userErrors")
    print(json.dumps({"handle": handle, "id": aid,
                      "scheduled": art["publishedAt"] if art else None, "errors": errs}))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
