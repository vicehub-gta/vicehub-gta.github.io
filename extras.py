"""Extra pages and widgets for Vice Hub: map, buy/setup (affiliate), follow box,
share bar, mobile tab bar, legal pages (Impressum / Datenschutz), ads.

All money settings live in site.json:
  amazon_tag, instant_gaming_ref      affiliate ids (links only appear if set)
  adsense_client                      "ca-pub-..." -> Google Auto Ads + ads.txt
  newsletter_action                   form POST URL (Buttondown/Brevo/...) -> email form
  discord_url                         invite link -> Discord button
  checkout_url                        premium payment link (Ko-fi/Stripe/...)
  legal{name,street,city,country,email}  -> /impressum/ + /datenschutz/ pages
"""
import html
import json
from urllib.parse import quote_plus

E = html.escape

X = {
    "en": dict(
        map="Map", buy="Buy & setup", follow="Follow", home="Home",
        hero_map="🗺️ Open the map", hero_news="Latest news",
        feat=[("🗺️", "Leonida map", "All 6 regions, what to find where", "/map/"),
              ("⏰", "Unlock time", "When GTA 6 starts where you live", "/a/gta-6-unlock-time-every-time-zone/"),
              ("🛒", "Buy & setup", "Editions, SSD space, best controller", "/buy/")],
        fb_h="NEVER MISS A GTA 6 SECRET", fb_p="New guides every day. Follow Rito GTA and you get the best tricks first, as short clips.",
        nl_ph="your@email.com", nl_btn="Get the daily guide", nl_note="One email a day at most. Unsubscribe with one click.",
        share="Share", copied="Link copied ✓", share_h="Send this to your squad",
        buybox_h="Don't have GTA 6 yet?", buybox_p="Editions, prices and the setup that makes the 212 GB download hurt less.", buybox_btn="See editions & setup",
        # map
        map_title="GTA 6 Map: all Leonida regions explained · Vice Hub",
        map_desc="Interactive GTA 6 map guide: Vice City, Leonida Keys, Grassrivers, Port Gellhorn, Ambrosia and Mount Kalaga. What to find in each region.",
        map_kicker="Interactive map", map_h="THE LEONIDA MAP", map_lead="Tap a pin. Six regions, each with its own vibe, missions and money. We add real spots (shops, stashes, fastest routes) as players find them.",
        map_hint="👆 Tap a region", map_soon="Spot something in-game? Post it and it can land on this map.", map_post="Post a spot",
        map_note="Regions as revealed by Rockstar before launch. Layout is a simplified fan sketch, not the in-game map.",
        # buy
        buy_title="Buy GTA 6: editions, prices & the best setup · Vice Hub",
        buy_desc="GTA 6 Standard vs Ultimate, what you need for the 212 GB download, and the controller, headset and TV worth it.",
        buy_kicker="Buy & setup", buy_h="GET GTA 6 READY", buy_lead="Which edition, how much space, and the gear that is actually worth it for Vice City. Short and honest.",
        ed_h="1. Pick your edition",
        eds=[("Standard", "$79.99", "Full game + pre-order bonus. Our pick: start here, you can upgrade any time."),
             ("Ultimate", "$99.99", "Extra cars, weapons, outfits, properties and shops that unlock through the story.")],
        bonus="Buy before 20 Nov: Vintage Vice City Pack ('55 Vapid Stanier + Shore Court Garage + outfits).",
        ps5="GTA 6 for PS5", xbox="GTA 6 for Xbox", credit="PSN / Xbox credit",
        setup_h="2. The setup that makes a difference",
        gear=[("💾", "2 TB SSD", "GTA 6 needs 212 GB. A PS5 SSD upgrade saves you deleting everything else.", "PS5 SSD 2TB heatsink"),
              ("🎮", "DualSense controller", "Second controller so one is always charged.", "DualSense controller"),
              ("🕹️", "DualSense Edge", "Back paddles: drive and shoot without leaving the sticks.", "DualSense Edge"),
              ("🎮", "Xbox controller", "For Series X|S players.", "Xbox Wireless Controller"),
              ("🎧", "Gaming headset", "Hear cops and footsteps before you see them.", "gaming headset PS5"),
              ("🔌", "Charging station", "Never start a mission at 5 % battery again.", "PS5 controller charging station"),
              ("📺", "4K 120 Hz TV", "Biggest visual upgrade for PS5 Pro and Series X.", "4K 120Hz TV HDMI 2.1")],
        on_amazon="on Amazon", on_ig="on Instant Gaming",
        disc="Affiliate links. As an Amazon Associate, Vice Hub earns from qualifying purchases.",
        footer_aff="Contains affiliate links.",
        imp="Legal notice", priv="Privacy",
        prem_notify="Want to know the second Premium opens?",
    ),
    "de": dict(
        map="Map", buy="Kaufen & Setup", follow="Folgen", home="Start",
        hero_map="🗺️ Zur Map", hero_news="Neueste News",
        feat=[("🗺️", "Leonida-Map", "Alle 6 Regionen, was du wo findest", "/map/"),
              ("⏰", "Startzeit", "Wann GTA 6 bei dir losgeht", "/a/gta-6-unlock-time-every-time-zone/"),
              ("🛒", "Kaufen & Setup", "Editionen, SSD-Platz, bester Controller", "/buy/")],
        fb_h="VERPASS KEIN GTA-6-GEHEIMNIS", fb_p="Jeden Tag neue Guides. Folge Rito GTA und du bekommst die besten Tricks zuerst, als kurze Clips.",
        nl_ph="deine@email.de", nl_btn="Täglichen Guide holen", nl_note="Höchstens eine Mail pro Tag. Abmelden mit einem Klick.",
        share="Teilen", copied="Link kopiert ✓", share_h="Schick das deiner Crew",
        buybox_h="Noch kein GTA 6?", buybox_p="Editionen, Preise und das Setup, mit dem der 212-GB-Download weniger wehtut.", buybox_btn="Editionen & Setup ansehen",
        map_title="GTA-6-Map: alle Regionen von Leonida erklärt · Vice Hub",
        map_desc="Interaktiver GTA-6-Map-Guide: Vice City, Leonida Keys, Grassrivers, Port Gellhorn, Ambrosia und Mount Kalaga. Was du in welcher Region findest.",
        map_kicker="Interaktive Map", map_h="DIE LEONIDA-MAP", map_lead="Tipp auf einen Pin. Sechs Regionen, jede mit eigenem Vibe, eigenen Missionen und eigenem Geld. Echte Spots (Shops, Verstecke, schnellste Routen) tragen wir ein, sobald Spieler sie finden.",
        map_hint="👆 Tipp auf eine Region", map_soon="Im Spiel was entdeckt? Poste es, dann kann es auf diese Map.", map_post="Spot posten",
        map_note="Regionen so, wie Rockstar sie vor dem Launch gezeigt hat. Die Skizze ist vereinfacht, nicht die echte Spielkarte.",
        buy_title="GTA 6 kaufen: Editionen, Preise & bestes Setup · Vice Hub",
        buy_desc="GTA 6 Standard oder Ultimate, was du für den 212-GB-Download brauchst und welcher Controller, welches Headset und welcher TV sich lohnen.",
        buy_kicker="Kaufen & Setup", buy_h="MACH DICH BEREIT FÜR GTA 6", buy_lead="Welche Edition, wie viel Speicher und welches Zubehör sich für Vice City wirklich lohnt. Kurz und ehrlich.",
        ed_h="1. Edition wählen",
        eds=[("Standard", "79,99 $", "Komplettes Spiel + Vorbesteller-Bonus. Unser Tipp: hier starten, upgraden geht jederzeit."),
             ("Ultimate", "99,99 $", "Extra Autos, Waffen, Outfits, Immobilien und Shops, die mit der Story freigeschaltet werden.")],
        bonus="Kauf vor dem 20. Nov.: Vintage Vice City Pack ('55 Vapid Stanier + Shore Court Garage + Outfits).",
        ps5="GTA 6 für PS5", xbox="GTA 6 für Xbox", credit="PSN- / Xbox-Guthaben",
        setup_h="2. Das Setup, das den Unterschied macht",
        gear=[("💾", "2-TB-SSD", "GTA 6 braucht 212 GB. Mit einer PS5-SSD musst du nicht alles andere löschen.", "PS5 SSD 2TB Kühlkörper"),
              ("🎮", "DualSense-Controller", "Zweiter Controller, damit immer einer geladen ist.", "DualSense Controller"),
              ("🕹️", "DualSense Edge", "Rückentasten: fahren und schießen, ohne die Sticks loszulassen.", "DualSense Edge"),
              ("🎮", "Xbox-Controller", "Für Series X|S.", "Xbox Wireless Controller"),
              ("🎧", "Gaming-Headset", "Cops und Schritte hören, bevor du sie siehst.", "Gaming Headset PS5"),
              ("🔌", "Ladestation", "Nie wieder Mission mit 5 % Akku starten.", "PS5 Controller Ladestation"),
              ("📺", "4K-120-Hz-TV", "Größtes Bild-Upgrade für PS5 Pro und Series X.", "4K 120Hz Fernseher HDMI 2.1")],
        on_amazon="bei Amazon", on_ig="bei Instant Gaming",
        disc="Affiliate-Links. Als Amazon-Partner verdient Vice Hub an qualifizierten Verkäufen.",
        footer_aff="Enthält Affiliate-Links.",
        imp="Impressum", priv="Datenschutz",
        prem_notify="Willst du wissen, wann Premium startet?",
    ),
}

# Regions revealed on Rockstar's official GTA VI site (May 2025). x/y in the SVG viewBox 0 0 400 520.
REGIONS = [
    ("vice-city", "Vice City", 300, 360, "🌴",
     "The neon heart of Leonida. Beaches, nightlife, yachts, influencers and the biggest scores. Expect the densest missions and the best money here.",
     "Das Neon-Herz von Leonida. Strände, Nachtleben, Yachten, Influencer und die dicksten Coups. Hier gibt es die meisten Missionen und das beste Geld."),
    ("leonida-keys", "Leonida Keys", 240, 470, "🏝️",
     "A chain of islands south of the mainland. Boats, mangroves, beach bars and a slower, looser life, until it isn't.",
     "Eine Inselkette südlich vom Festland. Boote, Mangroven, Strandbars und ein entspanntes Leben, bis es knallt."),
    ("grassrivers", "Grassrivers", 220, 360, "🐊",
     "Wild wetlands full of gators, airboats and people who don't want to be found. Great for hiding out after a job.",
     "Wilde Sümpfe voller Alligatoren, Airboats und Leute, die nicht gefunden werden wollen. Perfekt zum Untertauchen nach einem Job."),
    ("port-gellhorn", "Port Gellhorn", 80, 120, "⚓",
     "A faded port town on the Gulf coast. Cheap motels, industry, and the rough side of Leonida.",
     "Eine heruntergekommene Hafenstadt an der Golfküste. Billige Motels, Industrie und die raue Seite von Leonida."),
    ("ambrosia", "Ambrosia", 210, 210, "🏭",
     "Small-town Leonida around a sugar refinery. Biker gangs, back roads and trouble that grows in the fields.",
     "Kleinstadt-Leonida rund um eine Zuckerfabrik. Biker-Gangs, Landstraßen und Ärger, der auf den Feldern wächst."),
    ("mount-kalaga", "Mount Kalaga", 170, 60, "⛰️",
     "The national park in the north. Forests, rivers, hunting and off-road trails, the wildest part of the map.",
     "Der Nationalpark im Norden. Wälder, Flüsse, Jagd und Offroad-Strecken, der wildeste Teil der Map."),
]

# Simplified Florida-like silhouette, drawn by hand (fan sketch).
LAND = ("M20,40 L330,30 L345,70 L330,120 L300,150 L310,200 L340,260 L350,320 L345,380 L320,420 "
        "L280,430 L250,400 L215,380 L190,340 L180,300 L150,260 L130,200 L105,165 L60,140 L20,120 Z")
KEYS = [(255, 452, 14, 6), (230, 470, 12, 5), (205, 486, 11, 5), (180, 498, 10, 4), (155, 506, 8, 4)]


def amazon(cfg, query):
    tag = cfg.get("amazon_tag")
    q = quote_plus(query)
    return f"https://www.amazon.de/s?k={q}" + (f"&tag={tag}" if tag else "")


def instant(cfg, query):
    ref = cfg.get("instant_gaming_ref")
    return f"https://www.instant-gaming.com/en/search/?q={quote_plus(query)}" + (f"&igr={ref}" if ref else "")


def ext(href, label, cls="btn-ghost"):
    return f'<a class="{cls}" href="{E(href)}" target="_blank" rel="sponsored nofollow noopener">{label}</a>'


def head_extra(cfg, u):
    out = [f'<link rel="manifest" href="{u("/manifest.webmanifest")}">']
    if cfg.get("google_site_verification"):
        out.append(f'<meta name="google-site-verification" content="{E(cfg["google_site_verification"])}">')
    if cfg.get("adsense_client"):
        c = E(cfg["adsense_client"])
        out.append(f'<meta name="google-adsense-account" content="{c}">'
                   f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={c}" crossorigin="anonymous"></script>')
    return "".join(out)


def social_buttons(cfg, big=True):
    ic = {"TikTok": "♪", "YouTube": "▶", "Instagram": "◎", "Discord": "💬"}
    socials = list(cfg["socials"])
    if cfg.get("discord_url"):
        socials.append({"label": "Discord", "href": cfg["discord_url"]})
    return '<div class="socbtns">' + "".join(
        f'<a class="sb sb-{s["label"].lower()}" href="{E(s["href"])}" target="_blank" rel="noopener"><span>{ic.get(s["label"], "→")}</span>{s["label"]}</a>'
        for s in socials) + "</div>"


def follow_box(cfg, lang):
    x = X[lang]
    nl = ""
    if cfg.get("newsletter_action"):
        nl = (f'<form class="nl" action="{E(cfg["newsletter_action"])}" method="post" target="_blank">'
              f'<input type="email" name="{E(cfg.get("newsletter_email_field", "email"))}" required placeholder="{x["nl_ph"]}" aria-label="E-Mail">'
              f'<button class="btn-grad" type="submit">{x["nl_btn"]}</button></form><p class="tiny" style="text-align:left">{x["nl_note"]}</p>')
    return f"""<div class="fbox"><div><h2 class="sec" style="margin:0">{x['fb_h']}</h2><p class="lead">{x['fb_p']}</p></div>
<div>{nl}{social_buttons(cfg)}</div></div>"""


def share_bar(lang, url, title):
    x = X[lang]
    t = quote_plus(title)
    uq = quote_plus(url)
    return f"""<div class="share"><b>{x['share_h']}</b><div class="share-row">
<button class="sh sh-native" type="button" onclick="vhShare(this)" data-u="{E(url)}" data-t="{E(title)}">↗ {x['share']}</button>
<a class="sh" href="https://wa.me/?text={t}%20{uq}" target="_blank" rel="noopener">WhatsApp</a>
<a class="sh" href="https://x.com/intent/post?text={t}&url={uq}" target="_blank" rel="noopener">X</a>
<a class="sh" href="https://www.reddit.com/submit?url={uq}&title={t}" target="_blank" rel="noopener">Reddit</a>
<button class="sh" type="button" onclick="vhCopy(this)" data-u="{E(url)}" data-ok="{x['copied']}">🔗 Link</button></div></div>"""


SHARE_JS = """<script>function vhShare(b){var u=b.dataset.u,t=b.dataset.t;if(navigator.share){navigator.share({title:t,url:u}).catch(function(){})}else{vhCopy(b)}}
function vhCopy(b){var u=b.dataset.u,ok=b.dataset.ok||'✓';var d=function(){var o=b.textContent;b.textContent=ok;setTimeout(function(){b.textContent=o},1600)};
if(navigator.clipboard){navigator.clipboard.writeText(u).then(d,d)}else{var i=document.createElement('input');i.value=u;document.body.appendChild(i);i.select();try{document.execCommand('copy')}catch(e){}i.remove();d()}}</script>"""


def buy_box(lang, u):
    x = X[lang]
    return f"""<div class="buybox"><div><b>🛒 {x['buybox_h']}</b><p>{x['buybox_p']}</p></div>
<a class="btn-grad" href="{u('/buy/', lang)}">{x['buybox_btn']}</a></div>"""


def tabbar(cfg, lang, u, active=""):
    x = X[lang]
    tt = cfg["socials"][0]["href"]
    items = [("home", "🏠", x["home"], u("/", lang)), ("map", "🗺️", x["map"], u("/map/", lang)),
             ("community", "🗳️", "Community", u("/community/", lang)), ("buy", "🛒", x["buy"].split(" ")[0], u("/buy/", lang))]
    links = "".join(f'<a href="{h}"{" class=act" if k == active else ""}><span>{ic}</span>{lb}</a>' for k, ic, lb, h in items)
    return f'<nav class="tabbar">{links}<a href="{E(tt)}" target="_blank" rel="noopener" class="tb-follow"><span>➕</span>{x["follow"]}</a></nav>'


def features(lang, u):
    x = X[lang]
    return '<div class="feats">' + "".join(
        f'<a class="feat" href="{u(p, lang)}"><span class="em">{em}</span><b>{h}</b><small>{s}</small></a>' for em, h, s, p in x["feat"]
    ) + "</div>"


def map_page(cfg, lang, u, tip_url):
    x = X[lang]
    keys = "".join(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" class="land"/>' for cx, cy, rx, ry in KEYS)
    pins = "".join(
        f'<g class="pin" tabindex="0" role="button" data-r="{rid}" aria-label="{name}"><circle cx="{px}" cy="{py}" r="22" class="pin-halo"/>'
        f'<circle cx="{px}" cy="{py}" r="13" class="pin-dot"/><text x="{px}" y="{py + 5}" text-anchor="middle" class="pin-em">{em}</text>'
        f'<text x="{px}" y="{py + 38}" text-anchor="middle" class="pin-lbl">{name}</text></g>'
        for rid, name, px, py, em, _, _ in REGIONS)
    info = {rid: {"n": name, "e": em, "d": (de if lang == "de" else en)} for rid, name, _, _, em, en, de in REGIONS}
    lst = "".join(f'<li data-r="{rid}"><b>{em} {name}</b><span>{E(de if lang == "de" else en)}</span></li>'
                  for rid, name, _, _, em, en, de in REGIONS)
    return f"""<section class="wrap"><p class="kicker" style="padding-top:20px">{x['map_kicker']}</p><h1 class="cat">{x['map_h']}</h1>
<p class="lead">{x['map_lead']}</p>
<div class="mapwrap"><svg viewBox="0 0 400 520" class="map" role="img" aria-label="Leonida">
<defs><linearGradient id="sea" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1a0b33"/><stop offset="1" stop-color="#0b2a3f"/></linearGradient>
<linearGradient id="lg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3a1550"/><stop offset="1" stop-color="#5a1d4d"/></linearGradient></defs>
<rect width="400" height="520" rx="24" fill="url(#sea)"/><path d="{LAND}" class="land"/>{keys}
<path d="M300,330 Q320,350 300,380" class="road"/><path d="M80,120 Q160,170 210,210 T300,360" class="road"/><path d="M170,60 L210,210" class="road"/>
{pins}</svg>
<div class="mapinfo" id="mi"><p class="muted">{x['map_hint']}</p></div></div>
<ul class="reglist">{lst}</ul>
<div class="note">{x['map_soon']} <a class="btn-grad" style="margin:10px 0 0;display:inline-block" href="{E(tip_url)}" target="_blank" rel="noopener">{x['map_post']}</a></div>
<p class="tiny" style="text-align:left;margin-top:14px">{x['map_note']}</p></section>
<script>(function(){{var I={json.dumps(info, ensure_ascii=False)},mi=document.getElementById('mi');
function show(r){{var o=I[r];if(!o)return;mi.innerHTML='<div class="mi-em">'+o.e+'</div><h2>'+o.n+'</h2><p>'+o.d+'</p>';
document.querySelectorAll('[data-r]').forEach(function(e){{e.classList.toggle('on',e.dataset.r===r)}});if(window.innerWidth<860)mi.scrollIntoView({{behavior:'smooth',block:'nearest'}})}}
document.querySelectorAll('[data-r]').forEach(function(e){{e.addEventListener('click',function(){{show(e.dataset.r)}});e.addEventListener('keydown',function(k){{if(k.key==='Enter')show(e.dataset.r)}})}});show('vice-city')}})()</script>"""


def buy_page(cfg, lang, u):
    x = X[lang]
    eds = "".join(f'<div class="ed"><span>{n}</span><b>{p}</b><p>{E(d)}</p></div>' for n, p, d in x["eds"])
    btns = (ext(amazon(cfg, "GTA 6 PS5"), f'{x["ps5"]} {x["on_amazon"]}', "btn-grad") +
            ext(amazon(cfg, "GTA 6 Xbox Series X"), f'{x["xbox"]} {x["on_amazon"]}', "btn-ghost") +
            (ext(instant(cfg, "playstation network card"), f'{x["credit"]} {x["on_ig"]}', "btn-ghost") if cfg.get("instant_gaming_ref") else ""))
    gear = "".join(
        f'<a class="gear" href="{E(amazon(cfg, q))}" target="_blank" rel="sponsored nofollow noopener"><span class="em">{em}</span>'
        f'<div><b>{n}</b><p>{E(d)}</p><small>{x["on_amazon"]} →</small></div></a>'
        for em, n, d, q in x["gear"])
    return f"""<section class="wrap narrow"><p class="kicker" style="padding-top:20px">{x['buy_kicker']}</p><h1 class="cat">{x['buy_h']}</h1>
<p class="lead">{x['buy_lead']}</p>
<h2 class="sec">{x['ed_h']}</h2><div class="eds">{eds}</div><div class="note">🎁 {x['bonus']}</div>
<div class="btnrow">{btns}</div>
<h2 class="sec">{x['setup_h']}</h2><div class="gears">{gear}</div>
<p class="tiny" style="text-align:left;margin-top:24px">{x['disc']}</p></section>"""


def legal_ok(cfg):
    lg = cfg.get("legal") or {}
    return all(lg.get(k) for k in ("name", "street", "city", "email"))


def impressum_page(cfg, lang):
    lg = cfg["legal"]
    addr = (f'{E(lg["name"])}<br>' + (f'{E(lg["company"])}<br>' if lg.get("company") else "") +
            f'{E(lg["street"])}<br>{E(lg["city"])}<br>{E(lg.get("country", "Deutschland"))}')
    mail = E(lg["email"]).replace("@", "&#64;")
    if lang == "de":
        return f"""<section class="wrap narrow legal"><h1 class="cat">IMPRESSUM</h1>
<h2>Angaben gemäß § 5 DDG</h2><p>{addr}</p><h2>Kontakt</h2><p>E-Mail: {mail}</p>
<h2>Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV</h2><p>{E(lg["name"])}, Anschrift wie oben</p>
<h2>Affiliate-Hinweis</h2><p>Enthält Affiliate-Links. Als Amazon-Partner verdient Vice Hub an qualifizierten Verkäufen.</p>
<h2>Marken</h2><p>Grand Theft Auto VI und alle zugehörigen Marken gehören Rockstar Games / Take-Two Interactive. Vice Hub ist eine Fan-Seite und steht in keiner Verbindung zu Rockstar Games.</p>
<h2>Streitschlichtung</h2><p>Ich bin nicht bereit und nicht verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p></section>"""
    return f"""<section class="wrap narrow legal"><h1 class="cat">LEGAL NOTICE</h1>
<h2>Information according to § 5 DDG (Germany)</h2><p>{addr}</p><h2>Contact</h2><p>Email: {mail}</p>
<h2>Affiliate disclosure</h2><p>Contains affiliate links. As an Amazon Associate, Vice Hub earns from qualifying purchases.</p>
<h2>Trademarks</h2><p>Grand Theft Auto VI and all related marks belong to Rockstar Games / Take-Two Interactive. Vice Hub is a fan site and not affiliated with Rockstar Games.</p></section>"""


def privacy_page(cfg, lang):
    lg = cfg["legal"]
    who = f'{E(lg["name"])}' + (f', {E(lg["company"])}' if lg.get("company") else "") + f', {E(lg["street"])}, {E(lg["city"])}, E-Mail: {E(lg["email"]).replace("@", "&#64;")}'
    ads_de = ads_en = ""
    if cfg.get("adsense_client"):
        ads_de = ("<h2>Google AdSense</h2><p>Diese Website zeigt Werbung über Google AdSense (Google Ireland Limited, Gordon House, Barrow Street, Dublin 4, Irland). "
                  "Google kann dafür Cookies setzen und Daten wie IP-Adresse und Geräteinformationen verarbeiten, auch in den USA. Personalisierte Werbung "
                  "wird nur mit deiner Einwilligung über das Einwilligungsbanner ausgespielt (Art. 6 Abs. 1 lit. a DSGVO, § 25 TDDDG). Du kannst die Einwilligung "
                  "jederzeit über das Banner widerrufen. Mehr: https://policies.google.com/technologies/ads</p>")
        ads_en = ("<h2>Google AdSense</h2><p>This site shows ads via Google AdSense (Google Ireland Limited). Google may set cookies and process data such as IP "
                  "address and device information. Personalised ads are only shown with your consent via the consent banner, which you can withdraw at any time.</p>")
    nl_de = nl_en = ""
    if cfg.get("newsletter_action"):
        nl_de = ("<h2>Newsletter</h2><p>Wenn du dich für den Newsletter einträgst, verarbeiten wir deine E-Mail-Adresse, um dir den Newsletter zu senden "
                 "(Art. 6 Abs. 1 lit. a DSGVO). Der Versand läuft über einen externen Dienstleister. Abmelden geht jederzeit über den Link in jeder Mail.</p>")
        nl_en = "<h2>Newsletter</h2><p>If you sign up, we use your email address only to send the newsletter. Unsubscribe any time via the link in every email.</p>"
    if lang == "de":
        return f"""<section class="wrap narrow legal"><h1 class="cat">DATENSCHUTZ</h1>
<h2>Verantwortlicher</h2><p>{who}</p>
<h2>Hosting</h2><p>Diese Website wird bei GitHub Pages gehostet (GitHub Inc., 88 Colin P. Kelly Jr. St., San Francisco, USA). Beim Aufruf verarbeitet GitHub technisch notwendige Daten wie deine IP-Adresse in Server-Logfiles, um die Seite auszuliefern und abzusichern (Art. 6 Abs. 1 lit. f DSGVO). GitHub ist unter dem EU-US Data Privacy Framework zertifiziert. Mehr: https://docs.github.com/site-policy/privacy-policies/github-general-privacy-statement</p>
<h2>Schriftarten</h2><p>Die Schriftarten werden lokal von diesem Server geladen. Es findet keine Verbindung zu Google Fonts statt.</p>
<h2>Lokaler Speicher</h2><p>Wenn du die Sprache wechselst, speichert dein Browser diese Wahl lokal (localStorage). Diese Information verlässt dein Gerät nicht.</p>
<h2>Externe Links</h2><p>Links zu TikTok, YouTube, Instagram, Amazon, Instant Gaming, WhatsApp, X, Reddit und GitHub führen zu Angeboten anderer Anbieter. Erst wenn du sie anklickst, gelten deren Datenschutzbestimmungen. Affiliate-Links enthalten eine Partner-Kennung, damit der Shop einen Kauf zuordnen kann.</p>
<h2>Community-Tipps</h2><p>Tipps werden über ein GitHub-Formular eingereicht. Dafür gilt die Datenschutzerklärung von GitHub. Veröffentlicht wird nur, was du selbst schreibst, und dein GitHub-Name.</p>
{nl_de}{ads_de}
<h2>Deine Rechte</h2><p>Du hast das Recht auf Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung, Datenübertragbarkeit und Widerspruch (Art. 15 bis 21 DSGVO) sowie das Recht auf Beschwerde bei einer Datenschutz-Aufsichtsbehörde. Schreib dafür an die oben genannte E-Mail-Adresse.</p></section>"""
    return f"""<section class="wrap narrow legal"><h1 class="cat">PRIVACY</h1>
<h2>Controller</h2><p>{who}</p>
<h2>Hosting</h2><p>This site is hosted on GitHub Pages (GitHub Inc., USA). GitHub processes technically necessary data such as your IP address in server logs to deliver and secure the site.</p>
<h2>Fonts</h2><p>Fonts are served from this site. No connection to Google Fonts is made.</p>
<h2>Local storage</h2><p>If you switch language, your browser stores that choice locally. It never leaves your device.</p>
<h2>External links</h2><p>Links to TikTok, YouTube, Instagram, Amazon, Instant Gaming, WhatsApp, X, Reddit and GitHub lead to other providers whose privacy policies apply once you click. Affiliate links contain a partner ID.</p>
{nl_en}{ads_en}
<h2>Your rights</h2><p>Under the GDPR you can request access, correction, deletion, restriction, portability and object to processing, and complain to a data protection authority. Write to the email above.</p></section>"""


def manifest(cfg, base):
    return json.dumps({
        "name": "Vice Hub · GTA 6", "short_name": "Vice Hub", "start_url": f"{base}/", "scope": f"{base}/",
        "display": "standalone", "background_color": "#0d0614", "theme_color": "#0d0614",
        "description": cfg["description"],
        "icons": [{"src": f"{base}/assets/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": f"{base}/assets/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}],
    }, ensure_ascii=False)


CSS = """
@font-face{font-family:Anton;font-style:normal;font-weight:400;font-display:swap;src:url(fonts/anton.woff2) format('woff2')}
@font-face{font-family:Inter;font-style:normal;font-weight:100 900;font-display:swap;src:url(fonts/inter.woff2) format('woff2')}
.btn-ghost{display:inline-block;margin-top:12px;border:1px solid rgba(255,255,255,.3);color:#fff;font-weight:800;padding:11px 20px;border-radius:999px;text-align:center}
.btn-ghost:hover{border-color:#fff;background:rgba(255,255,255,.06)}
.cta-row{display:flex;flex-wrap:wrap;gap:10px;margin-top:8px}
.feats{display:grid;gap:12px;margin-top:16px}@media(min-width:720px){.feats{grid-template-columns:repeat(3,1fr)}}
.feat{display:flex;gap:14px;align-items:center;border:1px solid rgba(255,216,74,.35);background:linear-gradient(135deg,rgba(255,216,74,.08),rgba(255,60,172,.06));border-radius:18px;padding:16px 18px;transition:.15s}
.feat:hover{transform:translateY(-2px);border-color:var(--yellow)}.feat .em{font-size:30px}.feat b{display:block;color:#fff;font-weight:800}.feat small{display:block;color:#cdb9dc;font-size:13px}
.fbox{display:grid;gap:20px;border:1px solid rgba(43,155,255,.45);background:linear-gradient(135deg,rgba(43,155,255,.12),rgba(123,44,255,.12));border-radius:28px;padding:28px;margin-top:56px}
@media(min-width:860px){.fbox{grid-template-columns:1.2fr 1fr;align-items:center}}
.socbtns{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin-top:12px}
.sb{display:flex;align-items:center;justify-content:center;gap:8px;padding:12px 14px;border-radius:14px;font-weight:800;color:#fff;border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.06)}
.sb span{font-size:16px}.sb-tiktok{background:#000;border-color:#25f4ee;box-shadow:inset -3px 0 0 #fe2c55}.sb-youtube{background:#ff0033;border-color:#ff0033}
.sb-instagram{background:linear-gradient(45deg,#f9a825,#e91e63,#7b1fa2);border-color:transparent}.sb-discord{background:#5865f2;border-color:#5865f2}
.nl{display:flex;gap:8px;flex-wrap:wrap}.nl input{flex:1 1 200px;min-width:0;border-radius:999px;border:1px solid rgba(255,255,255,.25);background:rgba(0,0,0,.3);color:#fff;padding:12px 18px;font:inherit}
.nl .btn-grad{margin-top:0;border:0;cursor:pointer;font:inherit;font-weight:800}
.share{margin-top:32px;border-top:1px solid var(--line);padding-top:20px}.share b{color:#fff}.share-row{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}
.sh{border:1px solid rgba(255,255,255,.2);background:rgba(255,255,255,.05);color:#fff;border-radius:999px;padding:8px 14px;font:inherit;font-size:14px;font-weight:700;cursor:pointer}
.sh-native{background:linear-gradient(90deg,var(--pink),var(--orange));color:#1a0716;border:0}
.buybox{display:flex;flex-wrap:wrap;gap:12px 20px;align-items:center;justify-content:space-between;margin-top:28px;border:1px dashed rgba(255,216,74,.5);border-radius:18px;padding:16px 20px}
.buybox b{color:#ffe58a}.buybox p{margin:4px 0 0;color:#d4c1e2;font-size:14px}.buybox .btn-grad{margin-top:0}
.mapwrap{display:grid;gap:16px;margin-top:24px}@media(min-width:860px){.mapwrap{grid-template-columns:1.1fr 1fr;align-items:start}}
.map{width:100%;max-width:520px;height:auto;display:block;margin:0 auto}
.map .land{fill:url(#lg);stroke:rgba(255,60,172,.55);stroke-width:2}.map .road{fill:none;stroke:rgba(255,216,74,.35);stroke-width:2;stroke-dasharray:6 6}
.pin{cursor:pointer;outline:none}.pin-halo{fill:rgba(255,60,172,.18);transition:.2s}.pin-dot{fill:#ff3cac;stroke:#fff;stroke-width:2}
.pin-em{font-size:13px}.pin-lbl{fill:#fff;font:800 13px Inter,sans-serif;paint-order:stroke;stroke:#0d0614;stroke-width:4px}
.pin:hover .pin-halo,.pin:focus .pin-halo,.pin.on .pin-halo{fill:rgba(255,216,74,.45)}.pin.on .pin-dot{fill:#ffd84a}
.mapinfo{border:1px solid rgba(255,60,172,.45);background:linear-gradient(135deg,#2a0b2e,#170a24);border-radius:22px;padding:22px;min-height:160px}
.mapinfo h2{font-family:Anton,sans-serif;font-weight:400;font-size:34px;color:#fff;margin:4px 0 6px}.mapinfo p{color:#e6d6f2;margin:0}.mi-em{font-size:38px}
.reglist{list-style:none;padding:0;margin:24px 0 0;display:grid;gap:8px}@media(min-width:720px){.reglist{grid-template-columns:repeat(2,1fr)}}
.reglist li{border:1px solid var(--line);border-radius:14px;padding:12px 14px;cursor:pointer}.reglist li.on{border-color:var(--yellow);background:rgba(255,216,74,.08)}
.reglist b{display:block;color:#fff}.reglist span{font-size:14px;color:#cdb9dc}
.eds{display:grid;gap:12px}@media(min-width:640px){.eds{grid-template-columns:1fr 1fr}}
.ed{border:1px solid var(--line);background:rgba(255,255,255,.04);border-radius:18px;padding:18px}.ed span{font-size:12px;font-weight:800;letter-spacing:.2em;text-transform:uppercase;color:#ff8fd0}
.ed b{display:block;font-family:Anton,sans-serif;font-weight:400;font-size:36px;color:#fff}.ed p{margin:4px 0 0;color:#d4c1e2;font-size:14px}
.btnrow{display:flex;flex-wrap:wrap;gap:10px;margin-top:8px}
.gears{display:grid;gap:10px}.gear{display:flex;gap:14px;align-items:flex-start;border:1px solid var(--line);background:rgba(255,255,255,.04);border-radius:16px;padding:14px 16px;transition:.15s}
.gear:hover{border-color:rgba(255,216,74,.7)}.gear .em{font-size:28px}.gear b{color:#fff}.gear p{margin:2px 0;color:#cdb9dc;font-size:14px}.gear small{color:#ffe58a;font-weight:700}
.legal h2{font-size:18px;color:#fff;margin:28px 0 6px}.legal p{color:#d4c1e2;margin:0}
.foot nav{flex-wrap:wrap;gap:14px;margin:10px 0}.foot nav a{color:#bda6cf;font-size:14px}
.tabbar{display:none}
@media(max-width:860px){.nav-hide{display:none}}
@media(max-width:860px){body{padding-bottom:74px}.tabbar{display:flex;position:fixed;left:0;right:0;bottom:0;z-index:50;justify-content:space-around;gap:0;
background:rgba(13,6,20,.94);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border-top:1px solid rgba(255,60,172,.35);padding:6px 4px calc(6px + env(safe-area-inset-bottom))}
.tabbar a{flex:1;display:flex;flex-direction:column;align-items:center;font-size:11px;font-weight:700;color:#bda6cf;gap:1px}.tabbar a span{font-size:20px;line-height:1.2}
.tabbar a.act{color:#fff}.tabbar .tb-follow{color:#1a0716;background:linear-gradient(90deg,var(--pink),var(--orange));border-radius:14px;margin:0 4px;padding:2px 0}}
"""
