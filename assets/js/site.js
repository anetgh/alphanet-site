(function () {
  "use strict";
  var doc = document.documentElement;
  doc.classList.add("js");
  var ROOT = doc.getAttribute("data-root") || "";
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* Header: hide on scroll down, show on scroll up */
  var header = document.querySelector(".site-header");
  if (header) {
    var lastY = window.scrollY;
    window.addEventListener("scroll", function () {
      var y = window.scrollY;
      if (Math.abs(y - lastY) < 6) return;
      header.setAttribute("data-scroll", y > lastY && y > 140 ? "down" : "up");
      lastY = y;
    }, { passive: true });
  }

  /* Mega menu */
  var menu = document.getElementById("site-menu");
  var openers = document.querySelectorAll("[data-menu-open]");
  var lastFocus = null;
  function openMenu(focusSearch) {
    if (!menu) return;
    lastFocus = document.activeElement;
    menu.classList.add("is-open");
    menu.removeAttribute("inert");
    document.body.classList.add("menu-open");
    openers.forEach(function (b) { b.setAttribute("aria-expanded", "true"); });
    var target = focusSearch ? menu.querySelector(".menu__search input") : menu.querySelector("[data-menu-close]");
    setTimeout(function () { target && target.focus(); }, 30);
  }
  function closeMenu() {
    if (!menu) return;
    menu.classList.remove("is-open", "is-drilled", "is-searching");
    menu.setAttribute("inert", "");
    document.body.classList.remove("menu-open");
    openers.forEach(function (b) { b.setAttribute("aria-expanded", "false"); });
    if (lastFocus) lastFocus.focus();
  }
  openers.forEach(function (b) {
    b.addEventListener("click", function () { openMenu(b.hasAttribute("data-menu-search")); });
  });
  if (menu) {
    menu.querySelectorAll("[data-menu-close]").forEach(function (b) { b.addEventListener("click", closeMenu); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && menu.classList.contains("is-open")) closeMenu();
    });

    var items = menu.querySelectorAll(".menu__item[data-panel]");
    var panels = menu.querySelectorAll(".menu__panel");
    var desktop = window.matchMedia("(min-width: 1024px)");
    function activate(id) {
      items.forEach(function (i) { i.classList.toggle("is-active", i.getAttribute("data-panel") === id); i.setAttribute("aria-expanded", i.getAttribute("data-panel") === id ? "true" : "false"); });
      panels.forEach(function (p) { p.classList.toggle("is-active", p.id === id); });
    }
    items.forEach(function (i) {
      var id = i.getAttribute("data-panel");
      i.addEventListener("mouseenter", function () { if (desktop.matches) activate(id); });
      i.addEventListener("focus", function () { if (desktop.matches) activate(id); });
      i.addEventListener("click", function () {
        activate(id);
        if (!desktop.matches) menu.classList.add("is-drilled");
      });
    });
    menu.querySelectorAll(".menu__back").forEach(function (b) {
      b.addEventListener("click", function () { menu.classList.remove("is-drilled"); });
    });
    if (items[0]) activate(items[0].getAttribute("data-panel"));

    /* Site search (static index) */
    var input = menu.querySelector(".menu__search input");
    var results = menu.querySelector(".menu__results");
    var index = window.SITE_INDEX || [];
    function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
    function search(q) {
      q = q.trim().toLowerCase();
      if (q.length < 2) { menu.classList.remove("is-searching"); return; }
      menu.classList.add("is-searching");
      var terms = q.split(/\s+/);
      var hits = index.map(function (p) {
        var hay = (p.t + " " + p.d + " " + (p.k || "")).toLowerCase();
        var score = 0;
        for (var i = 0; i < terms.length; i++) {
          if (hay.indexOf(terms[i]) === -1) return null;
          score += p.t.toLowerCase().indexOf(terms[i]) !== -1 ? 3 : 1;
        }
        return { p: p, s: score };
      }).filter(Boolean).sort(function (a, b) { return b.s - a.s; }).slice(0, 12);
      results.innerHTML = '<h2>' + hits.length + (hits.length === 1 ? " result" : " results") + ' for “' + esc(q) + '”</h2>' +
        (hits.length ? hits.map(function (h) {
          return '<a href="' + ROOT + h.p.u + '"><strong>' + esc(h.p.t) + '</strong><span>' + esc(h.p.d) + '</span></a>';
        }).join("") : '<p class="menu__results-empty">No pages match that search. Try a service, industry or accelerator name.</p>');
    }
    if (input) input.addEventListener("input", function () { search(input.value); });
  }

  /* Hero coverflow */
  document.querySelectorAll("[data-coverflow]").forEach(function (root) {
    var slides = Array.prototype.slice.call(root.querySelectorAll(".coverflow__slide"));
    var n = slides.length, current = 0, timer = null, playing = !reduceMotion;
    var wrapper = root.parentElement;
    var pauseBtn = wrapper.querySelector("[data-cf-pause]");
    function layout() {
      slides.forEach(function (s, i) {
        var d = ((i - current) % n + n) % n;
        if (d > n / 2) d -= n;
        var pos = Math.abs(d) <= 2 ? String(d) : (d < 0 ? "hidden-l" : "hidden-r");
        s.setAttribute("data-pos", pos);
        s.setAttribute("tabindex", d === 0 ? "0" : "-1");
        s.setAttribute("aria-hidden", Math.abs(d) <= 2 ? "false" : "true");
      });
    }
    function go(delta) { current = (current + delta + n) % n; layout(); }
    function play() { stop(); if (playing) timer = setInterval(function () { go(1); }, 5500); }
    function stop() { if (timer) clearInterval(timer); timer = null; }
    slides.forEach(function (s, i) {
      s.addEventListener("click", function (e) {
        var pos = s.getAttribute("data-pos");
        if (pos !== "0") { e.preventDefault(); current = i; layout(); play(); }
      });
    });
    var prev = wrapper.querySelector("[data-cf-prev]"), next = wrapper.querySelector("[data-cf-next]");
    prev && prev.addEventListener("click", function () { go(-1); play(); });
    next && next.addEventListener("click", function () { go(1); play(); });
    function syncPause() {
      if (!pauseBtn) return;
      pauseBtn.setAttribute("aria-label", playing ? "Pause carousel" : "Play carousel");
      pauseBtn.querySelector(".i-pause").style.display = playing ? "" : "none";
      pauseBtn.querySelector(".i-play").style.display = playing ? "none" : "";
    }
    pauseBtn && pauseBtn.addEventListener("click", function () { playing = !playing; syncPause(); play(); });
    root.addEventListener("mouseenter", stop);
    root.addEventListener("mouseleave", play);
    layout(); syncPause(); play();
  });

  /* Horizontal scrollers with dots */
  document.querySelectorAll("[data-hscroll]").forEach(function (root) {
    var track = root.querySelector(".hscroll__track");
    var dotsWrap = root.querySelector(".hscroll__dots");
    if (!track || !dotsWrap) return;
    function pages() { return Math.max(1, Math.ceil((track.scrollWidth - 2) / track.clientWidth)); }
    function build() {
      var p = pages();
      dotsWrap.innerHTML = "";
      dotsWrap.style.display = p > 1 ? "" : "none";
      for (var i = 0; i < p; i++) {
        var b = document.createElement("button");
        b.className = "hscroll__dot"; b.type = "button";
        b.setAttribute("aria-label", "Show set " + (i + 1) + " of " + p);
        (function (k) { b.addEventListener("click", function () { track.scrollTo({ left: k * track.clientWidth, behavior: reduceMotion ? "auto" : "smooth" }); }); })(i);
        dotsWrap.appendChild(b);
      }
      sync();
    }
    function sync() {
      var p = pages(), max = track.scrollWidth - track.clientWidth;
      var k = max <= 0 ? 0 : Math.round(track.scrollLeft / max * (p - 1));
      dotsWrap.querySelectorAll(".hscroll__dot").forEach(function (d, i) { d.setAttribute("aria-current", i === k ? "true" : "false"); });
    }
    track.addEventListener("scroll", sync, { passive: true });
    window.addEventListener("resize", build);
    build();
  });

  /* Accordions */
  document.querySelectorAll(".acc__btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var open = btn.getAttribute("aria-expanded") === "true";
      btn.setAttribute("aria-expanded", open ? "false" : "true");
    });
  });

  /* Tabs */
  document.querySelectorAll("[data-tabs]").forEach(function (root) {
    var tabs = root.querySelectorAll("[role=tab]");
    tabs.forEach(function (t, i) {
      t.addEventListener("click", function () { select(i); });
      t.addEventListener("keydown", function (e) {
        if (e.key === "ArrowRight") { select((i + 1) % tabs.length); tabs[(i + 1) % tabs.length].focus(); }
        if (e.key === "ArrowLeft") { var k = (i - 1 + tabs.length) % tabs.length; select(k); tabs[k].focus(); }
      });
    });
    function select(k) {
      tabs.forEach(function (t, i) {
        t.setAttribute("aria-selected", i === k ? "true" : "false");
        t.setAttribute("tabindex", i === k ? "0" : "-1");
        var p = document.getElementById(t.getAttribute("aria-controls"));
        if (p) p.hidden = i !== k;
      });
    }
  });

  /* Reveal on scroll */
  if ("IntersectionObserver" in window && !reduceMotion) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    document.querySelectorAll(".reveal").forEach(function (el) {
      var r = el.getBoundingClientRect();
      if (r.top < window.innerHeight) el.classList.add("is-in"); else io.observe(el);
    });
  } else {
    document.querySelectorAll(".reveal").forEach(function (el) { el.classList.add("is-in"); });
  }

  /* Contact: link map pins and office cards on hover/focus */
  var pins = document.querySelectorAll(".pin[data-office]");
  if (pins.length) {
    var setActive = function (id, on) {
      document.querySelectorAll('[data-office="' + id + '"]').forEach(function (el) { el.classList.toggle("is-active", on); });
    };
    document.querySelectorAll(".pin[data-office], .office[data-office]").forEach(function (el) {
      var id = el.getAttribute("data-office");
      el.addEventListener("mouseenter", function () { setActive(id, true); });
      el.addEventListener("mouseleave", function () { setActive(id, false); });
      el.addEventListener("focusin", function () { setActive(id, true); });
      el.addEventListener("focusout", function () { setActive(id, false); });
    });
  }

  /* Copyright year */
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
