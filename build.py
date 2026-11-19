#!/usr/bin/env python3
"""Build viniciusarre.dev: posts/*.md + assets/ -> dist/worker.js (one self-contained Worker).

Usage: python3 build.py
Front matter keys: title, slug, date (YYYY-MM-DD), series, summary, draft (true/false).
"""
import html, json, pathlib, re, datetime
import mistune

ROOT = pathlib.Path(__file__).parent
SITE = "https://viniciusarre.dev"
NAME = "Vinícius Arré"
HOST = "viniciusarre.dev"

md = mistune.create_markdown(plugins=["table", "strikethrough"], escape=False)

LOGO = r"""██╗   ██╗ █████╗
██║   ██║██╔══██╗
██║   ██║███████║
╚██╗ ██╔╝██╔══██║
 ╚████╔╝ ██║  ██║
  ╚═══╝  ╚═╝  ╚═╝"""


def parse(path):
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    meta = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip()
    meta["draft"] = meta.get("draft", "false").lower() == "true"
    meta["body"] = m.group(2)
    return meta


def esc(s):
    return html.escape(s, quote=True)


def page(*, title, path, body, ws="home", filename="~", ft="", up="/", noindex=False, desc=""):
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    tabs = "".join(
        f'<a href="{href}" class="{"on" if ws == key else ""}">{label}</a>'
        for key, href, label in [("home", "/", "1:~"), ("posts", "/#posts", "2:posts"), ("about", "/about", "3:about")]
    )
    return f"""<!doctype html>
<html lang="en" data-theme="tokyonight">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{robots}
<link rel="alternate" type="application/rss+xml" title="{esc(NAME)}" href="/rss.xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/app.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%231a1b26'/><text x='5' y='22' font-family='monospace' font-size='16' font-weight='700' fill='%237aa2f7'>&gt;_</text></svg>">
</head>
<body data-up="{up}">
<header class="bar">
  <nav class="ws">{tabs}</nav>
  <span class="spacer"></span>
  <span class="pill m hide-m" id="theme-pill">◐ tokyonight</span>
  <span class="pill g hide-m" id="uptime">up 0d</span>
  <span class="pill y" id="clock">--:--</span>
</header>
<main class="wm">
  <div class="win">
    <div class="titlebar"><span class="dots"><i></i><i></i><i></i></span><span class="t">vinicius@{HOST}: {esc(filename)}</span><span>zsh</span></div>
    <div class="buf">
{body}
    </div>
  </div>
</main>
<div class="status"><span class="mode" id="mode">NORMAL</span><span class="f">{esc(filename)}</span><span class="fill"></span><span class="ft">{esc(ft)}</span><span class="ft">utf-8</span><span class="pos" id="pos">Top</span></div>
<div class="cmdline"><span id="cmd-pfx"></span><input id="cmd" hidden autocomplete="off" autocapitalize="off" spellcheck="false" aria-label="command line"><span id="msg" class="msg"></span><button class="kbtn" id="kbtn" aria-label="open command line">:</button></div>
<div class="help" id="help"><div class="box">
<h3>:help keys</h3>
<table>
<tr><td>j / k</td><td>move down / up (scroll in posts)</td></tr>
<tr><td>gg / G</td><td>top / bottom</td></tr>
<tr><td>Ctrl-d / Ctrl-u</td><td>half page down / up</td></tr>
<tr><td>Enter / l</td><td>open post</td></tr>
<tr><td>h / -</td><td>back to the listing</td></tr>
<tr><td>/text</td><td>search posts · n / N next / prev</td></tr>
<tr><td>t</td><td>cycle colour scheme</td></tr>
<tr><td>:about :posts :rss</td><td>jump around</td></tr>
<tr><td>:e &lt;slug&gt;</td><td>open a post</td></tr>
<tr><td>:colo &lt;name&gt;</td><td>tokyonight · catppuccin · gruvbox · nord</td></tr>
<tr><td>:q</td><td>back · Esc closes this</td></tr>
</table></div></div>
<script src="/assets/app.js" defer></script>
</body>
</html>"""


def ps1(cmd, live=False):
    return f'<p class="ps1{" live" if live else ""}"><span class="u">vinicius</span>@<span class="h">{HOST}</span> <span class="p">~</span> ❯ <span class="c">{esc(cmd)}</span></p>'


def tildes(n=4):
    return "".join('<div class="tilde">~</div>' for _ in range(n))


def build():
    posts = sorted((parse(p) for p in (ROOT / "posts").glob("*.md")), key=lambda p: p["date"], reverse=True)
    any_draft = any(p["draft"] for p in posts)
    routes = {}

    # ── home ──
    swatch = "".join(f'<span style="background:var(--{c})"></span>' for c in ["red", "green", "yellow", "blue", "magenta", "cyan", "orange", "fg"])
    info = f"""<pre class="info"><span class="hl">vinicius</span>@<span class="hl">{HOST}</span>
──────────────────────────
<span class="k">role</span>     software engineer · AI systems
<span class="k">focus</span>    evals · small models · decision records
<span class="k">research</span> NLP, CEFR difficulty classification
<span class="k">edu</span>      MBA AI &amp; Big Data, ICMC-USP
<span class="k">motto</span>    measure before you ship
<span class="k">posts</span>    {len(posts)}
<span class="k">keys</span>     press <span class="hl">?</span> · or tap <span class="hl">:</span>
<div class="swatch">{swatch}</div></pre>"""
    rows = []
    for p in posts:
        d = p["date"]
        badge = ' <span class="draft">DRAFT</span>' if p["draft"] else ""
        rows.append(
            f'<div class="row"><span class="perm">-rw-r--r--</span><span class="d">{d}</span>'
            f'<span><a href="/posts/{p["slug"]}">{esc(p["slug"])}.md</a>{badge} <span class="tag">[{esc(p["series"])}]</span>'
            f'<span class="s">{esc(p["summary"])}</span></span></div>'
        )
    home_body = (
        ps1("fetch")
        + f'<div class="fetch"><pre class="logo">{LOGO}</pre>{info}</div>'
        + '<div id="posts"></div>'
        + ps1("ls -lt posts/")
        + f'<div class="ls">{"".join(rows)}</div>'
        + ps1("", live=True)
        + tildes(3)
    )
    routes["/"] = page(title=f"{NAME} — measure before you ship", path="/", body=home_body, ws="home",
                       filename="~/posts", ft="dir", noindex=any_draft,
                       desc="Engineering notes on evals, small models and decision records.")

    # ── posts ──
    for i, p in enumerate(posts):
        banner = '<div class="banner">⚠ DRAFT: not final yet. Numbers and wording may change.</div>' if p["draft"] else ""
        nxt = posts[i - 1] if i > 0 else None
        prv = posts[i + 1] if i + 1 < len(posts) else None
        nav = '<p class="meta">'
        if prv: nav += f'← <a href="/posts/{prv["slug"]}">{esc(prv["slug"])}.md</a>&nbsp;&nbsp;'
        if nxt: nav += f'<a href="/posts/{nxt["slug"]}">{esc(nxt["slug"])}.md</a> →'
        nav += "</p>"
        body = (
            ps1(f"cat posts/{p['slug']}.md")
            + banner
            + f'<article><h1>{esc(p["title"])}</h1><p class="meta">{p["date"]} · <span class="tag">[{esc(p["series"])}]</span> · {max(1, round(len(p["body"].split()) / 220))} min read</p>'
            + md(p["body"])
            + "</article><br>"
            + nav
            + ps1("cd ..", live=True)
            + tildes(3)
        )
        routes[f"/posts/{p['slug']}"] = page(title=f"{p['title']} — {NAME}", path=f"/posts/{p['slug']}", body=body,
                                             ws="posts", filename=f"~/posts/{p['slug']}.md", ft="markdown",
                                             noindex=p["draft"], desc=p["summary"])

    # ── about ──
    about = f"""{ps1("cat about.md")}
<article>
<h1>about</h1>
<p>I'm <strong>{esc(NAME)}</strong>, a software engineer based in Brazil. I build AI features and the evals that decide whether they ship.</p>
<h2>what I do</h2>
<ul>
<li>Evals and quality gates for LLM-powered features</li>
<li>Fine-tuning and measuring small language models</li>
<li>Writing the decision records behind system design choices</li>
</ul>
<h2>research</h2>
<p>MBA in AI &amp; Big Data at ICMC-USP. My monograph trained a RoBERTa model to predict the CEFR level of English sentences. Read about it in <a href="/posts/roberta-vs-local-llm">roberta-vs-local-llm.md</a>.</p>
<h2>contact</h2>
<pre><code>$ finger vinicius
Login: vinicius            Name: {esc(NAME)}
Plan:  measure before you ship
Mail:  (coming soon)</code></pre>
</article>
{ps1("", live=True)}{tildes(3)}"""
    routes["/about"] = page(title=f"about — {NAME}", path="/about", body=about, ws="about",
                            filename="~/about.md", ft="markdown", noindex=any_draft, desc=f"About {NAME}.")

    # ── 404 ──
    nf = f"""{ps1("cd $REQUEST_PATH")}
<pre class="info"><span style="color:var(--red)">zsh: no such file or directory</span>

try  <a href="/">cd ~</a>  or press <span class="hl">:</span> and type <span class="hl">help</span></pre>
{ps1("", live=True)}{tildes(6)}"""
    not_found = page(title=f"404 — {NAME}", path="/404", body=nf, filename="E37: No such file", ft="", noindex=True)

    # ── rss ──
    items = "".join(
        f"<item><title>{esc(p['title'])}</title><link>{SITE}/posts/{p['slug']}</link><guid>{SITE}/posts/{p['slug']}</guid>"
        f"<pubDate>{datetime.datetime.strptime(p['date'], '%Y-%m-%d').strftime('%a, %d %b %Y 12:00:00 +0000')}</pubDate>"
        f"<description>{esc(p['summary'])}</description></item>"
        for p in posts
    )
    rss = (f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{esc(NAME)}</title>'
           f"<link>{SITE}</link><description>Measure before you ship.</description>{items}</channel></rss>")

    robots = "User-agent: *\nDisallow: /\n" if any_draft else f"User-agent: *\nAllow: /\nSitemap: {SITE}/rss.xml\n"

    files = {path: ("text/html; charset=utf-8", body) for path, body in routes.items()}
    files["/rss.xml"] = ("application/rss+xml; charset=utf-8", rss)
    files["/robots.txt"] = ("text/plain; charset=utf-8", robots)
    files["/assets/app.css"] = ("text/css; charset=utf-8", (ROOT / "assets/app.css").read_text(encoding="utf-8"))
    files["/assets/app.js"] = ("text/javascript; charset=utf-8",
                               f"window.__POSTS__={json.dumps([p['slug'] for p in posts])};\n" + (ROOT / "assets/app.js").read_text(encoding="utf-8"))

    worker = f"""// Generated by build.py — do not edit by hand.
const FILES = {json.dumps(files, ensure_ascii=False)};
const NOT_FOUND = {json.dumps(not_found, ensure_ascii=False)};
const SEC = {{
  "x-content-type-options": "nosniff",
  "referrer-policy": "strict-origin-when-cross-origin",
  "x-frame-options": "DENY",
}};
export default {{
  async fetch(request) {{
    const url = new URL(request.url);
    if (url.hostname.startsWith("www.")) return Response.redirect("https://{HOST}" + url.pathname, 301);
    let p = url.pathname.replace(/\\/+$/, "") || "/";
    p = p.replace(/\\.html$/, "").replace(/\\.md$/, "");
    const hit = FILES[p];
    if (!hit) return new Response(NOT_FOUND, {{ status: 404, headers: {{ "content-type": "text/html; charset=utf-8", ...SEC }} }});
    const [type, body] = hit;
    const cache = p.startsWith("/assets/") ? "public, max-age=3600" : "public, max-age=300";
    return new Response(body, {{ headers: {{ "content-type": type, "cache-control": cache, ...SEC }} }});
  }},
}};
"""
    out = ROOT / "dist"
    out.mkdir(exist_ok=True)
    (out / "worker.js").write_text(worker, encoding="utf-8")
    for path, body in routes.items():  # local preview copies
        f = out / "preview" / (path.strip("/") or "index")
        f.parent.mkdir(parents=True, exist_ok=True)
        f.with_suffix(".html").write_text(body, encoding="utf-8")
    print(f"built {len(files)} routes, {len(posts)} posts ({'drafts present' if any_draft else 'no drafts'}) -> dist/worker.js "
          f"({(out / 'worker.js').stat().st_size // 1024} KB)")


if __name__ == "__main__":
    build()
