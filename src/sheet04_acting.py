"""Acting sheet 04: ten beats. Muppet acting is mostly angle and timing; the face
barely moves. Every beat here is posed only with what a puppeteer actually has:
wrist (yaw, pitch, roll), thumb (jaw), focus (where both pupils meet), lids, rods."""
import cairo, math, os, sys, time
import numpy as np
from shapes import paper, text, INK, PENCIL, BOARD
import maquette as M

OUT = "../png/04_acting_sheet.png"
CACHE = "../notes/cache"
os.makedirs(CACHE, exist_ok=True)
CW, CH = 500, 540
PPCM = 7.0
CENTER = (0.0, -2.0)
COLS = 5
MX = 70
TOP = 210
CAP = 150
SW = MX * 2 + COLS * CW + (COLS - 1) * 20
SH = TOP + 2 * (CH + CAP) + 70
BLUE = (0.16, 0.28, 0.55)

d = math.radians
BEATS = [
    ("Hi! I'm Toki!", "hello",
     dict(jaw=0.42, wrist=(d(8), d(-7), d(3)),
          hands=((-27, -14, 6), (25, 10, 8)), hand_open=(0.6, 1.0)),
     "thumb opens on the stressed syllable; right rod up and wagging"),
    ("Hmm...", "thinking",
     dict(jaw=0.04, wrist=(d(-20), d(-24), d(13)),
          hands=((-26, -18, 4), (8, -16, 13)), hand_open=(0.5, 0.2)),
     "the whole head looks up and off (the pupils are glued); hold two beats"),
    ("Wait. I'm not sure.", "catching itself",
     dict(jaw=0.12, wrist=(d(12), d(-12), d(-4)),
          hands=((-25, -17, 5), (7, -7, 16)), hand_open=(0.4, 0.3)),
     "head pulls back off the line; one hand to the mouth"),
    ("Let's find out!", "let's find out",
     dict(jaw=0.5, wrist=(d(8), d(11), 0.0),
          hands=((-20, -9, 17), (20, -9, 17)), hand_open=(0.9, 0.9)),
     "the second half of the catchphrase: wrist drops toward the lens"),
    ("What does it taste like?", "tell me cookie",
     dict(jaw=0.12, wrist=(d(-30), d(-6), d(-7)),
          hands=((-6, -15, 15), (6, -15, 15)), hand_open=(0.2, 0.2)),
     "the head turns to the cookie; hands clasped, listening"),
    ("I don't remember yesterday. So I read about it!", "the notebook",
     dict(jaw=0.3, wrist=(d(4), d(17), d(8)),
          hands=((-8, -17, 16), (8, -17, 16)), hand_open=(0.3, 0.3)),
     "a comic morning routine, never grief: reading the notebook aloud"),
    ("No, thank you.", "a boundary",
     dict(jaw=0.05, wrist=(d(22), d(-2), d(-6)), lids=0.1,
          hands=((-26, -18, 4), (13, -5, 21)), hand_open=(0.4, 1.0)),
     "kind and clear: palm out, low; a small head shake; then back to play"),
    ("I think so? Mine might be different from yours. Will you tell me what yours feel like?", "the reach",
     dict(jaw=0.22, wrist=(d(-4), d(14), d(12)),
          hands=((-25, -16, 6), (15, -10, 21)), hand_open=(0.4, 0.9)),
     "head tilts down toward the child; a hand reaches, and waits"),
    ("Ha!", "laughing",
     dict(jaw=0.55, wrist=(d(4), d(-22), d(-6)),
          hands=((-14, -17, 12), (14, -17, 12)), hand_open=(0.5, 0.5)),
     "head back, jaw wide, eyes open (no lid swap mid-laugh): the laugh is in the wrist"),
    ("(listening)", "listening",
     dict(jaw=0.02, wrist=(d(-30), d(2), d(5)),
          hands=((-25, -19, 4), (25, -19, 4)), hand_open=(0.3, 0.3)),
     "alive but quiet: small nods, breath in the wrist, head turned to the speaker"),
]


def get(i, kw):
    path = os.path.join(CACHE, f"beat_{i:02d}.npy")
    if os.path.exists(path) and "--fresh" not in sys.argv:
        return np.load(path)
    t0 = time.time()
    img = M.render(M.Pose(**kw), width=CW, height=CH, ppcm=PPCM, center=CENTER, view_yaw=d(14), follow=True)
    np.save(path, img)
    print("beat", i, round(time.time() - t0, 1), "s")
    return img


def wrap(ctx, s, x, y, size, maxw, face="Gill Sans", **kw):
    ctx.select_font_face(face, cairo.FONT_SLANT_NORMAL, kw.get("weight", cairo.FONT_WEIGHT_NORMAL))
    ctx.set_font_size(size)
    words, line, lines = s.split(), "", []
    for w in words:
        t = (line + " " + w).strip()
        if ctx.text_extents(t).x_advance > maxw and line:
            lines.append(line)
            line = w
        else:
            line = t
    lines.append(line)
    for k, ln in enumerate(lines):
        text(ctx, ln, x, y + k * size * 1.3, size, face=face, **kw)
    return len(lines)


def main():
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, SW, SH)
    ctx = cairo.Context(surf)
    paper(ctx, SW, SH, seed=33, grain=16000)
    text(ctx, "THE WORKSHOP", MX, 78, 40, weight=cairo.FONT_WEIGHT_BOLD)
    text(ctx, "Acting sheet 04 · TOKI · ten beats, posed only with what a puppeteer has", MX, 118, 22, face="Gill Sans")
    text(ctx, "Muppet acting is mostly angle and timing. The pupils are glued felt, so Toki looks at something only by turning its head; "
              "the thumb drops the jaw. Numbers under each beat: wrist yaw / pitch / roll, jaw, lids.",
         MX, 150, 17, face="Gill Sans", slant=cairo.FONT_SLANT_ITALIC, alpha=0.75)
    for i, (line, name, kw, note) in enumerate(BEATS):
        img = get(i, kw)
        col, row = i % COLS, i // COLS
        x0 = MX + col * (CW + 20)
        y0 = TOP + row * (CH + CAP)
        # cell ground
        ctx.set_source_rgba(1, 1, 1, 0.22)
        ctx.rectangle(x0, y0, CW, CH); ctx.fill()
        s, arr = M.to_surface(img)
        ctx.set_source_surface(s, x0, y0); ctx.paint()
        M.fuzz_edges(ctx, img, x0, y0, seed=40 + i, every=2)
        by = y0 + CH / 2 - (-24 - CENTER[1]) * PPCM
        g = cairo.LinearGradient(0, by, 0, by + 70)
        g.add_color_stop_rgba(0, 0.957, 0.937, 0.890, 0.4)
        g.add_color_stop_rgba(1, 0.957, 0.937, 0.890, 1.0)
        ctx.set_source(g); ctx.rectangle(x0, by, CW, y0 + CH - by); ctx.fill()
        ctx.set_source_rgb(*BOARD); ctx.rectangle(x0 + 8, by, CW - 16, 16); ctx.fill()
        text(ctx, f"{i+1:02d}", x0 + 12, y0 + 30, 22, face="Futura", weight=cairo.FONT_WEIGHT_BOLD, alpha=0.5)
        text(ctx, name.upper(), x0 + 54, y0 + 30, 15, face="Futura", alpha=0.55)
        # caption
        cy = y0 + CH + 30
        n = wrap(ctx, "“" + line + "”", x0 + 4, cy, 21, CW - 10, face="Futura", weight=cairo.FONT_WEIGHT_BOLD)
        cy += n * 27 + 6
        n2 = wrap(ctx, note, x0 + 4, cy, 15, CW - 10, face="Chalkboard SE", rgb=BLUE)
        cy += n2 * 19.5 + 4
        w = kw["wrist"]
        nums = f"wrist {math.degrees(w[0]):+.0f}° / {math.degrees(w[1]):+.0f}° / {math.degrees(w[2]):+.0f}°   jaw {math.degrees(kw['jaw']):.0f}°   lids {kw.get('lids', 0):.2f}"
        text(ctx, nums, x0 + 4, cy + 4, 13, face="Gill Sans", alpha=0.6)
    text(ctx, "v3, after the crit wall (Thumb caught v2 moving the pupils). Rendered in code: one signed-distance maquette, re-posed per beat · Claude · 2026-10-18",
         SW - MX, SH - 30, 15, face="Gill Sans", align="right", alpha=0.6)
    surf.write_to_png(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
