"""
SOLA Medical Supply — Auto Blog Generator
Reads next pending keyword → calls Claude API → writes static HTML → updates blog index.
Run by GitHub Actions. Requires: ANTHROPIC_API_KEY env var.
"""
 
import anthropic
import json
import os
import re
from datetime import datetime
from pathlib import Path
 
# ── Paths ────────────────────────────────────────────────────────────────────
ROOT          = Path(__file__).parent.parent
KEYWORDS_FILE = ROOT / "data" / "keywords.json"
BLOG_DIR      = ROOT / "blog"
BLOG_INDEX    = BLOG_DIR / "index.html"
 
# ── Helpers ───────────────────────────────────────────────────────────────────
def load_data():
    with open(KEYWORDS_FILE, encoding="utf-8") as f:
        return json.load(f)
 
def save_data(data):
    with open(KEYWORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
 
def get_next_keyword(data):
    for i, item in enumerate(data["keywords"]):
        if item["status"] == "pending":
            return i, item
    return None, None
 
def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    return text[:80]
 
# ── Claude call ───────────────────────────────────────────────────────────────
def generate_post(kw_item: dict) -> dict:
    client = anthropic.Anthropic()
 
    lsi = ", ".join(kw_item.get("lsi", []))
    prompt = f"""You are an expert B2B content writer for SOLA Medical Supply (solamedicalsupply.com).
SOLA is a wholesale supplier of aesthetic and medical beauty products: dermal fillers, botox/toxin, skin boosters, meso, IV whitening, body contouring — targeting clinics, spas, and distributors in Malaysia, Philippines, and global markets.
 
Write a complete SEO-optimised English blog article.
 
CONTENT BRIEF:
- Target Keyword: {kw_item['keyword']}
- Suggested Title: {kw_item.get('title', 'Auto-generate a compelling H1 title')}
- Target Audience: {kw_item.get('audience', 'clinic owners, aesthetic doctors, distributors in Malaysia')}
- Category: {kw_item.get('category', 'Aesthetic Medicine')}
- LSI Keywords: {lsi if lsi else 'auto-select relevant ones'}
 
ARTICLE STRUCTURE (use exactly these sections):
1. H1: Include primary keyword near the start
2. Introduction (150-200 words): Open with a B2B pain point. Use keyword in first 2 sentences.
3. H2: What Is [Product/Topic] — Malaysian B2B clinic context
4. H2: Key Factors When Choosing a Supplier in Malaysia — cover MOH/KKM/NPRA compliance, cold chain (GDP), certification (CE, FDA, HALAL if applicable), MOQ, lead time
5. H2: How to Evaluate Product Quality — batch certs, expiry, packaging, sample policy
6. H2: Wholesale Pricing Overview in Malaysia — general range context, no competitor names
7. H2: Why Source From SOLA Medical Supply — trust-building, mention WhatsApp quotation system (+84 98 177 86 70)
8. Conclusion (100-150 words): recap + CTA mentioning WhatsApp and email (sales@solamedicalsupply.com)
 
SEO RULES:
- Primary keyword in H1, first 100 words, at least 1 H2, meta description, conclusion
- Keyword density 1-2% (do not stuff)
- Use LSI keywords naturally throughout
- Malaysia-specific context in each major section (MOH, NPRA, KKM references)
- E-E-A-T signals: cite regulations, safety standards, clinical context
- Total: 1,200-1,600 words
 
OUTPUT — return ONLY a valid JSON object (no markdown fences, no commentary):
{{
  "title": "Full H1 title as string",
  "meta_description": "Meta description max 155 chars, includes keyword",
  "slug": "url-slug-lowercase-hyphens-no-special-chars",
  "html_body": "Article HTML using ONLY these tags: <h2> <h3> <p> <ul> <li> <strong> <em>. No wrapper elements.",
  "excerpt": "60-word plain-text excerpt for blog listing",
  "read_time": "X min read"
}}"""
 
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
 
    raw = message.content[0].text.strip()
    # Strip markdown code fences if Claude wraps in them
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)
 
    return json.loads(raw)
 
# ── HTML builders ─────────────────────────────────────────────────────────────
YEAR = datetime.now().year
 
NAV = """  <div class="topbar">
    <div class="wrap"><span>B2B aesthetic &amp; medical beauty supply</span><b>WhatsApp: +84 98 177 86 70</b></div>
  </div>
  <nav class="nav">
    <div class="wrap nav-inner">
      <a class="brand" href="/index.html"><span class="logo"><img src="/assets/icons/logoNgang.png" alt="SOLA Medical Supply"></span></a>
      <div class="links">
        <a class="" href="/index.html">Home</a>
        <a class="" href="/products.html">Products</a>
        <a class="" href="/brands.html">Brands</a>
        <a class="" href="/catalogue.html">Catalogue</a>
        <a class="" href="/shipping.html">Shipping</a>
        <a class="" href="/about.html">About</a>
        <a class="" href="/faq.html">FAQ</a>
        <a class="active" href="/blog/index.html">Blog</a>
        <a class="" href="/contact.html">Contact</a>
      </div>
      <a class="btn primary" href="https://wa.me/84981778670" target="_blank">Get quote</a>
    </div>
  </nav>"""
 
FOOTER = f"""  <footer class="footer">
    <div class="wrap footer-inner">
      <a class="brand" href="/index.html"><span class="logo"><img src="/assets/icons/logoNgang.png" alt="SOLA Medical Supply"></span></a>
      <div class="footer-cols">
        <div class="footer-col">
          <h4>Products</h4>
          <a href="/products.html">Catalogue</a>
          <a href="/brands.html">Brands</a>
          <a href="/catalogue.html">PDF Catalogue</a>
        </div>
        <div class="footer-col">
          <h4>Company</h4>
          <a href="/about.html">About</a>
          <a href="/shipping.html">Shipping</a>
          <a href="/faq.html">FAQ</a>
        </div>
        <div class="footer-col">
          <h4>Contact</h4>
          <p>WhatsApp: +84 98 177 86 70</p>
          <p>Email: sales@solamedicalsupply.com</p>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <div class="wrap">© {YEAR} SOLA Medical Supply</div>
    </div>
  </footer>"""
 
POST_STYLE = """
    <style>
      .blog-post { max-width: 760px; margin: 0 auto; padding: 2rem 1.5rem 5rem; }
      .back-link { display: inline-block; margin-bottom: 1.5rem; color: #2563eb; text-decoration: none; font-size: 0.9rem; }
      .back-link:hover { text-decoration: underline; }
      .blog-post h1 { font-size: 2rem; line-height: 1.3; margin-bottom: 0.5rem; color: #1a1a2e; }
      .post-meta { color: #888; font-size: 0.9rem; margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid #eee; }
      .blog-post h2 { font-size: 1.4rem; margin-top: 2.5rem; margin-bottom: 0.8rem; color: #1a1a2e; }
      .blog-post h3 { font-size: 1.1rem; margin-top: 1.5rem; color: #333; }
      .blog-post p  { line-height: 1.85; margin-bottom: 1.2rem; color: #444; }
      .blog-post ul { padding-left: 1.5rem; margin-bottom: 1.2rem; }
      .blog-post li { line-height: 1.8; margin-bottom: 0.4rem; color: #444; }
      .cta-box { background: #eff6ff; border-left: 4px solid #2563eb; padding: 1.4rem 1.6rem; margin: 2.5rem 0; border-radius: 0 6px 6px 0; }
      .cta-box p { margin: 0; color: #1e3a5f; line-height: 1.7; }
      .cta-box a { color: #2563eb; }
    </style>"""
 
INDEX_STYLE = """
    <style>
      .blog-header { text-align: center; padding: 3rem 1rem 2rem; }
      .blog-header h1 { font-size: 2.2rem; color: #1a1a2e; margin-bottom: 0.5rem; }
      .blog-header p { color: #666; max-width: 600px; margin: 0 auto; }
      .posts-grid { max-width: 960px; margin: 0 auto; padding: 0 1.5rem 5rem;
        display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 1.5rem; }
      .post-card { border: 1px solid #e8e8e8; border-radius: 10px; background: #fff;
        display: flex; flex-direction: column; }
      .post-card-body { padding: 1.5rem; display: flex; flex-direction: column; flex: 1; }
      .post-category { display: inline-block; background: #eff6ff; color: #2563eb;
        font-size: 0.72rem; padding: 2px 9px; border-radius: 4px; font-weight: 700;
        text-transform: uppercase; letter-spacing: .04em; }
      .post-card h2 { font-size: 1.15rem; margin: 0.75rem 0 0.5rem; line-height: 1.45; }
      .post-card h2 a { color: #1a1a2e; text-decoration: none; }
      .post-card h2 a:hover { color: #2563eb; }
      .post-excerpt { color: #555; font-size: 0.9rem; line-height: 1.65; flex: 1; margin-bottom: 1rem; }
      .post-meta-line { color: #aaa; font-size: 0.8rem; margin-bottom: 0.75rem; }
      .read-more { color: #2563eb; font-size: 0.9rem; text-decoration: none; font-weight: 600; }
      .read-more:hover { text-decoration: underline; }
      .no-posts { text-align: center; color: #999; padding: 4rem 0; }
    </style>"""
 
 
def build_post_page(post_data: dict, date_str: str, slug: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{post_data['title']} | SOLA Medical Supply</title>
  <meta name="description" content="{post_data['meta_description']}">
  <meta property="og:title" content="{post_data['title']} | SOLA Medical Supply">
  <meta property="og:description" content="{post_data['meta_description']}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="https://www.solamedicalsupply.com/blog/{slug}.html">
  <link rel="canonical" href="https://www.solamedicalsupply.com/blog/{slug}.html">
  <link rel="icon" href="/assets/icons/favicon.ico" type="image/x-icon">
  <link rel="stylesheet" href="../assets/css/style.css">
  {POST_STYLE}
</head>
<body>
{NAV}
  <main>
    <div class="blog-post">
      <a class="back-link" href="/blog/index.html">← Back to Blog</a>
      <h1>{post_data['title']}</h1>
      <div class="post-meta">{date_str} &nbsp;·&nbsp; {post_data['read_time']}</div>
      {post_data['html_body']}
      <div class="cta-box">
        <p>
          <strong>Looking for a trusted wholesale supplier in Malaysia?</strong><br>
          Send your product list to SOLA Medical Supply for competitive wholesale pricing and availability.<br>
          WhatsApp: <a href="https://wa.me/84981778670">+84 98 177 86 70</a>
          &nbsp;·&nbsp;
          Email: <a href="mailto:sales@solamedicalsupply.com">sales@solamedicalsupply.com</a>
        </p>
      </div>
    </div>
  </main>
{FOOTER}
</body>
</html>"""
 
 
def build_index_page(posts: list) -> str:
    if not posts:
        cards_html = '<p class="no-posts">No posts yet. Check back soon.</p>'
    else:
        cards = []
        for p in sorted(posts, key=lambda x: x["date"], reverse=True):
            cards.append(f"""    <article class="post-card">
      <div class="post-card-body">
        <span class="post-category">{p.get('category', 'Aesthetic Medicine')}</span>
        <h2><a href="/blog/{p['slug']}.html">{p['title']}</a></h2>
        <p class="post-excerpt">{p['excerpt']}</p>
        <div class="post-meta-line">{p['date']} &nbsp;·&nbsp; {p.get('read_time', '5 min read')}</div>
        <a class="read-more" href="/blog/{p['slug']}.html">Read article →</a>
      </div>
    </article>""")
        cards_html = "\n".join(cards)
 
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Blog | SOLA Medical Supply</title>
  <meta name="description" content="Wholesale aesthetic medicine insights for B2B buyers in Malaysia and Southeast Asia — dermal fillers, botox, meso, IV whitening guides.">
  <link rel="canonical" href="https://www.solamedicalsupply.com/blog/">
  <link rel="icon" href="/assets/icons/favicon.ico" type="image/x-icon">
  <link rel="stylesheet" href="../assets/css/style.css">
  {INDEX_STYLE}
</head>
<body>
{NAV}
  <main>
    <div class="blog-header">
      <h1>Aesthetic Medicine Insights</h1>
      <p>Wholesale guides for clinics, distributors, and aesthetic practitioners in Malaysia and Southeast Asia.</p>
    </div>
    <div class="posts-grid">
{cards_html}
    </div>
  </main>
{FOOTER}
</body>
</html>"""
 
 
# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    BLOG_DIR.mkdir(exist_ok=True)
 
    data = load_data()
    if "posts" not in data:
        data["posts"] = []
 
    idx, kw_item = get_next_keyword(data)
    if kw_item is None:
        print("✓ No pending keywords. Nothing to generate.")
        return
 
    print(f"→ Generating post for: {kw_item['keyword']}")
 
    post_data = generate_post(kw_item)
 
    date_str = datetime.now().strftime("%B %d, %Y")
    slug = post_data.get("slug") or slugify(kw_item["keyword"])
 
    # Write individual post page
    post_path = BLOG_DIR / f"{slug}.html"
    with open(post_path, "w", encoding="utf-8") as f:
        f.write(build_post_page(post_data, date_str, slug))
    print(f"✓ Post written: {post_path}")
 
    # Update keyword status
    data["keywords"][idx]["status"]    = "done"
    data["keywords"][idx]["slug"]      = slug
    data["keywords"][idx]["published"] = date_str
 
    # Append to posts list
    data["posts"].append({
        "title":     post_data["title"],
        "slug":      slug,
        "date":      date_str,
        "excerpt":   post_data["excerpt"],
        "read_time": post_data["read_time"],
        "category":  kw_item.get("category", "Aesthetic Medicine"),
    })
 
    save_data(data)
 
    # Regenerate blog index
    with open(BLOG_INDEX, "w", encoding="utf-8") as f:
        f.write(build_index_page(data["posts"]))
    print("✓ Blog index updated.")
 
 
if __name__ == "__main__":
    main()