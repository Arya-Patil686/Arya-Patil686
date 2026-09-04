#!/bin/zsh
# Renders README.md through GitHub's own markdown API, un-proxies camo URLs so
# remote badges load locally, then screenshots the result.
cd "$(dirname "$0")"
python3 - <<'PY'
import json, subprocess, re, binascii
md = open("README.md").read()
r = subprocess.run(["gh","api","--method","POST","/markdown","--input","-"],
                   input=json.dumps({"text": md, "mode": "markdown"}),
                   capture_output=True, text=True)
r.check_returncode()
html = r.stdout
def uncamo(m):
    try: return binascii.unhexlify(m.group(1)).decode().replace("&","&amp;")
    except Exception: return m.group(0)
html = re.sub(r"https://camo\.githubusercontent\.com/[0-9a-f]+/([0-9a-f]+)", uncamo, html)
css = """<style>
body{background:#0d1117;color:#e6edf3;font-family:-apple-system,Segoe UI,sans-serif;
 max-width:1012px;margin:0 auto;padding:32px 48px;line-height:1.6}
img{max-width:100%}a{color:#4493f8;text-decoration:none}
hr{border:0;border-top:1px solid #30363d;margin:24px 0}
h3{border-bottom:0;margin-top:22px}
blockquote{border-left:3px solid #30363d;margin:0;padding:0 1em;color:#9198a1}
table{border-collapse:collapse}td,th{border:1px solid #30363d;padding:6px 13px}
code{background:#151b23;padding:2px 6px;border-radius:6px;font-size:85%}
sub{color:#9198a1}
</style>"""
open("_preview.html","w").write(css + html)
PY
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu \
  --screenshot="_preview.png" --window-size=1100,${1:-5200} --hide-scrollbars \
  --virtual-time-budget=8000 "file://$PWD/_preview.html" >/dev/null 2>&1
echo "rendered _preview.png"
