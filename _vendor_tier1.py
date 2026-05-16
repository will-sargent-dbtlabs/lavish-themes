#!/usr/bin/env python3
"""Vendor Tier 1 framework CSS into the local shells.

After this runs, each tier1/<slug>.html embeds the framework's CSS in an
inline <style> block - no external CDN dependency. For LaTeX.css, the Latin
Modern woff2 fonts are also fetched and base64-inlined as data: URIs.

Re-run any time you want to refresh from upstream:
    python3 _vendor_tier1.py
"""
from __future__ import annotations

import base64
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SHELLS = ROOT / "tier1"

# (slug, source URL, pinned version for the audit comment)
SOURCES = {
    "latex":    ("https://latex.vercel.app/style.css",                                        "latex.vercel.app (unversioned upstream)"),
    "terminal": ("https://unpkg.com/terminal.css@0.7.4/dist/terminal.min.css",                "terminal.css@0.7.4"),
    "water":    ("https://cdn.jsdelivr.net/npm/water.css@2/out/water.css",                    "water.css@2 (latest)"),
}

# Latin Modern woff2 fonts referenced by latex.css. Modern browsers (Safari 14+,
# Chrome 36+, FF 39+) all support woff2 natively, so we drop the woff/ttf fallbacks.
LM_FONTS = {
    "LM-regular":     "https://latex.vercel.app/fonts/LM-regular.woff2",
    "LM-italic":      "https://latex.vercel.app/fonts/LM-italic.woff2",
    "LM-bold":        "https://latex.vercel.app/fonts/LM-bold.woff2",
    "LM-bold-italic": "https://latex.vercel.app/fonts/LM-bold-italic.woff2",
}


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "lavish-vendor/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def inline_lm_fonts(css: str) -> str:
    """Replace the 12 LM font url() refs (woff2 + woff + ttf, x4 weights) with
    a single base64-inlined woff2 per weight. The @font-face blocks themselves
    are rewritten to have only one src."""
    # Download all woff2 fonts once.
    blobs: dict[str, str] = {}
    for name, url in LM_FONTS.items():
        b = fetch(url)
        blobs[name] = base64.b64encode(b).decode("ascii")
        print(f"    fetched {name}.woff2  ({len(b):,} bytes -> {len(blobs[name]):,} base64)")

    # Rewrite every @font-face block.
    def replace_face(match: re.Match) -> str:
        block = match.group(0)
        # Find the LM-<weight> name in the block via the url('./fonts/LM-XXX.woff2') ref.
        font_match = re.search(r"\./fonts/(LM-[a-z-]+)\.woff2", block)
        if not font_match:
            return block  # shouldn't happen
        name = font_match.group(1)
        b64 = blobs[name]
        # Replace the entire `src: ...;` line(s) with a single woff2 data URI.
        # Match: src: url('...woff2') format('woff2'), url('...woff') format('woff'), url('...ttf') format('truetype');
        new_block = re.sub(
            r"src:\s*[^;]+;",
            f"src: url('data:font/woff2;base64,{b64}') format('woff2');",
            block,
            count=1,
            flags=re.DOTALL,
        )
        return new_block

    return re.sub(r"@font-face\s*\{[^}]*\}", replace_face, css, flags=re.DOTALL)


def vendor_shell(slug: str, css: str, source_label: str) -> None:
    shell_path = SHELLS / f"{slug}.html"
    html = shell_path.read_text(encoding="utf-8")

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    style_block = (
        f'<style>\n'
        f'/* Vendored from {source_label} on {stamp}. Re-run _vendor_tier1.py to refresh. */\n'
        f'{css}\n'
        f'</style>'
    )

    # Replace either an existing <link rel="stylesheet" ...> for this framework
    # OR a previously vendored <style>...vendored.../style> block.
    # Use a lambda so re.sub treats `style_block` as a literal (CSS may contain
    # backslash escapes like \003e that look like regex back-references).
    new_html, n_link = re.subn(
        r'<link rel="stylesheet" href="[^"]+"[^>]*>',
        lambda _m: style_block,
        html,
        count=1,
    )
    if n_link == 0:
        # Already vendored - replace the existing inline block.
        new_html, n_style = re.subn(
            r'<style>\s*/\* Vendored from [^*]*\*/.*?</style>',
            lambda _m: style_block,
            html,
            count=1,
            flags=re.DOTALL,
        )
        if n_style == 0:
            print(f"    ! could not locate <link> or prior vendored <style> in {shell_path.name}")
            return

    shell_path.write_text(new_html, encoding="utf-8")
    print(f"    wrote {shell_path.relative_to(ROOT.parent)}  ({len(new_html):,} bytes)")


def main() -> None:
    for slug, (url, label) in SOURCES.items():
        print(f"[{slug}] {url}")
        raw = fetch(url).decode("utf-8")
        if slug == "latex":
            print(f"    inlining Latin Modern woff2 fonts")
            raw = inline_lm_fonts(raw)
        vendor_shell(slug, raw, label)


if __name__ == "__main__":
    main()
