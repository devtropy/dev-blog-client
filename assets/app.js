// viniciusarre.dev — vim-style navigation.
// NORMAL: j/k move (list) or scroll (post), gg/G, Ctrl-d/u, Enter/l open, h/- back,
// / search posts, n/N next/prev match, : command, ? help, t cycle theme.
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const THEMES = ["tokyonight", "catppuccin", "gruvbox", "nord"];
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch {} },
  };

  // ── theme ──
  const setTheme = (t) => {
    if (!THEMES.includes(t)) return false;
    document.documentElement.dataset.theme = t;
    store.set("theme", t);
    const el = $("#theme-pill"); if (el) el.textContent = "◐ " + t;
    return true;
  };
  setTheme(store.get("theme") || "tokyonight");

  // ── clock ──
  const clock = $("#clock");
  const tick = () => { if (clock) clock.textContent = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }); };
  tick(); setInterval(tick, 15000);

  // ── uptime-ish pill: days since first post ──
  const up = $("#uptime");
  if (up) { const d = Math.max(0, Math.floor((Date.now() - Date.parse("2026-11-19")) / 864e5)); up.textContent = "up " + d + "d"; }

  // ── state ──
  const mode = $("#mode"), cmd = $("#cmd"), msg = $("#msg"), pos = $("#pos");
  const rows = $$(".ls .row");
  let cur = 0, pending = "", lastSearch = "";
  const visible = () => rows.filter(r => !r.classList.contains("hide"));

  const say = (text, err = false) => { msg.textContent = text; msg.className = err ? "err" : "msg"; };
  const setMode = (m) => {
    mode.textContent = m;
    mode.className = "mode" + (m === "COMMAND" ? " cmd" : m === "SEARCH" ? " srch" : "");
  };

  const highlight = (i, scroll = true) => {
    const v = visible(); if (!v.length) return;
    cur = Math.max(0, Math.min(i, v.length - 1));
    rows.forEach(r => r.classList.remove("cur"));
    v[cur].classList.add("cur");
    if (scroll) v[cur].scrollIntoView({ block: "nearest" });
    updatePos();
  };

  const updatePos = () => {
    if (!pos) return;
    if (rows.length) { pos.textContent = (cur + 1) + ":" + visible().length; return; }
    const max = document.documentElement.scrollHeight - innerHeight;
    const pct = max <= 0 ? "All" : scrollY <= 2 ? "Top" : scrollY >= max - 2 ? "Bot" : Math.round(100 * scrollY / max) + "%";
    pos.textContent = pct;
  };
  addEventListener("scroll", () => { if (!rows.length) updatePos(); }, { passive: true });

  const open = () => { const v = visible()[cur]; const a = v && $("a", v); if (a) location.href = a.href; };
  const back = () => { location.href = location.pathname === "/" ? "/" : (document.body.dataset.up || "/"); };
  const scrollBy = (y) => scrollTo({ top: scrollY + y, behavior: "smooth" });
  const page = () => Math.round(innerHeight * 0.5);

  rows.forEach((r, i) => {
    r.addEventListener("mouseenter", () => highlight(visible().indexOf(r), false));
    r.addEventListener("click", (e) => { if (e.target.tagName !== "A") { highlight(visible().indexOf(r)); open(); } });
  });
  if (rows.length) highlight(0, false); else updatePos();

  // ── search ──
  const search = (q) => {
    lastSearch = q.toLowerCase();
    let n = 0;
    rows.forEach(r => {
      const hit = !lastSearch || r.textContent.toLowerCase().includes(lastSearch);
      r.classList.toggle("hide", !hit); if (hit) n++;
    });
    if (!rows.length && q) { location.href = "/?q=" + encodeURIComponent(q); return; }
    highlight(0);
    say(q ? `/${q}  [${n} match${n === 1 ? "" : "es"}]` : "");
  };
  const q0 = new URLSearchParams(location.search).get("q");
  if (q0 && rows.length) search(q0);

  // ── commands ──
  const go = (p) => { location.href = p; };
  const COMMANDS = {
    q: () => back(), quit: () => back(), "q!": () => go("/"), wq: () => say("E45: 'readonly' option is set (add ! to override)", true),
    help: () => toggleHelp(true), h: () => toggleHelp(true),
    home: () => go("/"), posts: () => go("/#posts"), about: () => go("/about"),
    rss: () => go("/rss.xml"), noh: () => search(""), nohlsearch: () => search(""),
    top: () => scrollTo({ top: 0, behavior: "smooth" }),
    e: (a) => {
      if (!a) return say("E32: No file name", true);
      const t = a.replace(/\.md$/, "");
      go(t === "about" ? "/about" : "/posts/" + t);
    },
    colorscheme: (a) => {
      if (!a) return say("themes: " + THEMES.join(" "));
      if (!setTheme(a)) say(`E185: Cannot find color scheme '${a}'`, true); else say("colorscheme " + a);
    },
    colo: (a) => COMMANDS.colorscheme(a),
    ls: () => say("posts: " + (window.__POSTS__ || []).join("  ")),
    whoami: () => say("vinicius — engineer who measures before shipping"),
    sudo: () => say("vinicius is not in the sudoers file. This incident will be reported.", true),
  };
  const run = (line) => {
    const s = line.trim();
    if (!s) return;
    if (/^\d+$/.test(s)) { rows.length ? highlight(+s - 1) : scrollTo({ top: 0 }); return; }
    const [c, ...rest] = s.split(/\s+/);
    const f = COMMANDS[c];
    if (f) f(rest.join(" ")); else say(`E492: Not an editor command: ${s}`, true);
  };

  const openPrompt = (ch) => {
    setMode(ch === ":" ? "COMMAND" : "SEARCH");
    msg.textContent = "";
    $("#cmd-pfx").textContent = ch;
    cmd.value = ""; cmd.hidden = false; cmd.focus();
  };
  const closePrompt = () => { cmd.hidden = true; cmd.blur(); $("#cmd-pfx").textContent = ""; setMode("NORMAL"); };

  cmd.addEventListener("keydown", (e) => {
    if (e.key === "Escape") { e.preventDefault(); closePrompt(); return; }
    if (e.key === "Enter") {
      e.preventDefault();
      const kind = $("#cmd-pfx").textContent, v = cmd.value;
      closePrompt();
      kind === ":" ? run(v) : search(v);
    }
  });
  cmd.addEventListener("input", () => { if ($("#cmd-pfx").textContent === "/" && rows.length) search(cmd.value); });

  // ── help ──
  const help = $("#help");
  const toggleHelp = (on) => help.classList.toggle("on", on ?? !help.classList.contains("on"));
  help.addEventListener("click", (e) => { if (e.target === help) toggleHelp(false); });

  // ── mobile ":" button ──
  const kb = $("#kbtn"); if (kb) kb.addEventListener("click", () => openPrompt(":"));

  // ── normal-mode keys ──
  addEventListener("keydown", (e) => {
    if (e.target === cmd) return;
    if (e.metaKey || e.altKey) return;
    if (help.classList.contains("on")) { if (e.key === "Escape" || e.key === "q" || e.key === "?") toggleHelp(false); return; }
    const k = e.key;
    if (e.ctrlKey) {
      if (k === "d") { e.preventDefault(); rows.length ? highlight(cur + 5) : scrollBy(page()); }
      else if (k === "u") { e.preventDefault(); rows.length ? highlight(cur - 5) : scrollBy(-page()); }
      return;
    }
    if (pending === "g") {
      pending = "";
      if (k === "g") { rows.length ? highlight(0) : scrollTo({ top: 0, behavior: "smooth" }); return; }
    }
    switch (k) {
      case "j": case "ArrowDown": if (rows.length) { e.preventDefault(); highlight(cur + 1); } else if (k === "j") scrollBy(60); break;
      case "k": case "ArrowUp": if (rows.length) { e.preventDefault(); highlight(cur - 1); } else if (k === "k") scrollBy(-60); break;
      case "G": rows.length ? highlight(visible().length - 1) : scrollTo({ top: document.documentElement.scrollHeight, behavior: "smooth" }); break;
      case "g": pending = "g"; setTimeout(() => (pending = ""), 600); break;
      case "Enter": case "l": if (rows.length) { e.preventDefault(); open(); } break;
      case "h": case "-": case "Backspace": if (!rows.length) { e.preventDefault(); back(); } break;
      case "n": if (rows.length && lastSearch) highlight(cur + 1); break;
      case "N": if (rows.length && lastSearch) highlight(cur - 1); break;
      case ":": e.preventDefault(); openPrompt(":"); break;
      case "/": e.preventDefault(); openPrompt("/"); break;
      case "?": toggleHelp(); break;
      case "t": { const i = THEMES.indexOf(document.documentElement.dataset.theme); const nx = THEMES[(i + 1) % THEMES.length]; setTheme(nx); say("colorscheme " + nx); break; }
      case "Escape": search(""); say(""); break;
    }
  });

  say(rows.length ? "type  ?  for keys  ·  j/k move  ·  enter open  ·  :help" : "j/k scroll  ·  h back  ·  gg/G  ·  ?  help");
})();
