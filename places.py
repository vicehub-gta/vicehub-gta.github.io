"""Locations checklist (free, on /map/) and the Premium members page.

Public data: content/places.json (safehouses, garages, collectible overview, secret teasers).
Premium data: content/premium/vault.json, encrypted with tools/seal.py. The page decrypts it
in the browser with the access code members get on Gumroad.
"""
import json
from html import escape as E
from pathlib import Path

ROOT = Path(__file__).parent

L = {
    "en": dict(
        h="FIND EVERYTHING", kicker="Locations checklist",
        lead="Every safehouse, garage and collectible we could verify, from at least two guide sites. Tick what you have, your progress stays on this device.",
        done="done", of="of", reset="Reset my ticks", src="Sources",
        safehouses="🏠 Safehouses", sh_note="You get these through the story, you can't buy homes.",
        garages_buy="🚗 Garages to buy", garages_story="🎁 Free story garages", garages_bonus="⭐ Edition and GTA+ garages",
        collect="💎 Collectibles", collect_note="Counts and rewards are free. The exact spot of every item is in Premium.",
        eggs="👽 Secrets and easter eggs", eggs_more="more secrets with exact spots in Premium",
        price="Price", unlock="Unlock", reward="Reward", total="Total",
        prem_cta="Unlock all spots in Premium",
        # members page
        m_title="Vice Hub Premium · Members", m_h="MEMBERS AREA",
        m_lead="Enter the access code from your Gumroad receipt or library. It is checked on this device only.",
        m_code="Access code", m_open="Open", m_bad="That code doesn't work. Copy it from your Gumroad library, without spaces.",
        m_buy="No code yet?", m_buy_btn="Get Premium for 5 € / month", m_forget="Log out on this device",
        m_tab_secrets="🔑 Secrets early", m_tab_spots="📍 All spots", m_tab_eggs="👽 Secrets map", m_tab_money="💰 Money guide",
        m_secrets_lead="Every GTA 6 secret one day before it goes up on YouTube and TikTok, with sources.",
        m_early="Early: public on", m_public="Public since", m_next="Next secret unlocks here on",
        m_spots_lead="Exact spots for every collectible we could verify. Tick them off, progress is shared with the free map.",
        m_eggs_lead="Every secret that at least two guide sites place in the same spot.",
    ),
    "de": dict(
        h="FINDE ALLES", kicker="Fundorte-Checkliste",
        lead="Jedes Versteck, jede Garage und jedes Sammelobjekt, das wir bei mindestens zwei Guide-Seiten bestätigt gefunden haben. Hak ab, was du hast, dein Fortschritt bleibt auf diesem Gerät.",
        done="erledigt", of="von", reset="Meine Haken löschen", src="Quellen",
        safehouses="🏠 Unterkünfte", sh_note="Die bekommst du über die Story, Häuser kaufen geht nicht.",
        garages_buy="🚗 Garagen zum Kaufen", garages_story="🎁 Gratis-Garagen aus der Story", garages_bonus="⭐ Editions- und GTA+-Garagen",
        collect="💎 Sammelobjekte", collect_note="Anzahl und Belohnung sind gratis. Den genauen Fundort jedes Teils gibt es in Premium.",
        eggs="👽 Geheimnisse und Easter Eggs", eggs_more="weitere Geheimnisse mit genauem Ort in Premium",
        price="Preis", unlock="Freischaltung", reward="Belohnung", total="Gesamt",
        prem_cta="Alle Fundorte in Premium freischalten",
        m_title="Vice Hub Premium · Mitglieder", m_h="MITGLIEDERBEREICH",
        m_lead="Gib den Zugangscode aus deinem Gumroad-Kauf ein. Er wird nur auf diesem Gerät geprüft.",
        m_code="Zugangscode", m_open="Öffnen", m_bad="Der Code passt nicht. Kopier ihn aus deiner Gumroad-Bibliothek, ohne Leerzeichen.",
        m_buy="Noch keinen Code?", m_buy_btn="Premium für 5 € / Monat holen", m_forget="Auf diesem Gerät abmelden",
        m_tab_secrets="🔑 Secrets vorab", m_tab_spots="📍 Alle Fundorte", m_tab_eggs="👽 Geheimnis-Orte", m_tab_money="💰 Geld-Guide",
        m_secrets_lead="Jedes GTA-6-Secret einen Tag bevor es auf YouTube und TikTok kommt, mit Quellen.",
        m_early="Vorab: öffentlich am", m_public="Öffentlich seit", m_next="Das nächste Secret erscheint hier am",
        m_spots_lead="Genaue Fundorte für jedes Sammelobjekt, das wir bestätigen konnten. Hak sie ab, der Fortschritt gilt auch auf der Gratis-Map.",
        m_eggs_lead="Jedes Geheimnis, das mindestens zwei Guide-Seiten am selben Ort sehen.",
    ),
}


def load():
    p = ROOT / "content" / "places.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def vault():
    p = ROOT / "content" / "premium" / "vault.json"
    return p.read_text(encoding="utf-8").strip() if p.exists() else ""


def _srcs(keys, srcmap):
    return " · ".join(f'<a href="{E(srcmap[k][1])}" target="_blank" rel="noopener">{E(srcmap[k][0])}</a>' for k in keys if k in srcmap)


def _item(it, lang, srcmap, extra=""):
    how = it.get("how_" + lang, "")
    return (f'<li><label class="ck"><input type="checkbox" data-id="{E(it["id"])}"><span class="box"></span>'
            f'<span class="ckt"><b>{E(it["name"])}</b><small class="area">📍 {E(it["area"])}</small>'
            f'{f"<small>{E(how)}</small>" if how else ""}{extra}'
            f'<small class="src">{_srcs(it.get("src", []), srcmap)}</small></span></label></li>')


def _group(title, items_html, n, note=""):
    return (f'<details class="pgrp" open><summary><span>{title}</span><em class="pc" data-n="{n}">0/{n}</em></summary>'
            f'{f"<p class=pnote>{note}</p>" if note else ""}<ul class="cklist">{items_html}</ul></details>')


def money(n, lang):
    return f"{n:,}".replace(",", "." if lang == "de" else ",") + " $"


CK_JS = """<script>(function(){var K='vh-done',S={};try{S=JSON.parse(localStorage.getItem(K)||'{}')}catch(e){}
function save(){try{localStorage.setItem(K,JSON.stringify(S))}catch(e){}}
function count(){document.querySelectorAll('.pgrp').forEach(function(g){var c=g.querySelectorAll('input[data-id]'),d=0;c.forEach(function(i){if(i.checked)d++});var e=g.querySelector('.pc');if(e)e.textContent=d+'/'+c.length;g.classList.toggle('full',c.length>0&&d===c.length)});
var all=document.querySelectorAll('input[data-id]'),d=0;all.forEach(function(i){if(i.checked)d++});var t=document.getElementById('ptot');if(t){t.textContent=d;document.getElementById('pall').textContent=all.length;document.getElementById('pbar').style.width=(all.length?d*100/all.length:0)+'%'}}
window.vhBind=function(root){(root||document).querySelectorAll('input[data-id]').forEach(function(i){i.checked=!!S[i.dataset.id];i.addEventListener('change',function(){if(i.checked)S[i.dataset.id]=1;else delete S[i.dataset.id];save();count()})});count()};
var r=document.getElementById('preset');if(r)r.addEventListener('click',function(){S={};save();document.querySelectorAll('input[data-id]').forEach(function(i){i.checked=false});count()});
vhBind()})()</script>"""


def checklist(lang, u):
    d = load()
    if not d:
        return ""
    t = L[lang]
    sm = d["src"]
    sh = "".join(_item(i, lang, sm) for i in d["safehouses"])
    gb = "".join(_item(i, lang, sm, f'<small class="price">{t["price"]}: {money(i["price"], lang)}</small>') for i in d["garages_buy"])
    gs = "".join(_item(i, lang, sm) for i in d["garages_story"])
    gx = "".join(_item(i, lang, sm) for i in d["garages_bonus"])
    col = "".join(
        f'<div class="colrow"><b>{E(c["name_" + lang])}</b><span class="cnum">{c["count"]}</span>'
        f'<small>{E(c.get("reward_" + lang, ""))}</small><small class="src">{_srcs(c.get("src", []), sm)}</small></div>'
        for c in d.get("collect_overview", []))
    eggs = d.get("eggs_teaser", [])
    egg_html = "".join(_item(i, lang, sm) for i in eggs)
    more = d.get("eggs_premium_count", 0)
    prem = u("/premium/", lang)
    return f"""<section class="wrap narrow" id="fundorte"><p class="kicker" style="padding-top:34px">{t['kicker']}</p><h2 class="cat">{t['h']}</h2>
<p class="lead">{t['lead']}</p>
<div class="ptop"><b><span id="ptot">0</span> {t['of']} <span id="pall">0</span> {t['done']}</b><div class="pbarw"><div id="pbar"></div></div></div>
{_group(t['safehouses'], sh, len(d['safehouses']), t['sh_note'])}
{_group(t['garages_buy'], gb, len(d['garages_buy']), E(d['garages_buy_note_' + lang]))}
{_group(t['garages_story'], gs, len(d['garages_story']))}
{_group(t['garages_bonus'], gx, len(d['garages_bonus']))}
{f'<details class="pgrp" open><summary><span>{t["collect"]}</span></summary><p class="pnote">{t["collect_note"]}</p><div class="cols">{col}</div><a class="btn-grad" href="{prem}">{t["prem_cta"]}</a></details>' if col else ''}
{_group(t['eggs'], egg_html, len(eggs)) if eggs else ''}
{f'<div class="note">🔒 +{more} {t["eggs_more"]} <a class="btn-grad" style="margin:10px 0 0;display:inline-block" href="{prem}">{t["prem_cta"]}</a></div>' if more else ''}
<p class="tiny" style="text-align:left;margin-top:12px"><button class="linkbtn" id="preset">{t['reset']}</button></p></section>{CK_JS}"""


MEMBERS_JS = r"""<script>(function(){var V=__VAULT__,LANG='__LANG__',T=__T__,K='vh-pass';
function b64(s){return Uint8Array.from(atob(s),function(c){return c.charCodeAt(0)})}
async function dec(pw){var km=await crypto.subtle.importKey('raw',new TextEncoder().encode(pw),'PBKDF2',false,['deriveKey']);
var key=await crypto.subtle.deriveKey({name:'PBKDF2',salt:b64(V.salt),iterations:V.iter,hash:'SHA-256'},km,{name:'AES-GCM',length:256},false,['decrypt']);
var pt=await crypto.subtle.decrypt({name:'AES-GCM',iv:b64(V.iv)},key,b64(V.ct));return JSON.parse(new TextDecoder().decode(pt))}
function e(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function src(keys,map){return (keys||[]).filter(function(k){return map&&map[k]}).map(function(k){return '<a href="'+e(map[k][1])+'" target="_blank" rel="noopener">'+e(map[k][0])+'</a>'}).join(' · ')}
function item(it,map){var how=it['how_'+LANG]||it[LANG]||'';return '<li><label class="ck"><input type="checkbox" data-id="'+e(it.id)+'"><span class="box"></span><span class="ckt"><b>'+e(it.name)+'</b><small class="area">📍 '+e(it.area)+'</small>'+(how?'<small>'+e(how)+'</small>':'')+'<small class="src">'+src(it.src,map)+'</small></span></label></li>'}
function grp(title,inner,n,note){return '<details class="pgrp" open><summary><span>'+title+'</span>'+(n?'<em class="pc">0/'+n+'</em>':'')+'</summary>'+(note?'<p class="pnote">'+note+'</p>':'')+inner+'</details>'}
function md(lines){var h='',ul=false;lines.forEach(function(l){if(l.indexOf('- ')===0){if(!ul){h+='<ul>';ul=true}h+='<li>'+e(l.slice(2))+'</li>';return}if(ul){h+='</ul>';ul=false}if(l.indexOf('## ')===0)h+='<h3>'+e(l.slice(3))+'</h3>';else h+='<p>'+e(l)+'</p>'});return h+(ul?'</ul>':'')}
function fmt(d){var p=d.split('-');return LANG==='de'?p[2]+'.'+p[1]+'.'+p[0]:new Date(d+'T12:00:00').toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric'})}
function render(D){var today=new Date(),iso=today.getFullYear()+'-'+('0'+(today.getMonth()+1)).slice(-2)+'-'+('0'+today.getDate()).slice(-2);
function minus1(d){var x=new Date(d+'T12:00:00');x.setDate(x.getDate()-1);return x.getFullYear()+'-'+('0'+(x.getMonth()+1)).slice(-2)+'-'+('0'+x.getDate()).slice(-2)}
var vis=D.secrets.filter(function(s){return minus1(s.post_date)<=iso}).sort(function(a,b){return b.n-a.n});
var next=D.secrets.filter(function(s){return minus1(s.post_date)>iso}).sort(function(a,b){return a.n-b.n})[0];
var sec='<p class="lead">'+T.m_secrets_lead+'</p>'+(next?'<div class="note">⏭️ '+T.m_next+' <b>'+fmt(minus1(next.post_date))+'</b> (#'+next.n+')</div>':'')+vis.map(function(s){var early=s.post_date>iso;
return '<article class="secret"><div class="sechead"><span class="secn">#'+s.n+'</span><span class="'+(early?'badge-early':'badge-pub')+'">'+(early?T.m_early:T.m_public)+' '+fmt(s.post_date)+'</span></div><h3>'+e(s['title_'+LANG])+'</h3><ol>'+s['tips_'+LANG].map(function(x){return '<li>'+e(x)+'</li>'}).join('')+'</ol><p class="src">'+s.sources.map(function(x){return '<a href="'+e(x[1])+'" target="_blank" rel="noopener">'+e(x[0])+'</a>'}).join(' · ')+'</p></article>'}).join('');
var spots=(D.collect||[]).map(function(c){return grp(e(c['name_'+LANG])+' <small>('+c.items.length+'/'+c.count+')</small>','<ul class="cklist">'+c.items.map(function(i){return item(i,D.collect_src)}).join('')+'</ul>',c.items.length,e(c['note_'+LANG]||''))}).join('');
var eggs='<ul class="cklist">'+D.eggs.items.map(function(i){return item(i,D.eggs.src)}).join('')+'</ul>';
var mg=D.money[LANG];
var tabs=[['s',T.m_tab_secrets,sec],['p',T.m_tab_spots,'<p class="lead">'+T.m_spots_lead+'</p>'+spots],['e',T.m_tab_eggs,'<p class="lead">'+T.m_eggs_lead+'</p>'+grp(T.m_tab_eggs,eggs,D.eggs.items.length)],['m',T.m_tab_money,'<h2 class="cat" style="font-size:34px">'+e(mg.title)+'</h2><div class="body">'+md(mg.body)+'</div>']];
var out=document.getElementById('mout');out.innerHTML='<div class="mtabs">'+tabs.map(function(t,i){return '<button data-t="'+t[0]+'" class="'+(i?'':'on')+'">'+t[1]+'</button>'}).join('')+'</div>'+tabs.map(function(t,i){return '<div class="mpane" data-p="'+t[0]+'"'+(i?' hidden':'')+'>'+t[2]+'</div>'}).join('')+'<p class="tiny" style="margin-top:28px"><button class="linkbtn" id="mout-x">'+T.m_forget+'</button></p>';
out.querySelectorAll('.mtabs button').forEach(function(b){b.addEventListener('click',function(){out.querySelectorAll('.mtabs button').forEach(function(x){x.classList.toggle('on',x===b)});out.querySelectorAll('.mpane').forEach(function(p){p.hidden=p.dataset.p!==b.dataset.t})})});
document.getElementById('mout-x').addEventListener('click',function(){try{localStorage.removeItem(K)}catch(x){}location.reload()});
document.getElementById('mlogin').hidden=true;if(window.vhBind)vhBind(out)}
async function go(pw,quiet){try{var D=await dec(pw.trim());try{localStorage.setItem(K,pw.trim())}catch(x){}render(D)}catch(x){if(!quiet)document.getElementById('merr').hidden=false}}
document.getElementById('mform').addEventListener('submit',function(ev){ev.preventDefault();document.getElementById('merr').hidden=true;go(document.getElementById('mpw').value)});
var saved=null;try{saved=localStorage.getItem(K)}catch(x){}if(saved)go(saved,true)})()</script>"""


def members_page(lang, checkout):
    t = L[lang]
    v = vault()
    if not v:
        return ""
    js = (MEMBERS_JS.replace("__VAULT__", v).replace("__LANG__", lang)
          .replace("__T__", json.dumps({k: t[k] for k in t if k.startswith("m_")}, ensure_ascii=False)))
    return f"""<section class="wrap narrow"><p class="kicker" style="padding-top:24px">Vice Hub Premium</p><h1 class="cat">{t['m_h']}</h1>
<div id="mlogin"><p class="lead">{t['m_lead']}</p>
<form id="mform" class="mform"><label for="mpw">{t['m_code']}</label><input id="mpw" autocomplete="off" autocapitalize="off" spellcheck="false" placeholder="xxxx-xxxx-xxxx-0000">
<button class="btn-grad" type="submit">{t['m_open']}</button></form><p class="note" id="merr" hidden>{t['m_bad']}</p>
<p class="tiny" style="text-align:left;margin-top:22px">{t['m_buy']} <a href="{E(checkout)}" target="_blank" rel="noopener">{t['m_buy_btn']}</a></p></div>
<div id="mout"></div></section>{CK_JS}{js}"""


CSS = """
.ptop{margin:18px 0 10px}.ptop b{color:#fff}.pbarw{height:8px;border-radius:8px;background:rgba(255,255,255,.08);margin-top:8px;overflow:hidden}
#pbar{height:100%;width:0;background:linear-gradient(90deg,var(--pink),var(--yellow));transition:width .3s}
.pgrp{border:1px solid var(--line);border-radius:16px;margin:12px 0;padding:4px 14px 10px;background:rgba(255,255,255,.02)}
.pgrp.full{border-color:var(--yellow)}.pgrp summary{display:flex;justify-content:space-between;align-items:center;cursor:pointer;padding:12px 0;font-weight:800;color:#fff;list-style:none}
.pgrp summary::-webkit-details-marker{display:none}.pgrp summary small{font-weight:500;color:#cdb9dc}.pc{font-style:normal;font-size:13px;color:#cdb9dc;border:1px solid var(--line);border-radius:20px;padding:2px 10px;white-space:nowrap}
.pnote{font-size:14px;color:#cdb9dc;margin:0 0 8px}.cklist{list-style:none;padding:0;margin:0;display:grid;gap:6px}
.ck{display:flex;gap:12px;align-items:flex-start;padding:10px 4px;border-top:1px solid var(--line);cursor:pointer}
.ck input{position:absolute;opacity:0;pointer-events:none}.ck .box{flex:0 0 24px;height:24px;border-radius:8px;border:2px solid #7b5a92;margin-top:1px;display:grid;place-items:center}
.ck input:checked+.box{background:linear-gradient(135deg,var(--pink),var(--yellow));border-color:transparent}.ck input:checked+.box::after{content:"✓";color:#1a0b22;font-weight:900;font-size:15px}
.ck input:focus-visible+.box{outline:2px solid var(--yellow);outline-offset:2px}
.ck input:checked~.ckt b{text-decoration:line-through;opacity:.6}.ckt{display:flex;flex-direction:column;gap:2px;min-width:0}.ckt b{color:#fff}
.ckt small{font-size:14px;color:#cdb9dc;line-height:1.45}.ckt .area{color:#ffd84a}.ckt .price{color:#7fffd4}.src,.ckt .src{font-size:12px;color:#9a86ad}.src a{color:#9a86ad}
.cols{display:grid;gap:8px;margin-bottom:14px}.colrow{display:grid;grid-template-columns:1fr auto;gap:2px 10px;border-top:1px solid var(--line);padding:10px 0}
.colrow b{color:#fff}.colrow .cnum{font-family:Anton,Impact,sans-serif;font-size:22px;color:var(--yellow);grid-row:span 2}.colrow small{font-size:14px;color:#cdb9dc;grid-column:1}
.linkbtn{background:none;border:0;color:#9a86ad;text-decoration:underline;cursor:pointer;font:inherit;padding:0}
.mform{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:18px 0}.mform label{width:100%;font-weight:700;color:#fff}
.mform input{flex:1 1 220px;min-width:0;background:rgba(255,255,255,.06);border:1px solid var(--line);border-radius:14px;color:#fff;font:inherit;padding:14px 16px}
.mform .btn-grad{margin:0}
.mtabs{display:flex;gap:8px;overflow-x:auto;padding:4px 0 14px;margin:0 -2px}.mtabs button{flex:0 0 auto;background:rgba(255,255,255,.05);border:1px solid var(--line);color:#fff;border-radius:22px;padding:9px 14px;font:inherit;font-weight:700;cursor:pointer}
.mtabs button.on{background:linear-gradient(135deg,var(--pink),var(--yellow));color:#1a0b22;border-color:transparent}
.secret{border:1px solid var(--line);border-radius:18px;padding:16px;margin:14px 0;background:rgba(255,255,255,.02)}.secret h3{color:#fff;margin:6px 0 10px;font-size:20px}
.secret ol{margin:0;padding-left:20px;color:#e7d9f2}.secret li{margin:6px 0}.sechead{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.secn{font-family:Anton,Impact,sans-serif;font-size:24px;color:var(--yellow)}.badge-early{font-size:12px;font-weight:800;background:var(--pink);color:#fff;border-radius:20px;padding:3px 10px}
.badge-pub{font-size:12px;color:#cdb9dc;border:1px solid var(--line);border-radius:20px;padding:3px 10px}
"""
