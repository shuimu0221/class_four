"""生成三张概念示意图（PIL），风格对齐 PPT 配色。

产出到 lecture4/yolo/docs/ppt_images/。
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

R = r"C:/Users/ziang.xu/Documents/sp/class_four"
OUT = os.path.join(R, "lecture4/yolo/docs/ppt_images")
os.makedirs(OUT, exist_ok=True)

BG = (244, 246, 250)
PANEL = (255, 255, 255)
ACCENT = (20, 201, 140)
ACCENT2 = (61, 90, 254)
WARN = (224, 106, 59)
TEXT = (32, 36, 51)
MUTE = (91, 99, 119)
LINE = (200, 208, 220)

FONT_PATH = r"C:/Windows/Fonts/msyh.ttc"
FONT_BOLD = r"C:/Windows/Fonts/msyhbd.ttc"


def F(size, bold=False):
    p = FONT_BOLD if bold else FONT_PATH
    try:
        return ImageFont.truetype(p, size)
    except OSError:
        return ImageFont.truetype(FONT_PATH, size)


def rrect(d, box, r, fill=None, outline=None, width=2):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def ctext(d, box, text, font, fill=TEXT, dy=0):
    x0, y0, x1, y1 = box
    l, t, r, b = d.textbbox((0, 0), text, font=font)
    d.text(((x0 + x1 - (r - l)) / 2 - l, (y0 + y1 - (b - t)) / 2 - t + dy),
           text, font=font, fill=fill)


def arrow(d, p0, p1, color=ACCENT2, w=4, head=14):
    d.line([p0, p1], fill=color, width=w)
    import math
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    for s in (+1, -1):
        a = ang + s * math.radians(152)
        d.line([p1, (p1[0] + head * math.cos(a), p1[1] + head * math.sin(a))],
               fill=color, width=w)


# ---------------- s05: Armor 结构体 ----------------
def s05():
    W, H = 1280, 720
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((40, 28), "detector.detect(img)  →  Armor 列表  →  Armor.points", font=F(30, True), fill=TEXT)

    # 左：检测到的装甲板
    rrect(d, (60, 120, 580, 620), 18, fill=PANEL, outline=LINE, width=2)
    d.text((90, 142), "图像上检测到的装甲板", font=F(24, True), fill=MUTE)
    pts = [(180, 250), (470, 300), (430, 490), (140, 440)]
    d.polygon(pts, outline=ACCENT)
    for i, (x, y) in enumerate(pts):
        d.ellipse((x - 13, y - 13, x + 13, y + 13), fill=ACCENT, outline=(255, 255, 255), width=3)
        d.text((x + 20, y - 36), str(i), font=F(30, True), fill=ACCENT)
    for i, lb in enumerate(["0 = 左上", "1 = 右上", "2 = 右下", "3 = 左下"]):
        d.text((300, 520 + i * 26), lb, font=F(20), fill=TEXT)

    arrow(d, (600, 360), (716, 360), ACCENT2, 5, 18)

    # 右：结构体（每行留足间距，避免注释压行）
    rrect(d, (736, 120, 1220, 620), 18, fill=PANEL, outline=LINE, width=2)
    d.text((766, 142), "struct Armor", font=F(26, True), fill=TEXT)
    d.text((766, 200), "std::vector<cv::Point2f> points;", font=F(21), fill=ACCENT)
    d.text((766, 232), "↑ 本讲只用它，4 个关键点", font=F(19), fill=ACCENT)
    d.text((766, 300), "Lightbar left;", font=F(21), fill=MUTE)
    d.text((766, 332), "↑ 从未赋值，取出来是 (0,0)", font=F(19), fill=WARN)
    d.text((766, 400), "Lightbar right;", font=F(21), fill=MUTE)
    d.text((766, 432), "↑ 传统灯条法的历史包袱", font=F(19), fill=WARN)
    d.line([(766, 486), (1190, 486)], fill=LINE, width=2)
    d.text((766, 506), "points[0..3] 顺序：", font=F(21, True), fill=TEXT)
    d.text((766, 538), "左上 → 右上 → 右下 → 左下", font=F(22, True), fill=ACCENT)

    im.save(os.path.join(OUT, "s05_armor_struct.png"))
    return "s05_armor_struct.png"


# ---------------- s12: PnP 原理 ----------------
def s12():
    W, H = 1280, 720
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((60, 40), "Perspective-n-Points：从对应点解出位姿", font=F(30, True), fill=TEXT)

    # 装甲板坐标系
    rrect(d, (60, 130, 420, 500), 18, fill=PANEL, outline=LINE, width=2)
    d.text((90, 152), "装甲板坐标系（3D）", font=F(23, True), fill=TEXT)
    box3 = [(150, 250), (330, 250), (330, 390), (150, 390)]
    d.polygon(box3, outline=ACCENT2)
    for i, (x, y) in enumerate(box3):
        d.ellipse((x - 11, y - 11, x + 11, y + 11), fill=ACCENT2)
        d.text((x + 16, y - 30), f"P{i+1}", font=F(19, True), fill=ACCENT2)
    d.text((90, 430), "已知：4 个点的 3D 坐标", font=F(19), fill=MUTE)

    # 图像平面
    rrect(d, (510, 130, 870, 500), 18, fill=PANEL, outline=LINE, width=2)
    d.text((540, 152), "图像平面（2D 像素）", font=F(23, True), fill=TEXT)
    d.rectangle((590, 240, 790, 400), outline=LINE, width=2)
    box2 = [(636, 275), (752, 288), (744, 372), (628, 360)]
    d.polygon(box2, outline=ACCENT)
    for i, (x, y) in enumerate(box2):
        d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=ACCENT)
        d.text((x + 15, y - 28), f"p{i+1}", font=F(19, True), fill=ACCENT)
    d.text((540, 430), "已知：4 个点的像素坐标", font=F(19), fill=MUTE)

    # 相机内参
    rrect(d, (960, 190, 1220, 440), 18, fill=PANEL, outline=LINE, width=2)
    d.text((988, 214), "相机内参 K + 畸变 D", font=F(21, True), fill=TEXT)
    d.text((988, 252), "已知（已标定）", font=F(19), fill=MUTE)
    d.line([(988, 296), (1192, 296)], fill=LINE, width=2)
    d.text((988, 318), "求解 →", font=F(21, True), fill=MUTE)
    d.text((988, 352), "R, t", font=F(34, True), fill=WARN)
    d.text((988, 398), "即 rvec / tvec", font=F(19), fill=MUTE)

    arrow(d, (432, 315), (498, 315), ACCENT2, 5, 16)
    d.text((437, 268), "一一对应", font=F(18), fill=MUTE)
    arrow(d, (882, 315), (948, 315), ACCENT2, 5, 16)

    d.text((60, 570), "4 组一一对应的 3D–2D 点  +  相机内参  +  畸变系数", font=F(24, True), fill=TEXT)
    d.text((60, 614), "↓", font=F(26, True), fill=ACCENT2)
    d.text((60, 650), "解出装甲板相对相机的旋转 R 与平移 t", font=F(24, True), fill=ACCENT)

    im.save(os.path.join(OUT, "s12_pnp_principle.png"))
    return "s12_pnp_principle.png"


# ---------------- s25: 旋转表示法 ----------------
def s25():
    W, H = 1280, 620
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)

    def node(box, title, sub, color):
        rrect(d, box, 16, fill=PANEL, outline=color, width=3)
        x0, y0, x1, y1 = box
        ctext(d, (x0, y0 + 8, x1, y0 + 62), title, F(28, True), color)
        ctext(d, (x0, y0 + 58, x1, y1), sub, F(19), MUTE)

    node((60, 210, 320, 350), "rvec", "3×1 旋转向量\n方向=轴，模长=角(弧度)", ACCENT2)
    node((470, 210, 760, 350), "rmat", "3×3 旋转矩阵", ACCENT)
    node((910, 120, 1220, 250), "欧拉角", "yaw / pitch / roll\n直观，但有万向锁", WARN)
    node((910, 350, 1220, 480), "四元数", "(w, x, y, z)\n无奇异点，插值稳健", ACCENT2)

    arrow(d, (330, 280), (458, 280), ACCENT, 5, 18)
    d.text((286, 230), "cv::Rodrigues", font=F(19, True), fill=ACCENT)
    d.text((330, 306), "（可逆）", font=F(18), fill=MUTE)

    arrow(d, (772, 250), (898, 195), WARN, 5, 18)
    d.text((790, 168), "反三角函数", font=F(21, True), fill=WARN)
    arrow(d, (772, 315), (898, 400), ACCENT2, 5, 18)
    d.text((790, 372), "直接转换", font=F(21, True), fill=ACCENT2)

    d.text((60, 60), "同一个旋转，四种写法——它们说的是同一件事", font=F(30, True), fill=TEXT)
    d.text((60, 520), "本讲主线：rvec → rmat → 欧拉角；四元数只做定性了解", font=F(22), fill=MUTE)

    im.save(os.path.join(OUT, "s25_rotation_chain.png"))
    return "s25_rotation_chain.png"


for fn in (s05, s12, s25):
    sys.stderr.write("wrote " + fn() + "\n")


# ---------------- s08: 飞机 yaw/pitch/roll ----------------
def s08():
    W, H = 1280, 660
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((60, 40), "yaw / pitch / roll —— 三个角，描述任意朝向", font=F(30, True), fill=TEXT)

    items = [
        ("yaw", "偏航", "绕竖直轴", "左右扭头", ACCENT2),
        ("pitch", "俯仰", "绕左右轴", "抬头低头", ACCENT),
        ("roll", "横滚", "绕前后轴", "侧身歪头", WARN),
    ]
    x0, w, gap = 60, 380, 30
    for k, (en, zh, axis, how, col) in enumerate(items):
        l = x0 + k * (w + gap)
        rrect(d, (l, 120, l + w, 500), 18, fill=PANEL, outline=col, width=3)
        ctext(d, (l, 140, l + w, 200), en, F(34, True), col)
        ctext(d, (l, 196, l + w, 240), zh, F(24, True), TEXT)
        ctext(d, (l, 258, l + w, 300), axis, F(21), MUTE)
        ctext(d, (l, 300, l + w, 342), how, F(21), MUTE)
        cx, cy = l + w // 2, 420
        if k == 0:
            d.arc((cx - 62, cy - 26, cx + 62, cy + 26), 0, 360, fill=col, width=4)
            d.line([(cx, cy - 26), (cx, cy - 58)], fill=col, width=4)
        elif k == 1:
            d.arc((cx - 62, cy - 40, cx + 62, cy + 40), 200, 340, fill=col, width=4)
            d.line([(cx + 46, cy - 22), (cx + 60, cy - 44)], fill=col, width=4)
        else:
            d.arc((cx - 62, cy - 40, cx + 62, cy + 40), 20, 160, fill=col, width=4)
            d.line([(cx - 46, cy - 22), (cx - 60, cy - 44)], fill=col, width=4)

    d.text((60, 560), "装甲板的朝向，就是这三个角；solvePnP 解出的 rvec 最终会变成它们。",
           font=F(23, True), fill=TEXT)

    im.save(os.path.join(OUT, "s08_yaw_pitch_roll.png"))
    return "s08_yaw_pitch_roll.png"


# ---------------- s09: 两个坐标系 ----------------
def s09():
    W, H = 1280, 680
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((60, 36), "先认清两个坐标系", font=F(30, True), fill=TEXT)

    def frame(box, title, tcol, ox, oy, show_z):
        rrect(d, box, 18, fill=PANEL, outline=tcol, width=3)
        d.text((box[0] + 30, box[1] + 24), title, font=F(23, True), fill=tcol)
        d.rectangle((ox - 105, oy - 185, ox + 105, oy - 65), outline=LINE, width=2)
        d.ellipse((ox - 9, oy - 9, ox + 9, oy + 9), fill=TEXT)
        arrow(d, (ox, oy), (ox + 115, oy), WARN, 5, 14)          # +x 右
        d.text((ox + 124, oy - 14), "x", font=F(26, True), fill=WARN)
        arrow(d, (ox, oy), (ox, oy + 85), ACCENT, 5, 14)          # +y 下
        d.text((ox + 12, oy + 92), "y", font=F(26, True), fill=ACCENT)
        if show_z:
            arrow(d, (ox, oy), (ox + 82, oy - 82), ACCENT2, 5, 14)  # +z 进屏
            d.text((ox + 90, oy - 110), "z", font=F(26, True), fill=ACCENT2)

    frame((70, 110, 590, 470), "装甲板坐标系（物体坐标系）", ACCENT, 260, 350, False)
    d.text((100, 496), "原点 = 装甲板中心", font=F(20), fill=MUTE)
    d.text((100, 528), "+x 向右　+y 向下　z = 0（四点共面）", font=F(20), fill=MUTE)

    frame((690, 110, 1210, 470), "相机坐标系", ACCENT2, 880, 350, True)
    d.text((720, 496), "原点 = 相机光心", font=F(20), fill=MUTE)
    d.text((720, 528), "+x 向右　+y 向下　+z 指向镜头前方", font=F(20), fill=MUTE)

    d.text((60, 596), "solvePnP 求的，就是装甲板坐标系到相机坐标系的 R 和 t。",
           font=F(23, True), fill=TEXT)

    im.save(os.path.join(OUT, "s09_two_frames.png"))
    return "s09_two_frames.png"


sys.stderr.write("wrote " + s08() + "\n")
sys.stderr.write("wrote " + s09() + "\n")
