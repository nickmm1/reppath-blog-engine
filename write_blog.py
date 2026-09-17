"""Write one RepPath blog by calling the Anthropic Messages API.

Reads RULES.md + anchor.html as the system prompt and the episode transcript as input,
and writes blogs/<handle>.html and blogs/<handle>.meta.json.

Env: ANTHROPIC_API_KEY (required), MODEL (default claude-sonnet-5).
"""
import os, json, re, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = os.environ.get("MODEL", "claude-sonnet-5")

def _anthropic(system, user, max_tokens=16000):
    body = json.dumps({
        "model": MODEL, "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body, method="POST")
    req.add_header("x-api-key", API_KEY)
    req.add_header("anthropic-version", "2023-06-01")
    req.add_header("content-type", "application/json")
    with urllib.request.urlopen(req, timeout=300) as x:
        data = json.loads(x.read())
    return "".join(b.get("text", "") for b in data.get("content", []))

def _extract_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n", "", text)
        text = re.sub(r"\n```$", "", text.strip())
    i, j = text.find("{"), text.rfind("}")
    return json.loads(text[i:j + 1])

def write(transcript_path, title, suggested_handle):
    rules = open(os.path.join(HERE, "RULES.md"), encoding="utf-8").read()
    anchor = open(os.path.join(HERE, "anchor.html"), encoding="utf-8").read()
    transcript = open(transcript_path, encoding="utf-8").read()
    system = (
        rules
        + "\n\n===== APPROVED ANCHOR EXEMPLAR (match this structure, HTML, schema, and blocks exactly) =====\n"
        + anchor
    )
    user = (
        f"Episode title: {title}\nSuggested handle: {suggested_handle}\n\n"
        "Write the blog now, in Joe Licata's blunt first-person voice, strictly following the rules "
        "and matching the anchor's structure (lede section, 8-11 h2 sections, FAQ section, closing CTA, "
        "author bio div, Article + FAQPage JSON-LD, rp-blog-related div, reppath-related-guides div).\n\n"
        "Return ONLY one JSON object (no prose, no code fences) with these exact keys:\n"
        '{\"handle\": ..., \"title\": ..., \"meta_title\": (<=60 chars), \"meta_description\": (<=155 chars), '
        '\"summary_html\": \"<p>...</p>\", \"thumbnail_headline\": (<=6 words), \"thumbnail_kicker\": \"\", '
        '\"html\": (the full body HTML string)}.\n'
        "In the schema @id and canonical url use https://reppath.com/blogs/articles/<handle>. "
        "Do NOT use em dashes or en dashes anywhere. Do NOT use the words genuinely, honestly, or straightforward.\n\n"
        "===== TRANSCRIPT =====\n" + transcript
    )
    out = _anthropic(system, user)
    obj = _extract_json(out)
    handle = obj.get("handle") or suggested_handle
    # hard guardrails: strip any stray em/en dashes from the HTML
    html = obj["html"].replace("—", ", ").replace("–", "-")
    os.makedirs(os.path.join(HERE, "blogs"), exist_ok=True)
    open(os.path.join(HERE, "blogs", handle + ".html"), "w", encoding="utf-8").write(html)
    meta = {k: obj.get(k) for k in ("title", "meta_title", "meta_description", "summary_html", "thumbnail_headline", "thumbnail_kicker")}
    meta["handle"] = handle
    meta["thumbnail_kicker"] = meta.get("thumbnail_kicker") or ""
    json.dump(meta, open(os.path.join(HERE, "blogs", handle + ".meta.json"), "w", encoding="utf-8"), indent=2)
    # basic validation
    words = len(re.sub(r"<[^>]+>", " ", html).split())
    schema = html.count("application/ld+json")
    return {"handle": handle, "words": words, "schema_blocks": schema,
            "has_dash": bool(re.search(r"[—–]", html)),
            "banned": bool(re.search(r"(?i)genuinely|honestly|straightforward", html))}

if __name__ == "__main__":
    import sys
    print(write(sys.argv[1], sys.argv[2], sys.argv[3]))
