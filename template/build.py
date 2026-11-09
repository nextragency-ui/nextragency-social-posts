#!/usr/bin/env python3
"""Build a Nextragency carousel from a JSON content file.
Usage: python3 template/build.py template/content/P02.json
Writes template/<id>.html, renders PNGs to posts/YYYY-MM_Pxx_slug/YYYY-MM_Pxx_slug_NN.png and manifest.json (alt text).
Brand: reuses the <style> of template/carousel.html (approved palette, Sora/Manrope with Inter fallback)."""
import json, re, html, sys, os, subprocess
ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
PATHS = ["M4 16 C 40 5, 80 21, 120 10 S 180 8, 196 12","M4 14 C 50 4, 90 20, 130 9 S 182 12, 196 7","M4 15 C 45 5, 95 20, 135 9 S 184 11, 196 8","M4 13 C 50 5, 90 19, 130 10 S 182 9, 196 12","M4 15 C 40 6, 90 20, 125 10 S 184 10, 196 7"]
ICONS = {
 "ads":'<path d="M8 38 L24 22 L32 30 L48 12"/><path d="M36 12 H48 V24"/>',
 "box":'<path d="M8 18 L28 8 L48 18 V38 L28 48 L8 38 Z"/><path d="M8 18 L28 28 L48 18"/><path d="M28 28 V48"/>',
 "user":'<circle cx="28" cy="18" r="9"/><path d="M10 48 C10 32 46 32 46 48"/>',
 "chat":'<path d="M8 12 H48 V36 H26 L16 46 V36 H8 Z"/>',
 "mail":'<rect x="8" y="14" width="40" height="28" rx="4"/><path d="M8 18 L28 32 L48 18"/>',
 "cal":'<rect x="8" y="12" width="40" height="36" rx="4"/><path d="M8 24 H48"/><path d="M18 8 V16"/><path d="M38 8 V16"/>',
 "clock":'<circle cx="28" cy="28" r="20"/><path d="M28 16 V28 L37 33"/>',
 "coins":'<ellipse cx="28" cy="16" rx="16" ry="7"/><path d="M12 16 V28 C12 32 20 35 28 35 C36 35 44 32 44 28 V16"/><path d="M12 28 V40 C12 44 20 47 28 47 C36 47 44 44 44 40 V28"/>',
 "eye":'<path d="M4 28 C14 12 42 12 52 28 C42 44 14 44 4 28 Z"/><circle cx="28" cy="28" r="7"/>',
 "cart":'<path d="M6 10 H13 L19 36 H43 L48 16 H15"/><circle cx="22" cy="44" r="3"/><circle cx="40" cy="44" r="3"/>',
 "alert":'<path d="M28 8 L50 46 H6 Z"/><path d="M28 22 V34"/><path d="M28 40 V41"/>',
 "check":'<circle cx="28" cy="28" r="20"/><path d="M18 29 L25 36 L39 20"/>',
}
EXTRA = """
  .grid2 { margin-top: 40px; display: grid; grid-template-columns: 1fr 1fr; gap: 28px; }
  .gcard { background: var(--card); border: 2px solid var(--line); border-radius: 36px; padding: 36px 36px 40px; min-height: 290px; }
  .gcard .ltr { font-family: 'Sora','Inter',sans-serif; font-size: 64px; font-weight: 900; color: var(--accent); line-height: 1; margin-bottom: 14px; }
  .gcard h3 { font-family: 'Sora','Inter',sans-serif; font-size: 40px; font-weight: 900; line-height: 1.12; margin-bottom: 12px; }
  .gcard p { font-size: 31px; font-weight: 700; color: var(--muted); line-height: 1.25; }
  .chk { margin-top: 36px; }
  .chk .row { align-items: center; padding: 26px 0; gap: 36px; }
  .chk .tick { width: 72px; height: 72px; border-radius: 50%; border: 4px solid var(--accent); flex: none; }
  .chk h3 { font-size: 42px; margin: 0; line-height: 1.15; }
  .nl { margin-top: 40px; }
  .nl .row { align-items: center; padding: 22px 0; gap: 28px; }
  .nl .num { font-size: 58px; width: 110px; }
  .nl h3 { font-size: 44px; margin: 0; line-height: 1.15; }
  .hyp { display: inline-block; font-size: 28px; font-weight: 800; letter-spacing: 2px; text-transform: uppercase; color: var(--accent); border: 2px solid var(--accent); border-radius: 999px; padding: 8px 24px; margin-bottom: 32px; }
  .calc { margin-top: 40px; }
  .crow { display: flex; justify-content: space-between; align-items: center; padding: 20px 0; border-top: 2px solid var(--line); }
  .crow:last-child { border-bottom: 2px solid var(--line); }
  .crow span { font-size: 40px; font-weight: 700; color: #E7EBE8; }
  .crow b { font-family: 'Sora','Inter',sans-serif; font-size: 48px; font-weight: 900; color: var(--text); }
  .crow.hi span, .crow.hi b { color: var(--accent); }
  .vs2 .panel { padding: 44px 48px; }
  .vs2 { margin-top: 44px; gap: 28px; }
  .vs2 .panel p { white-space: normal; }
"""
def hlspan(w, i): return f'<span class="hl">{w}<svg viewBox="0 0 200 24" preserveAspectRatio="none"><path d="{PATHS[i%5]}" stroke="#C6FF3A" stroke-width="7" fill="none" stroke-linecap="round"/></svg></span>'
_c = [0]
def md(t):
    t = html.escape(t, quote=False)
    def r(m):
        _c[0] += 1; return hlspan(m.group(1), _c[0])
    return re.sub(r"\[\[(.+?)\]\]", r, t)
def plain(t): return re.sub(r"\[\[(.+?)\]\]", r"\1", t)
def h2(t, size=None):
    s = size or (92 if len(plain(t)) > 34 else None)
    return f'<h2{f" style=\"font-size:{s}px;\"" if s else ""}>{md(t)}</h2>'
def render_slide(s, n, N, pill, last):
    t = s["type"]; alt = ""
    c = ""
    if t == "hook":
        c = f'<div class="glow" style="width:900px;height:900px;right:-300px;bottom:-250px;"></div>\n  <div class="content" style="top:210px;"><div class="label">{html.escape(s["label"])}</div><h1>{md(s["title"])}</h1>' + (f'<p class="body" style="margin-top:64px;max-width:860px;">{md(s["sub"])}</p>' if s.get("sub") else "") + '</div>'
        alt = f'{plain(s["title"])} {s.get("sub","")}'
    elif t == "cards":
        cards = "".join(f'<div class="card"><div class="icon"><svg viewBox="0 0 56 56">{ICONS[i["icon"]]}</svg></div><div><h3>{html.escape(i["h"])}</h3><p>{html.escape(i["p"])}</p></div></div>' for i in s["items"])
        c = f'<div class="content">{h2(s["title"])}<div class="cards">{cards}</div></div>'
        alt = plain(s["title"]) + ": " + "; ".join(f'{i["h"]} - {i["p"]}' for i in s["items"])
    elif t == "statement":
        c = f'<div class="glow" style="width:800px;height:800px;right:-260px;bottom:-200px;"></div>\n  <div class="content"><div class="label">{html.escape(s["label"])}</div>{h2(s["title"], s.get("size"))}<p class="body" style="margin-top:56px;max-width:900px;">{md(s["body"])}</p></div>'
        alt = plain(s["title"]) + ". " + s["body"]
    elif t == "numlist":
        items = s["items"]
        if all(i.get("p") for i in items) and len(items) <= 4:
            rows = "".join(f'<div class="row"><div class="num">{k+1:02d}</div><div><h3>{html.escape(i["h"])}</h3><p>{html.escape(i["p"])}</p></div></div>' for k, i in enumerate(items))
            c = f'<div class="content">{h2(s["title"])}<div class="list">{rows}</div></div>'
        else:
            rows = "".join(f'<div class="row"><div class="num">{k+1:02d}</div><h3>{html.escape(i["h"])}</h3></div>' for k, i in enumerate(items))
            c = f'<div class="content">{h2(s["title"])}<div class="list nl">{rows}</div></div>'
        alt = plain(s["title"]) + ": " + "; ".join(i["h"] + (" - " + i["p"] if i.get("p") else "") for i in items)
    elif t == "steps":
        hyp = '<div class="hyp">Hypothetical example</div>' if s.get("hyp") else ""
        steps = "".join(f'<div class="step"><div class="dot">{k+1}</div><p>{html.escape(i["h"])}<small>{html.escape(i["p"])}</small></p></div>' for k, i in enumerate(s["items"]))
        c = f'<div class="content">{hyp}{h2(s["title"], 92 if s.get("hyp") else None)}<div class="steps" style="margin-top:70px;gap:70px;">{steps}</div></div>'
        alt = ("Hypothetical example. " if s.get("hyp") else "") + plain(s["title"]) + ": " + "; ".join(f'{i["h"]} - {i["p"]}' for i in s["items"])
    elif t == "vs":
        def panel(cls, d):
            lines = "".join(f'<p>{html.escape(d.get("mark",""))} {html.escape(l)}</p>' for l in d["lines"])
            return f'<div class="panel {cls}"><div class="tag">{html.escape(d["tag"])}</div>{lines}</div>'
        hyp = '<div class="hyp">Hypothetical example</div>' if s.get("hyp") else ""
        c = f'<div class="content">{hyp}{h2(s["title"], 92 if s.get("hyp") else None)}<div class="vs vs2">{panel("old", s["old"])}{panel("new", s["new"])}</div></div>'
        alt = plain(s["title"]) + ". " + s["old"]["tag"] + ": " + "; ".join(s["old"]["lines"]) + ". " + s["new"]["tag"] + ": " + "; ".join(s["new"]["lines"])
    elif t == "check":
        rows = "".join(f'<div class="row"><div class="tick"></div><h3>{html.escape(i)}</h3></div>' for i in s["items"])
        c = f'<div class="content"><div class="label">{html.escape(s["label"])}</div>{h2(s["title"])}<div class="list chk">{rows}</div></div>'
        alt = plain(s["title"]) + ": " + "; ".join(s["items"])
    elif t == "grid2":
        g = "".join(f'<div class="gcard"><div class="ltr">{html.escape(i["l"])}</div><h3>{html.escape(i["h"])}</h3><p>{html.escape(i["p"])}</p></div>' for i in s["items"])
        c = f'<div class="content">{h2(s["title"])}<div class="grid2">{g}</div></div>'
        alt = plain(s["title"]) + ": " + "; ".join(i["h"] for i in s["items"])
    elif t == "calc":
        hyp = '<div class="hyp">Hypothetical figures</div>' if s.get("hyp") else ""
        rows = "".join(f'<div class="crow{" hi" if len(r)>2 and r[2] else ""}"><span>{html.escape(r[0])}</span><b>{html.escape(r[1])}</b></div>' for r in s["rows"])
        c = f'<div class="content">{hyp}{h2(s["title"], 92)}<div class="calc">{rows}</div></div>'
        alt = ("Hypothetical figures. " if s.get("hyp") else "") + plain(s["title"]) + ": " + "; ".join(f'{r[0]} {r[1]}' for r in s["rows"])
    elif t == "cta":
        c = f'<div class="glow" style="width:900px;height:900px;left:90px;bottom:-330px;"></div>\n  <img src="logo-full-t.png" style="position:absolute;width:500px;left:290px;bottom:20px;">\n  <div class="content" style="justify-content:flex-start;top:210px;"><h1 style="line-height:1.14;">{md(s["title"])}</h1><p class="body" style="margin-top:72px;max-width:900px;">{md(s["body"])}</p></div>'
        alt = "Nextragency logo. " + plain(s["title"]) + " " + s["body"]
    bar = "" if t == "cta" else '<div class="brand"><img src="logo-icon-t.png" alt=""><span>NEXTRA<b>GENCY</b></span></div>\n  <div class="swipe">Swipe →</div>'
    return f'<section class="slide" id="s{n}">\n  <div class="counter">{n} / {N}</div>\n  <div class="pill">{html.escape(pill)}</div>\n  {c}\n  {bar}\n</section>\n', alt.strip()
def main(path):
    d = json.load(open(path))
    src = open(os.path.join(ROOT, "carousel.html")).read()
    head = src[:src.index("<body>") + 6].replace("</style>", EXTRA + "</style>").replace("Black Friday Teaser Carousel", d["id"])
    N = len(d["slides"]); body = ""; alts = []
    for k, s in enumerate(d["slides"], 1):
        h, a = render_slide(s, k, N, d["pill"], k == N); body += h; alts.append(a)
    out_html = os.path.join(ROOT, f'{d["id"].lower()}.html')
    open(out_html, "w").write(head + "\n" + body + "\n</body>\n</html>\n")
    name = f'{d["month"]}_{d["id"]}_{d["slug"]}'
    outdir = os.path.join(REPO, "posts", name); os.makedirs(outdir, exist_ok=True)
    subprocess.run(["node", os.path.join(ROOT, "render.js"), out_html, outdir], check=True)
    for k in range(1, N + 1):
        os.replace(f"{outdir}/slide-{k}.png", f"{outdir}/{name}_{k:02d}.png")
    base = f"https://raw.githubusercontent.com/nextragency-ui/nextragency-social-posts/main/posts/{name}/"
    json.dump({"media": [f"{base}{name}_{k:02d}.png" for k in range(1, N + 1)], "alt": alts, "caption": d["caption"], "date": d.get("date")}, open(f"{outdir}/manifest.json", "w"), indent=1, ensure_ascii=False)
    print(name, N, "slides")
if __name__ == "__main__": main(sys.argv[1])
