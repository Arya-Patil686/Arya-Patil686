"""Render assets/stats.svg from live GitHub data, in the same pixel style as the
rest of the profile. Run by .github/workflows/stats.yml on a daily schedule.

Needs a token in GH_TOKEN or GITHUB_TOKEN (the contribution calendar is only
available through the GraphQL API, which requires authentication)."""
import json, os, sys, shutil, subprocess, urllib.request, datetime, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_assets import (Canvas, starfield, BG, GREEN, GREEN_D, PINK, CYAN,
                        YELLOW, ORANGE, LILAC, WHITE, px)
from pixfont import text_width

USER  = os.environ.get("GH_USER", "Arya-Patil686")
LC_USER = os.environ.get("LEETCODE_USER", "_arya__")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
OUT   = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")


GH = shutil.which("gh")  # present on Actions runners and most dev machines;
                         # it carries its own TLS trust store and auth


def _gh(args, stdin=None):
    r = subprocess.run([GH, "api", *args], input=stdin, capture_output=True,
                       text=True, timeout=60)
    if r.returncode:
        raise RuntimeError(r.stderr.strip()[:300])
    return json.loads(r.stdout)


def api(url):
    if GH:
        return _gh([url])
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": USER,
        **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def graphql(query, variables):
    if GH:
        args = ["graphql", "-f", f"query={query}"]
        for k, v in variables.items():
            args += ["-f", f"{k}={v}"]
        return _gh(args)["data"]
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=body, headers={
        "Authorization": f"Bearer {TOKEN}", "User-Agent": USER,
        "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["data"]


def leetcode():
    """Solved counts from LeetCode's public GraphQL endpoint. Returns None on any
    failure — the DSA panel is simply omitted rather than breaking the card."""
    q = ("query($u:String!){matchedUser(username:$u){submitStatsGlobal"
         "{acSubmissionNum{difficulty count}}}}")
    payload = json.dumps({"query": q, "variables": {"u": LC_USER}})
    try:
        r = subprocess.run(["curl", "-sS", "--max-time", "25", "-X", "POST",
                            "https://leetcode.com/graphql",
                            "-H", "Content-Type: application/json",
                            "-H", f"Referer: https://leetcode.com/u/{LC_USER}/",
                            "-A", "Mozilla/5.0", "-d", payload],
                           capture_output=True, text=True, timeout=40)
        d = json.loads(r.stdout)["data"]["matchedUser"]["submitStatsGlobal"]["acSubmissionNum"]
        by = {x["difficulty"]: x["count"] for x in d}
        if not by.get("All"):
            return None
        return by
    except Exception as e:
        print(f"  leetcode unavailable: {e}", file=sys.stderr)
        return None


def collect():
    user = api(f"https://api.github.com/users/{USER}")
    repos, page = [], 1
    while True:
        batch = api(f"https://api.github.com/users/{USER}/repos?per_page=100&page={page}")
        repos += batch
        if len(batch) < 100:
            break
        page += 1
    own = [r for r in repos if not r["fork"]]
    stars = sum(r["stargazers_count"] for r in own)
    last_push = max((r["pushed_at"] for r in own), default="")
    since = user["created_at"][:4]

    langs = collections.Counter()
    for r in own:
        try:
            for name, size in api(r["languages_url"]).items():
                langs[name] += size
        except Exception:
            if r.get("language"):
                langs[r["language"]] += 1

    contribs = streak = longest = 0
    if TOKEN or GH:
        try:
            d = graphql("""query($login:String!){ user(login:$login){
                 contributionsCollection{ contributionCalendar{ totalContributions
                   weeks{ contributionDays{ date contributionCount }}}}}}""",
                        {"login": USER})
            cal = d["user"]["contributionsCollection"]["contributionCalendar"]
            contribs = cal["totalContributions"]
            days = [dd for w in cal["weeks"] for dd in w["contributionDays"]]
            days.sort(key=lambda x: x["date"])
            today = datetime.date.today().isoformat()
            run = 0
            for dd in days:
                run = run + 1 if dd["contributionCount"] > 0 else 0
                longest = max(longest, run)
            # current streak: walk back from today, tolerating an empty today
            run = 0
            for dd in reversed(days):
                if dd["date"] > today:
                    continue
                if dd["contributionCount"] > 0:
                    run += 1
                elif dd["date"] == today:
                    continue
                else:
                    break
            streak = run
        except Exception as e:
            print(f"  contribution calendar unavailable: {e}", file=sys.stderr)
    return {"lc": leetcode(),
            "repos": len(own), "stars": stars, "followers": user["followers"],
            "contribs": contribs, "streak": streak, "longest": longest,
            "since": since, "last_push": last_push, "n_langs": len(langs),
            "langs": langs.most_common(6), "total_lang": sum(langs.values())}


def panel(c, x, y, w, h, title, accent):
    c.rect(x, y, w, h, "#0a0a16")
    c.frame(x, y, w, h, "#242440", 1)
    c.rect(x, y, 2, h, accent)
    c.text(x + 6, y + 4, title, accent, 1)
    c.rects([(x + 6, y + 13, w - 12, 1)], "#242440")


def build(s):
    lc = s.get("lc")
    W, H = 300, (154 if lc else 102)
    c = Canvas(W, H)
    c.rect(0, 0, W, H, BG)
    starfield(c, 26, 5, 1, 1, W - 2, H - 2)

    panel(c, 2, 2, 128, 84, "STATS.SYS", GREEN)
    push = ""
    if s["last_push"]:
        d = datetime.datetime.strptime(s["last_push"][:10], "%Y-%m-%d")
        push = d.strftime("%d %b").upper()
    rows = [("PUBLIC REPOS",  f"{s['repos']}", WHITE),
            ("CONTRIBS / YR", f"{s['contribs']}", CYAN),
            ("BEST STREAK",   f"{s['longest']} DAYS", ORANGE),
            ("LANGUAGES",     f"{s['n_langs']}", GREEN),
            ("BUILDING SINCE", f"{s['since']}", WHITE),
            ("LAST PUSH",     push, PINK)]
    yy = 19
    for label, value, col in rows:
        c.text(8, yy, label, "#6f6f93", 1)
        vw = text_width(value, 1)
        c.text(124 - vw, yy, value, col, 1)
        yy += 11

    panel(c, 134, 2, 164, 84, "LANG.DAT", LILAC)
    cols = [GREEN, CYAN, PINK, YELLOW, ORANGE, LILAC]
    total = s["total_lang"] or 1
    yy = 19
    BAR_X, BAR_W = 202, 68
    for i, (name, size) in enumerate(s["langs"]):
        pct = size / total * 100
        c.text(140, yy, name.upper()[:10], WHITE, 1)
        c.rect(BAR_X, yy + 1, BAR_W, 5, "#1c1c30")
        fill = max(1, round(BAR_W * pct / 100))
        c.raw(f'<rect x="{px(BAR_X)}" y="{px(yy + 1)}" width="{px(fill)}" height="{px(5)}" '
              f'fill="{cols[i % 6]}">'
              f'<animate attributeName="width" values="0;{px(fill)}" dur="1.1s" '
              f'begin="{i * 0.12}s" fill="freeze"/></rect>')
        lab = f"{pct:.0f}%"
        c.text(294 - text_width(lab, 1), yy, lab, cols[i % 6], 1)
        yy += 11

    if lc:
        panel(c, 2, 90, 296, 48, "DSA.EXE", ORANGE)
        total = lc.get("All", 0)
        tw = text_width(f"{total} SOLVED ON LEETCODE", 1)
        c.text(294 - tw, 94, f"{total} SOLVED ON LEETCODE", "#6f6f93", 1)
        tiers = [("EASY", lc.get("Easy", 0), GREEN),
                 ("MEDIUM", lc.get("Medium", 0), YELLOW),
                 ("HARD", lc.get("Hard", 0), PINK)]
        peak = max((v for _, v, _ in tiers), default=1) or 1
        BX, BW = 78, 180
        yy = 107
        for i, (name, val, col) in enumerate(tiers):
            c.text(8, yy, name, WHITE, 1)
            c.rect(BX, yy + 1, BW, 5, "#1c1c30")
            fill = max(1, round(BW * val / peak))
            c.raw(f'<rect x="{px(BX)}" y="{px(yy + 1)}" width="{px(fill)}" '
                  f'height="{px(5)}" fill="{col}">'
                  f'<animate attributeName="width" values="0;{px(fill)}" dur="1.1s" '
                  f'begin="{i * 0.14}s" fill="freeze"/></rect>')
            c.text(BX + BW + 6, yy, str(val), col, 1)
            yy += 11

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("UPDATED %d %b %Y").upper()
    c.text(W - 4 - text_width(stamp, 1), H - 10, stamp, "#3d3d5c", 1)
    c.write("stats.svg")


if __name__ == "__main__":
    if not (TOKEN or GH):
        print("warning: no token and no gh CLI; contribution stats will read 0",
              file=sys.stderr)
    build(collect())
