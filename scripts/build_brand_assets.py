# -*- coding: utf-8 -*-
"""브랜드 아이콘과 SNS 공유 이미지를 만든다.

마크는 라임 판에 검정 쓰레기통이다. 뚜껑, 통, 넣는 화살표 셋뿐이라
16px까지 줄여도 형태가 안 무너진다.

favicon.svg가 원본 도형이고, 이 스크립트는 같은 좌표를 래스터로 다시 그린다
(SVG를 못 읽는 곳 - 파비콘 폴백, iOS 홈 화면, 오픈그래프).

  favicon.svg          벡터        브라우저 탭
  favicon.ico          16/32/48    구형 폴백
  icon-192.png         192         안드로이드 홈 화면
  icon-512.png         512         PWA / 큰 타일
  apple-touch-icon.png 180         iOS 홈 화면
  og.png               1200x630    카카오톡, 트위터, 페이스북 공유 카드

글꼴은 윈도우 기본 맑은 고딕이다. 사이트 본문은 Pretendard지만 굽는 이미지는
빌드 환경에 웹폰트를 깔지 않으려고 시스템 글꼴을 쓴다.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site", "public")

PAPER = (245, 243, 238)
INK = (17, 17, 17)
LIME = (201, 242, 77)
FAINT = (107, 104, 98)

# 사이트의 판정 색과 순서를 그대로 쓴다 (site/src/lib/verdict.ts).
# 카드에서만 다른 색을 쓰면 들어와서 처음 보는 화면과 어긋난다.
VERDICTS = [
    ("재활용", (201, 242, 77)),
    ("무상수거", (169, 199, 255)),
    ("전용수거함", (213, 194, 255)),
    ("대형폐기물", (247, 198, 90)),
    ("음식물", (143, 217, 168)),
    ("조건부", (228, 224, 214)),
    ("일반쓰레기", (255, 159, 143)),
]

# 공유 카드에 올릴 배지. 판정 일곱을 다 놓으면 작은 썸네일에서 뭉개진다.
# 재활용 / 대형폐기물 / 일반쓰레기 는 사용자가 갈리는 세 갈래다
OG_CHIPS = ("재활용", "대형폐기물", "일반쓰레기")

FONT_BOLD = r"C:\Windows\Fonts\malgunbd.ttf"
FONT_REG = r"C:\Windows\Fonts\malgun.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def draw_mark(img, x, y, size):
    """마크 1개. favicon.svg 와 같은 좌표를 64 단위로 환산해 그린다."""
    d = ImageDraw.Draw(img)
    u = size / 64.0
    px = lambda v: x + v * u
    py = lambda v: y + v * u

    d.rectangle([px(0), py(0), px(64), py(64)], fill=LIME)
    # 테두리는 stroke-width 6 을 중앙 정렬한 것과 같게 3 안쪽에서 6 두께로 채운다
    d.rectangle([px(0), py(0), px(64), py(64)], outline=INK, width=int(round(6 * u)))
    d.rectangle([px(29), py(10), px(35), py(21)], fill=INK)
    d.polygon([(px(22), py(19)), (px(42), py(19)), (px(32), py(31))], fill=INK)
    d.rectangle([px(15), py(34), px(49), py(39)], fill=INK)
    d.polygon([(px(19), py(42)), (px(45), py(42)), (px(42), py(55)), (px(22), py(55))], fill=INK)


def icon(size):
    img = Image.new("RGB", (size, size), PAPER)
    draw_mark(img, 0, 0, size)
    return img


def build_icons():
    made = []
    icon(256).save(os.path.join(OUT, "favicon.ico"),
                   sizes=[(16, 16), (32, 32), (48, 48)])
    made.append("favicon.ico")
    for name, size in (("icon-192.png", 192), ("icon-512.png", 512),
                       ("apple-touch-icon.png", 180)):
        icon(size).save(os.path.join(OUT, name))
        made.append(name)
    return made


CHIP_PAD = 18


def chip(d, x, y, text, f, fill, h):
    """판정 배지. 사이트의 배지와 같은 문법이다 - 라운드 없음, 굵은 테두리."""
    box = d.textbbox((0, 0), text, font=f)
    w = box[2] - box[0]
    d.rectangle([x, y, x + w + CHIP_PAD * 2, y + h], fill=fill, outline=INK, width=5)
    d.text((x + CHIP_PAD - box[0], y + h / 2 - (box[3] + box[1]) / 2), text, font=f, fill=INK)
    return x + w + CHIP_PAD * 2


def chip_w(d, text, f):
    box = d.textbbox((0, 0), text, font=f)
    return box[2] - box[0] + CHIP_PAD * 2


def text_w(d, text, f):
    box = d.textbbox((0, 0), text, font=f)
    return box[2] - box[0]


def build_og():
    """공유 카드. 링크를 받은 사람이 3초 안에 '나한테 쓸모 있나'를 판단하게 한다.

    그래서 브랜드 이름이 아니라 사용자의 질문을 제일 크게 놓고, 어떤 답이
    나오는지를 판정 배지로 늘어놓는다. 색과 순서는 사이트와 같아서, 눌러 들어온
    사람이 처음 보는 화면과 카드가 이어진다.

    가로 1200 을 다 쓰지 않는다. 노션 북마크, 카카오톡 작은 카드처럼 미리보기를
    정사각으로 가운데 잘라 내는 데가 많아서, 글자와 배지는 전부 가운데 630
    (x 285~915) 안에 둔다. 바깥 285 씩은 여백과 테두리, 하단 띠 뿐이다.
    """
    W, H = 1200, 630
    CX = W // 2
    SAFE = 600  # 정사각 크롭이 남기는 630 에서 좌우 15 씩 뺀 폭
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # 바깥 테두리. 사이트의 2px 선을 공유 카드 크기로 키운 것이다
    d.rectangle([18, 18, W - 19, H - 19], outline=INK, width=8)

    # 로크업. 마크와 이름을 묶어 가운데 놓는다
    f_brand = font(FONT_BOLD, 38)
    mark = 54
    lock_w = mark + 16 + text_w(d, "잘버려", f_brand)
    lx = CX - lock_w // 2
    draw_mark(img, lx, 62, mark)
    d.text((lx + mark + 16, 68), "잘버려", font=f_brand, fill=INK)

    # 질문. 카드에서 제일 큰 글자다
    f_head = font(FONT_BOLD, 84)
    for i, line in enumerate(("이거 어디에", "버려요?")):
        d.text((CX - text_w(d, line, f_head) // 2, 152 + i * 96),
               line, font=f_head, fill=INK)

    # 판정 배지 한 줄. 일곱 개를 두 줄로 놓으면 글자가 24px 까지 내려가는데,
    # 노션 북마크는 이 카드를 가로 200px 안팎으로 줄여서 그 크기가 4px 이 된다.
    # 세 개만 큼직하게 놓아 축소를 견디게 한다. 고른 셋은 판정의 세 갈래다
    gap = 14
    row = [(t, c) for t, c in VERDICTS if t in OG_CHIPS]
    f, size = None, None
    for size in range(44, 19, -1):  # SAFE 안에 들어가는 제일 큰 글자를 쓴다
        f = font(FONT_BOLD, size)
        row_w = sum(chip_w(d, t, f) for t, _ in row) + gap * (len(row) - 1)
        if row_w <= SAFE:
            break
    else:
        raise AssertionError("배지 한 줄이 안전폭에 안 들어간다")
    h = size + 30
    x = CX - row_w // 2
    for text, fill in row:
        x = chip(d, x, 386, text, f, fill, h) + gap

    # 하단 라임 띠. 미리보기가 잘려도 브랜드 색과 주소는 남는다
    d.rectangle([18, H - 88, W - 19, H - 19], fill=LIME)
    d.rectangle([18, H - 88, W - 19, H - 19], outline=INK, width=8)
    f_url = font(FONT_BOLD, 34)
    d.text((CX - text_w(d, "jalbeo.com", f_url) // 2, H - 72),
           "jalbeo.com", font=f_url, fill=INK)

    img.save(os.path.join(OUT, "og.png"), optimize=True)
    return "og.png"


def main():
    made = build_icons()
    made.append(build_og())
    for name in made:
        size = os.path.getsize(os.path.join(OUT, name))
        print("%-22s %6.1f KB" % (name, size / 1024))
    print("\n-> %s" % OUT)


if __name__ == "__main__":
    main()
