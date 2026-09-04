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
import json
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


def item_count():
    """발행된 품목 수. 카드에 박는 숫자가 실제와 어긋나면 안 된다."""
    path = os.path.join(ROOT, "site", "src", "data", "items.json")
    with open(path, encoding="utf-8") as f:
        return len(json.load(f))


def chip(d, x, y, text, f):
    """라임 알약. 사이트의 배지와 같은 문법이다 - 라운드 없음, 굵은 테두리."""
    box = d.textbbox((0, 0), text, font=f)
    w = box[2] - box[0]
    pad_x, h = 22, 58
    d.rectangle([x, y, x + w + pad_x * 2, y + h], fill=LIME, outline=INK, width=4)
    d.text((x + pad_x - box[0], y + h / 2 - (box[3] + box[1]) / 2), text, font=f, fill=INK)
    return x + w + pad_x * 2


def build_og():
    """공유 카드. 링크를 받은 사람이 3초 안에 '나한테 쓸모 있나'를 판단하게 한다.

    그래서 브랜드 이름이 아니라 사용자의 질문을 제일 크게 놓는다. 그 밑에
    규모(품목 수)와 걸리는 수고(세 번)를 숫자로 주고, 무엇을 알려주는지를
    알약 세 개로 못 박는다.
    """
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # 바깥 테두리. 사이트의 2px 선을 공유 카드 크기로 키운 것이다
    d.rectangle([18, 18, W - 19, H - 19], outline=INK, width=8)

    # 좌상단 로크업. 브랜드는 작게, 질문은 크게
    draw_mark(img, 84, 66, 58)
    d.text((156, 74), "잘버려", font=font(FONT_BOLD, 40), fill=INK)

    d.text((80, 168), "이거 어디에", font=font(FONT_BOLD, 92), fill=INK)
    d.text((80, 262), "버려요?", font=font(FONT_BOLD, 92), fill=INK)

    d.text((86, 382), "품목 %d개. 세 번만 누르면 답이 나옵니다."
           % item_count(), font=font(FONT_REG, 32), fill=(60, 58, 53))

    f = font(FONT_BOLD, 27)
    x = 86
    for text in ("분리배출 판정", "대형폐기물 수수료", "무료수거 안내"):
        x = chip(d, x, 442, text, f) + 14

    draw_mark(img, 890, 190, 210)

    # 하단 라임 띠. 미리보기가 잘려도 브랜드 색과 주소는 남는다
    d.rectangle([18, H - 88, W - 19, H - 19], fill=LIME)
    d.rectangle([18, H - 88, W - 19, H - 19], outline=INK, width=8)
    d.text((90, H - 74), "jalbeo.com", font=font(FONT_BOLD, 34), fill=INK)

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
