#!/usr/bin/env python3
"""Build the public A4 portfolio PDF from the current case-study facts."""

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "Jeongmin-Koo-Portfolio.pdf"
FONT = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
W, H = A4
M = 42

PAPER = colors.HexColor("#F6F3EC")
WHITE = colors.HexColor("#FFFEFA")
INK = colors.HexColor("#101C2D")
SOFT = colors.HexColor("#45546A")
LINE = colors.HexColor("#C8C4B9")
BLUE = colors.HexColor("#315CFF")
CYAN = colors.HexColor("#19C7D8")
NAVY = colors.HexColor("#071321")
PALE_BLUE = colors.HexColor("#E9EEFF")
GREEN = colors.HexColor("#1C755C")
AMBER = colors.HexColor("#A86513")
RED = colors.HexColor("#A33C43")

PORTFOLIO_URL = "https://zionkoo.github.io/portfolio/"
STRION_URL = "https://zionkoo.github.io/strion-running-dashboard/"
SMART_FARM_URL = "https://zionkoo.github.io/smartfarm-dashboard/"
EMAIL_URL = "mailto:zionkoo@kakao.com"

pdfmetrics.registerFont(TTFont("Korean", FONT))
pdfmetrics.registerFont(TTFont("KoreanBold", FONT_BOLD))


def style(size=10, leading=None, color=INK, bold=False, align=TA_LEFT):
    return ParagraphStyle(
        name=f"s-{size}-{bold}-{color}",
        fontName="KoreanBold" if bold else "Korean",
        fontSize=size,
        leading=leading or size * 1.55,
        textColor=color,
        alignment=align,
        wordWrap="CJK",
        spaceAfter=0,
    )


def para(c, text, x, y_top, width, size=10, leading=None, color=INK, bold=False, max_height=300):
    p = Paragraph(text, style(size, leading, color, bold))
    _, height = p.wrap(width, max_height)
    p.drawOn(c, x, y_top - height)
    return height


def bg(c, dark=False):
    c.setFillColor(NAVY if dark else PAPER)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor("#193140") if dark else colors.HexColor("#E7E3D8"))
    c.setLineWidth(.25)
    for x in range(0, int(W) + 1, 28):
        c.line(x, 0, x, H)
    for y in range(0, int(H) + 1, 28):
        c.line(0, y, W, y)


def page_header(c, section, page, dark=False):
    color = CYAN if dark else BLUE
    c.setFont("KoreanBold", 8)
    c.setFillColor(color)
    c.drawString(M, H - 28, section.upper())
    c.setFillColor(colors.HexColor("#8494A0") if dark else SOFT)
    c.drawRightString(W - M, H - 28, f"KOO JEONGMIN  /  {page:02d}")
    c.setStrokeColor(colors.HexColor("#294758") if dark else LINE)
    c.line(M, H - 36, W - M, H - 36)


def title(c, eyebrow, heading, subtitle=None, dark=False):
    color = CYAN if dark else BLUE
    c.setFont("KoreanBold", 9)
    c.setFillColor(color)
    c.drawString(M, H - 70, eyebrow.upper())
    h = para(c, heading, M, H - 90, W - 2 * M, 24, 31, WHITE if dark else INK, True, 120)
    y = H - 98 - h
    if subtitle:
        h2 = para(c, subtitle, M, y, W - 2 * M, 10.5, 17, colors.HexColor("#AEBCCA") if dark else SOFT, False, 90)
        y -= h2 + 10
    return y


def rounded(c, x, y, w, h, fill=WHITE, stroke=LINE, radius=12, line=1):
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(line)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)


def pill(c, text, x, y, fill, color=WHITE):
    width = max(58, pdfmetrics.stringWidth(text, "KoreanBold", 8) + 22)
    c.setFillColor(fill)
    c.roundRect(x, y, width, 22, 11, fill=1, stroke=0)
    c.setFillColor(color)
    c.setFont("KoreanBold", 8)
    c.drawCentredString(x + width / 2, y + 7, text)
    return width


def link_region(c, url, x, y, width, height):
    c.linkURL(url, (x, y, x + width, y + height), relative=0, thickness=0)


def metric(c, x, y, w, label, value, dark=False):
    rounded(c, x, y, w, 58, colors.HexColor("#0B1B2A") if dark else WHITE, colors.HexColor("#315267") if dark else LINE, 10)
    c.setFillColor(CYAN if dark else BLUE)
    c.setFont("KoreanBold", 7)
    c.drawString(x + 12, y + 39, label.upper())
    c.setFillColor(WHITE if dark else INK)
    c.setFont("KoreanBold", 16)
    c.drawString(x + 12, y + 14, value)


def image_cover(c, path, x, y, w, h, radius=12):
    from PIL import Image
    im = Image.open(path).convert("RGB")
    src_ratio = im.width / im.height
    target_ratio = w / h
    if src_ratio > target_ratio:
        new_w = int(im.height * target_ratio)
        left = (im.width - new_w) // 2
        im = im.crop((left, 0, left + new_w, im.height))
    else:
        new_h = int(im.width / target_ratio)
        top = (im.height - new_h) // 2
        im = im.crop((0, top, im.width, top + new_h))
    import io
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=88)
    buf.seek(0)
    c.saveState()
    p = c.beginPath()
    p.roundRect(x, y, w, h, radius)
    c.clipPath(p, stroke=0, fill=0)
    c.drawImage(ImageReader(buf), x, y, w, h, preserveAspectRatio=False, mask="auto")
    c.restoreState()


def draw_symbol(c, x, y, scale=1.0, dark=False):
    # Same four-stage connected-flow geometry used by the web SVG.
    nodes = [(0, 0), (52, 22), (112, 58), (180, 96)]
    c.setLineCap(1)
    c.setLineJoin(1)
    c.setStrokeColor(BLUE)
    c.setLineWidth(7 * scale)
    p = c.beginPath()
    p.moveTo(x, y)
    p.curveTo(x + 25 * scale, y, x + 27 * scale, y + 22 * scale, x + 52 * scale, y + 22 * scale)
    p.curveTo(x + 82 * scale, y + 22 * scale, x + 82 * scale, y + 58 * scale, x + 112 * scale, y + 58 * scale)
    p.curveTo(x + 148 * scale, y + 58 * scale, x + 144 * scale, y + 96 * scale, x + 180 * scale, y + 96 * scale)
    c.drawPath(p, fill=0, stroke=1)
    node_colors = [INK if not dark else WHITE, BLUE, BLUE, CYAN]
    for idx, (nx, ny) in enumerate(nodes):
        c.setFillColor(NAVY if dark else PAPER)
        c.setStrokeColor(node_colors[idx])
        c.setLineWidth(4 * scale)
        c.roundRect(x + nx * scale - 13 * scale, y + ny * scale - 13 * scale, 26 * scale, 26 * scale, 7 * scale, fill=1, stroke=1)
    c.setStrokeColor(CYAN)
    c.setLineWidth(3 * scale)
    c.line(x + 173 * scale, y + 96 * scale, x + 179 * scale, y + 90 * scale)
    c.line(x + 179 * scale, y + 90 * scale, x + 188 * scale, y + 104 * scale)


def bullet_list(c, items, x, y_top, width, size=10, color=INK, bullet_color=BLUE, gap=8):
    y = y_top
    for item in items:
        c.setFillColor(bullet_color)
        c.circle(x + 4, y - 7, 2.4, fill=1, stroke=0)
        h = para(c, escape(item), x + 16, y, width - 16, size, size * 1.55, color, False, 100)
        y -= h + gap
    return y


def table(c, rows, x, y_top, widths, row_h=40, dark=False, header=True):
    y = y_top
    total = sum(widths)
    for r_idx, row in enumerate(rows):
        fill = colors.HexColor("#102433") if dark and r_idx % 2 else (colors.HexColor("#0B1B2A") if dark else (PALE_BLUE if r_idx == 0 and header else WHITE))
        c.setFillColor(fill)
        c.setStrokeColor(colors.HexColor("#294758") if dark else LINE)
        c.rect(x, y - row_h, total, row_h, fill=1, stroke=1)
        cx = x
        for idx, cell in enumerate(row):
            if idx:
                c.line(cx, y - row_h, cx, y)
            para(c, escape(str(cell)), cx + 8, y - 10, widths[idx] - 16, 8.2, 11.5, WHITE if dark else INK, r_idx == 0 and header, row_h - 8)
            cx += widths[idx]
        y -= row_h
    return y


def footer(c, page, dark=False):
    c.setStrokeColor(colors.HexColor("#294758") if dark else LINE)
    c.line(M, 30, W - M, 30)
    c.setFillColor(colors.HexColor("#82929F") if dark else SOFT)
    c.setFont("Korean", 7.5)
    c.drawString(M, 18, "SERVICE PLANNING PORTFOLIO")
    c.drawRightString(W - M, 18, f"{page:02d} / 12")


def page_cover(c):
    bg(c, True)
    draw_symbol(c, 352, 594, 1.0, True)
    c.setFillColor(CYAN)
    c.setFont("KoreanBold", 10)
    c.drawString(M, H - 68, "SERVICE PLANNING PORTFOLIO")
    para(c, "운영에서 발견한 문제를,<br/>사용 가능한 서비스로 설계합니다.", M, H - 134, 455, 30, 41, WHITE, True, 150)
    para(c, "온라인 MD·상품기획·사업운영·유통·물류에서 사용자와 운영의 흐름을 익히고, 이를 요구사항과 사용자 흐름으로 구체화했습니다.", M, H - 260, 430, 12, 20, colors.HexColor("#B4C2CC"), False, 120)
    c.setStrokeColor(CYAN)
    c.setLineWidth(3)
    c.line(M, 220, W - M, 220)
    c.setFillColor(WHITE)
    c.setFont("KoreanBold", 17)
    c.drawString(M, 176, "KOO JEONGMIN")
    c.setFillColor(CYAN)
    c.setFont("KoreanBold", 9)
    c.drawString(M, 152, "PROBLEM / PRODUCT / PROOF")
    c.setFillColor(colors.HexColor("#B4C2CC"))
    c.setFont("Korean", 9)
    c.drawString(M, 116, "zionkoo.github.io/portfolio/")
    c.drawString(M, 96, "zionkoo@kakao.com")
    link_region(c, PORTFOLIO_URL, M, 108, 180, 18)
    link_region(c, EMAIL_URL, M, 88, 150, 18)
    c.setFillColor(colors.HexColor("#6D8290"))
    c.drawRightString(W - M, 96, "2026.10")
    footer(c, 1, True)
    c.showPage()


def page_intro(c):
    bg(c)
    page_header(c, "Profile & Contents", 2)
    y = title(c, "Positioning", "사용자와 운영의 흐름을 이해하고, 서비스 요구사항으로 구체화합니다")
    rounded(c, M, y - 118, W - 2 * M, 106, WHITE, LINE, 16)
    para(c, "상품기획과 사업운영에서 고객 요구, 일정, 인력, 정보, 정산을 조율했습니다. 개발자나 전문 PM 경력을 주장하기보다, 관심 있는 문제를 직접 정의하고 AI 도구로 구현을 가속한 뒤 실제 데이터와 장치로 결과를 검증한 경험을 보여드립니다.", M + 20, y - 34, W - 2 * M - 40, 11, 18, INK, False, 80)
    c.setFont("KoreanBold", 12)
    c.setFillColor(INK)
    c.drawString(M, y - 156, "CONTENTS")
    rows = [
        ("01", "STRION", "FIT 분석 · Garmin 동기화 · 기록 재열람 · 레이스 계획", "03-07"),
        ("02", "SMART FARM", "DHT11 · MQTT · Node-RED · Telegram · LED 원격 제어", "08-11"),
        ("03", "PROFILE", "경력 · AI 협업 방식 · 연락처", "12"),
    ]
    y2 = y - 184
    for no, name, desc, pages in rows:
        c.setStrokeColor(LINE)
        c.line(M, y2, W - M, y2)
        c.setFillColor(BLUE)
        c.setFont("KoreanBold", 10)
        c.drawString(M, y2 - 26, no)
        c.setFillColor(INK)
        c.setFont("KoreanBold", 15)
        c.drawString(M + 50, y2 - 28, name)
        para(c, desc, M + 165, y2 - 16, 280, 9, 14, SOFT, False, 45)
        c.setFont("KoreanBold", 9)
        c.setFillColor(SOFT)
        c.drawRightString(W - M, y2 - 28, pages)
        y2 -= 72
    c.line(M, y2, W - M, y2)
    draw_symbol(c, M + 10, 88, .72)
    para(c, "문제 발견 → 요구사항·사용 흐름 설계 → 서비스 구체화 → 실제 결과 검증", M + 180, 155, W - M - (M + 180), 10, 16, INK, True, 70)
    footer(c, 2)
    c.showPage()


def page_strion_overview(c):
    bg(c, True)
    page_header(c, "Project 01 · STRION", 3, True)
    y = title(c, "01 · Problem & Service", "원본 러닝 데이터를 다음 행동으로 연결합니다", "FIT 파일을 매번 내려받아 재업로드하는 불편과 흩어진 기록·계획 흐름을 하나의 서비스로 묶었습니다.", True)
    image_cover(c, ROOT / "assets" / "strion-live.png", M, 340, W - 2 * M, 205, 14)
    c.setFillColor(colors.Color(0, 0, 0, alpha=.45))
    c.roundRect(M, 340, W - 2 * M, 205, 14, fill=1, stroke=0)
    metric(c, M + 18, 360, 145, "Input", "Garmin FIT", True)
    metric(c, M + 176, 360, 145, "Process", "분석·비교", True)
    metric(c, M + 334, 360, 145, "Output", "다음 계획", True)
    para(c, "사용자 문제", M, 314, 120, 12, 17, CYAN, True)
    bullet_list(c, ["운동 기록을 볼 때마다 FIT 파일을 다시 내려받고 업로드해야 함", "거리·페이스·심박·러닝 다이내믹스가 흩어져 있어 한 번에 해석하기 어려움", "분석 결과가 다음 훈련과 레이스 운영으로 자연스럽게 이어지지 않음"], M, 288, W - 2 * M, 9.5, WHITE, CYAN, 7)
    footer(c, 3, True)
    c.showPage()


def page_strion_flow(c):
    bg(c)
    page_header(c, "Project 01 · STRION", 4)
    y = title(c, "02 · User Flow & Requirements", "업로드에서 분석, 저장, 다음 계획까지 한 흐름으로 설계했습니다")
    steps = ["FIT 업로드\n또는 동기화", "원본 파싱", "기록 분석", "브라우저 저장", "훈련·레이스\n계획"]
    x = M
    sw = 92
    gap = 12
    for i, step in enumerate(steps):
        rounded(c, x, y - 80, sw, 62, PALE_BLUE if i in (0, 4) else WHITE, BLUE if i in (0, 4) else LINE, 12)
        para(c, step.replace("\n", "<br/>"), x + 9, y - 36, sw - 18, 8.4, 12, INK, True, 48)
        if i < len(steps) - 1:
            c.setFillColor(BLUE)
            c.setFont("KoreanBold", 12)
            c.drawString(x + sw + 2, y - 51, "→")
        x += sw + gap
    c.setFont("KoreanBold", 12)
    c.setFillColor(INK)
    c.drawString(M, y - 122, "핵심 기능 요구사항")
    reqs = [
        ("FR-01", "FIT 입력", "파일 업로드 및 Garmin 개인 동기화 경로 제공"),
        ("FR-02", "기록 분석", "거리·시간·페이스·심박·고도·러닝 다이내믹스 표시"),
        ("FR-03", "기록 재열람", "브라우저에 저장한 기록을 날짜로 다시 선택"),
        ("FR-04", "심박 Zone", "Garmin 개인 설정 경계와 구간별 시간을 반영"),
        ("FR-05", "계획 연결", "PB·대회 일정·목표 기록·km별 페이스 전략 생성"),
        ("FR-06", "공유", "사진·영상 위에 핵심 기록을 합성해 저장·공유"),
    ]
    table(c, [("ID", "기능", "설명")] + reqs, M, y - 142, [58, 108, W - 2 * M - 166], 43)
    footer(c, 4)
    c.showPage()


def page_strion_sync(c):
    bg(c, True)
    page_header(c, "Project 01 · STRION", 5, True)
    y = title(c, "03 · Garmin Sync", "불편을 줄이되, 개인 연동의 범위를 과장하지 않았습니다", "개인 API 키가 브라우저에 노출되지 않도록 Cloudflare Worker를 중계 계층으로 사용했습니다.", True)
    nodes = [("Garmin Connect", "개인 기록"), ("Cloudflare Worker", "키 보호·중계"), ("STRION", "분석·저장")]
    x = M
    for i, (name, sub) in enumerate(nodes):
        rounded(c, x, y - 94, 145, 76, colors.HexColor("#0B1B2A"), colors.HexColor("#315267"), 12)
        para(c, name, x + 12, y - 44, 121, 10, 14, WHITE, True, 28)
        para(c, sub, x + 12, y - 65, 121, 8, 11, colors.HexColor("#9EB0BD"), False, 20)
        if i < 2:
            c.setFillColor(CYAN)
            c.setFont("KoreanBold", 14)
            c.drawString(x + 153, y - 63, "→")
        x += 172
    c.setFont("KoreanBold", 12)
    c.setFillColor(WHITE)
    c.drawString(M, y - 138, "실제 구현 범위")
    bullet_list(c, ["개인 API 키를 사용한 본인 계정 기록 동기화", "월 단위 기록 가져오기와 브라우저 내 저장·재열람", "FIT 원본과 Garmin 화면을 대조한 단위·경계값 검증"], M, y - 162, W - 2 * M, 9.5, WHITE, CYAN, 8)
    c.setFont("KoreanBold", 12)
    c.setFillColor(WHITE)
    c.drawString(M, y - 288, "제한과 향후 확장")
    rounded(c, M, y - 410, W - 2 * M, 102, colors.HexColor("#102433"), colors.HexColor("#315267"), 12)
    para(c, "현재는 공식 Garmin 다중 사용자 OAuth 연동이 아닙니다. 개인 계정용 동기화 경로이며, 여러 사용자가 자신의 계정을 안전하게 연결하는 상용 구조에는 정식 파트너 API, 사용자 인증, 서버 저장 정책과 동의 절차가 추가로 필요합니다.", M + 18, y - 332, W - 2 * M - 36, 10, 16, colors.HexColor("#C0CCD5"), False, 78)
    footer(c, 5, True)
    c.showPage()


def page_strion_validation(c):
    bg(c)
    page_header(c, "Project 01 · STRION", 6)
    y = title(c, "04 · Validation", "원본 데이터와 Garmin 화면을 기준으로 파싱 결과를 대조했습니다")
    image_cover(c, ROOT / "assets" / "strion-run-share-card.png", M, 390, 190, 240, 14)
    x = M + 212
    para(c, "검증한 항목", x, 620, W - M - x, 12, 17, BLUE, True)
    bullet_list(c, ["거리·시간·평균 페이스·심박·케이던스", "심박 Zone 1-5 경계와 시간 분포", "수직 진폭 cm, 보폭 m 등 단위 변환", "km별 페이스·심박·고도·러닝 다이내믹스", "사진·영상 기록 카드 미리보기와 저장"], x, 590, W - M - x, 9.4, INK, BLUE, 6)
    c.setFont("KoreanBold", 12)
    c.setFillColor(INK)
    c.drawString(M, 356, "기획 의사결정")
    decisions = [
        ("기록 보존", "서버 없이도 다시 볼 수 있도록 브라우저 저장을 우선 적용"),
        ("심박 Zone", "일률적인 최대심박 비율보다 사용자의 Garmin 설정값을 우선"),
        ("레이스 전략", "목표 기록만 입력하면 이븐·포지티브·네거티브 km별 페이스 생성"),
        ("공유 경험", "분석 화면의 데이터를 사용자가 고른 사진·영상 위에 자동 배치"),
    ]
    yy = 330
    for name, desc in decisions:
        rounded(c, M, yy - 58, W - 2 * M, 50, WHITE, LINE, 10)
        c.setFillColor(BLUE)
        c.setFont("KoreanBold", 9)
        c.drawString(M + 14, yy - 29, name)
        para(c, desc, M + 112, yy - 18, W - 2 * M - 126, 8.7, 13, SOFT, False, 34)
        yy -= 62
    footer(c, 6)
    c.showPage()


def page_strion_result(c):
    bg(c, True)
    page_header(c, "Project 01 · STRION", 7, True)
    y = title(c, "05 · Result & Next", "작동하는 개인 러닝 서비스와 명확한 다음 조건을 남겼습니다", None, True)
    metrics = [("DATA INPUT", "FIT + SYNC"), ("ANALYSIS", "RUN FLOW"), ("PLANNING", "PACE CSV"), ("SHARE", "PHOTO + VIDEO")]
    for i, (lab, val) in enumerate(metrics):
        metric(c, M + (i % 2) * 252, y - 84 - (i // 2) * 76, 236, lab, val, True)
    para(c, "완료", M, y - 194, 90, 12, 17, CYAN, True)
    bullet_list(c, ["실사용 FIT 업로드·분석·저장·재열람", "개인 Garmin 기록 동기화와 월별 마일리지", "목표 페이스·레이스 전략·CSV", "사진·영상 러닝 기록 카드"], M, y - 218, 230, 9.5, WHITE, CYAN, 6)
    para(c, "다음 조건", M + 264, y - 194, 100, 12, 17, CYAN, True)
    bullet_list(c, ["공식 다중 사용자 계정 연동", "서버 기반 계정·기록 백업", "개인정보 동의와 삭제 정책", "훈련 추천 로직의 장기 검증"], M + 264, y - 218, 230, 9.5, WHITE, CYAN, 6)
    rounded(c, M, 92, W - 2 * M, 88, colors.HexColor("#102433"), colors.HexColor("#315267"), 12)
    para(c, "STRION = STRIDE + ON. 한 번의 기록을 이해하고 다음 걸음을 이어간다는 의미를 서비스 흐름에 반영했습니다.", M + 18, 145, W - 2 * M - 36, 11, 18, WHITE, True, 62)
    c.setFillColor(CYAN)
    c.setFont("KoreanBold", 8)
    c.drawRightString(W - M - 16, 106, "LIVE SERVICE ↗")
    link_region(c, STRION_URL, M, 92, W - 2 * M, 88)
    footer(c, 7, True)
    c.showPage()


def page_farm_overview(c):
    bg(c)
    page_header(c, "Project 02 · Smart Farm", 8)
    y = title(c, "01 · Problem & System", "장치가 앞에 없어도 상태를 알고 대응할 수 있어야 했습니다", "스마트팜 교육 조별 프로젝트에서 ICT 담당으로 센서 수집, 통신, 웹 모니터링과 제어 흐름을 연결했습니다.")
    image_cover(c, ROOT / "assets" / "smartfarm-live.png", M, 360, W - 2 * M, 220, 14)
    c.setFillColor(colors.Color(0, 0, 0, alpha=.42))
    c.roundRect(M, 360, W - 2 * M, 220, 14, fill=1, stroke=0)
    flow = ["DHT11", "Arduino", "Raspberry Pi 5\n+ Node-RED", "MQTT", "Dashboard\n+ Telegram"]
    x = M + 18
    for i, item in enumerate(flow):
        rounded(c, x, 422, 84, 70, colors.Color(1, 1, 1, alpha=.1), colors.Color(1, 1, 1, alpha=.45), 10)
        para(c, item.replace("\n", "<br/>"), x + 8, 466, 68, 8.2, 12, WHITE, True, 45)
        if i < len(flow) - 1:
            c.setFillColor(CYAN)
            c.setFont("KoreanBold", 12)
            c.drawString(x + 89, 450, "→")
        x += 101
    para(c, "핵심 사용자 시나리오", M, 324, 180, 12, 17, BLUE, True)
    bullet_list(c, ["현장을 계속 지키지 않고 휴대폰에서 온도·습도와 마지막 수신 시각 확인", "웹에서 ON/OFF 명령을 보내고 실제 장치가 반응하는지 확인", "대시보드를 열지 않아도 1시간 간격으로 최근 온습도 상태 수신"], M, 298, W - 2 * M, 9.5, INK, BLUE, 7)
    footer(c, 8)
    c.showPage()


def page_farm_led(c):
    bg(c)
    page_header(c, "Project 02 · Smart Farm", 9)
    y = title(c, "02 · Verified Case 01", "웹 명령이 실제 LED 반응까지 이어지는지 확인했습니다")
    steps = ["Dashboard\nON/OFF", "MQTT\nfarm/pump", "Node-RED\n명령 변환", "Serial\nPUMP_ON/OFF", "Arduino\nLED 반응"]
    x = M
    for i, step in enumerate(steps):
        rounded(c, x, y - 90, 92, 68, PALE_BLUE if i in (0, 4) else WHITE, BLUE if i in (0, 4) else LINE, 12)
        para(c, step.replace("\n", "<br/>"), x + 8, y - 45, 76, 8.3, 12, INK, True, 50)
        if i < 4:
            c.setFillColor(BLUE)
            c.setFont("KoreanBold", 12)
            c.drawString(x + 95, y - 62, "→")
        x += 104
    rounded(c, M, y - 255, W - 2 * M, 130, WHITE, LINE, 14)
    pill(c, "실물 검증 완료", M + 18, y - 158, GREEN)
    para(c, "Arduino와 브레드보드에 LED를 연결하고 대시보드 버튼으로 ON/OFF 명령을 실행했습니다. 웹 조작에 따라 실제 LED가 점등·소등되는 것을 직접 확인해 화면, 통신, 시리얼, 물리 장치 사이의 연결을 검증했습니다.", M + 18, y - 188, W - 2 * M - 36, 10.2, 17, INK, False, 85)
    rounded(c, M, y - 390, W - 2 * M, 104, colors.HexColor("#FFF4E5"), colors.HexColor("#E4C18E"), 14)
    pill(c, "범위 구분", M + 18, y - 320, AMBER)
    para(c, "같은 farm/pump 토픽과 명령 이름을 사용하지만 실제 펌프 하드웨어는 연결하지 않았습니다. 따라서 완료 표현은 LED 제어에만 사용하고, 펌프 구동은 실물 미검증으로 분리했습니다.", M + 18, y - 350, W - 2 * M - 36, 9.8, 16, INK, False, 68)
    footer(c, 9)
    c.showPage()


def page_farm_dht(c):
    bg(c, True)
    page_header(c, "Project 02 · Smart Farm", 10, True)
    y = title(c, "03 · Verified Case 02", "DHT11 실측값을 웹과 Telegram으로 전달했습니다", "대시보드 표시와 Telegram 알림은 같은 센서값을 사용하지만 서로 다른 전달 경로입니다.", True)
    flow = ["Serial In", "JSON", "Function", "MQTT Out", "Dashboard"]
    x = M
    for i, step in enumerate(flow):
        rounded(c, x, y - 72, 88, 54, colors.HexColor("#0B1B2A"), colors.HexColor("#315267"), 10)
        para(c, step, x + 8, y - 39, 72, 8.1, 11, WHITE, True, 30)
        if i < 4:
            c.setFillColor(CYAN)
            c.setFont("KoreanBold", 11)
            c.drawString(x + 91, y - 51, "→")
        x += 101
    c.setStrokeColor(CYAN)
    c.setLineWidth(2)
    c.line(M + 196, y - 72, M + 196, y - 110)
    rounded(c, M + 108, y - 184, 300, 62, colors.HexColor("#102433"), colors.HexColor("#315267"), 10)
    para(c, "Save Temp Humidity → Inject (3,600초) → Telegram Sender", M + 122, y - 145, 272, 8.5, 12, WHITE, True, 40)
    c.setFont("KoreanBold", 12)
    c.setFillColor(WHITE)
    c.drawString(M, y - 224, "Node-RED 노드 역할")
    roles = [
        ("Serial In", "Arduino 줄 단위 JSON 수신"), ("JSON", "문자열을 객체로 변환"),
        ("Function", "온도·습도 출력 분리"), ("MQTT Out", "farm/temp·humidity 발행"),
        ("Save Temp Humidity", "최근값과 시각 저장"), ("Inject", "3,600초마다 실행"),
        ("Telegram Sender", "최근 상태 메시지 전송"),
    ]
    yy = y - 248
    for i, (name, desc) in enumerate(roles):
        col = i % 2
        row = i // 2
        xx = M + col * 255
        top = yy - row * 60
        c.setStrokeColor(colors.HexColor("#294758"))
        c.line(xx, top - 48, xx + 235, top - 48)
        para(c, name, xx, top, 110, 8.2, 11, CYAN, True, 28)
        para(c, desc, xx + 112, top, 123, 8.1, 11, colors.HexColor("#B7C4CD"), False, 35)
    footer(c, 10, True)
    c.showPage()


def page_farm_matrix(c):
    bg(c)
    page_header(c, "Project 02 · Smart Farm", 11)
    y = title(c, "04 · Validation Matrix", "구현 여부가 아니라 확인 근거에 따라 상태를 구분했습니다")
    rows = [
        ("기능", "확인 근거", "상태"),
        ("DHT11 온습도", "실측값과 대시보드 갱신 확인", "실물 검증"),
        ("웹 ON/OFF → LED", "실제 점등·소등 확인", "실물 검증"),
        ("Telegram 1시간 메시지", "실제 메시지 수신 확인", "실물 검증"),
        ("Raspberry Pi·Node-RED", "교육 프로젝트 실제 연결·실행", "실물 검증"),
        ("JSON·MQTT 분리", "공개용 흐름과 코드 확인", "코드 확인"),
        ("시간별 MQTT 스냅샷", "3,600초 retained 발행 코드", "코드 확인"),
        ("실제 펌프", "명령 로직만 존재, 하드웨어 미연결", "미검증"),
        ("EC·pH 센서", "UI 확장, 실물 센서 미보유", "미검증"),
    ]
    table(c, rows, M, y - 8, [125, 280, W - 2 * M - 405], 46)
    rounded(c, M, 90, W - 2 * M, 95, colors.HexColor("#FFF4E5"), colors.HexColor("#E4C18E"), 14)
    para(c, "시간별 MQTT 스냅샷은 Telegram 알림과 별개의 보조 흐름입니다. 데이터베이스 장기 저장이나 기록 조회 화면은 확인되지 않아 완료 기능으로 표현하지 않았습니다.", M + 18, 156, W - 2 * M - 36, 9.6, 16, INK, False, 68)
    c.setFillColor(BLUE)
    c.setFont("KoreanBold", 8)
    c.drawRightString(W - M - 16, 104, "LIVE SERVICE ↗")
    link_region(c, SMART_FARM_URL, M, 90, W - 2 * M, 95)
    footer(c, 11)
    c.showPage()


def page_profile(c):
    bg(c, True)
    page_header(c, "Profile", 12, True)
    y = title(c, "Career & Collaboration", "운영 경험을 이해하고, AI로 구현을 가속하며, 결과는 직접 검증합니다", None, True)
    career = [
        ("2025.02-2026.02", "농업회사법인 이에프시 · 구매·재고·3PL 운영"),
        ("2024.02-2024.04", "호야홈텍 · 생산 원재료 구매·발주"),
        ("2021.04-2023.12", "주식회사 든솔 · 공동 운영 / 사업운영"),
        ("2018.05-2021.02", "컴퓨존 · 입출고·재고관리"),
        ("2017.10-2018.03", "롯데웰푸드 · 국내영업"),
        ("2017.03-2017.09", "디엠에이씨인터내셔널 · 온라인 MD·상품기획"),
    ]
    yy = y - 20
    for date, role in career:
        c.setStrokeColor(colors.HexColor("#294758"))
        c.line(M, yy - 34, W - M, yy - 34)
        c.setFillColor(CYAN)
        c.setFont("KoreanBold", 8)
        c.drawString(M, yy - 19, date)
        para(c, role, M + 130, yy - 8, W - 2 * M - 130, 9, 13, WHITE, True, 30)
        yy -= 48
    c.setFont("KoreanBold", 12)
    c.setFillColor(WHITE)
    c.drawString(M, yy - 10, "WORKING WITH AI")
    blocks = [
        ("MY OWNERSHIP", "문제·사용 상황·우선순위·요구사항·검증 기준 결정"),
        ("AI SUPPORT", "코드 초안·오류 원인 후보·UI 대안·문서 구조 탐색"),
        ("VALIDATION", "원본 데이터·실물 장치·로그·모바일 화면 직접 대조"),
    ]
    bx = M
    for label, desc in blocks:
        rounded(c, bx, 130, 158, 92, colors.HexColor("#0B1B2A"), colors.HexColor("#315267"), 12)
        para(c, label, bx + 12, 202, 134, 8, 11, CYAN, True, 22)
        para(c, desc, bx + 12, 180, 134, 8.2, 12, colors.HexColor("#B7C4CD"), False, 50)
        bx += 171
    c.setFillColor(WHITE)
    c.setFont("KoreanBold", 13)
    c.drawString(M, 88, "zionkoo.github.io/portfolio/")
    c.setFillColor(CYAN)
    c.setFont("Korean", 9)
    c.drawString(M, 66, "zionkoo@kakao.com")
    link_region(c, PORTFOLIO_URL, M, 80, 230, 20)
    link_region(c, EMAIL_URL, M, 58, 160, 20)
    footer(c, 12, True)
    c.showPage()


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=A4, pageCompression=1)
    c.setTitle("구정민 서비스 기획 포트폴리오")
    c.setAuthor("구정민")
    c.setSubject("Service Planning Portfolio - STRION and Smart Farm")
    for maker in (
        page_cover, page_intro, page_strion_overview, page_strion_flow,
        page_strion_sync, page_strion_validation, page_strion_result,
        page_farm_overview, page_farm_led, page_farm_dht,
        page_farm_matrix, page_profile,
    ):
        maker(c)
    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    build()
