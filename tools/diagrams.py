#!/usr/bin/env python3
"""Three ways to draw a system, so a topic page can show all three.

The site already had one diagram per topic: a layered block diagram, which
answers "what are the pieces and roughly in what order do they stack". That is
the high-level view and content_page.diagram() still draws it.

Two views were missing, and they are the two a reader actually needs when the
high-level picture has stopped helping:

  detail()  LOW LEVEL — open one box from the high-level diagram and show what
            is inside it, with the interfaces on its edges named. The question
            it answers is "what is actually in kube-proxy / the page cache /
            the Envoy sidecar, and what does it talk to".

  flow()    CONNECTION — follow one request, or one piece of data, along the
            path it really takes, with the protocol and the port on each hop.
            The question it answers is "where does my packet go, and which hop
            is the one that dropped it".

WHY SVG BY HAND AND NOT A LIBRARY
---------------------------------
The colophon says this site loads nothing from a CDN, and that is worth more
than the convenience of Mermaid. These renderers emit plain SVG with CSS
classes, which means the diagrams theme themselves: a node is `class="dg-node
n-core"` and the dark-mode rule in the stylesheet recolours it. A rendered PNG
would need two copies and would still be wrong at the reader's zoom level.

TEXT IS MEASURED, NOT GUESSED
-----------------------------
Every label is wrapped against the real advance width of DM Mono at the size
it is drawn. Getting this wrong is how diagrams end up with text hanging out
of boxes, and it is invisible to whoever wrote the spec because their label
happened to be short.
"""
import html

# DM Mono is monospaced, so one advance width per size is exact rather than an
# estimate. 0.605em is measured from the font, not guessed.
ADV = 0.605

ROLES = ("core", "warm", "hot", "go", "calm", "plain")

# fill, stroke, light-mode text — same palette as content_page.ACCENT so the
# three diagram kinds read as one family.
ACCENT = {
    "core":  ("rgba(0,194,212,.14)",  "#00c2d4",              "#066c77"),
    "warm":  ("rgba(245,158,11,.14)", "rgba(245,158,11,.6)",  "#8a5806"),
    "hot":   ("rgba(229,57,53,.13)",  "rgba(229,57,53,.55)",  "#a32b28"),
    "go":    ("rgba(132,204,22,.16)", "#84cc16",              "#3f6f0c"),
    "calm":  ("rgba(124,58,237,.12)", "rgba(124,58,237,.45)", "#5b21b6"),
    # plain must be a token, not a black hairline: rgba(0,0,0,.2) is
    # invisible on a dark background, so those boxes lost their outline
    # entirely in dark mode.
    "plain": ("transparent",          "var(--line-3)",        "var(--muted)"),
}


def esc(s):
    return html.escape(str(s), quote=True)


def _fit(text, width_px, size, max_lines=2):
    """Wrap `text` to fit `width_px` at `size`, honest about overflow."""
    limit = max(4, int((width_px - 14) / (size * ADV)))
    if len(text) <= limit:
        return [text]
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if len(t) <= limit:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
            if len(lines) == max_lines:
                break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if not lines:
        lines = [text[:limit]]
    if len(lines) == max_lines and sum(len(x) for x in lines) + len(lines) - 1 < len(text):
        lines[-1] = lines[-1][:max(3, limit - 1)] + "…"
    return lines


def _box(x, y, w, h, text, role, size=10.5, sub=None):
    fill, line, fg = ACCENT.get(role, ACCENT["plain"])
    dash = ' stroke-dasharray="3 3"' if role == "plain" else ""
    out = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="4" '
           f'fill="{fill}" stroke="{line}"{dash} stroke-width="1"/>']
    lines = _fit(text, w, size)
    block = len(lines) * (size + 1.5) + (11 if sub else 0)
    ty = y + h / 2 - block / 2 + size
    for i, ln in enumerate(lines):
        out.append(f'<text class="dg-node n-{role}" x="{x + w / 2:.1f}" '
                   f'y="{ty + i * (size + 1.5):.1f}" fill="{fg}" '
                   f'font-size="{size}">{esc(ln)}</text>')
    if sub:
        out.append(f'<text class="dg-sub" x="{x + w / 2:.1f}" '
                   f'y="{ty + len(lines) * (size + 1.5) + 7:.1f}">'
                   f'{esc(_fit(sub, w, 8.5, 1)[0])}</text>')
    return "".join(out)


# ═══════════════════════════════════════════════════════════════════════════
# LOW LEVEL — one component, opened up
# ═══════════════════════════════════════════════════════════════════════════
def detail(title, groups, *, label="", inputs=(), outputs=()):
    """Open one box and show its internals.

    groups : [(group_name, [(part, role, one-line-note or None), ...]), ...]
    inputs : labels entering from the left   (what calls this)
    outputs: labels leaving to the right     (what this calls)

    The interfaces matter as much as the internals — a low-level diagram that
    shows the parts but not the edges tells you how something is built without
    telling you how it is reached.
    """
    W = 1000
    PORT_W = 116 if (inputs or outputs) else 0
    GAP = 14
    inner_x = PORT_W + (GAP if PORT_W else 0)
    inner_w = W - inner_x - (PORT_W + GAP if outputs else 0)

    parts, y = [], 40                       # 40 leaves room for the title
    GH, PH, PAD = 22, 52, 12
    for gname, items in groups:
        parts.append(f'<text class="dg-gname" x="{inner_x + PAD}" y="{y + 12:.1f}">'
                     f'{esc(gname.upper())}</text>')
        gy = y + GH
        per_row = min(len(items), 4)
        while per_row > 1 and (inner_w - 2 * PAD - 9 * (per_row - 1)) / per_row < 118:
            per_row -= 1
        rows = [items[i:i + per_row] for i in range(0, len(items), per_row)]
        for ri, row in enumerate(rows):
            n = len(row)
            bw = (inner_w - 2 * PAD - 9 * (n - 1)) / n
            by = gy + ri * (PH + 9)
            for i, item in enumerate(row):
                text, role = item[0], item[1]
                sub = item[2] if len(item) > 2 else None
                parts.append(_box(inner_x + PAD + i * (bw + 9), by, bw, PH, text, role, sub=sub))
        y = gy + len(rows) * PH + (len(rows) - 1) * 9 + 18

    body_h = y - 18 + PAD
    # the enclosing component
    frame = (f'<rect x="{inner_x}" y="24" width="{inner_w}" height="{body_h - 24:.1f}" rx="6" '
             f'fill="none" stroke="var(--line-3)" stroke-width="1.5"/>'
             f'<text class="dg-title" x="{inner_x + PAD}" y="16">{esc(title.upper())}</text>')

    ports = []
    mid = 24 + (body_h - 24) / 2

    def port_column(items, x, arrow_from, arrow_to):
        h = 34
        total = len(items) * h + (len(items) - 1) * 8
        top = mid - total / 2
        for i, t in enumerate(items):
            py = top + i * (h + 8)
            ports.append(f'<rect x="{x}" y="{py:.1f}" width="{PORT_W}" height="{h}" rx="3" '
                         f'fill="var(--wash)" stroke="var(--line-2)" stroke-width="1"/>')
            for j, ln in enumerate(_fit(t, PORT_W, 9, 2)):
                ports.append(f'<text class="dg-port" x="{x + PORT_W / 2:.1f}" '
                             f'y="{py + h / 2 + (4 if len(_fit(t, PORT_W, 9, 2)) == 1 else -1) + j * 10:.1f}">'
                             f'{esc(ln)}</text>')
            ports.append(f'<line class="dg-edge" x1="{arrow_from:.1f}" y1="{py + h / 2:.1f}" '
                         f'x2="{arrow_to:.1f}" y2="{py + h / 2:.1f}" marker-end="url(#dgarrow)"/>')

    if inputs:
        port_column(inputs, 0, PORT_W + 2, inner_x - 3)
    if outputs:
        ox = inner_x + inner_w + GAP
        port_column(outputs, ox, inner_x + inner_w + 2, ox - 3)

    h = body_h + 10
    return (f'<svg class="dg dg-detail" viewBox="0 0 {W} {h:.0f}" role="img" '
            f'aria-label="{esc(label or title)}">{_DEFS}{frame}'
            + "".join(ports) + "".join(parts) + "</svg>")


# ═══════════════════════════════════════════════════════════════════════════
# CONNECTION — one request, hop by hop
# ═══════════════════════════════════════════════════════════════════════════
def flow(hops, *, label="", per_row=4):
    """Follow one request along the path it really takes.

    hops : [(node, role, edge_label_into_this_node or None), ...]

    The edge label is the point of the diagram. "Client -> Ingress -> Service
    -> Pod" is a picture anyone could draw from the docs; "Client -(:443 TLS)->
    Ingress -(:8080 HTTP)-> Service" is the one that tells you which hop to
    tcpdump.
    """
    W = 1000
    BH, GY = 62, 54
    rows = [hops[i:i + per_row] for i in range(0, len(hops), per_row)]
    cols = max(len(r) for r in rows)
    # The gap is set by the longest edge label, not by a constant. With a fixed
    # gap the labels ran over the boxes on either side, which is the failure
    # mode nobody notices until a label happens to be long.
    widest = max((len(h[2]) for h in hops if len(h) > 2 and h[2]), default=0)
    GX = max(56, widest * 8.5 * ADV + 18)
    BW = (W - GX * (cols - 1)) / cols
    parts = []

    for ri, row in enumerate(rows):
        y = ri * (BH + GY)
        rtl = ri % 2 == 1                      # snake, so the line stays continuous
        order = list(range(len(row)))
        for ci, idx in enumerate(order):
            text, role = row[idx][0], row[idx][1]
            edge = row[idx][2] if len(row[idx]) > 2 else None
            slot = (cols - 1 - ci) if rtl else ci
            x = slot * (BW + GX)
            parts.append(_box(x, y, BW, BH, text, role))

            if ci == 0 and ri > 0:
                # elbow down from the previous row's last box
                px = slot * (BW + GX) + BW / 2
                parts.append(f'<path class="dg-edge" d="M {px:.1f} {y - GY} '
                             f'L {px:.1f} {y - 6}" marker-end="url(#dgarrow)"/>')
                if edge:
                    # A label always drawn to the right of the elbow runs off
                    # the canvas when the elbow is in the last column, which is
                    # exactly where a snaking flow puts it on every odd row.
                    right = px > W / 2
                    parts.append(
                        f'<text class="dg-elabel" x="{px + (-8 if right else 8):.1f}" '
                        f'y="{y - GY / 2:.1f}" '
                        f'text-anchor="{"end" if right else "start"}">{esc(edge)}</text>')
            elif ci > 0:
                prev = (cols - 1 - (ci - 1)) if rtl else (ci - 1)
                x1 = prev * (BW + GX) + (0 if rtl else BW)
                x2 = x + (BW if rtl else 0)
                parts.append(f'<line class="dg-edge" x1="{x1 + (-4 if rtl else 4):.1f}" '
                             f'y1="{y + BH / 2:.1f}" x2="{x2 + (4 if rtl else -4):.1f}" '
                             f'y2="{y + BH / 2:.1f}" marker-end="url(#dgarrow)"/>')
                if edge:
                    parts.append(f'<text class="dg-elabel" x="{(x1 + x2) / 2:.1f}" '
                                 f'y="{y + BH / 2 - 9:.1f}">{esc(edge)}</text>')

    h = len(rows) * BH + (len(rows) - 1) * GY + 6
    return (f'<svg class="dg dg-flow" viewBox="0 0 {W} {h:.0f}" role="img" '
            f'aria-label="{esc(label)}">{_DEFS}' + "".join(parts) + "</svg>")


_DEFS = ('<defs><marker id="dgarrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" '
         'markerHeight="7" orient="auto-start-reverse">'
         '<path d="M0 0 L8 4 L0 8 z" fill="var(--line-3)"/></marker></defs>')


# ── the CSS these two need, on top of the .dg rules already shipped ─────────
CSS = """
.dg-detail,.dg-flow{min-width:680px;}
.dg-title{font-family:'Bebas Neue',sans-serif;font-size:14px;letter-spacing:2px;
 fill:var(--heading-fg);}
.dg-gname{font-family:'DM Mono',monospace;font-size:8.5px;letter-spacing:1.8px;
 fill:var(--muted);}
.dg-sub{font-family:'DM Mono',monospace;font-size:8.5px;text-anchor:middle;fill:var(--muted);}
.dg-port{font-family:'DM Mono',monospace;font-size:9px;text-anchor:middle;fill:var(--muted);}
.dg-edge{stroke:var(--line-3);stroke-width:1.3;fill:none;}
.dg-elabel{font-family:'DM Mono',monospace;font-size:8.5px;letter-spacing:.6px;
 text-anchor:middle;fill:var(--muted);}
/* The three views of one system, side by side on wide screens and stacked on
   a phone, each with the question it answers as its heading. */
.dgset{margin:6px 0 4px;}
.dgset-item{margin-bottom:34px;}
.dgset-item:last-child{margin-bottom:0;}
.dgset-h{display:flex;align-items:baseline;gap:12px;margin-bottom:4px;flex-wrap:wrap;}
.dgset-k{font-family:'DM Mono',monospace;font-size:9px;letter-spacing:2px;text-transform:uppercase;
 color:var(--crimson);border:1px solid var(--line-2);border-radius:3px;padding:3px 7px;
 white-space:nowrap;}
.dgset-q{font-family:'Instrument Serif',Georgia,serif;font-style:italic;font-size:15px;
 color:var(--heading-fg);}
.dgscroll{overflow-x:auto;-webkit-overflow-scrolling:touch;padding-bottom:4px;}
"""


def figure(kind, question, svg, caption=""):
    """One diagram with the question it answers stated above it."""
    cap = f'<div class="dg-cap">{caption}</div>' if caption else ""
    return (f'<div class="dgset-item"><div class="dgset-h">'
            f'<span class="dgset-k">{esc(kind)}</span>'
            f'<span class="dgset-q">{esc(question)}</span></div>'
            f'<div class="dgscroll">{svg}</div>{cap}</div>')


def figures(items):
    """items: [(kind, question, svg, caption), ...]"""
    return '<div class="dgset">' + "".join(figure(*i) for i in items) + "</div>"
