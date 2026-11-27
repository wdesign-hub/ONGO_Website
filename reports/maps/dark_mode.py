"""Add a light/dark mode switch to the Showroom Roboto page.

Usage: python3 dark_mode.py <page.html>
Default follows the system (and the viewer's data-theme); the switch sets data-mode on <html> and is remembered.
"""
import sys

p = sys.argv[1]
h = open(p, encoding="utf-8").read()


def rep(a, b, count=1):
    global h
    n = h.count(a)
    assert n == count, (n, a[:90])
    h = h.replace(a, b)


LIGHT_EXTRA = ("--surface:#ffffff; --on-green:#ffffff; --green-hover:#0b1f00; --header:#FBFBF8ee; --stage1:#ffffff; --stage3:#e3ecdc; "
               "--sea:#E4ECE7; --land:#F3F5F1; --svcbase:#FFFFFF; --svcfill:#A0E870; --svcop:.31; --svcline:#163200; --water:#CFE3DA; "
               "--r-minor:#163200; --r-minor-op:.16; --r-mid:#5E8F3A; --r-mid-op:.6; --r-major:#5E8F3A; --r-major-op:1; --logo-filter:none;")
DARK = ("--bg:#0B110C; --card:#111A13; --surface:#16211A; --ink:#E8EFE6; --ink-2:#A9B8A9; --green:#A0E870; --on-green:#10220A; "
        "--green-hover:#B9F08F; --mist:#16211A; --line:#E8EFE61f; --header:#0B110Cee; --stage1:#1C2A20; --stage3:#0D150F; "
        "--sea:#070D08; --land:#0E1610; --svcbase:#122016; --svcfill:#A0E870; --svcop:.12; --svcline:#A0E870; --water:#0B1A14; "
        "--r-minor:#A0E870; --r-minor-op:.13; --r-mid:#A0E870; --r-mid-op:.42; --r-major:#A0E870; --r-major-op:.8; "
        "--logo-filter:brightness(0) invert(1); color-scheme:dark;")

rep("  color-scheme:light;\n}", "  " + LIGHT_EXTRA + "\n  color-scheme:light;\n}\n"
    "@media (prefers-color-scheme:dark){:root:not([data-theme=\"light\"]):not([data-mode=\"light\"]){" + DARK + "}}\n"
    ":root[data-theme=\"dark\"]:not([data-mode=\"light\"]){" + DARK + "}\n"
    ":root[data-mode=\"dark\"]{" + DARK + "}\n"
    "body{transition:background-color .25s,color .25s}\n"
    ".logo-img{filter:var(--logo-filter)}\n"
    ".dohamap>rect{fill:var(--sea)}\n"
    ".dohamap>path:nth-of-type(1){fill:var(--land)}\n"
    ".dohamap>path:nth-of-type(2){fill:var(--svcbase)}\n"
    ".dohamap>path:nth-of-type(3){fill:var(--svcfill);fill-opacity:var(--svcop);stroke:var(--svcline)}\n"
    ".dohamap>path:nth-of-type(4){fill:var(--water)}\n"
    ".dohamap g path:nth-of-type(1){stroke:var(--r-minor);stroke-opacity:var(--r-minor-op)}\n"
    ".dohamap g path:nth-of-type(2){stroke:var(--r-mid);stroke-opacity:var(--r-mid-op)}\n"
    ".dohamap g path:nth-of-type(3){stroke:var(--r-major);stroke-opacity:var(--r-major-op)}\n"
    ".modebtn{width:46px;height:46px;flex:0 0 46px;border-radius:12px;border:1px solid var(--line);background:var(--surface);color:var(--ink);display:inline-flex;align-items:center;justify-content:center;cursor:pointer;transition:background .15s}\n"
    ".modebtn:hover{background:var(--mist)}\n"
    ".modebtn .moon{display:none}\n"
    ".is-dark .modebtn .sun{display:none}.is-dark .modebtn .moon{display:block}")

# Hard-coded colours -> tokens.
rep("color:#fff;text-decoration:none;font-weight:700;border:0;font:inherit;font-weight:700;cursor:pointer;transition:background .2s}",
    "color:var(--on-green);text-decoration:none;font-weight:700;border:0;font:inherit;font-weight:700;cursor:pointer;transition:background .2s,color .2s}")
rep(".btn:hover{background:#0b1f00}", ".btn:hover{background:var(--green-hover)}")
rep(".btn.line:hover{background:var(--ink);color:#fff}", ".btn.line:hover{background:var(--ink);color:var(--bg)}")
rep("background:var(--green);color:#fff;padding:10px 16px;border-radius:10px;font-weight:700;text-decoration:none}",
    "background:var(--green);color:var(--on-green);padding:10px 16px;border-radius:10px;font-weight:700;text-decoration:none}")
rep("z-index:20;background:#FBFBF8ee;backdrop-filter:blur(8px)}", "z-index:20;background:var(--header);backdrop-filter:blur(8px)}")
rep("border:1px solid var(--line);background:#fff;color:var(--ink);align-items:center;justify-content:center;cursor:pointer;transition:background .15s}",
    "border:1px solid var(--line);background:var(--surface);color:var(--ink);align-items:center;justify-content:center;cursor:pointer;transition:background .15s}")
rep("border:1px solid var(--line);background:#fff;display:grid;place-items:center;font-size:11px;color:var(--ink-2)}",
    "border:1px solid var(--line);background:#fff;display:grid;place-items:center;font-size:11px;color:#4A544C}")
rep(".note{position:absolute;z-index:2;background:#fff;", ".note{position:absolute;z-index:2;background:var(--surface);")
rep("background:radial-gradient(circle at 50% 40%,#fff 0%,var(--mist) 60%,#e3ecdc 100%)}",
    "background:radial-gradient(circle at 50% 40%,var(--stage1) 0%,var(--mist) 60%,var(--stage3) 100%)}")
rep("background:var(--lime);color:var(--green);padding:3px 8px;border-radius:6px;", "background:var(--lime);color:#163200;padding:3px 8px;border-radius:6px;")
rep(".northmark{position:absolute;right:16px;top:14px;font-weight:700;font-size:13px;color:var(--ink);background:#ffffffd9;",
    ".northmark{position:absolute;right:16px;top:14px;font-weight:700;font-size:13px;color:var(--ink);background:var(--header);")
rep("background:var(--green);border:2px solid #fff;box-shadow:0 0 0 6px #A0E87080;", "background:var(--green);border:2px solid var(--bg);box-shadow:0 0 0 6px #A0E87080;")
rep("color:var(--ink);background:#fff;border:1px solid #16320033;border-radius:999px;", "color:var(--ink);background:var(--surface);border:1px solid var(--line);border-radius:999px;")
rep('.pin:hover .tag,.pin[aria-expanded="true"] .tag{background:var(--green);color:#fff;border-color:var(--green)}',
    '.pin:hover .tag,.pin[aria-expanded="true"] .tag{background:var(--green);color:var(--on-green);border-color:var(--green)}')
rep(".areacard{position:absolute;z-index:5;width:min(300px,calc(100% - 24px));background:#fff;",
    ".areacard{position:absolute;z-index:5;width:min(300px,calc(100% - 24px));background:var(--surface);")
rep(".mapwrap{position:relative;border-radius:24px;overflow:hidden;border:1px solid var(--line);box-shadow:0 24px 60px #1117121a;background:#E4ECE7}",
    ".mapwrap{position:relative;border-radius:24px;overflow:hidden;border:1px solid var(--line);box-shadow:0 24px 60px #1117121a;background:var(--sea)}")
rep(".final{background:#0f1410;", ".final{background:#0f1410;border:1px solid var(--line);")
rep(".final .btn{background:var(--lime);color:var(--green)}", ".final .btn{background:var(--lime);color:#163200}")
rep(".final .btn:hover{background:#b9f08f;color:var(--green)}", ".final .btn:hover{background:#b9f08f;color:#163200}")
rep("text-align:center;font-size:12px;justify-self:end}", "text-align:center;font-size:12px;justify-self:end;color:#4A544C}")
rep("z-index:30;gap:12px;align-items:center;background:#fff;", "z-index:30;gap:12px;align-items:center;background:var(--surface);")

# Logos get the filter class.
for marker in ('<a href="#top" aria-label="ONGO home"><img ', '<div class="sticky"><img '):
    rep(marker, marker + 'class="logo-img" ')
h = h.replace('alt="ONGO" style="height:42px;align-self:flex-start"', 'alt="ONGO" class="logo-img" style="height:42px;align-self:flex-start"', 1)

# Switch button in the header, before the menu button.
btn = ('<button class="modebtn" type="button" id="modebtn" aria-label="Switch to dark mode" aria-pressed="false">'
       '<svg class="sun" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
       '<svg class="moon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5z"/></svg>'
       '</button>')
rep('<button class="menu" type="button"', btn + '\n  <button class="menu" type="button"')

# Head script: apply a saved choice before paint.
rep('<meta name="theme-color" content="#FBFBF8">',
    '<meta name="theme-color" content="#FBFBF8">\n'
    "<script>try{var m=localStorage.getItem('ongo-mode');if(m==='dark'||m==='light')document.documentElement.setAttribute('data-mode',m);}catch(e){}</script>")

# Switch logic.
rep("  var mb=document.getElementById('menubtn'), mn=document.getElementById('mnav');",
    "  var root=document.documentElement, modeBtn=document.getElementById('modebtn'), meta=document.querySelector('meta[name=\"theme-color\"]');\n"
    "  var mq=window.matchMedia('(prefers-color-scheme: dark)');\n"
    "  function isDark(){var m=root.getAttribute('data-mode');if(m) return m==='dark';var t=root.getAttribute('data-theme');if(t) return t==='dark';return mq.matches;}\n"
    "  function sync(){var d=isDark();root.classList.toggle('is-dark',d);modeBtn.setAttribute('aria-pressed',String(d));"
    "modeBtn.setAttribute('aria-label',d?'Switch to light mode':'Switch to dark mode');if(meta) meta.setAttribute('content',d?'#0B110C':'#FBFBF8');}\n"
    "  modeBtn.addEventListener('click',function(){var next=isDark()?'light':'dark';root.setAttribute('data-mode',next);try{localStorage.setItem('ongo-mode',next);}catch(e){}sync();});\n"
    "  if(mq.addEventListener) mq.addEventListener('change',sync);\n"
    "  new MutationObserver(sync).observe(root,{attributes:true,attributeFilter:['data-theme']});\n"
    "  sync();\n"
    "  var mb=document.getElementById('menubtn'), mn=document.getElementById('mnav');")

# Header gap on phones: switch sits left of the menu.
rep("  .nav{justify-content:space-between}\n", "  .nav{justify-content:space-between;gap:10px}\n  .nav>a:first-child{margin-right:auto}\n")

open(p, "w", encoding="utf-8").write(h)
print("ok")
