"""Extract ordered content blocks from saved anetcorp.com HTML pages.

Usage: venv/bin/python extract.py <html_dir> <out.json>
"""
import json, os, re, sys
from bs4 import BeautifulSoup, NavigableString

html_dir, out_path = sys.argv[1], sys.argv[2]

def clean(s):
    s = s.replace("\xa0", " ")
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r"\s*\n\s*", "\n", s)
    return s.strip()

def text(el):
    if el is None:
        return ""
    # keep <br> as line breaks
    for br in el.find_all("br"):
        br.insert_before("\n")
        br.unwrap()
    return clean(el.get_text(" "))

def hidden(el):
    for a in [el] + list(el.parents):
        cls = a.get("class") or [] if hasattr(a, "get") else []
        if any(c in ("elementor-hidden-desktop",) for c in cls):
            return True
    return False

def img_src(img):
    for k in ("data-src", "data-lazy-src", "src"):
        v = img.get(k)
        if v and not v.startswith("data:"):
            return v
    return None

def rich_blocks(container):
    """Ordered blocks from a rich-text container (text editor / post body)."""
    out = []
    for node in container.children:
        if isinstance(node, NavigableString):
            t = clean(str(node))
            if t:
                out.append({"t": "p", "x": t})
            continue
        name = node.name
        if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            t = text(node)
            if t:
                out.append({"t": "h", "l": int(name[1]), "x": t})
        elif name == "p":
            t = text(node)
            if t:
                out.append({"t": "p", "x": t})
        elif name in ("ul", "ol"):
            items = [text(li) for li in node.find_all("li", recursive=False)]
            items = [i for i in items if i]
            if items:
                out.append({"t": "ul", "o": name == "ol", "items": items})
        elif name == "blockquote":
            t = text(node)
            if t:
                out.append({"t": "quote", "x": t})
        elif name == "table":
            rows = []
            for tr in node.find_all("tr"):
                rows.append([text(c) for c in tr.find_all(["td", "th"])])
            if rows:
                out.append({"t": "table", "rows": rows})
        elif name in ("figure", "img"):
            im = node if name == "img" else node.find("img")
            if im is not None and img_src(im):
                out.append({"t": "img", "src": img_src(im), "alt": im.get("alt", "")})
        elif name in ("div", "section", "span", "strong", "em", "a"):
            inner = rich_blocks(node)
            if inner:
                out.extend(inner)
            else:
                t = text(node)
                if t:
                    out.append({"t": "p", "x": t})
        elif name in ("hr", "script", "style", "noscript", "svg", "form", "iframe"):
            continue
        else:
            t = text(node)
            if t:
                out.append({"t": "p", "x": t})
    return out

def widget_blocks(w):
    wt = w.get("data-widget_type", "")
    out = []
    if wt == "heading.default":
        h = w.find(re.compile("^h[1-6]$")) or w.find(class_="elementor-heading-title")
        if h is not None:
            lvl = int(h.name[1]) if h.name and h.name[0] == "h" and len(h.name) == 2 else 3
            t = text(h)
            if t:
                out.append({"t": "h", "l": lvl, "x": t})
    elif wt == "elementskit-heading.default":
        h = (w.find(re.compile("^h[1-6]$"), class_=re.compile("elementskit-section-title")) or next((x for x in w.find_all(re.compile("^h[1-6]$")) if not any("subtitle" in c for c in (x.get("class") or []))), None))
        sub = w.find(class_=re.compile("elementskit-section-subtitle"))
        if sub is not None and text(sub):
            out.append({"t": "kicker", "x": text(sub)})
        if h is not None:
            lvl = int(h.name[1]) if h.name and re.match(r"^h[1-6]$", h.name) else 2
            t = text(h)
            if t:
                out.append({"t": "h", "l": lvl, "x": t})
        desc = w.find(class_=re.compile("widget-heading-description|elementskit-section-description|ekit-heading__description"))
        if desc is None:
            # description paragraphs that follow the title inside the widget
            for p in w.find_all("p"):
                t = text(p)
                if t:
                    out.append({"t": "p", "x": t})
        else:
            for b in rich_blocks(desc) or [{"t": "p", "x": text(desc)}]:
                if b.get("x") or b.get("items"):
                    out.append(b)
    elif wt == "text-editor.default":
        c = w.find(class_="elementor-widget-container") or w
        out.extend(rich_blocks(c))
    elif wt in ("elementskit-icon-box.default", "icon-box.default", "elementskit-image-box.default"):
        title = (w.find(class_=re.compile("elementskit-info-box-title|elementor-icon-box-title|elementskit-image-box-title|ekit-image-box-title"))
                 or w.find(re.compile("^h[1-6]$")))
        desc = w.find(class_=re.compile("^box-body$|elementor-icon-box-description|elementskit-box-style-content|image-box-description"))
        tt = text(title) if title is not None else ""
        dd = ""
        if desc is not None:
            ps = [text(p) for p in desc.find_all("p")]
            dd = "\n".join([p for p in ps if p]) or text(desc)
            if tt and dd.startswith(tt):
                dd = dd[len(tt):].strip()
        img = w.find("img")
        b = {"t": "box", "title": tt, "desc": dd}
        if img is not None and img_src(img) and wt == "elementskit-image-box.default":
            b["img"] = img_src(img); b["alt"] = img.get("alt", "")
        a = w.find("a", href=True)
        if a is not None and a["href"] not in ("#", ""):
            b["href"] = a["href"]
        if tt or dd:
            out.append(b)
    elif wt == "image.default":
        im = w.find("img")
        if im is not None and img_src(im):
            out.append({"t": "img", "src": img_src(im), "alt": im.get("alt", "")})
    elif wt == "elementskit-button.default":
        a = w.find("a")
        if a is not None and text(a):
            out.append({"t": "btn", "x": text(a), "href": a.get("href", "")})
    elif wt == "elementskit-funfact.default":
        num = w.find(class_="number-percentage")
        wrap = w.find(class_="number-percentage-wraper")
        val = num.get("data-value") if num is not None else ""
        suffix = ""
        if wrap is not None:
            full = text(wrap)
            suffix = re.sub(r"^\s*0", "", full).strip()
            pre = ""
        title = w.find(class_="funfact-title")
        out.append({"t": "stat", "v": (val or "") + suffix, "x": text(title)})
    elif wt in ("elementskit-accordion.default", "elementskit-faq.default", "elementskit-advance-accordion.default"):
        cards = w.find_all(class_=re.compile("elementskit-card$|elementskit-single-faq|ekit-accordion-item|elementskit-card "))
        if not cards:
            cards = w.find_all(class_=re.compile("card"))
        for c in cards:
            q = c.find(class_=re.compile("ekit-accordion-title|elementskit-faq-title|ekit-adv-accordion-title")) or c.find(re.compile("^h[1-6]$"))
            a = c.find(class_=re.compile("elementskit-card-body|elementskit-faq-body|ekit-accordion--content|elementskit-faq-content"))
            if q is not None and a is not None and text(q):
                out.append({"t": "faq", "q": text(q), "a": text(a)})
    elif wt == "elementskit-testimonial.default":
        for item in w.find_all(class_=re.compile("elementskit-commentor-content|elementskit-testimonial-content|swiper-slide")):
            body = item.find(class_=re.compile("commentor-content|elementskit-testimonial-text|ekit-testimonial-text")) or item.find("p")
            who = item.find(class_=re.compile("author-name|commentor-name|ekit-testimonial-name"))
            role = item.find(class_=re.compile("author-des|commentor-designation|ekit-testimonial-des"))
            if body is not None and text(body):
                out.append({"t": "quote", "x": text(body), "who": text(who) if who else "", "role": text(role) if role else ""})
    elif wt in ("icon-list.default", "elementskit-stylish-list.default"):
        items = [text(li) for li in w.find_all("li")]
        items = [i for i in items if i]
        if items:
            out.append({"t": "ul", "items": items})
    elif wt in ("elementskit-client-logo.default", "image-carousel.default"):
        imgs = []
        for im in w.find_all("img"):
            s = img_src(im)
            if s and s not in [i["src"] for i in imgs]:
                imgs.append({"src": s, "alt": im.get("alt", "")})
        if imgs:
            out.append({"t": "logos", "imgs": imgs})
    elif wt == "elementskit-timeline.default":
        for it in w.find_all(class_=re.compile("timeline-content|single-timeline")):
            t = it.find(re.compile("^h[1-6]$")); p = it.find("p")
            if t is not None:
                out.append({"t": "box", "title": text(t), "desc": text(p) if p else ""})
    elif wt == "elementskit-team.default":
        for it in w.find_all(class_=re.compile("profile-card|ekit-team-wrap|profile-square-v")):
            n = it.find(class_=re.compile("profile-title|ekit-team-name")); r = it.find(class_=re.compile("profile-designation|ekit-team-designation"))
            im = it.find("img")
            if n is not None:
                out.append({"t": "person", "name": text(n), "role": text(r) if r else "", "img": img_src(im) if im is not None else ""})
    elif wt == "elementskit-simple-tab.default" or wt == "elementskit-tab.default":
        titles = [text(t) for t in w.find_all(class_=re.compile("elementskit-tab-title|tab-title"))]
        bodies = w.find_all(class_=re.compile("elementskit-tab-content|tab-content-inner|elementskit-tab-pane"))
        for i, b in enumerate(bodies):
            out.append({"t": "tab", "title": titles[i] if i < len(titles) else "", "blocks": rich_blocks(b)})
    elif wt == "elementskit-image-morphing.default":
        im = w.find("img")
        if im is not None and img_src(im):
            out.append({"t": "img", "src": img_src(im), "alt": im.get("alt", "")})
    elif wt in ("elementskit-contact-form7.default", "ekit-vertical-menu.default", "ekit-nav-menu.default",
                "elementskit-social-media.default", "elementskit-popup-modal.default", "kd_site_logo.default",
                "google_maps.default", "shortcode.default", "sidebar.default", "elementskit-blog-posts.default"):
        pass
    else:
        c = w.find(class_="elementor-widget-container")
        if c is not None:
            t = text(c)
            if t:
                out.append({"t": "p", "x": t, "raw_widget": wt})
    return out

pages = {}
for fn in sorted(os.listdir(html_dir)):
    if not fn.endswith(".html"):
        continue
    slug = fn[:-5]
    soup = BeautifulSoup(open(os.path.join(html_dir, fn), encoding="utf-8").read(), "html.parser")
    main = soup.find("main", id="main") or soup.body
    title = soup.title.get_text().strip() if soup.title else ""
    md = soup.find("meta", attrs={"name": "description"})
    desc = md["content"].strip() if md and md.get("content") else ""
    blocks = []
    art = main.find("article", class_=re.compile("article-single"))
    if slug.startswith("blogs__") and art is not None:
        h1 = soup.find("h1")
        ec = art.find(class_="entry-content")
        date = soup.find("time")
        cats = [a.get_text().strip() for a in art.select(".category-meta a")]
        blocks.append({"t": "h", "l": 1, "x": text(h1) if h1 else title})
        pages[slug] = {"title": title, "desc": desc, "kind": "post", "date": text(date) if date else "",
                       "cats": cats, "blocks": rich_blocks(ec) if ec is not None else []}
        og = soup.find("meta", property="og:image")
        if og is not None:
            pages[slug]["image"] = og.get("content")
        pub = soup.find("meta", property="article:published_time")
        if pub is not None:
            pages[slug]["published"] = pub.get("content")
        continue
    widgets = main.find_all(attrs={"data-widget_type": True})
    for w in widgets:
        # skip widgets nested inside another captured widget (eg. tabs)
        if w.find_parent(attrs={"data-widget_type": True}) is not None:
            continue
        if hidden(w):
            continue
        blocks.extend(widget_blocks(w))
    # de-duplicate consecutive identical blocks
    dedup = []
    for b in blocks:
        if dedup and json.dumps(dedup[-1], sort_keys=True) == json.dumps(b, sort_keys=True):
            continue
        dedup.append(b)
    og = soup.find("meta", property="og:image")
    pages[slug] = {"title": title, "desc": desc, "kind": "page", "blocks": dedup, "image": og.get("content") if og is not None else None}

json.dump(pages, open(out_path, "w"), indent=1, ensure_ascii=False)
print(len(pages), "pages")
