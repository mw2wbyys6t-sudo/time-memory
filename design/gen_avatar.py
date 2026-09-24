"""
时光记忆 · 微信小程序头像生成
生成 3 个候选方案，均为 1024x1024 高清 PNG
采用 4x 超采样保证矢量级平滑边缘
"""
import math
import os
from PIL import Image, ImageDraw, ImageFilter

SIZE = 1024
SS = 4
CANVAS = SIZE * SS

BRAND_A = (124, 108, 240)
BRAND_B = (155, 140, 255)
ACCENT = (255, 176, 32)
WHITE = (255, 255, 255)
DARK = (45, 40, 80)


def linear_gradient(size, color_top, color_bottom, vertical=True):
    w, h = size
    base = Image.new('RGB', (w, h), color_top)
    top = Image.new('RGB', (w, h), color_top)
    bottom = Image.new('RGB', (w, h), color_bottom)
    mask = Image.new('L', (w, h), 0)
    mdraw = ImageDraw.Draw(mask)
    if vertical:
        for y in range(h):
            mdraw.line([(0, y), (w, y)], fill=int(255 * y / max(1, h - 1)))
    else:
        for x in range(w):
            mdraw.line([(x, 0), (x, h)], fill=int(255 * x / max(1, w - 1)))
    base = Image.composite(bottom, top, mask)
    return base


def diag_gradient(size, c1, c2):
    w, h = size
    img = Image.new('RGB', (w, h), c1)
    px = img.load()
    for y in range(h):
        for x in range(w):
            t = (x + y) / (w + h)
            r = int(c1[0] + (c2[0] - c1[0]) * t)
            g = int(c1[1] + (c2[1] - c1[1]) * t)
            b = int(c1[2] + (c2[2] - c1[2]) * t)
            px[x, y] = (r, g, b)
    return img


def rounded_square(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def downscale(img):
    return img.resize((SIZE, SIZE), Image.LANCZOS)


def scheme_a():
    """方案 A · 时光拍立得：紫底 + 白色拍立得 + 表盘指针"""
    bg = diag_gradient((CANVAS, CANVAS), BRAND_A, BRAND_B).convert('RGBA')
    d = ImageDraw.Draw(bg)

    pad = CANVAS * 0.08
    rounded_square(d, [pad, pad, CANVAS - pad, CANVAS - pad], CANVAS * 0.22, (255, 255, 255, 0))

    cx = cy = CANVAS / 2

    photo_w = CANVAS * 0.46
    photo_h = CANVAS * 0.56
    px0 = cx - photo_w / 2
    py0 = cy - photo_h / 2 + CANVAS * 0.02
    rounded_square(d, [px0, py0, px0 + photo_w, py0 + photo_h], CANVAS * 0.04, (255, 255, 255, 255))

    img_w = photo_w * 0.78
    img_h = photo_h * 0.62
    ix0 = cx - img_w / 2
    iy0 = py0 + (photo_h - img_h) * 0.32
    rounded_square(d, [ix0, iy0, ix0 + img_w, iy0 + img_h], CANVAS * 0.02,
                   (124, 108, 240, 255))

    ccx = cx
    ccy = iy0 + img_h / 2
    r = img_h * 0.30
    d.ellipse([ccx - r, ccy - r, ccx + r, ccy + r], outline=(255, 255, 255, 255),
              width=int(CANVAS * 0.012))

    for ang in range(0, 360, 30):
        a = math.radians(ang - 90)
        x1 = ccx + r * 0.80 * math.cos(a)
        y1 = ccy + r * 0.80 * math.sin(a)
        x2 = ccx + r * 0.95 * math.cos(a)
        y2 = ccy + r * 0.95 * math.sin(a)
        d.line([x1, y1, x2, y2], fill=(255, 255, 255, 255), width=int(CANVAS * 0.008))

    ha = math.radians(60 - 90)
    ma = math.radians(150 - 90)
    d.line([ccx, ccy, ccx + r * 0.45 * math.cos(ha), ccy + r * 0.45 * math.sin(ha)],
           fill=(255, 255, 255, 255), width=int(CANVAS * 0.022))
    d.line([ccx, ccy, ccx + r * 0.65 * math.cos(ma), ccy + r * 0.65 * math.sin(ma)],
           fill=ACCENT + (255,), width=int(CANVAS * 0.016))
    d.ellipse([ccx - r * 0.07, ccy - r * 0.07, ccx + r * 0.07, ccy + r * 0.07],
              fill=ACCENT + (255,))

    return downscale(bg)


def scheme_b():
    """方案 B · 胶片时光轮：圆形紫底 + 胶片孔 + 播放与时针融合"""
    bg = diag_gradient((CANVAS, CANVAS), BRAND_A, BRAND_B).convert('RGBA')
    d = ImageDraw.Draw(bg)

    cx = cy = CANVAS / 2
    R = CANVAS * 0.42

    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(255, 255, 255, 235))

    rim = CANVAS * 0.10
    d.ellipse([cx - R + rim, cy - R + rim, cx + R - rim, cy + R - rim],
              outline=(255, 255, 255, 0), fill=(124, 108, 240, 255))

    inner_r = R - rim
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        hx = cx + (R - rim / 2) * math.cos(a)
        hy = cy + (R - rim / 2) * math.sin(a)
        hr = rim * 0.28
        d.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=(255, 255, 255, 230))

    fr = inner_r * 0.72
    fx = cx - fr * 0.18
    fy = cy
    tri = []
    p1 = (fx - fr * 0.45, fy - fr * 0.55)
    p2 = (fx - fr * 0.45, fy + fr * 0.55)
    p3 = (fx + fr * 0.65, fy)
    d.polygon([p1, p2, p3], fill=(255, 255, 255, 255))

    ha = math.radians(120 - 90)
    d.line([cx, cy, cx + inner_r * 0.55 * math.cos(ha), cy + inner_r * 0.55 * math.sin(ha)],
           fill=ACCENT + (255,), width=int(CANVAS * 0.024))
    d.ellipse([cx - CANVAS * 0.025, cy - CANVAS * 0.025, cx + CANVAS * 0.025, cy + CANVAS * 0.025],
              fill=ACCENT + (255,))

    return downscale(bg)


def scheme_c():
    """方案 C · 极简时光：圆角紫底 + 细线表盘 + 中心亮点（最高级、最通用）"""
    bg = diag_gradient((CANVAS, CANVAS), BRAND_A, BRAND_B).convert('RGBA')
    d = ImageDraw.Draw(bg)

    cx = cy = CANVAS / 2
    R = CANVAS * 0.30

    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=(255, 255, 255, 255),
              width=int(CANVAS * 0.016))

    for i in range(12):
        ang = math.radians(i * 30 - 90)
        major = (i % 3 == 0)
        inner = R * (0.82 if major else 0.90)
        outer = R * 0.98
        w = int(CANVAS * (0.018 if major else 0.010))
        x1 = cx + inner * math.cos(ang)
        y1 = cy + inner * math.sin(ang)
        x2 = cx + outer * math.cos(ang)
        y2 = cy + outer * math.sin(ang)
        d.line([x1, y1, x2, y2], fill=(255, 255, 255, 255), width=w)

    ha = math.radians(50 - 90)
    ma = math.radians(140 - 90)
    d.line([cx, cy, cx + R * 0.48 * math.cos(ha), cy + R * 0.48 * math.sin(ha)],
           fill=(255, 255, 255, 255), width=int(CANVAS * 0.03))
    d.line([cx, cy, cx + R * 0.68 * math.cos(ma), cy + R * 0.68 * math.sin(ma)],
           fill=ACCENT + (255,), width=int(CANVAS * 0.022))

    dot_r = CANVAS * 0.04
    d.ellipse([cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r], fill=ACCENT + (255,))

    return downscale(bg)


def export_alpha(img, name):
    out_dir = '/workspace/design/avatar'
    os.makedirs(out_dir, exist_ok=True)
    img.convert('RGB').save(os.path.join(out_dir, name), 'PNG')
    img.convert('RGB').resize((144, 144), Image.LANCZOS).save(
        os.path.join(out_dir, name.replace('.png', '_144.png')), 'PNG')


if __name__ == '__main__':
    export_alpha(scheme_a(), 'avatar_a_polaroid.png')
    export_alpha(scheme_b(), 'avatar_b_film.png')
    export_alpha(scheme_c(), 'avatar_c_minimal.png')
    print('done')
