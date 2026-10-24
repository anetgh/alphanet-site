"""Report old-site text that does not appear on the mapped new page."""
import html, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B

def norm(s):
    s = html.unescape(s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace(" ", " ").replace("’", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip().lower()

mapping = {}
for old, new in B.OLD_TO_NEW.items():
    if old and "/" not in old or old.count("/") == 1:
        mapping[old.replace("/", "__")] = new
for k in B.INDUSTRY_OLD.values():
    pass
mapping.update({"life-sciences-and-healthcare": "industries/healthcare-and-insurance/", "home": None})
total_missing = 0
ignore = {"btn", "img", "logos", "kicker"}
for old, new in sorted(mapping.items()):
    if old not in B.OLD or new is None or new.startswith("http"):
        continue
    path = os.path.join(B.ROOT, new, "index.html")
    if not os.path.exists(path):
        print("NO PAGE", old, new); continue
    page = norm(open(path, encoding="utf-8").read())
    miss = []
    def chk(t):
        t = norm(t)
        if t and len(t) > 3 and t not in page:
            miss.append(t[:90])
    for b in B.OLD[old]["blocks"]:
        t = b["t"]
        if t in ignore: continue
        if t in ("p", "h", "quote"): chk(b["x"])
        elif t == "box": chk(b["title"]); chk(b["desc"])
        elif t == "faq": chk(b["q"]); chk(b["a"])
        elif t == "stat": chk(b["x"])
        elif t == "ul": [chk(i) for i in b["items"]]
    if miss:
        total_missing += len(miss)
        print(f"== {old} -> {new}: {len(miss)} missing")
        for m in miss[:8]: print("   -", m)
print("TOTAL MISSING", total_missing)
