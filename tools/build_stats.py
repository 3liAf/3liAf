"""Renders sunset-themed stats cards from the GitHub API into assets/.

Self-hosted on purpose: the usual github-readme-stats / streak-stats images are
third-party servers that rate-limit, go down, and see every visit to your
profile. This runs in your own Actions runner and commits plain SVGs.

Run locally:  GH_TOKEN=<token> python tools/build_stats.py
In Actions:   GH_TOKEN comes from secrets.GITHUB_TOKEN
"""

import json
import os
import sys
import urllib.error
import urllib.request

LOGIN = os.environ.get("GH_LOGIN", "3liAf")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")

SUNSET = ["#ff4d8d", "#ff6a5e", "#ff7b4a", "#ff9a3c", "#ffb85c", "#ffd166"]
BG_DEEP, BG_DARK = "#1b1026", "#120a1a"
BORDER, TEXT, BRIGHT, MUTED = "#3d2547", "#c9a7c7", "#f3e9f7", "#8f7aa0"

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ASSETS = os.path.join(ROOT, "assets")

QUERY = """
query($login:String!){
  user(login:$login){
    name
    followers{totalCount}
    repositories(first:100, ownerAffiliations:OWNER, isFork:false){
      totalCount
      nodes{
        stargazerCount
        languages(first:8, orderBy:{field:SIZE,direction:DESC}){
          edges{ size node{ name } }
        }
      }
    }
    contributionsCollection{
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      contributionCalendar{ totalContributions }
    }
  }
}
"""

MONO = ("ui-monospace,'SFMono-Regular','JetBrains Mono','Cascadia Mono',"
        "Consolas,'Liberation Mono',Menlo,monospace")


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}",
                 "Content-Type": "application/json",
                 "User-Agent": f"{LOGIN}-profile-cards"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if "errors" in payload:
        raise RuntimeError(f"GitHub API returned errors: {payload['errors']}")
    return payload["data"]["user"]


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def defs(width, gradient_id="sunset"):
    stops = "".join(
        f'<stop offset="{i * 100 // (len(SUNSET) - 1)}%" stop-color="{c}"/>'
        for i, c in enumerate(SUNSET)
    )
    return f'''<defs>
    <linearGradient id="{gradient_id}" x1="0" y1="0" x2="1" y2="0">{stops}</linearGradient>
    <linearGradient id="card" x1="0" y1="0" x2="0.5" y2="1">
      <stop offset="0%" stop-color="{BG_DEEP}"/><stop offset="100%" stop-color="{BG_DARK}"/>
    </linearGradient>
  </defs>'''


def card_shell(w, h, title, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{esc(title)}">
  {defs(w)}
  <rect width="{w}" height="{h}" rx="10" fill="url(#card)" stroke="{BORDER}"/>
  <rect x="18" y="20" width="4" height="15" rx="2" fill="url(#sunset)"/>
  <text x="30" y="33" font-family="{MONO}" font-size="14" font-weight="600" fill="{SUNSET[2]}">{esc(title)}</text>
  {body}
</svg>
'''


def build_stats_card(user):
    repos = user["repositories"]["nodes"]
    stars = sum(r["stargazerCount"] for r in repos)
    c = user["contributionsCollection"]

    rows = [
        ("Total Stars Earned", stars),
        ("Total Commits (year)", c["totalCommitContributions"]),
        ("Total PRs", c["totalPullRequestContributions"]),
        ("Total Issues", c["totalIssueContributions"]),
        ("Contributions (year)", c["contributionCalendar"]["totalContributions"]),
        ("Followers", user["followers"]["totalCount"]),
        ("Public Repos", user["repositories"]["totalCount"]),
    ]

    body, y = [], 62
    for i, (label, value) in enumerate(rows):
        col = SUNSET[i % len(SUNSET)]
        body.append(
            f'<circle cx="26" cy="{y - 4}" r="3.5" fill="{col}"/>'
            f'<text x="40" y="{y}" font-family="{MONO}" font-size="12.5" fill="{TEXT}">{esc(label)}</text>'
            f'<text x="412" y="{y}" font-family="{MONO}" font-size="12.5" font-weight="600" '
            f'fill="{BRIGHT}" text-anchor="end">{value:,}</text>'
        )
        y += 24

    return card_shell(430, y + 4, f"{LOGIN} :: stats", "\n  ".join(body))


def build_langs_card(user):
    totals = {}
    for r in user["repositories"]["nodes"]:
        for e in r["languages"]["edges"]:
            totals[e["node"]["name"]] = totals.get(e["node"]["name"], 0) + e["size"]

    top = sorted(totals.items(), key=lambda kv: -kv[1])[:6]
    if not top:
        return card_shell(330, 200, f"{LOGIN} :: languages",
                          f'<text x="26" y="70" font-family="{MONO}" font-size="12.5" '
                          f'fill="{MUTED}">no language data</text>')

    grand = sum(v for _, v in top)
    W, X0, BAR_W = 330, 22, 286

    # stacked proportion bar
    segs, x = [], X0
    for i, (_, size) in enumerate(top):
        seg = BAR_W * size / grand
        segs.append(f'<rect x="{x:.1f}" y="56" width="{seg:.1f}" height="10" '
                    f'fill="{SUNSET[i % len(SUNSET)]}"/>')
        x += seg

    body = [f'<clipPath id="barclip"><rect x="{X0}" y="56" width="{BAR_W}" height="10" rx="5"/></clipPath>',
            f'<g clip-path="url(#barclip)">{"".join(segs)}</g>']

    y = 92
    for i, (name, size) in enumerate(top):
        pct = 100.0 * size / grand
        col = SUNSET[i % len(SUNSET)]
        body.append(
            f'<rect x="{X0}" y="{y - 9}" width="9" height="9" rx="2" fill="{col}"/>'
            f'<text x="{X0 + 17}" y="{y}" font-family="{MONO}" font-size="12" fill="{TEXT}">{esc(name)}</text>'
            f'<text x="{X0 + BAR_W}" y="{y}" font-family="{MONO}" font-size="12" fill="{MUTED}" '
            f'text-anchor="end">{pct:.1f}%</text>'
        )
        y += 22

    return card_shell(W, y + 2, f"{LOGIN} :: languages", "\n  ".join(body))


def main():
    if not TOKEN:
        sys.exit("GH_TOKEN (or GITHUB_TOKEN) is not set -- cannot call the GitHub API.")
    os.makedirs(ASSETS, exist_ok=True)
    try:
        user = fetch()
    except urllib.error.HTTPError as e:
        sys.exit(f"GitHub API HTTP {e.code}: {e.read().decode(errors='replace')[:400]}")

    with open(os.path.join(ASSETS, "stats.svg"), "w", encoding="utf-8") as f:
        f.write(build_stats_card(user))
    with open(os.path.join(ASSETS, "langs.svg"), "w", encoding="utf-8") as f:
        f.write(build_langs_card(user))
    print("wrote assets/stats.svg and assets/langs.svg")


if __name__ == "__main__":
    main()
