# -*- coding: utf-8 -*-
"""Generate Lecture 4 "Hello Armor" slide deck."""
import os
import re

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# 输出到脚本所在目录（= 仓库根）。不要写死绝对路径：仓库搬过一次，
# 写死的路径会让脚本一跑就 FileNotFoundError。
HERE = os.path.dirname(os.path.abspath(__file__))
assert os.path.isdir(os.path.join(HERE, "lecture4")), (
    f"脚本似乎不在仓库根目录下（找不到 {HERE}/lecture4）。请从仓库根运行本脚本。"
)
# 设 LECTURE4_OUT_DIR 可以把产物生成到别处，便于与已发布版做 diff 对账。
OUT_DIR = os.environ.get("LECTURE4_OUT_DIR") or HERE

# ---------- palette ----------
BG_DARK = RGBColor(0x0E, 0x16, 0x2B)
BG_LIGHT = RGBColor(0xFF, 0xFF, 0xFF)
BG_PANEL = RGBColor(0xF4, 0xF6, 0xFA)
ACCENT = RGBColor(0x14, 0xC9, 0x8C)      # SP green
ACCENT2 = RGBColor(0x3D, 0x5A, 0xFE)     # blue
WARN = RGBColor(0xE0, 0x6A, 0x3B)        # orange for warnings/tasks
TEXT_DARK = RGBColor(0x20, 0x24, 0x33)
TEXT_MUTE = RGBColor(0x5B, 0x63, 0x77)
TEXT_LIGHT = RGBColor(0xF3, 0xF5, 0xF9)
TEXT_LIGHT_MUTE = RGBColor(0xA9, 0xB4, 0xC9)
CODE_BG = RGBColor(0x1E, 0x1E, 0x1E)
CODE_TEXT = RGBColor(0xD4, 0xD4, 0xD4)
CODE_COMMENT = RGBColor(0x6A, 0x99, 0x55)
CODE_ACCENT = RGBColor(0x9C, 0xDC, 0xFE)

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

prs = Presentation()
prs.slide_width = SLIDE_W
prs.slide_height = SLIDE_H
BLANK = prs.slide_layouts[6]

PART_LABELS = {}
_slide_no = [0]
_part_total = [8]


def new_slide():
    return prs.slides.add_slide(BLANK)


def set_bg(slide, color):
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = color


def add_rect(slide, l, t, w, h, color, line=False, shadow=False, round_=False):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if round_ else MSO_SHAPE.RECTANGLE
    sp = slide.shapes.add_shape(shape_type, l, t, w, h)
    sp.fill.solid()
    sp.fill.fore_color.rgb = color
    if not line:
        sp.line.fill.background()
    sp.shadow.inherit = False
    if round_:
        try:
            sp.adjustments[0] = 0.06
        except Exception:
            pass
    return sp


def _apply_inline_bold(paragraph, text, base_size, base_color, bold_color=None, base_bold=False):
    """Support **bold** spans inside bullet text."""
    bold_color = bold_color or base_color
    parts = re.split(r"(\*\*[^*]+\*\*)", text)
    for part in parts:
        if not part:
            continue
        run = paragraph.add_run()
        if part.startswith("**") and part.endswith("**"):
            run.text = part[2:-2]
            run.font.bold = True
            run.font.color.rgb = bold_color
        else:
            run.text = part
            run.font.bold = base_bold
            run.font.color.rgb = base_color
        run.font.size = base_size
        run.font.name = "Microsoft YaHei"


def add_bullets(tf, bullets, base_size=20, color=TEXT_DARK, bold_color=None, line_spacing=1.18):
    """bullets: list of (text, level) or (text, level, marker_override)"""
    tf.word_wrap = True
    first = True
    for item in bullets:
        text, level = item[0], item[1]
        marker = item[2] if len(item) > 2 else None
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.level = 0
        p.line_spacing = line_spacing
        p.space_after = Pt(10 if level == 0 else 6)
        indent = "      " * level
        lead = marker if marker is not None else ("· " if level == 0 else "‑ ")
        size = base_size if level == 0 else base_size - 3
        _apply_inline_bold(p, indent + lead + text, Pt(size), color, bold_color)


def add_footer(slide, part_no, part_name, dark=False):
    # 页脚印的是「真实幻灯片序号」，与讲稿里的「翻到第 N 页」口径一致。
    # 不要用自增计数器：封面不调用 add_footer，自增会让页脚整体比序号少 1。
    _slide_no[0] = len(prs.slides._sldIdLst)
    color = TEXT_LIGHT_MUTE if dark else TEXT_MUTE
    left = slide.shapes.add_textbox(Inches(0.5), Inches(7.08), Inches(9.5), Inches(0.32))
    lp = left.text_frame.paragraphs[0]
    lr = lp.add_run()
    lr.text = f"Hello Armor · 装甲板位姿解算    P{part_no} {part_name}"
    lr.font.size = Pt(10)
    lr.font.name = "Consolas"
    lr.font.color.rgb = color
    right = slide.shapes.add_textbox(Inches(12.2), Inches(7.08), Inches(0.65), Inches(0.32))
    rp = right.text_frame.paragraphs[0]
    rp.alignment = PP_ALIGN.RIGHT
    rr = rp.add_run()
    rr.text = f"{_slide_no[0]:02d}"
    rr.font.size = Pt(10)
    rr.font.name = "Consolas"
    rr.font.color.rgb = color


def add_kicker(slide, text, dark=False):
    box = slide.shapes.add_textbox(Inches(0.55), Inches(0.35), Inches(8), Inches(0.4))
    tf = box.text_frame
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = text
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.name = "Consolas"
    run.font.color.rgb = ACCENT


def add_title(slide, text, top=Inches(0.72), size=30, color=TEXT_DARK, width=Inches(12.3)):
    box = slide.shapes.add_textbox(Inches(0.55), top, width, Inches(0.9))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = True
    run.font.name = "Microsoft YaHei"
    run.font.color.rgb = color


def add_code_box(slide, code, l, t, w, h, font_size=13.5):
    box = add_rect(slide, l, t, w, h, CODE_BG, round_=True)
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.22)
    tf.margin_right = Inches(0.18)
    tf.margin_top = Inches(0.16)
    tf.margin_bottom = Inches(0.16)
    lines = code.strip("\n").split("\n")
    first = True
    for line in lines:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.line_spacing = 1.05
        run = p.add_run()
        run.text = line if line.strip() else " "
        run.font.name = "Consolas"
        run.font.size = Pt(font_size)
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("#"):
            run.font.color.rgb = CODE_COMMENT
        elif stripped.startswith("////") or "####" in stripped:
            run.font.color.rgb = CODE_ACCENT
        else:
            run.font.color.rgb = CODE_TEXT
    return box


def add_caption_box(slide, text, l, t, w, h, color=TEXT_MUTE, size=12, align=PP_ALIGN.LEFT, italic=True):
    box = slide.shapes.add_textbox(l, t, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.italic = italic
    run.font.name = "Microsoft YaHei"
    run.font.color.rgb = color


# 已生成的配图：占位标签里出现左边这个关键词，就换成右边的真图。
# 生成脚本见 build_ppt_images.py；清单（含还需实拍/截图的）见 docs/ppt_images/README.md。
IMAGE_KEYS = [
    ("Armor 结构体", "s05_armor_struct.png"),
    ("不同距离", "s06_distance_angle.png"),
    ("飞机 yaw", "s08_yaw_pitch_roll.png"),
    ("双坐标轴", "s09_two_frames.png"),
    ("经典 PnP 示意图", "s12_pnp_principle.png"),
    ("绿点标注", "s16_armor_points.png"),
    ("左图点序正确", "s18_order_compare.png"),
    ("三行数字", "s23_s32_runtime_overlay.png"),
    ("三行数值", "s23_s32_runtime_overlay.png"),
    ("流程示意图", "s25_rotation_chain.png"),
    ("左右对比截图", "s31_reproj_compare.png"),
]


def add_image_placeholder(slide, l, t, w, h, label, dark_ok=False):
    """有真图就用真图，没有就画占位框。

    真图放在 lecture4/yolo/docs/ppt_images/ 下。
    见该目录的 README.md：哪些已生成、哪些还需要实拍或截图。
    """
    for needle, fn in IMAGE_KEYS:
        if needle not in label:
            continue
        path = os.path.join(HERE, "lecture4/yolo/docs/ppt_images", fn)
        if not os.path.exists(path):
            break
        pic = slide.shapes.add_picture(path, l, t, width=w)
        if pic.height > h:                      # 太高就按高度收缩并居中
            ratio = h / pic.height
            pic.height = int(pic.height * ratio)
            pic.width = int(pic.width * ratio)
            pic.left = int(l + (w - pic.width) / 2)
        else:                                   # 否则按宽度居中
            pic.top = int(t + (h - pic.height) / 2)
        return pic
    box = add_rect(slide, l, t, w, h, RGBColor(0xE7, 0xEB, 0xF3), round_=True)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "🖼  " + label
    run.font.size = Pt(13)
    run.font.italic = True
    run.font.name = "Microsoft YaHei"
    run.font.color.rgb = TEXT_MUTE
    return box


def add_task_tag(slide, text, l, t, color=WARN):
    w = Inches(1.9)
    tag = add_rect(slide, l, t, w, Inches(0.42), color, round_=True)
    tf = tag.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = text
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    run.font.name = "Microsoft YaHei"


# ---------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------

def slide_title():
    s = new_slide()
    set_bg(s, BG_DARK)
    add_rect(s, Inches(0), Inches(0), Inches(0.18), SLIDE_H, ACCENT)
    box = s.shapes.add_textbox(Inches(0.9), Inches(2.35), Inches(10.5), Inches(0.5))
    p = box.text_frame.paragraphs[0]
    r = p.add_run(); r.text = "视觉组第四讲 · HELLO ARMOR"
    r.font.size = Pt(18); r.font.bold = True; r.font.color.rgb = ACCENT; r.font.name = "Consolas"

    box2 = s.shapes.add_textbox(Inches(0.85), Inches(2.75), Inches(11.5), Inches(1.6))
    p2 = box2.text_frame.paragraphs[0]
    r2 = p2.add_run(); r2.text = "装甲板位姿解算"
    r2.font.size = Pt(52); r2.font.bold = True; r2.font.color.rgb = TEXT_LIGHT; r2.font.name = "Microsoft YaHei"
    p3 = box2.text_frame.add_paragraph()
    r3 = p3.add_run(); r3.text = "从 2D 识别结果到 3D 位姿：cv::solvePnP 全流程实战"
    r3.font.size = Pt(20); r3.font.color.rgb = TEXT_LIGHT_MUTE; r3.font.name = "Microsoft YaHei"

    box3 = s.shapes.add_textbox(Inches(0.9), Inches(6.3), Inches(10), Inches(0.6))
    p4 = box3.text_frame.paragraphs[0]
    r4 = p4.add_run(); r4.text = "主讲人：______　　助教：______　　时长：90 分钟　　承接 Lecture 3《Hello Modern C++》"
    r4.font.size = Pt(14); r4.font.color.rgb = TEXT_LIGHT_MUTE; r4.font.name = "Microsoft YaHei"
    add_image_placeholder(s, Inches(10.6), Inches(0.5), Inches(2.2), Inches(1.2), "SP 队徽", )


def slide_toc():
    s = new_slide(); set_bg(s, BG_LIGHT)
    add_kicker(s, "课程地图 · Roadmap")
    add_title(s, "今天 90 分钟，我们要走完这条链路")
    items = [
        ("P0", "复习导入：你 lecture2 作业里那套 YOLO 检测器", "5 min"),
        ("P1", "为什么装甲板需要“位姿”而不只是位置", "6 min"),
        ("P2", "PnP 原理与 cv::solvePnP 接口精讲", "13 min"),
        ("P3", "动手实验一：Task 01~03，解出 tvec / rvec", "24 min"),
        ("P4", "rvec 揭秘：旋转向量／矩阵／欧拉角／四元数", "14 min"),
        ("P5", "动手实验二：Task 04~05，把旋转变成角度", "16 min"),
        ("P6", "坐标系全景：从像素到机器人本体 / IMU", "6 min"),
        ("P7", "总结、答疑与作业布置", "3 min"),
    ]
    top = Inches(1.75)
    for i, (tag, text, mins) in enumerate(items):
        row_t = top + Inches(0.62) * i
        add_rect(s, Inches(0.55), row_t, Inches(0.85), Inches(0.46), ACCENT, round_=True)
        tb = s.shapes.add_textbox(Inches(0.55), row_t, Inches(0.85), Inches(0.46))
        tb.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        pp = tb.text_frame.paragraphs[0]; pp.alignment = PP_ALIGN.CENTER
        rr = pp.add_run(); rr.text = tag; rr.font.bold = True; rr.font.size = Pt(15); rr.font.color.rgb = RGBColor(255,255,255)
        tb2 = s.shapes.add_textbox(Inches(1.6), row_t, Inches(9.6), Inches(0.46))
        tb2.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        pp2 = tb2.text_frame.paragraphs[0]
        rr2 = pp2.add_run(); rr2.text = text; rr2.font.size = Pt(16); rr2.font.color.rgb = TEXT_DARK; rr2.font.name="Microsoft YaHei"
        tb3 = s.shapes.add_textbox(Inches(11.3), row_t, Inches(1.4), Inches(0.46))
        tb3.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        pp3 = tb3.text_frame.paragraphs[0]; pp3.alignment = PP_ALIGN.RIGHT
        rr3 = pp3.add_run(); rr3.text = mins; rr3.font.size = Pt(14); rr3.font.color.rgb = TEXT_MUTE; rr3.font.name="Consolas"
    add_footer(s, 0, "课程地图")


def slide_section(part_no, part_name, sub, next_hint=None):
    s = new_slide(); set_bg(s, BG_DARK)
    add_rect(s, Inches(0), Inches(0), Inches(0.18), SLIDE_H, ACCENT)
    box = s.shapes.add_textbox(Inches(0.9), Inches(2.7), Inches(3), Inches(1.4))
    p = box.text_frame.paragraphs[0]
    r = p.add_run(); r.text = f"P{part_no}"
    r.font.size = Pt(64); r.font.bold = True; r.font.color.rgb = ACCENT; r.font.name = "Consolas"
    box2 = s.shapes.add_textbox(Inches(3.6), Inches(2.95), Inches(9.0), Inches(1.4))
    p2 = box2.text_frame.paragraphs[0]
    r2 = p2.add_run(); r2.text = part_name
    r2.font.size = Pt(36); r2.font.bold = True; r2.font.color.rgb = TEXT_LIGHT; r2.font.name = "Microsoft YaHei"
    if sub:
        p3 = box2.text_frame.add_paragraph()
        r3 = p3.add_run(); r3.text = sub
        r3.font.size = Pt(18); r3.font.color.rgb = TEXT_LIGHT_MUTE; r3.font.name = "Microsoft YaHei"
    add_footer(s, part_no, part_name, dark=True)


def slide_content(part_no, part_name, title, bullets, kicker=None, image_label=None, caption=None, base_size=20):
    s = new_slide(); set_bg(s, BG_LIGHT)
    if kicker:
        add_kicker(s, kicker)
    add_title(s, title, top=Inches(0.85 if kicker else 0.55))
    body_w = Inches(7.5) if image_label else Inches(11.9)
    box = s.shapes.add_textbox(Inches(0.6), Inches(1.85), body_w, Inches(4.9))
    add_bullets(box.text_frame, bullets, base_size=base_size, bold_color=ACCENT2)
    if image_label:
        add_image_placeholder(s, Inches(8.35), Inches(1.9), Inches(4.35), Inches(4.3), image_label)
        if caption:
            add_caption_box(s, caption, Inches(8.35), Inches(6.25), Inches(4.35), Inches(0.6))
    add_footer(s, part_no, part_name)
    return s


def slide_code(part_no, part_name, title, intro_bullets, code, hint_bullets=None, task_tag=None, kicker=None, code_h=Inches(3.1)):
    s = new_slide(); set_bg(s, BG_LIGHT)
    if kicker:
        add_kicker(s, kicker)
    add_title(s, title, top=Inches(0.85 if kicker else 0.55))
    if task_tag:
        add_task_tag(s, task_tag, Inches(10.9), Inches(0.55))
    box = s.shapes.add_textbox(Inches(0.6), Inches(1.75), Inches(12.1), Inches(1.1))
    add_bullets(box.text_frame, intro_bullets, base_size=16, bold_color=ACCENT2)
    add_code_box(s, code, Inches(0.6), Inches(2.75), Inches(12.15), code_h)
    if hint_bullets:
        box2 = s.shapes.add_textbox(Inches(0.6), Inches(2.75) + code_h + Inches(0.12), Inches(12.1), Inches(1.2))
        add_bullets(box2.text_frame, hint_bullets, base_size=14, color=TEXT_MUTE, bold_color=ACCENT2)
    add_footer(s, part_no, part_name)
    return s


def slide_compare(part_no, part_name, title, left_title, left_bullets, right_title, right_bullets, kicker=None):
    s = new_slide(); set_bg(s, BG_LIGHT)
    if kicker: add_kicker(s, kicker)
    add_title(s, title, top=Inches(0.85 if kicker else 0.55))
    add_rect(s, Inches(0.6), Inches(1.85), Inches(5.85), Inches(4.9), BG_PANEL, round_=True)
    add_rect(s, Inches(6.75), Inches(1.85), Inches(5.85), Inches(4.9), BG_PANEL, round_=True)
    t1 = s.shapes.add_textbox(Inches(0.9), Inches(2.0), Inches(5.3), Inches(0.5))
    r = t1.text_frame.paragraphs[0].add_run(); r.text = left_title; r.font.bold=True; r.font.size=Pt(18); r.font.color.rgb=ACCENT2; r.font.name="Microsoft YaHei"
    t2 = s.shapes.add_textbox(Inches(7.05), Inches(2.0), Inches(5.3), Inches(0.5))
    r2 = t2.text_frame.paragraphs[0].add_run(); r2.text = right_title; r2.font.bold=True; r2.font.size=Pt(18); r2.font.color.rgb=ACCENT2; r2.font.name="Microsoft YaHei"
    b1 = s.shapes.add_textbox(Inches(0.9), Inches(2.55), Inches(5.3), Inches(4.0))
    add_bullets(b1.text_frame, left_bullets, base_size=15)
    b2 = s.shapes.add_textbox(Inches(7.05), Inches(2.55), Inches(5.3), Inches(4.0))
    add_bullets(b2.text_frame, right_bullets, base_size=15)
    add_footer(s, part_no, part_name)
    return s


def slide_end():
    s = new_slide(); set_bg(s, BG_DARK)
    add_rect(s, Inches(0), Inches(0), Inches(0.18), SLIDE_H, ACCENT)
    box = s.shapes.add_textbox(Inches(0.9), Inches(2.8), Inches(10), Inches(1.2))
    p = box.text_frame.paragraphs[0]
    r = p.add_run(); r.text = "Thanks · Q&A"
    r.font.size = Pt(48); r.font.bold = True; r.font.color.rgb = TEXT_LIGHT; r.font.name = "Microsoft YaHei"
    box2 = s.shapes.add_textbox(Inches(0.95), Inches(3.9), Inches(10.5), Inches(1.2))
    p2 = box2.text_frame.paragraphs[0]
    r2 = p2.add_run(); r2.text = "下一讲：Hello Kalman && Target —— 目标还在动，你得预测它下一刻在哪"
    r2.font.size = Pt(18); r2.font.color.rgb = TEXT_LIGHT_MUTE; r2.font.name = "Microsoft YaHei"
    box3 = s.shapes.add_textbox(Inches(0.95), Inches(4.5), Inches(10.5), Inches(1.0))
    p3 = box3.text_frame.paragraphs[0]
    r3 = p3.add_run(); r3.text = "（手眼标定是自瞄绕不过去的一步，但不会单独占一讲）"
    r3.font.size = Pt(14); r3.font.color.rgb = TEXT_LIGHT_MUTE; r3.font.name = "Microsoft YaHei"


# ---------------------------------------------------------------
# Build deck
# ---------------------------------------------------------------

slide_title()
slide_toc()

# P0 复习导入
slide_section(0, "复习导入", "上节课我们手里有了什么？")
slide_content(0, "复习导入", "上节课回顾（Hello Modern C++）",
    [("C/C++ 编译与 CMake：会写 CMakeLists.txt，能编译、运行自己的工程", 0),
     ("**面向对象**：类 = 属性 + 方法；构造/析构函数；**封装**——数据安全、隐藏实现、便于协作、防止耦合", 0),
     ("已经写好的两个类：", 0),
     ("**Camera** 类：封装取图细节，对外只给一帧图像 + 时间戳", 1),
     ("**YOLO 检测器**：目标是识别装甲板并分类（位置、颜色、数字）", 1),
     ("**今天用的就是你在 lecture2 作业里跑通的那套检测器——tasks/ 和 tools/ 一行没改**", 1),
     ("作业：连接工业相机，封装相机类，用神经网络识别装甲板", 0)],
    kicker="P0 · 复习导入")
slide_content(0, "复习导入", "现在，程序手里已经有了什么？",
    [("**detector.detect(img)** 返回 **armors**（一个 Armor 列表）", 0),
     ("**Armor.points** 就是 YOLO 直接回归出来的 **4 个关键点**（左上、右上、右下、左下）", 0),
     ("YOLO-pose 是**端到端**的一步：图片进去，类别 + 4 个关键点出来，**中间没有“灯条配对”这个步骤**", 0),
     ("⚠ Armor 里虽然还留着 left / right 两个成员，但走 YOLO 这条路**从未给它们赋值**，取出来全是 (0,0)——那是传统灯条法的历史包袱", 0),
     ("也就是说：识别这一步，已经把“装甲板在哪张图的哪个位置”这件事解决了", 0)],
    kicker="P0 · 复习导入", image_label="Armor 结构体：points[0..3] → 4 个像素点\n（旁注：left/right 是历史包袱，本讲不用）")
slide_content(0, "复习导入", "只有这 4 个 2D 点，够瞄准吗？",
    [("看两张图：3 号车比 4 号车离我们更远 —— 人眼一眼就能判断距离，程序呢？", 0),
     ("再看三张图：同一块装甲板，角度都不一样 —— 这是“朝向”的差异", 0),
     ("提问互动：仅凭图像上 4 个像素点的坐标，你能猜出装甲板离相机多远、朝哪个方向偏吗？", 0)],
    kicker="P0 · 复习导入", image_label="同一装甲板：不同距离 + 不同旋转角度\n的对比照片（3 张）",
    caption="引导学生讨论后再进入下一部分")

# P1 为什么需要位姿
slide_section(1, "为什么需要位姿", "位置够不够？朝向怎么描述？")
slide_content(1, "为什么需要位姿", "位姿 = 位置 + 朝向",
    [("**位置（Position）**：一个三维向量 (x, y, z)，装甲板中心在相机坐标系下的坐标", 0),
     ("**朝向（Orientation / Rotation）**：装甲板“转了多少度、往哪边转”", 0),
     ("直观理解朝向——借用飞机的三个转动自由度：", 0),
     ("**偏航 yaw**：绕“上下轴”转，改变朝向左右", 1),
     ("**俯仰 pitch**：绕“左右轴”转，改变抬头低头", 1),
     ("**横滚 roll**：绕“前后轴”转，改变侧向倾斜", 1)],
    kicker="P1 · 为什么需要位姿", image_label="飞机 yaw / pitch / roll 三轴示意图")
slide_content(1, "为什么需要位姿", "先认清两个坐标系",
    [("**装甲板局部坐标系**：原点在装甲板中心，x 向右、y 向下、z 指向板外", 0),
     ("物理尺寸（今天要用到）：**ARMOR_WIDTH = 0.135 m**（灯条间宽），**LIGHTBAR_LENGTH = 0.056 m**（单根灯条长）", 1),
     ("**相机坐标系**：原点是镜头光心，随相机刚体一起平移、旋转", 0),
     ("我们的目标：算出“装甲板坐标系”相对“相机坐标系”的 **旋转 R** 和 **平移 t**", 0)],
    kicker="P1 · 为什么需要位姿", image_label="装甲板局部坐标系 + 相机坐标系\n双坐标轴示意图")
slide_content(1, "为什么需要位姿", "工程上为什么必须要“姿态”，不只是“位置”",
    [("① **相机和枪管往往不重合、不共轴** —— 只用 2D 画面中心瞄准，会有系统性偏差", 0),
     ("② **真实机器人会自转、会移动**，姿态千变万化 —— 需要用装甲板姿态反推它的旋转中心，才能预测它下一刻在哪", 0),
     ("一句话：**2D 检测解决“看见”，3D 位姿解决“打中”**", 0)],
    kicker="P1 · 为什么需要位姿", image_label="相机与枪管不共轴示意图 +\n机器人自转底盘照片")

# P2 PnP 原理与 API
slide_section(2, "PnP 原理与 API", "从对应点到位姿")
slide_content(2, "PnP 原理与 API", "Perspective-n-Points 问题",
    [("已知 **n 组对应点**：", 0),
     ("物体局部坐标系下的 **n 个三维点**（我们知道装甲板多大、点在哪）", 1),
     ("图像上对应的 **n 个二维像素点**（检测器已经给出来了）", 1),
     ("再加上相机的 **内参（焦距、主点）和畸变系数**", 0),
     ("求解：物体相对相机的 **旋转 R** 和 **平移 t**", 0)],
    kicker="P2 · PnP 原理与 API", image_label="经典 PnP 示意图：\n世界坐标系 3D 点 → 图像平面 2D 点\n(R, t) 箭头连接两个坐标系")
s = slide_code(2, "PnP 原理与 API", "cv::solvePnP 函数签名精讲",
    [("OpenCV 已经把 PnP 问题的求解封装成了一个函数，我们只管“喂数据”：", 0)],
    """bool cv::solvePnP(
    InputArray  objectPoints,   // 输入：物体局部坐标系下的 n 个点
    InputArray  imagePoints,    // 输入：图像上对应的 n 个点
    InputArray  cameraMatrix,   // 输入：相机内参矩阵（我们会提供）
    InputArray  distCoeffs,     // 输入：畸变系数（我们会提供）
    OutputArray rvec,           // 输出：旋转向量
    OutputArray tvec,           // 输出：平移向量
    bool useExtrinsicGuess = false,
    int  flags = SOLVEPNP_ITERATIVE
);""",
    kicker="P2 · PnP 原理与 API")
slide_content(2, "PnP 原理与 API", "输出到底是什么？",
    [("**tvec**：一个 3×1 向量 —— 装甲板坐标系原点，在相机坐标系下的位置（平移向量）", 0),
     ("**rvec**：也是一个 3×1 向量，代表旋转……", 0),
     ("**rvec 具体是什么？先卖个关子** —— 我们先把代码跑起来，等会儿亲手转一转装甲板，你就懂了", 0)],
    kicker="P2 · PnP 原理与 API", image_label="装甲板坐标轴照片 + 相机坐标轴照片\n（并排对比）")

# P3 动手实验一
slide_section(3, "动手实验一", "Task 01~03：解出 tvec / rvec")
slide_content(3, "动手实验一", "实验环境 & 点位约定",
    [("打开 **lecture4/yolo** 工程：所有填空都在 **src/main.cpp** 一个文件里；`tasks/` 下的 YOLO 检测器就是你 lecture2 作业里那一份，一个字没改", 0),
     ("**先确认环境**：`cd lecture4/yolo && cmake -B build`。这一步课前已经验过，课上只花 30 秒确认", 1),
     ("**运行目录有约束**：configs / assets / logs 都按相对路径找，必须在 `lecture4/yolo/` 下运行", 1),
     ("**约法三章**：这 20 分钟不要打开 `answer/main.cpp`；卡住了举手。等你自己的跑起来，我在投影上跑参考版对照", 1),
     ("**关键约定**：4 个关键点的顺序 —— 左上、右上、右下、左下（自左上顺时针）", 0),
     ("物理上它们就是左灯条顶端 / 右灯条顶端 / 右灯条底端 / 左灯条底端，但**程序里没有“灯条”这个对象**了", 1),
     ("这个顺序在 object_points 和 img_points 里必须完全一致，否则解出来的位姿是错的", 0)],
    kicker="P3 · 动手实验一", image_label="实物装甲板照片，\n绿点标注 0/1/2/3 号点位置")
slide_code(3, "动手实验一", "Task 01 · 填写 object_points",
    [("在装甲板**局部坐标系**下写出 4 个点的 (x, y, 0) 坐标，结合 ARMOR_WIDTH / LIGHTBAR_LENGTH 和上一页的点序", 0)],
    """static const double LIGHTBAR_LENGTH = 0.056;  // 灯条长度  单位: 米
static const double ARMOR_WIDTH     = 0.135;  // 装甲板宽度 单位: 米

// #### Task 01 ####################################
// object_points 是 物体局部坐标系下 n 个点 的坐标，
// 也就是装甲板坐标系下 4 个点的坐标。
static const std::vector<cv::Point3f> object_points {
    {      ,      , 0 },  // 点 1  左上
    {      ,      , 0 },  // 点 2  右上
    {      ,      , 0 },  // 点 3  右下
    {      ,      , 0 }   // 点 4  左下
};""",
    hint_bullets=[("提示：原点在板中心，x 向右为正、y 向下为正，半宽 = ARMOR_WIDTH/2，半高 = LIGHTBAR_LENGTH/2；请用 ± ARMOR_WIDTH / 2 这样的表达式填写（代码中的模板已被注释，先解注释再填）", 0)],
    task_tag="TASK 01", kicker="P3 · 动手实验一", code_h=Inches(3.35))
slide_content(3, "动手实验一", "点序陷阱：注释是错的",
    [("`tasks/armor.hpp` 里关于 `Armor::points` 的注释写的是「左上、左下、右下、右上」", 0),
     ("**实测下来是「左上、右上、右下、左下」** —— 注释和真实顺序正好反了", 0),
     ("怎么证明（现场 3 秒）：`draw_points` 已经在画那 4 个点了，按下标标上 0/1/2/3 就能看出来", 1),
     ("更硬的办法：把 object_points 换成注释里那个顺序，重编一次，看 `reproj err` 从个位数跳到几十", 1),
     ("**这是本讲最值得带走的一条**：注释是人写的、会过期；代码和数据不会撒谎，冲突时信实测", 0)],
    kicker="P3 · 动手实验一", image_label="同一块装甲板：\n左图点序正确 / 右图点序写反，\n叠加 reproj err 数值对比",
    caption="顺序写错不会报错、画面也正常，只有重投影误差能一眼判死")
slide_code(3, "动手实验一", "Task 02 · 填写 img_points",
    [("把检测器已经给出的 2D 像素点，按同样的 1→2→3→4 顺序装进 img_points", 0)],
    """auto armors = detector.detect(img);
if (!armors.empty()) {
    auto armor = armors.front();
    tools::draw_points(img, armor.points);

    // #### Task 02 #############################################
    // img_points 是 像素坐标系下 n 个点 的坐标，
    // 也就是照片上装甲板 4 个点的坐标。
    // std::vector<cv::Point2f> img_points{ , , , };
    //
    // 提示：
    // - 看看 Armor 结构体有哪些成员；
    // - 4 个关键点就在 armor.points 里，顺序已由检测器规范好；
    // - ⚠ 不要用 armor.left / armor.right：走 YOLO 这条路它们从未被赋值，
    //   取出来是四个 (0,0)，solvePnP 会失败或返回垃圾位姿。
    // ###########################################################""",
    task_tag="TASK 02", kicker="P3 · 动手实验一", code_h=Inches(3.35))
slide_code(3, "动手实验一", "Task 03 · 调用 cv::solvePnP",
    [("camera_matrix / distort_coeffs 已经在代码里为你准备好，直接传入即可", 0)],
    """// #### Task 03 ##############################################
cv::Mat rvec, tvec;
// 所有要传入的值都已经具备了。现在调用 solvePnP 解算装甲板位姿，
// rvec 和 tvec 用于存储 solvePnP 输出的结果：
cv::solvePnP( , , , , rvec, tvec);
// ############################################################""",
    task_tag="TASK 03", kicker="P3 · 动手实验一", code_h=Inches(1.7))
slide_content(3, "动手实验一", "现场演示 & Debug 小贴士",
    [("编译运行：`cd lecture4/yolo && cmake -B build && cmake --build build`，再 `./build/main`", 0),
     ("跑通后画面上会打印出 tvec 的数值（还未显示，下一环节我们再打出来）", 0),
     ("**常见报错 ①**：`YAML::BadFile` / `what(): bad file: configs/yolo.yaml`", 0),
     ("原因：在错误的目录下运行了可执行文件。注意第一个报错的**不是视频、是模型**——报错顺序反映的是构造顺序", 1),
     ("解决：`cd` 回 `lecture4/yolo/`，再 `./build/main`", 1),
     ("**常见报错 ②**：`Failed to open video: assets/video.avi`", 0),
     ("原因：目录对了但 assets/ 缺失（多半是拷贝时漏了，约 60MB）。解决：补齐 assets/ 三个文件", 1),
     ("**常见报错 ③**：`error while loading shared libraries: libopenvino.so.*`", 0),
     ("解决：`source /opt/intel/openvino_2024.6.0/setupvars.sh`", 1)],
    kicker="P3 · 动手实验一", image_label="终端截图：YAML::BadFile 报错 +\ncd 回根目录后正常运行")

# P4 rvec 揭秘
slide_section(4, "rvec 揭秘", "旋转向量 / 矩阵 / 欧拉角 / 四元数")
slide_content(4, "rvec 揭秘", "转一转，看一看",
    [("**观察环节**：盯着**画面左上角**那三行数字，看视频里那只手转动装甲板时它们怎么变", 0),
     ("（程序默认循环播放 `assets/video.avi`——里面就是手持装甲板在动，25 秒一轮，不用等很久）", 1),
     ("引导提问：", 0),
     ("只绕一个轴转，rvec 的哪个分量在变？", 1),
     ("转得越多，rvec 的数值变化有什么规律？", 1),
     ("先靠直觉猜一猜，再看下一页的数学定义", 0)],
    kicker="P4 · rvec 揭秘", image_label="程序运行截图：画面左上角的\n三行数字 + 视频里手持装甲板的姿态")
slide_content(4, "rvec 揭秘", "rvec 到底是什么",
    [("**旋转向量（rotation vector）**：一种紧凑的旋转表示法", 0),
     ("**方向** = 旋转轴方向", 1),
     ("**模长（大小）** = 绕这根轴旋转的角度（弧度）", 1),
     ("好处：只用 3 个数就能表示任意旋转，比 3×3 的旋转矩阵更省", 0)],
    kicker="P4 · rvec 揭秘")
slide_content(4, "rvec 揭秘", "旋转的几种表示法，一张图看懂",
    [("**旋转向量 rvec**  --[ cv::Rodrigues，可逆 ]-->  **旋转矩阵 rmat**", 0),
     ("**旋转矩阵 rmat**  --[ 反三角函数 ]-->  **欧拉角**（yaw / pitch / roll）", 0),
     ("**旋转矩阵 rmat**  --[ 转换公式 ]-->  **四元数 quaternion**", 0),
     ("三种表示法本质等价，只是在不同场景下各有优劣（下一页展开）", 0)],
    kicker="P4 · rvec 揭秘", image_label="rvec → rmat → 欧拉角 / 四元数\n流程示意图")
s = slide_code(4, "rvec 揭秘", "从旋转矩阵提取欧拉角（INT_YXZ 约定）",
    [("拿到 rmat（旋转矩阵）之后，用反三角函数把 yaw / pitch / roll 解出来：", 0)],
    """// rmat 的第 i 行第 j 列元素记作 m_ij
yaw   = atan2( m13, m33 )
pitch = -asin( m23 )
roll  = atan2( m21, m22 )

// 注意：atan2 / asin 算出来是弧度。本讲程序直接显示弧度（画面上的角是很小的数，如 0.12），
// 需要度数时再乘 57.3 (≈180/π) 换算""",
    kicker="P4 · rvec 揭秘", code_h=Inches(2.2))
slide_compare(4, "rvec 揭秘", "欧拉角的坑：万向锁（Gimbal Lock）",
    "欧拉角", [("直观、好理解（yaw / pitch / roll）", 0),
               ("表示**不唯一**：不同旋转顺序结果不同", 0),
               ("特定姿态下会**丢失一个自由度**（万向锁）", 0)],
    "四元数", [("4 个数 (w, x, y, z)，无奇异点", 0),
              ("插值、连续旋转更稳健", 0),
              ("不直观，本讲不展开推导", 0),
              ("课后可用 **quaternions.online** 交互体验两者关系", 0)],
    kicker="P4 · rvec 揭秘")

# P5 动手实验二
slide_section(5, "动手实验二", "Task 04~05：把旋转变成看得懂的角度")
slide_code(5, "动手实验二", "Task 04 · 把 tvec / rvec 打印到画面上",
    [("现在 draw_text 只会打印 0.0，改写参数把真实解出来的值显示出来", 0)],
    """// #### Task 04 ####################################
// 现在，draw_text 只打印 0.0
// 请你改写下面 draw_text 的参数，把解得的 tvec 和 rvec 打印出来
tools::draw_text(img, fmt::format(
    "tvec:  x{:.2f} y{:.2f} z{:.2f}",
    tvec.at<double>(0), tvec.at<double>(1), tvec.at<double>(2)), ...);
tools::draw_text(img, fmt::format(
    "rvec:  x{:.2f} y{:.2f} z{:.2f}",
    rvec.at<double>(0), rvec.at<double>(1), rvec.at<double>(2)), ...);""",
    hint_bullets=[("提示：`tvec.at<double>(0)` 取出的是一个 double，即 tvec 的第一个元素", 0)],
    task_tag="TASK 04", kicker="P5 · 动手实验二", code_h=Inches(2.9))
slide_code(5, "动手实验二", "Task 05 · rvec → rmat → 欧拉角",
    [("用 cv::Rodrigues 把 rvec 转成 rmat，再套用上一环节的反三角函数公式", 0)],
    """// #### Task 05 ####################################
// 使用 cv::Rodrigues，把 rvec 旋转向量转换为 rmat 旋转矩阵，
// 再用反三角函数把 rmat 中的元素转化为欧拉角，并显示在画面上。
cv::Mat rmat;
cv::Rodrigues(rvec, rmat);
tools::draw_text(img, fmt::format(
    "euler angles:  yaw{:.2f} pitch{:.2f} roll{:.2f}",
    yaw, pitch, roll), ...);
// 提示：
// - cv::Mat 下标从 0 开始；
// - 取元素方式和 tvec 类似，例如 rmat.at<double>(0, 2)。""",
    task_tag="TASK 05", kicker="P5 · 动手实验二", code_h=Inches(3.0))
slide_content(5, "动手实验二", "重投影误差：给点序配一把尺",
    [("前面反复说「点序错了不报错、最难查」——现在给你一个一眼判死的工具", 0),
     ("**做法**：把 object_points 用解得的位姿**投影回图像**，和检测到的 img_points 比像素距离", 0),
     ("**判读口径**：个位数像素 = 对的；两位数 = 错的。中间没有灰色地带", 0),
     ("参考实现 `./build/answer` 已经把这一行画在画面上（`reproj err`），比学生版多这一行", 1),
     ("学生自己那份没有这一行——想自查就 `#include \"tools/pnp_check.hpp\"` 加上（header-only，不用改 CMake）", 1),
     ("**这条和上一页的点序陷阱是配对的**：一个说坑在哪，一个给出路", 0)],
    kicker="P5 · 动手实验二", image_label="左右对比截图：\n点序正确 reproj err ≈ 3 px /\n点序写反 reproj err ≈ 80 px")
slide_content(5, "动手实验二", "现场演示 & 互动",
    [("观察画面左上角：视频里那只手转动装甲板时，yaw / pitch / roll 数值实时变化", 0),
     ("（按**空格键可以暂停**，停在某一帧上慢慢看；再按一次继续）", 1),
     ("邀请 1~2 位同学上台演示，说说自己观察到的变化规律", 0),
     ("提问：把装甲板前后移动（不转动），tvec 和 rvec 分别会怎么变？", 0),
     ("验收判据：tvec.z 在 0.2~0.7 之间、跟着画面里的远近连续变、不乱跳。别用「框画出来了」当判据——画框那行在 Task 02 之前，一个字不填它也画", 0)],
    kicker="P5 · 动手实验二", image_label="程序运行截图：\nyaw/pitch/roll 三行数值叠加在画面上")

# P6 坐标系全景
slide_section(6, "坐标系全景", "从像素到机器人本体 / IMU")
slide_content(6, "坐标系全景", "我真的对准了吗？",
    [("**相机坐标系**：与相机刚性连接的坐标系，随相机一起平移、旋转；原点 = 镜头光心", 0),
     ("**思考**：如果相机安装时有倾斜，并且和枪管不在同一个位置，会发生什么？", 0),
     ("答案：仅靠“装甲板在相机坐标系下的位姿”还不够，还要知道相机相对枪管/机器人本体的安装关系", 0)],
    kicker="P6 · 坐标系全景", image_label="相机与枪管不共轴的实拍照片\n（两套坐标轴叠加标注）")
slide_content(6, "坐标系全景", "完整的坐标变换链条",
    [("**像素坐标系** --（今天学的 solvePnP）--> **相机坐标系**", 0),
     ("**相机坐标系** --（手眼标定，进阶内容）--> **机器人本体坐标系**", 0),
     ("**机器人本体坐标系** --（实际测量安装）--> **IMU 坐标系**", 0),
     ("今天我们打通了第一环；手眼标定和运动预测（卡尔曼滤波）留给后续课程", 0)],
    kicker="P6 · 坐标系全景", image_label="实物机器人标注 imu / base_link /\ncamera 三套坐标轴的照片")

# P7 总结与作业
slide_section(7, "总结与作业", "回顾、答疑、布置任务")
slide_content(7, "总结与作业", "本讲回顾",
    [("位姿 = **位置（3D 向量）** + **朝向（旋转）**", 0),
     ("**PnP 问题**：n 组 3D-2D 对应点 + 相机内参 → 解出 R, t", 0),
     ("**cv::solvePnP**：输入 4 类数据，输出 rvec / tvec", 0),
     ("**tvec** = 装甲板原点在相机坐标系下的位置", 0),
     ("**rvec** --Rodrigues--> **rmat** --反三角函数--> **欧拉角** / 四元数", 0),
     ("欧拉角存在**万向锁**问题，四元数更稳健", 0),
     ("**object_points 与 img_points 必须一一对应**；写错了不报错、画面正常、数值有值，但位姿全错", 0),
     ("自查手段：**重投影误差**（个位数像素=对，两位数=错）；顺带记住「注释会过期，实测不会撒谎」", 0),
     ("完整链条：像素 → 相机（solvePnP）→ 机器人本体（手眼标定）→ IMU（安装测量）", 0)],
    kicker="P7 · 总结与作业", base_size=17)
slide_content(7, "总结与作业", "课后作业",
    [("① **必做**：完成 Task 01~05（课上未完成的部分），跑通并正确显示 tvec / rvec / yaw / pitch / roll", 0),
     ("② **进阶（二选一）**：A 接 HikRobot 真相机（需 MVS SDK，用自己标定的内参替换 main.cpp 顶部那两组）；"
      "B 补上 `lecture4/homework/` 里 `Buff_Solver::solvePnP()` 的空函数体（能量机关脚手架已经搭好，注意它的 OpenVINO 路径与 yolo/ 工程不同）", 0),
     ("③ **思考题**：什么姿态下欧拉角会出现万向锁？用 **quaternions.online** 验证你的猜想，下节课抽查", 0),
     ("（可选自查练习）故意把 object_points 第 2、4 点对调，记录 reproj err 从多少变成多少，并解释为什么 tvec 仍然「看起来像个正常数字」", 0)],
    kicker="P7 · 总结与作业")
slide_end()

# 输出名带 _YOLO版 后缀：旧的那份同名 pptx 是 class/ 版的 37 页成品，
# 两份并存时靠后缀区分。旧文件确认不再需要后可直接删除。
PPTX_NAME = "Lecture4_HelloArmor_装甲板位姿解算_YOLO版.pptx"
out_path = os.path.join(OUT_DIR, PPTX_NAME)
prs.save(out_path)
print("SLIDES:", len(prs.slides.__iter__.__self__._sldIdLst))
print("Saved:", out_path)
print("提示：请用 git diff 复核生成的 pptx，确认没有把手工修正覆盖掉。")
