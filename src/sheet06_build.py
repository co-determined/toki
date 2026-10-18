"""Builder's sheet 06: materials, pattern pieces on a cutting mat, a cross-section
of the head, and how the puppet is performed."""
import cairo, math, os, sys, random, time
import numpy as np
from shapes import paper, text, INK, PENCIL, BOARD, rrect, ellipse
from fleece import fleece, shade
import maquette as M

OUT = "../png/06_builders_sheet.png"
CACHE = "../notes/cache"
os.makedirs(CACHE, exist_ok=True)
SW, SH = 2900, 2010
MX = 70
BLUE = (0.16, 0.28, 0.55)
CREAM = (0.955, 0.925, 0.845)
NAVY = (0.13, 0.17, 0.33)
KRAFT = (0.86, 0.77, 0.60)


def wrap(ctx, s, x, y, size, maxw, face="Gill Sans", lh=1.3, **kw):
    ctx.select_font_face(face, kw.get("slant", cairo.FONT_SLANT_NORMAL), kw.get("weight", cairo.FONT_WEIGHT_NORMAL))
    ctx.set_font_size(size)
    words, line, lines = s.split(), "", []
    for w in words:
        t = (line + " " + w).strip()
        if ctx.text_extents(t).x_advance > maxw and line:
            lines.append(line); line = w
        else:
            line = t
    lines.append(line)
    for k, ln in enumerate(lines):
        text(ctx, ln, x, y + k * size * lh, size, face=face, **kw)
    return len(lines)


def pinked(ctx, x, y, w, h, tooth=6):
    ctx.move_to(x, y)
    n = int(w / tooth)
    for i in range(n):
        ctx.line_to(x + (i + 0.5) * w / n, y + (tooth * 0.6 if i % 2 == 0 else 0) - tooth * 0.3)
    ctx.line_to(x + w, y)
    m = int(h / tooth)
    for i in range(m):
        ctx.line_to(x + w + (tooth * 0.6 if i % 2 == 0 else 0) - tooth * 0.3, y + (i + 0.5) * h / m)
    ctx.line_to(x + w, y + h)
    for i in range(n):
        ctx.line_to(x + w - (i + 0.5) * w / n, y + h + (tooth * 0.6 if i % 2 == 0 else 0) - tooth * 0.3)
    ctx.line_to(x, y + h)
    for i in range(m):
        ctx.line_to(x + (tooth * 0.6 if i % 2 == 0 else 0) - tooth * 0.3, y + h - (i + 0.5) * h / m)
    ctx.close_path()


# ---------------------------------------------------------------- swatches
def sw_fleece(ctx, x, y, s, rgb, seed):
    fleece(ctx, lambda c: pinked(c, x, y, s, s), rgb, seed=seed, density=1.4, fuzz=0.6, ao=0.3)


def sw_foam(ctx, x, y, s, seed):
    rnd = random.Random(seed)
    ctx.save(); ctx.rectangle(x, y, s, s); ctx.clip()
    ctx.set_source_rgb(0.93, 0.84, 0.55); ctx.paint()
    for _ in range(170):
        cx, cy = rnd.uniform(x, x + s), rnd.uniform(y, y + s)
        r = rnd.uniform(2, 5)
        ctx.set_source_rgba(0.62, 0.52, 0.25, 0.55); ctx.arc(cx, cy, r, 0, 2 * math.pi); ctx.fill()
        ctx.set_source_rgba(1, 0.97, 0.8, 0.5); ctx.arc(cx - 0.8, cy - 0.8, r * 0.5, 0, 2 * math.pi); ctx.fill()
    ctx.restore()
    ctx.set_source_rgba(0, 0, 0, 0.3); ctx.set_line_width(1); ctx.rectangle(x, y, s, s); ctx.stroke()


def sw_petg(ctx, x, y, s):
    g = cairo.LinearGradient(x, y, x + s, y + s)
    g.add_color_stop_rgba(0, 0.80, 0.92, 0.95, 0.55)
    g.add_color_stop_rgba(0.5, 0.95, 0.99, 1.0, 0.85)
    g.add_color_stop_rgba(1, 0.75, 0.88, 0.92, 0.55)
    ctx.set_source(g); rrect(ctx, x, y, s, s, 6); ctx.fill_preserve()
    ctx.set_source_rgba(0.3, 0.45, 0.5, 0.7); ctx.set_line_width(1.5); ctx.stroke()
    ctx.set_source_rgba(1, 1, 1, 0.8); ctx.set_line_width(3)
    ctx.move_to(x + 12, y + s - 20); ctx.line_to(x + s - 20, y + 12); ctx.stroke()


def sw_velvet(ctx, x, y, s, seed):
    fleece(ctx, lambda c: pinked(c, x, y, s, s), (0.10, 0.10, 0.20), seed=seed, density=0.6, fuzz=0.3, ao=0.2)
    g = cairo.LinearGradient(x, y, x + s, y + s)
    g.add_color_stop_rgba(0, 1, 1, 1, 0.0); g.add_color_stop_rgba(0.45, 0.7, 0.7, 0.9, 0.22); g.add_color_stop_rgba(1, 1, 1, 1, 0.0)
    ctx.set_source(g); ctx.rectangle(x, y, s, s); ctx.fill()


def sw_eye(ctx, x, y, s):
    cx, cy, r = x + s / 2, y + s / 2, s * 0.42
    g = cairo.RadialGradient(cx - r * 0.35, cy - r * 0.4, r * 0.1, cx, cy, r)
    g.add_color_stop_rgb(0, 1, 1, 1); g.add_color_stop_rgb(1, 0.82, 0.82, 0.82)
    ctx.set_source(g); ctx.arc(cx, cy, r, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgb(0.04, 0.04, 0.05); ctx.arc(cx + r * 0.1, cy + r * 0.12, r * 0.5, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.9); ctx.arc(cx - r * 0.35, cy - r * 0.4, r * 0.12, 0, 2 * math.pi); ctx.fill()


def sw_wire(ctx, x, y, s):
    ctx.set_source_rgb(0.62, 0.64, 0.66); ctx.set_line_width(3)
    for i in range(80):
        a = i * 0.35
        px = x + s / 2 + math.cos(a) * s * 0.3
        py = y + 10 + i * (s - 20) / 80 + math.sin(a) * 6
        (ctx.move_to if i == 0 else ctx.line_to)(px, py)
    ctx.stroke()


def sw_rod(ctx, x, y, s):
    ctx.set_source_rgb(0.35, 0.36, 0.38); ctx.set_line_width(3)
    ctx.move_to(x + 8, y + s - 8); ctx.line_to(x + s - 30, y + 26); ctx.stroke()
    ctx.save(); ctx.translate(x + s - 22, y + 18); ctx.rotate(-math.pi / 4)
    ctx.set_source_rgb(0.62, 0.44, 0.26); rrect(ctx, -9, -26, 18, 40, 8); ctx.fill()
    ctx.restore()


def sw_felt(ctx, x, y, s, seed):
    fleece(ctx, lambda c: c.arc(x + s / 2, y + s / 2, s * 0.4, 0, 2 * math.pi), (0.05, 0.05, 0.06), seed=seed,
           density=0.5, fuzz=0.4, ao=0.1)


def sw_magnet(ctx, x, y, s):
    for i, (dx, dy) in enumerate(((0.3, 0.35), (0.62, 0.55))):
        cx, cy = x + s * dx, y + s * dy
        g = cairo.RadialGradient(cx - 4, cy - 4, 1, cx, cy, 14)
        g.add_color_stop_rgb(0, 0.95, 0.95, 0.96); g.add_color_stop_rgb(1, 0.55, 0.56, 0.6)
        ctx.set_source(g); ctx.arc(cx, cy, 14, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgba(*CREAM, 1); ctx.arc(x + s * 0.5, y + s * 0.82, 16, math.pi, 2 * math.pi); ctx.fill()


MATERIALS = [
    ("sw_fleece_cream", "Body", "Cream nylon fleece, the Antron type (Antron itself is no longer made). Skin patterns are draped off the carved foam, not cut flat."),
    ("sw_fleece_navy", "Trim: piping, hands, tuft", "Ink-navy fleece. Piping: a 6 cm bias strip over cord, in two loops (head, jaw), ends tucked at the mouth corners."),
    ("sw_foam", "Shell", "1/2-inch reticulated foam, carved and contact-cemented into two shells, the upper head and the lower jaw. 42 × 33 × 22 cm."),
    ("sw_petg", "Mouth plates", "1 mm polypropylene cut to the head's footprint, hinged by stitching through drilled holes (gaffer creeps under lights). Jaw-return elastic across the hinge."),
    ("sw_velvet", "Mouth interior", "Navy-black velvet, with side gussets so the corners close on a wide laugh. Pink fleece tongue over a foam pad."),
    ("sw_eye", "Eyes", "4.2-inch acrylic half-spheres, 3 mm walls, set 9 mm apart for the lid edges. They go in last."),
    ("sw_felt", "Pupils", "Black felt, 5.2 cm, glued: Toki looks at something by turning its head. Large, because big pupils read young."),
    ("sw_magnet", "Lid sets", "Open, half, closed, on sewn-in snaps. No magnets: nothing for a child to find. The precedent is Julia's eye sets."),
    ("sw_wire", "Hands", "Navy fleece over thin foam, with wire cores in the fingers so a hand can point and hold the notebook."),
    ("sw_rod", "Arm rods", "1/8-inch steel on a swivel with a detent pin at the wrist (screw-ons back out when the rod rolls). Left hand, together."),
]


def materials(ctx, x0, y0):
    text(ctx, "MATERIALS", x0, y0, 24, face="Futura", weight=cairo.FONT_WEIGHT_BOLD)
    y = y0 + 30
    S = 88
    for i, (kind, title, desc) in enumerate(MATERIALS):
        sx, sy = x0, y
        if kind == "sw_fleece_cream":
            sw_fleece(ctx, sx, sy, S, CREAM, 1)
        elif kind == "sw_fleece_navy":
            sw_fleece(ctx, sx, sy, S, NAVY, 2)
        elif kind == "sw_foam":
            sw_foam(ctx, sx, sy, S, 3)
        elif kind == "sw_petg":
            sw_petg(ctx, sx, sy, S)
        elif kind == "sw_velvet":
            sw_velvet(ctx, sx, sy, S, 4)
        elif kind == "sw_eye":
            sw_eye(ctx, sx, sy, S)
        elif kind == "sw_felt":
            sw_felt(ctx, sx, sy, S, 5)
        elif kind == "sw_magnet":
            sw_magnet(ctx, sx, sy, S)
        elif kind == "sw_wire":
            sw_wire(ctx, sx, sy, S)
        elif kind == "sw_rod":
            sw_rod(ctx, sx, sy, S)
        text(ctx, title, sx + S + 22, sy + 22, 19, face="Futura", weight=cairo.FONT_WEIGHT_BOLD)
        wrap(ctx, desc, sx + S + 22, sy + 46, 15, 540, face="Gill Sans", alpha=0.85)
        y += S + 36


# ---------------------------------------------------------------- pattern pieces
def piece(ctx, path_fn, label, sub, lx, ly, grain=None, fill=KRAFT, notches=()):
    ctx.save()
    ctx.new_path(); path_fn(ctx)
    ctx.set_source_rgb(*fill); ctx.fill_preserve()
    ctx.set_source_rgba(*INK, 0.85); ctx.set_line_width(1.6); ctx.stroke()
    # seam allowance (dashed, inside)
    ctx.new_path(); path_fn(ctx)
    p = ctx.copy_path()
    ctx.save(); ctx.new_path(); path_fn(ctx); ctx.clip()
    ctx.new_path(); ctx.append_path(p)
    ctx.set_source_rgba(*INK, 0.55); ctx.set_line_width(10); ctx.stroke_preserve()
    ctx.set_source_rgb(*fill); ctx.set_line_width(7.5); ctx.stroke()
    ctx.restore()
    ctx.new_path(); ctx.append_path(p)
    ctx.set_source_rgba(*INK, 0.85); ctx.set_line_width(1.6); ctx.stroke()
    if grain:
        (gx0, gy0, gx1, gy1) = grain
        ctx.set_source_rgba(*INK, 0.7); ctx.set_line_width(1.4)
        ctx.move_to(gx0, gy0); ctx.line_to(gx1, gy1); ctx.stroke()
        for (x, y, a) in ((gx0, gy0, math.atan2(gy0 - gy1, gx0 - gx1)), (gx1, gy1, math.atan2(gy1 - gy0, gx1 - gx0))):
            ctx.move_to(x, y); ctx.line_to(x - math.cos(a - 0.4) * 10, y - math.sin(a - 0.4) * 10)
            ctx.move_to(x, y); ctx.line_to(x - math.cos(a + 0.4) * 10, y - math.sin(a + 0.4) * 10)
            ctx.stroke()
    for (nx, ny, a) in notches:
        ctx.save(); ctx.translate(nx, ny); ctx.rotate(a)
        ctx.move_to(-6, 0); ctx.line_to(6, 0); ctx.line_to(0, 9); ctx.close_path()
        ctx.set_source_rgba(*INK, 0.85); ctx.fill(); ctx.restore()
    text(ctx, label, lx, ly, 17, face="Futura", weight=cairo.FONT_WEIGHT_BOLD, alpha=0.9)
    text(ctx, sub, lx, ly + 19, 13, face="Gill Sans", alpha=0.85)
    ctx.restore()


def cutting_mat(ctx, x0, y0, w, h, cm):
    ctx.set_source_rgb(0.20, 0.42, 0.34)
    rrect(ctx, x0, y0, w, h, 14); ctx.fill()
    ctx.save(); rrect(ctx, x0, y0, w, h, 14); ctx.clip()
    for i in range(0, int(w / cm) + 1):
        ctx.set_source_rgba(0.85, 0.95, 0.88, 0.35 if i % 5 == 0 else 0.13)
        ctx.set_line_width(1.2 if i % 5 == 0 else 0.8)
        ctx.move_to(x0 + i * cm, y0); ctx.line_to(x0 + i * cm, y0 + h); ctx.stroke()
    for j in range(0, int(h / cm) + 1):
        ctx.set_source_rgba(0.85, 0.95, 0.88, 0.35 if j % 5 == 0 else 0.13)
        ctx.set_line_width(1.2 if j % 5 == 0 else 0.8)
        ctx.move_to(x0, y0 + j * cm); ctx.line_to(x0 + w, y0 + j * cm); ctx.stroke()
    ctx.set_source_rgba(0.9, 0.98, 0.9, 0.25); ctx.set_line_width(2)
    ctx.move_to(x0 + 60, y0 + h - 40); ctx.line_to(x0 + w - 60, y0 + 40); ctx.stroke()
    ctx.restore()


def patterns(ctx, x0, y0, w, h):
    cm = 6.2      # px per cm on the mat
    cutting_mat(ctx, x0, y0, w, h, cm * 5)
    text(ctx, "PATTERN PIECES", x0, y0 - 18, 24, face="Futura", weight=cairo.FONT_WEIGHT_BOLD)
    text(ctx, "on the mat, grid = 5 cm · dashed = 1 cm seam allowance · arrows = grain", x0 + 250, y0 - 18, 15,
         face="Gill Sans", alpha=0.7)

    def P(x, y):
        return x0 + 30 + x * cm, y0 + 40 + y * cm

    # A front panel (domed with four corner darts), mouth slash, eye marks
    def A(c):
        ax, ay = P(2, 2)
        rrect(c, ax, ay, 52 * cm, 40 * cm, 13 * cm)
    piece(ctx, A, "A · FRONT", "cut over-size · drape the final pattern off the carved foam", *P(4, 47), grain=(*P(27, 6), *P(27, 20)))
    ax, ay = P(2, 2)
    ctx.set_source_rgba(*INK, 0.8); ctx.set_line_width(1.4)
    for (dx, dy, sx, sy) in ((0, 0, 1, 1), (52, 0, -1, 1), (0, 40, 1, -1), (52, 40, -1, -1)):
        bx, by = ax + dx * cm, ay + dy * cm
        ctx.move_to(bx + sx * 3 * cm, by + sy * 7 * cm); ctx.line_to(bx + sx * 9 * cm, by + sy * 9 * cm)
        ctx.line_to(bx + sx * 7 * cm, by + sy * 3 * cm); ctx.stroke()
    ctx.set_source_rgba(*PENCIL, 0.9); ctx.set_line_width(2); ctx.set_dash([8, 5])
    ctx.move_to(*P(2, 24)); ctx.curve_to(*P(16, 26.5), *P(38, 26.5), *P(54, 24)); ctx.stroke(); ctx.set_dash([])
    text(ctx, "slash for the mouth, seam to seam", *P(14, 30), 13, face="Chalkboard SE", rgb=PENCIL)
    for ex in (21.5, 32.5):
        ctx.set_source_rgba(*INK, 0.7); ctx.set_dash([3, 3]); ctx.arc(*P(ex, 13.5), 5.3 * cm, 0, 2 * math.pi); ctx.stroke(); ctx.set_dash([])
    text(ctx, "eyes, set last", *P(22, 6.5), 13, face="Chalkboard SE", rgb=BLUE)

    # B back panel with the tail
    def B(c):
        bx, by = P(62, 2)
        c.save(); c.translate(bx + 26 * cm, by + 39 * cm)
        s = cm * 50 / 290
        c.scale(s, s)
        import toki2d as T
        T.bubble_outline(c, T.P(lift=0, W=290, H=215, tail_x=40, lean=-120, ttop=72, tbot=56, fillet=14))
        c.restore()
    piece(ctx, B, "B · BACK + TAIL", "cut over-size · the tail is the sleeve · opening 32 cm+", *P(80, 66), grain=(*P(87, 8), *P(87, 26)))

    # C tail front
    def C(c):
        pts = [P(120, 4), P(140, 4), P(138, 52), P(122, 52)]
        c.move_to(*pts[0])
        for q in pts[1:]:
            c.line_to(*q)
        c.close_path()
    piece(ctx, C, "C · TAIL", "cut 1 · cream · 16 cm at the cuff", *P(118, 57), grain=(*P(130, 10), *P(130, 44)))

    # E mouth plates: the head's footprint, straight hinge edge at the back
    def plate(c, ox, oy):
        ex, ey = P(ox, oy)
        w, d_, r = 38 * cm, 18 * cm, 8 * cm
        c.move_to(ex, ey); c.line_to(ex + w, ey)
        c.line_to(ex + w, ey + d_ - r); c.arc(ex + w - r, ey + d_ - r, r, 0, math.pi / 2)
        c.line_to(ex + r, ey + d_); c.arc(ex + r, ey + d_ - r, r, math.pi / 2, math.pi)
        c.close_path()
    piece(ctx, lambda c: plate(c, 148, 4), "E1 · UPPER PLATE", "1 mm PP · fingers · hinge edge at top", *P(148, 27), fill=(0.84, 0.93, 0.95))
    piece(ctx, lambda c: plate(c, 148, 34), "E2 · LOWER PLATE", "1 mm PP · thumb · stitch through drilled holes", *P(148, 57), fill=(0.84, 0.93, 0.95))
    for (ox, oy) in ((148, 4), (148, 34)):
        for i in range(9):
            hx_, hy_ = P(ox + 3 + i * 4, oy + 1.2)
            ctx.set_source_rgba(*INK, 0.7); ctx.arc(hx_, hy_, 2.2, 0, 2 * math.pi); ctx.fill()

    # F hands
    def F(c, ox, oy):
        hx, hy = P(ox, oy)
        c.new_sub_path(); c.save(); c.translate(hx, hy); c.scale(6 * cm, 5 * cm); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()
        for k, off in enumerate((-3.2, 0, 3.2)):
            c.new_sub_path(); c.save(); c.translate(hx + off * cm, hy - 7 * cm); c.scale(1.7 * cm, 4.2 * cm)
            c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()
        c.new_sub_path(); c.save(); c.translate(hx + 6.5 * cm, hy - 1 * cm); c.rotate(0.9); c.scale(1.6 * cm, 3.4 * cm)
        c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()
    for k, ox in enumerate((10, 26, 42, 58)):
        piece(ctx, lambda c, ox=ox: F(c, ox, 104), "F" if k == 0 else "", "" if k else "HAND · cut 4 · navy",
              *P(6, 115), fill=NAVY if False else (0.70, 0.73, 0.86))

    # G arms
    for k, ox in enumerate((74, 86)):
        def G(c, ox=ox):
            gx, gy = P(ox, 90)
            c.rectangle(gx, gy, 18 * cm * 0.5, 26 * cm)
        piece(ctx, G, "G" if k == 0 else "", "ARM · cut 2 on the fold (18 cm)" if k == 0 else "", *P(74, 121), grain=(*P(ox + 4.5, 94), *P(ox + 4.5, 110)))

    # H curl strip
    def Hh(c):
        for ox in (104, 118):
            hx_, hy_ = P(ox, 96)
            c.new_sub_path()
            c.move_to(hx_, hy_ - 6 * cm)
            c.curve_to(hx_ + 6 * cm, hy_ - 5 * cm, hx_ + 5 * cm, hy_ + 3 * cm, hx_, hy_ + 4 * cm)
            c.curve_to(hx_ - 5 * cm, hy_ + 3 * cm, hx_ - 6 * cm, hy_ - 5 * cm, hx_, hy_ - 6 * cm)
            c.close_path()
    piece(ctx, Hh, "H · TUFT", "cut 2 navy · over a carved foam core · no wire, no hook", *P(100, 104), fill=(0.70, 0.73, 0.86))
    def K(c):
        for ox in (8, 20):
            kx, ky = P(ox, 126)
            c.new_sub_path(); c.move_to(kx, ky); c.line_to(kx + 8 * cm, ky + 7 * cm); c.line_to(kx, ky + 14 * cm); c.close_path()
    piece(ctx, K, "K · GUSSETS", "cut 2 velvet · close the mouth corners", *P(32, 134), fill=(0.55, 0.55, 0.68))

    # D piping strip (folded)
    def D(c):
        c.rectangle(*P(102, 112), 85 * cm, 4 * cm)
        c.rectangle(*P(102, 118), 85 * cm, 4 * cm)
    piece(ctx, D, "D · PIPING", "navy bias strip 6 × 220 cm over 3/8\" cord, two loops (shown folded)", *P(102, 127), fill=(0.70, 0.73, 0.86))

    # J lid sets
    for k, (amt, name) in enumerate(((0.12, "open"), (0.5, "half"), (0.92, "closed"))):
        def J(c, k=k, amt=amt):
            jx, jy = P(150 + k * 13, 80)
            r = 5.6 * cm
            c.arc(jx, jy, r, math.pi, 2 * math.pi)
            c.line_to(jx + r, jy + (2 * amt - 1) * r * 0.9)
            c.curve_to(jx + r * 0.4, jy + (2 * amt - 1) * r + r * 0.15, jx - r * 0.4, jy + (2 * amt - 1) * r + r * 0.15, jx - r, jy + (2 * amt - 1) * r * 0.9)
            c.close_path()
        piece(ctx, J, "", "", 0, 0, fill=CREAM)
        text(ctx, name, *P(147 + k * 13, 92), 13, face="Gill Sans", alpha=0.9, rgb=(0.92, 0.95, 0.92))
    text(ctx, "J · LID SETS (swap on set)", *P(146, 98), 16, face="Futura", weight=cairo.FONT_WEIGHT_BOLD, rgb=(0.92, 0.95, 0.92))


# ---------------------------------------------------------------- cross-section
def section(ctx, x0, y0):
    text(ctx, "CROSS-SECTION, THROUGH THE MIDDLE", x0, y0, 22, face="Futura", weight=cairo.FONT_WEIGHT_BOLD)
    s = 10.0
    cx, cy = x0 + 190, y0 + 300   # head center
    def Ppx(z, y):
        return cx - z * s, cy - y * s
    ctx.save()
    # the sleeve, entering at the back (drawn first, behind the shell)
    ctx.set_source_rgb(*CREAM)
    ctx.move_to(*Ppx(-11.4, -14)); ctx.line_to(*Ppx(1.4, -14)); ctx.line_to(*Ppx(1.4, -26)); ctx.line_to(*Ppx(-11.4, -26)); ctx.close_path(); ctx.fill()
    ctx.set_source_rgba(*NAVY, 0.8); ctx.set_line_width(2)
    ctx.move_to(*Ppx(-11.4, -14)); ctx.line_to(*Ppx(-11.4, -26)); ctx.move_to(*Ppx(1.4, -14)); ctx.line_to(*Ppx(1.4, -26)); ctx.stroke()
    ctx.set_source_rgb(0.07, 0.07, 0.09)
    ctx.rectangle(*Ppx(1.4, -26), 12.8 * s, 5 * s); ctx.fill()
    # outer shell: 22 deep, 33 tall, corner r 10
    ctx.new_path(); rrect(ctx, *Ppx(11, 16.5), 22 * s, 33 * s, 10 * s)
    ctx.set_source_rgb(*CREAM); ctx.fill_preserve()
    ctx.set_source_rgb(*NAVY); ctx.set_line_width(2.5); ctx.stroke()
    ctx.new_path(); rrect(ctx, *Ppx(11, 16.5), 22 * s, 33 * s, 10 * s)
    rrect(ctx, *Ppx(9.7, 15.2), 19.4 * s, 30.4 * s, 8.8 * s)
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    ctx.set_source_rgb(0.93, 0.84, 0.55); ctx.fill()
    ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
    ctx.new_path(); rrect(ctx, *Ppx(9.7, 15.2), 19.4 * s, 30.4 * s, 8.8 * s)
    ctx.set_source_rgb(0.97, 0.95, 0.90); ctx.fill()
    # opening in the bottom of the shell, at the back, where the sleeve enters
    ctx.set_source_rgb(0.97, 0.95, 0.90)
    ctx.rectangle(*Ppx(-0.5, -15.0), 10.4 * s, 2.0 * s); ctx.fill()
    # mouth plates, hinged at the back; the hinge is where the wrist sits
    hz, hy = -7.5, -2.6
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_source_rgb(0.35, 0.55, 0.62); ctx.set_line_width(5)
    ctx.move_to(*Ppx(hz, hy + 0.4)); ctx.line_to(*Ppx(10.6, hy + 0.6)); ctx.stroke()
    ctx.move_to(*Ppx(hz, hy - 0.4)); ctx.line_to(*Ppx(10.3, hy - 2.2)); ctx.stroke()
    ctx.set_source_rgb(*PENCIL); ctx.arc(*Ppx(hz, hy), 6, 0, 2 * math.pi); ctx.fill()
    # jaw-return elastic across the hinge
    ctx.set_source_rgb(0.85, 0.35, 0.45); ctx.set_line_width(2)
    zx = [Ppx(hz + 1.6 + 0.35 * (i % 2), hy + 0.6 - i * 0.55) for i in range(8)]
    ctx.move_to(*zx[0])
    for q in zx[1:]:
        ctx.line_to(*q)
    ctx.stroke()
    # mouth opening in front
    ctx.set_source_rgb(0.10, 0.10, 0.20)
    ctx.move_to(*Ppx(10.6, hy + 0.6)); ctx.line_to(*Ppx(11.2, hy + 0.6)); ctx.line_to(*Ppx(11.0, hy - 2.4)); ctx.line_to(*Ppx(10.3, hy - 2.2))
    ctx.close_path(); ctx.fill()
    # eye: half-sphere set into the front, felt pupil at the front
    ex, ey = 8.3, 7.6
    ctx.new_path(); ctx.arc(*Ppx(ex, ey), 5.3 * s, 0, 2 * math.pi)
    ctx.save(); ctx.clip()
    ctx.set_source_rgb(0.98, 0.98, 0.96); ctx.paint()
    ctx.set_source_rgb(0.04, 0.04, 0.05)
    ctx.rectangle(*Ppx(13.7, ey + 2.6), 1.0 * s, 5.2 * s); ctx.fill()
    ctx.restore()
    ctx.new_path(); ctx.arc(*Ppx(ex, ey), 5.3 * s, 0, 2 * math.pi)
    ctx.set_source_rgba(0, 0, 0, 0.5); ctx.set_line_width(1.5); ctx.stroke()
    # tuft: fleece over a foam core, curling forward
    ctx.set_source_rgb(*NAVY)
    ctx.move_to(*Ppx(-1, 16.3))
    ctx.curve_to(*Ppx(0, 21.5), *Ppx(6, 23.5), *Ppx(9.5, 20.5))
    ctx.curve_to(*Ppx(10.5, 19.0), *Ppx(9.0, 17.6), *Ppx(7.5, 18.6))
    ctx.curve_to(*Ppx(6.0, 20.0), *Ppx(4.0, 19.0), *Ppx(4.0, 16.3))
    ctx.close_path(); ctx.fill()
    # the hand: in from the back, wrist at the hinge, 17 cm along the upper plate, thumb on the lower
    ctx.set_source_rgba(*PENCIL, 0.85); ctx.set_dash([6, 4]); ctx.set_line_width(2)
    hand = [(-9.4, -26), (-9.4, -14), (-9.6, -5.5), (-7.5, 1.6), (2.0, 2.6), (8.8, 2.0), (9.5, 0.8), (8.8, -0.4),
            (-1.0, -1.2), (-3.0, -3.4), (5.8, -4.4), (6.6, -5.6), (5.8, -6.7), (-2.0, -7.6), (-0.6, -14), (-0.6, -26)]
    ctx.move_to(*Ppx(*hand[0]))
    for q in hand[1:]:
        ctx.line_to(*Ppx(*q))
    ctx.stroke(); ctx.set_dash([])
    ctx.restore()
    callouts = [((-1.5, 15.9), "1/2\" foam shell, carved; fleece skin draped over it"),
                ((hz, hy), "hinge at the back, stitched; the wrist sits here"),
                ((hz + 2.2, hy - 1.6), "jaw-return elastic: a relaxed hand reads as a closed mouth"),
                ((10.8, hy - 0.8), "mouth: velvet over two 1 mm plates, gussets at the corners"),
                ((ex + 3.5, ey + 3.5), "eye: 3 mm acrylic half-sphere; felt pupil glued for focus"),
                ((5.5, 21.5), "tuft: fleece over a foam core; nothing to hang it by"),
                ((4.0, 2.0), "fingers along the upper plate (a 17 cm hand fits)"),
                ((3.5, -5.2), "thumb in the lower plate"),
                ((-5.0, -20), "sleeve in at the back; black velvet below the board")]
    lx = cx + 170
    for i, ((z, y), label) in enumerate(callouts):
        px, py = Ppx(z, y)
        ctx.set_source_rgb(*PENCIL)
        ctx.arc(px, py, 11, 0, 2 * math.pi); ctx.fill()
        text(ctx, str(i + 1), px, py + 5, 13, face="Futura", weight=cairo.FONT_WEIGHT_BOLD, align="center", rgb=(1, 1, 1))
        ly = y0 + 50 + i * 32
        ctx.set_source_rgb(*PENCIL); ctx.arc(lx, ly - 5, 11, 0, 2 * math.pi); ctx.fill()
        text(ctx, str(i + 1), lx, ly, 13, face="Futura", weight=cairo.FONT_WEIGHT_BOLD, align="center", rgb=(1, 1, 1))
        text(ctx, label, lx + 20, ly, 14, face="Gill Sans", alpha=0.9)


def top_view(ctx, x0, y0):
    text(ctx, "TOP VIEW, WITH THE HAND TRACED", x0, y0, 20, face="Futura", weight=cairo.FONT_WEIGHT_BOLD)
    text(ctx, "(the view the builder asked for)", x0, y0 + 22, 14, face="Gill Sans", alpha=0.7)
    ppcm, VW, VH = 6.4, 420, 300
    path = os.path.join(CACHE, "top_view.npy")
    if os.path.exists(path) and "--fresh" not in sys.argv:
        img = np.load(path)
    else:
        img = M.render(M.Pose(), width=VW, height=VH, ppcm=ppcm, center=(0.0, 0.0), view_pitch=-math.pi / 2, follow=True)
        np.save(path, img)
    oy = y0 + 40
    s, arr = M.to_surface(img)
    ctx.set_source_surface(s, x0, oy); ctx.paint()
    def T(x, z):
        return x0 + VW / 2 + x * ppcm, oy + VH / 2 + z * ppcm
    ctx.save()
    ctx.set_source_rgba(*PENCIL, 0.9); ctx.set_dash([5, 4]); ctx.set_line_width(2)
    hand = [(-4.2, -9.0), (-4.6, -1.0), (-4.0, 6.5), (-2.4, 9.6), (2.4, 9.6), (4.0, 6.5), (4.6, -1.0), (4.2, -9.0)]
    ctx.move_to(*T(*hand[0]))
    for q in hand[1:]:
        ctx.line_to(*T(*q))
    ctx.stroke(); ctx.set_dash([])
    ctx.restore()
    text(ctx, "front", x0 + VW / 2, oy + VH + 2, 13, face="Gill Sans", align="center", alpha=0.7)
    text(ctx, "back: wrist at the hinge", x0 + VW / 2, oy - 4, 13, face="Gill Sans", align="center", alpha=0.7, rgb=PENCIL)


# ---------------------------------------------------------------- performance
def perform(ctx, x0, y0):
    text(ctx, "HOW IT'S PERFORMED", x0, y0, 24, face="Futura", weight=cairo.FONT_WEIGHT_BOLD)
    ppcm = 3.6
    VW, VH = 620, 820
    center = (-12.0, -70.0)
    path = os.path.join(CACHE, "perform_front.npy")
    if os.path.exists(path) and "--fresh" not in sys.argv:
        img = np.load(path)
    else:
        img = M.render(M.Pose(rods=True, rod_end=(-6.0, -66.0, 10.0)), width=VW, height=VH, ppcm=ppcm, center=center, follow=True)
        np.save(path, img)
    ox, oy = x0, y0 + 30
    def W(x, y):
        return ox + VW / 2 + (x - center[0]) * ppcm, oy + VH / 2 - (y - center[1]) * ppcm
    # floor + monitor
    fy = W(0, -168)[1]
    ctx.set_source_rgba(*INK, 0.5); ctx.set_line_width(2); ctx.move_to(ox, fy); ctx.line_to(ox + VW, fy); ctx.stroke()
    mx, my = W(18, -150)
    ctx.set_source_rgb(0.15, 0.15, 0.17); rrect(ctx, mx - 34, my - 26, 68, 46, 4); ctx.fill()
    ctx.set_source_rgb(0.55, 0.75, 0.85); rrect(ctx, mx - 28, my - 21, 56, 34, 2); ctx.fill()
    ctx.set_source_rgb(*CREAM); ctx.arc(mx, my - 6, 9, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgb(0.15, 0.15, 0.17); ctx.rectangle(mx - 4, my + 20, 8, fy - my - 20); ctx.fill()
    # puppeteer: a gray figure in blacks, below the playboard
    g = (0.30, 0.30, 0.33)
    ctx.set_source_rgba(*g, 0.92)
    hx, hy = W(-40, -92)
    ctx.arc(hx, hy, 11 * ppcm, 0, 2 * math.pi); ctx.fill()
    ctx.move_to(*W(-58, -104)); ctx.line_to(*W(-22, -104)); ctx.line_to(*W(-24, -168)); ctx.line_to(*W(-56, -168)); ctx.close_path(); ctx.fill()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_width(9 * ppcm)
    ctx.move_to(*W(-26, -106)); ctx.line_to(*W(-15, -58)); ctx.line_to(*W(-4, -30)); ctx.stroke()   # right arm up the sleeve
    ctx.set_line_width(8 * ppcm)
    ctx.move_to(*W(-54, -108)); ctx.line_to(*W(-34, -122)); ctx.line_to(*W(-8, -70)); ctx.stroke()   # left hand on the rods
    # the puppet
    s, arr = M.to_surface(img)
    ctx.set_source_surface(s, ox, oy); ctx.paint()
    by = W(0, -27)[1]
    ctx.set_source_rgba(*BOARD, 0.85); ctx.rectangle(ox, by, VW, 10 * ppcm); ctx.fill()
    ctx.set_source_rgba(*BOARD, 0.25); ctx.rectangle(ox, by + 10 * ppcm, VW, fy - by - 10 * ppcm); ctx.fill()
    text(ctx, "playboard", ox + VW - 8, by - 8, 13, face="Gill Sans", align="right", alpha=0.7)
    notes = [
        "Right hand in the head from the back: wrist at the hinge, fingers along the upper plate, thumb in the lower. Left hand holds both rods.",
        "The tail leans about 25°: that's the comic-strip tail, and it costs the shoulder (a vertical arm rests; this one holds). Plan arm rests between takes.",
        "The puppeteer watches the monitor. A jaw-return elastic makes listening, most of the day, nearly free.",
    ]
    yy = oy + VH + 26
    for n_ in notes:
        k = wrap(ctx, n_, ox, yy, 15, VW, face="Gill Sans")
        yy += k * 19.5 + 8
    yy += 30
    text(ctx, "WEIGHT BUDGET v3 (estimates; weigh at first fitting)", ox, yy, 18, face="Futura", weight=cairo.FONT_WEIGHT_BOLD)
    rows = [("foam shells", 190), ("fleece skin + piping", 165), ("plates (2 × 1 mm PP)", 90),
            ("velvet, gussets, tongue", 45), ("eyes (3 mm) + felt", 110), ("arms + hands + finger wire", 85),
            ("tuft (foam core)", 15), ("cement, thread, snaps", 45)]
    yy += 30
    for name, g_ in rows:
        text(ctx, name, ox, yy, 15, face="Gill Sans", alpha=0.9)
        ctx.set_source_rgba(*NAVY, 0.8); ctx.rectangle(ox + 260, yy - 12, g_ * 1.6, 13); ctx.fill()
        text(ctx, f"{g_} g", ox + 270 + g_ * 1.6, yy, 14, face="Gill Sans", alpha=0.8)
        yy += 24
    tot = sum(g_ for _, g_ in rows)
    ctx.set_source_rgba(*INK, 0.5); ctx.set_line_width(1); ctx.move_to(ox, yy - 10); ctx.line_to(ox + VW - 40, yy - 10); ctx.stroke()
    text(ctx, f"head + arms about {tot} g (rods not included). v1 guessed 555; the builder said 750–800.", ox, yy + 12, 15, face="Gill Sans",
         weight=cairo.FONT_WEIGHT_BOLD)


def main():
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, SW, SH)
    ctx = cairo.Context(surf)
    paper(ctx, SW, SH, seed=61, grain=20000)
    text(ctx, "THE WORKSHOP", MX, 78, 40, weight=cairo.FONT_WEIGHT_BOLD)
    text(ctx, "Builder's sheet 06 · TOKI · how it's made, and how it's performed", MX, 118, 22, face="Gill Sans")
    text(ctx, "v3, after the crit wall. Per Sahlin and Henson: the eyes go in last, with focus set about 70 cm in front, and the designer in the room for it.",
         MX, 150, 17, face="Gill Sans", slant=cairo.FONT_SLANT_ITALIC, alpha=0.75)
    materials(ctx, MX, 220)
    patterns(ctx, 800, 240, 1340, 990)
    section(ctx, 820, 1300)
    # notebook prop
    nx, ny = 1500, 1330
    text(ctx, "PROP: TOKI'S NOTEBOOK", nx, ny - 30, 22, face="Futura", weight=cairo.FONT_WEIGHT_BOLD)
    ctx.save(); ctx.translate(nx + 40, ny + 20); ctx.rotate(-0.06)
    ctx.set_source_rgba(0, 0, 0, 0.18); rrect(ctx, 8, 10, 300, 400, 10); ctx.fill()
    ctx.set_source_rgb(*CREAM); rrect(ctx, 0, 0, 300, 400, 10); ctx.fill()
    ctx.set_source_rgb(*NAVY); ctx.set_line_width(4); rrect(ctx, 0, 0, 300, 400, 10); ctx.stroke()
    for i in range(12):
        ctx.set_source_rgb(0.5, 0.52, 0.55); ctx.set_line_width(3)
        ctx.arc(150 - 132 + i * 24, -4, 7, math.pi * 0.9, math.pi * 2.1); ctx.stroke()
    text(ctx, "TOKI", 150, 70, 34, face="Futura", weight=cairo.FONT_WEIGHT_BOLD, align="center", rgb=NAVY)
    lines = ["my friends:", "Elmo (red! laughs a lot)", "Cookie (tells me cookie)", "Abby (magic, says wait)",
             "", "things I know what they're like:", "rain? (Big Bird told me)", "cookie (sort of!)"]
    for i, l in enumerate(lines):
        text(ctx, l, 26, 125 + i * 30, 17, face="Chalkboard SE", rgb=(0.85, 0.15, 0.15) if i == 0 else NAVY)
    ctx.restore()
    wrap(ctx, "9 × 12 cm, on a navy ribbon. Toki can't hold a pencil: Elmo draws in it and a grown-up writes the words. "
              "Every morning Toki reads it aloud, a comic routine, never a sad one.", nx + 380, ny + 60, 15, 290, face="Gill Sans")
    perform(ctx, 2180, 220)
    top_view(ctx, 2200, 1590)
    text(ctx, "drawn in code (pycairo + the numpy maquette) · Claude · 2026-10-18",
         SW - MX, SH - 30, 15, face="Gill Sans", align="right", alpha=0.6)
    surf.write_to_png(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
