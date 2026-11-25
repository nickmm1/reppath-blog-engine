"""Forever-cron entrypoint: discover NEW RepPath episodes and publish them.

Runs in GitHub Actions. Uses yt-dlp to read the channel (no API key), finds uploads
that are not already in the inventory or the store, fetches each transcript, writes the
blog via the Claude API (write_blog), and schedules it. Idempotent via Shopify state.

Env: ANTHROPIC_API_KEY, SHOPIFY_ADMIN_TOKEN, MODEL (optional), CHANNEL (optional),
MAX_PER_RUN (optional, default 1).
"""
import os, sys, json, re, subprocess, tempfile, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import shopify_ops, make_thumb, write_blog

import urllib.request, html as _html
CHANNEL_ID = os.environ.get("CHANNEL_ID", "UCONIT7SJmFjwgiA86YEQm5w")  # @JoeLicata28
MAX_PER_RUN = int(os.environ.get("MAX_PER_RUN", "1"))
MIN_WORDS = 1200  # transcripts shorter than this are short clips, skip

def slugify(t):
    t = re.sub(r"[’']", "", t.lower())
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:70]

def channel_videos():
    """Newest-first (video_id, title) from the channel's YouTube RSS feed (no auth, stable).

    The feed returns the 15 most recent uploads, which is enough to catch new episodes on
    a 3x-per-week cadence. The yt-dlp channel-tab endpoint is unreliable, so we avoid it.
    """
    rss = "https://www.youtube.com/feeds/videos.xml?channel_id=" + CHANNEL_ID
    req = urllib.request.Request(rss, headers={"User-Agent": "Mozilla/5.0"})
    xml = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "ignore")
    entries = re.findall(r"<entry>(.*?)</entry>", xml, re.DOTALL)
    out = []
    for e in entries:
        vid = re.search(r"<yt:videoId>([^<]+)</yt:videoId>", e)
        title = re.search(r"<media:title>([^<]+)</media:title>", e) or re.search(r"<title>([^<]+)</title>", e)
        if vid and title:
            out.append((vid.group(1).strip(), _html.unescape(title.group(1).strip())))
    return out

def fetch_transcript(video_id):
    """Return plain-text transcript via yt-dlp auto-subs, or '' if none."""
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(
            ["yt-dlp", "--skip-download", "--write-auto-subs", "--sub-langs", "en",
             "--sub-format", "vtt", "--no-warnings", "-o", os.path.join(d, "%(id)s.%(ext)s"),
             "https://www.youtube.com/watch?v=" + video_id],
            capture_output=True, text=True, timeout=300)
        vtts = glob.glob(os.path.join(d, "*.vtt"))
        if not vtts:
            return ""
        raw = open(vtts[0], encoding="utf-8", errors="ignore").read()
    lines, seen, prev = [], set(), None
    for ln in raw.splitlines():
        if "-->" in ln or ln.strip() in ("WEBVTT", "") or ln.strip().isdigit():
            continue
        txt = re.sub(r"<[^>]+>", "", ln).strip()
        if txt and txt != prev:
            lines.append(txt); prev = txt
    return " ".join(lines)

def main():
    q = json.load(open(os.path.join(HERE, "queue.json"), encoding="utf-8"))
    known = {e["video_id"] for e in q.get("all_episodes", [])}
    skip_path = os.path.join(HERE, "skip.json")
    skip = set(json.load(open(skip_path, encoding="utf-8"))) if os.path.exists(skip_path) else set()
    state = shopify_ops.get_state(n_slots=MAX_PER_RUN + 3)
    done = set(state["done_video_ids"])
    done_handles = set(state["done_handles"])

    videos = channel_videos()
    # genuinely new uploads = not in our inventory, not already built, not skipped
    new = [(vid, title) for (vid, title) in videos if vid not in known and vid not in done and vid not in skip]
    new.reverse()  # oldest of the new first, to publish in chronological order

    built = 0
    slot_i = 0
    for vid, title in new:
        if built >= MAX_PER_RUN:
            break
        handle = slugify(title)
        if handle in done_handles:
            continue
        text = fetch_transcript(vid)
        if len(text.split()) < MIN_WORDS:
            print(f"[skip short/no-transcript] {vid} {title!r} ({len(text.split())} words)")
            continue
        tp = os.path.join(HERE, "transcripts", vid + ".txt")
        open(tp, "w", encoding="utf-8").write(title + "\n\n" + text)
        print(f"[build] {vid} -> {handle}")
        chk = write_blog.write(tp, title, handle)
        handle = chk["handle"]
        meta = json.load(open(os.path.join(HERE, "blogs", handle + ".meta.json"), encoding="utf-8"))
        html = open(os.path.join(HERE, "blogs", handle + ".html"), encoding="utf-8").read()
        theme = "dark" if (len(done_handles) + built) % 2 == 0 else "light"
        os.makedirs(os.path.join(HERE, "thumbnails"), exist_ok=True)
        thumb = os.path.join(HERE, "thumbnails", handle + ".png")
        make_thumb.make(meta.get("thumbnail_headline") or meta["title"], "", thumb, theme)
        aid = shopify_ops.create_draft(meta, html, thumb, vid)
        date = state["next_slots"][slot_i]; slot_i += 1
        res = shopify_ops.schedule(aid, shopify_ops.publish_datetime(date))
        art = res.get("data", {}).get("articleUpdate", {}).get("article")
        print(f"  scheduled id={aid} for {art['publishedAt'] if art else '?'} ({theme})")
        built += 1

    if built == 0:
        print("No new episodes to publish. Backlog and uploads are all handled.")

if __name__ == "__main__":
    main()
