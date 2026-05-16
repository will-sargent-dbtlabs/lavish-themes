# Lavish theme library

A small library of self-contained HTML/CSS themes the `publish` skill (and any ad-hoc artifact authoring) can pick from. Built because the Lavish brand kit alone is one look, and DaisyUI's themes blur into one DaisyUI look.

Six themes, deliberately distinct from each other.

## Tier 1 — vendored from upstream

The CSS lives inline in each shell. No external CDN dep at view time.

| Slug | Aesthetic | Best for | Vendored from |
|---|---|---|---|
| `latex` | Academic paper, Latin Modern | Briefs that should feel like research | `latex.vercel.app/style.css` + LM woff2 fonts base64-inlined |
| `terminal` | Monospace terminal stationery | Postmortems, runbooks, RFCs | `terminal.css@0.7.4` |
| `water` | Neutral classless, auto dark/light | General briefs | `water.css@2` |

Refresh from upstream any time with `python3 _vendor_tier1.py`.

## Tier 2 — hand-built (inline styles)

Authored in this repo, no external dependency beyond Google Fonts:

| Slug | Aesthetic | Best for |
|---|---|---|
| `swiss` | International typographic. Inter Tight, black/red/white grid, flush-left. | Decisive product/strategy briefs |
| `handwritten` | Lined exercise book + Caveat + Permanent Marker. Warm paper. | Personal notes, casual writing |
| `zine` | Yellow / black / magenta. Anton display. Clip-path angles, hard shadows. | Loud manifestos, launches |

## Browse

Open the gallery to see them side-by-side:

```
open <repo>/themes/_gallery.html
```

Works in any browser, no server needed. Also works under `lavish-axi <file>` if you want the editor chrome around it.

The gallery iframes use `srcdoc` (inlined HTML), so sibling shells don't need to be fetched - everything is in one file.

## File layout

```
templates/
├── README.md           # this file
├── _build_gallery.py   # regenerates _gallery.html from tier1/* + tier2/*
├── _vendor_tier1.py    # refreshes tier1 CSS from upstream (no runtime CDN dep)
├── _gallery.html       # generated; do not edit by hand
├── tier1/              # CSS vendored inline; only Google Fonts external
│   ├── latex.html
│   ├── terminal.html
│   └── water.html
└── tier2/              # hand-built inline styles; only Google Fonts external
    ├── swiss.html
    ├── handwritten.html
    └── zine.html
```

After editing any shell, rebuild the gallery:

```
python3 <repo>/themes/_build_gallery.py
```

To add a new template: drop the HTML in `tier1/` or `tier2/`, add a line to the `THEMES = [...]` list in `_build_gallery.py`, re-run the script.

## Conventions

- Each Tier 1 shell loads its framework via public HTTPS CDN. The publish-cloudflare worker CSP `style-src 'self' 'unsafe-inline' https:` allows this.
- No JavaScript anywhere. `script-src 'none'` blocks it on the worker, and these themes don't need it.
- Sample content in each shell is identical so themes are directly comparable. When adapting a shell into a real page, replace the body content but keep the theme-specific markup conventions (e.g. Tufte's `<article>` wrapping, MVP's nested `<section>` headers, YoRHa's class hooks).

## Compatibility with lavish-axi auto-injection

Every shell (and the gallery itself) carries `<meta name="lavish-design" content="off">` in its `<head>`. This tells `lavish-axi` to skip its Tailwind/DaisyUI injection so each theme renders cleanly without DaisyUI cascading on top of it.

If you derive a real page from one of these shells and want DaisyUI back, just delete that meta tag.

## Tier 2 (planned)

- **Swiss / international typographic** - CSS Grid + Inter/Helvetica + black/red/white, flush-left.
- **Handwritten / lined paper** - Caveat/Reenie Beanie + `repeating-linear-gradient`.
- **Zine / cyberpunk** - Yellow/black/magenta, clip-path panels, distressed.
