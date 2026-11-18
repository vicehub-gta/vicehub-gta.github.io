#!/usr/bin/env python3
"""Static site generator for Vice Hub (GTA 6 fan hub).

Content: content/categories.json, content/articles/*.json (one article per file).
Output: _site/  (deployed to GitHub Pages by .github/workflows/pages.yml)

Article JSON: {slug, title, category, date (YYYY-MM-DD), minutes, summary,
               body: ["paragraph", "## Heading", "- bullet"], premium?: bool,
               sources?: [{label, url}]}
"""
import datetime as dt
import html
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "_site"
CFG = json.loads((ROOT / "site.json").read_text())
BASE = os.environ.get("BASE_PATH", CFG.get("base", "")).rstrip("/")
ORIGIN = CFG["origin"].rstrip("/")
CATS = json.loads((ROOT / "content" / "categories.json").read_text())
CAT = {c["id"]: c for c in CATS}
E = html.escape


def load_articles():
    arts = []
    for p in (ROOT / "content" / "articles").glob("*.json"):
        a = json.loads(p.read_text())
        assert a["category"] in CAT, f"{p}: unknown category"
        arts.append(a)
    arts.sort(key=lambda a: (a["date"], a.get("order", 0)), reverse=True)
    return arts


def u(path):
    return f"{BASE}{path}"


def fmt(d):
    return dt.date.fromisoformat(d).strftime("%-d %b %Y")


def page(title, desc, path, body, og_type="website"):
    canon = f"{ORIGIN}{path}"
    cover = f"{ORIGIN}/assets/cover.png"
    nav = "".join(
        f'<a href="{u("/" + c + "/")}" class="nav-hide">{CAT[c]["label"]}</a>' for c in ("hacks", "tips", "missions")
    ) + f'<a href="{u("/community/")}" style="color:#ffe58a">Community</a>'
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="{og_type}"><meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{canon}">
<meta property="og:image" content="{cover}"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="{u('/assets/favicon.png')}">
<link rel="apple-touch-icon" href="{u('/assets/apple-touch-icon.png')}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@400;600;800&display=swap">
<link rel="stylesheet" href="{u('/assets/style.css')}">
</head><body>
<div class="glow"></div>
<header class="wrap top">
  <a href="{u('/')}" class="logo">VICE<span>HUB</span><small>GTA 6 community hub</small></a>
  <nav>{nav}<a href="{u('/premium/')}" class="btn-prem">Premium</a></nav>
</header>
<main>{body}</main>
<footer class="wrap foot">
  <p>Vice Hub by Rito GTA · fan-made guides, not affiliated with or endorsed by Rockstar Games or Take-Two Interactive. Grand Theft Auto is a trademark of Take-Two Interactive.</p>
  <p class="soc">{''.join(f'<a href="{s["href"]}" target="_blank" rel="noopener">{s["label"]}</a>' for s in CFG["socials"])}</p>
</footer>
</body></html>"""


def chip(c):
    return f'<span class="chip">{CAT[c]["emoji"]} {CAT[c]["label"]}</span>'


def card(a):
    tag = '<span class="lock">🔒 PREMIUM</span>' if a.get("premium") else f'<span class="muted">{a["minutes"]} min</span>'
    return f"""<a class="card" href="{u('/a/' + a['slug'] + '/')}">
<div class="row">{chip(a['category'])}{tag}</div>
<h3>{E(a['title'])}</h3><p>{E(a['summary'])}</p><span class="date">{fmt(a['date'])}</span></a>"""


def week_strip(today):
    start = today - dt.timedelta(days=today.weekday())
    cells = []
    for i in range(7):
        d = start + dt.timedelta(days=i)
        on = d <= today
        cells.append(f'<div class="day{" on" if on else ""}"><b>{d.strftime("%a").upper()[:2]}</b>{"✓" if on else "·"}</div>')
    return f'<div class="week">{"".join(cells)}<span class="pill">● updated daily</span></div>'


def premium_card(compact=False):
    perks = "" if compact else "<ul><li>Every tested money method, ranked by cash per hour</li><li>Full mission walkthroughs with gold-medal routes</li><li>Map of hidden shops, stashes and secrets</li><li>New premium guide every day</li></ul>"
    return f"""<div class="prem"><div class="prem-top"><span>VICE HUB PREMIUM</span><b>5 €<small> / month</small></b></div>
{perks}<a href="{u('/premium/')}" class="btn-grad">Get Premium</a><p class="tiny">Cancel anytime.</p></div>"""


def render_body(lines):
    out, ul = [], []
    for ln in lines:
        if ln.startswith("- "):
            ul.append(f"<li>{E(ln[2:])}</li>")
            continue
        if ul:
            out.append("<ul>" + "".join(ul) + "</ul>")
            ul = []
        if ln.startswith("## "):
            out.append(f"<h2>{E(ln[3:])}</h2>")
        else:
            out.append(f"<p>{E(ln)}</p>")
    if ul:
        out.append("<ul>" + "".join(ul) + "</ul>")
    return "\n".join(out)


def write(path, content):
    p = OUT / path.lstrip("/")
    if path.endswith("/"):
        p = p / "index.html"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    (OUT / ".nojekyll").write_text("")
    arts = load_articles()
    today = dt.date.fromisoformat(arts[0]["date"]) if arts else dt.date.today()
    today = max(today, dt.date.today())

    tiles = "".join(
        f'<a class="tile" href="{u("/" + c["id"] + "/")}"><div class="em">{c["emoji"]}</div><b>{c["label"]}</b><small>{E(c["blurb"])}</small></a>'
        for c in CATS
    ) + f'<a class="tile" href="{u("/community/")}" style="border-color:rgba(255,216,74,.4)"><div class="em">🗳️</div><b>Community</b><small>Player tips, voted by you</small></a>'
    home = f"""
<section class="wrap hero">
  <div><p class="kicker">GTA 6 · Vice City · Leonida</p>
  <h1>EVERYTHING GTA 6.<br><span class="grad">UPDATED DAILY.</span></h1>
  <p class="lead">Hacks, tips, mission guides and rankings. Checked against real sources, no fake glitches, no spoilers in titles.</p>
  {week_strip(today)}</div>
  {premium_card(compact=True)}
</section>
<section class="wrap"><div class="tiles">{tiles}</div></section>
<section class="wrap" id="latest"><h2 class="sec">LATEST</h2><div class="grid">{''.join(card(a) for a in arts)}</div></section>
<section class="wrap"><div class="band"><div><h2 class="sec">GO PREMIUM FOR THE GOOD STUFF</h2>
<p class="lead">Free guides stay free. Premium gets every tested money method, full mission walkthroughs and the map of hidden spots, the day we find them.</p></div>{premium_card()}</div></section>"""
    write("/", page("Vice Hub · Everything GTA 6, updated daily", CFG["description"], "/", home))

    soon = CFG.get("soon", {})
    for c in CATS:
        lst = [a for a in arts if a["category"] == c["id"]]
        pills = "".join(
            f'<a class="pillnav{" act" if x["id"] == c["id"] else ""}" href="{u("/" + x["id"] + "/")}">{x["emoji"]} {x["label"]}</a>' for x in CATS
        )
        note = f'<div class="note">{E(soon[c["id"]])}</div>' if c["id"] in soon else ""
        grid = f'<div class="grid">{"".join(card(a) for a in lst)}</div>' if lst else '<p class="muted">First guides land here on launch day.</p>'
        body = f"""<section class="wrap"><div class="pills">{pills}</div>
<h1 class="cat">{c['emoji']} GTA 6 {c['label'].upper()}</h1><p class="lead">{E(c['blurb'])}. New posts every day.</p>{note}</section>
<section class="wrap">{grid}</section><section class="wrap narrow">{premium_card()}</section>"""
        write(f"/{c['id']}/", page(f"GTA 6 {c['label']} · Vice Hub", f"{c['blurb']}. Updated daily on Vice Hub.", f"/{c['id']}/", body))

    for a in arts:
        prem = a.get("premium")
        content = render_body(a["body"])
        if prem:
            content = f'<div class="locked">{content}<div class="fade"></div></div>{premium_card()}'
        src = ""
        if a.get("sources"):
            src = '<div class="sources"><b>Sources</b><ul>' + "".join(
                f'<li><a href="{E(s["url"])}" target="_blank" rel="noopener nofollow">{E(s["label"])}</a></li>' for s in a["sources"]
            ) + "</ul></div>"
        more = [x for x in arts if x["slug"] != a["slug"]][:3]
        body = f"""<article class="wrap art">
<a class="back" href="{u('/' + a['category'] + '/')}">← {CAT[a['category']]['label']}</a>
<div class="row">{chip(a['category'])}<span class="muted">{fmt(a['date'])} · {a['minutes']} min read</span></div>
<h1>{E(a['title'])}</h1><p class="lead">{E(a['summary'])}</p>
<div class="prose">{content}</div>{src}</article>
<section class="wrap"><h2 class="sec">MORE GUIDES</h2><div class="grid">{''.join(card(x) for x in more)}</div></section>"""
        write(f"/a/{a['slug']}/", page(f"{a['title']} · Vice Hub", a["summary"], f"/a/{a['slug']}/", body, "article"))

    tips = json.loads((ROOT / "content" / "community.json").read_text())
    post = CFG["tip_url"]
    tip_html = "".join(
        f'<div class="tip"><a class="vote" href="{E(t["url"])}" target="_blank" rel="noopener">▲<span>{t.get("votes", 0)}</span></a><div><small>{E(t.get("category", "Tips"))} · by {E(t.get("author", "anonymous"))}</small><h3>{E(t["title"])}</h3><p>{E(t["body"])}</p></div></div>'
        for t in sorted(tips, key=lambda t: -t.get("votes", 0))
    ) or '<div class="note">No tips on the board yet. Be the first one.</div>'
    com = f"""<section class="wrap"><p class="kicker" style="padding-top:24px;color:#ffe58a">By players, for players</p><h1 class="cat">COMMUNITY TIPS</h1>
<p class="lead">Found a money trick, a hidden shop or a faster mission route? Post it. Upvote the best ones with 👍. The top tips get checked and turned into full guides.</p>
<div class="cgrid"><div>{tip_html}</div><div class="prem"><div class="prem-top"><span>POST A TIP</span></div><p style="color:#e6d6f2">Takes 30 seconds. Pick a category, write your tip, done. Tips with the most 👍 land on this board.</p><a class="btn-grad" style="display:block" href="{E(post)}" target="_blank" rel="noopener">Share your tip</a><p class="tiny">Opens a short form (free GitHub account needed).</p></div></div></section>"""
    write("/community/", page("GTA 6 Community Tips · Vice Hub", "Tips, glitches and secrets found by GTA 6 players. Vote for the best ones.", "/community/", com))

    checkout = CFG.get("checkout_url", "")
    cta = (f'<a class="btn-grad big" href="{E(checkout)}">Subscribe for 5 € / month</a>' if checkout else
           '<div class="note">Premium opens at launch. Follow us so you do not miss it:</div><p class="soc big">' +
           "".join(f'<a href="{s["href"]}" target="_blank" rel="noopener">{s["label"]}</a>' for s in CFG["socials"]) + "</p>")
    prem_body = f"""<section class="wrap narrow"><p class="kicker">Vice Hub Premium</p><h1 class="cat">THE GOOD STUFF. 5 € / MONTH.</h1>
<ul class="perks"><li>💰 Every tested money method, ranked by cash per hour</li><li>🎯 Full mission walkthroughs with gold-medal routes</li>
<li>🗺️ The map of hidden shops, stashes and secrets</li><li>⚡ A new premium guide every day</li><li>🚫 No ads</li></ul>{cta}</section>"""
    write("/premium/", page("Vice Hub Premium · 5 € / month", "Every tested GTA 6 money method, mission walkthroughs and hidden spots.", "/premium/", prem_body))

    write("/404.html", page("Not found · Vice Hub", "Page not found", "/404.html",
                            f'<section class="wrap narrow"><h1 class="cat">WASTED.</h1><p class="lead">This page does not exist.</p><a class="btn-grad" href="{u("/")}">Back to the hub</a></section>'))

    urls = ["/", "/premium/", "/community/"] + [f"/{c['id']}/" for c in CATS] + [f"/a/{a['slug']}/" for a in arts]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"  <url><loc>{ORIGIN}{p}</loc><lastmod>{today.isoformat()}</lastmod></url>" for p in urls]
    sm.append("</urlset>")
    (OUT / "sitemap.xml").write_text("\n".join(sm))
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {ORIGIN}/sitemap.xml\n")
    print(f"built {len(arts)} articles, {len(urls)} pages -> {OUT}")


if __name__ == "__main__":
    build()
