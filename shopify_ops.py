"""RepPath Shopify operations for the blog engine (cloud + local).

Token is read from the SHOPIFY_ADMIN_TOKEN environment variable so it is never
committed to the repo. All scheduling uses GraphQL articleUpdate with
isPublished:false + publishDate (REST cannot future-date articles).

Each article stores a metafield reppath.source_video_id so the engine can derive
"what is already built" directly from Shopify and stay idempotent (never double-post).
"""
import os, json, base64, urllib.request, urllib.error, datetime

TOKEN = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
STORE = os.environ.get("SHOPIFY_STORE", "reppath.myshopify.com")
BLOG_ID = int(os.environ.get("REPPATH_BLOG_ID", "118459400474"))
API = "2024-10"
PUBLISH_HOUR_ET = "08:30:00-04:00"  # 8:30am ET

def _req(method, path, payload=None):
    r = urllib.request.Request(f"https://{STORE}/admin/api/{API}/{path}",
        data=(json.dumps(payload).encode() if payload is not None else None), method=method)
    r.add_header("X-Shopify-Access-Token", TOKEN)
    r.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(r) as x:
            return x.status, json.loads(x.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

def gql(query, variables=None):
    return _req("POST", "graphql.json", {"query": query, "variables": variables or {}})[1]

ARTICLE_UPDATE = """
mutation SetSchedule($id: ID!, $article: ArticleUpdateInput!) {
  articleUpdate(id: $id, article: $article) {
    article { id handle isPublished publishedAt }
    userErrors { field message }
  }
}
"""

def schedule(article_id, publish_date_iso):
    """Schedule an article to publish in the future (isPublished:false + publishDate)."""
    return gql(ARTICLE_UPDATE, {
        "id": f"gid://shopify/Article/{article_id}",
        "article": {"isPublished": False, "publishDate": publish_date_iso},
    })

def create_draft(meta, html, thumb_path, video_id):
    """Create an unpublished article with thumbnail, SEO metafields, and source_video_id."""
    b64 = base64.b64encode(open(thumb_path, "rb").read()).decode()
    article = {"article": {
        "title": meta["title"], "author": "Joe Licata", "handle": meta["handle"],
        "body_html": html, "summary_html": meta["summary_html"], "published": False,
        "image": {"attachment": b64, "alt": meta["title"]},
        "metafields": [
            {"namespace": "global", "key": "title_tag", "value": meta["meta_title"], "type": "single_line_text_field"},
            {"namespace": "global", "key": "description_tag", "value": meta["meta_description"], "type": "single_line_text_field"},
            {"namespace": "reppath", "key": "source_video_id", "value": video_id, "type": "single_line_text_field"},
        ],
    }}
    st, resp = _req("POST", f"blogs/{BLOG_ID}/articles.json", article)
    if st not in (200, 201):
        raise RuntimeError(f"create failed {st}: {resp}")
    return resp["article"]["id"]

def _all_articles():
    """Return list of {id, handle, publishedAt, source_video_id} for every article via GraphQL."""
    out, cursor = [], None
    q = """
    query($cursor: String) {
      articles(first: 100, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes { id handle publishedAt metafield(namespace:"reppath", key:"source_video_id"){ value } }
      }
    }"""
    while True:
        d = gql(q, {"cursor": cursor}).get("data", {}).get("articles", {})
        for n in d.get("nodes", []):
            out.append({
                "id": n["id"], "handle": n["handle"], "publishedAt": n.get("publishedAt"),
                "video_id": (n.get("metafield") or {}).get("value") if n.get("metafield") else None,
            })
        if d.get("pageInfo", {}).get("hasNextPage"):
            cursor = d["pageInfo"]["endCursor"]
        else:
            break
    return out

def _next_mwf(after_date):
    d = after_date + datetime.timedelta(days=1)
    while d.weekday() not in (0, 2, 4):
        d += datetime.timedelta(days=1)
    return d

def get_state(n_slots=6):
    """Return {done_video_ids, done_handles, next_slots}. Idempotent state from Shopify."""
    arts = _all_articles()
    done_vids = {a["video_id"] for a in arts if a["video_id"]}
    done_handles = {a["handle"] for a in arts}
    # latest scheduled/published date across all articles
    dates = []
    for a in arts:
        if a["publishedAt"]:
            try:
                dates.append(datetime.datetime.fromisoformat(a["publishedAt"].replace("Z", "+00:00")).date())
            except Exception:
                pass
    anchor = max(dates) if dates else datetime.date.today()
    if anchor < datetime.date.today():
        anchor = datetime.date.today()
    slots, d = [], anchor
    for _ in range(n_slots):
        d = _next_mwf(d)
        slots.append(d.isoformat())
    return {"done_video_ids": sorted(done_vids), "done_handles": sorted(done_handles), "next_slots": slots}

def publish_datetime(date_iso):
    return f"{date_iso}T{PUBLISH_HOUR_ET}"

if __name__ == "__main__":
    print(json.dumps(get_state(), indent=2))
