"""Key art 05: "Tell Me Cookie". Dusk on the Street. Cookie Monster as a backlit
silhouette (someone else's character, drawn only as a shape), holding up his last
cookie. Toki leans in from behind the stoop wall, eyes on the cookie."""
import cairo, math, os, sys, random, time
import numpy as np
from shapes import text, rrect, ellipse
import maquette as M

OUT = "../png/05_key_art.png"
CACHE = "../notes/cache"
os.makedirs(CACHE, exist_ok=True)
W, H = 2400, 1500
RW, RH = 1350, 1180
ROX, ROY = 860, 10                     # where the Toki render sits on the canvas
CAM = dict(cam=(-8.0, 3.0, 165.0), look=(2.0, -1.0, 0.0), fov=28.0)   # v3c: over Cookie's shoulder, so Toki faces Cookie and us
COOKIE_WORLD = np.array([-22.0, 2.0, 78.0])   # held up between them, near the camera axis
# the focus point slides down the camera ray through the cookie, to just in front of Toki's face:
# same pixel in the picture, so the gaze lands on the cookie, but the pupils turn toward us
_cam = np.array(CAM["cam"])
FOCUS_WORLD = _cam + 0.68 * (COOKIE_WORLD - _cam)
NAVY = (0.13, 0.17, 0.33)


def project(p):
    cam = np.array(CAM["cam"]); look = np.array(CAM["look"])
    fw = look - cam; fw /= np.linalg.norm(fw)
    rt = np.cross(fw, [0, 1, 0]); rt /= np.linalg.norm(rt)
    up = np.cross(rt, fw)
    k = math.tan(math.radians(CAM["fov"]) / 2)
    v = np.array(p) - cam
    z = v @ fw
    sx, sy = (v @ rt) / z, (v @ up) / z
    px = RW / 2 + sx / k * (RH / 2)
    py = RH / 2 - sy / k * (RH / 2)
    return ROX + px, ROY + py


def toki_render():
    path = os.path.join(CACHE, "keyart_toki.npy")
    if os.path.exists(path) and "--fresh" not in sys.argv:
        return np.load(path)
    t0 = time.time()
    # v3: listening, not reaching (the crit wall and the cold readers read v1 as keep-away).
    # Pupils are glued: Toki looks at the cookie by turning its head.
    pose = M.Pose(jaw=0.2, wrist=(math.radians(-16), math.radians(4), math.radians(-9)), lids=0.0,
                  hands=((-5.5, -12.5, 16), (5.5, -12.5, 16)), hand_open=(0.15, 0.15))
    img = M.render(pose, width=RW, height=RH, persp=(CAM["cam"], CAM["look"], CAM["fov"]),
                   light=(-0.78, 0.42, 0.46), key_col=(1.08, 0.86, 0.64), fill_col=(0.55, 0.64, 0.92),
                   fill_dir=(0.8, 0.1, 0.5), amb_col=(0.62, 0.62, 0.78), amb=0.30,
                   rim_col=(1.0, 0.75, 0.5), rim_dir=(-0.6, 0.5, -0.6), steps=130)
    np.save(path, img)
    print("toki", round(time.time() - t0, 1), "s")
    return img


# ------------------------------------------------------------------ the set
def sky(ctx):
    g = cairo.LinearGradient(0, 0, 0, 1100)
    g.add_color_stop_rgb(0.0, 0.25, 0.30, 0.50)
    g.add_color_stop_rgb(0.45, 0.70, 0.52, 0.56)
    g.add_color_stop_rgb(0.75, 0.97, 0.70, 0.50)
    g.add_color_stop_rgb(1.0, 0.99, 0.84, 0.58)
    ctx.set_source(g)
    ctx.rectangle(0, 0, W, H)
    ctx.fill()
    # low sun glow behind the lamppost side
    rg = cairo.RadialGradient(260, 860, 10, 260, 860, 900)
    rg.add_color_stop_rgba(0, 1.0, 0.86, 0.6, 0.85)
    rg.add_color_stop_rgba(1, 1.0, 0.86, 0.6, 0.0)
    ctx.set_source(rg)
    ctx.rectangle(0, 0, W, H)
    ctx.fill()


def far_buildings(ctx, rnd):
    x = -20
    while x < 1250:
        w = rnd.uniform(120, 260)
        h = rnd.uniform(260, 560)
        top = 1080 - h
        ctx.set_source_rgb(0.47, 0.40, 0.52)
        ctx.rectangle(x, top, w, h + 400)
        ctx.fill()
        # windows
        for wy in np.arange(top + 30, 1060, 42):
            for wx in np.arange(x + 14, x + w - 20, 30):
                if rnd.random() < 0.3:
                    ctx.set_source_rgba(1.0, 0.85, 0.5, rnd.uniform(0.5, 0.9))
                else:
                    ctx.set_source_rgba(0.38, 0.33, 0.45, 0.8)
                ctx.rectangle(wx, wy, 13, 20)
                ctx.fill()
        x += w + rnd.uniform(4, 16)
    # haze
    g = cairo.LinearGradient(0, 560, 0, 1100)
    g.add_color_stop_rgba(0, 0.95, 0.75, 0.6, 0.0)
    g.add_color_stop_rgba(1, 0.97, 0.80, 0.62, 0.55)
    ctx.set_source(g)
    ctx.rectangle(0, 500, 1300, 700)
    ctx.fill()


def bricks(ctx, x0, y0, x1, y1, rnd, base=(0.50, 0.27, 0.20), bw=34, bh=13, light_left=True):
    ctx.save()
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.clip()
    ctx.set_source_rgb(0.66, 0.55, 0.47)
    ctx.paint()
    row = 0
    y = y0
    while y < y1:
        off = (bw / 2) if row % 2 else 0
        x = x0 - off
        while x < x1:
            j = rnd.gauss(0, 0.045)
            c = tuple(max(0, min(1, v + j + rnd.gauss(0, 0.01))) for v in base)
            ctx.set_source_rgb(*c)
            ctx.rectangle(x + 1.2, y + 1.2, bw - 2.4, bh - 2.4)
            ctx.fill()
            x += bw
        y += bh
        row += 1
    # warm light from the left, falling off to the right; darker toward the ground
    g = cairo.LinearGradient(x0, 0, x1, 0)
    g.add_color_stop_rgba(0, 1.0, 0.78, 0.5, 0.30 if light_left else 0)
    g.add_color_stop_rgba(1, 0.1, 0.05, 0.15, 0.35)
    ctx.set_source(g)
    ctx.paint()
    ctx.restore()


def brownstone(ctx, rnd):
    bricks(ctx, 1180, 0, W, 1120, rnd)
    # window with warm interior
    wx, wy, ww, wh = 1700, 120, 330, 470
    ctx.set_source_rgb(0.80, 0.72, 0.60)  # stone lintel and sill
    ctx.rectangle(wx - 34, wy - 52, ww + 68, 48); ctx.fill()
    ctx.rectangle(wx - 26, wy + wh, ww + 52, 30); ctx.fill()
    ctx.set_source_rgb(0.93, 0.90, 0.82)  # frame
    ctx.rectangle(wx - 10, wy - 10, ww + 20, wh + 20); ctx.fill()
    g = cairo.LinearGradient(0, wy, 0, wy + wh)
    g.add_color_stop_rgb(0, 1.0, 0.85, 0.52)
    g.add_color_stop_rgb(1, 0.92, 0.58, 0.30)
    ctx.set_source(g)
    ctx.rectangle(wx, wy, ww, wh); ctx.fill()
    # curtain
    ctx.set_source_rgba(0.85, 0.35, 0.28, 0.75)
    ctx.move_to(wx, wy); ctx.curve_to(wx + 90, wy + 140, wx + 40, wy + 300, wx + 70, wy + wh)
    ctx.line_to(wx, wy + wh); ctx.close_path(); ctx.fill()
    ctx.set_source_rgb(0.93, 0.90, 0.82)
    ctx.rectangle(wx + ww / 2 - 6, wy, 12, wh); ctx.fill()
    ctx.rectangle(wx, wy + wh * 0.45, ww, 12); ctx.fill()
    # window glow onto the wall
    rg = cairo.RadialGradient(wx + ww / 2, wy + wh / 2, 50, wx + ww / 2, wy + wh / 2, 520)
    rg.add_color_stop_rgba(0, 1.0, 0.8, 0.45, 0.22)
    rg.add_color_stop_rgba(1, 1.0, 0.8, 0.45, 0.0)
    ctx.set_source(rg); ctx.rectangle(1180, 0, W - 1180, 1120); ctx.fill()
    # stoop: stone steps rising to the right
    for i in range(7):
        sy = 1120 - i * 46
        sx = 2080 + i * 20
        ctx.set_source_rgb(0.60 - i * 0.015, 0.50 - i * 0.015, 0.43 - i * 0.012)
        ctx.rectangle(sx, sy - 46, W - sx, 46); ctx.fill()
        ctx.set_source_rgba(1, 0.9, 0.75, 0.35)
        ctx.rectangle(sx, sy - 46, W - sx, 5); ctx.fill()
    # iron railing with a curl at the newel
    ctx.set_source_rgb(0.08, 0.08, 0.09)
    ctx.set_line_width(7)
    ctx.move_to(2060, 820); ctx.line_to(W, 520); ctx.stroke()
    for i in range(9):
        x = 2075 + i * 40
        y_top = 820 - (x - 2060) * (300 / (W - 2060))
        ctx.set_line_width(4)
        ctx.move_to(x, y_top); ctx.line_to(x, 1120 - max(0, (x - 2080)) * 0.0); ctx.stroke()
    ctx.set_line_width(7)
    ctx.move_to(2060, 820); ctx.line_to(2060, 1080); ctx.stroke()
    ctx.new_sub_path()
    ctx.arc(2040, 812, 22, 0, math.pi * 1.6); ctx.stroke()


def lamppost(ctx):
    x = 640
    ctx.set_source_rgb(0.10, 0.14, 0.12)
    ctx.rectangle(x - 9, 180, 18, 1000); ctx.fill()
    ctx.rectangle(x - 22, 1000, 44, 200); ctx.fill()
    # lantern
    ctx.move_to(x - 40, 110); ctx.line_to(x + 40, 110); ctx.line_to(x + 28, 190); ctx.line_to(x - 28, 190); ctx.close_path()
    ctx.fill()
    ctx.set_source_rgb(1.0, 0.88, 0.55)
    ctx.move_to(x - 30, 120); ctx.line_to(x + 30, 120); ctx.line_to(x + 21, 180); ctx.line_to(x - 21, 180); ctx.close_path()
    ctx.fill()
    ctx.set_source_rgb(0.10, 0.14, 0.12)
    ctx.move_to(x - 50, 112); ctx.line_to(x, 70); ctx.line_to(x + 50, 112); ctx.close_path(); ctx.fill()
    rg = cairo.RadialGradient(x, 150, 10, x, 150, 300)
    rg.add_color_stop_rgba(0, 1.0, 0.9, 0.6, 0.55)
    rg.add_color_stop_rgba(1, 1.0, 0.9, 0.6, 0.0)
    ctx.set_source(rg); ctx.arc(x, 150, 300, 0, 2 * math.pi); ctx.fill()


def front_wall(ctx, rnd, top):
    """The stoop's side wall Toki is behind: the playboard, dressed as the Street."""
    bricks(ctx, 1060, top + 26, W, H, rnd, base=(0.46, 0.24, 0.18), bw=40, bh=15)
    g = cairo.LinearGradient(0, top + 26, 0, H)
    g.add_color_stop_rgba(0, 0, 0, 0, 0.0)
    g.add_color_stop_rgba(1, 0.05, 0.02, 0.08, 0.45)
    ctx.set_source(g); ctx.rectangle(1060, top + 26, W - 1060, H); ctx.fill()
    # coping stone
    ctx.set_source_rgb(0.76, 0.68, 0.58)
    ctx.rectangle(1040, top, W - 1040, 30); ctx.fill()
    ctx.set_source_rgba(1, 0.92, 0.78, 0.6)
    ctx.rectangle(1040, top, W - 1040, 5); ctx.fill()
    ctx.set_source_rgba(0, 0, 0, 0.3)
    ctx.rectangle(1040, top + 30, W - 1040, 6); ctx.fill()
    # end of the wall
    ctx.set_source_rgb(0.40, 0.22, 0.17)
    ctx.rectangle(1040, top + 30, 26, H); ctx.fill()


def sidewalk(ctx):
    g = cairo.LinearGradient(0, 1080, 0, H)
    g.add_color_stop_rgb(0, 0.70, 0.62, 0.58)
    g.add_color_stop_rgb(1, 0.46, 0.40, 0.42)
    ctx.set_source(g)
    ctx.rectangle(0, 1080, 1100, H - 1080); ctx.fill()
    ctx.set_source_rgba(0.3, 0.25, 0.3, 0.35)
    ctx.set_line_width(2)
    for i in range(5):
        y = 1110 + i * i * 22
        ctx.move_to(0, y); ctx.line_to(1100, y); ctx.stroke()


# ------------------------------------------------------------------ cookie (the shape only)
def cookie_monster_silhouette(ctx, rnd, cookie_xy):
    cx, cy = 360, 1070
    R = 430
    hx, hy = cookie_xy[0] - 30, cookie_xy[1] + 58
    parts = []
    parts.append(lambda c: (c.new_sub_path(), c.arc(cx, cy, R, 0, 2 * math.pi)))
    # googly eyes: small, touching, toward the side he faces
    for ang, er in ((-71, 64), (-55, 61)):
        ex = cx + (R + 34) * math.cos(math.radians(ang))
        ey = cy + (R + 34) * math.sin(math.radians(ang))
        parts.append(lambda c, ex=ex, ey=ey, er=er: (c.new_sub_path(), c.arc(ex, ey, er, 0, 2 * math.pi)))
    sx, sy = cx + R * math.cos(math.radians(30)), cy - R * math.sin(math.radians(30))

    def arm(c):
        n = 30
        left, right = [], []
        c1x, c1y = sx + 150, sy - 20
        for i in range(n + 1):
            u = i / n
            bx = (1 - u) ** 2 * sx + 2 * (1 - u) * u * c1x + u * u * hx
            by = (1 - u) ** 2 * sy + 2 * (1 - u) * u * c1y + u * u * hy
            tx = 2 * (1 - u) * (c1x - sx) + 2 * u * (hx - c1x)
            ty = 2 * (1 - u) * (c1y - sy) + 2 * u * (hy - c1y)
            L = math.hypot(tx, ty) or 1
            px, py = -ty / L, tx / L
            w = 96 * (1 - u) + 50 * u
            left.append((bx + px * w, by + py * w)); right.append((bx - px * w, by - py * w))
        poly = left + list(reversed(right))
        area = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))
        if area < 0:      # match the arcs' winding, or overlaps cancel under the nonzero rule
            poly = poly[::-1]
        c.new_sub_path(); c.move_to(*poly[0])
        for p in poly[1:]:
            c.line_to(*p)
        c.close_path()
    parts.append(arm)
    parts.append(lambda c: (c.new_sub_path(), c.arc(sx - 30, sy + 20, 110, 0, 2 * math.pi)))   # shoulder
    parts.append(lambda c: (c.new_sub_path(), c.arc(sx + 30, sy + 110, 105, 0, 2 * math.pi)))  # under the arm
    parts.append(lambda c: (c.new_sub_path(), c.arc(hx, hy - 8, 66, 0, 2 * math.pi)))          # hand
    for (fx, fy) in ((-34, -48), (0, -58), (34, -46)):
        def finger(c, fx=fx, fy=fy):
            c.new_sub_path(); c.save(); c.translate(hx + fx, hy + fy); c.scale(22, 30)
            c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()
        parts.append(finger)

    def union(c):
        for p in parts:
            p(c)

    body = (0.10, 0.18, 0.42)   # deep blue, not black: the cold read found black menacing
    ctx.save()
    ctx.new_path(); union(ctx)
    ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
    ctx.set_source_rgb(*body); ctx.fill_preserve()
    ctx.clip()
    # over-the-shoulder: we see his back, in fur. Long strokes flowing down and out from the crown.
    frnd = random.Random(23)
    for _ in range(26000):
        x = frnd.uniform(-80, 1000); y = frnd.uniform(500, 1500)
        a = math.atan2(y - 560, x - 480) + frnd.gauss(0, 0.3)
        a = 0.55 * a + 0.45 * (math.pi / 2)
        ln = frnd.uniform(10, 26)
        # light: warm from the low sun at upper left, cool from the window at right
        warm = max(0.0, 1 - math.hypot(x - 120, y - 620) / 520)
        cool = max(0.0, 1 - math.hypot(x - 760, y - 760) / 360)
        v = frnd.gauss(0, 0.05)
        r_ = body[0] + v + warm * 0.25 + cool * 0.05
        g_ = body[1] + v + warm * 0.13 + cool * 0.12
        b_ = body[2] + v + warm * 0.02 + cool * 0.20
        ctx.set_source_rgba(min(1, max(0, r_)), min(1, max(0, g_)), min(1, max(0, b_)), 0.55)
        ctx.set_line_width(frnd.uniform(1.2, 2.6))
        ctx.move_to(x, y); ctx.line_to(x + math.cos(a) * ln, y + math.sin(a) * ln); ctx.stroke()
    # shadow side, away from the sun, so he reads round
    sg = cairo.RadialGradient(260, 760, 120, 420, 1050, 640)
    sg.add_color_stop_rgba(0, 0, 0, 0, 0.0); sg.add_color_stop_rgba(1, 0.02, 0.03, 0.10, 0.55)
    ctx.set_source(sg); ctx.paint()
    ctx.restore()
    # fur: per part, outward normals from that part alone; skip fibers that start inside the union
    ctx.save()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    probe = cairo.Context(cairo.ImageSurface(cairo.FORMAT_A8, 4, 4))
    probe.new_path(); union(probe)
    for part in parts:
        pc = cairo.Context(cairo.ImageSurface(cairo.FORMAT_A8, 4, 4))
        pc.new_path(); part(pc)
        flat = pc.copy_path_flat()
        pts = []
        cur = start = None
        for kind, p in flat:
            if kind == cairo.PATH_MOVE_TO:
                cur = start = p
            elif kind in (cairo.PATH_LINE_TO, cairo.PATH_CLOSE_PATH):
                q = p if kind == cairo.PATH_LINE_TO else start
                if cur is not None and q is not None:
                    dx, dy = q[0] - cur[0], q[1] - cur[1]
                    L = math.hypot(dx, dy)
                    m = max(1, int(L / 2.2))
                    for i in range(m):
                        u = i / m
                        pts.append((cur[0] + dx * u, cur[1] + dy * u, dx / (L or 1), dy / (L or 1)))
                cur = q
        for (x, y, tx, ty) in pts:
            nx, ny = ty, -tx
            if pc.in_fill(x + nx * 3, y + ny * 3):
                nx, ny = -nx, -ny
            if probe.in_fill(x + nx * 3, y + ny * 3):
                continue
            a = math.atan2(ny, nx) + rnd.gauss(0, 0.45)
            ln = rnd.uniform(8, 24)
            facing = (-nx * 0.75 - ny * 0.66)
            if facing > 0.35 and rnd.random() < 0.55:
                ctx.set_source_rgba(0.95, 0.72 + rnd.uniform(0, 0.12), 0.48, min(0.7, 0.2 + facing * 0.45))
            else:
                ctx.set_source_rgba(*body, 0.9)
            ctx.set_line_width(rnd.uniform(1.4, 3.0))
            ctx.new_path()
            ctx.move_to(x - math.cos(a) * ln * 0.45, y - math.sin(a) * ln * 0.45)
            ctx.line_to(x + math.cos(a) * ln, y + math.sin(a) * ln)
            ctx.stroke()
    ctx.restore()


def cookie_glow(ctx, x, y):
    rg = cairo.RadialGradient(x, y, 20, x, y, 240)
    rg.add_color_stop_rgba(0, 1.0, 0.86, 0.55, 0.35)
    rg.add_color_stop_rgba(1, 1.0, 0.86, 0.55, 0.0)
    ctx.set_source(rg); ctx.arc(x, y, 240, 0, 2 * math.pi); ctx.fill()


def the_cookie(ctx, rnd, x, y):
    ctx.save()
    ctx.translate(x, y); ctx.rotate(-0.25)
    # bumpy edge
    ctx.new_path()
    for i in range(73):
        a = 2 * math.pi * i / 72
        r = 64 + rnd.gauss(0, 1.8)
        (ctx.move_to if i == 0 else ctx.line_to)(math.cos(a) * r, math.sin(a) * r * 0.9)
    ctx.close_path()
    g = cairo.RadialGradient(-18, -20, 5, 0, 0, 70)
    g.add_color_stop_rgb(0, 0.95, 0.76, 0.46)
    g.add_color_stop_rgb(0.7, 0.84, 0.60, 0.32)
    g.add_color_stop_rgb(1, 0.66, 0.42, 0.20)
    ctx.set_source(g); ctx.fill_preserve()
    ctx.set_source_rgba(0.45, 0.27, 0.12, 0.6); ctx.set_line_width(2); ctx.stroke()
    # baked speckle
    for _ in range(260):
        a = rnd.uniform(0, 2 * math.pi); r = 60 * math.sqrt(rnd.random())
        ctx.set_source_rgba(0.55, 0.35, 0.15, rnd.uniform(0.1, 0.35))
        ctx.arc(math.cos(a) * r, math.sin(a) * r * 0.9, rnd.uniform(0.6, 1.8), 0, 2 * math.pi); ctx.fill()
    # chips
    for (cx_, cy_, cr) in ((-26, -18, 9), (18, -28, 8), (30, 10, 10), (-8, 22, 9), (-38, 14, 7), (6, -2, 6), (40, -12, 6)):
        ctx.new_path()
        for i in range(9):
            a = 2 * math.pi * i / 8
            r = cr * rnd.uniform(0.75, 1.15)
            (ctx.move_to if i == 0 else ctx.line_to)(cx_ + math.cos(a) * r, cy_ + math.sin(a) * r * 0.85)
        ctx.close_path()
        ctx.set_source_rgb(0.24, 0.12, 0.07); ctx.fill_preserve()
        ctx.set_source_rgba(0.55, 0.35, 0.25, 0.6); ctx.set_line_width(1); ctx.stroke()
        ctx.set_source_rgba(1, 0.9, 0.8, 0.35); ctx.arc(cx_ - cr * 0.3, cy_ - cr * 0.3, cr * 0.25, 0, 2 * math.pi); ctx.fill()
    ctx.restore()
    # crumbs falling
    for _ in range(26):
        cx_ = x + rnd.gauss(0, 30)
        cy_ = y + 70 + abs(rnd.gauss(0, 120))
        ctx.set_source_rgba(0.86, 0.62, 0.34, rnd.uniform(0.6, 0.95))
        ctx.arc(cx_, cy_, rnd.uniform(1.5, 4.0), 0, 2 * math.pi); ctx.fill()


def speech_bubble(ctx, x, y, w, h, tail_to, lines):
    r = h * 0.42
    ctx.save()
    ctx.new_path()
    rrect(ctx, x, y, w, h, r)
    ctx.set_source_rgb(0.99, 0.98, 0.95); ctx.fill_preserve()
    ctx.set_source_rgb(*NAVY); ctx.set_line_width(5); ctx.stroke()
    # tail
    bx = x + w * 0.30
    ctx.move_to(bx - 24, y + h - 3)
    ctx.curve_to(bx - 10, y + h + 30, tail_to[0] + 10, tail_to[1] - 40, *tail_to)
    ctx.curve_to(tail_to[0] + 30, tail_to[1] - 60, bx + 30, y + h + 20, bx + 26, y + h - 3)
    ctx.set_source_rgb(0.99, 0.98, 0.95); ctx.fill_preserve()
    ctx.set_source_rgb(*NAVY); ctx.set_line_width(5); ctx.stroke()
    ctx.set_source_rgb(0.99, 0.98, 0.95)
    ctx.rectangle(bx - 21, y + h - 8, 44, 9); ctx.fill()
    for i, (s, size) in enumerate(lines):
        text(ctx, s, x + w / 2, y + 56 + i * 52, size, face="Futura", weight=cairo.FONT_WEIGHT_BOLD,
             align="center", rgb=NAVY)
    ctx.restore()


def main():
    rnd = random.Random(7)
    img = toki_render()
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    sky(ctx)
    far_buildings(ctx, random.Random(3))
    brownstone(ctx, random.Random(5))
    lamppost(ctx)
    sidewalk(ctx)
    # Toki behind the wall
    s, arr = M.to_surface(img)
    # soft shadow cast onto the brick behind Toki
    sh = cairo.ImageSurface(cairo.FORMAT_ARGB32, RW, RH)
    sc = cairo.Context(sh)
    sc.set_source_surface(s, 0, 0); sc.paint()
    ctx.save()
    ctx.translate(ROX + 60, ROY + 30)
    ctx.set_source_rgba(0.12, 0.05, 0.10, 0.32)
    ctx.mask_surface(sh, 0, 0)
    ctx.restore()
    ctx.set_source_surface(s, ROX, ROY); ctx.paint()
    M.fuzz_edges(ctx, img, ROX, ROY, seed=77, every=1, length=(1.4, 4.6))
    wall_top = project((0.0, -27.0, 8.0))[1]   # lower than v1, so the bubble's tail shows; the black sleeve stays hidden
    front_wall(ctx, random.Random(9), wall_top)
    # Cookie, his cookie, his line
    cxy = project(tuple(COOKIE_WORLD))
    cookie_glow(ctx, *cxy)
    cookie_monster_silhouette(ctx, random.Random(11), cxy)
    the_cookie(ctx, random.Random(13), *cxy)
    speech_bubble(ctx, 120, 130, 720, 190, (500, 545),
                  [("TOKI CAN'T EAT COOKIE?", 36), ("ME TELL YOU WHAT IT LIKE!", 36)])
    # vignette
    rg = cairo.RadialGradient(W / 2, H / 2, 500, W / 2, H / 2, 1500)
    rg.add_color_stop_rgba(0, 0, 0, 0, 0)
    rg.add_color_stop_rgba(1, 0.08, 0.03, 0.10, 0.45)
    ctx.set_source(rg); ctx.paint()
    # title block
    text(ctx, "TOKI", W - 70, H - 96, 44, face="Futura", weight=cairo.FONT_WEIGHT_BOLD, align="right",
         rgb=(0.98, 0.95, 0.88))
    text(ctx, "key art 05 · “Tell Me Cookie”", W - 70, H - 60, 20, face="Gill Sans", align="right",
         rgb=(0.98, 0.95, 0.88), alpha=0.9)
    text(ctx, "drawn in code · Cookie Monster shown from behind, as a shape only · v3 · Claude · 2026-10-18", W - 70, H - 32, 14,
         face="Gill Sans", align="right", rgb=(0.98, 0.95, 0.88), alpha=0.7)
    surf.write_to_png(OUT)
    print("wrote", OUT, "cookie at", cxy, "wall top", wall_top)


if __name__ == "__main__":
    main()
