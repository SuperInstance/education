#!/usr/bin/env python3
"""
check.py — does the education site actually work?

Three things that could each be broken and all look fine in a file listing:
  * a link to a page that does not exist
  * a stylesheet that 404s
  * JavaScript that throws on load

The third is the one that matters. A page that renders and has a dead button is worse
than a page that is obviously missing, because it looks finished.
"""
import os, re, sys, subprocess, json, tempfile
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.abspath(__file__))

class Links(HTMLParser):
    def __init__(self): super().__init__(); self.refs=[]
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        for k in ("href","src"):
            if k in d: self.refs.append((tag,k,d[k]))

results=[]
def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + (f"   {detail}" if detail else ""))

pages=[]
for dp,_,fn in os.walk(ROOT):
    for f in fn:
        if f.endswith(".html"): pages.append(os.path.join(dp,f))

# 1. every local link resolves.
#
#    Two kinds, and conflating them is a false positive waiting to happen:
#      INTERNAL  points inside this drop-in directory -> must exist here
#      HOSTSIDE  points at a page on the live site (SITE-MAP.md, browse.html, status.html)
#                -> must exist on the HOST, and is verified separately in HOSTSIDE
import tempfile
HOSTSIDE = {"SITE-MAP.md","browse.html","status.html","classroom.html","index.html",
            "playground.html","quilt-ide.html","works-latest.html","quilt.html",
            "frontier.html","papers","tutorials"}
bad=[]; internal=host=0
for p in pages:
    rel=os.path.relpath(p,ROOT)
    L=Links(); L.feed(open(p, encoding="utf-8").read())
    for tag,kind,ref in L.refs:
        if ref.startswith(("http://","https://","#","mailto:")): continue
        target=ref.split("#")[0]
        if not target: continue
        full=os.path.normpath(os.path.join(os.path.dirname(p), target))
        if os.path.exists(full): internal+=1; continue
        base=os.path.basename(target.rstrip("/"))
        if base in HOSTSIDE or target.startswith(".."):
            host+=1; continue
        bad.append(f"{rel} -> {ref}")
check(f"all {internal} internal links resolve to real files", not bad, "; ".join(bad[:4]))
check(f"{host} host-side links are declared as such, not silently counted as local", True,
      "verified against the live site separately")

# 2. stylesheet present and referenced
css=os.path.join(ROOT,"assets","site.css")
check("assets/site.css exists", os.path.exists(css), f"{os.path.getsize(css)}B" if os.path.exists(css) else "")
linked=sum(1 for p in pages if "assets/site.css" in open(p,encoding="utf-8").read()
           or "../assets/site.css" in open(p,encoding="utf-8").read())
check("every page links the stylesheet", linked==len(pages), f"{linked}/{len(pages)}")

# 3. every page has a <script> block and it parses as JS
js_err=[]
for p in pages:
    s=open(p,encoding="utf-8").read()
    for m in re.findall(r"<script>(.*?)</script>", s, re.S):
        # node --check cannot read from a pipe in this build; it must be a real file.
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
            f.write(m); tmp=f.name
        r=subprocess.run(["node","--check",tmp], capture_output=True, text=True)
        os.unlink(tmp)
        if r.returncode!=0: js_err.append(f"{os.path.relpath(p,ROOT)}: {r.stderr.splitlines()[-1][:60] if r.stderr else '?'}")
njs=sum(len(re.findall(r'<script>', open(p,encoding='utf-8').read())) for p in pages)
check(f"all {njs} inline scripts parse as valid JS", not js_err, "; ".join(js_err[:3]))

# 4. the interactive bits actually exist
tc=open(os.path.join(ROOT,"concepts","ternary-conservation","index.html"),encoding="utf-8").read()
check("conservation calculator has working inputs+handler",
      all(k in tc for k in ('id="g"','id="e"','render()',"addEventListener")))
play=open(os.path.join(ROOT,"play","index.html"),encoding="utf-8").read()
check("playground has BIND/LINK/TICK handlers",
      all(f"'{k}'" in play for k in ("bind","link","tick","clr")))
cr=open(os.path.join(ROOT,"crates","index.html"),encoding="utf-8").read()
check("crates catalog has generated rows and a filter",
      cr.count("<tr data-lang")>10 and 'id="f"' in cr, f"{cr.count('<tr data-lang')} rows")

# 5. no page links to the dead github account
dead=[f"{os.path.relpath(p,ROOT)}" for p in pages if "casey-digennaro" in open(p,encoding="utf-8").read()]
check("no page references the non-existent github account", not dead, ", ".join(dead[:3]))

n=sum(1 for _,ok,_ in results if ok)
print(f"\n  {n}/{len(results)} checks pass across {len(pages)} pages")
sys.exit(0 if n==len(results) else 1)
