# AI 日报网站：posts/YYYY-MM-DD.json → 静态网页（index.html + d/YYYY-MM-DD.html）
# 只放公开内容：新闻、对普通人和企业意味着什么、来源、可信度。抖音运营策略不放这里。
# 用法：python build.py        （定时任务每天写好 posts/*.json 后调用，再 git push，GitHub Pages 自动更新）
import os, json, glob, html
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = "AI 日报"
TAGLINE = "每天几条 AI 新闻，讲清楚对普通人和企业意味着什么"
WEEK = "一二三四五六日"
WEEK_EN = "MON TUE WED THU FRI SAT SUN".split()
CRED = {"官方": "官方发布", "报道": "媒体报道", "传闻": "传闻，未证实"}

# 科技艺术风：深色底 + 渐隐网格 + 光晕，渐变标题，等宽字体做编号和日期，可信度用发光小灯
CSS = """
:root{--bg:#07080d;--fg:#e9ecf5;--muted:#8a90a6;--line:rgba(140,160,255,.14);--card:rgba(18,21,34,.72);
--a1:#5b8cff;--a2:#b06bff;--a3:#3ee6c4;--glow:rgba(91,140,255,.22);--grid:rgba(120,140,220,.07)}
@media (prefers-color-scheme:light){:root:not([data-theme=dark]){--bg:#f4f5fa;--fg:#12131a;--muted:#5d6275;
--line:rgba(40,60,160,.14);--card:rgba(255,255,255,.82);--a1:#2f5dff;--a2:#8a3dff;--a3:#0aa889;--glow:rgba(47,93,255,.12);--grid:rgba(40,60,160,.06)}}
*{box-sizing:border-box}
html{background:var(--bg)}
body{margin:0;color:var(--fg);font:17px/1.8 -apple-system,"PingFang SC","Microsoft YaHei",sans-serif;min-height:100vh;
background:radial-gradient(900px 500px at 85% -10%,var(--glow),transparent 60%),radial-gradient(700px 420px at -10% 30%,rgba(176,107,255,.10),transparent 60%),var(--bg)}
body:before{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;
background-image:linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px);
background-size:44px 44px;-webkit-mask-image:linear-gradient(180deg,#000,transparent 70%);mask-image:linear-gradient(180deg,#000,transparent 70%)}
main{position:relative;z-index:1;max-width:760px;margin:0 auto;padding:36px 16px 72px}
a{color:var(--a1);text-decoration:none}a:hover{text-decoration:underline}
.mono{font-family:"JetBrains Mono","SF Mono",Consolas,"Cascadia Mono",monospace;letter-spacing:.04em}
header.site{display:flex;align-items:center;justify-content:space-between;gap:12px;padding-bottom:16px;margin-bottom:34px;position:relative}
header.site:after{content:"";position:absolute;left:0;right:0;bottom:0;height:1px;
background:linear-gradient(90deg,transparent,var(--a1),var(--a2),var(--a3),transparent);background-size:200% 100%;animation:flow 8s linear infinite}
@keyframes flow{to{background-position:-200% 0}}
.brand{display:flex;align-items:center;gap:10px;color:var(--fg);font-weight:800;font-size:19px}
.brand:hover{text-decoration:none}
.dot{width:10px;height:10px;border-radius:50%;background:var(--a3);box-shadow:0 0 12px var(--a3);animation:pulse 2.4s ease-in-out infinite}
@keyframes pulse{50%{opacity:.35}}
header.site .tag{color:var(--muted);font-size:12px}
.kicker{color:var(--a3);font-size:13px;margin-bottom:10px}
h1{font-size:clamp(28px,6vw,42px);line-height:1.25;margin:0 0 14px;font-weight:900;letter-spacing:-.01em;
background:linear-gradient(100deg,var(--fg) 30%,var(--a1) 70%,var(--a2));-webkit-background-clip:text;background-clip:text;color:transparent}
.meta{color:var(--muted);font-size:13px;margin-bottom:22px}
.intro{margin:0 0 30px;font-size:18px;opacity:.88;border-left:2px solid var(--a2);padding-left:14px}
article.item{position:relative;background:var(--card);-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);border:1px solid var(--line);border-radius:16px;
padding:22px 22px 14px;margin:0 0 18px;transition:border-color .25s,transform .25s,box-shadow .25s}
article.item:hover{border-color:rgba(91,140,255,.45);transform:translateY(-2px);box-shadow:0 10px 40px -12px var(--glow)}
.num{position:absolute;right:18px;top:12px;font-size:34px;font-weight:800;color:transparent;-webkit-text-stroke:1px var(--muted);opacity:.45;line-height:1}
article.item h2{font-size:20px;line-height:1.45;margin:0 52px 12px 0}
.row{display:grid;grid-template-columns:88px 1fr;gap:10px;margin:0 0 10px}
.label{font-size:11px;color:var(--a1);padding-top:5px;text-transform:uppercase}
.label b{display:block;color:var(--muted);font-weight:400;font-size:12px;text-transform:none;letter-spacing:0}
.row p{margin:0}
.src{display:flex;flex-wrap:wrap;align-items:center;gap:6px 14px;font-size:13px;color:var(--muted);border-top:1px dashed var(--line);padding-top:10px;margin-top:6px}
.cred{display:inline-flex;align-items:center;gap:6px}
.cred i{width:7px;height:7px;border-radius:50%;display:inline-block;background:var(--muted)}
.c-官方 i{background:#3ee6c4;box-shadow:0 0 8px #3ee6c4}.c-报道 i{background:#ffc94a;box-shadow:0 0 8px #ffc94a}.c-传闻 i{background:#ff5d7a;box-shadow:0 0 8px #ff5d7a}
h2.sec{font-size:13px;color:var(--muted);margin:48px 0 8px;font-weight:600}
ul.archive{list-style:none;padding:0;margin:0}
ul.archive li{display:flex;gap:14px;border-bottom:1px solid var(--line);padding:14px 0}
ul.archive .d{color:var(--muted);font-size:13px;white-space:nowrap;padding-top:2px}
nav.days{display:flex;align-items:center;justify-content:center;gap:10px;margin:-14px 0 30px;flex-wrap:wrap}
nav.days a,nav.days span.off{font-size:13px;padding:6px 12px;border:1px solid var(--line);border-radius:999px;background:var(--card);color:var(--fg)}
nav.days a:hover{border-color:var(--a1);text-decoration:none}
nav.days span.off{opacity:.35}
nav.days input{font-size:13px;font-family:inherit;padding:5px 10px;border:1px solid var(--line);border-radius:999px;background:var(--card);color:var(--fg);color-scheme:dark light}
.nodate{color:var(--muted);font-size:13px;text-align:center;margin:-20px 0 24px;min-height:1em}
footer{margin-top:48px;color:var(--muted);font-size:12px;padding-top:16px;border-top:1px solid var(--line)}
@media (max-width:520px){.row{grid-template-columns:1fr;gap:2px}.label{padding-top:0}.num{font-size:28px}}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
"""


def page(title, body, depth=0):
    up = "../" * depth
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title>
<meta name="description" content="{TAGLINE}"><meta name="theme-color" content="#07080d"><link rel="stylesheet" href="{up}style.css"></head>
<body><main><header class="site"><a class="brand" href="{up}index.html"><span class="dot"></span>{SITE}</a><span class="tag mono">DAILY · AI SIGNAL</span></header>
{body}
<footer>{TAGLINE}。每条都附来源；「传闻」表示还没有官方确认。内容由 AI 辅助整理，人工把关。</footer></main></body></html>"""


def label_date(d):
    y, m, dd = map(int, d.split("-"))
    return f"{m} 月 {dd} 日 · 周{WEEK[date(y, m, dd).weekday()]}"


def stamp(d):
    y, m, dd = map(int, d.split("-"))
    return f"{y}.{m:02d}.{dd:02d} / {WEEK_EN[date(y, m, dd).weekday()]}"


def day_nav(cur, dates, depth):
    """dates：已有日报的日期，新到旧。前一天/后一天跳到相邻的那期，日期框可选任意一天"""
    up = "../" * depth
    i = dates.index(cur)
    prev_d = dates[i + 1] if i + 1 < len(dates) else None
    next_d = dates[i - 1] if i > 0 else None
    link = lambda d: f"{up}index.html" if d == dates[0] else f"{up}d/{d}.html"
    prev_html = f"<a href='{link(prev_d)}'>‹ 前一天</a>" if prev_d else "<span class='off'>‹ 前一天</span>"
    next_html = f"<a href='{link(next_d)}'>后一天 ›</a>" if next_d else "<span class='off'>后一天 ›</span>"
    return f"""<nav class="days">{prev_html}<input type="date" id="pick" value="{cur}" min="{dates[-1]}" max="{dates[0]}" aria-label="选择日期">{next_html}</nav>
<div class="nodate" id="nodate"></div>
<script>(function(){{var D={json.dumps(dates)},up="{up}",el=document.getElementById("pick");
el.addEventListener("change",function(){{var d=el.value;if(!d)return;
if(D.indexOf(d)<0){{document.getElementById("nodate").textContent=d+" 没有日报";el.value="{cur}";return}}
location.href=d===D[0]?up+"index.html":up+"d/"+d+".html"}})}})();</script>"""


def day_body(p):
    E = html.escape
    out = [f"<div class='kicker mono'>{stamp(p['date'])} · {len(p['items'])} SIGNALS</div>",
           f"<h1>{E(p['title'])}</h1>",
           f"<div class='meta'>{label_date(p['date'])}" + (f" · {E(p['updated'])} 更新" if p.get("updated") else "") + "</div>"]
    if p.get("intro"):
        out.append(f"<p class='intro'>{E(p['intro'])}</p>")
    for n, it in enumerate(p["items"], 1):
        src = " · ".join(f"<a href='{E(s['url'])}' rel='noopener' target='_blank'>{E(s['name'])}</a>" for s in it.get("sources", []))
        c = it.get("credibility", "")
        out.append(f"""<article class="item"><span class="num mono">{n:02d}</span><h2>{E(it['title'])}</h2>
<div class="row"><span class="label mono">What<b>发生了什么</b></span><p>{E(it['what'])}</p></div>
<div class="row"><span class="label mono">So what<b>意味着什么</b></span><p>{E(it['meaning'])}</p></div>
<div class="src"><span class="cred c-{E(c)}"><i></i>{E(CRED.get(c, c))}</span>{'<span>来源：' + src + '</span>' if src else ''}</div></article>""")
    return "\n".join(out)


def main():
    posts = []
    for f in sorted(glob.glob(os.path.join(HERE, "posts", "*.json")), reverse=True):
        posts.append(json.load(open(f, encoding="utf-8")))
    os.makedirs(os.path.join(HERE, "d"), exist_ok=True)
    open(os.path.join(HERE, "style.css"), "w", encoding="utf-8").write(CSS)
    dates = [p["date"] for p in posts]
    for p in posts:
        open(os.path.join(HERE, "d", p["date"] + ".html"), "w", encoding="utf-8").write(
            page(f"{p['title']} · {SITE}", day_nav(p["date"], dates, 1) + day_body(p), 1))
    if posts:
        archive = "".join(f"<li><span class='d mono'>{stamp(p['date'])}</span><a href='d/{p['date']}.html'>{html.escape(p['title'])}</a></li>"
                          for p in posts[1:])
        body = day_nav(dates[0], dates, 0) + day_body(posts[0]) + (f"<h2 class='sec mono'>ARCHIVE · 往期</h2><ul class='archive'>{archive}</ul>" if archive else "")
        open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(page(SITE, body))
    print(f"生成 {len(posts)} 天")


if __name__ == "__main__":
    main()
