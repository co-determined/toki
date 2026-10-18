"""Toki as a 3D maquette: a signed-distance model sphere-traced in numpy.

Units are centimetres. y up, z toward the front of the puppet, x to its left
(our right in the front view). The model is posed by puppeteer parameters:
  wrist (yaw, pitch, roll)  - the head turns about the wrist at the top of the sleeve
  jaw                       - the thumb dropping the lower jaw (radians)
  focus                     - the point in space both pupils look at
  lids                      - fleece lids, 0 open .. 1 shut
  hands                     - wrist positions for the two rod arms (head coords)

Construction mirrors the build: a cushion head in two halves hinged at the back
(the mouth plate), piping sewn into the seam between the front and back panels
and continuing down the tail, ping-pong-ball eyes, a fleece curl, a sleeve.
"""
import numpy as np
import math

F = np.float32

# --------------------------------------------------------------- geometry
HEAD_B = np.array([21.0, 16.5, 11.0], F)   # half extents: 42 wide (inertia, weight), 22 deep (a 17-19 cm hand lies flat inside)
HEAD_R = 10.0                               # rounding: a cushion
MOUTH_Y = -2.6                              # mouth seam height at center
SMILE_K = 0.0068                            # seam curvature (a smile)
HINGE = np.array([0.0, -2.6, -7.5], F)      # mouth plate hinge, toward the back
EYE_R = 5.3
EYES = np.array([[-5.75, 7.6, 8.3], [5.75, 7.6, 8.3]], F)   # 9 mm apart: room for two lid edges
TAIL_A = np.array([5.0, -12.0, -5.0], F)    # sleeve enters at the back: the wrist is the hinge
TAIL_B = np.array([-16.0, -54.0, -5.0], F)  # forearm, below the playboard
TAIL_RA, TAIL_RB = 6.4, 5.1
PIPE_R = 1.35
SHOULDERS = np.array([[-19.0, -4.5, 0.0], [19.0, -4.5, 0.0]], F)
WRIST_PIVOT = np.array([5.0, -12.5, -5.0], F)
SLEEVE_Y = -28.5                            # below this the sleeve is black velvet (the puppeteer's sleeve)
FOCUS_HEAD = np.array([0.0, 6.0, 70.0], F)  # pupils are glued felt: focus is fixed in head space

COL = {
    0: (0.955, 0.925, 0.845),   # body: cream Antron fleece
    1: (0.13, 0.17, 0.33),      # piping: ink navy
    2: (0.975, 0.975, 0.955),   # eye white
    3: (0.03, 0.03, 0.045),     # pupil felt
    4: (0.13, 0.17, 0.33),      # curl
    5: (0.13, 0.17, 0.33),      # hands
    6: (0.11, 0.10, 0.19),      # mouth interior
    7: (0.84, 0.43, 0.48),      # tongue
    8: (0.06, 0.06, 0.06),      # rods
    9: (0.94, 0.91, 0.83),      # lids
    10: (0.07, 0.07, 0.09),     # black velvet sleeve
}


def curl_points():
    """v3: a soft quiff, not a hook. The cold readers saw the question-mark hook as a suitcase handle
    and a coat hanger, and the builder said crew would hang the puppet by it. So: a fat lock of navy
    fleece that rises off the top and curls forward over the front edge, tip tucked. Nothing to grab."""
    ctrl = np.array([[-2.6, 14.6, 1.0], [-3.0, 18.6, 2.6], [-3.4, 21.0, 5.6], [-3.7, 21.2, 8.6],
                     [-3.9, 19.6, 10.4], [-4.0, 17.9, 9.6]], F)
    rad = np.array([3.2, 3.0, 2.6, 2.1, 1.6, 1.1], F)
    pts, radii = [], []
    for i in range(len(ctrl) - 1):
        for k in range(5):
            u = k / 5
            pts.append(ctrl[i] * (1 - u) + ctrl[i + 1] * u)
            radii.append(rad[i] * (1 - u) + rad[i + 1] * u)
    pts.append(ctrl[-1]); radii.append(rad[-1])
    return np.array(pts, F), np.array(radii, F)


CURL_P, CURL_R = curl_points()
CURL_CENTER = CURL_P.mean(0)
CURL_BOUND = float(np.max(np.linalg.norm(CURL_P - CURL_CENTER, axis=1)) + 3.0)


# --------------------------------------------------------------- sdf helpers
def length(v):
    return np.sqrt(np.einsum("ij,ij->i", v, v))


def sd_round_box(p, b, r):
    q = np.abs(p) - (b - r)
    return length(np.maximum(q, 0)) + np.minimum(q.max(1), 0) - r


def sd_capsule(p, a, b, ra, rb):
    pa = p - a
    ba = b - a
    h = np.clip(pa @ ba / float(ba @ ba), 0, 1)
    return length(pa - h[:, None] * ba) - (ra * (1 - h) + rb * h)


def sd_sphere(p, c, r):
    return length(p - c) - r


def sd_ellipsoid(p, c, r):
    q = (p - c) / r
    k0 = length(q)
    k1 = length((p - c) / (r * r))
    return k0 * (k0 - 1.0) / np.maximum(k1, 1e-6)


def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)


def rrect2d(xy, b, r):
    q = np.abs(xy) - (b - r)
    return np.sqrt((np.maximum(q, 0) ** 2).sum(1)) + np.minimum(q.max(1), 0) - r


def capsule2d(xy, a, b, ra, rb):
    pa = xy - a
    ba = b - a
    h = np.clip(pa @ ba / float(ba @ ba), 0, 1)
    d = pa - h[:, None] * ba
    return np.sqrt((d ** 2).sum(1)) - (ra * (1 - h) + rb * h)


def rot(yaw=0.0, pitch=0.0, roll=0.0):
    cy, sy = math.cos(yaw), math.sin(yaw)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cr, sr = math.cos(roll), math.sin(roll)
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]], F)
    Rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]], F)
    Rz = np.array([[cr, -sr, 0], [sr, cr, 0], [0, 0, 1]], F)
    return (Ry @ Rx @ Rz).astype(F)


# --------------------------------------------------------------- the pose
class Pose:
    def __init__(self, jaw=0.05, wrist=(0.0, 0.0, 0.0), focus=(0.0, 6.0, 70.0), lids=0.0,
                 hands=((-30.0, -16.0, 5.0), (30.0, -16.0, 5.0)), rods=False, lid_tilt=0.0,
                 hand_open=(0.6, 0.6), body=None, rod_end=None, free_eyes=False):
        self.jaw = jaw
        self.R = rot(*wrist)            # head rotation about the wrist pivot
        self.Rinv = self.R.T.copy()
        self.focus = np.array(focus, F)  # in world coords
        self.lids = lids
        self.lid_tilt = lid_tilt
        self.hands = np.array(hands, F)
        self.rods = rods
        self.hand_open = hand_open
        self.rod_end = None if rod_end is None else np.array(rod_end, F)
        if body is not None:
            COL[0] = body
        ca, sa = math.cos(jaw), math.sin(jaw)
        self.jaw_c, self.jaw_s = ca, sa
        # gaze directions (head coords): focus point brought into head space
        # glued pupils: the build focus is fixed in head space; to look at something, turn the head
        f_head = FOCUS_HEAD if not free_eyes else (self.focus - WRIST_PIVOT) @ self.R + WRIST_PIVOT
        self.gaze = []
        for e in EYES:
            g = f_head - e
            self.gaze.append(g / np.linalg.norm(g))
        self.hand_geo = [self._hand_geo(i) for i in range(2)]

    def _hand_geo(self, i):
        S = SHOULDERS[i]
        Wr = self.hands[i]
        a = Wr - S
        a = a / np.linalg.norm(a)
        side = -1 if i == 0 else 1
        s = np.cross(a, np.array([0, 0, 1], F))
        s = s / (np.linalg.norm(s) + 1e-6)
        if s[1] < 0:
            s = -s           # s points "up-ish" across the hand
        op = self.hand_open[i]
        caps = []
        palm = Wr + a * 1.2
        for k, off in enumerate((-1.0, 0.0, 1.0)):
            base = palm + a * 2.0 + s * off * (1.25 + 0.5 * op) * -1
            d = a + s * off * -0.35 * op
            d = d / np.linalg.norm(d)
            caps.append((base, base + d * 3.4, 1.12, 1.0))
        tb = palm + s * 2.2
        td = a * 0.35 + s * 0.95
        td = td / np.linalg.norm(td)
        caps.append((tb, tb + td * 3.0, 1.1, 0.95))
        bound_c = palm + a * 2.5
        return dict(palm=palm, a=a, caps=caps, bc=bound_c, br=8.5)

    # ----------------------------------------------------------- scene
    def to_head(self, p):
        return (p - WRIST_PIVOT) @ self.R + WRIST_PIVOT

    def sdf(self, p, mat=False):
        """p: (N,3) world points. Returns distance (and material ids)."""
        h = self.to_head(p)
        # head halves
        gx = np.sqrt(1 + (2 * SMILE_K * h[:, 0]) ** 2)
        hz = HINGE[2]
        # the mouth is only cut in front of the hinge; behind it the head is whole
        cu = ((MOUTH_Y + SMILE_K * h[:, 0] ** 2) - h[:, 1]) / gx
        upper = np.maximum(sd_round_box(h, HEAD_B, HEAD_R), np.minimum(cu, h[:, 2] - hz))
        q = h - HINGE
        qy = q[:, 1] * self.jaw_c + q[:, 2] * self.jaw_s
        qz = -q[:, 1] * self.jaw_s + q[:, 2] * self.jaw_c
        qj = np.stack([h[:, 0], qy + HINGE[1], qz + HINGE[2]], 1)
        cl = (qj[:, 1] - (MOUTH_Y + SMILE_K * qj[:, 0] ** 2)) / gx
        lower = np.maximum(sd_round_box(qj, HEAD_B, HEAD_R), np.maximum(cl, hz - qj[:, 2]))
        tongue = sd_ellipsoid(qj, np.array([0.8, MOUTH_Y - 0.4, 3.0], F), np.array([8.0, 1.6, 6.0], F))
        head = np.minimum(upper, lower)
        # the sleeve (world coords: the forearm stays put)
        tail = np.maximum(sd_capsule(p, TAIL_A, TAIL_B, TAIL_RA, TAIL_RB), p[:, 1] + 12.0)  # forearm stays below the mouth
        body = smin(head, tail, 3.5)
        # piping: a cord in the seam plane of the head (z=0, head coords), and down each side of the
        # cream part of the tail (in the tail's own plane, world coords), ending where the black sleeve starts
        d2h = rrect2d(h[:, :2], HEAD_B[:2], HEAD_R)
        pipe_head = np.sqrt(d2h ** 2 + h[:, 2] ** 2) - PIPE_R
        d2t = capsule2d(p[:, :2], TAIL_A[:2], TAIL_B[:2], TAIL_RA, TAIL_RB)
        pipe_tail = np.sqrt(d2t ** 2 + (p[:, 2] - TAIL_A[2]) ** 2) - PIPE_R
        pipe_tail = np.maximum(pipe_tail, np.maximum(SLEEVE_Y - p[:, 1], p[:, 1] + 13.5))
        pipe = np.minimum(pipe_head, pipe_tail)
        # mouth gap: no piping across the open mouth (the cord stays on each jaw)
        # eyes
        e0 = sd_sphere(h, EYES[0], EYE_R)
        e1 = sd_sphere(h, EYES[1], EYE_R)
        eyes = np.minimum(e0, e1)
        # lids
        if self.lids > 0.01:
            lid_d = np.full(len(p), 1e3, F)
            for e in EYES:
                cut = EYE_R * (1 - 2 * self.lids)
                rel = h - e
                yy = rel[:, 1] * math.cos(self.lid_tilt) + rel[:, 0] * math.sin(self.lid_tilt) * (1 if e[0] > 0 else -1)
                lid_d = np.minimum(lid_d, np.maximum(sd_sphere(h, e, EYE_R + 0.35), cut - yy))
        else:
            lid_d = None
        # curl (bounded)
        dc = length(h - CURL_CENTER) - CURL_BOUND
        curl = dc.copy()
        near = dc < 1.5
        if near.any():
            hn = h[near]
            cd = np.full(len(hn), 1e3, F)
            for i in range(len(CURL_P) - 1):
                cd = np.minimum(cd, sd_capsule(hn, CURL_P[i], CURL_P[i + 1], CURL_R[i], CURL_R[i + 1]))
            curl[near] = cd
        # arms + hands (head coords: they ride on the head)
        arm_d = np.full(len(p), 1e3, F)
        hand_d = np.full(len(p), 1e3, F)
        for i in range(2):
            S, Wr = SHOULDERS[i], self.hands[i]
            mid = (S + Wr) / 2 + np.array([0, -2.0, 1.0], F)
            arm_d = np.minimum(arm_d, np.minimum(sd_capsule(h, S, mid, 2.7, 2.45), sd_capsule(h, mid, Wr, 2.45, 2.2)))
            g = self.hand_geo[i]
            db = length(h - g["bc"]) - g["br"]
            hd = db.copy()
            nr = db < 1.5
            if nr.any():
                hn = h[nr]
                d = sd_ellipsoid(hn, g["palm"], np.array([3.2, 3.2, 2.2], F))
                for (a0, a1, r0, r1) in g["caps"]:
                    d = smin(d, sd_capsule(hn, a0, a1, r0, r1), 0.8)
                hd[nr] = d
            hand_d = np.minimum(hand_d, hd)
        body = smin(body, arm_d, 1.6)
        rods = np.full(len(p), 1e3, F)
        if self.rods:
            for i in range(2):
                w_world = (self.hands[i] - WRIST_PIVOT) @ self.Rinv + WRIST_PIVOT
                end = self.rod_end if self.rod_end is not None else w_world + np.array([4.0 * (1 if i else -1), -60, 6], F)
                rods = np.minimum(rods, sd_capsule(p, w_world, end, 0.32, 0.32))
        parts = [body, pipe, eyes, curl, hand_d, tongue, rods]
        if lid_d is not None:
            parts.append(lid_d)
        d = parts[0]
        for x in parts[1:]:
            d = np.minimum(d, x)
        if not mat:
            return d
        # material ids
        stack = np.stack(parts, 1)
        idx = stack.argmin(1)
        ids = np.zeros(len(p), np.int8)
        sleeve = (idx == 0) & (tail <= head + 0.05) & (p[:, 1] < SLEEVE_Y)
        ids[idx == 1] = 1
        ids[idx == 3] = 4
        ids[idx == 4] = 5
        ids[idx == 5] = 7
        ids[idx == 6] = 8
        if lid_d is not None:
            li = np.where(idx == 7)[0]
            ids[li] = 9
            if len(li):
                hl = h[li]
                cut = EYE_R * (1 - 2 * self.lids)
                best = np.full(len(li), 1e3, F)
                edge = np.zeros(len(li), bool)
                for e in EYES:
                    rel = hl - e
                    dist_e = length(rel)
                    yy = rel[:, 1] * math.cos(self.lid_tilt) + rel[:, 0] * math.sin(self.lid_tilt) * (1 if e[0] > 0 else -1)
                    closer = dist_e < best
                    best = np.where(closer, dist_e, best)
                    edge = np.where(closer, np.abs(yy - cut) < 0.55, edge)
                ids[li[edge]] = 1
        # eyes: white or pupil, by angle to the gaze
        ei = np.where(idx == 2)[0]
        if len(ei):
            he = h[ei]
            use0 = e0[ei] < e1[ei]
            for k, e in enumerate(EYES):
                sel = ei[(use0 if k == 0 else ~use0)]
                if len(sel) == 0:
                    continue
                v = h[sel] - e
                v = v / np.linalg.norm(v, axis=1, keepdims=True)
                cosang = v @ self.gaze[k]
                ids[sel] = np.where(cosang > math.cos(0.50), 3, 2)
        # mouth interior: body hits where a mouth cut (not the cushion) is the active surface
        bi = np.where(idx == 0)[0]
        if len(bi):
            hb = h[bi]
            gxb = np.sqrt(1 + (2 * SMILE_K * hb[:, 0]) ** 2)
            cu_b = ((MOUTH_Y + SMILE_K * hb[:, 0] ** 2) - hb[:, 1]) / gxb
            act_u = np.minimum(cu_b, hb[:, 2] - HINGE[2])
            rb_u = sd_round_box(hb, HEAD_B, HEAD_R)
            on_u = (act_u >= rb_u - 0.04) & (upper[bi] <= lower[bi] + 0.02) & (upper[bi] < tail[bi])
            qb = qj[bi]
            cl_b = (qb[:, 1] - (MOUTH_Y + SMILE_K * qb[:, 0] ** 2)) / gxb
            act_l = np.maximum(cl_b, HINGE[2] - qb[:, 2])
            rb_l = sd_round_box(qb, HEAD_B, HEAD_R)
            on_l = (act_l >= rb_l - 0.04) & (lower[bi] <= upper[bi] + 0.02) & (lower[bi] < tail[bi])
            ids[bi[on_u | on_l]] = 6
        ids[sleeve] = 10
        return d, ids


# --------------------------------------------------------------- rendering
def value_noise3(p, scale):
    x = p / scale
    i = np.floor(x).astype(np.int64)
    f = x - i
    f = f * f * (3 - 2 * f)

    def hsh(ix, iy, iz):
        n = (ix * 73856093) ^ (iy * 19349663) ^ (iz * 83492791)
        n = (n ^ (n >> 13)) * 1274126177
        return ((n & 0xFFFF) / 65535.0).astype(F)
    out = 0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (f[:, 0] if dx else 1 - f[:, 0]) * (f[:, 1] if dy else 1 - f[:, 1]) * (f[:, 2] if dz else 1 - f[:, 2])
                out = out + w * hsh(i[:, 0] + dx, i[:, 1] + dy, i[:, 2] + dz)
    return out


def render(pose, width=720, height=800, ppcm=9.0, center=(0.0, -6.0), view_yaw=0.0, view_pitch=0.0,
           persp=None, steps=110, shadows=True, light=(-0.55, 0.65, 0.55), follow=False,
           key_col=(1, 1, 1), fill_col=(1, 1, 1), amb_col=(1, 1, 1), rim_col=(1.0, 0.97, 0.9),
           fill_dir=(0.7, 0.15, 0.45), rim_dir=(0.15, 0.55, -0.85), amb=0.32):
    """Returns float RGBA image (H, W, 4). Orthographic unless persp=(cam_pos, look_at, fov_deg)."""
    H, W = height, width
    js, is_ = np.meshgrid(np.arange(W, dtype=F), np.arange(H, dtype=F))
    u = (js - W / 2 + 0.5) / ppcm + center[0]
    v = -(is_ - H / 2 + 0.5) / ppcm + center[1]
    V = rot(view_yaw, view_pitch, 0.0)
    if persp is None:
        o = np.stack([u, v, np.full_like(u, 120.0)], -1).reshape(-1, 3) @ V.T
        d = np.tile(np.array([0, 0, -1], F) @ V.T, (H * W, 1))
    else:
        cam, look, fov = persp
        cam = np.array(cam, F); look = np.array(look, F)
        fw = look - cam; fw /= np.linalg.norm(fw)
        rt = np.cross(fw, np.array([0, 1, 0], F)); rt /= np.linalg.norm(rt)
        up = np.cross(rt, fw)
        k = math.tan(math.radians(fov) / 2)
        sx = (js - W / 2 + 0.5) / (H / 2) * k
        sy = -(is_ - H / 2 + 0.5) / (H / 2) * k
        d = (fw[None, None] + sx[..., None] * rt + sy[..., None] * up).reshape(-1, 3)
        d /= np.linalg.norm(d, axis=1, keepdims=True)
        o = np.tile(cam, (H * W, 1))
    d = d.astype(F); o = o.astype(F)
    N = H * W
    t = np.zeros(N, F)
    hit = np.zeros(N, bool)
    alive = np.ones(N, bool)
    tmax = 260.0 if persp is None else 600.0
    for _ in range(steps):
        ai = np.where(alive)[0]
        if len(ai) == 0:
            break
        p = o[ai] + d[ai] * t[ai, None]
        dist = pose.sdf(p)
        h_ = dist < 0.02
        hit[ai[h_]] = True
        t[ai] += np.maximum(dist * 0.82, 0.01)
        dead = h_ | (t[ai] > tmax)
        alive[ai[dead]] = False
    img = np.zeros((N, 4), F)
    hi = np.where(hit)[0]
    if len(hi) == 0:
        return img.reshape(H, W, 4)
    for _ in range(4):
        P = o[hi] + d[hi] * t[hi, None]
        t[hi] += pose.sdf(P) * 0.9
    P = o[hi] + d[hi] * t[hi, None]
    _, ids = pose.sdf(P, mat=True)
    # normals (tetrahedral)
    e = 0.06
    ks = np.array([[1, -1, -1], [-1, -1, 1], [-1, 1, -1], [1, 1, 1]], F)
    n = np.zeros_like(P)
    for k in ks:
        n += k[None] * pose.sdf(P + k[None] * e)[:, None]
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
    # fleece: perturb normals with fine noise; albedo noise
    fleecy = np.isin(ids, [0, 1, 4, 5, 9, 10])
    nz = np.stack([value_noise3(P * 1.0, 0.22), value_noise3(P + 17.0, 0.22), value_noise3(P - 9.0, 0.22)], 1) - 0.5
    n = n + nz * np.where(fleecy, 0.32, 0.0)[:, None]
    n /= np.linalg.norm(n, axis=1, keepdims=True)
    base = np.array([COL[int(i)] for i in range(len(COL))], F)[ids]
    grain = value_noise3(P, 0.35) * 0.6 + value_noise3(P, 0.09) * 0.4
    base = base * (1 + (grain[:, None] - 0.5) * np.where(fleecy, 0.16, 0.03)[:, None])
    # lights
    L = np.array(light, F); L /= np.linalg.norm(L)
    Fill = np.array(fill_dir, F); Fill /= np.linalg.norm(Fill)
    Rim = np.array(rim_dir, F); Rim /= np.linalg.norm(Rim)
    kc, fc, ac, rc = (np.array(c, F) for c in (key_col, fill_col, amb_col, rim_col))
    if follow:  # studio lighting that turns with the camera (for model sheets)
        L, Fill, Rim = (V @ L).astype(F), (V @ Fill).astype(F), (V @ Rim).astype(F)
    view = -d[hi]
    ndl = n @ L
    wrap = 0.45
    diff = np.clip((ndl + wrap) / (1 + wrap), 0, 1)
    # soft shadow from the key
    sh = np.ones(len(hi), F)
    if shadows:
        rng = np.random.default_rng(1)
        ts = (0.4 + rng.random(len(hi)) * 0.7).astype(F)
        jit = (0.75 + rng.random(len(hi)) * 0.5).astype(F)
        live = np.ones(len(hi), bool)
        for _ in range(72):
            li = np.where(live)[0]
            if len(li) == 0:
                break
            dd = pose.sdf(P[li] + n[li] * 0.08 + L[None] * ts[li, None])
            sh[li] = np.minimum(sh[li], np.clip(8.0 * dd / ts[li], 0, 1))
            ts[li] += np.clip(dd, 0.06, 1.2) * jit[li]
            live[li[(dd < 0.01) | (ts[li] > 60)]] = False
        sh = np.clip(sh, 0, 1)
        sh = sh * sh * (3 - 2 * sh)
    # ambient occlusion
    ao = np.ones(len(hi), F)
    for k, hh in enumerate((0.4, 1.0, 2.0, 3.5, 5.5)):
        dd = pose.sdf(P + n * hh)
        ao -= (hh - dd) * (0.55 / (k + 1)) / hh * 0.45
    ao = np.clip(ao, 0.25, 1)
    fill = np.clip(n @ Fill, 0, 1) * 0.28
    sheen = np.clip(1 - np.abs(np.einsum("ij,ij->i", n, view)), 0, 1) ** 2.2
    rim = np.clip(n @ Rim, 0, 1) * 0.35
    lightv = ((diff * sh * 0.95)[:, None] * kc + fill[:, None] * fc + amb * ac) * ao[:, None]
    col = base * lightv
    col += (sheen * np.where(fleecy, 0.28, 0.05) * ao)[:, None] * np.clip(base + 0.25, 0, 1) * (0.5 * kc + 0.5 * fc)
    col += rim[:, None] * rc * 0.5
    # eyes: glossy highlight
    gl = np.isin(ids, [2, 3])
    if gl.any():
        Hh = L + view[gl]
        Hh /= np.linalg.norm(Hh, axis=1, keepdims=True)
        spec = np.clip(np.einsum("ij,ij->i", n[gl], Hh), 0, 1) ** 60
        col[gl] += spec[:, None] * 0.9
    col = np.clip(col, 0, 1)
    img[hi, :3] = col
    img[hi, 3] = 1.0
    return img.reshape(H, W, 4)


def to_surface(img):
    """float RGBA (premultiplied by alpha already since bg=0) -> cairo ImageSurface ARGB32."""
    import cairo
    H, W, _ = img.shape
    a = img[..., 3:4]
    rgb = img[..., :3] * a
    arr = np.zeros((H, W, 4), np.uint8)
    arr[..., 0] = (rgb[..., 2] * 255).astype(np.uint8)
    arr[..., 1] = (rgb[..., 1] * 255).astype(np.uint8)
    arr[..., 2] = (rgb[..., 0] * 255).astype(np.uint8)
    arr[..., 3] = (a[..., 0] * 255).astype(np.uint8)
    surf = cairo.ImageSurface.create_for_data(memoryview(arr), cairo.FORMAT_ARGB32, W, H, W * 4)
    return surf, arr


def fuzz_edges(ctx, img, ox, oy, scale=1.0, seed=0, every=2, length=(1.2, 3.8)):
    """Draw fibers across the silhouette of a rendered image placed at (ox, oy)."""
    import cairo, random
    rnd = random.Random(seed)
    a = img[..., 3]
    H, W = a.shape
    edge = np.zeros_like(a, bool)
    edge[1:-1, 1:-1] = (a[1:-1, 1:-1] > 0.5) & (
        (a[:-2, 1:-1] < 0.5) | (a[2:, 1:-1] < 0.5) | (a[1:-1, :-2] < 0.5) | (a[1:-1, 2:] < 0.5))
    ys, xs = np.where(edge)
    gy, gx = np.gradient(a.astype(np.float32))
    ctx.save()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(0, len(xs), every):
        y, x = ys[k], xs[k]
        nx, ny = -gx[y, x], -gy[y, x]
        L = math.hypot(nx, ny)
        if L < 1e-6:
            continue
        nx, ny = nx / L, ny / L
        ang = math.atan2(ny, nx) + rnd.gauss(0, 0.5)
        ln = rnd.uniform(*length) * scale
        c = img[y, x, :3]
        ctx.set_source_rgba(float(c[0]), float(c[1]), float(c[2]), 0.75)
        ctx.set_line_width(rnd.uniform(0.6, 1.3) * scale)
        sx, sy = ox + x * scale, oy + y * scale
        ctx.move_to(sx - math.cos(ang) * ln * 0.3, sy - math.sin(ang) * ln * 0.3)
        ctx.line_to(sx + math.cos(ang) * ln, sy + math.sin(ang) * ln)
        ctx.stroke()
    ctx.restore()


if __name__ == "__main__":
    import time, sys
    from PIL import Image
    t0 = time.time()
    pose = Pose()
    im = render(pose, width=600, height=660, ppcm=7.5)
    print("render", round(time.time() - t0, 1), "s")
    bg = np.array([0.957, 0.937, 0.890], F)
    out = im[..., :3] * im[..., 3:4] + bg * (1 - im[..., 3:4])
    Image.fromarray((out * 255).astype(np.uint8)).save(sys.argv[1] if len(sys.argv) > 1 else "/tmp/ws_maq.png")
