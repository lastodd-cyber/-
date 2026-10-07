"""과학 문항용 그림: 입자 모형, 상태 변화 그림, 가열·냉각 곡선, 지구와 중력 등."""
import math
import random

from reportlab.graphics.shapes import (Circle, Drawing, Ellipse, Line, Polygon,
                                       Rect, String, PolyLine)
from reportlab.lib import colors

import exam_pdf  # noqa: F401  (글꼴 등록)

BLACK = colors.black
GREY = colors.HexColor("#555555")
LIGHT = colors.HexColor("#DDDDDD")
WATER = colors.HexColor("#DCEBF5")


def _text(d, x, y, s, size=8.5, anchor="middle", font="KR", color=BLACK):
    d.add(String(x, y, s, fontName=font, fontSize=size, textAnchor=anchor,
                 fillColor=color))


def arrow(d, x1, y1, x2, y2, width=0.9, head=5, color=BLACK):
    d.add(Line(x1, y1, x2, y2, strokeWidth=width, strokeColor=color))
    ang = math.atan2(y2 - y1, x2 - x1)
    a1, a2 = ang + math.radians(155), ang - math.radians(155)
    d.add(Polygon([x2, y2,
                   x2 + head * math.cos(a1), y2 + head * math.sin(a1),
                   x2 + head * math.cos(a2), y2 + head * math.sin(a2)],
                  fillColor=color, strokeColor=color, strokeWidth=0.5))


# ---------------------------------------------------------------- 입자 모형
def _particles(kind, r_box, seed):
    """원 안(반지름 r_box)에 놓일 입자 중심 좌표 목록과 입자 반지름."""
    rnd = random.Random(seed)
    if kind == "solid":
        pr = r_box * 0.085
        step = pr * 2.05
        pts = []
        n = int(r_box / step) + 1
        for i in range(-n, n + 1):
            for j in range(-n, n + 1):
                x, y = i * step, j * step
                if math.hypot(x, y) < r_box - pr * 1.6:
                    pts.append((x, y))
        return pts, pr
    if kind == "liquid":
        pr = r_box * 0.085
        pts = []
        tries = 0
        while len(pts) < 34 and tries < 6000:
            tries += 1
            x = rnd.uniform(-r_box, r_box)
            y = rnd.uniform(-r_box, r_box * 0.35)
            if math.hypot(x, y) > r_box - pr * 1.4:
                continue
            if all(math.hypot(x - a, y - b) > pr * 2.25 for a, b in pts):
                pts.append((x, y))
        return pts, pr
    # gas
    pr = r_box * 0.085
    pts = []
    tries = 0
    while len(pts) < 6 and tries < 6000:
        tries += 1
        x = rnd.uniform(-r_box, r_box)
        y = rnd.uniform(-r_box, r_box)
        if math.hypot(x, y) > r_box - pr * 2:
            continue
        if all(math.hypot(x - a, y - b) > r_box * 0.55 for a, b in pts):
            pts.append((x, y))
    return pts, pr


def particle_models(models, size=58, gap=16, seed=3):
    """models: [(kind, label), ...] kind는 'solid'|'liquid'|'gas'."""
    n = len(models)
    w = n * size + (n - 1) * gap + 4
    h = size + 18
    d = Drawing(w, h)
    for i, (kind, label) in enumerate(models):
        cx = 2 + size / 2 + i * (size + gap)
        cy = 16 + size / 2
        r = size / 2
        d.add(Circle(cx, cy, r, strokeColor=BLACK, strokeWidth=0.8,
                     fillColor=colors.white))
        pts, pr = _particles(kind, r, seed + i)
        for x, y in pts:
            d.add(Circle(cx + x, cy + y, pr, strokeColor=BLACK, strokeWidth=0.5,
                         fillColor=colors.HexColor("#8A8A8A")))
        _text(d, cx, 3, label, 8.5)
    return d


# ---------------------------------------------------------------- 상태 변화 그림
def state_triangle(arrows, w=200, h=118):
    """arrows: {'A': ('고체', '액체'), ...} 고체(왼쪽 아래)·액체(오른쪽 아래)·기체(위)."""
    d = Drawing(w, h)
    pos = {"기체": (w / 2, h - 14), "고체": (26, 14), "액체": (w - 26, 14)}
    for name, (x, y) in pos.items():
        d.add(Rect(x - 21, y - 9, 42, 18, strokeColor=BLACK, strokeWidth=0.8,
                   fillColor=colors.white))
        _text(d, x, y - 3.5, name, 9)
    for label, (a, b) in arrows.items():
        ax, ay = pos[a]
        bx, by = pos[b]
        # 두 상태를 잇는 선을 기준으로 진행 방향 왼쪽으로 띄운 평행 화살표
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        nx, ny = -uy, ux
        off = 7
        start = 27 if abs(dy) < 1 else 22
        sx, sy = ax + ux * start + nx * off, ay + uy * start + ny * off
        ex, ey = bx - ux * start + nx * off, by - uy * start + ny * off
        arrow(d, sx, sy, ex, ey)
        mx, my = (sx + ex) / 2 + nx * 8, (sy + ey) / 2 + ny * 8 - 3
        _text(d, mx, my, label, 8.5)
    return d


# ---------------------------------------------------------------- 그래프
def curve_graph(series, xmax, ymin, ymax, w=210, h=130, yticks=(), xticks=(),
                seg_labels=(), xlabel="시간(분)", ylabel="온도(℃)",
                guides=(), legend=(), origin=True, legend_at=None):
    """series: [dict(pts=[(x, y), ...], dash=False)]. guides: [(x, y)] 점선 보조선.
    yticks/xticks: [(값, '표시')]. seg_labels: [(x, y, '글자')] (그래프 좌표)."""
    d = Drawing(w, h)
    ox, oy = 30, 18
    pw, ph = w - ox - 12, h - oy - 16

    def P(x, y):
        return ox + x / float(xmax) * pw, oy + (y - ymin) / float(ymax - ymin) * ph

    arrow(d, ox, oy, ox + pw + 8, oy, width=0.8, head=4)
    arrow(d, ox, oy, ox, oy + ph + 10, width=0.8, head=4)
    if origin:
        _text(d, ox - 3, oy - 10, "O", 8, anchor="end", font="MI")
    _text(d, ox + pw + 8, oy - 11, xlabel, 7.5, anchor="end")
    _text(d, ox + 3, oy + ph + 6, ylabel, 7.5, anchor="start")
    for v, s in yticks:
        _, y = P(0, v)
        _text(d, ox - 3, y - 2.8, s, 7.5, anchor="end")
    for v, s in xticks:
        x, _ = P(v, ymin)
        _text(d, x, oy - 10, s, 7.5)
    for gx, gy in guides:
        x, y = P(gx, gy)
        d.add(Line(ox, y, x, y, strokeDashArray=[2, 2], strokeWidth=0.5,
                   strokeColor=GREY))
        d.add(Line(x, oy, x, y, strokeDashArray=[2, 2], strokeWidth=0.5,
                   strokeColor=GREY))
    for s in series:
        flat = []
        for x, y in s["pts"]:
            flat.extend(P(x, y))
        d.add(PolyLine(flat, strokeColor=BLACK, strokeWidth=1.3,
                       strokeDashArray=[4, 2] if s.get("dash") else None))
    for x, y, s in seg_labels:
        px, py = P(x, y)
        _text(d, px, py, s, 8.5)
    for i, (txt, dash) in enumerate(legend):
        if legend_at:
            lx, ly = P(*legend_at)
            ly -= i * 11
        else:
            lx = ox + pw - 58
            ly = oy + ph - 4 - i * 11
        d.add(Line(lx, ly + 2.5, lx + 16, ly + 2.5, strokeWidth=1.3,
                   strokeDashArray=[4, 2] if dash else None))
        _text(d, lx + 19, ly, txt, 7.5, anchor="start")
    return d


# ---------------------------------------------------------------- 지구와 중력
def earth_gravity(w=210, h=160, spots=None):
    """spots: [(이름, 각도(도), {화살표이름: 'in'|'out'|'down'|'up'|'left'|'right'}, 이름위치각도)]"""
    d = Drawing(w, h)
    cx, cy, R = w / 2 - 6, h / 2, 40
    d.add(Circle(cx, cy, R, strokeColor=BLACK, strokeWidth=0.9,
                 fillColor=colors.HexColor("#E9F1E4")))
    _text(d, cx, cy + 6, "지구", 9)
    d.add(Circle(cx, cy, 1.4, fillColor=BLACK, strokeColor=BLACK))
    _text(d, cx, cy - 9, "지구 중심", 6.5, color=GREY)
    for spot in spots or []:
        name, deg, arrows = spot[:3]
        name_deg = spot[3] if len(spot) > 3 else deg + 90
        a = math.radians(deg)
        dist = R + 19
        bx, by = cx + dist * math.cos(a), cy + dist * math.sin(a)
        d.add(Circle(bx, by, 4, fillColor=colors.white, strokeColor=BLACK,
                     strokeWidth=0.8))
        na = math.radians(name_deg)
        _text(d, bx + 13 * math.cos(na), by + 13 * math.sin(na) - 3, name, 8.5)
        dirs = {"in": (-math.cos(a), -math.sin(a)), "out": (math.cos(a), math.sin(a)),
                "down": (0, -1), "up": (0, 1), "left": (-1, 0), "right": (1, 0)}
        for label, key in arrows.items():
            ux, uy = dirs[key]
            L = 10 if key == "in" else 17
            sx, sy = bx + ux * 5, by + uy * 5
            ex, ey = bx + ux * (5 + L), by + uy * (5 + L)
            arrow(d, sx, sy, ex, ey, width=0.8, head=4)
            # 글자는 화살표 끝에서 화살표와 수직 방향으로 살짝 비켜 놓는다
            px, py = -uy, ux
            _text(d, ex + px * 7, ey + py * 7 - 3, label, 8)
    return d


# ---------------------------------------------------------------- 실험 장치
def zipper_bag(w=220, h=70):
    """뜨거운 물이 담긴 수조에 넣기 전(가)·후(나)의 지퍼 백."""
    d = Drawing(w, h)
    # (가) 납작한 지퍼 백
    d.add(Rect(10, 24, 70, 18, rx=3, ry=3, strokeColor=BLACK, strokeWidth=0.8,
               fillColor=colors.white))
    d.add(Line(10, 38, 80, 38, strokeWidth=0.6))
    for x in (40, 46, 52):
        d.add(Circle(x, 28, 1.6, fillColor=GREY, strokeColor=GREY))
    _text(d, 45, 8, "(가) 넣기 전", 8)
    _text(d, 45, 46, "액체 아세톤", 7, color=GREY)
    arrow(d, 92, 33, 112, 33)
    # (나) 수조와 부푼 지퍼 백
    d.add(Rect(122, 14, 90, 46, strokeColor=BLACK, strokeWidth=0.8,
               fillColor=colors.white))
    d.add(Rect(122.5, 14.5, 89, 32, strokeWidth=0, fillColor=WATER))
    d.add(Ellipse(167, 40, 30, 15, strokeColor=BLACK, strokeWidth=0.8,
                  fillColor=colors.white))
    _text(d, 167, 2, "(나) 뜨거운 물에 넣은 후", 8)
    return d


def ink_beakers(temps=("10 ℃", "60 ℃"), labels=("(가)", "(나)"), w=200, h=74):
    d = Drawing(w, h)
    for i, (t, lab) in enumerate(zip(temps, labels)):
        x = 26 + i * 96
        d.add(Rect(x, 14, 56, 50, strokeColor=BLACK, strokeWidth=0.8,
                   fillColor=colors.white))
        d.add(Rect(x + 0.5, 14.5, 55, 36, strokeWidth=0, fillColor=WATER))
        d.add(Circle(x + 28, 58, 2.2, fillColor=colors.HexColor("#333366"),
                     strokeColor=colors.HexColor("#333366")))
        _text(d, x + 28, 28, "물 " + t, 7.5)
        _text(d, x + 28, 3, lab, 8.5)
        _text(d, x + 46, 66, "잉크", 7, color=GREY)
    return d


# ---------------------------------------------------------------- 확산 유리관
def diffusion_tube(w=220, h=62, left="기체 A를 묻힌 솜", right="기체 B를 묻힌 솜"):
    """양 끝을 마개로 막은 긴 유리관과 양 끝의 솜, 가운데 표시."""
    d = Drawing(w, h)
    x0, x1, y, th = 14, w - 14, 30, 14
    d.add(Rect(x0, y, x1 - x0, th, strokeColor=BLACK, strokeWidth=0.9,
               fillColor=colors.HexColor("#F3F8FB")))
    for xs in (x0 - 6, x1):
        d.add(Rect(xs, y - 2, 6, th + 4, strokeColor=BLACK, strokeWidth=0.6,
                   fillColor=GREY))
    for cx in (x0 + 9, x1 - 9):
        d.add(Ellipse(cx, y + th / 2, 6.5, 5.5, strokeColor=GREY, strokeWidth=0.6,
                      fillColor=LIGHT))
    mid = (x0 + x1) / 2.0
    d.add(Line(mid, y - 5, mid, y + th + 5, strokeDashArray=[2, 2], strokeWidth=0.6,
               strokeColor=GREY))
    _text(d, mid, y + th + 8, "가운데", 7.5, color=GREY)
    d.add(Line(x0 + 9, y - 1, x0 + 9, 14, strokeWidth=0.5, strokeColor=GREY))
    d.add(Line(x1 - 9, y - 1, x1 - 9, 14, strokeWidth=0.5, strokeColor=GREY))
    _text(d, x0 + 2, 5, left, 7.8, anchor="start")
    _text(d, x1 - 2, 5, right, 7.8, anchor="end")
    return d


# ---------------------------------------------------------------- 힘의 화살표(모눈)
def force_grid(arrows, ncol=12, nrow=5, cell=14, note=None):
    """arrows: [(이름, x0, y0, x1, y1, (글자dx, 글자dy))] 모눈 칸 단위. 시작점에 점을 찍는다."""
    pad = 6
    w, h = ncol * cell + 2 * pad, nrow * cell + 2 * pad + (12 if note else 0)
    d = Drawing(w, h)
    oy = pad + (12 if note else 0)
    for i in range(ncol + 1):
        x = pad + i * cell
        d.add(Line(x, oy, x, oy + nrow * cell, strokeWidth=0.4, strokeColor=LIGHT))
    for j in range(nrow + 1):
        y = oy + j * cell
        d.add(Line(pad, y, pad + ncol * cell, y, strokeWidth=0.4, strokeColor=LIGHT))
    for name, ax, ay, bx, by, (tx, ty) in arrows:
        sx, sy = pad + ax * cell, oy + ay * cell
        ex, ey = pad + bx * cell, oy + by * cell
        arrow(d, sx, sy, ex, ey, width=1.4, head=6)
        d.add(Circle(sx, sy, 2.2, fillColor=BLACK, strokeColor=BLACK))
        _text(d, (sx + ex) / 2 + tx, (sy + ey) / 2 + ty, name, 9, font="MI")
    if note:
        _text(d, w - pad, 2, note, 7.5, anchor="end", color=GREY)
    return d
