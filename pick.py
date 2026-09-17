"""Pick the next episodes to build, with publish slots and thumbnail themes.

Idempotent: reads current state from Shopify (which video_ids are already built and
the latest scheduled date), so it never picks an episode that already has a post.
Prints JSON the routine agent consumes. Does NOT write anything.

Usage: python engine/pick.py [count]   (default 3)
"""
import json, sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shopify_ops

def slugify(t):
    t = t.lower()
    t = re.sub(r"[’']", "", t)
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t[:70]

def main(count=3):
    here = os.path.dirname(os.path.abspath(__file__))
    q = json.load(open(os.path.join(here, "queue.json"), encoding="utf-8"))
    state = shopify_ops.get_state(n_slots=count)
    done = set(state["done_video_ids"])
    done_handles = set(state["done_handles"])
    picks = []
    for e in q["remaining_prioritized"]:
        if e["video_id"] in done:
            continue
        tp = os.path.join(here, "transcripts", e["video_id"] + ".txt")
        if not os.path.exists(tp):
            continue
        handle = slugify(e["title"])
        if handle in done_handles:
            continue
        picks.append(e)
        if len(picks) >= count:
            break
    # theme alternates across the whole run so it stays balanced
    base = len(done_handles)
    out = []
    for i, e in enumerate(picks):
        out.append({
            "video_id": e["video_id"],
            "title": e["title"],
            "transcript_path": os.path.join(here, "transcripts", e["video_id"] + ".txt").replace("\\", "/"),
            "suggested_handle": slugify(e["title"]),
            "publish_date": state["next_slots"][i],
            "theme": "dark" if (base + i) % 2 == 0 else "light",
        })
    print(json.dumps({"picks": out, "done_count": len(done_handles)}, indent=2))

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
