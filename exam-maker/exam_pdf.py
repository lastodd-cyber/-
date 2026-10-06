"""학교 정기시험 형식(A4 2단)의 예상문제 PDF와 정답·해설 PDF를 만드는 생성기.

사용 예 (exams/ 아래 스크립트 참고):

    from exam_pdf import Exam, Q, Essay, Sub, Group, bogi, box, choice_table

    exam = Exam(top="옥길새길중학교 1학년 · 2026학년도 2학기 1차 정기시험 대비",
                title="사회 예상문제 1회",
                expect=dict(mc=22, mc_pts=90, essay=2, essay_pts=10))
    exam.add(Q(1, "다음 설명에 해당하는 개념은? {pts}", pts=4,
               choices=["사회화", "재사회화", ...], ans=1, exp="해설"))
    exam.build("out/사회_1회.pdf")   # 정답·해설 PDF도 함께 생성

문항 텍스트는 ReportLab Paragraph 문법(<b>, <u>, <i>, <sub>, <sup>)을 쓴다.
'<', '>', '&'를 글자로 쓰려면 &lt; &gt; &amp; 로 적는다.
문항 안의 '{pts}' 자리에 배점 "[4점]"이 들어간다. 없으면 발문 끝에 붙는다.
"""
import os
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, KeepTogether,
                                PageBreak, PageTemplate, Paragraph, Spacer,
                                Table, TableStyle)
from reportlab.platypus.doctemplate import FrameBreak

# ---------------------------------------------------------------- 글꼴
_HERE = os.path.dirname(os.path.abspath(__file__))
_FONT_DIRS = [os.path.join(_HERE, "fonts"), "C:/Windows/Fonts",
              "/usr/share/fonts/truetype/nanum",
              "/usr/share/fonts/truetype/liberation"]
_FONT_CHOICES = {
    "KR": ["malgun.ttf", "NanumGothic.ttf"],
    "KR-B": ["malgunbd.ttf", "NanumGothicBold.ttf"],
    "MI": ["timesi.ttf", "LiberationSerif-Italic.ttf"],
    "MR": ["times.ttf", "LiberationSerif-Regular.ttf"],
}


def _find_font(names):
    for name in names:
        for d in _FONT_DIRS:
            path = os.path.join(d, name)
            if os.path.exists(path):
                return path
    raise FileNotFoundError("글꼴을 찾을 수 없습니다: " + ", ".join(names))


for _alias, _names in _FONT_CHOICES.items():
    pdfmetrics.registerFont(TTFont(_alias, _find_font(_names)))
pdfmetrics.registerFontFamily("KR", normal="KR", bold="KR-B",
                              italic="KR", boldItalic="KR-B")
pdfmetrics.registerFontFamily("MR", normal="MR", bold="MR",
                              italic="MI", boldItalic="MI")

# ---------------------------------------------------------------- 치수
PAGE_W, PAGE_H = A4
MARGIN_X = 15 * mm
COL_GAP = 10 * mm
BODY_TOP = PAGE_H - 35 * mm
BODY_BOTTOM = 17 * mm
COL_W = (PAGE_W - 2 * MARGIN_X - COL_GAP) / 2

FS = 9.6          # 본문 글자 크기
LEAD = 14.6       # 본문 줄 간격
GREY = colors.HexColor("#444444")

CIRCLED = "①②③④⑤⑥⑦⑧⑨⑩"

ST_STEM = ParagraphStyle("stem", fontName="KR", fontSize=FS, leading=LEAD)
ST_TEXT = ParagraphStyle("text", parent=ST_STEM)
ST_CHOICE = ParagraphStyle("choice", parent=ST_STEM, leftIndent=12,
                           firstLineIndent=-12)
ST_CELL = ParagraphStyle("cell", parent=ST_STEM, fontSize=FS - 0.6,
                         leading=LEAD - 1.6)
ST_CELL_C = ParagraphStyle("cellc", parent=ST_CELL, alignment=TA_CENTER)
ST_BOX = ParagraphStyle("box", parent=ST_STEM, fontSize=FS - 0.4,
                        leading=LEAD - 0.8)
ST_BOX_ITEM = ParagraphStyle("boxitem", parent=ST_BOX, leftIndent=13,
                             firstLineIndent=-13)
ST_BOX_C = ParagraphStyle("boxc", parent=ST_BOX, alignment=TA_CENTER)

_ITEM_RE = re.compile(r"^\s*([ㄱ-ㅎ]\.|[㉠-㉭㉮-㉻]|\([가-힣A-Za-z0-9]\)|[A-E]\.|[·∙-])\s")


def _strip_tags(text):
    return re.sub(r"<[^>]+>", "", text).replace("&lt;", "<").replace(
        "&gt;", ">").replace("&amp;", "&")


def text_width(text, size=FS):
    return pdfmetrics.stringWidth(_strip_tags(text), "KR", size)


def m(expr):
    """수식 변수용 이탤릭(Times 계열). 예: m('x') + ' + ' + m('y')"""
    return '<font name="MI">%s</font>' % expr


def P(text, style=ST_TEXT):
    return Paragraph(text, style)


# ---------------------------------------------------------------- 상자들
class TitledBox(Flowable):
    """〈보기〉처럼 윗변 가운데에 제목이 걸친 테두리 상자. title=None이면 일반 상자."""

    def __init__(self, content, title="〈보기〉", pad=6, center=False):
        super().__init__()
        self.content = content
        self.title = title
        self.pad = pad
        self.center = center
        self.spaceBefore = 3
        self.spaceAfter = 3

    def _top_extra(self):
        return 6 if self.title else 0

    def wrap(self, aw, ah):
        self.width = aw
        inner = aw - 2 * self.pad - 2
        self._sizes = []
        h = 0
        for f in self.content:
            _, fh = f.wrap(inner, ah)
            self._sizes.append(fh)
            h += fh
        self.height = h + 2 * self.pad + self._top_extra()
        return aw, self.height

    def draw(self):
        c = self.canv
        w, h = self.width, self.height
        top = h - (5 if self.title else 0)
        c.setLineWidth(0.7)
        c.setStrokeColor(colors.black)
        c.line(0, 0, w, 0)
        c.line(0, 0, 0, top)
        c.line(w, 0, w, top)
        if self.title:
            tsize = FS - 0.8
            tw = pdfmetrics.stringWidth(self.title, "KR", tsize)
            cx = w / 2
            c.line(0, top, cx - tw / 2 - 4, top)
            c.line(cx + tw / 2 + 4, top, w, top)
            c.setFont("KR", tsize)
            c.drawCentredString(cx, top - tsize / 2 + 1, self.title)
        else:
            c.line(0, top, w, top)
        y = h - self.pad - self._top_extra()
        for f, fh in zip(self.content, self._sizes):
            y -= fh
            f.drawOn(c, self.pad + 1, y)


class AnswerBox(Flowable):
    """논술형 답안 칸. label은 왼쪽 위 작은 글씨('풀이' 등), answer_strip이면 아래에 '답' 칸."""

    def __init__(self, height, label="풀이", answer_strip=True):
        super().__init__()
        self.box_h = height
        self.label = label
        self.answer_strip = answer_strip
        self.spaceBefore = 4
        self.spaceAfter = 4

    def wrap(self, aw, ah):
        self.width = aw
        self.height = self.box_h
        return aw, self.box_h

    def draw(self):
        c = self.canv
        c.setLineWidth(0.7)
        c.rect(0, 0, self.width, self.box_h)
        c.setFont("KR", 7.5)
        c.setFillColor(GREY)
        if self.label:
            c.drawString(5, self.box_h - 11, self.label)
        if self.answer_strip:
            c.line(0, 20, self.width, 20)
            c.drawString(5, 7, "답")
        c.setFillColor(colors.black)


class _Marker(Flowable):
    """그려질 때 문항 번호를 해당 쪽에 기록한다(머리말의 '선택형 1~5번' 표시용)."""

    def __init__(self, kind, num):
        super().__init__()
        self.kind, self.num = kind, num

    def wrap(self, aw, ah):
        return 0, 0

    def draw(self):
        rec = getattr(self.canv, "_qrecord", None)
        if rec is not None:
            rec.setdefault(self.canv.getPageNumber(), []).append(
                (self.kind, self.num))


def bogi(*lines, title="〈보기〉"):
    """〈보기〉 상자. 'ㄱ. ', '㉠ ', '(가) ' 등으로 시작하는 줄은 내어쓰기."""
    paras = []
    for ln in lines:
        if isinstance(ln, Flowable):
            paras.append(ln)
        elif _ITEM_RE.match(ln):
            paras.append(Paragraph(ln, ST_BOX_ITEM))
        else:
            paras.append(Paragraph(ln, ST_BOX))
    return TitledBox(paras, title=title)


def box(*lines, title=None, center=False):
    """제시문/자료 상자(제목 없는 테두리). title을 주면 '(가)' 같은 제목이 윗변에 걸린다."""
    st = ST_BOX_C if center else ST_BOX
    paras = [ln if isinstance(ln, Flowable) else
             Paragraph(ln, ST_BOX_ITEM if _ITEM_RE.match(ln) else st)
             for ln in lines]
    return TitledBox(paras, title=title)


def data_table(rows, col_widths=None, header=True, width_ratio=1.0,
               align="CENTER", font_size=None):
    """격자 표. rows는 문자열 2차원 리스트. 첫 행은 header=True면 회색 바탕."""
    st = ST_CELL_C if align == "CENTER" else ST_CELL
    if font_size:
        st = ParagraphStyle("cellx", parent=st, fontSize=font_size,
                            leading=font_size + 3.4)
    data = [[c if isinstance(c, Flowable) else Paragraph(str(c), st)
             for c in r] for r in rows]
    total = COL_W * width_ratio
    if col_widths is None:
        ncol = len(rows[0])
        col_widths = [total / ncol] * ncol
    else:
        s = float(sum(col_widths))
        col_widths = [total * w / s for w in col_widths]
    t = Table(data, colWidths=col_widths, hAlign="CENTER")
    style = [
        ("GRID", (0, 0), (-1, -1), 0.6, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDEDED")))
    t.setStyle(TableStyle(style))
    t.spaceBefore = 3
    t.spaceAfter = 3
    return t


def choice_table(headers, rows, width_ratio=0.8, col_widths=None):
    """선지가 표인 문항용: headers=['(가)','(나)'], rows=[('융해','액화'), ...]."""
    data = [[""] + list(headers)]
    for i, r in enumerate(rows):
        data.append([CIRCLED[i]] + list(r))
    if col_widths is None:
        col_widths = [0.6] + [2] * len(headers)
    else:
        col_widths = [0.6] + list(col_widths)
    return data_table(data, col_widths=col_widths, width_ratio=width_ratio)


def figure(drawing):
    """reportlab.graphics Drawing을 가운데 정렬해서 넣는다."""
    t = Table([[drawing]], colWidths=[COL_W])
    t.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"),
                           ("LEFTPADDING", (0, 0), (-1, -1), 0),
                           ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                           ("TOPPADDING", (0, 0), (-1, -1), 3),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    return t


# ---------------------------------------------------------------- 문항
def _choices_flow(choices, layout):
    labelled = ["%s %s" % (CIRCLED[i], c) for i, c in enumerate(choices)]
    if layout == "auto":
        widest = max(text_width(c) for c in labelled) + 8
        n = len(labelled)
        if widest * n <= COL_W:
            layout = "row"
        elif widest * 3 <= COL_W:
            layout = "grid3"
        elif widest * 2 <= COL_W:
            layout = "grid2"
        else:
            layout = "stack"
    if layout == "stack":
        out = [Paragraph(c, ST_CHOICE) for c in labelled]
        for p in out:
            p.spaceBefore = 1.2
        return out
    per_row = {"row": len(labelled), "grid3": 3, "grid2": 2}[layout]
    rows = []
    for i in range(0, len(labelled), per_row):
        cells = [Paragraph(c, ST_CHOICE) for c in labelled[i:i + per_row]]
        cells += [""] * (per_row - len(cells))
        rows.append(cells)
    t = Table(rows, colWidths=[COL_W / per_row] * per_row, hAlign="LEFT")
    t.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0),
                           ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                           ("TOPPADDING", (0, 0), (-1, -1), 1.2),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 1.2),
                           ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    return [t]


def _fill_pts(texts, pts):
    """텍스트 목록에서 첫 '{pts}'를 배점으로 바꾼다. 없으면 첫 텍스트 끝에 붙인다."""
    tag = "[%s점]" % _fmt_pts(pts)
    out, done = [], False
    for t in texts:
        if isinstance(t, str) and "{pts}" in t and not done:
            out.append(t.replace("{pts}", tag))
            done = True
        elif isinstance(t, str):
            out.append(t.replace("{pts}", ""))
        else:
            out.append(t)
    if not done:
        out[0] = out[0] + " " + tag
    return out


def _fmt_pts(p):
    return ("%g" % p)


class Q:
    """선택형 문항.

    stem: 발문(첫 문단). parts: 발문 뒤에 올 자료(문자열이면 문단, 그 밖엔 flowable).
    choices: 선지 5개(문자열). layout: auto|stack|row|grid3|grid2.
    choice_tbl: choice_table(...)로 만든 표를 선지 대신 쓸 때.
    ans: 정답 번호(1~5, 복수 정답이면 튜플). exp: 해설(문자열 또는 줄 목록).
    concept: 핵심 개념. ans_text: 정답지에 쓸 정답 내용(없으면 선지 문장).
    src: 출제 근거.
    """

    kind = "mc"

    def __init__(self, num, stem, pts, choices=None, ans=None, exp="",
                 parts=(), layout="auto", choice_tbl=None, src="",
                 concept="", ans_text=None):
        self.num, self.stem, self.pts = num, stem, pts
        self.choices, self.ans, self.exp = choices, ans, exp
        self.parts, self.layout, self.choice_tbl = list(parts), layout, choice_tbl
        self.src, self.concept, self.ans_text = src, concept, ans_text

    def flowables(self):
        texts = _fill_pts([self.stem] + self.parts, self.pts)
        body = [_Marker(self.kind, self.num)]
        first = True
        for t in texts:
            if isinstance(t, str):
                txt = ("<b>%s.</b> %s" % (self.num, t)) if first else t
                p = Paragraph(txt, ST_STEM)
                if not first:
                    p.spaceBefore = 3
                body.append(p)
            else:
                body.append(t)
            first = False
        if self.choice_tbl is not None:
            body.append(self.choice_tbl)
        elif self.choices:
            body.append(Spacer(1, 2.5))
            body.extend(_choices_flow(self.choices, self.layout))
        return [KeepTogether(body), Spacer(1, 15)]


class Sub:
    """논술형의 소문항. box_h: 답안 칸 높이(pt).

    ans: 짧은 답(빠른 정답용), model: 모범 답안(문자열 또는 줄 목록),
    rubric: 채점 기준 문장 목록.
    """

    def __init__(self, text, pts, box_h=90, ans="", label=None,
                 answer_strip=False, parts=(), model=(), rubric=()):
        self.text, self.pts, self.box_h, self.ans = text, pts, box_h, ans
        self.label, self.answer_strip, self.parts = label, answer_strip, list(parts)
        self.model = [model] if isinstance(model, str) else list(model)
        self.rubric = list(rubric)


class Essay:
    """논술형 문항. subs가 없으면 box_h 크기의 답안 칸 하나.

    ans: 짧은 답, model: 모범 답안, rubric: 채점 기준 문장 목록
    """

    kind = "essay"

    def __init__(self, num, stem, pts=None, parts=(), subs=(), box_h=120,
                 label=None, answer_strip=False, ans="", rubric=(), src="",
                 model=(), concept=""):
        self.num, self.stem, self.parts = num, stem, list(parts)
        self.subs = list(subs)
        self.pts = pts if pts is not None else sum(s.pts for s in self.subs)
        self.box_h, self.label, self.answer_strip = box_h, label, answer_strip
        self.ans, self.rubric, self.src = ans, list(rubric), src
        self.model = [model] if isinstance(model, str) else list(model)
        self.concept = concept

    def flowables(self):
        head = [_Marker(self.kind, self.num)]
        texts = _fill_pts([self.stem] + self.parts, self.pts)
        first = True
        for t in texts:
            if isinstance(t, str):
                txt = ("<b>논술형 %s.</b> %s" % (self.num, t)) if first else t
                p = Paragraph(txt, ST_STEM)
                if not first:
                    p.spaceBefore = 3
                head.append(p)
            else:
                head.append(t)
            first = False
        out = []
        if not self.subs:
            head.append(AnswerBox(self.box_h, self.label, self.answer_strip))
            out.append(KeepTogether(head))
        else:
            out.append(KeepTogether(head))
            for s in self.subs:
                blk = [Spacer(1, 4),
                       Paragraph("%s [%s점]" % (s.text, _fmt_pts(s.pts)),
                                 ParagraphStyle("sub", parent=ST_STEM,
                                                leftIndent=14,
                                                firstLineIndent=-14))]
                blk.extend(s.parts)
                blk.append(AnswerBox(s.box_h, s.label, s.answer_strip))
                out.append(KeepTogether(blk))
        if getattr(self, "keep_whole", False):
            whole = []
            for f in out:
                whole.extend(f._content if isinstance(f, KeepTogether) else [f])
            out = [KeepTogether(whole)]
        out.append(Spacer(1, 15))
        return out


class Group:
    """[3~4] 공통 자료 묶음. header + parts(자료)를 첫 문항과 붙여서 배치한다."""

    def __init__(self, header, parts, questions):
        self.header, self.parts, self.questions = header, list(parts), list(questions)

    def flowables(self):
        lead = [Paragraph(self.header, ST_STEM), Spacer(1, 2)] + self.parts + [Spacer(1, 6)]
        first = self.questions[0].flowables()
        # KeepTogether를 겹쳐 넣으면 높이가 무한대로 계산되어 항상 다음 단으로 밀리므로 내용만 꺼내 합친다
        head = first[0]
        inner = list(head._content) if isinstance(head, KeepTogether) else [head]
        out = [KeepTogether(lead + inner)] + first[1:]
        for q in self.questions[1:]:
            out.extend(q.flowables())
        return out


class _ColumnBreak:
    pass


COLUMN_BREAK = _ColumnBreak()
PAGE_BREAK = PageBreak()


# ---------------------------------------------------------------- 시험지
class Exam:
    def __init__(self, top, title, footer=None, expect=None,
                 essay_new_page=True, mc_label="선택형", essay_label="논술형",
                 check_total=True):
        self.top, self.title = top, title
        self.check_total = check_total
        self.footer = footer or ("가정통신문 시험 범위·교과서·학습지를 바탕으로 만든 "
                                 "자체 예상문제 · 학교 공식 시험지가 아님")
        self.expect = expect
        self.essay_new_page = essay_new_page
        self.mc_label, self.essay_label = mc_label, essay_label
        self.items = []

    def add(self, *items):
        self.items.extend(items)

    # 문항 목록 펼치기
    def questions(self):
        out = []
        for it in self.items:
            if isinstance(it, Group):
                out.extend(it.questions)
            elif isinstance(it, (Q, Essay)):
                out.append(it)
        return out

    def summary(self):
        qs = self.questions()
        mc = [q for q in qs if q.kind == "mc"]
        es = [q for q in qs if q.kind == "essay"]
        return dict(mc=len(mc), mc_pts=sum(q.pts for q in mc),
                    essay=len(es), essay_pts=sum(q.pts for q in es))

    def check(self):
        s = self.summary()
        msgs = []
        total = s["mc_pts"] + s["essay_pts"]
        if self.check_total and abs(total - 100) > 1e-6:
            msgs.append("총점이 100점이 아닙니다: %g점" % total)
        if self.expect:
            for k, v in self.expect.items():
                if abs(s[k] - v) > 1e-6:
                    msgs.append("%s: 예상 %g, 실제 %g" % (k, v, s[k]))
        for q in self.questions():
            if q.kind == "mc":
                if q.ans is None:
                    msgs.append("%s번 정답 없음" % q.num)
                if q.choices and len(q.choices) != 5:
                    msgs.append("%s번 선지 %d개" % (q.num, len(q.choices)))
        nums = [q.num for q in self.questions() if q.kind == "mc"]
        if nums != list(range(1, len(nums) + 1)):
            msgs.append("선택형 번호가 1부터 연속이 아닙니다: %s" % nums)
        return msgs

    def _summary_text(self):
        s = self.summary()
        parts = []
        if s["mc"]:
            parts.append("%s %d문항 %g점" % (self.mc_label, s["mc"], s["mc_pts"]))
        if s["essay"]:
            parts.append("%s %d문항 %g점" % (self.essay_label, s["essay"], s["essay_pts"]))
        return ", ".join(parts)

    def build(self, path, key=True):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        story = []
        essay_started = False
        for it in self.items:
            if it is COLUMN_BREAK:
                story.append(FrameBreak())
                continue
            if isinstance(it, PageBreak):
                story.append(it)
                continue
            if (self.essay_new_page and not essay_started
                    and isinstance(it, Essay)):
                story.append(PageBreak())
            if isinstance(it, Essay):
                essay_started = True
            story.extend(it.flowables())

        exam = self
        record = {}

        class _Canvas(rl_canvas.Canvas):
            def __init__(self, *a, **k):
                super().__init__(*a, **k)
                self._pages = []
                self._qrecord = record

            def showPage(self):
                self._pages.append(dict(self.__dict__))
                self._startPage()

            def save(self):
                n = len(self._pages)
                for i, state in enumerate(self._pages, start=1):
                    self.__dict__.update(state)
                    exam._draw_page(self, i, n, record.get(i, []))
                    super().showPage()
                super().save()

        doc = BaseDocTemplate(path, pagesize=A4, title="%s (%s)" % (self.title, self.top),
                              author="자체 제작", leftMargin=MARGIN_X,
                              rightMargin=MARGIN_X, topMargin=PAGE_H - BODY_TOP,
                              bottomMargin=BODY_BOTTOM)
        fh = BODY_TOP - BODY_BOTTOM
        frames = [Frame(MARGIN_X, BODY_BOTTOM, COL_W, fh, id="L",
                        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0),
                  Frame(MARGIN_X + COL_W + COL_GAP, BODY_BOTTOM, COL_W, fh, id="R",
                        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)]
        doc.addPageTemplates([PageTemplate(id="two", frames=frames)])
        doc.build(story, canvasmaker=_Canvas)
        for msg in self.check():
            print("[확인 필요]", msg)
        if key:
            root, ext = os.path.splitext(path)
            build_key(self, root + "_정답및해설" + ext)
        return path

    def _range_text(self, recs):
        parts = []
        for kind, label in (("mc", self.mc_label), ("essay", self.essay_label)):
            nums = [n for k, n in recs if k == kind]
            if nums:
                a, b = min(nums), max(nums)
                parts.append("%s %s번" % (label, a if a == b else "%s~%s" % (a, b)))
        return ", ".join(parts)

    def _draw_page(self, c, page, total, recs):
        c.saveState()
        c.setFillColor(colors.black)
        c.setFont("KR", 8.5)
        c.drawString(MARGIN_X, PAGE_H - 14 * mm, self.top)
        c.setFont("KR-B", 17)
        c.drawString(MARGIN_X, PAGE_H - 23.5 * mm, self.title)
        c.setFont("KR", 8)
        sub = self._range_text(recs)
        sub = (sub + " · " if sub else "") + self._summary_text()
        c.drawString(MARGIN_X, PAGE_H - 30 * mm, sub)
        c.drawString(PAGE_W / 2 + COL_GAP / 2, PAGE_H - 30 * mm,
                     "반: ______ 번호: ______ 이름: ______________")
        c.setLineWidth(0.9)
        c.line(MARGIN_X, PAGE_H - 32 * mm, PAGE_W - MARGIN_X, PAGE_H - 32 * mm)
        c.setLineWidth(0.6)
        x = PAGE_W / 2
        c.line(x, BODY_TOP + 1 * mm, x, BODY_BOTTOM - 2 * mm)
        c.setFont("KR", 6.8)
        c.setFillColor(GREY)
        c.drawString(MARGIN_X, 9 * mm, self.footer)
        c.drawRightString(PAGE_W - MARGIN_X, 9 * mm, "%d / %d" % (page, total))
        c.restoreState()


# ---------------------------------------------------------------- 정답·해설
def _lines(x):
    if not x:
        return []
    return [x] if isinstance(x, str) else list(x)


class _SectionBar(Flowable):
    """회색 바탕의 구역 제목 줄('빠른 정답', '객관식 풀이' 등)."""

    def __init__(self, text):
        super().__init__()
        self.text = text
        self.spaceBefore = 10
        self.spaceAfter = 6

    def wrap(self, aw, ah):
        self.width = aw
        return aw, 19

    def draw(self):
        c = self.canv
        c.setFillColor(colors.HexColor("#E6E6E6"))
        c.rect(0, 0, self.width, 19, stroke=0, fill=1)
        c.setFillColor(colors.black)
        c.setFont("KR-B", 9.6)
        c.drawString(10, 6, self.text)


def build_key(exam, path, footer=None):
    from reportlab.platypus import SimpleDocTemplate

    footer = footer or "자체 제작 예상문제의 정답 · 학교 공식 정답이 아님"
    st_q = ParagraphStyle("kq", fontName="KR", fontSize=9.2, leading=13.6,
                          spaceBefore=7)
    st_p = ParagraphStyle("kp", fontName="KR", fontSize=8.9, leading=13,
                          leftIndent=12)
    st_label = ParagraphStyle("kl", fontName="KR-B", fontSize=8.9, leading=13,
                              leftIndent=12, spaceBefore=2)
    st_p2 = ParagraphStyle("kp2", parent=st_p, leftIndent=22)
    st_note = ParagraphStyle("kn", fontName="KR", fontSize=8.9, leading=13)
    st_quick = ParagraphStyle("kqk", fontName="KR", fontSize=8.9, leading=13,
                              leftIndent=48, firstLineIndent=-48, spaceBefore=2)
    st_c = ParagraphStyle("kc", fontName="KR", fontSize=9.2, leading=12,
                          alignment=TA_CENTER)

    qs = exam.questions()
    mcs = [q for q in qs if q.kind == "mc"]
    ess = [q for q in qs if q.kind == "essay"]

    def ans_mark(a):
        if isinstance(a, (tuple, list)):
            return ", ".join(CIRCLED[i - 1] for i in a)
        return CIRCLED[a - 1] if isinstance(a, int) else str(a)

    def ans_text(q):
        if q.ans_text is not None:
            return q.ans_text
        if q.choices and isinstance(q.ans, int):
            return _strip_tags(q.choices[q.ans - 1])
        return ""

    story = [_SectionBar("빠른 정답")]
    per_row = 11
    rows, style = [], [("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                       ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                       ("TOPPADDING", (0, 0), (-1, -1), 3),
                       ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5)]
    for i in range(0, len(mcs), per_row):
        chunk = mcs[i:i + per_row]
        rows.append([Paragraph(str(q.num), st_c) for q in chunk] + [""] * (per_row - len(chunk)))
        rows.append([Paragraph(ans_mark(q.ans), st_c) for q in chunk] + [""] * (per_row - len(chunk)))
        if len(chunk) < per_row:
            r = len(rows)
            style.append(("GRID", (len(chunk), r - 2), (-1, r - 1), 0, colors.white))
            style.append(("LINEBEFORE", (len(chunk), r - 2), (len(chunk), r - 1), 0.5, colors.black))
    if rows:
        w = PAGE_W - 2 * MARGIN_X
        t = Table(rows, colWidths=[w / per_row] * per_row)
        t.setStyle(TableStyle(style))
        story.append(t)
    story.append(Spacer(1, 7))
    for q in ess:
        if q.subs:
            quick = " ".join("%s %s" % (_sub_tag(q.num, s), s.ans) for s in q.subs)
        else:
            quick = q.ans
        story.append(Paragraph("<b>논술형 %s</b>&nbsp;&nbsp;%s" % (q.num, quick), st_quick))

    if mcs:
        story.append(_SectionBar("객관식 풀이"))
    for q in mcs:
        head = "<b>%s.</b> 정답 %s %s · [%s점]" % (q.num, ans_mark(q.ans), ans_text(q),
                                              _fmt_pts(q.pts))
        if q.concept:
            head += " 핵심 개념: " + q.concept
        blk = [Paragraph(head, st_q)]
        blk += [Paragraph(ln, st_p) for ln in _lines(q.exp)]
        if q.src:
            blk.append(Paragraph("<font color='#666666'>출제 근거: %s</font>" % q.src, st_p))
        story.append(KeepTogether(blk))

    for q in ess:
        story.append(_SectionBar("논술형 %s 모범 답안과 채점 기준 (예시)" % q.num))
        story.append(Paragraph("학교의 실제 채점 기준은 확인하지 못했으므로, 배점에 맞춘 예시 기준이다.", st_note))
        parts = q.subs if q.subs else [q]
        for s in parts:
            tag = _sub_tag(q.num, s) if q.subs else "%s" % q.num
            blk = [Paragraph("<b>%s</b> 답: %s · [%s점]" % (tag, s.ans, _fmt_pts(s.pts)), st_q)]
            if s.model:
                blk.append(Paragraph("모범 답안", st_label))
                blk += [Paragraph(ln, st_p2) for ln in s.model]
            if s.rubric:
                blk.append(Paragraph("채점 기준", st_label))
                for r in s.rubric:
                    if isinstance(r, (tuple, list)):
                        r = "%s %s점" % (r[0], _fmt_pts(r[1]))
                    blk.append(Paragraph("· " + r, st_p2))
            story.append(KeepTogether(blk))
        if q.src:
            story.append(Paragraph("<font color='#666666'>출제 근거: %s</font>" % q.src, st_p))

    title = exam.title + " 정답 및 해설"

    def on_page(c, doc):
        c.saveState()
        c.setFont("KR", 8.5)
        c.drawString(MARGIN_X, PAGE_H - 14 * mm, exam.top)
        c.setFont("KR-B", 15)
        c.drawString(MARGIN_X, PAGE_H - 22.5 * mm, title)
        c.setLineWidth(0.9)
        c.line(MARGIN_X, PAGE_H - 26 * mm, PAGE_W - MARGIN_X, PAGE_H - 26 * mm)
        c.setFont("KR", 6.8)
        c.setFillColor(GREY)
        c.drawString(MARGIN_X, 9 * mm, footer)
        c.drawRightString(PAGE_W - MARGIN_X, 9 * mm, str(doc.page))
        c.restoreState()

    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=MARGIN_X,
                            rightMargin=MARGIN_X, topMargin=30 * mm,
                            bottomMargin=17 * mm, title=title)
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    return path


def _sub_tag(num, sub):
    """'(1) ...' 형식의 소문항에서 '1-1' 같은 꼬리표를 만든다."""
    mt = re.match(r"\s*\((\d+)\)", sub.text)
    return "%s-%s" % (num, mt.group(1)) if mt else str(num)
