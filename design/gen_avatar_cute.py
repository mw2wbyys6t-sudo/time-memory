"""
时光记忆 · 卡通版头像
3 个可爱方案：时光小怪兽 / 记忆相机精灵 / 拍立得小人
4x 超采样保证平滑
"""
import math
import os
from PIL import Image, ImageDraw, ImageFilter

SIZE = 1024
SS = 4
CANVAS = SIZE * SS

PURPLE = (124, 108, 240)
PURPLE_LIGHT = (165, 150, 255)
PURPLE_DEEP = (98, 82, 200)
PINK = (255, 138, 161)
PINK_SOFT = (255, 180, 200)
YELLOW = (255, 200, 80)
ORANGE = (255, 160, 90)
WHITE = (255, 255, 255)
BLACK = (45, 40, 70)
CREAM = (255, 248, 235)


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


def radial_gradient(size, center_color, edge_color, cx_ratio=0.5, cy_ratio=0.42):
    w, h = size
    img = Image.new('RGB', (w, h), center_color)
    px = img.load()
    cx, cy = int(w * cx_ratio), int(h * cy_ratio)
    max_d = math.hypot(max(cx, w - cx), max(cy, h - cy))
    for y in range(h):
        for x in range(w):
            d = math.hypot(x - cx, y - cy) / max_d
            t = min(1, d * 1.05)
            r = int(center_color[0] + (edge_color[0] - center_color[0]) * t)
            g = int(center_color[1] + (edge_color[1] - center_color[1]) * t)
            b = int(center_color[2] + (edge_color[2] - center_color[2]) * t)
            px[x, y] = (r, g, b)
    return img


def downscale(img):
    return img.resize((SIZE, SIZE), Image.LANCZOS)


def draw_eye(draw, cx, cy, r, look=(0, 0)):
    """画一只卡通大眼睛：眼白 + 瞳孔 + 高光"""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WHITE)
    pr = r * 0.62
    px = cx + look[0] * r * 0.18
    py = cy + look[1] * r * 0.18
    draw.ellipse([px - pr, py - pr, px + pr, py + pr], fill=BLACK)
    hr = r * 0.26
    draw.ellipse([px - pr * 0.4 - hr, py - pr * 0.5 - hr,
                  px - pr * 0.4 + hr, py - pr * 0.5 + hr], fill=WHITE)
    hr2 = r * 0.13
    draw.ellipse([px + pr * 0.35 - hr2, py + pr * 0.35 - hr2,
                  px + pr * 0.35 + hr2, py + pr * 0.35 + hr2], fill=(255, 255, 255, 200))


def draw_blush(draw, cx, cy, r):
    """腮红：半透明粉色椭圆"""
    layer = Image.new('RGBA', (CANVAS, CANVAS), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.ellipse([cx - r, cy - r * 0.7, cx + r, cy + r * 0.7], fill=(255, 150, 175, 140))
    blurred = layer.filter(ImageFilter.GaussianBlur(CANVAS * 0.012))
    draw._image.paste(blurred, (0, 0), blurred)
    ImageDraw.Draw(draw._image if hasattr(draw, '_image') else None)


def draw_smile(draw, cx, cy, w, color=BLACK, lw=None):
    """画微笑弧线"""
    lw = lw or int(CANVAS * 0.022)
    draw.arc([cx - w, cy - w * 0.6, cx + w, cy + w * 0.9],
             start=20, end=160, fill=color, width=lw)


def scheme_d():
    """方案 D · 时光小怪兽：圆滚滚紫色身体 + 大眼 + 腮红 + 头顶时钟"""
    bg = radial_gradient((CANVAS, CANVAS), (190, 175, 255), (110, 95, 220),
                         cx_ratio=0.5, cy_ratio=0.4).convert('RGBA')
    d = ImageDraw.Draw(bg)
    cx = cy = CANVAS / 2

    body_r = CANVAS * 0.34
    by = cy + CANVAS * 0.04
    d.ellipse([cx - body_r * 1.05, by - body_r, cx + body_r * 1.05, by + body_r],
              fill=PURPLE_DEEP)
    d.ellipse([cx - body_r, by - body_r * 0.98, cx + body_r, by + body_r * 0.98],
              fill=PURPLE)
    hl_r = body_r * 0.7
    d.ellipse([cx - hl_r, by - body_r * 0.85 - hl_r * 0.6,
               cx + hl_r, by - body_r * 0.85 + hl_r * 0.6],
              fill=PURPLE_LIGHT)

    ear = CANVAS * 0.07
    for sign in (-1, 1):
        ex = cx + sign * body_r * 0.78
        ey = by - body_r * 0.78
        d.polygon([(ex - ear, ey), (ex + ear, ey), (ex, ey - ear * 1.8)],
                  fill=PURPLE_DEEP)
        d.polygon([(ex - ear * 0.5, ey + ear * 0.1),
                   (ex + ear * 0.5, ey + ear * 0.1),
                   (ex, ey - ear * 1.0)], fill=PINK)

    clock_r = CANVAS * 0.085
    ccy = by - body_r - clock_r * 0.35
    d.ellipse([cx - clock_r, ccy - clock_r, cx + clock_r, ccy + clock_r],
              fill=WHITE)
    d.ellipse([cx - clock_r, ccy - clock_r, cx + clock_r, ccy + clock_r],
              outline=PURPLE_DEEP, width=int(CANVAS * 0.014))
    for ang in range(0, 360, 90):
        a = math.radians(ang - 90)
        x1 = cx + clock_r * 0.72 * math.cos(a)
        y1 = ccy + clock_r * 0.72 * math.sin(a)
        x2 = cx + clock_r * 0.88 * math.cos(a)
        y2 = ccy + clock_r * 0.88 * math.sin(a)
        d.line([x1, y1, x2, y2], fill=BLACK, width=int(CANVAS * 0.014))
    ha = math.radians(60 - 90)
    ma = math.radians(135 - 90)
    d.line([cx, ccy, cx + clock_r * 0.45 * math.cos(ha),
            ccy + clock_r * 0.45 * math.sin(ha)], fill=BLACK, width=int(CANVAS * 0.022))
    d.line([cx, ccy, cx + clock_r * 0.6 * math.cos(ma),
            ccy + clock_r * 0.6 * math.sin(ma)], fill=ORANGE, width=int(CANVAS * 0.018))

    eye_y = by - body_r * 0.18
    eye_r = CANVAS * 0.075
    eye_dx = CANVAS * 0.13
    draw_eye(d, cx - eye_dx, eye_y, eye_r, look=(0.15, 0.1))
    draw_eye(d, cx + eye_dx, eye_y, eye_r, look=(0.15, 0.1))

    blush_layer = Image.new('RGBA', (CANVAS, CANVAS), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blush_layer)
    blush_r = CANVAS * 0.06
    for sign in (-1, 1):
        bd.ellipse([cx + sign * CANVAS * 0.235 - blush_r,
                    by + CANVAS * 0.04 - blush_r * 0.7,
                    cx + sign * CANVAS * 0.235 + blush_r,
                    by + CANVAS * 0.04 + blush_r * 0.7],
                   fill=(255, 150, 175, 150))
    bg.paste(blush_layer, (0, 0), blush_layer)

    draw_smile(d, cx, by + CANVAS * 0.14, CANVAS * 0.1)

    return downscale(bg)


def scheme_e():
    """方案 E · 记忆相机精灵：可爱相机 + 镜头大眼 + 闪光灯"""
    bg = radial_gradient((CANVAS, CANVAS), (255, 225, 200), (255, 165, 110),
                         cx_ratio=0.5, cy_ratio=0.4).convert('RGBA')
    d = ImageDraw.Draw(bg)
    cx = cy = CANVAS / 2

    bw = CANVAS * 0.62
    bh = CANVAS * 0.5
    bx0 = cx - bw / 2
    by0 = cy - bh / 2 + CANVAS * 0.02
    d.rounded_rectangle([bx0, by0, bx0 + bw, by0 + bh],
                        radius=CANVAS * 0.07, fill=PURPLE_DEEP)
    d.rounded_rectangle([bx0 + CANVAS * 0.03, by0 + CANVAS * 0.03,
                         bx0 + bw - CANVAS * 0.03, by0 + bh - CANVAS * 0.03],
                        radius=CANVAS * 0.06, fill=PURPLE)

    grip_w = CANVAS * 0.24
    grip_h = CANVAS * 0.07
    d.rounded_rectangle([cx - grip_w / 2, by0 - grip_h * 0.5,
                         cx + grip_w / 2, by0 + grip_h * 0.5],
                        radius=grip_h * 0.4, fill=PURPLE_DEEP)

    flash_w = CANVAS * 0.11
    fx = bx0 + CANVAS * 0.13
    fy = by0 + CANVAS * 0.16
    d.rounded_rectangle([fx, fy, fx + flash_w, fy + flash_w * 0.5],
                        radius=flash_w * 0.2, fill=YELLOW)
    for i in range(3):
        sx = fx + flash_w + CANVAS * 0.02 + i * CANVAS * 0.015
        d.line([sx, fy + flash_w * 0.1, sx + CANVAS * 0.02, fy + flash_w * 0.4],
               fill=YELLOW, width=int(CANVAS * 0.012))

    lens_r = CANVAS * 0.16
    lcx = cx + CANVAS * 0.04
    lcy = cy + CANVAS * 0.02
    d.ellipse([lcx - lens_r, lcy - lens_r, lcx + lens_r, lcy + lens_r],
              fill=PURPLE_DEEP)
    d.ellipse([lcx - lens_r * 0.85, lcy - lens_r * 0.85,
               lcx + lens_r * 0.85, lcy + lens_r * 0.85], fill=WHITE)
    pr = lens_r * 0.55
    d.ellipse([lcx - pr, lcy - pr, lcx + pr, lcy + pr], fill=(40, 50, 90))
    hr = lens_r * 0.28
    d.ellipse([lcx - pr * 0.5 - hr, lcy - pr * 0.6 - hr,
               lcx - pr * 0.5 + hr, lcy - pr * 0.6 + hr], fill=WHITE)
    d.ellipse([lcx - lens_r * 0.95, lcy - lens_r * 0.95,
               lcx + lens_r * 0.95, lcy + lens_r * 0.95],
              outline=PURPLE_LIGHT, width=int(CANVAS * 0.02))

    eye_r = CANVAS * 0.05
    ex = bx0 + bw * 0.78
    ey = by0 + bh * 0.32
    draw_eye(d, ex, ey, eye_r, look=(-0.3, 0.1))

    blush_layer = Image.new('RGBA', (CANVAS, CANVAS), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blush_layer)
    blush_r = CANVAS * 0.045
    bd.ellipse([ex - CANVAS * 0.135 - blush_r, ey + CANVAS * 0.075 - blush_r * 0.7,
                ex - CANVAS * 0.135 + blush_r, ey + CANVAS * 0.075 + blush_r * 0.7],
               fill=(255, 150, 175, 150))
    bd.ellipse([ex + CANVAS * 0.135 - blush_r, ey + CANVAS * 0.075 - blush_r * 0.7,
                ex + CANVAS * 0.135 + blush_r, ey + CANVAS * 0.075 + blush_r * 0.7],
               fill=(255, 150, 175, 150))
    bg.paste(blush_layer, (0, 0), blush_layer)

    draw_smile(d, ex + CANVAS * 0.005, ey + CANVAS * 0.17, CANVAS * 0.07)

    btn_r = CANVAS * 0.04
    d.ellipse([bx0 + bw - CANVAS * 0.16 - btn_r, by0 + bh - CANVAS * 0.14 - btn_r,
               bx0 + bw - CANVAS * 0.16 + btn_r, by0 + bh - CANVAS * 0.14 + btn_r],
              fill=YELLOW)
    d.ellipse([bx0 + bw - CANVAS * 0.16 - btn_r * 0.5,
               by0 + bh - CANVAS * 0.14 - btn_r * 0.5,
               bx0 + bw - CANVAS * 0.16 + btn_r * 0.5,
               by0 + bh - CANVAS * 0.14 + btn_r * 0.5], fill=WHITE)

    return downscale(bg)


def scheme_f():
    """方案 F · 拍立得小人：拍立得化身可爱小人 + 照片里有星空"""
    bg = radial_gradient((CANVAS, CANVAS), (175, 255, 220), (90, 200, 170),
                         cx_ratio=0.5, cy_ratio=0.4).convert('RGBA')
    d = ImageDraw.Draw(bg)
    cx = cy = CANVAS / 2

    body_w = CANVAS * 0.5
    body_h = CANVAS * 0.58
    bx0 = cx - body_w / 2
    by0 = cy - body_h / 2 + CANVAS * 0.03
    d.rounded_rectangle([bx0, by0, bx0 + body_w, by0 + body_h],
                        radius=CANVAS * 0.05, fill=WHITE)
    d.rounded_rectangle([bx0, by0, bx0 + body_w, by0 + body_h],
                        radius=CANVAS * 0.05, outline=PURPLE_DEEP,
                        width=int(CANVAS * 0.012))

    photo_w = body_w * 0.78
    photo_h = body_h * 0.58
    px0 = cx - photo_w / 2
    py0 = by0 + (body_h - photo_h) * 0.22
    photo_box = [px0, py0, px0 + photo_w, py0 + photo_h]
    d.rounded_rectangle(photo_box, radius=CANVAS * 0.02, fill=PURPLE_DEEP)

    sky = Image.new('RGBA', (int(photo_w), int(photo_h)), PURPLE_DEEP)
    sd = ImageDraw.Draw(sky)
    import random
    random.seed(7)
    for _ in range(45):
        sx = random.randint(0, int(photo_w))
        sy = random.randint(0, int(photo_h))
        sr = random.randint(1, 3) * SS
        sd.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                   fill=(255, 255, random.randint(180, 230)))
    moon_r = photo_h * 0.18
    mcx = photo_w * 0.72
    mcy = photo_h * 0.3
    sd.ellipse([mcx - moon_r, mcy - moon_r, mcx + moon_r, mcy + moon_r],
               fill=YELLOW)
    sd.ellipse([mcx - moon_r * 0.4, mcy - moon_r * 0.3,
                mcx + moon_r * 0.4, mcy + moon_r * 0.5], fill=YELLOW)
    bg.paste(sky, (int(px0), int(py0)), sky)

    leg_w = CANVAS * 0.06
    leg_h = CANVAS * 0.1
    for sign in (-1, 1):
        lx = cx + sign * body_w * 0.22
        ly = by0 + body_h + leg_h * 0.3
        d.ellipse([lx - leg_w, ly - leg_h, lx + leg_w, ly + leg_h * 0.3],
                  fill=PURPLE_DEEP)
        d.ellipse([lx - leg_w * 0.9, ly + leg_h * 0.15,
                   lx + leg_w * 0.9, ly + leg_h * 0.5],
                  fill=PURPLE)

    arm_w = CANVAS * 0.035
    arm_l = CANVAS * 0.14
    for sign in (-1, 1):
        ax = bx0 if sign < 0 else bx0 + body_w
        ay = py0 + photo_h + CANVAS * 0.04
        tip_x = ax + sign * arm_l
        tip_y = ay + CANVAS * 0.02
        d.line([ax, ay, tip_x, tip_y], fill=PURPLE_DEEP,
               width=int(arm_w * 2))
        d.ellipse([tip_x - arm_w, tip_y - arm_w, tip_x + arm_w, tip_y + arm_w],
                  fill=WHITE)
        d.ellipse([tip_x - arm_w, tip_y - arm_w, tip_x + arm_w, tip_y + arm_w],
                  outline=PURPLE_DEEP, width=int(CANVAS * 0.008))

    eye_r = CANVAS * 0.032
    ey = py0 + photo_h + CANVAS * 0.06
    draw_eye(d, cx - CANVAS * 0.07, ey, eye_r, look=(0, 0.15))
    draw_eye(d, cx + CANVAS * 0.07, ey, eye_r, look=(0, 0.15))

    draw_smile(d, cx, ey + CANVAS * 0.075, CANVAS * 0.045,
               color=PURPLE_DEEP, lw=int(CANVAS * 0.016))

    blush_layer = Image.new('RGBA', (CANVAS, CANVAS), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blush_layer)
    blush_r = CANVAS * 0.038
    bd.ellipse([cx - CANVAS * 0.14 - blush_r, ey + CANVAS * 0.005 - blush_r * 0.7,
                cx - CANVAS * 0.14 + blush_r, ey + CANVAS * 0.005 + blush_r * 0.7],
               fill=(255, 150, 175, 150))
    bd.ellipse([cx + CANVAS * 0.14 - blush_r, ey + CANVAS * 0.005 - blush_r * 0.7,
                cx + CANVAS * 0.14 + blush_r, ey + CANVAS * 0.005 + blush_r * 0.7],
               fill=(255, 150, 175, 150))
    bg.paste(blush_layer, (0, 0), blush_layer)

    return downscale(bg)


def export(img, name):
    out_dir = '/workspace/design/avatar'
    os.makedirs(out_dir, exist_ok=True)
    img.convert('RGB').save(os.path.join(out_dir, name), 'PNG')
    img.convert('RGB').resize((144, 144), Image.LANCZOS).save(
        os.path.join(out_dir, name.replace('.png', '_144.png')), 'PNG')


if __name__ == '__main__':
    export(scheme_d(), 'avatar_d_monster.png')
    export(scheme_e(), 'avatar_e_camera.png')
    export(scheme_f(), 'avatar_f_polaroid.png')
    print('done')
