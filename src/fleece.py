"""2D fleece rendering for pycairo: base fill, soft form shading, pile texture,
and fuzzy edges. Antron fleece is a short soft pile; fur is longer and directional."""
import cairo, math, random, colorsys


def mix(a, b, t):
    return tuple(a[i] * (1 - t) + b[i] * t for i in range(3))


def shade(rgb, dl=0.0, ds=0.0):
    h, l, s = colorsys.rgb_to_hls(*rgb)
    return colorsys.hls_to_rgb(h, max(0, min(1, l + dl)), max(0, min(1, s + ds)))


def _resample(flat, step):
    """Points + segment directions along a flattened cairo path, every `step` px."""
    pts = []
    cur = start = None
    for kind, p in flat:
        if kind == cairo.PATH_MOVE_TO:
            cur = start = p
        elif kind in (cairo.PATH_LINE_TO, cairo.PATH_CLOSE_PATH):
            q = p if kind == cairo.PATH_LINE_TO else start
            if cur is None or q is None:
                cur = q
                continue
            dx, dy = q[0] - cur[0], q[1] - cur[1]
            L = math.hypot(dx, dy)
            n = max(1, int(L / step))
            for i in range(n):
                u = i / n
                pts.append((cur[0] + dx * u, cur[1] + dy * u, dx / (L or 1), dy / (L or 1)))
            cur = q
    return pts


def fleece(ctx, path_fn, rgb, seed=0, light=(-0.45, -0.7), density=1.0, fuzz=1.0,
           pile="fleece", ao=1.0, sheen=1.0):
    rnd = random.Random(seed)
    ctx.save()
    ctx.new_path()
    path_fn(ctx)
    x0, y0, x1, y1 = ctx.fill_extents()
    w, h = x1 - x0, y1 - y0
    if w <= 0 or h <= 0:
        ctx.restore()
        return
    flat = ctx.copy_path_flat()
    ctx.set_source_rgb(*rgb)
    ctx.fill_preserve()
    ctx.clip()
    # form light: highlight toward the light, shadow away from it
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = max(w, h)
    lx, ly = cx + light[0] * w * 0.45, cy + light[1] * h * 0.45
    g = cairo.RadialGradient(lx, ly, 0, lx, ly, R * 0.95)
    hi = shade(rgb, 0.12)
    g.add_color_stop_rgba(0, *hi, 0.75)
    g.add_color_stop_rgba(0.55, *hi, 0.0)
    ctx.set_source(g)
    ctx.paint()
    g2 = cairo.LinearGradient(lx, ly, cx - light[0] * w * 0.6, cy - light[1] * h * 0.6)
    lo = shade(rgb, -0.22, 0.05)
    g2.add_color_stop_rgba(0.35, *lo, 0.0)
    g2.add_color_stop_rgba(1.0, *lo, 0.55)
    ctx.set_source(g2)
    ctx.paint()
    # soft inner edge (form turning away)
    if ao > 0:
        ctx.new_path()
        path_fn(ctx)
        p = ctx.copy_path()
        for i, (lw, a) in enumerate([(0.16, 0.05), (0.10, 0.06), (0.06, 0.07), (0.03, 0.09)]):
            ctx.new_path(); ctx.append_path(p)
            ctx.set_line_width(min(w, h) * lw)
            ctx.set_source_rgba(*shade(rgb, -0.35), a * ao)
            ctx.stroke()
    # pile texture
    n = int(w * h / (10 if pile == "fleece" else 16) * density)
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        dl = rnd.gauss(0, 0.07)
        ctx.set_source_rgba(*shade(rgb, dl), 0.35)
        if pile == "fleece":
            a = rnd.uniform(0, math.pi)
            L = rnd.uniform(1.2, 3.2)
        else:  # fur: flows downward-outward from the top center
            a = math.atan2(y - (y0 - h * 0.3), x - cx) + rnd.gauss(0, 0.25)
            L = rnd.uniform(4, 10)
        ctx.set_line_width(rnd.uniform(0.8, 1.6))
        ctx.move_to(x, y)
        ctx.line_to(x + math.cos(a) * L, y + math.sin(a) * L)
        ctx.stroke()
    ctx.restore()
    # fuzzy edge: short fibers crossing the silhouette
    if fuzz > 0:
        ctx.save()
        ctx.new_path(); path_fn(ctx)
        pts = _resample(flat, 1.6 / fuzz)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        for (x, y, tx, ty) in pts:
            nx, ny = ty, -tx
            if ctx.in_fill(x + nx * 2.5, y + ny * 2.5):
                nx, ny = -nx, -ny
            a = math.atan2(ny, nx) + rnd.gauss(0, 0.5)
            L = rnd.uniform(1.0, 3.6 if pile == "fleece" else 8) * fuzz
            ctx.set_source_rgba(*shade(rgb, rnd.gauss(-0.04, 0.06)), 0.7)
            ctx.set_line_width(rnd.uniform(0.7, 1.4))
            bx, by = x - math.cos(a) * L * 0.4, y - math.sin(a) * L * 0.4
            ctx.new_path()
            ctx.move_to(bx, by)
            ctx.line_to(x + math.cos(a) * L, y + math.sin(a) * L)
            ctx.stroke()
        ctx.restore()


def muppet_eye(ctx, x, y, r, look=(0.0, 0.0), lid=0.0, lid_rgb=None, rim_rgb=None, pupil=0.42, seed=0):
    """Ping-pong-ball eye. look = pupil offset in units of r (focus). lid 0..1 covers from the top."""
    # shadow under the ball
    ctx.save()
    ctx.set_source_rgba(0, 0, 0, 0.18)
    ctx.arc(x + r * 0.08, y + r * 0.14, r * 1.02, 0, 2 * math.pi)
    ctx.fill()
    g = cairo.RadialGradient(x - r * 0.35, y - r * 0.4, r * 0.1, x, y, r * 1.05)
    g.add_color_stop_rgb(0, 1, 1, 0.99)
    g.add_color_stop_rgb(0.7, 0.95, 0.95, 0.93)
    g.add_color_stop_rgb(1, 0.80, 0.80, 0.80)
    ctx.set_source(g)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()
    # pupil (felt, flat black), placed for focus
    px, py = x + look[0] * r * 0.5, y + look[1] * r * 0.5
    ctx.save()
    ctx.arc(x, y, r, 0, 2 * math.pi); ctx.clip()
    ctx.set_source_rgb(0.05, 0.05, 0.07)
    ctx.arc(px, py, r * pupil, 0, 2 * math.pi)
    ctx.fill()
    if lid > 0 and lid_rgb is not None:
        # lid: a fleece cap that comes down over the top of the ball
        ctx.set_source_rgb(*lid_rgb)
        top = y - r
        edge = top + 2 * r * lid
        ctx.move_to(x - r * 1.2, top - 2)
        ctx.line_to(x + r * 1.2, top - 2)
        ctx.line_to(x + r * 1.2, edge - r * 0.12)
        ctx.curve_to(x + r * 0.5, edge + r * 0.12, x - r * 0.5, edge + r * 0.12, x - r * 1.2, edge - r * 0.12)
        ctx.close_path()
        ctx.fill()
        ctx.set_source_rgba(0, 0, 0, 0.25)
        ctx.set_line_width(r * 0.07)
        ctx.move_to(x + r * 1.2, edge - r * 0.12)
        ctx.curve_to(x + r * 0.5, edge + r * 0.12, x - r * 0.5, edge + r * 0.12, x - r * 1.2, edge - r * 0.12)
        ctx.stroke()
    ctx.restore()
    # specular glint
    ctx.set_source_rgba(1, 1, 1, 0.9)
    ctx.arc(x - r * 0.38, y - r * 0.42, r * 0.13, 0, 2 * math.pi)
    ctx.fill()
    if rim_rgb is not None:
        ctx.set_source_rgb(*rim_rgb)
        ctx.set_line_width(r * 0.14)
        ctx.arc(x, y, r * 1.03, 0, 2 * math.pi)
        ctx.stroke()
    ctx.restore()
