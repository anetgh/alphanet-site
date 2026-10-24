#!/usr/bin/env python3
"""Static site generator for the Alpha Net website.

Run from the project root:  python3 _src/build.py
Reads copy from _src/newcontent.py (new Word-document copy) and
_src/data/old-site-pages.json (verbatim text from anetcorp.com), then writes
plain HTML pages that GitHub Pages can serve as-is.
"""
import html, json, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "_src")
sys.path.insert(0, SRC)
import newcontent as NC  # noqa: E402

OLD = json.load(open(os.path.join(SRC, "data", "old-site-pages.json"), encoding="utf-8"))
BG = json.load(open(os.path.join(SRC, "data", "old-site-backgrounds.json"), encoding="utf-8"))
IMGMAP = json.load(open(os.path.join(SRC, "data", "old-site-images.json"), encoding="utf-8"))

EMAIL = "info@anetcorp.com"
BRAND = "Alpha Net"
SITE_URL = ""  # set to the final https://… address to emit absolute canonical/OG URLs

E = lambda s: html.escape(str(s or ""), quote=True)


def nl2br(s):
    return "<br>".join(E(x) for x in str(s).split("\n"))


def oneline(s):
    return re.sub(r"\s*\n\s*", " ", str(s or "")).strip()


# --------------------------------------------------------------------------
# Icons (authored inline SVG, one stroke weight)
# --------------------------------------------------------------------------
I = {
    "arrow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 12h15"/><path d="M13 6l6 6-6 6"/></svg>',
    "arrow-ur": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17L17 7"/><path d="M8 7h9v9"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18"/></svg>',
    "close": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" aria-hidden="true"><path d="M5 5l14 14M19 5L5 19"/></svg>',
    "search": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" aria-hidden="true"><circle cx="10.5" cy="10.5" r="7"/><path d="M15.8 15.8L21 21"/></svg>',
    "chev-r": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg>',
    "chev-l": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3.5 6.5l8.5 6.5 8.5-6.5"/></svg>',
    "linkedin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M8 10.5V17M8 7.2v.1M12 17v-6.5M12 13.3c0-1.7 1-2.9 2.5-2.9S17 11.5 17 13.3V17"/></svg>',
    "facebook": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" aria-hidden="true"><path d="M14.5 21v-7.5h2.6l.4-3h-3V8.6c0-.9.3-1.6 1.6-1.6h1.6V4.3c-.3 0-1.3-.1-2.4-.1-2.4 0-4 1.4-4 4.1v2.2H8.6v3h2.7V21"/></svg>',
    "x": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" aria-hidden="true"><path d="M4 4l16 16M20 4L4 20"/></svg>',
    "instagram": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.2" cy="6.8" r=".6" fill="currentColor"/></svg>',
    "youtube": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" aria-hidden="true"><rect x="2.5" y="5.5" width="19" height="13" rx="4"/><path d="M10 9.3v5.4l4.6-2.7z"/></svg>',
    "pinterest": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M10.5 20.5l2-8.5M10.2 13.6c.5 1 1.4 1.5 2.4 1.5 2 0 3.4-1.8 3.4-4.1 0-2.4-1.9-4.1-4.3-4.1-2.7 0-4.4 1.9-4.4 4.1 0 1 .4 2 1.1 2.4"/></svg>',
    "pause": '<svg class="i-pause" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M9 6v12M15 6v12"/></svg>',
    "play": '<svg class="i-play" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true"><path d="M8 5.5v13l10-6.5z"/></svg>',
}

# Line illustrations for icon cards (72px, 1.2 stroke)
LINE = {
    "gear": '<svg viewBox="0 0 72 72" aria-hidden="true"><circle cx="36" cy="36" r="9"/><path d="M36 14v8M36 50v8M14 36h8M50 36h8M20.4 20.4l5.7 5.7M45.9 45.9l5.7 5.7M20.4 51.6l5.7-5.7M45.9 26.1l5.7-5.7"/><circle cx="36" cy="36" r="17"/></svg>',
    "chart": '<svg viewBox="0 0 72 72" aria-hidden="true"><path d="M12 58h48"/><path d="M18 50V38M30 50V28M42 50V34M54 50V18"/><path d="M16 30l12-10 12 8 16-14"/><circle cx="56" cy="14" r="2"/></svg>',
    "shield": '<svg viewBox="0 0 72 72" aria-hidden="true"><path d="M36 10l20 8v16c0 13-8.5 23-20 28-11.5-5-20-15-20-28V18z"/><path d="M27 36l7 7 12-14"/></svg>',
    "layers": '<svg viewBox="0 0 72 72" aria-hidden="true"><path d="M36 12l24 12-24 12-24-12z"/><path d="M12 36l24 12 24-12"/><path d="M12 48l24 12 24-12"/></svg>',
    "people": '<svg viewBox="0 0 72 72" aria-hidden="true"><circle cx="26" cy="26" r="8"/><circle cx="48" cy="28" r="6"/><path d="M12 56c0-9 6-15 14-15s14 6 14 15"/><path d="M40 44c2-2 5-3 8-3 7 0 12 5 12 13"/></svg>',
    "bolt": '<svg viewBox="0 0 72 72" aria-hidden="true"><path d="M40 10L18 40h16l-4 22 24-32H38z"/></svg>',
    "target": '<svg viewBox="0 0 72 72" aria-hidden="true"><circle cx="36" cy="36" r="22"/><circle cx="36" cy="36" r="13"/><circle cx="36" cy="36" r="4"/><path d="M52 20l8-8M54 12h6v6"/></svg>',
    "cloud": '<svg viewBox="0 0 72 72" aria-hidden="true"><path d="M22 52h30a11 11 0 0 0 1-22 15 15 0 0 0-29-3 12 12 0 0 0-2 25z"/><path d="M30 44l6-6 6 6M36 38v12"/></svg>',
    "code": '<svg viewBox="0 0 72 72" aria-hidden="true"><rect x="10" y="14" width="52" height="40" rx="4"/><path d="M10 24h52"/><path d="M28 34l-6 6 6 6M44 34l6 6-6 6M39 32l-6 16"/></svg>',
    "search": '<svg viewBox="0 0 72 72" aria-hidden="true"><circle cx="31" cy="31" r="17"/><path d="M43.5 43.5L60 60"/><path d="M24 31h14M31 24v14"/></svg>',
    "network": '<svg viewBox="0 0 72 72" aria-hidden="true"><circle cx="36" cy="16" r="6"/><circle cx="16" cy="54" r="6"/><circle cx="56" cy="54" r="6"/><circle cx="36" cy="40" r="5"/><path d="M36 22v13M32 43l-12 7M40 43l12 7"/></svg>',
    "bulb": '<svg viewBox="0 0 72 72" aria-hidden="true"><path d="M28 48c0-6-8-9-8-20a16 16 0 0 1 32 0c0 11-8 14-8 20z"/><path d="M29 54h14M31 60h10"/><path d="M36 4v4M14 12l3 3M58 12l-3 3"/></svg>',
    "doc": '<svg viewBox="0 0 72 72" aria-hidden="true"><path d="M20 10h24l12 12v40H20z"/><path d="M44 10v12h12"/><path d="M28 34h20M28 42h20M28 50h12"/></svg>',
    "clock": '<svg viewBox="0 0 72 72" aria-hidden="true"><circle cx="36" cy="36" r="24"/><path d="M36 22v14l10 6"/></svg>',
}
LINE_RULES = [
    (r"secur|complian|risk|privacy|protect|govern|trust|safe|fraud", "shield"),
    (r"data|analytic|insight|report|metric|measur|kpi|dashboard|roi|cost|value|result|perform", "chart"),
    (r"team|people|talent|employee|staff|collaborat|partner|customer|experience|human", "people"),
    (r"fast|speed|accelerat|agil|rapid|quick|real-time", "bolt"),
    (r"cloud|infra|migrat|hybrid|platform", "cloud"),
    (r"code|develop|engineer|software|stack|build|api|devops", "code"),
    (r"search|knowledge|discover|retriev|assess|audit", "search"),
    (r"integrat|network|connect|ecosystem|multi", "network"),
    (r"innovat|idea|strateg|vision|ai\b|intelligen", "bulb"),
    (r"document|policy|contract|form|record", "doc"),
    (r"support|24/7|monitor|continu|lifecycle|ongoing", "clock"),
    (r"scal|layer|architect|framework|foundation", "layers"),
    (r"goal|target|focus|outcome|precision|quality", "target"),
]


def line_icon(text, i=0):
    t = (text or "").lower()
    for pat, name in LINE_RULES:
        if re.search(pat, t):
            return LINE[name]
    return list(LINE.values())[i % len(LINE)]


# --------------------------------------------------------------------------
# Site map (navigation from the Word document; names from the spreadsheet)
# --------------------------------------------------------------------------
SOLUTIONS = [
    {
        "slug": "agentic-product-engineering", "name": "Agentic Product Engineering", "old": "product-engineering",
        "old_name": "Product Engineering", "art": "sphere-glow.svg",
        "children": [
            ("ai-product-strategy-and-architecture", "AI Product Strategy and Architecture", "product-engineering__software-development", "Software Development"),
            ("agentic-ai-and-multi-agent-systems", "Agentic AI and Multi-Agent Systems", "product-engineering__technology-and-product", "Forward Engineering"),
            ("enterprise-knowledge-and-rag-engineering", "Enterprise Knowledge and RAG Engineering", "product-engineering__product-lifecycle-management", "Product Lifecycle Management"),
            ("full-stack-ai-product-development", "Full-Stack AI Product Development", "accelerators__qa-automation", "Test Automation"),
            ("ai-evaluation-governance-and-operations", "AI Evaluation, Governance and Operations", None, None),
        ],
        "extras": [],
    },
    {
        "slug": "enterprise-ai-engineering", "name": "Enterprise AI Engineering", "old": "enterprise-engineering",
        "old_name": "Enterprise Engineering", "art": "rings-green.svg",
        "children": [
            ("agentic-ai-engineering", "Agentic AI Engineering", None, None),
            ("intelligent-workflow-automation", "Intelligent Workflow Automation", "enterprise-engineering__erp-implementation", "ERP Implementation"),
            ("enterprise-data-foundations", "Enterprise Data Foundations", "enterprise-engineering__integration-middleware", "Integration & Middleware"),
            ("secure-software-delivery-devsecops", "Secure Software Delivery (DevSecOps)", "enterprise-engineering__devsecops", "DevSecOps"),
            ("ai-application-modernization-and-engineering", "AI Application Modernization and Engineering", "enterprise-engineering__enterprise-application-support", "Enterprise Application Support"),
        ],
        "extras": [
            ("ai-strategy-and-roadmapping", "AI Strategy and Roadmapping", "enterprise-engineering__it-strategy-dev", "IT Strategy"),
            ("data-model-and-ai-observability", "Data, Model and AI Observability", "enterprise-engineering__data-observability", "Data Observability"),
        ],
    },
    {
        "slug": "ai-infra-and-cloud", "name": "AI Infra & Cloud", "old": "infrastructure-and-cloud",
        "old_name": "Infrastructure & Cloud", "art": "waves.svg",
        "children": [
            ("ai-platform-operations", "AI Platform Operations (AIOps, LLMOps and MLOps)", "infrastructure-and-cloud__cloud-transformation", "Cloud Transformation"),
            ("cloud-modernization-and-optimization", "Cloud Modernization and Optimization", "infrastructure-and-cloud__cloud-migration", "Cloud Migration"),
            ("cloud-adoption-and-migration", "Cloud Adoption and Migration", "infrastructure-and-cloud__multi-cloud-operations", "Multi-Cloud Operations"),
            ("hybrid-and-multi-cloud-management", "Hybrid and Multi-Cloud Management", "infrastructure-and-cloud__continuous-integration-and-continuous-deployment", "CI/CD"),
            ("cyber-defense-and-resilience", "Cyber Defense and Resilience", "infrastructure-and-cloud__cyber-security", "Cyber Security"),
        ],
        "extras": [
            ("network-and-connectivity-services", "Network and Connectivity Services", "infrastructure-and-cloud__network-operations", "Network Operations – Voice & Data"),
            ("digital-workplace-and-it-support", "Digital Workplace and IT Support", "infrastructure-and-cloud__it-helpdesk", "IT Helpdesk"),
        ],
    },
    {
        "slug": "ai-business-solutions", "name": "AI Business Solutions", "old": "business-services",
        "old_name": "Business Services", "art": "orbs-mint.svg",
        "children": [],
        # Business operations pages kept with their existing names (no rename given)
        "extras": [
            ("contact-center", "Contact Center", "business-services__contact-center-operations", "Contact Center"),
            ("content-moderation", "Content Moderation", "business-services__content-moderation", "Content Moderation"),
            ("hr-operations", "HR Operations", "business-services__hr-operations", "HR Operations"),
            ("gcc-hiring-ops", "GCC Hiring Ops", "business-services__global-capability-center-hiring-operations", "GCC Hiring Ops"),
            ("finance-and-accounting-operations", "Finance & Accounting Operations", "business-services__finance-accounting-operations", "Finance & Accounting Operations"),
            ("supply-chain-management-operations", "Supply Chain Management Operations", "business-services__supply-chain-management-operations", "Supply Chain Management Operations"),
            ("procurement-operations", "Procurement Operations", "business-services__procurement-operations", "Procurement Operations"),
            ("asset-management-and-field-services-operations", "Asset Management & Field Services Operations", "business-services__asset-management-field-services-operations", "Asset Management & Field Services Operations"),
        ],
    },
]
SOL_BY_SLUG = {s["slug"]: s for s in SOLUTIONS}
SUMMARY_KEY = {"agentic-product-engineering": "agentic-product-engineering", "enterprise-ai-engineering": "enterprise-ai-engineering",
               "ai-infra-and-cloud": "infrastructure-and-cloud", "ai-business-solutions": "business-services"}

ACCELS = [
    ("enterprise-rag-platform", "Enterprise RAG Platform"),
    ("data-preparation-agent", "Data Preparation Agent"),
    ("csv-excel-data-analysis-agent", "CSV & Excel Data Analysis Agent"),
    ("natural-language-sql-agent", "Natural Language SQL Agent"),
    ("semantic-search-assistant", "Semantic Search Assistant"),
    ("entity-extraction-agent", "Entity Extraction Agent"),
]
ACCEL_ART = {"enterprise-rag-platform": "rings-green.svg", "data-preparation-agent": "waves.svg", "csv-excel-data-analysis-agent": "orbs-mint.svg",
             "natural-language-sql-agent": "chevrons.svg", "semantic-search-assistant": "sphere-glow.svg", "entity-extraction-agent": "streaks.svg"}

INDUSTRY_OLD = {
    "healthcare-and-insurance": "life-sciences-and-healthcare",
    "life-sciences": "life-sciences-and-healthcare",
    "financial-services": "finance-and-banking",
    "manufacturing-and-supply-chain": "manufacturing",
    "retail-and-consumer": "retail-and-ecommerce",
    "technology-and-saas": "hi-tech",
}

def ind_img(k):
    if k == "life-sciences":
        boxes = [b for b in OLD["life-sciences-and-healthcare"]["blocks"] if b["t"] == "box" and b.get("img")]
        if boxes:
            return old_img(boxes[0]["img"])
    return bg_img(INDUSTRY_OLD[k])


COMPANY = [
    ("about/", "About"),
    ("our-approach/", "Our Approach"),
    ("insights/", "Insights & Resources"),
    ("case-studies/", "Case Studies"),
    ("careers/", "Careers"),
    ("contact/", "Contact Us"),
]

POSTS = [k for k, v in OLD.items() if v.get("kind") == "post"]
POSTS.sort(key=lambda k: OLD[k].get("published", ""), reverse=True)
CASES = [
    "case-studies__accelerating-fintech-innovation-with-scalable-qa-automation",
    "case-studies__empowering-digital-commerce-transformation-for-global-electronics-leader",
    "case-studies__powering-global-intercompany-excellence-for-a-semiconductor-leader",
    "case-studies__enhancing-e-commerce-support-for-a-global-cosmetics-leader-in-apac",
    "case-studies__powering-global-gaming-experiences-for-sony-interactive-entertainment",
    "case-studies__shot-with-geforce",
    "case-studies__streamlining-erp-access-management",
    "case-studies__manufacturing-erp-process-re-engineered",
]
CASE_IMG = {}
for b in OLD["case-studies"]["blocks"]:
    if b["t"] == "box" and b.get("img"):
        CASE_IMG[b["title"]] = b["img"]


def post_slug(k):
    return k.split("__", 1)[1]


def post_title(k):
    return re.sub(r"\s*[-–|]\s*Alpha Net Consulting\s*$", "", OLD[k]["title"]).strip()


def post_excerpt(k):
    t = post_title(k)
    bl = OLD["blogs"]["blocks"]
    for i, b in enumerate(bl):
        if b["t"] == "h" and b["x"].strip() == t and i + 1 < len(bl) and bl[i + 1]["t"] == "p":
            return bl[i + 1]["x"]
    paras = [b["x"] for b in OLD[k]["blocks"] if b["t"] == "p" and len(b["x"]) > 80]
    return paras[0] if paras else OLD[k].get("desc", "")


# Old URL -> new path (for buttons and in-text links)
OLD_TO_NEW = {"contact": "contact/", "case-studies": "case-studies/", "about-us": "about/", "how-we-engage": "our-approach/",
              "talent": "careers/", "blogs": "insights/", "our-vision": "about/our-vision/", "team-members": "about/leadership/",
              "privacy-policy": "privacy-policy/", "accelerators": "ai-accelerators/", "": ""}
for s in SOLUTIONS:
    OLD_TO_NEW[s["old"]] = s["slug"] + "/"
    for c in s["children"] + s["extras"]:
        if c[2]:
            OLD_TO_NEW[c[2].replace("__", "/")] = f'{s["slug"]}/{c[0]}/'
for k in CASES:
    OLD_TO_NEW[k.replace("__", "/")] = f"case-studies/{post_slug(k)}/"
for k in POSTS:
    OLD_TO_NEW[k.replace("__", "/")] = f"insights/{post_slug(k)}/"
for new, old in INDUSTRY_OLD.items():
    OLD_TO_NEW.setdefault(old, f"industries/{new}/")


def map_href(h):
    if not h:
        return "contact/"
    if h.startswith("mailto:"):
        return h
    p = re.sub(r"^https?://(www\.)?anetcorp\.com", "", h).strip("/")
    p = p.split("#")[0].split("?")[0]
    if p in OLD_TO_NEW:
        return OLD_TO_NEW[p]
    if h.startswith("http"):
        return h
    return "contact/"


# --------------------------------------------------------------------------
# Images
# --------------------------------------------------------------------------
def old_img(src):
    """Local path (root-relative) for an image that came from the old site."""
    if not src:
        return None
    base = src.split("?")[0].split("/")[-1]
    if base in IMGMAP:
        return "assets/img/anet/" + IMGMAP[base]
    return None


def bg_img(old_slug, idx=None):
    files = BG.get(old_slug) or []
    if not files:
        return None
    pick = None
    if idx is None:
        heads = [f for f in files if f.startswith("header")]
        pick = heads[0] if heads else files[-1]
    else:
        pick = files[min(idx, len(files) - 1)]
    return "assets/img/bg/" + pick


class Ctx:
    def __init__(self, path):
        self.path = path
        self.depth = path.count("/")
        self.rot = 0
        self.uid = 0

    def u(self, target):
        """Relative URL from this page to a root-relative target."""
        if target is None:
            return "#"
        if target.startswith(("http://", "https://", "mailto:", "tel:", "#")):
            return target
        pre = "../" * self.depth
        if target == "":
            return pre or "./"
        return pre + target

    def next_id(self, p="m"):
        self.uid += 1
        return f"{p}{self.uid}"


def media(ctx, src, alt="", cls="", eager=False, pos=None):
    if src and src.endswith(".svg") and "/" not in src:
        src = "assets/art/" + src
    if not src:
        src = "assets/art/rings-green.svg"
    style = f' style="object-position:{pos}"' if pos else ""
    load = "eager" if eager else "lazy"
    if src.startswith("assets/art/"):
        cls = (cls + " art").strip()
    c = f' class="{cls}"' if cls else ""
    a = E(alt) if src and not src.startswith("assets/art/") else ""
    return f'<img{c} src="{ctx.u(src)}" alt="{a}" loading="{load}" decoding="async"{style}>'


def btn(ctx, text, href, kind="", icon="arrow", extra=""):
    k = f" btn--{kind}" if kind else ""
    ext = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
    return f'<a class="btn{k}{extra}" href="{E(ctx.u(href))}"{ext}><span>{E(text)}</span>{I[icon]}</a>'


# --------------------------------------------------------------------------
# Chrome
# --------------------------------------------------------------------------
SEARCH_INDEX = []


def menu_html(ctx):
    sol_items, panels = [], []
    for s in SOLUTIONS:
        pid = "panel-" + s["slug"]
        sol_items.append(f'<button class="menu__item" type="button" data-panel="{pid}" aria-controls="{pid}" aria-expanded="false"><span>{E(s["name"])}</span>{I["chev-r"]}</button>')
        summ = NC.SOLUTION_SUMMARIES[SUMMARY_KEY[s["slug"]]]
        links = s["children"] if s["children"] else s["extras"]
        lis = "".join(f'<a href="{ctx.u(s["slug"] + "/" + c[0] + "/")}">{E(c[1])}</a>' for c in links)
        panels.append(f'''<section class="menu__panel" id="{pid}" aria-label="{E(s["name"])}">
<button class="menu__back" type="button">{I["chev-l"]}<span>Back</span></button>
<div class="menu__panel-head"><a href="{ctx.u(s["slug"] + "/")}">{E(s["name"])}</a><p>{E(summ["desc"])}</p></div>
<div class="menu__links">{lis}</div></section>''')
    # Accelerators
    sol_items.append(f'<button class="menu__item" type="button" data-panel="panel-acc" aria-controls="panel-acc" aria-expanded="false"><span>AI Accelerators</span>{I["chev-r"]}</button>')
    panels.append(f'''<section class="menu__panel" id="panel-acc" aria-label="AI Accelerators">
<button class="menu__back" type="button">{I["chev-l"]}<span>Back</span></button>
<div class="menu__panel-head"><a href="{ctx.u("ai-accelerators/")}">AI Accelerators</a><p>{E(NC.HOME["accelerators_body"])}</p></div>
<div class="menu__links">{"".join(f'<a href="{ctx.u("ai-accelerators/" + a + "/")}">{E(n)}</a>' for a, n in ACCELS)}</div></section>''')
    sol_items.append(f'<button class="menu__item" type="button" data-panel="panel-ind" aria-controls="panel-ind" aria-expanded="false"><span>Industries</span>{I["chev-r"]}</button>')
    panels.append(f'''<section class="menu__panel" id="panel-ind" aria-label="Industries">
<button class="menu__back" type="button">{I["chev-l"]}<span>Back</span></button>
<div class="menu__panel-head"><a href="{ctx.u("industries/")}">Industries</a><p>{E(oneline(OLD["about-us"]["blocks"][[i for i, b in enumerate(OLD["about-us"]["blocks"]) if b.get("x") == "Industries We Serve"][0] + 1]["x"]))}</p></div>
<div class="menu__links">{"".join(f'<a href="{ctx.u("industries/" + k + "/")}">{E(v[0] if k != "retail-and-consumer" else "Retail & Consumer")}</a>' for k, v in NC.INDUSTRIES.items())}</div></section>''')
    comp = "".join(f'<a class="menu__item" href="{ctx.u(p)}"><span>{E(n)}</span>{I["chev-r"]}</a>' for p, n in COMPANY)
    return f'''<div class="menu" id="site-menu" role="dialog" aria-modal="true" aria-label="Site menu" inert>
<div class="menu__top">
  <button class="burger" type="button" data-menu-close aria-label="Close site menu">{I["close"]}</button>
  <a class="logo" href="{ctx.u("")}" aria-label="{BRAND} home"><img src="{ctx.u("assets/img/logo-green.png")}" alt="{BRAND} — Real World Solutions" width="143" height="34"></a>
  <label class="menu__search">{I["search"]}<span class="sr-only">Search the site</span><input type="search" placeholder="Type to search" autocomplete="off"></label>
  <a class="header-cta" href="{ctx.u("contact/")}">Contact</a>
</div>
<div class="menu__results" aria-live="polite"></div>
<div class="menu__body">
  <nav class="menu__nav" aria-label="Main">
    <div class="menu__group"><span class="menu__group-title" role="heading" aria-level="2">Our Services</span>{"".join(sol_items)}</div>
    <div class="menu__group"><a class="menu__group-title" href="{ctx.u("insights/")}">Insights &amp; Resources</a></div>
    <div class="menu__group"><a class="menu__group-title" href="{ctx.u("case-studies/")}">Case Studies</a></div>
    <div class="menu__group"><span class="menu__group-title" role="heading" aria-level="2">Company</span>{comp}</div>
  </nav>
  <div class="menu__panels">{"".join(panels)}</div>
</div>
</div>'''


def header_html(ctx, subnav=None):
    sub = ""
    if subnav:
        label, links = subnav
        cur_attr = ' aria-current="page"'
        items = "".join(f'<a href="{ctx.u(h)}"{cur_attr if cur else ""}>{E(t)}</a>' for t, h, cur in links)
        sub = f'<nav class="pill subnav" aria-label="{E(label)}"><span class="subnav__label">{E(label)}:</span>{items}</nav>'
    return f'''<header class="site-header" data-scroll="up">
<div class="wrap">
  <div class="pill-left-group">
    <div class="pill pill-left">
      <button class="burger" type="button" data-menu-open aria-controls="site-menu" aria-expanded="false" aria-label="Open site menu">{I["menu"]}</button>
      <a class="logo" href="{ctx.u("")}" aria-label="{BRAND} home"><img src="{ctx.u("assets/img/logo-green.png")}" alt="{BRAND} — Real World Solutions" width="143" height="34"></a>
    </div>{sub}
  </div>
  <div class="pill pill-right">
    <button class="icon-btn" type="button" data-menu-open data-menu-search aria-controls="site-menu" aria-expanded="false" aria-label="Search the site">{I["search"]}</button>
    <a class="header-cta" href="{ctx.u("contact/")}">Contact</a>
  </div>
</div>
</header>'''


def footer_html(ctx, after_band=False):
    links = [("Careers", "careers/"), ("Insights", "insights/"), ("Case Studies", "case-studies/"), ("About", "about/"), ("Our Approach", "our-approach/")]
    socials = [("linkedin", "https://www.linkedin.com/company/alpha-net", "LinkedIn"), ("facebook", "https://www.facebook.com/anetcorp/", "Facebook"),
               ("x", "https://x.com/AlphaNetCorp", "X"), ("instagram", "https://www.instagram.com/alphanet_consulting/", "Instagram"),
               ("youtube", "https://www.youtube.com/@AlphaNetConsulting", "YouTube"), ("pinterest", "https://www.pinterest.com/alphanetconsulting/", "Pinterest")]
    contact_desc = OLD["contact"]["blocks"][1]["x"]
    return f'''<footer class="site-footer{" after-band" if after_band else ""}">
<div class="wrap">
  <div class="footer-top">
    <p class="footer-tagline">We deliver a broad portfolio of services to clients with a team committed to providing innovation.</p>
    <nav class="footer-links" aria-label="Footer">{"".join(f'<a href="{ctx.u(h)}">{E(t)}</a>' for t, h in links)}</nav>
    <div class="footer-assist">
      <h2>How can we assist you?</h2>
      <p>{E(contact_desc)}</p>
      <p class="email-line"><a class="link-inline" href="mailto:{EMAIL}">{EMAIL}</a></p>
      {btn(ctx, "Contact Us", "contact/")}
    </div>
  </div>
  <div class="footer-bar">
    <a class="footer-bar__logo" href="{ctx.u("")}" aria-label="{BRAND} home"><img src="{ctx.u("assets/img/logo-green.png")}" alt="{BRAND} — Real World Solutions" width="168" height="40" loading="lazy"></a>
    <nav class="footer-legal" aria-label="Legal"><a href="{ctx.u("privacy-policy/")}">Privacy Policy</a><a href="{ctx.u("contact/")}">Contact Us</a><a href="{ctx.u("careers/")}">Careers @ Alpha Net</a></nav>
    <div class="footer-social"><span class="footer-social__label">Follow us</span>{"".join(f'<a href="{u}" target="_blank" rel="noopener" aria-label="{n}">{I[k]}</a>' for k, u, n in socials)}</div>
  </div>
  <div class="footer-fine"><p>© <span data-year>2026</span> Alpha Net Consultation LLC. All Rights Reserved.</p></div>
</div>
</footer>'''


def page(path, title, desc, body, subnav=None, keywords="", after_band=False, og_image=None, home=False):
    ctx = Ctx(path)
    body = body(ctx) if callable(body) else body
    full_title = title if home else f"{title} | {BRAND}"
    SEARCH_INDEX.append({"t": title, "d": oneline(desc)[:200], "u": path, "k": keywords})
    canonical = f'<link rel="canonical" href="{SITE_URL}/{path}">' if SITE_URL else ""
    ogi = og_image or "assets/img/logo-green.png"
    ogi_abs = f"{SITE_URL}/{ogi}" if SITE_URL else ctx.u(ogi)
    doc = f'''<!doctype html>
<html lang="en" data-root="{"../" * ctx.depth}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(full_title)}</title>
<meta name="description" content="{E(oneline(desc)[:300])}">
<meta property="og:title" content="{E(full_title)}">
<meta property="og:description" content="{E(oneline(desc)[:300])}">
<meta property="og:type" content="website">
<meta property="og:image" content="{E(ogi_abs)}">
<meta name="theme-color" content="#ffffff">
{canonical}
<link rel="icon" type="image/png" href="{ctx.u("assets/img/mark-green.png")}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@300;400;600;700&family=Source+Serif+4:opsz,wght@8..60,600&display=swap">
<link rel="stylesheet" href="{ctx.u("assets/css/site.css")}">
</head>
<body>
<a class="skip-nav sr-only" href="#main">Skip to Main</a>
{header_html(ctx, subnav)}
{menu_html(ctx)}
<main id="main">
{body}
</main>
{footer_html(ctx, after_band)}
<script src="{ctx.u("assets/js/search-index.js")}" defer></script>
<script src="{ctx.u("assets/js/site.js")}" defer></script>
</body>
</html>
'''
    out = os.path.join(ROOT, path, "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(doc)


# --------------------------------------------------------------------------
# Modules
# --------------------------------------------------------------------------
def module_head(ctx, title, desc=None, kicker=None, link=None, h="h2", cls="t-h2", id_=None):
    k = f'<span class="eyebrow">{E(kicker)}</span>' if kicker else ""
    d = f'<p class="module-head__desc">{nl2br(desc)}</p>' if desc else ""
    l = f'<div class="module-head__row"><a class="link-caps" href="{E(ctx.u(link[1]))}">{E(link[0])}</a></div>' if link else ""
    i = f' id="{id_}"' if id_ else ""
    return f'<div class="module-head"{i}><div>{k}<{h} class="{cls}">{nl2br(title)}</{h}></div>{d}{l}</div>'


def m_banner(ctx, title, text, cta_text="Contact Us", cta_href="contact/", art="streaks.svg", img=None, compact=False):
    bg = media(ctx, img or art, cls="banner__bg") + ('<div class="banner__shade"></div>' if img else "")
    return f'''<section class="module module--tight reveal"><div class="wrap"><div class="banner{" banner--compact" if compact else ""}">{bg}
<h2 class="banner__title">{nl2br(title)}</h2>
<div class="banner__body"><p class="banner__text">{nl2br(text)}</p>{btn(ctx, cta_text, cta_href)}</div>
</div></div></section>'''


def m_cards7(ctx, title, items, desc=None, kicker=None, link=None, band=False, id_=None, cols4=True):
    """items: dicts with title, desc, img, href, type"""
    cards = []
    for i, it in enumerate(items):
        tag = "a" if it.get("href") else "div"
        href = f' href="{E(ctx.u(it["href"]))}"' if it.get("href") else ""
        img = f'<div class="card7__img">{media(ctx, it.get("img"), it.get("title"))}</div>' if it.get("img") is not False else ""
        typ = f'<span class="card7__type">{E(it["type"])}</span>' if it.get("type") else ""
        d = f'<p class="card7__desc">{nl2br(it["desc"])}</p>' if it.get("desc") else ""
        cls = "card7" + ("" if img else " card7--text")
        cards.append(f'<{tag} class="{cls}"{href}>{img}<div class="card7__body">{typ}<h3 class="card7__title">{E(it["title"])}</h3>{d}</div></{tag}>')
    grid = f'<div class="cards7{"" if cols4 else " cards7--3"}">{"".join(cards)}</div>'
    inner = f'<div class="wrap">{module_head(ctx, title, desc, kicker, link, id_=id_)}{grid}</div>'
    if band:
        return f'<section class="band reveal">{inner}</section>'
    return f'<section class="module reveal">{inner}</section>'


def m_icon_cards(ctx, title, items, desc=None, kicker=None, link=None):
    n = len(items)
    cols = 4 if n in (4, 7, 8) else 3
    wide = " icon-cards--wide" if cols == 4 or n > 3 else ""
    cards = "".join(
        f'<div class="icon-card">{line_icon(it["title"] + " " + it.get("desc", ""), i)}<h3 class="icon-card__title">{E(it["title"])}</h3>'
        f'{f"<p class=icon-card__desc>{nl2br(it[chr(100)+chr(101)+chr(115)+chr(99)])}</p>" if it.get("desc") else ""}</div>'
        for i, it in enumerate(items))
    return f'<section class="module reveal"><div class="wrap">{module_head(ctx, title, desc, kicker, link)}<div class="icon-cards{wide}" style="--cols:{cols}">{cards}</div></div></section>'


def m_cards18(ctx, title, items, desc=None, kicker=None, link=None, meta=None):
    cards = []
    for it in items:
        m = f'<div class="card18__meta">{E(it.get("meta") or meta or "")}</div>' if (it.get("meta") or meta) else ""
        if it.get("href"):
            cards.append(f'<a class="card18" href="{E(ctx.u(it["href"]))}">{m}<div class="card18__head"><h3 class="card18__title">{E(it["title"])}</h3><span class="card18__arrow">{I["arrow"]}</span></div>'
                         f'{f"<p class=card18__desc>{nl2br(it[chr(100)+chr(101)+chr(115)+chr(99)])}</p>" if it.get("desc") else ""}</a>')
        else:
            cards.append(f'<div class="card18 card18--plain">{m}<div class="card18__head"><h3 class="card18__title">{E(it["title"])}</h3></div>'
                         f'{f"<p class=card18__desc>{nl2br(it[chr(100)+chr(101)+chr(115)+chr(99)])}</p>" if it.get("desc") else ""}</div>')
    return f'<section class="module reveal"><div class="wrap">{module_head(ctx, title, desc, kicker, link)}<div class="cards18">{"".join(cards)}</div></div></section>'


def m_accordion(ctx, title, items, desc=None, kicker=None, link=None, numbered=False, open_first=True, band=False, id_=None):
    rows = []
    for i, it in enumerate(items):
        bid = ctx.next_id("acc")
        num = f'<span class="acc__num">{i + 1:02d}</span> ' if numbered else ""
        body = it.get("html") or "".join(f"<p>{nl2br(p)}</p>" for p in it.get("paras", []))
        exp = "true" if (open_first and i == 0) else "false"
        rows.append(f'<div class="acc"><button class="acc__btn" type="button" aria-expanded="{exp}" aria-controls="{bid}" id="{bid}-b"><span class="acc__icon" aria-hidden="true"></span><span>{num}{E(it["title"])}</span></button>'
                    f'<div class="acc__panel" id="{bid}" role="region" aria-labelledby="{bid}-b"><div><div class="acc__inner">{body}</div></div></div></div>')
    inner = f'<div class="wrap">{module_head(ctx, title, desc, kicker, link, id_=id_)}<div class="accordion">{"".join(rows)}</div></div>'
    return f'<section class="{"band" if band else "module"} reveal">{inner}</section>'


def m_numbers(ctx, title, stats, desc=None, kicker=None, link=None):
    cols = 3 if len(stats) in (3, 6) else 4
    items = "".join(f'<div class="numbers__item"><strong>{E(s["v"])}</strong><span>{nl2br(s["x"])}</span></div>' for s in stats)
    head = module_head(ctx, title, desc, kicker, link) if title else ""
    return f'<section class="module reveal"><div class="wrap">{head}<div class="numbers" style="--cols:{cols}">{items}</div></div></section>'


def m_rich(ctx, title, paras, kicker=None, link=None, uls=None, sub=None):
    body = []
    for p in paras:
        if isinstance(p, dict) and p.get("t") == "ul":
            body.append("<ul>" + "".join(f"<li>{nl2br(x)}</li>" for x in p["items"]) + "</ul>")
        elif isinstance(p, dict) and p.get("t") == "h":
            body.append(f'<h3 class="t-sans-l" style="margin-top:28px">{nl2br(p["x"])}</h3>')
        else:
            body.append(f'<p class="t-body-l">{nl2br(p if isinstance(p, str) else p["x"])}</p>')
    k = f'<span class="eyebrow">{E(kicker)}</span>' if kicker else ""
    s = f'<p class="t-sans-l" style="margin-top:22px">{nl2br(sub)}</p>' if sub else ""
    l = f'<p style="margin-top:28px"><a class="link-caps" href="{E(ctx.u(link[1]))}">{E(link[0])}</a></p>' if link else ""
    return f'<section class="module reveal"><div class="wrap">{k}<h2 class="t-h2">{nl2br(title)}</h2>{s}<div class="rich" style="margin-top:32px">{"".join(body)}</div>{l}</div></section>'


def m_split(ctx, title, paras, img, kicker=None, cta=None, flip=False, items=None):
    ps = "".join(f"<p>{nl2br(p)}</p>" for p in paras)
    its = ""
    if items:
        its = '<div style="margin-top:28px;display:grid;gap:22px">' + "".join(
            f'<div><h3 style="font-size:22px;font-weight:400;line-height:1.2">{E(i["title"])}</h3>{f"<p style=margin-top:8px;font-size:16px;line-height:1.45>{nl2br(i[chr(100)+chr(101)+chr(115)+chr(99)])}</p>" if i.get("desc") else ""}</div>'
            for i in items) + "</div>"
    k = f'<span class="eyebrow">{E(kicker)}</span>' if kicker else ""
    c = btn(ctx, cta[0], cta[1]) if cta else ""
    return f'''<section class="reveal"><div class="wrap"><div class="split{" split--flip" if flip else ""}">
<div class="split__media">{media(ctx, img, title)}</div>
<div class="split__copy">{k}<h2 class="t-promo">{nl2br(title)}</h2>{ps}{its}<div class="feature__spacer"></div>{c}</div>
</div></div></section>'''


def m_quote(ctx, title, quotes, desc=None, img=None):
    q = dict(quotes[0])
    for part in (q.get("role"), q.get("who")):
        if part and q["x"].rstrip().endswith(part):
            q["x"] = q["x"].rstrip()[: -len(part)].rstrip()
    who = " — ".join(x for x in [q.get("who"), q.get("role")] if x)
    cite = f'<p style="margin-top:24px;font-size:14px;font-weight:700;text-transform:uppercase">{E(who)}</p>' if who else ""
    m = f'<div class="quote__media">{media(ctx, img, "")}</div>' if img else ""
    return f'<section class="band band--mint reveal"><div class="wrap">{module_head(ctx, title, desc)}<div class="quote"><div><blockquote>{nl2br(q["x"])}</blockquote>{cite}</div>{m}</div></div></section>'


def m_logos(ctx, title, imgs, desc=None, link=None):
    lis = "".join(f'<li>{media(ctx, old_img(i["src"]), i.get("alt"))}</li>' for i in imgs if old_img(i["src"]))
    return f'<section class="module reveal"><div class="wrap">{module_head(ctx, title, desc, link=link)}<ul class="logos">{lis}</ul></div></section>'


def m_explore(ctx, big, smalls):
    """big: (eyebrow, title, href, cta); smalls: list of (eyebrow, title, href, img)"""
    sm = "".join(
        f'<a class="explore__small" href="{E(ctx.u(h))}"><div>{f"<span class=eyebrow>{E(e)}</span>" if e else ""}<p class="explore__small-title">{E(t)}</p></div><div class="explore__thumb">{media(ctx, im, "")}</div></a>'
        for e, t, h, im in smalls)
    return f'''<section class="module reveal" style="padding-bottom:110px"><div class="wrap"><h2 class="t-h2">Explore More</h2>
<div class="explore"><a class="explore__big" href="{E(ctx.u(big[2]))}"><span class="eyebrow">{E(big[0])}</span><p class="explore__big-title">{E(big[1])}</p><span class="btn"><span>{E(big[3])}</span>{I["arrow"]}</span></a>
<div class="explore__stack">{sm}</div></div></div></section>'''


def page_hero(ctx, title, lead=None, img=None, rich=None, white=False, pos="right center", actions=None, eyebrow=None):
    l = f'<p class="page-hero__lead">{nl2br(lead)}</p>' if lead else ""
    m = f'<div class="page-hero__media">{media(ctx, img, title, eager=True, pos=pos)}</div>' if img else ""
    r = ""
    if rich:
        def rp(p):
            if isinstance(p, dict) and p.get("t") == "ul":
                return "<ul>" + "".join(f"<li>{nl2br(x)}</li>" for x in p["items"]) + "</ul>"
            if isinstance(p, dict) and p.get("t") == "h":
                return f'<p class="t-sans-l">{nl2br(p["x"])}</p>'
            return f"<p>{nl2br(p)}</p>"
        r = '<div class="page-hero__rich">' + "".join(rp(p) for p in rich) + "</div>"
    a = f'<div class="page-hero__actions">{actions}</div>' if actions else ""
    eb = f'<span class="eyebrow">{E(eyebrow)}</span>' if eyebrow else ""
    return f'<section class="page-hero{" page-hero--white" if white else ""}"><div class="wrap">{eb}<h1 class="t-display">{nl2br(title)}</h1>{l}{m}{r}{a}</div></section>'


# --------------------------------------------------------------------------
# Old-page section renderer
# --------------------------------------------------------------------------
CTA_PAT = re.compile(r"^(ready|take quick action|need to|power your|let[’']s|lets|let us|get started|transform your|start|unlock|accelerate your)", re.I)


def split_sections(blocks):
    pre, sections, cur, kicker = [], [], None, None
    for b in blocks:
        t = b["t"]
        if t == "kicker":
            kicker = b["x"]
            continue
        if t == "h" and kicker and b["l"] >= 4 and b["x"].strip() == kicker.strip():
            cur = {"title": kicker, "level": 2, "kicker": None, "parts": [], "_from_kicker": True}
            kicker = None
            sections.append(cur)
            continue
        if t == "h" and re.fullmatch(r"\d{1,2}", b["x"].strip()):
            if cur is not None:
                cur["parts"].append({"t": "stepnum", "x": b["x"]})
            continue
        if t == "h" and b["l"] in (1, 2, 3) and not (b["l"] == 3 and cur is not None and cur.get("_h3_items")):
            if b["l"] == 1:
                pre.append(b)
                continue
            if cur is not None and cur.get("_from_kicker") and not cur["parts"]:
                kicker = cur["title"]
                sections.pop()
            cur = {"title": b["x"], "level": b["l"], "kicker": kicker, "parts": []}
            kicker = None
            sections.append(cur)
            continue
        (cur["parts"] if cur is not None else pre).append(b)
    return pre, sections


def classify(sec):
    parts = sec["parts"]
    g = {k: [] for k in ("p", "box", "step", "stat", "faq", "quote", "img", "btn", "logos", "ul", "h", "person", "tab")}
    pending_num = False
    for b in parts:
        t = b["t"]
        if t == "stepnum":
            pending_num = True
            continue
        if t == "box":
            if pending_num:
                g["step"].append(b)
                pending_num = False
            else:
                g["box"].append(b)
        elif t in ("p",):
            g["p"].append(b)
        elif t in g:
            g[t].append(b)
    # short-title boxes are really stats ("24/7", "10x", "ROI")
    short = [b for b in g["box"] if len(b["title"]) <= 6]
    if len(short) >= 2:
        g["stat"] += [{"v": b["title"], "x": b["desc"]} for b in short]
        g["box"] = [b for b in g["box"] if len(b["title"]) > 6]
    return g


def render_section(ctx, sec, old_slug, is_last=False, skip_titles=()):
    g = classify(sec)
    title = sec["title"]
    if title.strip() in skip_titles:
        return ""
    kicker = sec.get("kicker")
    intro = g["p"][0]["x"] if g["p"] else None
    rest_p = [p["x"] for p in g["p"][1:]]
    link = None
    if g["btn"] and not (is_last or CTA_PAT.match(title)):
        b0 = g["btn"][0]
        link = (b0["x"], map_href(b0.get("href")))

    if g["logos"] and not re.search(r"trusted|brand|partner|accredit|client", title, re.I):
        g["logos"] = []
    if g["logos"] and not g["box"]:
        return m_logos(ctx, oneline(title), g["logos"][0]["imgs"], desc=intro, link=link)
    out = render_section_main(ctx, sec, g, title, kicker, intro, link, is_last)
    if g["stat"] and g["box"]:
        out += m_numbers(ctx, None, g["stat"])
    return out


def render_section_main(ctx, sec, g, title, kicker, intro, link, is_last):
    # CTA banner
    ptext = " ".join(p["x"] for p in g["p"])
    if (is_last or CTA_PAT.match(title)) and not g["box"] and not g["step"] and not g["faq"] and not g["img"] and not g["h"] and len(ptext) < 420:
        cta = g["btn"][0] if g["btn"] else {"x": "Contact Us", "href": "/contact/"}
        text = " ".join(p["x"] for p in g["p"]) or ""
        if g["stat"]:
            stats = m_numbers(ctx, None, g["stat"])
        else:
            stats = ""
        return m_banner(ctx, title, text, cta["x"], map_href(cta.get("href")), art=["streaks.svg", "rings-green.svg", "waves.svg"][ctx.rot % 3]) + stats

    if g["faq"]:
        items = [{"title": f["q"], "paras": [f["a"]]} for f in g["faq"]]
        return m_accordion(ctx, title, items, desc=intro, kicker=kicker, link=link)
    if g["step"]:
        items = [{"title": s["title"], "paras": [s["desc"]] if s["desc"] else []} for s in g["step"]]
        return m_accordion(ctx, title, items, desc=intro, kicker=kicker, link=link, numbered=True)
    if g["stat"] and not g["box"]:
        out = m_numbers(ctx, title, g["stat"], desc=intro, kicker=kicker, link=link)
        if g["ul"]:
            lis = "".join(f"<li>{nl2br(x)}</li>" for u in g["ul"] for x in u["items"])
            out = out.replace('<div class="numbers"', f'<div class="rich" style="margin-top:28px"><ul class="t-body-l">{lis}</ul></div><div class="numbers"', 1)
        return out
    if g["quote"]:
        img = old_img(g["img"][0]["src"]) if g["img"] else None
        return m_quote(ctx, title, g["quote"], desc=intro, img=img)
    if g["person"]:
        return m_people(ctx, title, g["person"], intro)
    if g["box"]:
        boxes = [{"title": b["title"], "desc": b["desc"], "img": old_img(b.get("img")), "href": map_href(b["href"]) if b.get("href") and b["href"] not in ("#",) else None} for b in g["box"]]
        boxes = [b for b in boxes if b["title"]]
        for b in boxes:
            if b["href"] == "contact/":
                b["href"] = None
        if any(b["img"] for b in boxes):
            for b in boxes:
                if not b["img"]:
                    b["img"] = False
            return m_cards7(ctx, title, boxes, desc=intro, kicker=kicker, link=link, band=True)
        if g["img"] and len(boxes) <= 5:
            ctx.rot += 1
            return m_split(ctx, title, [intro] if intro else [], old_img(g["img"][0]["src"]), kicker=kicker,
                           cta=link, flip=ctx.rot % 2 == 0, items=boxes)
        ctx.rot += 1
        kind = ctx.rot % 3
        for b in boxes:
            b.pop("img", None)
        if kind == 1:
            return m_icon_cards(ctx, title, boxes, desc=intro, kicker=kicker, link=link)
        if kind == 2:
            return m_cards18(ctx, title, boxes, desc=intro, kicker=kicker, link=link)
        return m_cards7(ctx, title, [dict(b, img=False) for b in boxes], desc=intro, kicker=kicker, link=link, cols4=len(boxes) % 3 != 0)
    if g["logos"] and not g["p"][1:]:
        return m_logos(ctx, oneline(title), g["logos"][0]["imgs"], desc=intro, link=link)
    if g["img"] and (g["p"] or g["ul"]):
        ctx.rot += 1
        paras = [b["x"] if b["t"] != "ul" else "\n".join("• " + x for x in b["items"]) for b in sec["parts"] if b["t"] in ("p", "ul") or (b["t"] == "h" and b["l"] >= 4)]
        return m_split(ctx, title, paras, old_img(g["img"][0]["src"]), kicker=kicker, cta=link, flip=ctx.rot % 2 == 0)
    if g["p"] or g["ul"]:
        seq = [b for b in sec["parts"] if b["t"] in ("p", "ul", "h")]
        return m_rich(ctx, title, seq, kicker=kicker, link=link)
    return ""


def m_people(ctx, title, people, intro=None):
    cards = "".join(f'<div class="person">{media(ctx, old_img(p.get("img")), p["name"])}<div class="person__body"><p class="person__name">{E(p["name"])}</p><p class="person__role">{E(p["role"])}</p></div></div>' for p in people)
    return f'<section class="module reveal"><div class="wrap">{module_head(ctx, title, intro)}<div class="people">{cards}</div></div></section>'


def old_body(ctx, old_slug, skip_titles=(), skip_first_overview=True, drop_children_names=()):
    """Render all sections of an old page (after the hero)."""
    pre, secs = split_sections(OLD[old_slug]["blocks"])
    html_parts = []
    n = len(secs)
    for i, s in enumerate(secs):
        if skip_first_overview and i == 0 and s["title"].strip().lower() == "overview":
            continue
        g = classify(s)
        if drop_children_names and g["box"] and sum(1 for b in g["box"] if b["title"] in drop_children_names) >= 2:
            continue
        html_parts.append(render_section(ctx, s, old_slug, is_last=(i == n - 1), skip_titles=skip_titles))
    return "\n".join(html_parts)


def old_intro(old_slug):
    """Intro paragraphs: preface paragraph(s) + an 'Overview' section if it is first."""
    pre, secs = split_sections(OLD[old_slug]["blocks"])
    h1 = next((b["x"] for b in pre if b["t"] == "h" and b["l"] == 1), None)
    paras = [b["x"] for b in pre if b["t"] == "p"]
    ov = []
    if secs and secs[0]["title"].strip().lower() == "overview":
        for b in secs[0]["parts"]:
            if b["t"] == "p":
                ov.append(b["x"])
            elif b["t"] == "box":
                ov.append(b["title"] + ("\n" + b["desc"] if b["desc"] else ""))
            elif b["t"] == "h" and b["l"] >= 4:
                ov.append({"t": "h", "x": b["x"]})
            elif b["t"] == "ul":
                ov.append({"t": "ul", "items": b["items"]})
    return h1, paras, ov


def sub_title_items(ov):
    """Overview blocks: h4 subtitle then paragraphs -> list for hero rich."""
    return ov


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
def solution_subnav(s, current):
    return (s["name"], [("Overview", s["slug"] + "/", current == "overview"), ("Services", s["slug"] + "/#services", False),
                        ("Case Studies", "case-studies/", False), ("Insights", "insights/", False)])


def build_solution_overview(s):
    slug = s["slug"]
    summ = NC.SOLUTION_SUMMARIES[SUMMARY_KEY[slug]]
    det = NC.SOLUTION_DETAIL.get(SUMMARY_KEY[slug])

    def body(ctx):
        out = [page_hero(ctx, s["name"], det["headline"], bg_img(s["old"], 0) or s["art"], [det["intro"]])]
        desc_by_name = {n: d for n, d in det["services"]}
        cards = []
        for c in s["children"] + s["extras"]:
            name = c[1]
            d = desc_by_name.get(name) or desc_by_name.get(name.replace(" (AIOps, LLMOps and MLOps)", "").replace("AI Platform Operations", "AI Platform Operations: AIOps, LLMOps and MLOps"))
            if name == "Agentic AI Engineering":
                d = desc_by_name.get("Enterprise AI Engineering")
            if d is None and name.startswith("AI Platform Operations"):
                d = desc_by_name.get("AI Platform Operations: AIOps, LLMOps and MLOps")
            cards.append({"title": name, "desc": d, "img": bg_img(c[2]) if c[2] else s["art"], "href": f"{slug}/{c[0]}/"})
        out.append(m_cards7(ctx, "Our Services", cards, desc=summ["desc"], id_="services", link=("Talk to Our Team", "contact/")))
        oh1, oparas, _ = old_intro(s["old"])
        if oh1:
            out.append(m_rich(ctx, oh1, oparas))
        old_children = [c[3] for c in s["children"] + s["extras"] if c[3]] + ["PML", "Quality Assurance", "Software Development", "Forward Engineering", "IT Strategy"]
        out.append(old_body(ctx, s["old"], drop_children_names=set(old_children)))
        out.append(m_banner(ctx, det["cta"], summ["desc"], "Contact Us", "contact/", art="streaks.svg"))
        others = [o for o in SOLUTIONS if o["slug"] != slug]
        out.append(m_explore(ctx, ("Next section", others[0]["name"], others[0]["slug"] + "/", "Learn More"),
                             [("Solution", o["name"], o["slug"] + "/", o["art"]) for o in others[1:3]]))
        return "\n".join(out)

    page(slug + "/", s["name"], det["headline"] + " " + det["intro"], body, subnav=solution_subnav(s, "overview"),
         keywords=" ".join(c[1] for c in s["children"] + s["extras"]))


def build_service(s, c, all_children):
    slug, name, old_slug, old_name = c
    det = NC.SOLUTION_DETAIL.get(SUMMARY_KEY[s["slug"]])
    desc = None
    if det:
        dmap = {n: d for n, d in det["services"]}
        desc = dmap.get(name)
        if name == "Agentic AI Engineering":
            desc = dmap.get("Enterprise AI Engineering")
        if desc is None and name.startswith("AI Platform Operations"):
            desc = dmap.get("AI Platform Operations: AIOps, LLMOps and MLOps")
    path = f'{s["slug"]}/{slug}/'

    def body(ctx):
        out = []
        if old_slug:
            h1, paras, ov = old_intro(old_slug)
            lead = desc or (paras[0] if paras else None)
            rich = []
            dup = paras and any(isinstance(p, str) and p.strip().startswith(paras[0].strip()[:80]) for p in ov)
            if desc and paras and not dup:
                rich += paras[:1]
            rich += ov
            out.append(page_hero(ctx, name, lead, bg_img(old_slug) or s["art"], rich))
            pre_, secs_ = split_sections(OLD[old_slug]["blocks"])
            if secs_ and secs_[0]["title"].strip().lower() == "overview":
                st = classify(secs_[0])["stat"]
                if st:
                    out.append(m_numbers(ctx, None, st))
            out.append(old_body(ctx, old_slug))
        else:
            out.append(page_hero(ctx, name, desc, s["art"], [det["intro"]] if det else None))
            out.append(m_banner(ctx, det["cta"] if det else "Contact Us", NC.SOLUTION_SUMMARIES[SUMMARY_KEY[s["slug"]]]["desc"], "Contact Us", "contact/"))
        sibs = [x for x in all_children if x[0] != slug]
        out.append(m_explore(ctx, ("Overview", s["name"], s["slug"] + "/", "Learn More"),
                             [("Service", x[1], f'{s["slug"]}/{x[0]}/', bg_img(x[2]) if x[2] else s["art"]) for x in sibs[:2]]))
        return "\n".join(out)

    page(path, name, desc or (OLD[old_slug]["desc"] if old_slug else name), body, subnav=solution_subnav(s, "service"),
         keywords=f"{s['name']} {old_name or ''}")


def build_business():
    s = SOL_BY_SLUG["ai-business-solutions"]
    B = NC.BUSINESS

    def body(ctx):
        out = [page_hero(ctx, s["name"], B["headline"], bg_img("business-services", 0) or s["art"], B["intro"])]
        items = []
        for t, sub, lst in B["deliver"]:
            items.append({"title": t, "html": f"<p>{E(sub)}</p><ul>" + "".join(f"<li>{E(x)}</li>" for x in lst) + "</ul>"})
        out.append(m_accordion(ctx, B["deliver_title"], items, numbered=True, id_="services"))
        steps = "".join(f'<div class="step"><strong>{E(t)}</strong><span>{E(d)}</span></div>' for t, d in B["approach"])
        out.append(f'<section class="band reveal"><div class="wrap">{module_head(ctx, B["approach_title"])}<p class="flow">{E(B["approach_flow"])}</p><div class="steps">{steps}</div></div></section>')
        out.append(m_icon_cards(ctx, B["impact_title"], [{"title": t, "desc": d} for t, d in B["impact"]], desc=B["impact_intro"]).replace(
            "</div></div></section>", f'</div><p class="t-body" style="margin-top:32px;max-width:850px">{E(B["impact_outro"])}</p></div></section>', 1))
        out.append(m_split(ctx, B["built_title"], B["built"], bg_img("business-services", 1) or "orbs-mint.svg", cta=("Talk to Our Team", "contact/")))
        oh1, oparas, _ = old_intro("business-services")
        out.append(m_rich(ctx, oh1, oparas))
        pre_, secs_ = split_sections(OLD["business-services"]["blocks"])
        ops = next(x for x in secs_ if x["title"].startswith("Streamlining Your Operations"))
        og = classify(ops)
        cards = [{"title": c[1], "desc": og["box"][i]["desc"] if i < len(og["box"]) else "", "img": bg_img(c[2]), "href": f'{s["slug"]}/{c[0]}/'} for i, c in enumerate(s["extras"])]
        out.append(m_cards7(ctx, ops["title"], cards, desc=og["p"][0]["x"] if og["p"] else None, band=True))
        out.append(old_body(ctx, "business-services", drop_children_names=set(c[1] for c in s["extras"]) | {"Contact Center Operations", "GCC Hiring Operations"}))
        out.append(m_banner(ctx, B["cta_title"], B["cta_body"], B["cta"], "contact/", art="rings-green.svg"))
        others = [o for o in SOLUTIONS if o["slug"] != s["slug"]]
        out.append(m_explore(ctx, ("Next section", "AI Accelerators", "ai-accelerators/", "Learn More"),
                             [("Solution", o["name"], o["slug"] + "/", o["art"]) for o in others[:2]]))
        return "\n".join(out)

    page(s["slug"] + "/", s["name"], B["headline"] + " " + B["intro"][0], body,
         subnav=(s["name"], [("Overview", s["slug"] + "/", True), ("What We Deliver", s["slug"] + "/#services", False), ("Case Studies", "case-studies/", False), ("Insights", "insights/", False)]),
         keywords="business process discovery decision intelligence " + " ".join(c[1] for c in s["extras"]))
    for c in s["extras"]:
        build_service(s, c, s["extras"])


def build_accelerators():
    A = NC.ACCELERATORS
    sub = lambda cur: ("AI Accelerators", [("Overview", "ai-accelerators/", cur), ("Accelerators", "ai-accelerators/#accelerators", False), ("Case Studies", "case-studies/", False)])

    def body(ctx):
        out = [page_hero(ctx, "AI Accelerators", A["headline"], bg_img("accelerators", 0), [A["intro"]])]
        cards = [{"title": n, "desc": A["items"][a][1], "img": ACCEL_ART[a], "href": f"ai-accelerators/{a}/"} for a, n in ACCELS]
        out.append(m_cards7(ctx, "Our AI Accelerators", cards, desc=NC.HOME["accelerators_body"], id_="accelerators", cols4=False))
        oh1, oparas, _ = old_intro("accelerators")
        out.append(m_rich(ctx, oh1, oparas))
        out.append(old_body(ctx, "accelerators", drop_children_names={"Gen AI & Agentic AI", "Tech Debt Reduction", "No Code, Low Code", "QA Automation"}))
        out.append(m_banner(ctx, A["cta"], A["headline"], "Contact Us", "contact/", art="rings-green.svg"))
        out.append(m_explore(ctx, ("Next section", "Industries", "industries/", "Learn More"),
                             [("Solution", o["name"], o["slug"] + "/", o["art"]) for o in SOLUTIONS[:2]]))
        return "\n".join(out)

    page("ai-accelerators/", "AI Accelerators", A["headline"] + " " + A["intro"], body, subnav=sub(True), keywords=" ".join(n for a, n in ACCELS))

    for a, n in ACCELS:
        doc_title, desc, uses = A["items"][a]

        def body(ctx, a=a, n=n, doc_title=doc_title, desc=desc, uses=uses):
            out = [page_hero(ctx, n, desc, ACCEL_ART[a], [A["intro"]])]
            uc = [u.strip().rstrip(".") for u in uses.split(",")]
            items = [{"title": u[:1].upper() + u[1:]} for u in uc]
            out.append(m_icon_cards(ctx, "Use cases", items, desc=f"Use cases: {uses}"))
            others = [(x, y) for x, y in ACCELS if x != a]
            out.append(m_cards7(ctx, "More AI Accelerators", [{"title": y, "desc": A["items"][x][1], "img": ACCEL_ART[x], "href": f"ai-accelerators/{x}/"} for x, y in others[:3]],
                                link=("See All Accelerators", "ai-accelerators/"), band=True, cols4=False))
            out.append(m_banner(ctx, A["cta"], A["headline"], "Contact Us", "contact/"))
            out.append(m_explore(ctx, ("Overview", "AI Accelerators", "ai-accelerators/", "Learn More"),
                                 [("Accelerator", y, f"ai-accelerators/{x}/", ACCEL_ART[x]) for x, y in others[3:5]]))
            return "\n".join(out)

        page(f"ai-accelerators/{a}/", n, desc, body, subnav=sub(False), keywords=f"{doc_title} {uses}")


def build_industries():
    about_blocks = OLD["about-us"]["blocks"]
    i = [k for k, b in enumerate(about_blocks) if b.get("x") == "Industries We Serve"][0]
    ind_intro = about_blocks[i + 1]["x"]
    sub = lambda cur: ("Industries", [("Overview", "industries/", cur), ("Case Studies", "case-studies/", False), ("Insights", "insights/", False)])

    def body(ctx):
        out = [page_hero(ctx, "Industries", NC.INDUSTRIES_TITLE, "rings-green.svg", [ind_intro])]
        cards = [{"title": (v[0] if k != "retail-and-consumer" else "Retail & Consumer"), "desc": v[1], "img": ind_img(k), "href": f"industries/{k}/"} for k, v in NC.INDUSTRIES.items()]
        out.append(m_cards7(ctx, NC.INDUSTRIES_TITLE, cards, cols4=False))
        out.append(m_banner(ctx, NC.HOME["solutions_title"], NC.HOME["solutions_body"], "Explore Solutions", "agentic-product-engineering/"))
        out.append(m_explore(ctx, ("Next section", "AI Accelerators", "ai-accelerators/", "Learn More"),
                             [("Solution", o["name"], o["slug"] + "/", o["art"]) for o in SOLUTIONS[:2]]))
        return "\n".join(out)

    page("industries/", "Industries", ind_intro, body, subnav=sub(True), keywords=" ".join(v[0] for v in NC.INDUSTRIES.values()))

    keys = list(NC.INDUSTRIES.keys())
    for k, (nm, d) in NC.INDUSTRIES.items():
        name = nm if k != "retail-and-consumer" else "Retail & Consumer"
        old = INDUSTRY_OLD[k]

        def body(ctx, k=k, name=name, d=d, old=old):
            h1, paras, ov = old_intro(old)
            out = [page_hero(ctx, name, d, ind_img(k))]
            if h1:
                out.append(m_rich(ctx, h1, paras + ov))
            out.append(old_body(ctx, old, skip_first_overview=False))
            others = [x for x in keys if x != k]
            out.append(m_explore(ctx, ("Overview", "Industries", "industries/", "Learn More"),
                                 [("Industry", NC.INDUSTRIES[x][0] if x != "retail-and-consumer" else "Retail & Consumer", f"industries/{x}/", ind_img(x)) for x in others[:2]]))
            return "\n".join(out)

        page(f"industries/{k}/", name, d, body, subnav=sub(False), keywords=OLD[old]["title"])


def about_subnav(cur):
    return ("About Alpha Net", [("Overview", "about/", cur == "about"), ("Our Vision", "about/our-vision/", cur == "vision"),
                                ("Leadership", "about/leadership/", cur == "leadership"), ("Our Approach", "our-approach/", cur == "approach"),
                                ("Careers", "careers/", cur == "careers")])


HOME_STATS = [b for b in OLD["home"]["blocks"] if b["t"] == "stat"]


def build_about():
    def body(ctx):
        h1, paras, ov = old_intro("about-us")
        out = [f'<section class="image-hero">{media(ctx, bg_img("about-us", 0), "", eager=True, pos="center 30%")}<div class="wrap"><h1 class="t-display">{E(h1)}</h1></div></section>',
               f'<section class="lead-under"><div class="wrap"><p>{E(paras[0])}</p></div></section>',
               m_numbers(ctx, None, HOME_STATS)]
        out.append(old_body(ctx, "about-us"))
        out.append(m_explore(ctx, ("Next section", "Our Vision", "about/our-vision/", "Learn More"),
                             [("Company", "Leadership", "about/leadership/", bg_img("team-members", 1)), ("Company", "Our Approach", "our-approach/", bg_img("how-we-engage", 1))]))
        return "\n".join(out)

    page("about/", "About", OLD["about-us"]["desc"], body, subnav=about_subnav("about"))

    def vbody(ctx):
        h1, paras, ov = old_intro("our-vision")
        out = [page_hero(ctx, h1, paras[0] if paras else None, bg_img("our-vision", 0), pos="center")]
        out.append(old_body(ctx, "our-vision"))
        out.append(m_explore(ctx, ("Company", "About Alpha Net", "about/", "Learn More"),
                             [("Company", "Leadership", "about/leadership/", bg_img("team-members", 1)), ("Company", "Careers", "careers/", bg_img("talent", 1))]))
        return "\n".join(out)

    page("about/our-vision/", "Our Vision", OLD["our-vision"]["desc"], vbody, subnav=about_subnav("vision"))

    def lbody(ctx):
        h1, paras, ov = old_intro("team-members")
        pre, secs = split_sections(OLD["team-members"]["blocks"])
        out = [page_hero(ctx, h1, paras[0] if paras else None, bg_img("team-members", 1), pos="center")]
        # people are stored as image + H2 name + role paragraph
        people, i, blocks = [], 0, OLD["team-members"]["blocks"]
        while i < len(blocks):
            b = blocks[i]
            if b["t"] == "img" and i + 2 < len(blocks) and blocks[i + 1]["t"] == "h" and blocks[i + 2]["t"] == "p":
                people.append({"img": b["src"], "name": blocks[i + 1]["x"], "role": blocks[i + 2]["x"]})
                i += 3
                continue
            i += 1
        for s in secs:
            names = {p["name"] for p in people}
            if s["title"] in names or s["title"].startswith("Packed with powerful"):
                continue
            if s["title"].startswith("Get to know"):
                out.append(m_people(ctx, s["title"], people, s["parts"][0]["x"] if s["parts"] and s["parts"][0]["t"] == "p" else None))
                continue
            out.append(render_section(ctx, s, "team-members"))
        out.append(m_explore(ctx, ("Company", "About Alpha Net", "about/", "Learn More"),
                             [("Company", "Our Vision", "about/our-vision/", bg_img("our-vision", 0)), ("Company", "Careers", "careers/", bg_img("talent", 1))]))
        return "\n".join(out)

    page("about/leadership/", "Leadership", OLD["team-members"]["desc"], lbody, subnav=about_subnav("leadership"))


def build_approach():
    def body(ctx):
        h1, paras, ov = old_intro("how-we-engage")
        pre, secs = split_sections(OLD["how-we-engage"]["blocks"])
        out = [page_hero(ctx, "Our Approach", paras[0] if paras else None, bg_img("how-we-engage", 1), pos="center", eyebrow=h1)]
        models, others = [], []
        for s in secs:
            g = classify(s)
            if s["title"] in ("Fixed Price", "Hybrid", "ODC Partnership", "Time and Material", "Dedicated Development Centre"):
                models.append((s, g))
            else:
                others.append(s)
        # intro sections
        others = [s for s in others if s["title"] != "Flexible Engagement Models"] + [s for s in others if s["title"] == "Flexible Engagement Models"][:1]
        fem_sec = others.pop() if others and others[-1]["title"] == "Flexible Engagement Models" else None
        for s in others[:1]:
            out.append(render_section(ctx, s, "how-we-engage"))
        # engagement models as horizontal tabs
        imgs = [b for b in OLD["how-we-engage"]["blocks"] if b["t"] == "img"]
        img_for = {"Fixed Price": "price", "Hybrid": "hybrid", "ODC Partnership": "partnership", "Time and Material": "gallery-2", "Dedicated Development Centre": "development"}
        tabs, panels = [], []
        for i, (s, g) in enumerate(models):
            tid, pid = ctx.next_id("tab"), ctx.next_id("tp")
            im = next((old_img(b["src"]) for b in imgs if img_for[s["title"]] in b["src"]), None)
            tabs.append(f'<button class="tabs__btn" role="tab" id="{tid}" aria-controls="{pid}" aria-selected="{"true" if i == 0 else "false"}" tabindex="{0 if i == 0 else -1}">{E(s["title"])}</button>')
            panels.append(f'<div class="tabs__panel" role="tabpanel" id="{pid}" aria-labelledby="{tid}"{"" if i == 0 else " hidden"}><div><h3>{E(s["title"])}</h3>{"".join(f"<p style=margin-top:20px>{nl2br(p[chr(120)])}</p>" for p in g["p"])}</div><div class="tabs__media">{media(ctx, im, s["title"])}</div></div>')
        fem = next((s for s in others if s["title"] == "Flexible Engagement Models"), None)
        if fem:
            pass
        out.append(f'<section class="module reveal"><div class="wrap">{module_head(ctx, "Flexible Engagement Models", classify(fem_sec)["p"][0]["x"] if fem_sec else None)}<div class="tabs" data-tabs><div class="tabs__list" role="tablist" aria-label="Engagement models">{"".join(tabs)}</div>{"".join(panels)}</div></div></section>')
        for s in others[1:]:
            out.append(render_section(ctx, s, "how-we-engage", is_last=(s is others[-1])))
        out.append(m_explore(ctx, ("Company", "About Alpha Net", "about/", "Learn More"),
                             [("Company", "Case Studies", "case-studies/", bg_img("case-studies")), ("Company", "Careers", "careers/", bg_img("talent", 1))]))
        return "\n".join(out)

    page("our-approach/", "Our Approach", OLD["how-we-engage"]["desc"], body, subnav=about_subnav("approach"), keywords="engagement model fixed price hybrid ODC time and material dedicated development centre global capability centers")


def article_blocks(ctx, blocks, skip_h1=True):
    out = []
    for b in blocks:
        t = b["t"]
        if t == "h":
            if b["l"] == 1 and skip_h1:
                continue
            lvl = max(2, min(b["l"], 4)) if b["l"] != 1 else 2
            out.append(f"<h{lvl}>{nl2br(b['x'])}</h{lvl}>")
        elif t == "p":
            if b["x"].strip() in ("Edit Content",):
                continue
            out.append(f"<p>{nl2br(b['x'])}</p>")
        elif t == "ul":
            tag = "ol" if b.get("o") else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{nl2br(x)}</li>" for x in b["items"]) + f"</{tag}>")
        elif t == "quote":
            out.append(f"<blockquote>{nl2br(b['x'])}</blockquote>")
        elif t == "img":
            src = old_img(b["src"])
            if src:
                out.append(media(ctx, src, b.get("alt")))
        elif t == "table":
            rows = b["rows"]
            out.append("<table>" + "".join("<tr>" + "".join(f"<td>{nl2br(c)}</td>" for c in r) + "</tr>" for r in rows) + "</table>")
        elif t == "box":
            out.append(f"<h3>{E(b['title'])}</h3>" + (f"<p>{nl2br(b['desc'])}</p>" if b["desc"] else ""))
        elif t == "faq":
            out.append(f"<h3>{E(b['q'])}</h3><p>{nl2br(b['a'])}</p>")
        elif t == "stat":
            out.append(f"<p><strong>{E(b['v'])}</strong> {E(b['x'])}</p>")
    return "\n".join(out)


def fmt_date(iso):
    import datetime
    try:
        d = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return d.strftime("%B %-d, %Y")
    except Exception:
        return ""


def build_insights():
    blogs = OLD["blogs"]

    def card(ctx, k):
        p = OLD[k]
        h1 = post_title(k)
        first = post_excerpt(k)
        img = old_img(p.get("image")) or "rings-green.svg"
        cats = ", ".join(p.get("cats") or [])
        return f'<a class="insight" href="{E(ctx.u("insights/" + post_slug(k) + "/"))}"><div class="insight__img">{media(ctx, img, h1, pos="top")}</div><div class="insight__body"><p class="insight__meta">Article <span>{E(fmt_date(p.get("published", "")))}</span></p><h3 class="insight__title">{E(h1)}</h3><p class="insight__desc">{E(first)}</p></div></a>'

    def body(ctx):
        pre, secs = split_sections(blogs["blocks"])
        h1 = next(b["x"] for b in pre if b["t"] == "h")
        out = [page_hero(ctx, "Insights & Resources", blogs["desc"], None, white=False)]
        out.append(f'<section class="module reveal" style="padding-top:72px"><div class="wrap"><h2 class="t-h2">{E(h1)}</h2><div class="insight-list">{"".join(card(ctx, k) for k in POSTS)}</div></div></section>')
        out.append(m_explore(ctx, ("Next section", "Case Studies", "case-studies/", "Learn More"),
                             [("Solution", o["name"], o["slug"] + "/", o["art"]) for o in SOLUTIONS[:2]]))
        return "\n".join(out)

    page("insights/", "Insights & Resources", blogs["desc"], body, keywords="blog blogs articles")

    for k in POSTS:
        p = OLD[k]

        def body(ctx, k=k, p=p):
            h1 = post_title(k)
            img = old_img(p.get("image"))
            cats = ", ".join(p.get("cats") or [])
            media_html = f'<div class="article-hero__media" style="background:var(--beige)">{media(ctx, img, h1, eager=True)}</div>' if img else ""
            out = [f'<section class="article-hero"><div class="wrap"><p class="meta">Article <span>· {E(fmt_date(p.get("published", "")))}{" · " + E(cats) if cats else ""}</span></p><h1>{E(h1)}</h1>{media_html}</div></section>',
                   f'<div class="wrap"><article class="article"><div class="article__body">{article_blocks(ctx, p["blocks"])}</div></article></div>']
            others = [x for x in POSTS if x != k][:3]
            out.append(f'<section class="module reveal"><div class="wrap"><h2 class="t-h2">More Insights</h2><div class="insight-list">{"".join(card(ctx, x) for x in others)}</div></div></section>')
            out.append(m_banner(ctx, NC.HOME["possibilities_title"], NC.HOME["hero_sub"], NC.HOME["hero_cta"], "contact/"))
            out.append('<div style="height:110px"></div>')
            return "\n".join(out)

        page(f"insights/{post_slug(k)}/", post_title(k), post_excerpt(k), body, keywords=" ".join(p.get("cats") or []), og_image=old_img(p.get("image")))


def build_cases():
    cs = OLD["case-studies"]

    def cimg(k):
        h1 = OLD[k]["blocks"][0]["x"]
        src = CASE_IMG.get(h1)
        return old_img(src) if src else bg_img(k)

    def body(ctx):
        pre, secs = split_sections(cs["blocks"])
        h1, paras, ov = old_intro("case-studies")
        out = [page_hero(ctx, h1, paras[0] if paras else cs["desc"], bg_img("case-studies"))]
        cards = [{"title": OLD[k]["blocks"][0]["x"], "img": cimg(k), "href": f"case-studies/{post_slug(k)}/", "type": "Client Impact"} for k in CASES]
        out.append(m_cards7(ctx, "Our Customer Success Stories", cards, cols4=True))
        for s in secs[1:]:
            out.append(render_section(ctx, s, "case-studies", is_last=s is secs[-1]))
        out.append('<div style="height:110px"></div>')
        return "\n".join(out)

    page("case-studies/", "Case Studies", cs["desc"], body, keywords="client impact success stories")

    rel_map = {"Product Engineering": "agentic-product-engineering/", "Enterprise Engineering": "enterprise-ai-engineering/", "Infrastructure & Cloud": "ai-infra-and-cloud/",
               "Business Services": "ai-business-solutions/", "Accelerators": "ai-accelerators/"}
    rel_new = {"Product Engineering": "Agentic Product Engineering", "Enterprise Engineering": "Enterprise AI Engineering", "Infrastructure & Cloud": "AI Infra & Cloud",
               "Business Services": "AI Business Solutions", "Accelerators": "AI Accelerators"}
    for k in CASES:
        p = OLD[k]

        def body(ctx, k=k, p=p):
            h1 = p["blocks"][0]["x"]
            blocks = p["blocks"][1:]
            # drop trailing "Explore Related Services" list (rendered as cards below)
            cut = next((i for i, b in enumerate(blocks) if b["t"] == "h" and b["x"].startswith("Explore Related Services")), None)
            related = []
            if cut is not None:
                nxt = blocks[cut + 1] if cut + 1 < len(blocks) else None
                if nxt and nxt["t"] == "ul":
                    related = nxt["items"]
                blocks = blocks[:cut]
            blocks = [b for b in blocks if b["t"] != "btn"]
            out = [f'<section class="article-hero"><div class="wrap"><p class="meta">Client Impact</p><h1>{E(h1)}</h1><div class="article-hero__media">{media(ctx, cimg(k), h1, eager=True)}</div></div></section>',
                   f'<div class="wrap"><article class="article"><div class="article__body">{article_blocks(ctx, blocks)}</div></article></div>']
            if related:
                out.append(m_cards18(ctx, "Explore Related Services", [{"title": rel_new.get(r, r), "href": rel_map.get(r, "contact/"), "meta": "Solution"} for r in related]))
            out.append(m_banner(ctx, NC.HOME["possibilities_title"], NC.HOME["hero_sub"], "Schedule a Consultation", "contact/"))
            out.append('<div style="height:110px"></div>')
            return "\n".join(out)

        page(f"case-studies/{post_slug(k)}/", p["blocks"][0]["x"], next((b["x"] for b in p["blocks"] if b["t"] == "p"), p["title"]), body, keywords="case study client impact")


def build_careers():
    t = OLD["talent"]

    def body(ctx):
        h1, paras, ov = old_intro("talent")
        pre, secs = split_sections(t["blocks"])
        out = [page_hero(ctx, "Careers", paras[0] if paras else None, bg_img("talent", 1), pos="center", eyebrow=h1)]
        join = secs[0]
        jg = classify(join)
        out.append(f'''<section class="careers reveal"><div class="careers__copy"><span class="eyebrow">Alpha Net Careers</span><h2 class="t-sans-xl">{E(join["title"])}</h2><p>{E(jg["p"][0]["x"])}</p>
<div class="careers__ctas">{btn(ctx, "Email Your Resume", "mailto:" + EMAIL + "?subject=Careers%20at%20Alpha%20Net", icon="arrow-ur")}</div></div>
<div class="careers__media">{media(ctx, "petals.svg")}<div class="careers__frame">{media(ctx, bg_img("talent", 0), "")}</div></div></section>''')
        for s in secs[1:]:
            g = classify(s)
            if s["title"] == "Open Positions":
                out.append(f'<section class="module reveal"><div class="wrap">{module_head(ctx, s["title"], g["p"][0]["x"] if g["p"] else None)}<div class="cards18"><a class="card18" href="mailto:{EMAIL}?subject=Careers%20at%20Alpha%20Net"><div class="card18__meta">Careers</div><div class="card18__head"><h3 class="card18__title">{EMAIL}</h3><span class="card18__arrow">{I["arrow"]}</span></div></a></div></div></section>')
                continue
            out.append(render_section(ctx, s, "talent", is_last=s is secs[-1]))
        out.append('<div style="height:110px"></div>')
        return "\n".join(out)

    page("careers/", "Careers", t["desc"], body, subnav=about_subnav("careers"), keywords="talent jobs join our team open positions")


def build_contact():
    c = OLD["contact"]

    def body(ctx):
        h1, paras, ov = old_intro("contact")
        pre, secs = split_sections(c["blocks"])
        out = [page_hero(ctx, "Contact Us", None, None)]
        out[0] = out[0].replace("</h1>", f'</h1><p class="page-hero__lead">{E(h1)}. {E(paras[0])}</p><div class="contact-cta"><a class="contact-email" href="mailto:{EMAIL}">{EMAIL}</a><div>{btn(ctx, "Email Us", "mailto:" + EMAIL, icon="arrow-ur")}</div></div>', 1)
        for s in secs:
            g = classify(s)
            if s["title"] == "Connect With Us":
                sub_h = next((b["x"] for b in s["parts"] if b["t"] == "h"), None)
                out.append(m_split(ctx, s["title"], [p["x"] for p in g["p"]], bg_img("contact"), kicker=None, cta=("Email Us", "mailto:" + EMAIL)).replace('<h2 class="t-promo">', f'<span class="eyebrow">{E(sub_h)}</span><h2 class="t-promo">' if sub_h else '<h2 class="t-promo">', 1))
                if g["logos"]:
                    out.append(m_logos(ctx, "Trusted by Leading Brands", g["logos"][0]["imgs"]))
                continue
            if s["title"] == "Our Global Presence":
                out.append(m_rich(ctx, s["title"], [p["x"] for p in g["p"]]))
                continue
            if s["title"] == "Explore Our Office Locations":
                def office_lines(desc):
                    lines = []
                    for x in desc.split("\n"):
                        num = x.strip()
                        if re.fullmatch(r"\+?[\d ]{8,}", num):
                            lines.append(f'<a href="tel:{num.replace(" ", "")}">{E(num)}</a>')
                        else:
                            lines.append(E(x))
                    return "<br>".join(lines)
                offices = "".join(f'<div class="office"><h3>{E(b["title"])}</h3><p>{office_lines(b["desc"])}</p></div>' for b in g["box"])
                out.append(f'<section class="module reveal"><div class="wrap">{module_head(ctx, s["title"], g["p"][0]["x"] if g["p"] else None)}<div class="offices">{offices}</div></div></section>')
                continue
            out.append(render_section(ctx, s, "contact"))
        out.append('<div style="height:110px"></div>')
        return "\n".join(out)

    page("contact/", "Contact Us", c["desc"], body, keywords="email offices locations phone address")


def build_privacy():
    p = OLD["privacy-policy"]

    def body(ctx):
        h1 = next((b["x"] for b in p["blocks"] if b["t"] == "h" and b["l"] == 1), "Privacy Policy")
        return f'<section class="article-hero"><div class="wrap"><h1>{E(h1)}</h1></div></section><div class="wrap"><article class="article" style="margin-bottom:110px"><div class="article__body">{article_blocks(ctx, p["blocks"])}</div></article></div>'

    page("privacy-policy/", "Privacy Policy", p["desc"] or "Privacy Policy", body)


def build_home():
    H = NC.HOME

    def body(ctx):
        # Hero coverflow slides: solutions, accelerators, industries
        slides = [
            ("Agentic AI", "Solution", "Agentic Product Engineering", "agentic-product-engineering/", bg_img("accelerators__agentic-ai")),
            ("Enterprise AI", "Solution", "Enterprise AI Engineering", "enterprise-ai-engineering/", bg_img("enterprise-engineering__it-strategy-dev")),
            ("AI Accelerators", "Accelerator", "Enterprise RAG Platform", "ai-accelerators/enterprise-rag-platform/", "sphere-glow.svg"),
            ("Cloud", "Solution", "AI Infra & Cloud", "ai-infra-and-cloud/", bg_img("infrastructure-and-cloud", 1)),
            ("Business", "Solution", "AI Business Solutions", "ai-business-solutions/", bg_img("business-services", 0)),
            ("Client Impact", "Case Study", OLD[CASES[0]]["blocks"][0]["x"], f"case-studies/{post_slug(CASES[0])}/", old_img(CASE_IMG.get(OLD[CASES[0]]["blocks"][0]["x"]))),
            ("Industries", "Industry", "Financial Services", "industries/financial-services/", bg_img("finance-and-banking")),
        ]
        sl = []
        for i, (chip, typ, title, href, img) in enumerate(slides):
            sl.append(f'<a class="coverflow__slide" href="{E(ctx.u(href))}" data-pos="hidden-r">{media(ctx, img, title, eager=i < 5)}<span class="coverflow__chip">{E(chip)}</span>'
                      f'<span class="coverflow__card"><span class="coverflow__meta"><span>{E(typ)}</span></span><span class="coverflow__title">{E(title)}</span></span></a>')
        hero = f'''<section class="home-hero"><div class="wrap">
<span class="eyebrow">Welcome to Alpha Net</span>
<h1 class="t-hero">{E(H["hero_title"])}</h1>
<div class="coverflow-wrap"><div class="coverflow" data-coverflow aria-roledescription="carousel" aria-label="Featured">{"".join(sl)}</div>
<div class="carousel-controls"><button class="ctrl" type="button" data-cf-pause aria-label="Pause carousel">{I["pause"]}{I["play"]}</button><button class="ctrl" type="button" data-cf-prev aria-label="Previous slide">{I["chev-l"]}</button><button class="ctrl" type="button" data-cf-next aria-label="Next slide">{I["chev-r"]}</button></div></div>
<nav class="spotlight" aria-label="Alpha Net spotlight"><span class="spotlight__label">Alpha Net Spotlight</span><a href="{ctx.u("agentic-product-engineering/agentic-ai-and-multi-agent-systems/")}">Agentic AI</a><a href="{ctx.u("ai-accelerators/enterprise-rag-platform/")}">Enterprise RAG</a><a href="{ctx.u("ai-accelerators/")}">AI Accelerators</a></nav>
</div></section>'''

        banner = f'''<section class="module reveal" style="padding-top:80px"><div class="wrap"><div class="banner">{media(ctx, "streaks.svg", cls="banner__bg")}
<h2 class="banner__title">{E(H["hero_sub"])}</h2>
<div class="banner__body"><p class="banner__text">{E(H["hero_body"])}</p>{btn(ctx, H["hero_cta"], "contact/")}</div></div></div></section>'''

        # From AI possibilities: impact carousel
        pill_imgs = [bg_img("product-engineering", 0), bg_img("enterprise-engineering__data-engineering-and-analytics"), bg_img("enterprise-engineering__erp-implementation"), bg_img("infrastructure-and-cloud__cyber-security")]
        hrefs = ["agentic-product-engineering/", "enterprise-ai-engineering/enterprise-data-foundations/", "enterprise-ai-engineering/intelligent-workflow-automation/", "agentic-product-engineering/ai-evaluation-governance-and-operations/"]
        cards = []
        for i, (t, d) in enumerate(H["pillars"]):
            st = HOME_STATS[i]
            if i == 0:
                cards.append(f'<a class="impact impact--wide" href="{E(ctx.u(hrefs[i]))}">{media(ctx, pill_imgs[i], t)}<span class="impact__stat"><strong>{E(st["v"])}</strong><span>{E(st["x"])}</span></span>'
                             f'<span class="impact__card"><span class="eyebrow eyebrow--sm">Capability</span><span class="impact__title">{E(t)}</span><span class="impact__desc">{E(d)}</span><span class="btn btn--sm"><span>Learn More</span>{I["arrow"]}</span></span></a>')
            else:
                cards.append(f'<a class="impact" href="{E(ctx.u(hrefs[i]))}">{media(ctx, pill_imgs[i], t)}<span class="impact__stat"><strong>{E(st["v"])}</strong><span>{E(st["x"])}</span></span>'
                             f'<span class="impact__card"><span class="eyebrow eyebrow--sm">Capability</span><span class="impact__title">{E(t)}</span></span></a>')
        possibilities = f'''<section class="module reveal"><div class="wrap">{module_head(ctx, H["possibilities_title"], H["possibilities_body"][0] + chr(10) + H["possibilities_body"][1], link=("See All Solutions", "agentic-product-engineering/"))}</div>
<div class="hscroll" data-hscroll><div class="hscroll__track">{"".join(cards)}</div><div class="wrap"><div class="hscroll__dots"></div></div></div></section>'''

        feature = f'''<section class="feature reveal"><div class="wrap"><div class="feature__copy"><span class="eyebrow">{E(H["accelerators_title"])}</span><h2 class="t-promo">{E(H["accelerators_headline"])}</h2>
<p class="feature__text">{E(H["accelerators_body"])}</p><ul class="feature__list">{"".join(f"<li>{E(x)}</li>" for x in H["accelerators_list"])}</ul><div class="feature__spacer"></div>{btn(ctx, "Explore AI Accelerators", "ai-accelerators/")}</div>
<div class="feature__media">{media(ctx, "orbs-mint.svg")}</div></div></section>'''

        S = NC.SOLUTION_SUMMARIES
        def pcard(key, slug, img, cls=""):
            s = S[key]
            return (f'<a class="promo-card {cls}" href="{E(ctx.u(slug + "/"))}">{media(ctx, img, s["title"])}<span class="eyebrow eyebrow--light">Our Solutions</span>'
                    f'<h3 class="promo-card__title">{E(s["title"])}</h3><p class="promo-card__desc">{E(s["desc"])}</p><p class="promo-card__tags">{E(s["tags"])}</p><span class="btn"><span>Learn More</span>{I["arrow"]}</span></a>')
        grid = f'''<section class="module reveal"><div class="wrap">{module_head(ctx, H["solutions_title"], H["solutions_body"])}
<div class="promo-grid">{pcard("agentic-product-engineering", "agentic-product-engineering", bg_img("accelerators__agentic-ai"), "promo-card--tall")}
<div class="promo-grid__col">{pcard("enterprise-ai-engineering", "enterprise-ai-engineering", "rings-green.svg", "promo-card--mint")}{pcard("infrastructure-and-cloud", "ai-infra-and-cloud", bg_img("infrastructure-and-cloud", 1))}</div></div></div></section>'''

        bs = S["business-services"]
        split = f'''<section class="reveal"><div class="wrap"><div class="split"><div class="split__media">{media(ctx, bg_img("business-services", 1), bs["title"])}</div>
<div class="split__copy"><span class="eyebrow">{E(bs["title"])}</span><h2 class="t-promo">{E(bs["headline"])}</h2><p>{E(bs["desc"])}</p><p style="font-size:16px;margin-top:20px">{E(bs["tags"])}</p><div class="feature__spacer"></div>{btn(ctx, "Learn More", "ai-business-solutions/")}</div></div></div></section>'''

        ind_cards = [{"title": (v[0] if k != "retail-and-consumer" else "Retail & Consumer"), "desc": v[1], "img": ind_img(k), "href": f"industries/{k}/"} for k, v in NC.INDUSTRIES.items()]
        industries = m_cards7(ctx, NC.INDUSTRIES_TITLE, ind_cards, link=("See All Industries", "industries/"), cols4=False)

        talent = OLD["talent"]
        join = next(b for b in talent["blocks"] if b["t"] == "p" and b["x"].startswith("We believe"))
        careers = f'''<section class="careers reveal"><div class="careers__copy"><span class="eyebrow">Alpha Net Careers</span><h2 class="t-sans-xl">Join Our Team</h2><p>{E(join["x"])}</p>
<div class="careers__ctas">{btn(ctx, "Explore Careers", "careers/", kind="secondary", icon="arrow-ur")}{btn(ctx, "Apply Today", "mailto:" + EMAIL + "?subject=Careers%20at%20Alpha%20Net", icon="arrow-ur")}</div></div>
<div class="careers__media">{media(ctx, "petals.svg")}<div class="careers__frame">{media(ctx, bg_img("talent", 0), "")}</div></div></section>'''

        blogs = OLD["blogs"]
        band = f'''<section class="insights-band reveal"><div class="insights-band__grid"><div class="insights-band__copy"><h2>Featured Insights</h2><p>{E(blogs["desc"])}</p></div>
<div class="insights-band__media">{media(ctx, bg_img("blogs"), "")}</div></div>
<div class="subscribe"><p class="subscribe__label">Get the latest industry insights delivered to you</p><div class="subscribe__field"><a class="subscribe__email" href="mailto:{EMAIL}?subject=Subscribe%20to%20Alpha%20Net%20insights">{EMAIL}</a>{btn(ctx, "Subscribe", "mailto:" + EMAIL + "?subject=Subscribe%20to%20Alpha%20Net%20insights")}</div></div></section>'''

        return "\n".join([hero, banner, possibilities, feature, grid, split, industries, careers, band])

    page("", "Alpha Net | " + NC.HOME["hero_title"], NC.HOME["hero_sub"] + " " + NC.HOME["hero_body"], body, after_band=True, home=True,
         keywords="home ai agentic enterprise")


def main():
    for s in SOLUTIONS:
        if s["slug"] == "ai-business-solutions":
            continue
        build_solution_overview(s)
        for c in s["children"] + s["extras"]:
            build_service(s, c, s["children"] + s["extras"])
    build_business()
    build_accelerators()
    build_industries()
    build_about()
    build_approach()
    build_insights()
    build_cases()
    build_careers()
    build_contact()
    build_privacy()
    build_home()
    # 404 page
    page("404/", "Page not found", "The page you were looking for does not exist.", lambda ctx: page_hero(ctx, "Page not found", "The page you were looking for has moved or no longer exists.", None, actions=btn(ctx, "Back to Home", "")) + '<div style="height:110px"></div>')
    shutil.move(os.path.join(ROOT, "404", "index.html"), os.path.join(ROOT, "404.html"))
    os.rmdir(os.path.join(ROOT, "404"))
    # fix relative paths in 404 (served from any depth) -> use absolute-from-root via <base>
    p404 = open(os.path.join(ROOT, "404.html"), encoding="utf-8").read()
    open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8").write(p404.replace('"../', '"').replace('data-root="../"', 'data-root=""'))
    SEARCH_INDEX[:] = [x for x in SEARCH_INDEX if x["u"] != "404/"]
    open(os.path.join(ROOT, "assets", "js", "search-index.js"), "w", encoding="utf-8").write("window.SITE_INDEX=" + json.dumps(SEARCH_INDEX, ensure_ascii=False) + ";\n")
    print(f"Built {len(SEARCH_INDEX)} pages")


if __name__ == "__main__":
    main()
