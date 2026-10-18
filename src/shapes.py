"""Shared drawing primitives for the workshop sheets (pycairo).

Coordinates: cairo y-down. Each puppet is drawn in a local frame where the
playboard top edge is y=0 and the puppet rises into negative y.
"""
import cairo, math, random

PAPER = (0.957, 0.937, 0.890)
INK = (0.075, 0.075, 0.095)
PENCIL = (0.78, 0.16, 0.14)
BOARD = (0.42, 0.40, 0.38)


def blob(ctx, cx, cy, rx, ry, n=2.6, squish=0.0, steps=140):
    """Superellipse; squish>0 widens the bottom (pear), <0 the top."""
    for i in range(steps + 1):
        t = 2 * math.pi * i / steps
        c, s = math.cos(t), math.sin(t)
        x = rx * math.copysign(abs(c) ** (2 / n), c)
        y = ry * math.copysign(abs(s) ** (2 / n), s)
        x *= 1 + squish * (y / ry)
        (ctx.move_to if i == 0 else ctx.line_to)(cx + x, cy + y)
    ctx.close_path()


def ellipse(ctx, cx, cy, rx, ry, rot=0.0):
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(rot)
    ctx.scale(rx, ry)
    ctx.new_sub_path()
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()


def rrect(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()


def limb(ctx, x0, y0, x1, y1, t0, t1, bend=0.0, n=24):
    """Tapered limb along a quadratic curve. bend = sideways offset of the control point."""
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    cx, cy = mx + nx * bend, my + ny * bend
    left, right = [], []
    for i in range(n + 1):
        u = i / n
        bx = (1 - u) ** 2 * x0 + 2 * (1 - u) * u * cx + u * u * x1
        by = (1 - u) ** 2 * y0 + 2 * (1 - u) * u * cy + u * u * y1
        tx = 2 * (1 - u) * (cx - x0) + 2 * u * (x1 - cx)
        ty = 2 * (1 - u) * (cy - y0) + 2 * u * (y1 - cy)
        tl = math.hypot(tx, ty) or 1
        px, py = -ty / tl, tx / tl
        w = (t0 * (1 - u) + t1 * u) / 2
        left.append((bx + px * w, by + py * w))
        right.append((bx - px * w, by - py * w))
    ctx.move_to(*left[0])
    for p in left[1:]:
        ctx.line_to(*p)
    for p in reversed(right):
        ctx.line_to(*p)
    ctx.close_path()


def mitten(ctx, x, y, r, ang=0.0):
    """Four-finger Muppet hand reduced to palm + thumb."""
    ellipse(ctx, x, y, r, r * 0.82, ang)
    tx = x + math.cos(ang - 2.2) * r * 0.85
    ty = y + math.sin(ang - 2.2) * r * 0.85
    ellipse(ctx, tx, ty, r * 0.36, r * 0.55, ang - 0.6)


def arms(ctx, r, sx, sy, length, thick, droop=None, hands=True, both=True):
    """Two arms from shoulders (±sx, sy)."""
    droop = r.uniform(0.2, 1.3) if droop is None else droop
    for side in ((-1, 1) if both else (1,)):
        ang = math.pi / 2 - side * (math.pi / 2 - droop)  # 0 = horizontal out, pi/2 = straight down
        ex = side * sx + side * math.cos(droop) * length
        ey = sy + math.sin(droop) * length
        limb(ctx, side * sx, sy, ex, ey, thick, thick * 0.75, bend=side * length * 0.15)
        ctx.fill()
        if hands:
            mitten(ctx, ex, ey, thick * 0.95, math.atan2(ey - sy, ex - side * sx) + (0 if side > 0 else math.pi) * 0)
            ctx.fill()


def wobble_ring(ctx, cx, cy, rx, ry, seed=0, turns=1.15, width=3.2):
    """A hand-drawn red-pencil circle (for picks)."""
    rnd = random.Random(seed)
    ph = rnd.uniform(0, 2 * math.pi)
    steps = 160
    ctx.set_source_rgba(*PENCIL, 0.85)
    ctx.set_line_width(width)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    a1, a2 = rnd.uniform(0.6, 1.4), rnd.uniform(2, 3.5)
    for i in range(steps + 1):
        t = ph + 2 * math.pi * turns * i / steps
        k = 1 + 0.035 * math.sin(a1 * t) + 0.02 * math.sin(a2 * t + 1) + 0.04 * i / steps
        x = cx + rx * k * math.cos(t)
        y = cy + ry * k * math.sin(t)
        (ctx.move_to if i == 0 else ctx.line_to)(x, y)
    ctx.stroke()


def text(ctx, s, x, y, size, face="Futura", weight=cairo.FONT_WEIGHT_NORMAL,
         slant=cairo.FONT_SLANT_NORMAL, rgb=INK, align="left", alpha=1.0):
    ctx.select_font_face(face, slant, weight)
    ctx.set_font_size(size)
    ext = ctx.text_extents(s)
    if align == "center":
        x -= ext.x_advance / 2
    elif align == "right":
        x -= ext.x_advance
    ctx.set_source_rgba(*rgb, alpha)
    ctx.move_to(x, y)
    ctx.show_text(s)
    return ext.x_advance


def paper(ctx, W, H, seed=1, rgb=PAPER, grain=9000):
    """Warm paper with faint grain."""
    ctx.set_source_rgb(*rgb)
    ctx.paint()
    rnd = random.Random(seed)
    for _ in range(grain):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        a = rnd.uniform(0.01, 0.045)
        c = rnd.choice([0.0, 1.0])
        ctx.set_source_rgba(c, c, c, a)
        ctx.rectangle(x, y, rnd.uniform(0.6, 1.8), rnd.uniform(0.6, 1.8))
        ctx.fill()
