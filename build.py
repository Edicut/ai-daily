# AI 日报网站：posts/YYYY-MM-DD.json → 静态网页（index.html + d/YYYY-MM-DD.html）
# 只放公开内容：新闻、对普通人和企业意味着什么、来源、可信度。抖音运营策略不放这里。
# 用法：python build.py        （定时任务每天写好 posts/*.json 后调用，再 git push，GitHub Pages 自动更新）
import os, json, glob, html
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = "AI 日报"
TAGLINE = "每天几条 AI 新闻，讲清楚对普通人和企业意味着什么"
WEEK = "一二三四五六日"
CRED = {"官方": "官方发布", "报道": "媒体报道", "传闻": "传闻，未证实"}

CSS = """
:root{--bg:#fafaf7;--fg:#1d1d1b;--muted:#6b6b66;--line:#e6e4dc;--card:#fff;--accent:#1747c9;--tag:#eef2fd}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#141413;--fg:#ecebe6;--muted:#9d9c95;--line:#2d2d2a;--card:#1c1c1a;--accent:#7ea2ff;--tag:#1e2640}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.75 -apple-system,"PingFang SC","Microsoft YaHei",sans-serif}
main{max-width:720px;margin:0 auto;padding:28px 16px 64px}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
header.site{border-bottom:1px solid var(--line);padding-bottom:14px;margin-bottom:24px}
header.site .name{font-size:22px;font-weight:800;color:var(--fg)}
header.site p{margin:2px 0 0;color:var(--muted);font-size:14px}
h1{font-size:26px;line-height:1.35;margin:0 0 6px}
.meta{color:var(--muted);font-size:14px;margin-bottom:18px}
.intro{margin:0 0 22px}
article.item{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 18px 12px;margin:0 0 16px}
article.item h2{font-size:19px;line-height:1.45;margin:0 0 8px}
.label{display:inline-block;font-size:12px;font-weight:700;color:var(--accent);background:var(--tag);border-radius:6px;padding:1px 8px;margin-right:6px}
.item p{margin:6px 0 10px}
.src{font-size:14px;color:var(--muted)}
ul.archive{list-style:none;padding:0;margin:0}
ul.archive li{border-bottom:1px solid var(--line);padding:12px 0}
ul.archive .d{color:var(--muted);font-size:14px;margin-right:10px}
footer{margin-top:40px;color:var(--muted);font-size:13px;border-top:1px solid var(--line);padding-top:14px}
"""


def page(title, body, depth=0):
    up = "../" * depth
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title>
<meta name="description" content="{TAGLINE}"><link rel="stylesheet" href="{up}style.css"></head>
<body><main><header class="site"><a class="name" href="{up}index.html">{SITE}</a><p>{TAGLINE}</p></header>
{body}
<footer>每条都附来源；「传闻」表示还没有官方确认。内容由 AI 辅助整理，人工把关。</footer></main></body></html>"""


def label_date(d):
    y, m, dd = map(int, d.split("-"))
    return f"{m} 月 {dd} 日 · 周{WEEK[date(y, m, dd).weekday()]}"


def day_body(p):
    E = html.escape
    out = [f"<h1>{E(p['title'])}</h1>",
           f"<div class='meta'>{label_date(p['date'])}" + (f" · {E(p['updated'])} 更新" if p.get("updated") else "") + "</div>"]
    if p.get("intro"):
        out.append(f"<p class='intro'>{E(p['intro'])}</p>")
    for it in p["items"]:
        src = " · ".join(f"<a href='{E(s['url'])}' rel='noopener' target='_blank'>{E(s['name'])}</a>" for s in it.get("sources", []))
        out.append(f"""<article class="item"><h2>{E(it['title'])}</h2>
<p><span class="label">发生了什么</span>{E(it['what'])}</p>
<p><span class="label">意味着什么</span>{E(it['meaning'])}</p>
<p class="src">可信度：{E(CRED.get(it.get('credibility', ''), it.get('credibility', '')))}{' · 来源：' + src if src else ''}</p></article>""")
    return "\n".join(out)


def main():
    posts = []
    for f in sorted(glob.glob(os.path.join(HERE, "posts", "*.json")), reverse=True):
        posts.append(json.load(open(f, encoding="utf-8")))
    os.makedirs(os.path.join(HERE, "d"), exist_ok=True)
    open(os.path.join(HERE, "style.css"), "w", encoding="utf-8").write(CSS)
    for p in posts:
        open(os.path.join(HERE, "d", p["date"] + ".html"), "w", encoding="utf-8").write(
            page(f"{p['title']} · {SITE}", day_body(p), 1))
    if posts:
        archive = "".join(f"<li><span class='d'>{label_date(p['date'])}</span><a href='d/{p['date']}.html'>{html.escape(p['title'])}</a></li>"
                          for p in posts[1:])
        body = day_body(posts[0]) + (f"<h2 style='margin-top:36px'>往期</h2><ul class='archive'>{archive}</ul>" if archive else "")
        open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(page(SITE, body))
    print(f"生成 {len(posts)} 天")


if __name__ == "__main__":
    main()
