"""수학 문항용 그림 도구: 좌표평면(Plane)과 평면·입체 도형(Geo).

좌표는 모두 수학 좌표(오른쪽 x, 위쪽 y)로 주고, 화면 크기에 맞춰 자동으로 늘린다.
"""
import math

from reportlab.graphics.shapes import (Circle, Drawing, Line, Polygon, PolyLine,
                                       String)
from reportlab.lib import colors

import exam_pdf  # noqa: F401  (글꼴 등록)

BLACK = colors.black
GREY = colors.HexColor("#555555")
SHADE = colors.HexColor("#D9D9D9")
LIGHT = colors.HexColor("#EFEFEF")


def _txt(d, x, y, s, size=9, font="MR", anchor="middle", color=BLACK):
    d.add(String(x, y, s, fontName=font, fontSize=size, textAnchor=anchor,
                 fillColor=color))


def _arrow(d, x1, y1, x2, y2, w=0.8, head=4.5):
    d.add(Line(x1, y1, x2, y2, strokeWidth=w, strokeColor=BLACK))
    a = math.atan2(y2 - y1, x2 - x1)
    p = [x2, y2]
    for s in (1, -1):
        p += [x2 - head * math.cos(a + s * 0.38), y2 - head * math.sin(a + s * 0.38)]
    d.add(Polygon(p, fillColor=BLACK, strokeColor=BLACK, strokeWidth=0.3))


# ---------------------------------------------------------------- 도형
class Geo:
    """pts: {이름: (x, y)}. width로 가로 크기를 정하면 비율대로 늘린다."""

    def __init__(self, pts, width=170, pad=14, extra=(), unit=None):
        self.pts = dict(pts)
        xs = [p[0] for p in self.pts.values()] + [e[0] for e in extra]
        ys = [p[1] for p in self.pts.values()] + [e[1] for e in extra]
        self.x0, self.y0 = min(xs), min(ys)
        span = max(max(xs) - self.x0, 1e-9)
        self.u = unit or (width - 2 * pad) / span
        self.pad = pad
        self.W = span * self.u + 2 * pad
        self.H = (max(ys) - self.y0) * self.u + 2 * pad
        self.d = Drawing(self.W, self.H)

    def S(self, p):
        if isinstance(p, str):
            p = self.pts[p]
        return (self.pad + (p[0] - self.x0) * self.u,
                self.pad + (p[1] - self.y0) * self.u)

    def seg(self, a, b, dash=False, w=0.9, color=BLACK):
        (x1, y1), (x2, y2) = self.S(a), self.S(b)
        self.d.add(Line(x1, y1, x2, y2, strokeWidth=w, strokeColor=color,
                        strokeDashArray=[3, 2] if dash else None))

    def path(self, names, dash=False, w=0.9, close=False):
        for i in range(len(names) - 1):
            self.seg(names[i], names[i + 1], dash=dash, w=w)
        if close:
            self.seg(names[-1], names[0], dash=dash, w=w)

    def fill(self, names, color=SHADE):
        flat = []
        for n in names:
            flat += list(self.S(n))
        self.d.add(Polygon(flat, fillColor=color, strokeColor=None, strokeWidth=0))

    def dot(self, a, r=1.5):
        x, y = self.S(a)
        self.d.add(Circle(x, y, r, fillColor=BLACK, strokeColor=BLACK))

    def lab(self, a, text=None, dx=0, dy=0, size=9, font="MR"):
        x, y = self.S(a)
        _txt(self.d, x + dx, y + dy - size * 0.35, text if text is not None else a,
             size=size, font=font)

    def text(self, x, y, s, size=9, font="MR", anchor="middle"):
        _txt(self.d, x, y, s, size=size, font=font, anchor=anchor)

    def _dirs(self, v, a, b):
        vx, vy = self.S(v)
        ax, ay = self.S(a)
        bx, by = self.S(b)
        t1 = math.degrees(math.atan2(ay - vy, ax - vx))
        t2 = math.degrees(math.atan2(by - vy, bx - vx))
        sweep = (t2 - t1) % 360
        if sweep > 180:
            t1, t2 = t2, t1
            sweep = 360 - sweep
        return vx, vy, t1, sweep

    def arc(self, v, a, b, r=9, label=None, lr=None, size=8, font="MR",
            shade=False, double=False):
        vx, vy, t1, sweep = self._dirs(v, a, b)
        n = max(6, int(sweep / 4))
        pts = []
        for i in range(n + 1):
            t = math.radians(t1 + sweep * i / n)
            pts += [vx + r * math.cos(t), vy + r * math.sin(t)]
        if shade:
            self.d.add(Polygon([vx, vy] + pts, fillColor=SHADE, strokeColor=None,
                               strokeWidth=0))
        self.d.add(PolyLine(pts, strokeWidth=0.6, strokeColor=BLACK))
        if double:
            pts2 = []
            for i in range(n + 1):
                t = math.radians(t1 + sweep * i / n)
                pts2 += [vx + (r + 2.2) * math.cos(t), vy + (r + 2.2) * math.sin(t)]
            self.d.add(PolyLine(pts2, strokeWidth=0.6, strokeColor=BLACK))
        if label:
            mid = math.radians(t1 + sweep / 2)
            lr = lr or r + 7
            _txt(self.d, vx + lr * math.cos(mid), vy + lr * math.sin(mid) - size * 0.35,
                 label, size=size, font=font)

    def mark(self, v, a, b, sym="•", r=8, size=7, font="KR"):
        """각 안쪽에 기호(•, ×, ∘ 등)를 찍어 같은 각을 표시한다."""
        vx, vy, t1, sweep = self._dirs(v, a, b)
        mid = math.radians(t1 + sweep / 2)
        _txt(self.d, vx + r * math.cos(mid), vy + r * math.sin(mid) - size * 0.35, sym,
             size=size, font=font)

    def right(self, v, a, b, s=5):
        vx, vy = self.S(v)
        ax, ay = self.S(a)
        bx, by = self.S(b)
        ua = (ax - vx, ay - vy)
        ub = (bx - vx, by - vy)
        la, lb = math.hypot(*ua), math.hypot(*ub)
        ua = (ua[0] / la * s, ua[1] / la * s)
        ub = (ub[0] / lb * s, ub[1] / lb * s)
        self.d.add(PolyLine([vx + ua[0], vy + ua[1], vx + ua[0] + ub[0], vy + ua[1] + ub[1],
                             vx + ub[0], vy + ub[1]], strokeWidth=0.6, strokeColor=BLACK))

    def ticks(self, a, b, n=1, size=3.2):
        (x1, y1), (x2, y2) = self.S(a), self.S(b)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        L = math.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        nx, ny = -uy, ux
        for i in range(n):
            off = (i - (n - 1) / 2) * 2.4
            cx, cy = mx + ux * off, my + uy * off
            self.d.add(Line(cx - nx * size, cy - ny * size, cx + nx * size, cy + ny * size,
                            strokeWidth=0.7, strokeColor=BLACK))

    def brace_len(self, a, b, text, off=8, size=8):
        """두 점 사이에 점선 호를 그리고 길이를 적는다(수직선 위 길이 표시)."""
        (x1, y1), (x2, y2) = self.S(a), self.S(b)
        n = 20
        pts = []
        for i in range(n + 1):
            t = i / n
            pts += [x1 + (x2 - x1) * t, y1 + (y2 - y1) * t + off * math.sin(math.pi * t)]
        self.d.add(PolyLine(pts, strokeWidth=0.6, strokeColor=BLACK, strokeDashArray=[1.5, 1.5]))
        _txt(self.d, (x1 + x2) / 2, (y1 + y2) / 2 + off + 2, text, size=size, font="MR")


# ---------------------------------------------------------------- 좌표평면
class Plane:
    def __init__(self, xmin, xmax, ymin, ymax, unit=10, pad=12):
        self.xmin, self.xmax, self.ymin, self.ymax = xmin, xmax, ymin, ymax
        self.u = unit
        self.pad = pad
        self.W = (xmax - xmin) * unit + 2 * pad
        self.H = (ymax - ymin) * unit + 2 * pad
        self.d = Drawing(self.W, self.H)

    def S(self, x, y):
        return (self.pad + (x - self.xmin) * self.u, self.pad + (y - self.ymin) * self.u)

    def grid(self, step=1, color=LIGHT):
        x = math.ceil(self.xmin / step) * step
        while x <= self.xmax + 1e-9:
            (sx, sy0), (_, sy1) = self.S(x, self.ymin), self.S(x, self.ymax)
            self.d.add(Line(sx, sy0, sx, sy1, strokeWidth=0.4, strokeColor=color))
            x += step
        y = math.ceil(self.ymin / step) * step
        while y <= self.ymax + 1e-9:
            (sx0, sy), (sx1, _) = self.S(self.xmin, y), self.S(self.xmax, y)
            self.d.add(Line(sx0, sy, sx1, sy, strokeWidth=0.4, strokeColor=color))
            y += step

    def axes(self, xl="x", yl="y", origin=True, ox=0, oy=0):
        x0, y0 = self.S(self.xmin, oy)
        x1, _ = self.S(self.xmax, oy)
        _arrow(self.d, x0, y0, x1 + 4, y0)
        sx, sy0 = self.S(ox, self.ymin)
        _, sy1 = self.S(ox, self.ymax)
        _arrow(self.d, sx, sy0, sx, sy1 + 4)
        _txt(self.d, x1 + 3, y0 - 11, xl, size=9, font="MI" if len(xl) == 1 else "KR",
             anchor="end" if len(xl) > 1 else "middle")
        _txt(self.d, sx + 5, sy1 + 1, yl, size=9, font="MI" if len(yl) == 1 else "KR",
             anchor="start")
        if origin:
            ox_, oy_ = self.S(ox, oy)
            _txt(self.d, ox_ - 6, oy_ - 10, "O", size=8.5, font="MI")

    def xtick(self, v, text=None, dy=-10, size=8, mark=True):
        x, y = self.S(v, 0)
        if mark:
            self.d.add(Line(x, y - 1.8, x, y + 1.8, strokeWidth=0.6, strokeColor=BLACK))
        _txt(self.d, x, y + dy, text if text is not None else str(v), size=size)

    def ytick(self, v, text=None, dx=-7, size=8, mark=True):
        x, y = self.S(0, v)
        if mark:
            self.d.add(Line(x - 1.8, y, x + 1.8, y, strokeWidth=0.6, strokeColor=BLACK))
        _txt(self.d, x + dx, y - 3, text if text is not None else str(v), size=size,
             anchor="end" if dx < 0 else "start")

    def curve(self, f, x0, x1, n=120, w=1.1, dash=False):
        seg = []
        for i in range(n + 1):
            x = x0 + (x1 - x0) * i / n
            y = f(x)
            if self.ymin - 1e-9 <= y <= self.ymax + 1e-9:
                seg += list(self.S(x, y))
            elif seg:
                if len(seg) >= 4:
                    self.d.add(PolyLine(seg, strokeWidth=w, strokeColor=BLACK,
                                        strokeDashArray=[3, 2] if dash else None))
                seg = []
        if len(seg) >= 4:
            self.d.add(PolyLine(seg, strokeWidth=w, strokeColor=BLACK,
                                strokeDashArray=[3, 2] if dash else None))

    def seg(self, p, q, dash=False, w=0.9):
        (x1, y1), (x2, y2) = self.S(*p), self.S(*q)
        self.d.add(Line(x1, y1, x2, y2, strokeWidth=w, strokeColor=BLACK,
                        strokeDashArray=[2.5, 2] if dash else None))

    def poly(self, pts, fill=SHADE, stroke=True):
        flat = []
        for p in pts:
            flat += list(self.S(*p))
        self.d.add(Polygon(flat, fillColor=fill, strokeColor=BLACK if stroke else None,
                           strokeWidth=0.8 if stroke else 0))

    def point(self, x, y, label=None, dx=6, dy=4, size=9, font="MR", r=1.6):
        sx, sy = self.S(x, y)
        self.d.add(Circle(sx, sy, r, fillColor=BLACK, strokeColor=BLACK))
        if label:
            _txt(self.d, sx + dx, sy + dy - size * 0.35, label, size=size, font=font)

    def guide(self, x, y):
        self.seg((x, 0), (x, y), dash=True, w=0.6)
        self.seg((0, y), (x, y), dash=True, w=0.6)

    def label(self, x, y, text, size=8.5, font="MR", dx=0, dy=0, anchor="middle"):
        sx, sy = self.S(x, y)
        _txt(self.d, sx + dx, sy + dy - size * 0.35, text, size=size, font=font, anchor=anchor)

    def right(self, x, y, sx=1, sy=1, s=4):
        """(x, y)에 직각 표시. sx, sy는 표시가 놓일 방향(+1/-1)."""
        px, py = self.S(x, y)
        self.d.add(PolyLine([px + sx * s, py, px + sx * s, py + sy * s, px, py + sy * s],
                            strokeWidth=0.6, strokeColor=BLACK))


def mini_graph(segs, label, w=72, h=54):
    """작은 시간-높이 그래프. segs: [(시간 길이, 높이 증가량), ...]"""
    d = Drawing(w, h)
    ox, oy = 16, 9
    pw, ph = w - 22, h - 20
    _arrow(d, ox, oy, ox + pw + 3, oy, w=0.6, head=3)
    _arrow(d, ox, oy, ox, oy + ph + 3, w=0.6, head=3)
    _txt(d, ox - 4, oy - 7, "O", size=6.5, font="MI")
    _txt(d, ox + pw + 3, oy - 7, "시간", size=5.5, font="KR", anchor="end")
    _txt(d, ox + 2, oy + ph + 4, "높이", size=5.5, font="KR", anchor="start")
    _txt(d, 1, h - 10, label, size=9, font="KR", anchor="start")
    T = sum(s[0] for s in segs)
    Hh = sum(s[1] for s in segs)
    pts = [ox, oy]
    t = hh = 0
    for dt, dh in segs:
        t += dt
        hh += dh
        pts += [ox + pw * 0.95 * t / T, oy + ph * 0.9 * hh / Hh]
    d.add(PolyLine(pts, strokeWidth=1, strokeColor=BLACK))
    return d


# ---------------------------------------------------------------- 그림 속 수식 라벨
from reportlab.pdfbase import pdfmetrics as _pm


def _piece_w(p, size):
    kind = p[0]
    if kind == "f":
        fs = size * 0.78
        return max(_pm.stringWidth(p[1], p[3] if len(p) > 3 else "MR", fs),
                   _pm.stringWidth(p[2], p[4] if len(p) > 4 else "MR", fs)) + 2
    font = {"r": "MR", "i": "MI", "k": "KR"}[kind]
    return _pm.stringWidth(p[1], font, size)


def eq(d, x, y, parts, size=8.5, anchor="middle"):
    """parts: [("r", "y = "), ("i", "x"), ("f", "2", "3"), ("k", "형")] 형태의 수식 라벨.
    ("f", 분자, 분모, 분자글꼴, 분모글꼴)은 세로 분수. y는 글자 기준선."""
    total = sum(_piece_w(p, size) for p in parts)
    cx = x - total / 2 if anchor == "middle" else (x - total if anchor == "end" else x)
    for p in parts:
        w = _piece_w(p, size)
        if p[0] == "f":
            fs = size * 0.78
            nf = p[3] if len(p) > 3 else "MR"
            df = p[4] if len(p) > 4 else "MR"
            bar_y = y + size * 0.3
            d.add(Line(cx + 0.5, bar_y, cx + w - 0.5, bar_y, strokeWidth=0.5, strokeColor=BLACK))
            _txt(d, cx + w / 2, bar_y + 1.6, p[1], size=fs, font=nf)
            _txt(d, cx + w / 2, bar_y - fs * 0.85, p[2], size=fs, font=df)
        else:
            font = {"r": "MR", "i": "MI", "k": "KR"}[p[0]]
            _txt(d, cx, y, p[1], size=size, font=font, anchor="start")
        cx += w


def _geo_eqlab(self, a, parts, dx=0, dy=0, size=8.5, anchor="middle"):
    x, y = self.S(a)
    eq(self.d, x + dx, y + dy - size * 0.35, parts, size=size, anchor=anchor)


def _plane_eqlab(self, x, y, parts, dx=0, dy=0, size=8.5, anchor="middle"):
    sx, sy = self.S(x, y)
    eq(self.d, sx + dx, sy + dy - size * 0.35, parts, size=size, anchor=anchor)


Geo.eqlab = _geo_eqlab
Plane.eqlab = _plane_eqlab


def _geo_arc_parts(self, v, a, b, r=9, parts=None, lr=None, size=8, shade=False, double=False):
    self.arc(v, a, b, r=r, shade=shade, double=double)
    if parts:
        vx, vy, t1, sweep = self._dirs(v, a, b)
        mid = math.radians(t1 + sweep / 2)
        lr = lr or r + 9
        eq(self.d, vx + lr * math.cos(mid), vy + lr * math.sin(mid) - size * 0.35, parts, size=size)


Geo.arcq = _geo_arc_parts
