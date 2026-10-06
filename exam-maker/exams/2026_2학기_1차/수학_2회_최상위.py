"""수학 예상문제 2회 최상위.

범위: Ⅲ-01 좌표와 그래프 ~ Ⅳ-02 작도와 합동 (학교 학습지 포함)
형식: 선택형 21문항 90점, 논술형 2문항 10점 (가정통신문 기준)
학습지의 기초·기본·도전 문항 유형을 한 단계 더 비틀어 만들었다.
정답은 scratchpad의 verify_math.py로 수치 검증하였다.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))

from reportlab.graphics.shapes import Drawing, Ellipse, Line, PolyLine  # noqa: E402
from reportlab.platypus import Table, TableStyle  # noqa: E402

from exam_pdf import (COL_W, COLUMN_BREAK, Exam, Essay, Q, Sub, bogi, box,  # noqa: E402
                      figure)
from math_figs import (BLACK, LIGHT, SHADE, Geo, Plane, _arrow, _txt,  # noqa: E402
                       eq, mini_graph)

TOP = "옥길새길중학교 1학년 · 2026학년도 2학기 1차 정기시험 대비 · 수학 Ⅲ-01~Ⅳ-02"
ex = Exam(top=TOP, title="수학 예상문제 2회 최상위",
          expect=dict(mc=21, mc_pts=90, essay=2, essay_pts=10), essay_new_page=False,
          mc_label="객관식")


# ------------------------------------------------------------ 수식 표기
def M(s):
    """영문 수식: 소문자는 기울임, '-'는 빼기 기호."""
    out = []
    for ch in s:
        if "a" <= ch <= "z":
            out.append('<font name="MI">%s</font>' % ch)
        elif ch == "-":
            out.append("−")
        else:
            out.append(ch)
    return '<font name="MR">%s</font>' % "".join(out)


def ov(s):
    """선분 기호(윗줄)."""
    return '<font name="MR"><strike offset="7.6" width="0.55">%s</strike></font>' % s


def F(n, d):
    return '<font name="MR"><super>%s</super>⁄<sub>%s</sub></font>' % (n, d)


def SQ(s):
    return M(s) + '<font name="MR"><super>2</super></font>'


X, Y = M("x"), M("y")
LP = M("l") + " ∥ " + M("m")
DEG = '<font name="MR">°</font>'


def A_(s):
    return "∠" + M(s)


def num_choices(vals, unit=""):
    return ["%s%s" % (M(str(v)) if isinstance(v, (int, float)) else v, unit) for v in vals]


def deg_choices(vals):
    return [M(str(v)) + DEG for v in vals]


def grid_choices(drawings, cols=3):
    rows = []
    for i in range(0, len(drawings), cols):
        r = drawings[i:i + cols]
        r += [""] * (cols - len(r))
        rows.append(r)
    t = Table(rows, colWidths=[COL_W / cols] * cols, hAlign="CENTER")
    t.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"),
                           ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("TOPPADDING", (0, 0), (-1, -1), 2),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    return t


def inter(p1, d1, p2, d2):
    det = d1[0] * (-d2[1]) - d1[1] * (-d2[0])
    t = ((p2[0] - p1[0]) * (-d2[1]) - (p2[1] - p1[1]) * (-d2[0])) / det
    return (p1[0] + t * d1[0], p1[1] + t * d1[1])


def U(deg):
    return (math.cos(math.radians(deg)), math.sin(math.radians(deg)))


# ============================================================ Ⅲ-01 좌표와 그래프
ex.add(Q(1, "두 순서쌍 %s, %s이 서로 같을 때, 점 %s은 제몇 사분면 위의 점인가? (단, %s, %s는 수이다.) {pts}"
         % (M("(3a-2, b+4)"), M("(a+6, 2b-1)"), M("(b-a, a-") + SQ("b") + M(")"), M("a"), M("b")), 3,
         choices=["제1사분면", "제2사분면", "제3사분면", "제4사분면", "어느 사분면에도 속하지 않는다."],
         layout="stack", ans=4, concept="순서쌍, 사분면",
         exp=["%s에서 %s, %s에서 %s" % (M("3a-2=a+6"), M("a=4"), M("b+4=2b-1"), M("b=5")),
              "점 %s = %s은 %s좌표가 양수, %s좌표가 음수이므로 제4사분면 위의 점이다."
              % (M("(b-a, a-") + SQ("b") + M(")"), M("(1, -21)"), X, Y)]))

ex.add(Q(2, "점 %s가 제2사분면 위의 점일 때, 〈보기〉의 점 중 제2사분면 위의 점은 모두 몇 개인가? "
            "(단, %s, %s는 수이다.) {pts}" % (M("A(ab, a-b)"), M("a"), M("b")), 4,
         parts=[bogi("ㄱ. %s&nbsp;&nbsp;&nbsp;&nbsp;ㄴ. %s&nbsp;&nbsp;&nbsp;&nbsp;ㄷ. %s"
                     % (M("(b-a, a") + SQ("b") + M(")"), M("(") + SQ("a") + M("b, -b)"),
                        M("(a-b, ") + F(M("b"), M("a")) + M(")")),
                     "ㄹ. %s&nbsp;&nbsp;&nbsp;&nbsp;ㅁ. %s" % (M("(-ab, b-a)"), M("(ab, ") + SQ("a") + M(")")))],
         choices=["1개", "2개", "3개", "4개", "5개"], ans=3, concept="좌표의 부호",
         exp=["제2사분면 위의 점이므로 %s, %s이다. 곱이 음수이면 두 수의 부호가 다르고, %s이므로 %s, %s"
              % (M("ab<0"), M("a-b>0"), M("a-b>0"), M("a>0"), M("b<0")),
              "ㄱ (−, +) 제2사분면, ㄴ (−, +) 제2사분면, ㄷ (+, −) 제4사분면, ㄹ (+, −) 제4사분면, "
              "ㅁ (−, +) 제2사분면 → 3개",
              "%s, %s은 0이 아닌 수의 제곱이므로 항상 양수임을 이용한다." % (SQ("a"), SQ("b"))]))

ex.add(Q(3, "좌표평면 위의 세 점 %s, %s, %s를 꼭짓점으로 하는 삼각형 ABC의 넓이는? {pts}"
         % (M("A(-3, 4)"), M("B(-5, -2)"), M("C(4, 1)")), 4,
         choices=num_choices([16, 18, 20, 22, 24]), ans=5, concept="좌표평면 위의 도형의 넓이",
         exp=["세 점을 모두 포함하고 변이 좌표축에 평행한 직사각형(%s, %s)의 넓이는 %s이다."
              % (M("-5") + " ≤ " + X + " ≤ " + M("4"), M("-2") + " ≤ " + Y + " ≤ " + M("4"), M("9 × 6 = 54")),
              "여기서 세 직각삼각형의 넓이 %s, %s, %s를 빼면 %s"
              % (M("6"), F(27, 2), F(21, 2), M("54 - 30 = 24"))]))


def container():
    d = Drawing(130, 104)
    cx = 65
    parts = [(76, 24), (30, 24), (54, 24)]
    rs = [w / 2 for w, _ in parts]
    rys = [w * 0.1 for w, _ in parts]
    ys = [6, 30, 54]

    def half(r, ry, y):
        pts = []
        for k in range(41):
            t = math.pi + math.pi * k / 40
            pts += [cx + r * math.cos(t), y + ry * math.sin(t)]
        d.add(PolyLine(pts, strokeWidth=0.9, strokeColor=BLACK))

    for i, (w, h) in enumerate(parts):
        r, ry, y = rs[i], rys[i], ys[i]
        top = y + h
        above_wider = i + 1 < len(parts) and rs[i + 1] > r
        if above_wider:
            # 위 원기둥의 아랫면 테두리(앞쪽 반원)에 가려지는 곳까지만 옆선을 그린다
            top = top - rys[i + 1] * math.sqrt(1 - (r / rs[i + 1]) ** 2)
        d.add(Line(cx - r, y, cx - r, top, strokeWidth=0.9, strokeColor=BLACK))
        d.add(Line(cx + r, y, cx + r, top, strokeWidth=0.9, strokeColor=BLACK))
        half(r, ry, y)
        if not above_wider:
            d.add(Ellipse(cx, y + h, r, ry, fillColor=None, strokeColor=BLACK, strokeWidth=0.9))
    y = ys[-1] + parts[-1][1]
    _arrow(d, cx, y + 16, cx, y + 4, w=0.8)
    _txt(d, cx + 6, y + 10, "물", size=8, font="KR", anchor="start")
    return d


Q4_SEGS = [
    [(50, 20), (8, 20), (24.5, 20)],
    [(8, 20), (50, 20), (24.5, 20)],
    [(50, 20), (24.5, 20), (8, 20)],
    [(24.5, 20), (8, 20), (50, 20)],
    [(50, 20), (8, 20), (50, 20)],
]
ex.add(Q(4, "그림과 같이 높이가 같고 밑면의 반지름의 길이가 서로 다른 세 원기둥을 쌓아 만든 그릇이 있다. "
            "이 그릇에 시간당 일정한 양의 물을 넣을 때, 시간에 따른 물의 높이를 나타낸 그래프로 가장 "
            "알맞은 것은? {pts}", 4,
         parts=[figure(container())],
         choice_tbl=grid_choices([mini_graph(s, "①②③④⑤"[i]) for i, s in enumerate(Q4_SEGS)]),
         ans=1, ans_text="완만 → 가파름 → 중간 기울기", concept="상황에 맞는 그래프",
         exp=["밑면이 넓을수록 물의 높이는 천천히, 좁을수록 빠르게 높아진다.",
              "아래(가장 넓음) → 가장 완만, 가운데(가장 좁음) → 가장 가파름, 위(중간) → 중간 기울기이다.",
              "⑤는 맨 위 부분의 기울기가 맨 아래와 같으므로 알맞지 않다. 맨 위는 맨 아래보다 좁으므로 더 가파르다."]))


def race_graph():
    p = Plane(0, 10, 0, 7, unit=16, pad=16)
    p.grid(1)
    p.axes(xl="", yl="", origin=True)
    for i in range(1, 10):
        p.xtick(i, str(5 * i), size=6.5)
    for j in (2, 4, 6):
        p.ytick(j, str(j // 2), size=7)
    p.seg((0, 0), (9, 6), w=1.2)
    p.seg((3, 0), (6, 6), w=1.2)
    p.label(7.6, 4.2, "동생", font="KR", size=8)
    p.label(4.9, 5.6, "형", font="KR", size=8)
    sx, sy = p.S(10, 0)
    eq(p.d, sx + 6, sy - 16, [("i", "x"), ("k", "(분)")], size=8, anchor="end")
    sx, sy = p.S(0, 7)
    eq(p.d, sx + 4, sy + 6, [("i", "y"), ("k", "(km)")], size=8, anchor="start")
    return p.d


ex.add(Q(5, "그래프는 동생이 집에서 출발하여 걸어서 도서관에 가고, 형은 자전거를 타고 같은 길로 도서관에 갈 때, "
            "동생이 출발한 지 %s분 후 집에서 떨어진 거리를 %s km라 하여 나타낸 것이다. 이에 대한 설명으로 옳은 것만을 "
            "〈보기〉에서 있는 대로 고른 것은? (단, 두 사람은 각각 일정한 속력으로 이동한다.) {pts}" % (X, Y), 5,
         parts=[figure(race_graph()),
                bogi("ㄱ. 도서관은 집에서 3 km 떨어진 곳에 있다.",
                     "ㄴ. 형이 동생을 따라잡은 곳은 집에서 1.5 km 떨어진 곳이다.",
                     "ㄷ. 형은 동생보다 15분 먼저 도서관에 도착하였다.",
                     "ㄹ. 동생의 속력은 형의 속력의 %s이다." % F(1, 2),
                     "ㅁ. 형이 동생을 따라잡은 것은 동생이 출발한 지 20분 후이다.")],
         choices=["ㄱ, ㄷ", "ㄱ, ㄴ, ㄷ", "ㄴ, ㄹ", "ㄱ, ㄷ, ㅁ", "ㄴ, ㄷ, ㄹ"], ans=2,
         concept="그래프의 해석",
         exp=["동생은 45분 동안 3 km → 1분에 %s km, 형은 15분 동안 3 km → 1분에 %s km (동생의 3배)이므로 ㄹ은 틀렸다."
              % (F(1, 15), F(1, 5)),
              "형이 출발할 때(15분) 동생은 1 km 앞에 있고, 1분에 %s km씩 가까워지므로 %s분 후 따라잡는다."
              % (F(2, 15), M("1 ÷ ") + F(2, 15) + M(" = 7.5")),
              "즉 동생이 출발한 지 22.5분 후, 집에서 %s km 떨어진 곳이다. (ㄴ 옳음, ㅁ 틀림)"
              % (M("22.5 × ") + F(1, 15) + M(" = 1.5")),
              "형은 30분, 동생은 45분에 도착하므로 형이 15분 먼저 도착한다."]))

# ============================================================ Ⅲ-02 정비례와 반비례
ex.add(Q(6, "〈보기〉에서 %s가 %s에 정비례하는 것의 개수를 %s, 반비례하는 것의 개수를 %s라 할 때, %s의 값은? {pts}"
         % (Y, X, M("a"), M("b"), M("a × b")), 4,
         parts=[bogi("ㄱ. 시속 60 km로 %s시간 동안 달린 거리 %s km" % (X, Y),
                     "ㄴ. 넓이가 24 cm<super>2</super>인 삼각형의 밑변의 길이 %s cm와 높이 %s cm" % (X, Y),
                     "ㄷ. 둘레의 길이가 %s cm인 정육각형의 한 변의 길이 %s cm" % (X, Y),
                     "ㄹ. 1000원짜리 공책 %s권을 사고 10000원을 냈을 때 받는 거스름돈 %s원" % (X, Y),
                     "ㅁ. 톱니 30개인 톱니바퀴 A가 4번 회전할 때, A와 맞물려 돌아가는 톱니 %s개인 톱니바퀴 B의 "
                     "회전 수 %s" % (X, Y),
                     "ㅂ. 시계의 시침이 %s시간 동안 회전한 각도 %s°" % (X, Y),
                     "ㅅ. 나이가 %s살인 사람의 키 %s cm" % (X, Y))],
         choices=num_choices([2, 3, 4, 5, 6]), ans=5, concept="정비례와 반비례의 판별",
         exp=["정비례: ㄱ %s, ㄷ %s, ㅂ %s → %s" % (M("y=60x"), M("y=") + F(M("x"), 6), M("y=30x"), M("a=3")),
              "반비례: ㄴ %s, ㅁ %s → %s" % (M("y=") + F(48, M("x")), M("y=") + F(120, M("x")), M("b=2")),
              "ㄹ %s, ㅅ은 어느 것도 아니다. 따라서 %s" % (M("y=10000-1000x"), M("a × b = 6"))]))

ex.add(Q(7, "정비례 관계 %s의 그래프가 점 %s을 지날 때, 이 그래프에 대한 설명으로 옳은 것만을 〈보기〉에서 "
            "있는 대로 고른 것은? (단, %s는 수이다.) {pts}" % (M("y=ax"), M("(-4, 6)"), M("a")), 4,
         parts=[bogi("ㄱ. 원점을 지나는 직선이다.",
                     "ㄴ. 제2사분면과 제4사분면을 지난다.",
                     "ㄷ. %s의 값이 증가하면 %s의 값도 증가한다." % (X, Y),
                     "ㄹ. 점 %s를 지난다." % M("(6, -9)"),
                     "ㅁ. 정비례 관계 %s의 그래프보다 %s축에 더 가깝다." % (M("y=-x"), Y))],
         choices=["ㄱ, ㄴ", "ㄱ, ㄷ, ㄹ", "ㄴ, ㄷ, ㅁ", "ㄱ, ㄴ, ㄹ, ㅁ", "ㄱ, ㄴ, ㄷ, ㄹ, ㅁ"], ans=4,
         concept="정비례 관계의 그래프",
         exp=["%s에서 %s, 즉 %s" % (M("6=-4a"), M("a=-") + F(3, 2), M("y=-") + F(3, 2) + X),
              "ㄷ. %s < 0이므로 %s의 값이 증가하면 %s의 값은 감소한다." % (M("a"), X, Y),
              "ㅁ. %s의 절댓값이 클수록 %s축에 가깝다. %s이므로 %s보다 %s축에 가깝다."
              % (M("a"), Y, M("|-") + F(3, 2) + M("| > |-1|"), M("y=-x"), Y)]))

ex.add(Q(8, "정비례 관계 %s의 그래프와 반비례 관계 %s의 그래프가 점 %s에서 만난다. 반비례 관계 %s의 그래프 "
            "위의 점 중에서 제2사분면 위에 있고 %s좌표와 %s좌표가 모두 정수인 점의 개수는? (단, %s는 수이다.) {pts}"
         % (M("y=-") + F(4, 3) + X, M("y=") + F(M("a"), M("x")), M("P(3, k)"), M("y=") + F(M("a"), M("x")),
            X, Y, M("a")), 4,
         choices=num_choices([2, 4, 6, 8, 12]), ans=3, concept="반비례 관계의 그래프 위의 점",
         exp=["%s에서 %s, 점 %s를 대입하면 %s" % (M("k=-") + F(4, 3) + M(" × 3"), M("k=-4"), M("P(3, -4)"),
                                              M("a=3 × (-4)=-12")),
              "제2사분면이므로 %s < 0, %s > 0이고 %s는 12의 약수에 −를 붙인 수이다." % (X, Y, X),
              "%s의 6개" % M("(-1, 12), (-2, 6), (-3, 4), (-4, 3), (-6, 2), (-12, 1)")]))


def q9_fig():
    p = Plane(-8.5, 8.5, -8.5, 8.5, unit=9, pad=12)
    p.axes()
    p.curve(lambda x: -18 / x, -8.5, -2.1)
    p.curve(lambda x: -18 / x, 2.1, 8.5)
    p.poly([(-3, 6), (0, 0), (6, -3)], fill=SHADE)
    p.seg((3, -6), (3, 0), dash=True, w=0.6)
    p.seg((3, -6), (0, -6), dash=True, w=0.6)
    p.right(3, 0, sx=-1, sy=-1)
    p.right(0, -6, sx=1, sy=1)
    p.point(-3, 6, "A", dx=-7, dy=5)
    p.point(6, -3, "B", dx=7, dy=4)
    p.point(3, -6, "P", dx=7, dy=-3)
    p.label(3, 0, "Q", dx=4, dy=8)
    p.label(0, -6, "R", dx=-7, dy=0)
    p.eqlab(-6.9, 7.4, [("i", "y"), ("r", " = "), ("f", "a", "x", "MI", "MI")], size=8.5)
    return p.d


ex.add(Q(9, "그림과 같이 반비례 관계 %s의 그래프가 제2사분면과 제4사분면을 지난다. 그래프 위의 한 점 P에서 "
            "%s축, %s축에 내린 수선의 발을 각각 Q, R라 하면 직사각형 OQPR의 넓이는 18이다. 이 그래프 위의 두 점 "
            "%s, %s에 대하여 삼각형 AOB의 넓이는? (단, 점 O는 원점이고, %s는 수이다.) {pts}"
         % (M("y=") + F(M("a"), M("x")), X, Y, M("A(-3, b)"), M("B(c, -3)"), M("a")), 5,
         parts=[figure(q9_fig())],
         choices=[M("12"), F(27, 2), M("15"), M("18"), M("27")], ans=2, ans_text=F(27, 2),
         concept="반비례 그래프와 넓이",
         exp=["점 %s에 대하여 직사각형 OQPR의 넓이는 %s이고, 제2·4사분면을 지나므로 %s"
              % (M("P(p, q)"), M("|pq| = |a| = 18"), M("a=-18")),
              "%s, %s" % (M("b=") + F(M("-18"), M("-3")) + M("=6") + " → " + M("A(-3, 6)"),
                          M("-3=") + F(M("-18"), M("c")) + " → " + M("c=6") + ", " + M("B(6, -3)")),
              "직선 AB는 %s축과 점 %s, %s축과 점 %s에서 만나므로 삼각형 AOB를 세 부분으로 나누면"
              % (Y, M("(0, 3)"), X, M("(3, 0)")),
              "%s" % (F(1, 2) + M(" × 3 × 3 + ") + F(1, 2) + M(" × 3 × 3 + ") + F(1, 2) + M(" × 3 × 3 = ")
                      + F(27, 2))]))


def q10_fig():
    p = Plane(-1.2, 9.6, -1.2, 13.8, unit=9.2, pad=12)
    p.axes()
    p.curve(lambda x: 2 * x / 3, -1.2, 9.4)
    p.curve(lambda x: 24 / x, 1.75, 9.6)
    p.poly([(0, 0), (6, 4), (2, 12)], fill=SHADE)
    p.seg((2, 0), (2, 12), dash=True, w=0.6)
    p.seg((0, 4), (6, 4), dash=True, w=0.6)
    p.xtick(2, "2", mark=False)
    p.ytick(4, "4", mark=False)
    p.point(6, 4, "A", dx=6, dy=6)
    p.point(2, 12, "B", dx=7, dy=3)
    p.eqlab(8.2, 7.3, [("i", "y"), ("r", " = "), ("f", "2", "3"), ("i", "x")], size=8.5)
    p.eqlab(7.7, 1.6, [("i", "y"), ("r", " = "), ("f", "a", "x", "MI", "MI")], size=8.5)
    return p.d


ex.add(Q(10, "그림과 같이 정비례 관계 %s의 그래프와 반비례 관계 %s %s의 그래프가 점 A에서 만나고, 점 A의 %s좌표는 "
             "4이다. 반비례 관계 %s의 그래프 위의 점 B의 %s좌표가 2일 때, 삼각형 AOB의 넓이는? "
             "(단, 점 O는 원점이고, %s는 수이다.) {pts}"
         % (M("y=") + F(2, 3) + X, M("y=") + F(M("a"), M("x")), M("(x>0)"), Y, M("y=") + F(M("a"), M("x")),
            X, M("a")), 5,
         parts=[figure(q10_fig())],
         choices=num_choices([30, 32, 34, 36, 38]), ans=2, concept="정비례·반비례 그래프와 넓이",
         exp=["%s에서 %s → %s, %s" % (M("4=") + F(2, 3) + X, M("x=6"), M("A(6, 4)"), M("a=6 × 4=24")),
              "%s → %s" % (M("y=") + F(24, 2) + M("=12"), M("B(2, 12)")),
              "직사각형(%s, %s) 넓이 72에서 세 직각삼각형 12, 12, 16을 빼면 %s"
              % (M("0") + " ≤ " + X + " ≤ " + M("6"), M("0") + " ≤ " + Y + " ≤ " + M("12"),
                 M("72-40=32"))]))

# ============================================================ Ⅳ-01 기본 도형
def q11_fig():
    pts = {"O": (0, 0)}
    for a in (0, 65, 115, 180, 245, 295):
        pts["r%d" % a] = U(a)
    g = Geo(pts, width=175, pad=10)
    for a in (0, 65, 115):
        g.seg("r%d" % a, "r%d" % (a + 180))
    g.dot("O")
    lab = lambda a, b, c: [("r", a), ("i", "x"), ("r", b)] + ([("r", c)] if c else [])
    g.arcq("O", "r0", "r65", r=12, parts=lab("(2", "+15)°", ""), lr=40, size=8)
    g.arcq("O", "r245", "r295", r=12, parts=lab("(", "+25)°", ""), lr=34, size=8)
    g.arcq("O", "r115", "r180", r=15, parts=lab("(3", "-10)°".replace("-", "−"), ""), lr=40, size=8)
    g.arcq("O", "r295", "r0", r=12, parts=[("i", "y"), ("r", "°")], lr=24, size=8.5)
    return g.d


ex.add(Q(11, "그림과 같이 세 직선이 한 점에서 만날 때, %s의 값은? {pts}" % M("x+y"), 3,
         parts=[figure(q11_fig())],
         choices=num_choices([70, 75, 80, 85, 90]), ans=5, concept="맞꼭지각",
         exp=["%s°의 맞꼭지각은 위쪽의 두 각 사이에 있으므로 %s" % (M("(x+25)"), M("(2x+15)+(x+25)+(3x-10)=180")),
              "%s, %s → %s" % (M("6x+30=180"), M("x=25"), M("y=3x-10=65") + " (맞꼭지각)"),
              "따라서 %s" % M("x+y=90")]))


def q12_fig():
    g = Geo({"L0": (-0.7, 0), "L1": (5.7, 0), "A": (0, 0), "B": (1.7, 0), "C": (3.1, 0),
             "D": (5, 0), "E": (2.4, 1.5)}, width=170, pad=10)
    g.seg("L0", "L1")
    for n in "ABCDE":
        g.dot(n)
    for n in "ABCD":
        g.lab(n, dy=-10)
    g.lab("E", dy=9)
    return g.d


ex.add(Q(12, "그림과 같이 한 직선 위에 네 점 A, B, C, D가 있고, 직선 위에 있지 않은 한 점 E가 있다. 이 5개의 점 중 "
             "두 점을 이어 만들 수 있는 서로 다른 직선의 개수를 %s, 반직선의 개수를 %s, 선분의 개수를 %s라 할 때, "
             "%s의 값은? {pts}" % (M("a"), M("b"), M("c"), M("a+b+c")), 5,
         parts=[figure(q12_fig())],
         choices=num_choices([29, 31, 33, 35, 40]), ans=1, concept="직선, 반직선, 선분",
         exp=["직선: 한 직선 위의 네 점으로 만든 직선은 모두 같으므로 1개, E와 A, B, C, D를 잇는 직선 4개 → %s"
              % M("a=5"),
              "반직선: 직선 위에서 %s, %s, %s, %s, %s, %s의 6개(%s 등은 같은 반직선), "
              "E를 포함하는 반직선 8개 → %s" % (ov("AB"), ov("BA"), ov("BC"), ov("CB"), ov("CD"), ov("DC"),
                                          ov("AB") + "=" + ov("AC") + "=" + ov("AD"), M("b=14")),
              "선분: 두 점마다 하나씩 10개 → %s. 따라서 %s" % (M("c=10"), M("a+b+c=29"))]))


def q13_fig():
    g = Geo({"A": (0, 0), "M": (3, 0), "B": (6, 0), "C": (18, 0), "N": (24, 0), "D": (30, 0)},
            width=200, pad=12, extra=[(0, 5.2), (0, -2.6)])
    g.seg("A", "D")
    for n in "AMBCND":
        g.dot(n)
        g.lab(n, dy=-10)
    g.ticks("A", "M", 1)
    g.ticks("M", "B", 1)
    g.ticks("C", "N", 2)
    g.ticks("N", "D", 2)
    g.brace_len("A", "D", "30 cm", off=22)
    g.brace_len("M", "N", "21 cm", off=9)
    return g.d


ex.add(Q(13, "그림과 같이 네 점 A, B, C, D가 이 순서로 한 직선 위에 있고, 두 점 M, N은 각각 %s, %s의 중점이다. "
             "%s = 30 cm, %s = 21 cm이고 %s : %s = 1 : 2일 때, %s의 길이는? {pts}"
         % (ov("AB"), ov("CD"), ov("AD"), ov("MN"), ov("AB"), ov("CD"), ov("BN")), 4,
         parts=[figure(q13_fig())],
         choices=num_choices([15, 16, 17, 18, 20], " cm"), ans=4, concept="선분의 중점",
         exp=["%s이므로 %s, 즉 %s"
              % (ov("MN") + " = " + ov("AD") + " − (" + ov("AM") + " + " + ov("ND") + ")",
                 M("21 = 30 - ") + F(1, 2) + M("(") + ov("AB") + M(" + ") + ov("CD") + M(")"),
                 ov("AB") + " + " + ov("CD") + M(" = 18")),
              "%s : %s = 1 : 2이므로 %s = 6 cm, %s = 12 cm, %s = 30 − 18 = 12 (cm)"
              % (ov("AB"), ov("CD"), ov("AB"), ov("CD"), ov("BC")),
              "%s = %s + %s = 12 + 6 = 18 (cm)" % (ov("BN"), ov("BC"), ov("CN"))]))


def q14_fig():
    A, C = (0, 10), (0.2, 0)
    B = inter(A, U(180 + 70), C, U(180 - 70))
    Dd = inter(A, U(180 + 105), C, U(180 - 105))
    g = Geo({"l0": (-5, 10), "l1": (5, 10), "m0": (-5, 0), "m1": (5, 0), "P": (-3.8, 10), "Q": (-3.6, 0),
             "A": A, "C": C, "B": B, "D": Dd}, width=180, pad=12)
    g.seg("l0", "l1")
    g.seg("m0", "m1")
    g.path(["A", "B", "C"])
    g.path(["A", "D", "C"])
    for n in ("P", "Q", "A", "C"):
        g.dot(n, r=1.3)
    g.lab("P", dy=8)
    g.lab("A", dy=8)
    g.lab("Q", dy=-9)
    g.lab("C", dy=-9)
    g.lab("B", dx=-7)
    g.lab("D", dx=8, dy=0)
    g.lab("l1", "l", dx=6, font="MI")
    g.lab("m1", "m", dx=7, font="MI")
    g.mark("A", "B", "D", "•", r=18, size=7)
    g.mark("A", "P", "B", "••", r=12, size=6)
    g.mark("C", "B", "D", "×", r=17, size=7)
    g.mark("C", "Q", "B", "××", r=12, size=6)
    g.arc("D", "A", "C", r=7, label="150°", lr=17, size=7.5)
    g.arcq("B", "A", "C", r=7, parts=[("i", "x")], lr=14, size=9)
    return g.d


ex.add(Q(14, "그림에서 %s이고, %s, %s이다. %s일 때, %s의 크기는? {pts}"
         % (LP, "∠PAB = 2∠BAD", "∠QCB = 2∠BCD", "∠ADC = " + M("150") + DEG, A_("x")), 5,
         parts=[figure(q14_fig())],
         choices=deg_choices([120, 125, 130, 135, 140]), ans=5, concept="평행선의 성질(꺾인 선)",
         exp=["∠BAD = ●, ∠BCD = ×라 하면 ∠PAB = 2●, ∠QCB = 2×이다.",
              "점 D를 지나고 %s에 평행한 직선을 그으면, 엇각에 의해 ∠ADC = (180° − 3●) + (180° − 3×) = 150°"
              % M("l"),
              "따라서 ● + × = 70°",
              "점 B를 지나고 %s에 평행한 직선을 그으면 %s = 2● + 2× = 2 × 70° = 140°" % (M("l"), A_("x"))]))


def q15_fig():
    h, w, f = 40, 120, 50
    Fp = (f, 0)
    E = (f + h / math.tan(math.radians(70)), h)

    def refl(P):
        dx, dy = E[0] - Fp[0], E[1] - Fp[1]
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        px, py = P[0] - Fp[0], P[1] - Fp[1]
        t = px * ux + py * uy
        return (Fp[0] + 2 * t * ux - px, Fp[1] + 2 * t * uy - py)

    pts = {"A": (0, h), "B": (0, 0), "C": (w, 0), "D": (w, h), "E": E, "F": Fp,
           "C'": refl((w, 0)), "D'": refl((w, h))}
    g = Geo(pts, width=200, pad=12)
    g.fill(["E", "F", "C'", "D'"])
    g.path(["E", "A", "B", "F"])
    g.path(["F", "C", "D", "E"], dash=True)
    g.path(["E", "F", "C'", "D'"], close=True)
    g.lab("A", dx=-7)
    g.lab("B", dx=-6, dy=-7)
    g.lab("C", dx=6, dy=-7)
    g.lab("D", dx=7)
    g.lab("E", dx=4, dy=8)
    g.lab("F", dy=-9)
    g.lab("C'", dx=-8, dy=2)
    g.lab("D'", dy=8)
    g.arc("F", "C'", "B", r=10, label="40°", lr=21, size=7.5)
    g.arcq("F", "E", "C'", r=8, parts=[("i", "x")], lr=14, size=9)
    g.arcq("E", "A", "D'", r=9, parts=[("i", "y")], lr=15, size=9)
    return g.d


ex.add(Q(15, "그림과 같이 직사각형 ABCD 모양의 종이를 %s를 접는 선으로 하여 접었더니 두 점 C, D가 각각 점 C', D'으로 "
             "옮겨졌다. ∠C'FB = %s일 때, %s의 크기는? {pts}"
         % (ov("EF"), M("40") + DEG, A_("x") + " + " + A_("y")), 4,
         parts=[figure(q15_fig())],
         choices=deg_choices([100, 105, 110, 115, 120]), ans=3, concept="접은 도형과 평행선",
         exp=["접은 각은 같으므로 ∠EFC = ∠EFC' = %s, %s → %s" % (A_("x"), M("40") + DEG + " + 2" + A_("x") + " = "
                                                         + M("180") + DEG, A_("x") + " = " + M("70") + DEG),
              "%s이므로 ∠DEF = ∠EFB = 40° + 70° = 110° (엇각)" % (ov("AD") + " ∥ " + ov("BC")),
              "∠D'EF = ∠DEF = 110°이고 ∠AEF = 180° − 110° = 70°이므로 %s = 110° − 70° = 40°" % A_("y"),
              "따라서 %s = 70° + 40° = 110°" % (A_("x") + " + " + A_("y"))]))


def q16_fig():
    w, dpt, h = 3.2, 2.0, 2.3
    k, th = 0.55, math.radians(35)

    def pr(x, y, z):
        return (x + k * y * math.cos(th), z + k * y * math.sin(th))

    pts = {"A": pr(0, dpt, h), "B": pr(0, 0, h), "C": pr(w, 0, h),
           "E": pr(0, dpt, 0), "F": pr(0, 0, 0), "G": pr(w, 0, 0)}
    g = Geo(pts, width=140, pad=12)
    g.path(["A", "B", "C"], close=True)
    g.path(["B", "F", "G", "C"])
    g.path(["A", "E", "F"], dash=True)
    g.seg("E", "G", dash=True)
    g.lab("A", dy=8)
    g.lab("B", dx=-7)
    g.lab("C", dx=7)
    g.lab("E", dx=-7, dy=2)
    g.lab("F", dx=-6, dy=-7)
    g.lab("G", dx=6, dy=-7)
    return g.d


ex.add(Q(16, "그림은 직육면체를 네 꼭짓점 A, C, G, E를 지나는 평면으로 잘라서 만든 삼각기둥이다. 이에 대한 설명으로 "
             "옳은 것만을 〈보기〉에서 있는 대로 고른 것은? {pts}", 5,
         parts=[figure(q16_fig()),
                bogi("ㄱ. 모서리 AB와 꼬인 위치에 있는 모서리는 3개이다.",
                     "ㄴ. 모서리 AC와 평행한 면은 2개이다.",
                     "ㄷ. 모서리 BF와 수직인 면은 2개이다.",
                     "ㄹ. 면 ACGE와 수직인 면은 3개이다.",
                     "ㅁ. 모서리 CG와 꼬인 위치에 있는 모서리는 2개이다.")],
         choices=["ㄱ, ㄷ, ㅁ", "ㄱ, ㄴ, ㄷ", "ㄷ, ㄹ", "ㄱ, ㄹ, ㅁ", "ㄴ, ㄷ, ㅁ"], ans=1,
         concept="공간에서의 위치 관계",
         exp=["ㄱ. AB와 꼬인 위치: CG, FG, GE의 3개 (EF는 평행) ○",
              "ㄴ. AC와 평행한 면은 면 EFG 1개뿐이다. (AC는 면 ABC, 면 ACGE에 포함) ×",
              "ㄷ. BF와 수직인 면: 면 ABC, 면 EFG ○",
              "ㄹ. 면 ACGE와 수직인 면은 면 ABC, 면 EFG의 2개이다. 면 ABFE, 면 BCGF와는 수직이 아니다. ×",
              "ㅁ. CG와 꼬인 위치: AB, EF의 2개 ○"]))

# ============================================================ Ⅳ-02 작도와 합동
ex.add(Q(17, "길이가 2 cm, 3 cm, 4 cm, 5 cm, 7 cm인 5개의 선분 중 3개를 골라 만들 수 있는 서로 다른 삼각형의 개수는? {pts}",
         3, choices=num_choices([4, 5, 6, 7, 8], "개"), ans=2, concept="삼각형의 세 변의 길이 사이의 관계",
         exp=["(가장 긴 변의 길이) < (나머지 두 변의 길이의 합)이어야 한다.",
              "(2, 3, 4), (2, 4, 5), (3, 4, 5), (3, 5, 7), (4, 5, 7)의 5개",
              "(2, 3, 5), (2, 5, 7), (3, 4, 7)은 가장 긴 변이 나머지 두 변의 합과 같으므로 삼각형이 되지 않는다."]))

ex.add(Q(18, "작도와 삼각형의 결정 조건에 대한 설명으로 옳은 것은 〈보기〉에서 모두 몇 개인가? {pts}", 4,
         parts=[bogi("ㄱ. 선분의 길이를 재어서 다른 직선 위로 옮길 때는 컴퍼스를 사용한다.",
                     "ㄴ. 두 점을 지나는 선분을 그릴 때는 눈금 없는 자를 사용한다.",
                     "ㄷ. %s = 4 cm, %s = 7 cm, %s = 11 cm이면 △ABC가 하나로 정해진다." % (ov("AB"), ov("BC"), ov("CA")),
                     "ㄹ. %s = 6 cm, ∠A = 50°, ∠B = 130°이면 △ABC가 하나로 정해진다." % ov("AB"),
                     "ㅁ. %s = 5 cm, %s = 4 cm, ∠A = 40°이면 △ABC가 하나로 정해진다." % (ov("AB"), ov("BC")),
                     "ㅂ. ∠A = 40°, ∠B = 60°, %s = 5 cm이면 △ABC가 하나로 정해진다." % ov("AC"))],
         choices=["1개", "2개", "3개", "4개", "5개"], ans=3, concept="작도, 삼각형이 하나로 정해지는 조건",
         exp=["ㄷ. 4 + 7 = 11이므로 삼각형이 만들어지지 않는다. ×",
              "ㄹ. ∠A + ∠B = 180°이므로 삼각형이 만들어지지 않는다. ×",
              "ㅁ. ∠A는 두 변 AB, BC의 끼인각이 아니므로 하나로 정해지지 않는다(두 개가 생길 수 있다). ×",
              "ㅂ. ∠C = 80°이므로 한 변 AC와 그 양 끝 각 ∠A, ∠C가 주어진 것과 같다(ASA). ○",
              "옳은 것은 ㄱ, ㄴ, ㅂ의 3개"]))


def q19_fig():
    s1 = 10.0
    t = math.tan(math.radians(22))
    s2 = t * s1 / (math.sqrt(3) / 2 - t / 2)
    B, C, Dd = (0, 0), (s1, 0), (s1 + s2, 0)
    A = (s1 / 2, s1 * math.sqrt(3) / 2)
    E = (s1 + s2 / 2, s2 * math.sqrt(3) / 2)
    P = inter(A, (Dd[0] - A[0], Dd[1] - A[1]), B, (E[0] - B[0], E[1] - B[1]))
    g = Geo({"A": A, "B": B, "C": C, "D": Dd, "E": E, "P": P}, width=195, pad=12)
    g.path(["B", "A", "C"])
    g.seg("B", "D")
    g.path(["C", "E", "D"])
    g.seg("A", "D")
    g.seg("B", "E")
    g.lab("A", dy=8)
    g.lab("B", dx=-6, dy=-6)
    g.lab("C", dy=-9)
    g.lab("D", dx=6, dy=-6)
    g.lab("E", dy=8)
    g.lab("P", dy=8)
    g.arc("B", "C", "E", r=22, label="22°", lr=33, size=7.5)
    return g.d


ex.add(Q(19, "그림에서 점 C는 %s 위의 점이고, △ABC와 △ECD는 정삼각형이다. %s와 %s의 교점을 P라 하자. "
             "∠CBE = %s일 때, 옳은 것만을 〈보기〉에서 있는 대로 고른 것은? {pts}"
         % (ov("BD"), ov("AD"), ov("BE"), M("22") + DEG), 5,
         parts=[figure(q19_fig()),
                bogi("ㄱ. △ACD ≡ △BCE",
                     "ㄴ. %s = %s" % (ov("AD"), ov("BE")),
                     "ㄷ. ∠ADC = 38°",
                     "ㄹ. ∠APE = 60°",
                     "ㅁ. ㄱ의 두 삼각형은 ASA 합동이다.")],
         choices=["ㄱ, ㄴ", "ㄴ, ㄷ", "ㄱ, ㄴ, ㄹ", "ㄱ, ㄴ, ㄷ", "ㄴ, ㄷ, ㅁ"], ans=4,
         concept="삼각형의 합동(SAS)과 각의 크기",
         exp=["△ACD와 △BCE에서 %s, %s, ∠ACD = ∠BCE = 120°이므로 △ACD ≡ △BCE (SAS 합동) → ㄱ ○, ㅁ ×"
              % (ov("AC") + " = " + ov("BC"), ov("CD") + " = " + ov("CE")),
              "대응변이므로 %s ○" % (ov("AD") + " = " + ov("BE")),
              "∠CAD = ∠CBE = 22°이므로 ∠ADC = 180° − 120° − 22° = 38° ○",
              "△PBD에서 ∠BPD = 180° − 22° − 38° = 120°이고 ∠APE는 그 맞꼭지각이므로 120°이다. ×",
              "(∠APB = 60°와 혼동하지 않도록 주의한다.)"]))


def q20_fig():
    g = Geo({"A": (0, 10), "B": (0, 0), "C": (10, 0), "D": (10, 10), "E": (5, 10 + 5 * math.sqrt(3))},
            width=120, pad=12)
    g.path(["A", "B", "C", "D"], close=True)
    g.path(["A", "E", "D"])
    g.seg("B", "E")
    g.seg("C", "E")
    g.lab("A", dx=-7)
    g.lab("B", dx=-6, dy=-6)
    g.lab("C", dx=6, dy=-6)
    g.lab("D", dx=7)
    g.lab("E", dy=8)
    g.arcq("B", "E", "C", r=10, parts=[("i", "x")], lr=17, size=9)
    g.arcq("E", "B", "C", r=13, parts=[("i", "y")], lr=21, size=9)
    return g.d


ex.add(Q(20, "그림에서 사각형 ABCD는 정사각형이고, △AED는 정삼각형이다. ∠EBC = %s, ∠BEC = %s라 할 때, "
             "%s의 크기는? {pts}" % (A_("x"), A_("y"), A_("x") + " − " + A_("y")), 5,
         parts=[figure(q20_fig())],
         choices=deg_choices([45, 50, 55, 60, 75]), ans=1, concept="정사각형·정삼각형과 합동",
         exp=["%s이고 ∠BAE = 90° + 60° = 150°이므로 △ABE는 이등변삼각형, ∠ABE = ∠AEB = 15°"
              % (ov("AB") + " = " + ov("AD") + " = " + ov("AE")),
              "%s = 90° − 15° = 75°" % A_("x"),
              "△ABE ≡ △DCE (SAS 합동)이므로 ∠DEC = ∠AEB = 15°",
              "%s = 60° − 15° − 15° = 30°, 따라서 %s = 45°" % (A_("y"), A_("x") + " − " + A_("y"))]))


def q21_fig():
    s = 10.0
    B, C = (0, 0), (s, 0)
    A = (s / 2, s * math.sqrt(3) / 2)
    bd = s * math.sin(math.radians(18)) / math.sin(math.radians(102))
    Dd = (bd, 0)
    ca = (A[0] - C[0], A[1] - C[1])
    L = math.hypot(*ca)
    E = (C[0] + ca[0] / L * bd, C[1] + ca[1] / L * bd)
    P = inter(A, (Dd[0] - A[0], Dd[1] - A[1]), B, (E[0] - B[0], E[1] - B[1]))
    g = Geo({"A": A, "B": B, "C": C, "D": Dd, "E": E, "P": P}, width=160, pad=12)
    g.path(["A", "B", "C"], close=True)
    g.seg("A", "D")
    g.seg("B", "E")
    g.ticks("B", "D", 1)
    g.ticks("C", "E", 1)
    g.lab("A", dy=8)
    g.lab("B", dx=-6, dy=-6)
    g.lab("C", dx=6, dy=-6)
    g.lab("D", dy=-9)
    g.lab("E", dx=7, dy=2)
    g.lab("P", dx=-3, dy=9)
    g.arc("A", "B", "D", r=16, label="18°", lr=26, size=7.5)
    g.arcq("P", "B", "D", r=7, parts=[("i", "x")], lr=13, size=9)
    g.arcq("D", "A", "C", r=7, parts=[("i", "y")], lr=13, size=9)
    return g.d


ex.add(Q(21, "그림에서 △ABC는 정삼각형이고, 두 점 D, E는 각각 %s, %s 위의 점으로 %s이다. %s와 %s의 교점을 P라 하자. "
             "∠BAD = %s일 때, %s의 크기는? (단, %s = ∠BPD, %s = ∠ADC) {pts}"
         % (ov("BC"), ov("CA"), ov("BD") + " = " + ov("CE"), ov("AD"), ov("BE"), M("18") + DEG,
            A_("x") + " + " + A_("y"), A_("x"), A_("y")), 5,
         parts=[figure(q21_fig())],
         choices=deg_choices([132, 135, 138, 141, 144]), ans=3, concept="삼각형의 합동(SAS)과 외각",
         exp=["△ABD와 △BCE에서 %s, ∠ABD = ∠BCE = 60°, %s이므로 △ABD ≡ △BCE (SAS 합동)"
              % (ov("AB") + " = " + ov("BC"), ov("BD") + " = " + ov("CE")),
              "∠CBE = ∠BAD = 18°이므로 ∠ABP = 60° − 18° = 42°",
              "%s = ∠BPD는 △ABP의 외각이므로 18° + 42° = 60° (∠BAD의 크기와 관계없이 항상 60°)" % A_("x"),
              "%s = ∠ADC는 △ABD의 외각이므로 18° + 60° = 78°, 따라서 %s = 138°"
              % (A_("y"), A_("x") + " + " + A_("y"))]))

# ============================================================ 논술형
def e1_fig():
    p = Plane(-8.5, 8.5, -8.5, 8.5, unit=8.6, pad=12)
    p.axes()
    p.curve(lambda x: -0.75 * x, -8.5, 8.5)
    p.curve(lambda x: -12 / x, -8.5, -1.42)
    p.curve(lambda x: -12 / x, 1.42, 8.5)
    p.seg((-4, 0), (-4, 3), dash=True, w=0.6)
    p.xtick(-4, "−4", dy=-11, mark=False)
    p.point(-4, 3, "A", dx=-6, dy=7)
    p.point(4, -3, "B", dx=6, dy=7)
    p.eqlab(5.6, -7.6, [("i", "y"), ("r", " = −"), ("f", "3", "4"), ("i", "x")], size=8.5)
    p.eqlab(-3.6, 7.5, [("i", "y"), ("r", " = "), ("f", "a", "x", "MI", "MI")], size=8.5)
    return p.d


ex.add(COLUMN_BREAK)
ex.add(Essay(1, "그림과 같이 정비례 관계 %s의 그래프와 반비례 관계 %s의 그래프가 두 점 A, B에서 만나고, 점 A의 "
                "%s좌표는 −4이다. 다음 물음에 답하시오. (단, %s는 수이다.)"
             % (M("y=-") + F(3, 4) + X, M("y=") + F(M("a"), M("x")), X, M("a")),
             parts=[figure(e1_fig())],
             subs=[
                 Sub("(1) %s의 값을 구하시오." % M("a"), 2, box_h=58, label="풀이", answer_strip=True,
                     ans="−12",
                     model=["점 A는 %s의 그래프 위의 점이므로 %s → %s" % (M("y=-") + F(3, 4) + X,
                                                              M("y=-") + F(3, 4) + M(" × (-4)=3"), M("A(-4, 3)")),
                            "점 A는 %s의 그래프 위의 점이기도 하므로 %s → %s"
                            % (M("y=") + F(M("a"), M("x")), M("3=") + F(M("a"), M("-4")), M("a=-12"))],
                     rubric=["점 A의 좌표를 바르게 구한 경우 1점", "a = −12를 구한 경우 1점"]),
                 Sub("(2) 반비례 관계 %s의 그래프 위의 점 중에서 %s좌표와 %s좌표가 모두 정수인 점에 대하여, 제4사분면 "
                     "위에 있는 점의 좌표를 모두 구하고, 이러한 점은 모두 몇 개인지 구하시오."
                     % (M("y=") + F(M("a"), M("x")), X, Y), 3, box_h=92, label="풀이", answer_strip=True,
                     ans="(1, −12), (2, −6), (3, −4), (4, −3), (6, −2), (12, −1) / 모두 12개",
                     model=["%s에서 %s가 12의 약수이거나 12의 약수에 −를 붙인 수일 때 %s도 정수이다."
                            % (M("y=-") + F(12, M("x")), X, Y),
                            "제4사분면(%s > 0, %s < 0): %s"
                            % (X, Y, M("(1, -12), (2, -6), (3, -4), (4, -3), (6, -2), (12, -1)")),
                            "제2사분면에도 같은 방법으로 6개가 있으므로 모두 12개이다."],
                     rubric=["제4사분면 위의 점 6개를 모두 쓴 경우 2점 (3~5개를 쓴 경우 1점)",
                             "정수인 점이 모두 12개임을 구한 경우 1점"]),
             ], concept="정비례·반비례 그래프", src="학습지 Ⅲ 서술형 11번 변형"))


def e2_fig():
    be = 10 * math.tan(math.radians(25))
    A, B, C, Dd = (0, 10), (0, 0), (10, 0), (10, 10)
    E, Fp = (be, 0), (10, be)
    P = inter(A, (E[0] - A[0], E[1] - A[1]), B, (Fp[0] - B[0], Fp[1] - B[1]))
    g = Geo({"A": A, "B": B, "C": C, "D": Dd, "E": E, "F": Fp, "P": P}, width=120, pad=12)
    g.path(["A", "B", "C", "D"], close=True)
    g.seg("A", "E")
    g.seg("B", "F")
    g.lab("A", dx=-7, dy=3)
    g.lab("B", dx=-6, dy=-6)
    g.lab("C", dx=6, dy=-6)
    g.lab("D", dx=7, dy=3)
    g.lab("E", dy=-9)
    g.lab("F", dx=7)
    g.lab("P", dx=1, dy=9)
    g.ticks("B", "E", 1)
    g.ticks("C", "F", 1)
    return g.d


ex.add(Essay(2, "그림에서 사각형 ABCD는 정사각형이고, 두 점 E, F는 각각 %s, %s 위의 점으로 %s이다. %s와 %s의 교점을 "
                "P라 할 때, 다음 물음에 답하시오." % (ov("BC"), ov("CD"), ov("BE") + " = " + ov("CF"), ov("AE"), ov("BF")),
             parts=[figure(e2_fig())],
             subs=[
                 Sub("(1) △ABE ≡ △BCF임을 설명하고, 합동 조건을 쓰시오.", 3, box_h=92,
                     ans="SAS 합동",
                     model=["△ABE와 △BCF에서",
                            "%s (정사각형의 변), ∠ABE = ∠BCF = 90°, %s (가정)"
                            % (ov("AB") + " = " + ov("BC"), ov("BE") + " = " + ov("CF")),
                            "두 변의 길이와 그 끼인각의 크기가 각각 같으므로 △ABE ≡ △BCF (SAS 합동)"],
                     rubric=["대응하는 두 변과 끼인각이 같음을 모두 쓴 경우 2점 (하나라도 빠지면 1점)",
                             "SAS 합동을 쓴 경우 1점"]),
                 Sub("(2) ∠BAE = 25°일 때, ∠BFC와 ∠APF의 크기를 각각 구하시오.", 2, box_h=74,
                     label="풀이", answer_strip=True, ans="∠BFC = 65°, ∠APF = 90°",
                     model=["(1)에서 ∠BFC = ∠AEB = 180° − 90° − 25° = 65°",
                            "∠PBE = ∠CBF = ∠BAE = 25°이므로 △PBE에서 ∠BPE = 180° − 25° − 65° = 90°",
                            "∠APF는 ∠BPE의 맞꼭지각이므로 90°이다."],
                     rubric=["∠BFC = 65°를 구한 경우 1점", "∠APF = 90°를 구한 경우 1점"]),
             ], concept="삼각형의 합동", src="학습지 Ⅳ 도전 15번 변형"))

for q in ex.questions():
    if q.kind == "essay":
        q.keep_whole = True

if __name__ == "__main__":
    out = os.path.join(HERE, "..", "..", "out", "2026_2학기_1차", "수학_예상문제_2회_최상위.pdf")
    ex.build(os.path.normpath(out))
    print("저장:", os.path.normpath(out))
