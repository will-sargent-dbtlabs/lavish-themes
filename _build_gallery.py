#!/usr/bin/env python3
"""Build _gallery.html by inlining tier1/*.html and tier2/*.html as iframe srcdoc.

Run after editing any theme shell:
    python3 _build_gallery.py

The gallery becomes a single self-contained file so it works under
lavish-axi (which serves only one file) AND via direct `open` (file://).
"""
from html import escape
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parent

# Order + metadata for each theme card in the gallery.
THEMES = [
    # (slug, dir, label, blurb, docs_url)
    ("latex",       "tier1", "latex",       "Academic paper. Latin Modern, immaculate hierarchy. Briefs that should feel like research.", "https://latex.vercel.app/"),
    ("terminal",    "tier1", "terminal",    "Monospace terminal stationery. Postmortems, runbooks, RFCs.", "https://terminalcss.xyz/"),
    ("water",       "tier1", "water",       "Neutral, tasteful, auto dark/light. The 'makes any HTML look decent' pick.", "https://watercss.kognise.dev/"),
    # Tier 2 hand-built themes.
    ("swiss",       "tier2", "swiss",       "International typographic. Helvetica/Inter, black/red/white grid, flush-left.", ""),
    ("lavish-light","tier2", "lavish-light","Softened Swiss. Dark gray on near-white, hairline rules, light code blocks. The default \u2014 decisive but easy on the eyes.", ""),
    ("handwritten", "tier2", "handwritten", "Lined exercise book + Caveat. Notebook feel.", ""),
    ("zine",        "tier2", "zine",        "High-contrast yellow/black/magenta. Clip-path angles. Distressed shouty.", ""),
]

GALLERY_CSS = dedent("""
    :root {
      --bg: #0f1115;
      --panel: #14171d;
      --fg: #f7f3ea;
      --muted: #8a8675;
      --accent: #f4c95d;
      --border: #2a2d35;
    }
    * { box-sizing: border-box; }
    html, body { margin: 0; padding: 0; background: var(--bg); color: var(--fg); font-family: ui-sans-serif, system-ui, -apple-system, "Geist", "Inter", sans-serif; -webkit-font-smoothing: antialiased; }
    header.gallery-head {
      position: sticky; top: 0; z-index: 20;
      background: rgba(15, 17, 21, 0.92);
      backdrop-filter: saturate(140%) blur(8px);
      border-bottom: 1px solid var(--border);
      padding: 14px 24px;
      display: grid; grid-template-columns: minmax(0,1fr) auto; gap: 12px; align-items: baseline;
    }
    .title { display: flex; align-items: baseline; gap: 14px; min-width: 0; }
    .title h1 { font-family: "EB Garamond", "Iowan Old Style", Georgia, serif; font-style: italic; font-weight: 500; margin: 0; font-size: 1.4rem; color: var(--accent); letter-spacing: 0.01em; }
    .title .sub { color: var(--muted); font-size: 0.85rem; }
    nav.jump { display: flex; flex-wrap: wrap; gap: 6px; justify-content: flex-end; }
    nav.jump a {
      color: var(--fg); text-decoration: none;
      border: 1px solid var(--border); border-radius: 999px;
      padding: 4px 12px; font-size: 0.78rem; font-family: ui-monospace, "Geist Mono", SFMono-Regular, Menlo, monospace;
      background: var(--panel); transition: border-color 0.15s, color 0.15s;
    }
    nav.jump a:hover { color: var(--accent); border-color: var(--accent); }
    main { padding: 32px 24px 80px; max-width: 1400px; margin: 0 auto; }
    section.sample { margin: 0 0 48px; }
    section.sample header.label {
      display: grid; grid-template-columns: minmax(0,1fr) auto; gap: 12px; align-items: baseline;
      margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px dashed var(--border);
    }
    section.sample .name {
      font-family: ui-monospace, "Geist Mono", SFMono-Regular, Menlo, monospace;
      font-size: 0.95rem; color: var(--accent); letter-spacing: 0.04em; text-transform: uppercase;
    }
    section.sample .blurb { color: var(--muted); font-size: 0.85rem; font-style: italic; min-width: 0; overflow-wrap: anywhere; }
    section.sample .actions { display: flex; gap: 10px; align-items: baseline; }
    section.sample .actions a { color: var(--muted); font-size: 0.75rem; text-decoration: none; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; border: 1px solid var(--border); padding: 3px 9px; border-radius: 999px; }
    section.sample .actions a:hover { color: var(--accent); border-color: var(--accent); }
    section.sample iframe {
      width: 100%; height: 900px; border: 1px solid var(--border); border-radius: 6px;
      background: #fff;
      box-shadow: 0 24px 60px -30px rgba(0,0,0,0.6);
    }
    footer.gallery-foot { color: var(--muted); font-size: 0.8rem; text-align: center; padding: 24px; border-top: 1px solid var(--border); }
    footer.gallery-foot code { background: var(--panel); border: 1px solid var(--border); padding: 2px 6px; border-radius: 4px; font-size: 0.78rem; color: var(--fg); }
""").strip()


def build():
    sections = []
    nav_links = []
    for slug, subdir, label, blurb, docs in THEMES:
        shell_path = ROOT / subdir / f"{slug}.html"
        if not shell_path.exists():
            print(f"  skip: {shell_path.relative_to(ROOT)} (not yet authored)")
            continue
        shell_html = shell_path.read_text(encoding="utf-8")
        # Escape so the whole document can live inside srcdoc="..."
        srcdoc = escape(shell_html, quote=True)
        nav_links.append(f'    <a href="#{slug}">{label}</a>')
        docs_link = f'\n        <a href="{escape(docs)}" target="_blank" rel="noopener">docs ↗</a>' if docs else ""
        sections.append(f'''
  <section class="sample" id="{slug}">
    <header class="label">
      <div>
        <div class="name">{label}</div>
        <div class="blurb">{escape(blurb)}</div>
      </div>
      <div class="actions">
        <a href="{subdir}/{slug}.html" target="_blank" rel="noopener">open standalone ↗</a>{docs_link}
      </div>
    </header>
    <iframe srcdoc="{srcdoc}" loading="lazy" title="{label} sample"></iframe>
  </section>''')

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="lavish-design" content="off">
<title>Lavish theme gallery</title>
<style>
{GALLERY_CSS}
</style>
</head>
<body>

<header class="gallery-head">
  <div class="title">
    <h1>Lavish theme gallery</h1>
    <span class="sub">Self-contained themes, identical sample content. Scroll &amp; pick.</span>
  </div>
  <nav class="jump">
{chr(10).join(nav_links)}
  </nav>
</header>

<main>
{''.join(sections)}
</main>

<footer class="gallery-foot">
  Generated by <code>_build_gallery.py</code>. Re-run after editing any shell. See <code>README.md</code>.
</footer>

</body>
</html>
"""
    out = ROOT / "_gallery.html"
    out.write_text(html, encoding="utf-8")
    print(f"  wrote: {out.relative_to(ROOT.parent)}  ({len(html):,} bytes, {len(sections)} themes)")


if __name__ == "__main__":
    build()
