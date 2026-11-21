#!/usr/bin/env python3
"""Static site generator for Vice Hub (GTA 6 fan hub), English + German.

Content: content/categories.json, content/articles/*.json (one article per file).
Output: _site/  (deployed to GitHub Pages by .github/workflows/pages.yml)
English lives at /, German at /de/.

Article JSON: {slug, title, category, date (YYYY-MM-DD), summary,
               body: ["paragraph", "## Heading", "- bullet"], premium?: bool,
               sources?: [{label, url}],
               de?: {title, summary, body}}   <- German version (falls back to English)
Reading time is computed from the body.
"""
import datetime as dt
import html
import json
import os
import shutil
from pathlib import Path

import extras
from extras import X

ROOT = Path(__file__).parent
OUT = ROOT / "_site"
CFG = json.loads((ROOT / "site.json").read_text())
BASE = os.environ.get("BASE_PATH", CFG.get("base", "")).rstrip("/")
ORIGIN = CFG["origin"].rstrip("/")
CATS = json.loads((ROOT / "content" / "categories.json").read_text())
CAT = {c["id"]: c for c in CATS}
LANGS = ("en", "de")
LAUNCH = "2026-11-19"  # midnight local time, rolling launch
E = html.escape

T = {
    "en": dict(
        tagline="GTA 6 community hub", community="Community", premium="Premium",
        footer="Vice Hub by Rito GTA · fan-made guides, not affiliated with or endorsed by Rockstar Games or Take-Two Interactive. Grand Theft Auto is a trademark of Take-Two Interactive.",
        min="min", min_read="min read", locked="🔒 PREMIUM", updated="● updated daily",
        days=["MO", "TU", "WE", "TH", "FR", "SA", "SU"],
        prem_label="VICE HUB PREMIUM", per_month=" / month", get_prem="See what's in Premium", cancel="Cancel anytime.",
        perks=["Day-1 money guide: every confirmed method, ranked by payout", "Mission routes, added as we test them",
               "Hidden shops, stashes and secrets, added as we find them", "At most one new premium guide per day"],
        kicker="GTA 6 · Vice City · Leonida", h1a="EVERYTHING GTA 6.", h1b="UPDATED DAILY.",
        lead_home="Hacks, tips, mission guides and rankings. Every fact linked to its source, no fake glitches, no spoilers in titles.",
        cd_label="GTA 6 unlocks in", cd_out="GTA 6 IS OUT NOW", cd_static="19 Nov 2026 · 00:00 your local time",
        cd_units=["d", "h", "m", "s"],
        community_tile="Player tips, voted by you", latest="LATEST", band_h="GO PREMIUM FOR THE GOOD STUFF",
        band_p="News and basic guides stay free forever. Premium is for the deep stuff: tested money methods, mission routes and hidden spots, added as we test them.",
        home_title="Vice Hub · Everything GTA 6, updated daily",
        cat_suffix=". New posts every day.", cat_empty="First guides land here on launch day.",
        cat_desc="Updated daily on Vice Hub.", more="MORE GUIDES", sources="Sources",
        com_kicker="By players, for players", com_h="COMMUNITY TIPS",
        com_lead="Found a money trick, a hidden shop or a faster mission route? Post it. Upvote the best ones with 👍. The top tips get checked and turned into full guides.",
        com_empty="The board opens with the game. Post the first tip and it shows up here.",
        post_tip_h="POST A TIP", post_tip_p="Takes 30 seconds. Pick a category, write your tip, done. Tips with the most 👍 land on this board.",
        share_tip="Share your tip", form_note="Opens a short form (free GitHub account needed).", by="by", anon="anonymous",
        com_title="GTA 6 Community Tips · Vice Hub", com_desc="Tips, glitches and secrets found by GTA 6 players. Vote for the best ones.",
        prem_sub="Subscribe for 5 € / month", prem_vat="In Germany you pay about 5 € in total, VAT included (4.20 € plus 19 % VAT). Gumroad bills in US dollars and tax differs by country, so the amount can vary by a few cents.", prem_h="THE GOOD STUFF. 5 € / MONTH.",
        prem_intro="Vice Hub stays free for news, launch info and basic tips. Premium unlocks the guides that take us hours of testing.",
        prem_perks=["💰 Inside now: the Day-1 money guide, every confirmed method ranked by payout", "🎯 Mission routes, added as we test them",
                    "🗺️ Hidden shops, stashes and secrets, added as we find them", "⚡ At most one new premium guide per day, never news"],
        prem_status="Premium is not open yet. We take no payments and ask for no card details until it launches. Follow us to hear first:",
        prem_faq=[("What stays free?", "All news, launch facts, release times and basic tips. Only deep guides are Premium."),
                  ("Can I cancel?", "Yes, anytime. No minimum term."),
                  ("When does it open?", "Once the first real guides are tested after launch. We announce it on TikTok, YouTube and Instagram.")],
        prem_faq_live=[("What do I get today?", "The Day-1 money guide with every confirmed legit money method. New deep guides are added as we test them, at most one per day."),
                       ("How do I pay and read?", "Checkout and the member area run on Gumroad, which is the seller. You get the guides there right after payment.")],
        prem_title="Vice Hub Premium · 5 € / month", prem_desc="Deep GTA 6 guides: tested money methods, mission routes and hidden spots, added as we test them.",
        nf_title="Not found · Vice Hub", nf_p="This page does not exist.", nf_btn="Back to the hub",
        switch="DE", switch_name="Deutsch",
    ),
    "de": dict(
        tagline="GTA-6-Community-Hub", community="Community", premium="Premium",
        footer="Vice Hub by Rito GTA · Fan-Guides, nicht verbunden mit oder unterstützt von Rockstar Games oder Take-Two Interactive. Grand Theft Auto ist eine Marke von Take-Two Interactive.",
        min="Min.", min_read="Min. Lesezeit", locked="🔒 PREMIUM", updated="● täglich neu",
        days=["MO", "DI", "MI", "DO", "FR", "SA", "SO"],
        prem_label="VICE HUB PREMIUM", per_month=" / Monat", get_prem="Das steckt in Premium", cancel="Jederzeit kündbar.",
        perks=["Tag-1-Geld-Guide: jede bestätigte Methode, sortiert nach Auszahlung", "Missions-Routen, sobald sie getestet sind",
               "Versteckte Shops, Verstecke und Geheimnisse, sobald wir sie finden", "Höchstens ein neuer Premium-Guide pro Tag"],
        kicker="GTA 6 · Vice City · Leonida", h1a="ALLES ZU GTA 6.", h1b="JEDEN TAG NEU.",
        lead_home="Hacks, Tipps, Missionsguides und Rankings. Jeder Fakt mit Quelle, keine Fake-Glitches, keine Spoiler in Titeln.",
        cd_label="GTA 6 startet in", cd_out="GTA 6 IST DRAUSSEN", cd_static="19. Nov. 2026 · 00:00 Uhr deine Ortszeit",
        cd_units=["T", "h", "m", "s"],
        community_tile="Spieler-Tipps, von euch gevotet", latest="NEU", band_h="PREMIUM FÜR DIE HARTEN SACHEN",
        band_p="News und Basis-Guides bleiben für immer gratis. Premium ist für das Tiefe: getestete Geldmethoden, Missions-Routen und versteckte Orte, sobald sie getestet sind.",
        home_title="Vice Hub · Alles zu GTA 6, jeden Tag neu",
        cat_suffix=". Jeden Tag neue Beiträge.", cat_empty="Die ersten Guides kommen am Launch-Tag.",
        cat_desc="Täglich neu auf Vice Hub.", more="MEHR GUIDES", sources="Quellen",
        com_kicker="Von Spielern, für Spieler", com_h="COMMUNITY-TIPPS",
        com_lead="Geldtrick, versteckter Shop oder schnellere Missionsroute gefunden? Poste ihn. Die besten bekommen 👍, die Top-Tipps prüfen wir und machen daraus ganze Guides.",
        com_empty="Das Board startet mit dem Spiel. Poste den ersten Tipp und er erscheint hier.",
        post_tip_h="TIPP POSTEN", post_tip_p="Dauert 30 Sekunden. Kategorie wählen, Tipp schreiben, fertig. Tipps mit den meisten 👍 landen auf diesem Board.",
        share_tip="Tipp teilen", form_note="Öffnet ein kurzes Formular (kostenloses GitHub-Konto nötig).", by="von", anon="anonym",
        com_title="GTA-6-Community-Tipps · Vice Hub", com_desc="Tipps, Glitches und Geheimnisse von GTA-6-Spielern. Vote für die besten.",
        prem_sub="Für 5 € / Monat abonnieren", prem_vat="In Deutschland zahlst du insgesamt rund 5 € inkl. MwSt. (4,20 € plus 19 % MwSt.). Gumroad rechnet in US-Dollar ab und die Steuer hängt vom Land ab, deshalb kann der Betrag um ein paar Cent abweichen.", prem_h="DIE HARTEN SACHEN. 5 € / MONAT.",
        prem_intro="Vice Hub bleibt gratis für News, Launch-Infos und Basis-Tipps. Premium schaltet die Guides frei, für die wir stundenlang testen.",
        prem_perks=["💰 Schon drin: der Tag-1-Geld-Guide, jede bestätigte Methode sortiert nach Auszahlung", "🎯 Missions-Routen, sobald sie getestet sind",
                    "🗺️ Versteckte Shops, Verstecke und Geheimnisse, sobald wir sie finden", "⚡ Höchstens ein neuer Premium-Guide pro Tag, nie News"],
        prem_status="Premium ist noch nicht offen. Bis zum Start nehmen wir kein Geld und fragen keine Kartendaten ab. Folge uns, dann erfährst du es zuerst:",
        prem_faq=[("Was bleibt gratis?", "Alle News, Launch-Fakten, Release-Zeiten und Basis-Tipps. Nur tiefe Guides sind Premium."),
                  ("Kann ich kündigen?", "Ja, jederzeit. Keine Mindestlaufzeit."),
                  ("Wann geht es los?", "Sobald nach dem Launch die ersten echten Guides getestet sind. Wir sagen es auf TikTok, YouTube und Instagram an.")],
        prem_faq_live=[("Was bekomme ich heute?", "Den Tag-1-Geld-Guide mit jeder bestätigten legalen Geldmethode. Neue tiefe Guides kommen dazu, sobald sie getestet sind, höchstens einer pro Tag."),
                       ("Wie zahle und lese ich?", "Bezahlung und Mitgliederbereich laufen über Gumroad, Gumroad ist der Verkäufer. Die Guides bekommst du dort direkt nach der Zahlung.")],
        prem_title="Vice Hub Premium · 5 € / Monat", prem_desc="Tiefe GTA-6-Guides: getestete Geldmethoden, Missions-Routen und versteckte Orte, sobald sie getestet sind.",
        nf_title="Nicht gefunden · Vice Hub", nf_p="Diese Seite gibt es nicht.", nf_btn="Zurück zum Hub",
        switch="EN", switch_name="English",
    ),
}
MONTHS_DE = ["Jan.", "Feb.", "März", "Apr.", "Mai", "Juni", "Juli", "Aug.", "Sep.", "Okt.", "Nov.", "Dez."]


def load_articles():
    arts = []
    for p in (ROOT / "content" / "articles").glob("*.json"):
        a = json.loads(p.read_text())
        assert a["category"] in CAT, f"{p}: unknown category"
        arts.append(a)
    arts.sort(key=lambda a: (a["date"], a.get("order", 0)), reverse=True)
    return arts


def loc(a, lang):
    """Article in the given language (falls back to English)."""
    if lang == "de" and isinstance(a.get("de"), dict):
        return {**a, **{k: v for k, v in a["de"].items() if v}}
    return a


def minutes(a):
    words = sum(len(x.split()) for x in a["body"]) + len(a["summary"].split())
    return max(1, round(words / 200))


def pre(lang):
    return "/de" if lang == "de" else ""


def u(path, lang=None):
    return f"{BASE}{pre(lang)}{path}"


def fmt(d, lang):
    d = dt.date.fromisoformat(d)
    return f"{d.day}. {MONTHS_DE[d.month - 1]} {d.year}" if lang == "de" else d.strftime("%-d %b %Y")


def cl(c, lang, key="label"):
    return c.get(f"{key}_{lang}") or c[key] if lang != "en" else c[key]


def page(lang, title, desc, path, body, og_type="website", alternates=True, active=""):
    t = T[lang]
    canon = f"{ORIGIN}{pre(lang)}{path}"
    cover = f"{ORIGIN}/assets/cover.png"
    x = X[lang]
    nav = f'<a href="{u("/map/", lang)}" class="nav-hide">🗺️ {x["map"]}</a>' + "".join(
        f'<a href="{u("/" + c + "/", lang)}" class="nav-hide">{cl(CAT[c], lang)}</a>' for c in ("news", "hacks", "tips")
    ) + f'<a href="{u("/community/", lang)}" class="nav-hide" style="color:#ffe58a">{t["community"]}</a>' \
      + f'<a href="{u("/buy/", lang)}" class="nav-hide">🛒 {x["buy"]}</a>'
    legal = (f'<a href="{u("/impressum/", lang)}">{x["imp"]}</a><a href="{u("/datenschutz/", lang)}">{x["priv"]}</a>'
             if extras.legal_ok(CFG) else "")
    fnav = (f'<nav><a href="{u("/map/", lang)}">{x["map"]}</a><a href="{u("/buy/", lang)}">{x["buy"]}</a>'
            f'<a href="{u("/community/", lang)}">Community</a><a href="{u("/premium/", lang)}">Premium</a>{legal}</nav>')
    other = "de" if lang == "en" else "en"
    switch = (f'<a href="{u(path, other)}" class="lang" hreflang="{other}" title="{T[lang]["switch_name"]}" '
              f'onclick="try{{localStorage.setItem(\'lang\',\'{other}\')}}catch(e){{}}">{t["switch"]}</a>')
    alt = ""
    if alternates:
        alt = (f'<link rel="alternate" hreflang="en" href="{ORIGIN}{path}">'
               f'<link rel="alternate" hreflang="de" href="{ORIGIN}/de{path}">'
               f'<link rel="alternate" hreflang="x-default" href="{ORIGIN}{path}">')
    # German browsers land on /de/ unless the visitor picked a language before.
    redirect = ""
    if lang == "en" and alternates:
        redirect = ("<script>try{if(!localStorage.getItem('lang')&&/^de\\b/i.test(navigator.language||'')){"
                    f"location.replace('{BASE}/de'+location.pathname.slice({len(BASE)})+location.search+location.hash)}}}}catch(e){{}}</script>")
    return f"""<!doctype html>
<html lang="{lang}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
{redirect}<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{canon}">{alt}
<meta property="og:type" content="{og_type}"><meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{canon}">
<meta property="og:locale" content="{'de_DE' if lang == 'de' else 'en_US'}">
<meta property="og:image" content="{cover}"><meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0d0614">
<link rel="icon" type="image/png" href="{u('/assets/favicon.png')}">
<link rel="apple-touch-icon" href="{u('/assets/apple-touch-icon.png')}">
<link rel="preload" href="{u('/assets/fonts/anton.woff2')}" as="font" type="font/woff2" crossorigin>
{extras.head_extra(CFG, u)}
<link rel="stylesheet" href="{u('/assets/style.css')}">
</head><body>
<div class="glow"></div>
<header class="wrap top">
  <a href="{u('/', lang)}" class="logo">VICE<span>HUB</span><small>{t['tagline']}</small></a>
  <nav>{nav}{switch}<a href="{u('/premium/', lang)}" class="btn-prem">{t['premium']}</a></nav>
</header>
<main>{body}</main>
<footer class="wrap foot">
  {fnav}
  <p class="soc">{''.join(f'<a href="{s["href"]}" target="_blank" rel="noopener">{s["label"]}</a>' for s in CFG["socials"])}</p>
  <p>{t['footer']}</p>
  <p class="tiny" style="text-align:left">{x['footer_aff']}</p>
</footer>
{extras.tabbar(CFG, lang, u, active)}{extras.SHARE_JS}
</body></html>"""


def chip(c, lang):
    return f'<span class="chip">{CAT[c]["emoji"]} {cl(CAT[c], lang)}</span>'


def thumb(c, lang, big=False):
    return f'<div class="thumb t-{c}{" big" if big else ""}" aria-hidden="true"><span class="em">{CAT[c]["emoji"]}</span><span class="w">{cl(CAT[c], lang).upper()}</span></div>'


def card(a, lang):
    t = T[lang]
    tag = f'<span class="lock">{t["locked"]}</span>' if a.get("premium") else f'<span class="muted">{minutes(a)} {t["min"]}</span>'
    la = loc(a, lang)
    return f"""<a class="card" href="{u('/a/' + a['slug'] + '/', lang)}">{thumb(a['category'], lang)}
<h3>{E(la['title'])}</h3><p>{E(la['summary'])}</p><div class="row date"><span>{fmt(a['date'], lang)}</span>{tag}</div></a>"""


def week_strip(today, lang):
    t = T[lang]
    start = today - dt.timedelta(days=today.weekday())
    cells = []
    for i in range(7):
        d = start + dt.timedelta(days=i)
        on = d <= today
        cells.append(f'<div class="day{" on" if on else ""}"><b>{t["days"][i]}</b>{"✓" if on else "·"}</div>')
    return f'<div class="week">{"".join(cells)}<span class="pill">{t["updated"]}</span></div>'


def countdown(lang):
    t = T[lang]
    y, m, d = (int(x) for x in LAUNCH.split("-"))
    units = json.dumps(t["cd_units"])
    return f"""<div class="cd" id="cd"><span class="cd-l">{t['cd_label']}</span><b class="cd-v" id="cdv">{t['cd_static']}</b></div>
<script>(function(){{var T=new Date({y},{m - 1},{d},0,0,0),U={units},el=document.getElementById('cdv'),box=document.getElementById('cd');
function p(n){{return n<10?'0'+n:n}}function f(){{var s=Math.floor((T-new Date())/1000);if(s<=0){{box.className='cd out';box.innerHTML='<b class="cd-v">{t['cd_out']}</b>';return}}
var dd=Math.floor(s/86400);el.textContent=(dd?dd+U[0]+' ':'')+p(Math.floor(s%86400/3600))+U[1]+' '+p(Math.floor(s%3600/60))+U[2]+' '+p(s%60)+U[3];setTimeout(f,1000)}}f()}})()</script>"""


def premium_card(lang, compact=False):
    t = T[lang]
    perks = "" if compact else "<ul>" + "".join(f"<li>{p}</li>" for p in t["perks"]) + "</ul>"
    return f"""<div class="prem"><div class="prem-top"><span>{t['prem_label']}</span><b>5 €<small>{t['per_month']}</small></b></div>
{perks}<a href="{u('/premium/', lang)}" class="btn-grad">{t['get_prem']}</a><p class="tiny">{t['cancel']}</p></div>"""


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


def build_lang(lang, arts, today, tips):
    t = T[lang]
    P = pre(lang)
    soc = "".join(f'<a href="{s["href"]}" target="_blank" rel="noopener">{s["label"]}</a>' for s in CFG["socials"])

    tiles = "".join(
        f'<a class="tile" href="{u("/" + c["id"] + "/", lang)}"><div class="em">{c["emoji"]}</div><b>{cl(c, lang)}</b><small>{E(cl(c, lang, "blurb"))}</small></a>'
        for c in CATS
    ) + f'<a class="tile" href="{u("/community/", lang)}" style="border-color:rgba(255,216,74,.4)"><div class="em">🗳️</div><b>{t["community"]}</b><small>{t["community_tile"]}</small></a>'
    show_cd = today <= dt.date.fromisoformat(LAUNCH)
    home = f"""
<section class="wrap hero">
  <div><p class="kicker">{t['kicker']}</p>
  <h1>{t['h1a']}<br><span class="grad">{t['h1b']}</span></h1>
  <p class="lead">{t['lead_home']}</p>
  {countdown(lang) if show_cd else ''}
  <div class="cta-row"><a class="btn-grad" href="{u('/map/', lang)}">{X[lang]['hero_map']}</a><a class="btn-ghost" href="#latest">{X[lang]['hero_news']}</a></div>
  {week_strip(today, lang)}</div>
  <div class="hero-prem">{premium_card(lang, compact=True)}</div>
</section>
<section class="wrap">{extras.bf_banner(lang, u) if extras.bf_active(today) else ''}<div class="tiles" style="margin-top:14px">{tiles}</div>{extras.features(lang, u)}</section>
<section class="wrap" id="latest"><h2 class="sec">{t['latest']}</h2><div class="grid">{''.join(card(a, lang) for a in arts[:6])}</div></section>
<section class="wrap">{extras.follow_box(CFG, lang)}</section>
<section class="wrap"><div class="grid" style="margin-top:16px">{''.join(card(a, lang) for a in arts[6:])}</div></section>
<section class="wrap"><div class="band"><div><h2 class="sec">{t['band_h']}</h2>
<p class="lead">{t['band_p']}</p></div>{premium_card(lang)}</div></section>"""
    desc = CFG.get(f"description_{lang}") or CFG["description"] if lang != "en" else CFG["description"]
    write(f"{P}/", page(lang, t["home_title"], desc, "/", home, active="home"))

    soon = CFG.get("soon_de" if lang == "de" else "soon", {}) or CFG.get("soon", {})
    for c in CATS:
        lst = [a for a in arts if a["category"] == c["id"]]
        pills = "".join(
            f'<a class="pillnav{" act" if x["id"] == c["id"] else ""}" href="{u("/" + x["id"] + "/", lang)}">{x["emoji"]} {cl(x, lang)}</a>' for x in CATS
        )
        note = f'<div class="note">{E(soon[c["id"]])}</div>' if c["id"] in soon else ""
        grid = f'<div class="grid">{"".join(card(a, lang) for a in lst)}</div>' if lst else f'<p class="muted">{t["cat_empty"]}</p>'
        blurb = cl(c, lang, "blurb")
        body = f"""<section class="wrap"><div class="pills">{pills}</div>
<h1 class="cat">{c['emoji']} GTA 6 {cl(c, lang).upper()}</h1><p class="lead">{E(blurb)}{t['cat_suffix']}</p>{note}</section>
<section class="wrap">{grid}</section><section class="wrap narrow">{premium_card(lang)}</section>"""
        write(f"{P}/{c['id']}/", page(lang, f"GTA 6 {cl(c, lang)} · Vice Hub", f"{blurb}. {t['cat_desc']}", f"/{c['id']}/", body))

    for a in arts:
        la = loc(a, lang)
        prem = a.get("premium")
        # Premium: only a teaser goes into the HTML, the full guide never ships publicly.
        content = render_body(la["body"][:2] if prem else la["body"])
        if prem:
            content = f'<div class="locked">{content}<div class="fade"></div></div>{premium_card(lang)}'
        src = ""
        if a.get("sources"):
            src = f'<div class="sources"><b>{t["sources"]}</b><ul>' + "".join(
                f'<li><a href="{E(s["url"])}" target="_blank" rel="noopener nofollow">{E(s["label"])}</a></li>' for s in a["sources"]
            ) + "</ul></div>"
        more = [x for x in arts if x["slug"] != a["slug"]][:3]
        ld = {"@context": "https://schema.org", "@type": "Article", "headline": la["title"], "description": la["summary"],
              "datePublished": a["date"], "inLanguage": lang, "image": f"{ORIGIN}/assets/cover.png",
              "publisher": {"@type": "Organization", "name": "Vice Hub"}, "isAccessibleForFree": not prem}
        body = f"""<article class="wrap art">
<a class="back" href="{u('/' + a['category'] + '/', lang)}">← {cl(CAT[a['category']], lang)}</a>
{thumb(a['category'], lang, big=True)}
<div class="row">{chip(a['category'], lang)}<span class="muted">{fmt(a['date'], lang)} · {minutes(la)} {t['min_read']}</span></div>
<h1>{E(la['title'])}</h1><p class="lead">{E(la['summary'])}</p>
<div class="prose">{content}</div>{src}
{extras.share_bar(lang, f"{ORIGIN}{P}/a/{a['slug']}/", la['title'])}{extras.buy_box(lang, u)}</article>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<section class="wrap"><h2 class="sec">{t['more']}</h2><div class="grid">{''.join(card(x, lang) for x in more)}</div>{extras.follow_box(CFG, lang)}</section>"""
        write(f"{P}/a/{a['slug']}/", page(lang, f"{la['title']} · Vice Hub", la["summary"], f"/a/{a['slug']}/", body, "article"))

    tip_html = "".join(
        f'<div class="tip"><a class="vote" href="{E(x["url"])}" target="_blank" rel="noopener">▲<span>{x.get("votes", 0)}</span></a><div><small>{E(x.get("category", "Tips"))} · {t["by"]} {E(x.get("author", t["anon"]))}</small><h3>{E(x["title"])}</h3><p>{E(x["body"])}</p></div></div>'
        for x in sorted(tips, key=lambda x: -x.get("votes", 0))
    ) or f'<div class="note">{t["com_empty"]}</div>'
    com = f"""<section class="wrap"><p class="kicker" style="padding-top:24px;color:#ffe58a">{t['com_kicker']}</p><h1 class="cat">{t['com_h']}</h1>
<p class="lead">{t['com_lead']}</p>
<div class="cgrid"><div>{tip_html}</div><div class="prem"><div class="prem-top"><span>{t['post_tip_h']}</span></div><p style="color:#e6d6f2">{t['post_tip_p']}</p><a class="btn-grad" style="display:block" href="{E(CFG['tip_url'])}" target="_blank" rel="noopener">{t['share_tip']}</a><p class="tiny">{t['form_note']}</p></div></div></section>"""
    write(f"{P}/community/", page(lang, t["com_title"], t["com_desc"], "/community/", com, active="community"))

    checkout = CFG.get("checkout_url", "")
    cta = (f'<a class="btn-grad big" href="{E(checkout)}" target="_blank" rel="noopener">{t["prem_sub"]}</a><p class="tiny">{t["prem_vat"]}</p>' if checkout else
           f'<div class="note">{t["prem_status"]}</div><p class="soc big">{soc}</p>')
    faq_items = t["prem_faq"][:2] + t["prem_faq_live"] if checkout else t["prem_faq"]
    faq = "".join(f"<details><summary>{q}</summary><p>{a_}</p></details>" for q, a_ in faq_items)
    prem_body = f"""<section class="wrap narrow"><p class="kicker" style="padding-top:24px">Vice Hub Premium</p><h1 class="cat">{t['prem_h']}</h1>
<p class="lead">{t['prem_intro']}</p>
<ul class="perks">{''.join(f'<li>{p}</li>' for p in t['prem_perks'])}</ul>{cta}<div class="faq">{faq}</div>
{'' if checkout else extras.follow_box(CFG, lang)}</section>"""
    write(f"{P}/premium/", page(lang, t["prem_title"], t["prem_desc"], "/premium/", prem_body))

    x = X[lang]
    write(f"{P}/map/", page(lang, x["map_title"], x["map_desc"], "/map/", extras.map_page(CFG, lang, u, CFG["tip_url"]) +
                            f'<section class="wrap">{extras.follow_box(CFG, lang)}</section>', active="map"))
    bfb = extras.bf_banner(lang, u) if extras.bf_active(today) else ""
    write(f"{P}/buy/", page(lang, x["buy_title"], x["buy_desc"], "/buy/",
                            (f'<section class="wrap narrow">{bfb}</section>' if bfb else "") + extras.buy_page(CFG, lang, u), active="buy"))
    write(f"{P}/black-friday/", page(lang, x["bf_title"], x["bf_desc"], "/black-friday/", extras.bf_page(CFG, lang, u, today), active="buy"))
    if extras.legal_ok(CFG):
        write(f"{P}/impressum/", page(lang, f"{x['imp']} · Vice Hub", x["imp"], "/impressum/", extras.impressum_page(CFG, lang)))
        write(f"{P}/datenschutz/", page(lang, f"{x['priv']} · Vice Hub", x["priv"], "/datenschutz/", extras.privacy_page(CFG, lang)))

    nf = page(lang, t["nf_title"], t["nf_title"], "/404.html",
              f'<section class="wrap narrow"><h1 class="cat">WASTED.</h1><p class="lead">{t["nf_p"]}</p><a class="btn-grad" href="{u("/", lang)}">{t["nf_btn"]}</a></section>',
              alternates=False)
    return nf


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    css = OUT / "assets" / "style.css"
    css.write_text(extras.CSS + css.read_text())
    (OUT / ".nojekyll").write_text("")
    (OUT / "manifest.webmanifest").write_text(extras.manifest(CFG, BASE))
    if CFG.get("adsense_client"):
        pub = CFG["adsense_client"].replace("ca-", "")
        (OUT / "ads.txt").write_text(f"google.com, {pub}, DIRECT, f08c47fec0942fa0\n")
    if CFG.get("indexnow_key"):
        (OUT / f"{CFG['indexnow_key']}.txt").write_text(CFG["indexnow_key"])
    for f in CFG.get("verification_files", []):
        (OUT / f["name"]).write_text(f["content"])
    arts = load_articles()
    today = dt.date.fromisoformat(arts[0]["date"]) if arts else dt.date.today()
    today = max(today, dt.date.today())
    tips = json.loads((ROOT / "content" / "community.json").read_text())

    for lang in LANGS:
        nf = build_lang(lang, arts, today, tips)
        write(f"{pre(lang)}/404.html", nf)

    paths = ["/", "/map/", "/buy/", "/black-friday/", "/premium/", "/community/"] + [f"/{c['id']}/" for c in CATS] + [f"/a/{a['slug']}/" for a in arts]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for p in paths:
        alts = (f'<xhtml:link rel="alternate" hreflang="en" href="{ORIGIN}{p}"/>'
                f'<xhtml:link rel="alternate" hreflang="de" href="{ORIGIN}/de{p}"/>')
        for lang in LANGS:
            sm.append(f"  <url><loc>{ORIGIN}{pre(lang)}{p}</loc><lastmod>{today.isoformat()}</lastmod>{alts}</url>")
    sm.append("</urlset>")
    (OUT / "sitemap.xml").write_text("\n".join(sm))
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {ORIGIN}/sitemap.xml\n")
    print(f"built {len(arts)} articles x {len(LANGS)} languages, {len(paths) * len(LANGS)} pages -> {OUT}")


if __name__ == "__main__":
    build()
