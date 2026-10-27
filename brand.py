"""SkinSense brand system - palette, logo, loader and CSS.

Lifted from the SkinSense Space so the two apps are visually one product.
The loader and fonts live in HEAD_HTML because Gradio only injects CSS once
the app mounts, and the loader has to cover the boot screen before that.
"""

# ── Palette: espresso / coffee / caramel / tan / cream ──────────────────────────
FOREST  = "#3B2A20"   # espresso - primary brand, buttons, headers
PINE    = "#5A3E2B"   # coffee - hover / gradient partner
EMERALD = "#8A5A36"   # brown - accents, positive status
JADE    = "#B07A4A"   # caramel - highlights, gradients
MINT    = "#F3E8DA"   # latte fill
MIST    = "#FAF5EE"   # page background
WHITE   = "#FFFFFF"
INK     = "#2A1D15"   # primary text
SUBTLE  = "#6E5645"   # secondary text
FAINT   = "#8E7563"   # tertiary text
LINE    = "#E9DCCB"   # borders
FILL    = "#F6EEE3"   # soft fill
CARD    = WHITE
PAGE    = MIST

GOOD  = "#5E7A3E"     # olive - passed validation
AMBER = "#B07D18"     # fallback fired
RED   = "#B3402F"     # refused

FONT_STACK = ["Geist", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"]


def logo_svg(size=40, gid="a", light=False):
    """SkinSense mark: a scan ring around a leaf-droplet."""
    c1 = "#E6C9A3" if light else JADE
    c2 = "#B07A4A" if light else FOREST
    ring = "#EAD7BE" if light else EMERALD
    vein = "#3B2A20" if light else "#FFFFFF"
    return (
        '<svg width="' + str(size) + '" height="' + str(size) + '" viewBox="0 0 48 48" '
        'fill="none" xmlns="http://www.w3.org/2000/svg" style="flex-shrink:0;display:block;">'
        '<defs><linearGradient id="ssl' + gid + '" x1="10" y1="8" x2="38" y2="42" '
        'gradientUnits="userSpaceOnUse">'
        '<stop stop-color="' + c1 + '"/><stop offset="1" stop-color="' + c2 + '"/>'
        '</linearGradient></defs>'
        '<circle cx="24" cy="24" r="21.2" stroke="' + ring + '" stroke-width="2.4" '
        'stroke-linecap="round" stroke-dasharray="88 22"/>'
        '<path d="M24 9.5c6.4 4.6 10.6 10.2 10.6 15.6 0 6-4.7 10.4-10.6 10.4S13.4 31.1 13.4 25.1'
        'c0-5.4 4.2-11 10.6-15.6z" fill="url(#ssl' + gid + ')"/>'
        '<path d="M24 15.5v15.8" stroke="' + vein + '" stroke-width="1.5" '
        'stroke-linecap="round" opacity="0.9"/>'
        '<path d="M24 22.6l4.4-3.6M24 27.4l-4.4-3.6" stroke="' + vein + '" stroke-width="1.5" '
        'stroke-linecap="round" opacity="0.9"/>'
        '</svg>'
    )


def wordmark(size=40, gid="a", light=False, sub=""):
    ink = "#FFFFFF" if light else INK
    dim = "#CDB49A" if light else FAINT
    html = (
        '<div style="display:flex;align-items:center;gap:11px;">'
        + logo_svg(size, gid, light) +
        '<div style="line-height:1.05;">'
        '<div style="font-size:' + str(round(size * 0.44, 2)) + 'px;font-weight:750;'
        'color:' + ink + ';letter-spacing:-0.025em;">Skin<span style="color:'
        + (JADE if not light else "#E6C9A3") + ';">Sense</span></div>'
    )
    if sub:
        html += ('<div style="font-size:' + str(round(size * 0.2, 2)) + 'px;color:' + dim + ';'
                 'letter-spacing:0.16em;text-transform:uppercase;margin-top:3px;font-weight:600;">'
                 + sub + '</div>')
    html += '</div></div>'
    return html


FORCE_LIGHT_JS = """
() => {
    function forceLight() {
        document.documentElement.classList.remove('dark');
        document.body.classList.remove('dark');
    }
    forceLight();
    setTimeout(forceLight, 300);
    setTimeout(forceLight, 1000);
    return [];
}
"""

# Fonts and the full-screen loader, identical to the SkinSense Space.
HEAD_HTML = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700;800&family=Geist+Mono:wght@500;600&display=swap" rel="stylesheet">
<style>
.ss-loader {
  position: fixed; inset: 0; z-index: 2147483000;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  background: radial-gradient(120% 90% at 50% 42%, #5A3E2B 0%, #3B2A20 55%, #2A1D15 100%);
  font-family: "Geist", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  opacity: 0; visibility: hidden;
  transition: opacity 0.22s ease, visibility 0s linear 0.22s;
}
.ss-loader.ss-loader-on { opacity: 1; visibility: visible; transition: opacity 0.22s ease; }
.ss-loader-mark {
  width: 104px; height: 104px; display: block;
  filter: drop-shadow(0 0 22px rgba(176, 122, 74, 0.35));
}
.ss-ld-ring { transform-box: fill-box; transform-origin: center;
              animation: ss-ld-spin 2.8s linear infinite; }
.ss-ld-wave { animation: ss-ld-sweep 1.6s cubic-bezier(0.45, 0, 0.25, 1) infinite; }
.ss-ld-leaf { fill: #6E4B33; animation: ss-ld-blink 1.6s ease-in-out infinite; }
.ss-loader-word { margin-top: 20px; font-size: 1.4rem; font-weight: 750;
                  letter-spacing: -0.025em; color: #F3E8DA; }
.ss-loader-word span { color: #E6C9A3; }
.ss-loader-msg { margin-top: 8px; min-height: 1.2em; font-size: 0.84rem;
                 letter-spacing: 0.04em; color: #CDB49A; }
@keyframes ss-ld-spin { to { transform: rotate(360deg); } }
@keyframes ss-ld-sweep { 0% { transform: translateY(-18px); }
                         70%, 100% { transform: translateY(40px); } }
@keyframes ss-ld-blink { 0%, 55% { fill: #6E4B33; } 72% { fill: #B07A4A; } 100% { fill: #6E4B33; } }
@media (prefers-reduced-motion: reduce) {
  .ss-ld-ring, .ss-ld-wave { animation: none; }
  .ss-ld-wave { transform: translateY(14px); }
  .ss-ld-leaf { animation-duration: 2.4s; }
}
</style>
<script>
/* Full-screen loader. Covers first load until the app has drawn. Waits under
   250 ms never show it; once up it stays at least 450 ms so the wave reads. */
(function () {
  var LEAF = 'M24 9.5c6.4 4.6 10.6 10.2 10.6 15.6 0 6-4.7 10.4-10.6 10.4S13.4 31.1 13.4 25.1' +
             'c0-5.4 4.2-11 10.6-15.6z';
  var MARK = '<svg class="ss-loader-mark" viewBox="0 0 48 48" fill="none" aria-hidden="true">' +
    '<defs><clipPath id="ss-ld-clip"><path d="' + LEAF + '"/></clipPath>' +
    '<linearGradient id="ss-ld-grad" x1="0" y1="0" x2="0" y2="1">' +
    '<stop offset="0" stop-color="#B07A4A" stop-opacity="0"/>' +
    '<stop offset="0.38" stop-color="#C9935F"/><stop offset="0.5" stop-color="#F3E8DA"/>' +
    '<stop offset="0.62" stop-color="#C9935F"/>' +
    '<stop offset="1" stop-color="#B07A4A" stop-opacity="0"/></linearGradient></defs>' +
    '<circle class="ss-ld-ring" cx="24" cy="24" r="21.2" stroke="#8A5A36" stroke-width="2.4" ' +
    'stroke-linecap="round" stroke-dasharray="88 22"/>' +
    '<path class="ss-ld-leaf" d="' + LEAF + '" fill="#6E4B33"/>' +
    '<g clip-path="url(#ss-ld-clip)"><rect class="ss-ld-wave" x="8" y="0" width="32" ' +
    'height="18" fill="url(#ss-ld-grad)"/></g>' +
    '<path d="M24 15.5v15.8M24 22.6l4.4-3.6M24 27.4l-4.4-3.6" stroke="#2A1D15" ' +
    'stroke-width="1.5" stroke-linecap="round" opacity="0.85"/></svg>';
  var el, msg, depth = 0, delay = null, fade = null, guard = null, since = 0;

  function build() {
    el = document.createElement('div');
    el.className = 'ss-loader';
    el.setAttribute('role', 'status');
    el.setAttribute('aria-live', 'polite');
    el.innerHTML = MARK + '<div class="ss-loader-word">Skin<span>Sense</span></div>' +
      '<div class="ss-loader-msg"></div>';
    msg = el.lastChild;
    (document.body || document.documentElement).appendChild(el);
  }
  function up() { delay = null; since = Date.now(); el.classList.add('ss-loader-on'); }
  function down() {
    clearTimeout(delay); delay = null; clearTimeout(guard);
    fade = setTimeout(function () { el.classList.remove('ss-loader-on'); },
                      Math.max(0, 450 - (Date.now() - since)));
  }
  function show(text, now) {
    if (!el) { build(); }
    depth += 1;
    msg.textContent = text || 'Just a moment…';
    clearTimeout(fade); clearTimeout(guard);
    guard = setTimeout(function () { depth = 0; down(); }, 60000);
    if (el.classList.contains('ss-loader-on') || delay) { return; }
    if (now) { up(); } else { delay = setTimeout(up, 250); }
  }
  function hide() { if (!el || !depth) { return; } depth -= 1; if (!depth) { down(); } }
  window.ssLoader = { show: show, hide: hide };

  var started = Date.now();
  show('Loading SkinSense…', true);
  (function ready() {
    if (document.querySelector('.gradio-container .html-container') ||
        Date.now() - started > 15000) { hide(); return; }
    setTimeout(ready, 100);
  })();
})();
</script>
"""

REVEAL_JS = """
() => {
  document.documentElement.classList.add('ss-js');
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var io = ('IntersectionObserver' in window) ? new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (en.isIntersecting) { en.target.classList.add('ss-in'); io.unobserve(en.target); }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }) : null;
  function scan() {
    document.querySelectorAll('.ss-reveal:not(.ss-seen)').forEach(function (el) {
      el.classList.add('ss-seen');
      if (!io || reduce) { el.classList.add('ss-in'); } else { io.observe(el); }
    });
  }
  new MutationObserver(scan).observe(document.documentElement, { childList: true, subtree: true });
  scan();
  return [];
}
"""

SHOW_LOADER_JS = ('() => { window.ssLoader && window.ssLoader.show("Reading the reference…"); '
                  'return []; }')
HIDE_LOADER_JS = "() => { window.ssLoader && window.ssLoader.hide(); return []; }"


CSS = f"""
.gradio-container {{
    background: {PAGE} !important;
    font-family: "Geist", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
    max-width: 1080px !important;
    color: {INK} !important;
}}

/* Header band */
#ss-header {{
    background: linear-gradient(135deg, {FOREST} 0%, {PINE} 55%, {EMERALD} 100%);
    border-radius: 17px; padding: 24px 28px; margin-bottom: 8px;
    box-shadow: 0 10px 22px -12px rgba(59,42,32,0.55);
}}
#ss-header .ss-tag {{
    color: #CDB49A; font-size: 0.79rem; line-height: 1.65; margin-top: 11px; max-width: 72ch;
}}
#ss-header a {{ color: #E6C9A3; text-decoration: underline; }}

/* Cards */
.block, .form, .gr-box {{
    background: {CARD} !important;
    border: 1px solid {LINE} !important;
    border-radius: 17px !important;
    transition: box-shadow 0.25s ease, border-color 0.25s ease;
}}
.tabs, .tabitem {{ border-color: {LINE} !important; }}
input[type="range"] {{ accent-color: {EMERALD} !important; }}
.gradio-container, :root {{
    --slider-color: {EMERALD} !important;
    --color-accent: {EMERALD} !important;
    --color-accent-soft: {FILL} !important;
}}
button.selected {{ color: {FOREST} !important; border-bottom-color: {JADE} !important; }}

/* Primary button - pill, matching SkinSense */
.gr-button-primary, button.primary {{
    background: linear-gradient(135deg, {FOREST} 0%, {EMERALD} 100%) !important;
    color: {WHITE} !important; border: none !important; border-radius: 100px !important;
    font-size: 0.9rem !important; font-weight: 700 !important; letter-spacing: 0.015em !important;
    padding: 15px 24px !important;
    box-shadow: 0 10px 22px -12px rgba(59,42,32,0.55) !important;
}}
.gr-button-primary:hover, button.primary:hover {{ opacity: 0.93 !important; }}

/* Inputs */
input, textarea, select, .wrap-inner {{
    background: {WHITE} !important; border-color: {LINE} !important; color: {INK} !important;
    border-radius: 12px !important;
}}
input:focus, textarea:focus {{
    border-color: {EMERALD} !important;
    box-shadow: 0 0 0 3px rgba(138,90,54,0.14) !important;
}}

/* Validation trace */
#ss-trace textarea, #ss-trace2 textarea {{
    background: {FILL} !important; border: 1.6px dashed #D2B895 !important;
    font-family: "Geist Mono", ui-monospace, Consolas, monospace !important;
    font-size: 12px !important; color: {SUBTLE} !important;
}}

/* Disclaimer footer, mirroring DASH_FOOTER */
#ss-note {{
    text-align: center; padding: 34px 0 22px; margin-top: 16px;
    border-top: 1px solid {LINE};
}}
#ss-note p {{
    font-size: 0.72rem; color: {FAINT}; line-height: 1.8;
    margin: 12px auto 0; max-width: 620px;
}}
#ss-note .ss-mark {{ display: flex; justify-content: center; }}

/* Kill Gradio's own progress readout - the loader replaces it */
.gradio-container .meta-text,
.gradio-container .meta-text-center,
.gradio-container .progress-text,
.gradio-container .eta-bar,
.gradio-container .progress-level,
.gradio-container .progress-level-inner,
.gradio-container .clear-status {{ display: none !important; }}
.gradio-container .wrap.generating,
.gradio-container .wrap.loading {{
    opacity: 0 !important; background: transparent !important; pointer-events: none !important;
}}
.gradio-container .generating {{ border-color: transparent !important; box-shadow: none !important; }}

/* Cards lift on hover, and sections slide up as they enter view - both
   lifted from SkinSense so the motion language matches. */
.ss-card {{ transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease; }}
.ss-card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 18px 40px -22px rgba(59,42,32,0.45);
    border-color: #D9C4AE !important;
}}
.ss-js .ss-reveal {{
    opacity: 0; transform: translateY(24px);
    transition: opacity 0.7s cubic-bezier(.2,.7,.2,1), transform 0.7s cubic-bezier(.2,.7,.2,1);
}}
.ss-js .ss-reveal.ss-in {{ opacity: 1; transform: none; }}

/* Micro-label: the uppercase caramel kicker used across SkinSense */
.ss-kicker {{
    font-size: 0.66rem; letter-spacing: 0.1em; color: {EMERALD};
    text-transform: uppercase; margin: 0 0 12px; font-weight: 750;
}}
.ss-panel {{
    background: {WHITE}; border: 1px solid {LINE}; border-radius: 17px; padding: 19px 21px;
}}
.ss-panel p {{ font-size: 0.79rem; color: {SUBTLE}; line-height: 1.7; margin: 0; }}

/* Outcome chips on the validation trace */
.ss-chip {{
    display: inline-flex; align-items: center; gap: 7px; border-radius: 100px;
    padding: 5px 13px; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.02em;
}}
.ss-chip-ok {{ background: rgba(94,122,62,0.12); color: {GOOD}; }}
.ss-chip-fallback {{ background: rgba(176,125,24,0.13); color: {AMBER}; }}
.ss-chip-refused {{ background: rgba(179,64,47,0.11); color: {RED}; }}
.ss-chip-detail {{ font-size: 0.72rem; color: {FAINT}; margin-top: 8px; line-height: 1.6; }}

@media (prefers-reduced-motion: reduce) {{
    .ss-card {{ transition: none !important; }}
    .ss-js .ss-reveal {{ opacity: 1 !important; transform: none !important; transition: none !important; }}
}}

footer {{ display: none !important; }}

@media (max-width: 640px) {{
    #ss-header {{ padding: 20px 18px; }}
}}
"""
