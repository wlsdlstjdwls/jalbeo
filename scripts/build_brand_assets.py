# -*- coding: utf-8 -*-
"""브랜드 아이콘과 SNS 공유 이미지를 만든다.

site/public/favicon.svg 가 원본 도형이다. 이 스크립트는 같은 도형을 래스터로
다시 그린다 (SVG를 못 읽는 곳 - 파비콘 폴백, iOS 홈 화면, 오픈그래프).

  favicon.ico          16/32/48    브라우저 탭 폴백
  icon-192.png         192         안드로이드 홈 화면
  icon-512.png         512         PWA / 큰 타일
  apple-touch-icon.png 180         iOS 홈 화면
  og.png               1200x630    카카오톡, 트위터, 페이스북 공유 카드

글꼴은 윈도우 기본 맑은 고딕이다. 사이트 본문은 Pretendard지만 공유 이미지는
빌드 환경에 웹폰트를 깔지 않으려고 시스템 폰트로 굽는다.
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

FONT_BOLD = r"C:\Windows\Fonts\malgunbd.ttf"
FONT_REG = r"C:\Windows\Fonts\malgun.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def draw_mark(img, x, y, size):
    """favicon.svg 와 같은 도형. 64 단위 좌표를 size 로 환산한다."""
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
    ico = icon(256)
    ico.save(os.path.join(OUT, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
    made.append("favicon.ico")
    for name, size in (("icon-192.png", 192), ("icon-512.png", 512),
                       ("apple-touch-icon.png", 180)):
        icon(size).save(os.path.join(OUT, name))
        made.append(name)
    return made


def build_og():
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # 바깥 테두리. 사이트의 2px 선을 공유 카드 크기로 키운 것이다
    d.rectangle([18, 18, W - 19, H - 19], outline=INK, width=8)

    draw_mark(img, 800, 195, 240)

    d.text((84, 150), "잘버려", font=font(FONT_BOLD, 132), fill=INK)
    d.text((90, 316), "쓰레기, 어떻게 버리지", font=font(FONT_BOLD, 46), fill=INK)
    d.text((90, 390), "품목별 배출 방법과 대형폐기물 수수료를", font=font(FONT_REG, 30), fill=FAINT)
    d.text((90, 432), "한 페이지에서 확인한다", font=font(FONT_REG, 30), fill=FAINT)

    # 하단 라임 띠. 카드가 잘려도 브랜드 색이 남는다
    d.rectangle([18, H - 88, W - 19, H - 19], fill=LIME)
    d.rectangle([18, H - 88, W - 19, H - 19], outline=INK, width=8)
    d.text((90, H - 74), "jalbeo.com", font=font(FONT_BOLD, 34), fill=INK)

    path = os.path.join(OUT, "og.png")
    img.save(path, optimize=True)
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
