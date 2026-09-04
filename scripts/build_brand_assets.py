# -*- coding: utf-8 -*-
"""브랜드 아이콘과 SNS 공유 이미지를 만든다.

마크는 검정 판에 라임색 "잘" 한 글자다. 20px로 줄여도 뭔지 읽히는 게
도형 시안들보다 나았다.

favicon.svg도 여기서 만든다. 글자를 텍스트로 두면 보는 사람 기기에 그 글꼴이
없을 때 모양이 달라지므로, 맑은 고딕 볼드에서 윤곽을 떠 패스로 박는다.

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

from fontTools.misc.transform import Transform
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
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

MARK_CHAR = "잘"


def font(path, size):
    return ImageFont.truetype(path, size)


def draw_mark(img, x, y, size):
    """마크 1개. 검정 판 위에 라임 '잘'."""
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + size, y + size], fill=INK)
    f = font(FONT_BOLD, int(size * 0.66))
    box = d.textbbox((0, 0), MARK_CHAR, font=f)
    w, h = box[2] - box[0], box[3] - box[1]
    d.text((x + size / 2 - w / 2 - box[0], y + size / 2 - h / 2 - box[1]),
           MARK_CHAR, font=f, fill=LIME)


def glyph_svg_path(char, box=64.0, ratio=0.60):
    """글리프 윤곽을 viewBox 좌표계의 SVG 패스로 옮긴다.

    폰트는 y축이 위로 자라고 SVG는 아래로 자란다. 뒤집고, 정한 비율로 키운 뒤
    실제 잉크 영역 기준으로 가운데 놓는다.
    """
    tt = TTFont(FONT_BOLD)
    name = tt.getBestCmap()[ord(char)]
    glyphs = tt.getGlyphSet()

    bounds = BoundsPen(glyphs)
    glyphs[name].draw(bounds)
    x0, y0, x1, y1 = bounds.bounds
    scale = box * ratio / max(x1 - x0, y1 - y0)
    tx = box / 2 - (x0 + x1) / 2 * scale
    ty = box / 2 + (y0 + y1) / 2 * scale   # y를 뒤집으므로 부호가 반대다

    pen = SVGPathPen(glyphs)
    glyphs[name].draw(TransformPen(pen, Transform(scale, 0, 0, -scale, tx, ty)))
    tt.close()
    return pen.getCommands()


def build_favicon_svg():
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="잘버려">',
        '  <!-- scripts/build_brand_assets.py 가 만든다. 직접 고치지 않는다.',
        '       글자를 패스로 떠서 박았다 - 보는 기기에 글꼴이 없어도 같은 모양이 나온다. -->',
        '  <rect width="64" height="64" fill="#111"/>',
        '  <path d="%s" fill="#c9f24d"/>' % glyph_svg_path(MARK_CHAR),
        '</svg>',
        '',
    ]
    path = os.path.join(OUT, "favicon.svg")
    open(path, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
    return "favicon.svg"


def icon(size):
    img = Image.new("RGB", (size, size), INK)
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

    img.save(os.path.join(OUT, "og.png"), optimize=True)
    return "og.png"


def main():
    made = [build_favicon_svg()]
    made += build_icons()
    made.append(build_og())
    for name in made:
        size = os.path.getsize(os.path.join(OUT, name))
        print("%-22s %6.1f KB" % (name, size / 1024))
    print("\n-> %s" % OUT)


if __name__ == "__main__":
    main()
