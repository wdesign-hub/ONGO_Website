"""Replace the All of Doha section of the Showroom Roboto page with an interactive SVG map.

Usage: python3 inject_map.py <page.html> <doha.svg> <pins.json>
"""
import json
import re
import sys

page, svg_path, pins_path = sys.argv[1:4]
h = open(page, encoding="utf-8").read()
svg = open(svg_path, encoding="utf-8").read()
pins = json.load(open(pins_path))["pins"]

DESC = {
    "west-bay": "Office towers, hotels and residential car parks along the Corniche.",
    "the-pearl": "Residential towers and marina car parks across the islands.",
    "lusail": "Marina District, Lusail Boulevard and the new residential quarters.",
    "msheireb": "Downtown Doha, from Msheireb Downtown to Souq Waqif.",
    "al-sadd": "Apartments, offices and malls around Al Sadd Street.",
    "al-waab": "Villas and compounds near Aspire Zone.",
}
LEFT = {"al-sadd"}
ORDER = ["lusail", "the-pearl", "west-bay", "msheireb", "al-sadd", "al-waab"]

pin_html = "".join(
    f'<button type="button" class="pin{" left" if k in LEFT else ""}" id="pin-{k}" data-area="{k}" aria-expanded="false" aria-controls="areacard" '
    f'style="left:{pins[k]["left"]}%;top:{pins[k]["top"]}%"><span class="dot" aria-hidden="true"></span>'
    f'<span class="tag">{pins[k]["name"]}</span></button>'
    for k in ORDER
)

section = f'''<section class="s g" id="areas" style="background:var(--card)"><div class="in areas">
  <div class="areas-copy"><h2 style="font-size:clamp(40px,5.6vw,72px)">All of <em>Doha</em></h2><p style="color:var(--ink-2);font-size:18px;margin-top:18px;max-width:440px">At home, at work or at the mall. If your car is in Doha, a washer can come to it.</p>
  <ul><li>West Bay</li><li>Lusail</li><li>The Pearl</li><li>Al Waab</li><li>Al Sadd</li><li>Msheireb</li><li><em>and in between</em></li></ul>
  <p class="maphint">Tap an area on the map to see what's covered.</p></div>
  <figure class="mapfig"><div class="mapwrap" id="mapwrap">{svg}{pin_html}
    <div class="areacard" id="areacard" role="dialog" aria-modal="false" aria-labelledby="areacard-title" hidden>
      <button type="button" class="close" id="areacard-close" aria-label="Close area details"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button>
      <span class="ok"><span class="lime-dot"></span>Washers cover this area</span>
      <h3 id="areacard-title">Area</h3>
      <p id="areacard-desc"></p>
      <dl><div><dt>Arrival</dt><dd>Usually 15–30 min</dd></div><div><dt>Express</dt><dd>from 45 QAR</dd></div><div><dt>Payment</dt><dd>After the wash</dd></div></dl>
      <a class="btn" href="#download">Book in the app</a>
    </div>
    <span class="northmark" aria-hidden="true">N</span>
  </div>
  <figcaption>The shaded area is where ONGO washers work today. Map data © OpenStreetMap contributors via Overture Maps · Boundaries: geoBoundaries</figcaption></figure>
</div></section>'''

i = h.index('<section class="s g" id="areas"')
j = h.index("</section>", i) + len("</section>")
h = h[:i] + section + h[j:]

# CSS: drop the old image rules, add the interactive map styles.
h = re.sub(r"\.mapfig\{[^}]*\}\n?", "", h)
h = re.sub(r"\.mapfig img\{[^}]*\}\n?", "", h)
h = re.sub(r"\.mapfig figcaption\{[^}]*\}\n?", "", h)
h = re.sub(r"@media \(max-width:600px\)\{\.mapfig img\{[^}]*\}\}\n?", "", h)
css = """
.areas{grid-template-columns:.85fr 1.15fr;align-items:start}
.areas-copy{display:flex;flex-direction:column;gap:22px;position:sticky;top:110px}
.maphint{font-size:14px;color:var(--ink-2);display:flex;align-items:center;gap:8px}
.mapfig{margin:0;display:flex;flex-direction:column;gap:10px;min-width:0}
.mapfig figcaption{font-size:12.5px;color:var(--ink-2)}
.mapwrap{position:relative;border-radius:24px;overflow:hidden;border:1px solid var(--line);box-shadow:0 24px 60px #1117121a;background:#E4ECE7}
.dohamap{display:block;width:100%;height:auto}
.northmark{position:absolute;right:16px;top:14px;font-weight:700;font-size:13px;color:var(--ink);background:#ffffffd9;border-radius:8px;padding:4px 8px}
.pin{position:absolute;transform:translate(-18px,-18px);display:flex;align-items:center;gap:6px;background:none;border:0;cursor:pointer;font:inherit;min-height:44px;padding:11px}
.pin.left{flex-direction:row-reverse;transform:translate(calc(-100% + 18px),-18px)}
.pin .dot{flex:0 0 14px;height:14px;border-radius:50%;background:var(--green);border:2px solid #fff;box-shadow:0 0 0 6px #A0E87080;transition:box-shadow .2s}
.pin .tag{font-size:13px;font-weight:700;color:var(--ink);background:#fff;border:1px solid #16320033;border-radius:999px;padding:4px 10px;box-shadow:0 4px 12px #11171214;white-space:nowrap;transition:background .15s,color .15s}
.pin:hover .tag,.pin[aria-expanded="true"] .tag{background:var(--green);color:#fff;border-color:var(--green)}
.pin[aria-expanded="true"] .dot{box-shadow:0 0 0 9px #A0E870aa}
.pin:focus-visible{outline:none}.pin:focus-visible .tag{outline:2px solid var(--green);outline-offset:2px}
.areacard{position:absolute;z-index:5;width:min(300px,calc(100% - 24px));background:#fff;border-radius:18px;box-shadow:0 24px 50px #11171233;border:1px solid var(--line);padding:18px 18px 16px;display:flex;flex-direction:column;gap:10px}
.areacard[hidden]{display:none}
.areacard h3{font-size:24px;letter-spacing:-.02em}
.areacard p{color:var(--ink-2);font-size:14px;line-height:1.5}
.areacard .ok{font-size:12.5px;font-weight:700;color:var(--green)}
.areacard dl{margin:2px 0 4px;display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.areacard dl div{background:var(--mist);border-radius:10px;padding:8px}
.areacard dt{font-size:11px;color:var(--ink-2)}
.areacard dd{margin:0;font-size:13px;font-weight:700}
.areacard .btn{min-height:44px;font-size:14px}
.areacard .close{position:absolute;right:8px;top:8px;width:36px;height:36px;border-radius:10px;border:0;background:transparent;color:var(--ink-2);cursor:pointer;display:grid;place-items:center}
.areacard .close:hover{background:var(--mist)}
@media (prefers-reduced-motion:no-preference){.areacard:not([hidden]){animation:pop .18s ease-out}@keyframes pop{from{opacity:.4;transform:translateY(6px)}to{opacity:1;transform:none}}}
@media (max-width:900px){.areas{grid-template-columns:1fr}.areas-copy{position:static}}
@media (max-width:600px){.pin .tag{font-size:12px;padding:3px 8px}.areacard{left:12px!important;right:12px;top:auto!important;bottom:12px;width:auto}}
"""
anchor = ".areas li{font-family:var(--serif);font-size:26px;font-weight:300;line-height:1.6}"
assert h.count(anchor) == 1
h = h.replace(anchor, anchor + css)

js = """
<script>
(function(){
  var wrap=document.getElementById('mapwrap'); if(!wrap) return;
  var card=document.getElementById('areacard'), title=document.getElementById('areacard-title'), desc=document.getElementById('areacard-desc');
  var D=%s, open=null;
  function place(btn){
    if(window.matchMedia('(max-width:600px)').matches){card.style.left='';card.style.top='';return;}
    var w=wrap.clientWidth,h=wrap.clientHeight,x=btn.offsetLeft,y=btn.offsetTop,cw=card.offsetWidth,ch=card.offsetHeight;
    var left=x+24; if(left+cw>w-12) left=x-cw-24; left=Math.max(12,Math.min(left,w-cw-12));
    var top=y-ch/2; top=Math.max(12,Math.min(top,h-ch-12));
    card.style.left=left+'px'; card.style.top=top+'px';
  }
  function close(focus){ if(!open) return; open.setAttribute('aria-expanded','false'); card.hidden=true; if(focus) open.focus(); open=null; }
  function show(btn){
    if(open===btn){close(true);return;}
    if(open) open.setAttribute('aria-expanded','false');
    var k=btn.getAttribute('data-area'); title.textContent=btn.querySelector('.tag').textContent; desc.textContent=D[k];
    card.hidden=false; btn.setAttribute('aria-expanded','true'); open=btn; place(btn);
  }
  wrap.querySelectorAll('.pin').forEach(function(b){ b.addEventListener('click',function(e){e.stopPropagation();show(b);}); });
  document.getElementById('areacard-close').addEventListener('click',function(){close(true);});
  card.addEventListener('click',function(e){e.stopPropagation();});
  document.addEventListener('click',function(){close(false);});
  document.addEventListener('keydown',function(e){ if(e.key==='Escape') close(true); });
  window.addEventListener('resize',function(){ if(open) place(open); });
})();
</script>
""" % json.dumps(DESC)
h = h.rstrip() + "\n" + js
open(page, "w", encoding="utf-8").write(h)
print("ok", len(h))
