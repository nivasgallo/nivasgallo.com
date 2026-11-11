/* nivasgallo.com — shared behaviour */
(function () {
  var root = document.documentElement;
  if (!root.lang) root.lang = 'en-GB';
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');

  /* ---------- Light / dark toggle ---------- */
  var btn = document.getElementById('mode');
  var sys = window.matchMedia('(prefers-color-scheme: dark)');
  function current() { return root.dataset.theme || (sys.matches ? 'dark' : 'light'); }
  function paint() {
    if (!btn) return;
    var next = current() === 'dark' ? 'light' : 'dark';
    btn.dataset.next = next;
    btn.setAttribute('aria-label', 'Switch to ' + next + ' mode');
    btn.title = 'Switch to ' + next + ' mode';
  }
  try { var saved = localStorage.getItem('ng-theme'); if (saved === 'dark' || saved === 'light') root.dataset.theme = saved; } catch (e) {}
  if (btn) btn.addEventListener('click', function () {
    var next = current() === 'dark' ? 'light' : 'dark';
    root.dataset.theme = next;
    try { localStorage.setItem('ng-theme', next); } catch (e) {}
    paint();
  });
  if (sys.addEventListener) sys.addEventListener('change', paint);
  new MutationObserver(paint).observe(root, { attributes: true, attributeFilter: ['data-theme'] });
  paint();

  /* ---------- Kinetic titles ----------
     Any element with data-kinetic: letters near the pointer swap weight,
     heavy letters go light and light letters go heavy.
     Screen readers get the plain text once; the split letters are hidden from them. */
  function split(el) {
    var label = el.textContent.replace(/\s+/g, ' ').trim();
    var vis = document.createElement('span');
    vis.setAttribute('aria-hidden', 'true');
    while (el.firstChild) vis.appendChild(el.firstChild);
    var sr = document.createElement('span');
    sr.className = 'sr-only';
    sr.textContent = label;
    el.appendChild(sr);
    el.appendChild(vis);

    var walker = document.createTreeWalker(vis, NodeFilter.SHOW_TEXT);
    var nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    var chars = [];
    nodes.forEach(function (t) {
      var base = parseFloat(getComputedStyle(t.parentElement).fontWeight) || 400;
      var frag = document.createDocumentFragment();
      t.textContent.split(/(\s+)/).forEach(function (part) {
        if (!part) return;
        if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(' ')); return; }
        var wd = document.createElement('span');
        wd.className = 'wd';
        Array.from(part).forEach(function (ch) {
          var c = document.createElement('span');
          c.className = 'c';
          c.textContent = ch;
          wd.appendChild(c);
          chars.push({ c: c, base: base, target: base >= 600 ? 200 : 900 });
        });
        frag.appendChild(wd);
      });
      t.parentNode.replaceChild(frag, t);
    });
    return chars;
  }

  document.querySelectorAll('[data-kinetic]').forEach(function (el) {
    var chars = split(el);
    var raf = 0;
    function reset() { chars.forEach(function (o) { o.c.style.fontWeight = ''; }); }
    el.addEventListener('pointermove', function (e) {
      if (reduce.matches) return;
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(function () {
        var R = Math.max(140, parseFloat(getComputedStyle(el).fontSize) * 1.3);
        chars.forEach(function (o) {
          var r = o.c.getBoundingClientRect();
          var d = Math.hypot(e.clientX - (r.left + r.width / 2), e.clientY - (r.top + r.height / 2));
          var k = Math.max(0, 1 - d / R);
          o.c.style.fontWeight = k ? Math.round(o.base + (o.target - o.base) * k) : '';
        });
      });
    });
    el.addEventListener('pointerleave', reset);
    if (reduce.addEventListener) reduce.addEventListener('change', reset);
  });
})();

/* ---------- Motion A–D ----------
   A  weight settle: page titles, once on load
   B  line rise: headings, ledes and the first paragraph of each chapter
   C  ink wipe: wireframes, flows and wide images
   D  rise: phones, screen rows and the scrollable device
   Exposed as window.ngMotion(root) so content added later (Your Odds+) can use it. */
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  var E = 'cubic-bezier(.2,.7,.1,1)';
  if (reduce.matches || !('IntersectionObserver' in window) || !Element.prototype.animate) { window.ngMotion = function () {}; return; }

  /* A */
  function settle(el) {
    var cs = el.querySelectorAll('.c');
    var step = Math.min(35, 700 / Math.max(cs.length, 1));
    cs.forEach(function (c, i) {
      var w = parseFloat(getComputedStyle(c).fontWeight);
      c.animate([{ fontWeight: 100, opacity: 0.3 }, { fontWeight: w, opacity: 1 }], { duration: 900, delay: i * step, easing: E, fill: 'backwards' });
    });
  }

  /* B: wrap each word in a mask; words on the same line rise together */
  function maskWords(el) {
    el.dataset.mOriginal = el.innerHTML;
    var walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    var nodes = []; while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach(function (t) {
      var f = document.createDocumentFragment();
      t.textContent.split(/(\s+)/).forEach(function (part) {
        if (!part) return;
        if (/^\s+$/.test(part)) { f.appendChild(document.createTextNode(part)); return; }
        var w = document.createElement('span'); w.className = 'm-w';
        var i = document.createElement('span'); i.className = 'm-i'; i.textContent = part;
        w.appendChild(i); f.appendChild(w);
      });
      t.parentNode.replaceChild(f, t);
    });
  }
  function rise(el) {
    var inner = Array.from(el.querySelectorAll('.m-i'));
    var tops = [], anims = [];
    inner.forEach(function (i) {
      var top = Math.round(i.parentNode.getBoundingClientRect().top);
      var line = tops.indexOf(top); if (line < 0) { tops.push(top); line = tops.length - 1; }
      anims.push(i.animate([{ transform: 'translateY(110%)' }, { transform: 'none' }], { duration: 700, delay: line * 80, easing: E, fill: 'backwards' }));
    });
    el.classList.remove('m-pending');
    Promise.all(anims.map(function (a) { return a.finished; })).then(function () {
      el.innerHTML = el.dataset.mOriginal; delete el.dataset.mOriginal;   // restore clean markup
    }).catch(function () {});
  }

  /* C */
  function prepWipe(frame) {
    frame.classList.add('m-host');
    var c = document.createElement('div'); c.className = 'm-cover'; c.setAttribute('aria-hidden', 'true');
    frame.appendChild(c);
  }
  function wipe(frame) {
    var c = frame.querySelector(':scope > .m-cover'), img = frame.querySelector('img');
    frame.classList.remove('m-pending');
    c.animate([{ transform: 'scaleY(1)' }, { transform: 'scaleY(0)' }], { duration: 800, easing: E, fill: 'backwards' }).finished.then(function () { c.remove(); });
    if (img) img.animate([{ transform: 'scale(1.04)' }, { transform: 'none' }], { duration: 1100, easing: E });
  }

  /* D */
  function lift(el, i) {
    el.classList.remove('m-pending');
    el.animate([{ opacity: 0, transform: 'translateY(32px)' }, { opacity: 1, transform: 'none' }], { duration: 700, delay: (i || 0) * 120, easing: E, fill: 'backwards' });
  }

  var io = new IntersectionObserver(function (entries) {
    var batch = 0;
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      var el = e.target; io.unobserve(el);
      var kind = el.dataset.m;
      if (kind === 'B') rise(el);
      else if (kind === 'C') wipe(el);
      else if (kind === 'D') lift(el, batch++);
    });
  }, { threshold: 0.2, rootMargin: '0px 0px -8% 0px' });

  window.ngMotion = function (root) {
    root = root || document;
    if (root === document) root.querySelectorAll('h1[data-kinetic]').forEach(settle);
    root.querySelectorAll('h2.big, .chapter h2, .lede, .results h2, .chapter .body p:first-of-type').forEach(function (el) {
      if (el.dataset.m || el.closest('[data-m]')) return;
      el.dataset.m = 'B'; maskWords(el); el.classList.add('m-pending'); io.observe(el);
    });
    root.querySelectorAll('.fig:not(.phone):not(.screens) > .frame').forEach(function (f) {
      if (f.dataset.m) return; f.dataset.m = 'C'; prepWipe(f); f.classList.add('m-pending'); io.observe(f);
    });
    root.querySelectorAll('.fig.phone, .fig.screens, .device-wrap').forEach(function (el) {
      if (el.dataset.m) return; el.dataset.m = 'D'; el.classList.add('m-rise', 'm-pending'); io.observe(el);
    });
  };
  window.ngMotion(document);
})();
