# exam-maker

학교 정기시험 형식(A4 2단)의 예상문제 PDF와 정답·해설 PDF를 만든다.

- `exam_pdf.py`: 생성기 (머리말·쪽 번호·〈보기〉 상자·선지 배치·논술형 답안 칸·정답표)
- `exams/`: 회차별 문제 스크립트. 실행하면 `out/`에 시험지와 `_정답및해설.pdf`가 생긴다.

```bash
pip install reportlab
python exams/<스크립트>.py
```

글꼴은 Windows의 맑은 고딕, 없으면 나눔고딕(`fonts-nanum`)을 쓴다.
