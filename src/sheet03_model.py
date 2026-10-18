"""Model sheet 03: the maquette turnaround. Front, three-quarter, profile, back,
orthographic, one scale, with construction lines, the puppeteer's hand ghosted in
the profile, and the eye focus drawn out."""
import cairo, math, os, sys, time
import numpy as np
from shapes import paper, text, INK, PENCIL, BOARD
import maquette as M

OUT = "../png/03_model_sheet.png"
CACHE = "../notes/cache"
os.makedirs(CACHE, exist_ok=True)
PPCM = 8.0
VW, VH = 600, 640
CENTER = (0.0, -6.5)
SW, SH = 2860, 940
TOPY = 215            # top of the view row on the sheet
BLUE = (0.16, 0.28, 0.55)

VIEWS = [("FRONT", 0.0), ("THREE-QUARTER", math.radians(38)), ("PROFILE", math.radians(90)), ("BACK", math.radians(180))]


def get_view(name, yaw, pose_kw):
    path = os.path.join(CACHE, f"model_{name}.npy")
    if os.path.exists(path) and "--fresh" not in sys.argv:
        return np.load(path)
    t0 = time.time()
    pose = M.Pose(**pose_kw)
    img = M.render(pose, width=VW, height=VH, ppcm=PPCM, center=CENTER, view_yaw=yaw, follow=True)
    np.save(path, img)
    print(name, round(time.time() - t0, 1), "s")
    return img


def y_px(y_cm):
    return TOPY + VH / 2 - (y_cm - CENTER[1]) * PPCM


def dashed(ctx, pts, rgb=INK, w=1.6, dash=(7, 5), alpha=0.8, close=False):
    ctx.save()
    ctx.set_source_rgba(*rgb, alpha)
    ctx.set_line_width(w)
    ctx.set_dash(list(dash))
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    if close:
        ctx.close_path()
    ctx.stroke()
    ctx.restore()


def arrow_dim(ctx, x0, y0, x1, y1, label, off=0, rgb=INK, size=14, at=0.5):
    ctx.save()
    ctx.set_source_rgba(*rgb, 0.85)
    ctx.set_line_width(1.3)
    ctx.move_to(x0, y0); ctx.line_to(x1, y1); ctx.stroke()
    ang = math.atan2(y1 - y0, x1 - x0)
    for (x, y, a) in ((x0, y0, ang + math.pi), (x1, y1, ang)):
        ctx.move_to(x, y)
        ctx.line_to(x - math.cos(a - 0.35) * 9, y - math.sin(a - 0.35) * 9)
        ctx.move_to(x, y)
        ctx.line_to(x - math.cos(a + 0.35) * 9, y - math.sin(a + 0.35) * 9)
        ctx.stroke()
    ctx.restore()
    mx, my = x0 + (x1 - x0) * at, y0 + (y1 - y0) * at
    ctx.save(); ctx.translate(mx, my)
    if abs(x1 - x0) < abs(y1 - y0):
        ctx.rotate(-math.pi / 2)
    text(ctx, label, 0, -6 + off, size, face="Gill Sans", align="center", rgb=rgb)
    ctx.restore()


def main():
    front_kw = dict(rods=True)
    renders = []
    for name, yaw in VIEWS:
        renders.append(get_view(name, yaw, front_kw if name == "FRONT" else {}))
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, SW, SH)
    ctx = cairo.Context(surf)
    paper(ctx, SW, SH, seed=21, grain=16000)
    MX = 70
    text(ctx, "THE WORKSHOP", MX, 78, 40, weight=cairo.FONT_WEIGHT_BOLD)
    text(ctx, "Model sheet 03 · TOKI · maquette turnaround, orthographic, one scale · v3, after the crit wall", MX, 118, 22, face="Gill Sans")
    text(ctx, "A hand-rod puppet. Cushion head in two halves hinged at the back; the hand goes in at the back so the wrist is the hinge. "
              "Piping in the seam between front and back panels, down the tail; the tail is the sleeve over the forearm.",
         MX, 150, 17, face="Gill Sans", slant=cairo.FONT_SLANT_ITALIC, alpha=0.75)
    gap = (SW - 2 * MX - 160 - 4 * VW) / 3
    xs = [MX + i * (VW + gap) for i in range(4)]
    # construction lines across all views
    guides = [(23.9, "top of tuft  23.9"), (16.5, "top of head  16.5"), (7.6, "eye line  7.6"),
              (-2.6, "mouth seam  −2.6"), (-16.5, "bottom of head  −16.5"), (-27.0, "playboard  −27")]
    for y, lab in guides:
        yy = y_px(y)
        ctx.save()
        ctx.set_source_rgba(*BLUE, 0.35)
        ctx.set_line_width(1)
        ctx.set_dash([2, 6])
        ctx.move_to(MX - 10, yy); ctx.line_to(SW - MX - 150, yy); ctx.stroke()
        ctx.restore()
        text(ctx, lab + " cm", SW - MX - 140, yy + 4, 13, face="Gill Sans", align="left", rgb=BLUE, alpha=0.85)
    for i, ((name, yaw), img) in enumerate(zip(VIEWS, renders)):
        x0 = xs[i]
        s, arr = M.to_surface(img)
        # soft contact shadow on the paper
        ctx.save()
        ctx.set_source_surface(s, x0, TOPY)
        ctx.paint()
        ctx.restore()
        M.fuzz_edges(ctx, img, x0, TOPY, seed=i, every=2)
        # below the playboard the sleeve fades out (it's there, but it isn't the character)
        by = y_px(-27.0)
        g = cairo.LinearGradient(0, by, 0, y_px(-38.5))
        g.add_color_stop_rgba(0, 0.957, 0.937, 0.890, 0.45)
        g.add_color_stop_rgba(1, 0.957, 0.937, 0.890, 1.0)
        ctx.set_source(g)
        ctx.rectangle(x0 - 5, by, VW + 10, TOPY + VH - by + 5)
        ctx.fill()
        ctx.set_source_rgb(*BOARD)
        ctx.rectangle(x0 + 10, by, VW - 20, 20); ctx.fill()
        ctx.set_source_rgba(0, 0, 0, 0.25)
        ctx.rectangle(x0 + 10, by, VW - 20, 3); ctx.fill()
        text(ctx, name, x0 + VW / 2, TOPY - 18, 22, face="Futura", weight=cairo.FONT_WEIGHT_BOLD, align="center")
    # ----- front-view callouts
    fx = xs[0]
    def fpx(x, y):
        return fx + VW / 2 + (x - CENTER[0]) * PPCM, y_px(y)
    a = fpx(-21, 19.5); b = fpx(21, 19.5)
    arrow_dim(ctx, a[0], a[1] - 0, b[0], b[1], "42 cm", off=-2, at=0.78)
    a = fpx(-25.5, 16.5); b = fpx(-25.5, -16.5)
    arrow_dim(ctx, a[0], a[1], b[0], b[1], "33 cm")
    a = fpx(-5.55, 7.6); b = fpx(5.55, 7.6)
    p0, p1 = fpx(-5.55, 13.4), fpx(5.55, 13.4)
    text(ctx, "eyes 10.6 cm, set close", fpx(23, 13.5)[0], fpx(23, 13.5)[1], 13, face="Chalkboard SE", rgb=BLUE)
    text(ctx, "and high, 9 mm apart", fpx(23, 13.5)[0], fpx(23, 13.5)[1] + 16, 13, face="Chalkboard SE", rgb=BLUE)
    text(ctx, "(room for two lid edges)", fpx(23, 13.5)[0], fpx(23, 13.5)[1] + 32, 13, face="Chalkboard SE", rgb=BLUE)
    text(ctx, "arm rods (removable)", fpx(10, -33)[0], fpx(10, -33)[1], 13, face="Chalkboard SE", rgb=BLUE)
    # ----- profile: the hand inside, and the focus line
    px0 = xs[2]
    def ppx(z, y):  # profile: image-right = -z
        return px0 + VW / 2 + (-z - CENTER[0]) * PPCM, y_px(y)
    # the puppeteer's hand, ghosted: forearm up the sleeve, fingers in the upper jaw, thumb in the lower
    # the hand enters at the back: wrist at the hinge, a 17 cm hand lying along the upper jaw, thumb in the lower
    hand_pts = [(-9.4, -36), (-9.4, -14), (-9.6, -5.5), (-7.5, 1.6), (2.0, 2.6), (8.6, 2.0), (9.3, 0.8), (8.6, -0.4),
                (-1.0, -1.2), (-3.0, -3.4), (5.6, -4.4), (6.4, -5.6), (5.6, -6.7), (-2.0, -7.6), (-0.6, -14), (-0.6, -36)]
    pts = [ppx(z, y) for (z, y) in hand_pts]
    ctx.save()
    ctx.move_to(*pts[0])
    for p_ in pts[1:]:
        ctx.line_to(*p_)
    ctx.set_source_rgba(*PENCIL, 0.16)
    ctx.fill_preserve()
    ctx.set_source_rgba(*PENCIL, 0.85)
    ctx.set_line_width(2)
    ctx.set_dash([6, 4])
    ctx.stroke()
    ctx.restore()
    tx, ty = ppx(-6, -20)
    text(ctx, "fingers: upper jaw", ppx(26, 4.5)[0], ppx(26, 4.5)[1], 14, face="Chalkboard SE", rgb=PENCIL)
    text(ctx, "thumb: lower jaw", ppx(26, -7)[0], ppx(26, -7)[1], 14, face="Chalkboard SE", rgb=PENCIL)
    text(ctx, "wrist = hinge, at the back", ppx(-12, 5.5)[0], ppx(-12, 5.5)[1], 14, face="Chalkboard SE", rgb=PENCIL)
    # focus: from the eye forward to a point 70 cm out (off the sheet; we draw the first 30 cm)
    e = ppx(13.6, 7.6)
    f = ppx(37, 6.6)
    dashed(ctx, [e, f], rgb=BLUE, w=1.5, dash=(3, 4))
    ctx.set_source_rgba(*BLUE, 0.9)
    text(ctx, "focus: 70 cm in front,", f[0] + 4, f[1] - 22, 13, face="Chalkboard SE", rgb=BLUE)
    text(ctx, "pupils set to meet there", f[0] + 4, f[1] - 6, 13, face="Chalkboard SE", rgb=BLUE)
    a = ppx(11, -22); b = ppx(-11, -22)
    arrow_dim(ctx, a[0], a[1], b[0], b[1], "22 cm deep", at=0.84)
    # ----- back: the seam and the access
    bx0 = xs[3]
    def bpx(x, y):  # back view: image-right = -x
        return bx0 + VW / 2 + (-x - CENTER[0]) * PPCM, y_px(y)
    text(ctx, "the sleeve enters at the back, under the hinge;", bpx(28, -32)[0], bpx(28, -32)[1], 13, face="Chalkboard SE", rgb=BLUE)
    text(ctx, "black velvet below the board. No zipper, no magnets:", bpx(28, -32)[0], bpx(28, -32)[1] + 17, 13, face="Chalkboard SE", rgb=BLUE)
    text(ctx, "nothing for a child to find", bpx(28, -32)[0], bpx(28, -32)[1] + 34, 13, face="Chalkboard SE", rgb=BLUE)
    # ----- three-quarter note
    qx0 = xs[1]
    text(ctx, "piping: the balloon's ink line from the front", qx0 + 30, y_px(-32), 14, face="Chalkboard SE", rgb=BLUE)
    text(ctx, "and three-quarter; in profile, a seam stripe", qx0 + 30, y_px(-32) + 18, 14, face="Chalkboard SE", rgb=BLUE)
    # scale bar
    sx, sy = MX, SH - 60
    for k in range(5):
        ctx.set_source_rgb(*(INK if k % 2 == 0 else (0.95, 0.93, 0.88)))
        ctx.rectangle(sx + k * 10 * PPCM, sy, 10 * PPCM, 8); ctx.fill()
    ctx.set_source_rgb(*INK); ctx.set_line_width(1); ctx.rectangle(sx, sy, 50 * PPCM, 8); ctx.stroke()
    text(ctx, "0", sx, sy - 6, 12, face="Gill Sans", align="center")
    text(ctx, "50 cm", sx + 50 * PPCM, sy - 6, 12, face="Gill Sans", align="center")
    text(ctx, "rendered in code: a signed-distance model sphere-traced in numpy, posed by puppeteer parameters "
              "(wrist, thumb, focus); edge fibers drawn in pycairo · Claude · 2026-10-17",
         SW - MX, SH - 48, 15, face="Gill Sans", align="right", alpha=0.6)
    surf.write_to_png(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
