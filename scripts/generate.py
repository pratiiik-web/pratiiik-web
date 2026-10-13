#!/usr/bin/env python3
"""Generate SVG assets for a GitHub profile README from config.json.

Outputs into assets/: terminal.svg, radar1.svg, radar2.svg, stats.svg
Then renders README.md from README.template.md.

Env: GITHUB_TOKEN (optional, enables live stats via the GitHub API).
"""
import json, math, os, sys, urllib.request
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "config.json").read_text())
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

BG, PANEL, BORDER = "#0d1117", "#0f1a2e", "#1f3a5f"
CYAN, GREEN, TEXT, MUTED, ACCENT = "#22d3ee", "#3fb950", "#e6edf3", "#7d8590", "#a78bfa"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"


# ---------- terminal card ----------
def terminal():
    rows = CFG["rows"]
    row_h, top = 26, 118
    h = top + len(rows) * row_h + 70
    w = 760
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{MONO}">',
           f'<rect width="{w}" height="{h}" rx="14" fill="{PANEL}" stroke="{BORDER}"/>',
           '<circle cx="28" cy="26" r="6" fill="#ff5f56"/><circle cx="50" cy="26" r="6" fill="#ffbd2e"/><circle cx="72" cy="26" r="6" fill="#27c93f"/>',
           f'<text x="{w/2}" y="30" fill="{MUTED}" font-size="12" text-anchor="middle">{escape(CFG["title"])}</text>',
           f'<line x1="0" y1="48" x2="{w}" y2="48" stroke="{BORDER}"/>',
           f'<text x="32" y="82" fill="{CYAN}" font-size="12" letter-spacing="2">SYSTEM.INFO</text>',
           f'<circle cx="{w-190}" cy="78" r="4" fill="#f85149"><animate attributeName="opacity" values="1;0.2;1" dur="1.6s" repeatCount="indefinite"/></circle>',
           f'<text x="{w-180}" y="82" fill="#f85149" font-size="11">LIVE</text>',
           f'<text x="{w-32}" y="82" fill="{CYAN}" font-size="12" text-anchor="end">{escape(CFG["tag"])}</text>',
           f'<line x1="24" y1="96" x2="{w-24}" y2="96" stroke="{BORDER}"/>']
    for i, (k, v) in enumerate(rows):
        y = top + i * row_h
        out.append(f'<text x="32" y="{y}" fill="{MUTED}" font-size="13">{escape(k)}</text>')
        out.append(f'<line x1="170" y1="{y-4}" x2="{w-300}" y2="{y-4}" stroke="{BORDER}" stroke-dasharray="1 5"/>')
        out.append(f'<text x="{w-32}" y="{y}" fill="{TEXT}" font-size="13" text-anchor="end">{escape(v)}</text>')
    fy = h - 24
    out.append(f'<line x1="24" y1="{fy-18}" x2="{w-24}" y2="{fy-18}" stroke="{BORDER}"/>')
    out.append(f'<circle cx="34" cy="{fy-3}" r="3" fill="{GREEN}"/>')
    out.append(f'<text x="44" y="{fy}" fill="{GREEN}" font-size="10">{escape(CFG["footer_left"])}</text>')
    out.append(f'<text x="{w-32}" y="{fy}" fill="{MUTED}" font-size="10" text-anchor="end">{escape(CFG["footer_right"])}</text>')
    out.append("</svg>")
    (ASSETS / "terminal.svg").write_text("\n".join(out))


# ---------- radar charts ----------
def radar(key, fname):
    d = CFG[key]
    axes = list(d["axes"].items())
    n = len(axes)
    W, H, cx, cy, R = 420, 380, 210, 200, 120
    def pt(i, r):
        a = -math.pi / 2 + 2 * math.pi * i / n
        return cx + r * math.cos(a), cy + r * math.sin(a)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}">',
           f'<rect width="{W}" height="{H}" fill="{BG}"/>',
           f'<text x="{W/2}" y="32" fill="{TEXT}" font-size="14" font-weight="bold" text-anchor="middle">{escape(d["title"])}</text>']
    for lvl in (0.25, 0.5, 0.75, 1.0):
        pts = " ".join("%.1f,%.1f" % pt(i, R * lvl) for i in range(n))
        out.append(f'<polygon points="{pts}" fill="none" stroke="#21262d"/>')
    for i in range(n):
        x, y = pt(i, R)
        out.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#21262d"/>')
    poly = " ".join("%.1f,%.1f" % pt(i, R * v / 100) for i, (_, v) in enumerate(axes))
    out.append(f'<polygon points="{poly}" fill="{ACCENT}" fill-opacity="0.22" stroke="{GREEN}" stroke-width="2"/>')
    for i, (name, v) in enumerate(axes):
        x, y = pt(i, R * v / 100)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{GREEN}"/>')
        lx, ly = pt(i, R + 26)
        anchor = "middle" if abs(lx - cx) < 8 else ("start" if lx > cx else "end")
        out.append(f'<text x="{lx:.1f}" y="{ly:.1f}" fill="{TEXT}" font-size="11" text-anchor="{anchor}">{escape(name)}</text>')
        out.append(f'<text x="{lx:.1f}" y="{ly+13:.1f}" fill="{MUTED}" font-size="10" text-anchor="{anchor}">{v}</text>')
    out.append("</svg>")
    (ASSETS / fname).write_text("\n".join(out))


# ---------- live stats ----------
def gh(path, token):
    req = urllib.request.Request("https://api.github.com" + path)
    req.add_header("Accept", "application/vnd.github+json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def gql(query, token):
    req = urllib.request.Request("https://api.github.com/graphql", data=json.dumps({"query": query}).encode())
    req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def fetch_stats():
    user = CFG["username"]
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    stats = dict(stars="–", repos="–", followers="–", contribs="–", cur="–", longest="–", langs=[])
    try:
        u = gh(f"/users/{user}", token)
        stats["repos"], stats["followers"] = u["public_repos"], u["followers"]
        repos, page = [], 1
        while True:
            batch = gh(f"/users/{user}/repos?per_page=100&page={page}&type=owner", token)
            repos += batch
            if len(batch) < 100:
                break
            page += 1
        stats["stars"] = sum(r["stargazers_count"] for r in repos)
        langs = {}
        for r in repos:
            if r["fork"]:
                continue
            try:
                for l, b in gh(f"/repos/{user}/{r['name']}/languages", token).items():
                    langs[l] = langs.get(l, 0) + b
            except Exception:
                pass
        total = sum(langs.values()) or 1
        stats["langs"] = [(l, b, 100 * b / total) for l, b in sorted(langs.items(), key=lambda x: -x[1])[:8]]
    except Exception as e:
        print("stats (REST) failed:", e, file=sys.stderr)
    if token:
        try:
            q = '{ user(login:"%s"){ contributionsCollection{ contributionCalendar{ totalContributions weeks{ contributionDays{ date contributionCount }}}}}}' % user
            cal = gql(q, token)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
            stats["contribs"] = cal["totalContributions"]
            days = [d["contributionCount"] for w in cal["weeks"] for d in w["contributionDays"]]
            best = run = 0
            for c in days:
                run = run + 1 if c else 0
                best = max(best, run)
            # today may still be empty; don't let that break the current streak
            tail = days[:-1] if days and days[-1] == 0 else days
            cur = 0
            for c in reversed(tail):
                if not c:
                    break
                cur += 1
            stats["cur"], stats["longest"] = cur, best
        except Exception as e:
            print("stats (GraphQL) failed:", e, file=sys.stderr)
    return stats


def fmt_bytes(b):
    return f"{b/1e6:.2f} MB" if b >= 1e6 else f"{b/1e3:.0f} kB"


LANG_COLORS = {"Python": "#3572A5", "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "Jupyter Notebook": "#DA5B0B",
               "HTML": "#e34c26", "CSS": "#663399", "Java": "#b07219", "C++": "#f34b7d", "C": "#555555",
               "SQL": "#e38c00", "Shell": "#89e051", "PLpgSQL": "#336790"}


def stats_svg():
    s = fetch_stats()
    W = 560
    langs = s["langs"]
    H = 250 + (len(langs) + 1) // 2 * 26
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}">',
           f'<rect width="{W}" height="{H}" fill="{BG}"/>',
           f'<rect x="10" y="10" width="{W-20}" height="150" rx="14" fill="none" stroke="#30363d"/>',
           f'<text x="32" y="40" fill="{ACCENT}" font-size="16" font-weight="bold">{escape(CFG["username"])}</text>',
           f'<text x="{W-32}" y="40" fill="{MUTED}" font-size="12" text-anchor="end">at a glance</text>',
           f'<line x1="32" y1="52" x2="{W-32}" y2="52" stroke="#30363d"/>']
    cells = [("stars", "Total stars"), ("repos", "Public repos"), ("followers", "Followers"),
             ("contribs", "Contributions (1y)"), ("cur", "Current streak"), ("longest", "Longest streak")]
    for i, (k, label) in enumerate(cells):
        x, y = 32 + (i % 3) * 170, 88 + (i // 3) * 52
        out.append(f'<text x="{x}" y="{y}" fill="{TEXT}" font-size="26" font-weight="bold">{s[k]}</text>')
        out.append(f'<text x="{x}" y="{y+16}" fill="{MUTED}" font-size="11">{label}</text>')
    if langs:
        out.append(f'<text x="{W/2}" y="190" fill="#388bfd" font-size="14" text-anchor="middle">Most used languages</text>')
        x0, bw, cur = 32, W - 64, 32
        for l, b, p in langs:
            seg = bw * p / 100
            out.append(f'<rect x="{cur:.1f}" y="202" width="{seg:.1f}" height="8" fill="{LANG_COLORS.get(l, "#8b949e")}"/>')
            cur += seg
        for i, (l, b, p) in enumerate(langs):
            col, row = i % 2, i // 2
            x, y = 32 + col * 260, 240 + row * 26
            out.append(f'<circle cx="{x+6}" cy="{y-4}" r="5" fill="{LANG_COLORS.get(l, "#8b949e")}"/>')
            out.append(f'<text x="{x+20}" y="{y}" fill="{MUTED}" font-size="12">{escape(l)}</text>')
            out.append(f'<text x="{x+240}" y="{y}" fill="{MUTED}" font-size="11" text-anchor="end">{p:.1f}%</text>')
    out.append("</svg>")
    (ASSETS / "stats.svg").write_text("\n".join(out))


# ---------- README ----------
def readme():
    tpl = (ROOT / "README.template.md").read_text()
    (ROOT / "README.md").write_text(tpl.replace("{{username}}", CFG["username"]))


if __name__ == "__main__":
    terminal()
    radar("radar1", "radar1.svg")
    radar("radar2", "radar2.svg")
    stats_svg()
    readme()
    print("generated:", ", ".join(sorted(p.name for p in ASSETS.iterdir())), "+ README.md")
