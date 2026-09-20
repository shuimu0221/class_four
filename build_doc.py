# -*- coding: utf-8 -*-
"""Generate Lecture 4 "Hello Armor" 教案 (lesson plan) as a docx."""
import os

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# 输出到脚本所在目录（= 仓库根）。不要写死绝对路径：仓库搬过一次，
# 写死的路径会让脚本一跑就 FileNotFoundError。
HERE = os.path.dirname(os.path.abspath(__file__))
assert os.path.isdir(os.path.join(HERE, "lecture4")), (
    f"脚本似乎不在仓库根目录下（找不到 {HERE}/lecture4）。请从仓库根运行本脚本。"
)
# 设 LECTURE4_OUT_DIR 可以把产物生成到别处，便于与已发布版做 diff 对账。
OUT_DIR = os.environ.get("LECTURE4_OUT_DIR") or HERE

ACCENT = RGBColor(0x0E, 0x8A, 0x5F)
DARK = RGBColor(0x20, 0x24, 0x33)

doc = Document()

# base font
style = doc.styles["Normal"]
style.font.name = "Microsoft YaHei"
style.font.size = Pt(11)
rpr = style.element.get_or_add_rPr()
rFonts = rpr.find(qn('w:rFonts'))
if rFonts is None:
    rFonts = OxmlElement('w:rFonts')
    rpr.append(rFonts)
rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')


def set_cell_shading(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)


def h1(text):
    p = doc.add_heading(level=1)
    r = p.add_run(text)
    r.font.color.rgb = ACCENT
    r.font.name = "Microsoft YaHei"
    r.font.size = Pt(18)
    return p


def h2(text):
    p = doc.add_heading(level=2)
    r = p.add_run(text)
    r.font.color.rgb = DARK
    r.font.name = "Microsoft YaHei"
    r.font.size = Pt(14)
    return p


def para(text, bold=False, size=11, indent=False):
    p = doc.add_paragraph()
    if indent:
        p.paragraph_format.left_indent = Cm(0.6)
    r = p.add_run(text)
    r.bold = bold
    r.font.size = Pt(size)
    r.font.name = "Microsoft YaHei"
    return p


def bullet(text, level=0):
    p = doc.add_paragraph(style="List Bullet" if level == 0 else "List Bullet 2")
    r = p.add_run(text)
    r.font.size = Pt(11)
    r.font.name = "Microsoft YaHei"
    return p


def code_block(text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.4)
    shading_elm = OxmlElement('w:shd')
    shading_elm.set(qn('w:fill'), 'F2F2F2')
    for line in text.strip("\n").split("\n"):
        run = p.add_run((line if line.strip() else " ") + "\n")
        run.font.name = "Consolas"
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    p_pr = p._p.get_or_add_pPr()
    p_pr.append(shading_elm)
    return p


# ================= 封面信息 =================
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = title.add_run("《Hello Armor：装甲板位姿解算》教案")
r.bold = True
r.font.size = Pt(24)
r.font.color.rgb = ACCENT
r.font.name = "Microsoft YaHei"

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = sub.add_run("视觉组第四讲 · 承接 Lecture 3《Hello Modern C++》")
r.font.size = Pt(13)
r.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

doc.add_paragraph()

# 基本信息表
info = doc.add_table(rows=4, cols=4)
info.style = "Light Grid Accent 1"
info_data = [
    ("课程名称", "视觉组第四讲：Hello Armor —— 装甲板位姿解算", "授课时长", "90 分钟（1.5 小时）"),
    ("适用对象", "已完成 Lecture 1~3、且完成 Lecture 2《Hello C++&&OOP》YOLO 装甲板检测作业的视觉组新成员", "授课形式", "讲授 + 现场演示 + 随堂编程练习"),
    ("前置知识", "C++ 基础语法、类与对象、OpenCV 基本 API；Lecture 2 作业里那套 YOLO 装甲板检测器（Armor 结构体与它的 4 个关键点）。另需确认学生拿到的是完整仓库（含 assets/ 约 60MB），而非只拷了源码目录", "教具/环境", "Ubuntu 虚拟机、VS Code、投影。依赖：CMake ≥ 3.16、OpenCV4、fmt、Eigen3、yaml-cpp、spdlog、OpenVINO 2024.6.0。实物相机演示另需装甲板 + 工业相机 + MVS SDK"),
    ("素材来源", "本教案整合自《2025 视觉组培训第五课·装甲板位姿解算》与《视觉组第四讲·Hello Armor》两版历史课程录像，统一为本届 Lecture 4", "配套代码", "lecture4/yolo 工程（学生填空版 src/main.cpp + 参考版 answer/main.cpp，同一个 CMake 工程）"),
]
for i, row in enumerate(info_data):
    cells = info.rows[i].cells
    for j in range(0, 4, 2):
        cells[j].text = ""
        p = cells[j].paragraphs[0]
        r = p.add_run(row[j]); r.bold = True; r.font.size = Pt(10.5); r.font.name = "Microsoft YaHei"
        set_cell_shading(cells[j], "EAF6F0")
        cells[j+1].text = ""
        p2 = cells[j+1].paragraphs[0]
        r2 = p2.add_run(row[j+1]); r2.font.size = Pt(10.5); r2.font.name = "Microsoft YaHei"

doc.add_page_break()

# ================= 一、教学目标 =================
h1("一、教学目标")
h2("1. 知识与理解")
for t in [
    "理解为什么 2D 检测结果不足以支撑自动瞄准，必须求解装甲板的 3D 位姿（位置 + 朝向）。",
    "理解 PnP（Perspective-n-Points）问题的数学含义：已知 n 组三维-二维对应点及相机内参，求解旋转 R 与平移 t。",
    "理解 tvec、rvec 的物理意义，以及旋转向量、旋转矩阵、欧拉角、四元数之间的转换关系与适用场景（含万向锁问题）。",
    "理解 object_points 与 img_points 必须一一对应，以及顺序写错时的表现：编译通过、画面正常、数值有值，但位姿全错。",
    "理解从像素坐标到机器人本体/IMU坐标系的完整变换链条（solvePnP → 手眼标定 → 物理安装测量）在自瞄系统中的位置。",
]:
    bullet(t)
h2("2. 技能与实践")
for t in [
    "能正确调用 cv::solvePnP，按约定顺序构造 objectPoints / imagePoints。",
    "能使用 cv::Rodrigues 完成 rvec 与 rmat 的相互转换，并用反三角函数公式提取欧拉角。",
    "能独立完成 Task 01~05 编程练习并现场调试运行（含常见的工作目录类报错排查）。",
    "能用重投影误差自查点序是否写对（个位数像素=对，两位数=错）。",
]:
    bullet(t)
h2("3. 情感与工程素养")
for t in [
    "建立“检测只是第一步，位姿才是可用信息”的工程直觉，为后续手眼标定、卡尔曼滤波预测课程埋下伏笔。",
    "养成先猜想、再验证的实验习惯（如“转一转，看一看”环节）。",
    "建立“注释是人写的、会过期，代码和数据不会撒谎”的判断力——本讲以 Armor::points 的错误注释为实例。",
]:
    bullet(t)

h2("教学重点")
bullet("cv::solvePnP 的输入输出含义与调用方式；四点坐标的顺序约定与对应关系。")
bullet("object_points 与 img_points 的一一对应；用重投影误差验证对应关系是否正确。")
h2("教学难点")
bullet("rvec/rmat/欧拉角/四元数之间的转换关系与万向锁问题的理解；坐标系变换链条的整体把握。")
bullet("点序写错时没有任何错误信号，必须靠重投影误差这类主动自查手段才能发现。")

doc.add_page_break()

# ================= 二、教学过程 =================
h1("二、教学过程与时间分配（共 90 分钟）")

table = doc.add_table(rows=1, cols=5)
table.style = "Light Grid Accent 1"
table.alignment = WD_TABLE_ALIGNMENT.CENTER
hdr = table.rows[0].cells
headers = ["时间", "环节 / PPT 页", "教师活动", "学生活动", "设计意图"]
for i, htext in enumerate(headers):
    hdr[i].text = ""
    p = hdr[i].paragraphs[0]
    r = p.add_run(htext); r.bold = True; r.font.size = Pt(10.5); r.font.color.rgb = RGBColor(255,255,255)
    set_cell_shading(hdr[i], "0E8A5F")

rows = [
 ("0:00-0:02\n(2min)", "开场\nP.1 封面", "说明本讲目标：从“看到装甲板”到“算出装甲板在哪、朝哪”。", "明确本讲定位与产出。", "建立学习期待，承上启下。"),
 ("0:02-0:03\n(1min)", "课程地图\nP.2", "过一遍今天 8 个环节的顺序和大致用时。", "了解节奏，便于自我把控练习进度。", "让学生对 90 分钟有整体预期。"),
 ("0:03-0:08\n(5min)", "P0 复习导入\nP.3-6", "回顾 Lecture 2 的 YOLO 装甲板检测作业：模型直接吐出 class_id / confidence / box / 4 个关键点，是端到端的一步，中间没有灯条配对；提问“程序现在手里有什么”，引出 Armor.points 的 4 个 2D 点；用“3号车 vs 4号车”“同一装甲板三种朝向”两组照片提问引入。", "回答提问，讨论仅凭 2D 点能否判断距离与朝向。", "确认前置知识到位，制造认知冲突，引出本讲必要性。"),
 ("0:08-0:14\n(6min)", "P1 为什么需要位姿\nP.7-10", "讲解“位姿=位置+朝向”；用飞机比喻讲 yaw/pitch/roll；介绍装甲板局部坐标系与相机坐标系；讲两条工程理由（相机枪管不共轴、机器人会自转）。", "记录两个坐标系的定义与 ARMOR_WIDTH/LIGHTBAR_LENGTH 数值。", "让学生带着“为什么要学”的动机进入数学/API部分。"),
 ("0:14-0:27\n(13min)", "P2 PnP 原理与 API\nP.11-14", "讲解 PnP 问题定义；逐参数讲解 cv::solvePnP 签名；讲解 tvec 含义；rvec 留悬念。", "对照 PPT 抄写函数签名到自己代码注释里，标出每个参数对应关系。", "把“黑箱函数”拆解成学生能看懂的输入输出，降低后续编程门槛。"),
 ("0:27-0:51\n(24min)", "P3 动手实验一 Task01-03\nP.15-21", "讲解项目结构（打开 lecture4/yolo，填空全在 src/main.cpp 一个文件）、运行目录约束与依赖确认；讲 answer/ 的约法三章；逐个 Task 讲解思路（不直接给答案）；讲点序陷阱（armor.hpp 的注释是错的）；巡场答疑；现场跑通演示。", "打开 lecture4/yolo 工程，依次完成 Task01(object_points)→Task02(img_points)→Task03(solvePnP调用)，编译运行验证 tvec 是否被正确解出。", "第一次编程实操，把“坐标系”这一抽象概念落到 4 个具体数字上；通过报错与“注释会撒谎”培养调试能力。"),
 ("0:51-1:05\n(14min)", "P4 rvec揭秘与旋转表示法\nP.22-27", "组织“转一转看一看”小实验（看视频里手持装甲板转动），引导学生观察 rvec 分量变化规律；讲解 rvec 定义（轴+角）；讲 rvec⇄rmat（Rodrigues）与 rmat→欧拉角公式（INT_YXZ）；讲万向锁与四元数（点到为止）。", "观察视频里装甲板转动时的数值变化，口头描述规律；记录 INT_YXZ 公式。", "用实验建立直觉，再给出数学表达，符合“具体到抽象”的学习曲线；埋下四元数伏笔。"),
 ("1:05-1:21\n(16min)", "P5 动手实验二 Task04-05\nP.28-32", "讲解 Task04(打印tvec/rvec)、Task05(Rodrigues+反三角函数算欧拉角)的思路与提示；提示 draw_text 的参数顺序与 class/ 版相反；讲重投影误差自查；巡场答疑；邀请1-2名学生上台演示、描述观察到的yaw/pitch/roll变化。", "完成 Task04、Task05，编译运行，观察角度实时变化；被邀请学生上台演示并回答提问。", "完成本讲的完整编程闭环：从像素点到人类可读的角度；用提问巩固对 tvec 不变/rvec 变化等边界情况的理解。"),
 ("1:21-1:27\n(6min)", "P6 坐标系全景\nP.33-35", "提出“我真的对准了吗”的问题，讲相机与枪管不共轴场景；讲完整变换链条：像素→相机(solvePnP)→机器人本体(手眼标定)→IMU(实际安装)。", "跟随讲解建立全局坐标链条的心智图，明确今天只完成了第一环。", "把今天的内容放进整个自瞄系统的大图景里，衔接后续课程（手眼标定、卡尔曼滤波）。"),
 ("1:27-1:30\n(3min)", "P7 总结\nP.36-37", "带学生过一遍 8 条知识点回顾。", "对照自己的笔记/代码自查是否都掌握。", "巩固记忆，暴露遗漏点。"),
 ("1:30\n(结束前1min内完成，可延展至课后)", "作业布置 & Q&A\nP.38-39", "布置必做/进阶/思考题三档作业（进阶指向 lecture4/homework 的 buff 脚手架），说明下节课会抽查思考题；开放提问。", "记录作业要求，提出遗留问题。", "分层作业兼顾进度不同的学生；思考题为下节课内容（四元数/滤波）预热。"),
]

for row in rows:
    cells = table.add_row().cells
    for i, val in enumerate(row):
        cells[i].text = ""
        p = cells[i].paragraphs[0]
        r = p.add_run(val)
        r.font.size = Pt(9.5)
        r.font.name = "Microsoft YaHei"

doc.add_page_break()

# ================= 三、Task 01-05 参考答案 =================
h1("三、Task 01~05 参考答案（教师用，不对学生展示）")
para("注：PPT 学生版仅给出填空模板与提示，不含以下答案；请教师课前自行验证工程可编译运行。", size=10)
para("⚠ 本讲用的是 lecture4/yolo 工程，它的 tools::draw_text 参数顺序是 "
     "(img, text, point, color, font_scale, thickness)——color 在 font_scale 之前，"
     "与 lecture4/class/ 版正好相反。写反会在第 5 个实参上报 "
     "cannot convert 'cv::Scalar' to 'double'。Task 04 与 Task 05 都涉及，别只改一处。", size=10)

h2("Task 01：object_points（装甲板局部坐标系，单位：米）")
para("约定：原点在装甲板中心，x 轴向右为正，y 轴向下为正；半宽 = ARMOR_WIDTH/2 = 0.0675，半高 = LIGHTBAR_LENGTH/2 = 0.028。按代码注释的要求，学生应当用 ± ARMOR_WIDTH / 2 这样的表达式填写，不要写死小数。")
para("点序：左上、右上、右下、左下（自左上顺时针）。这个顺序必须与 Task 02 的 img_points 一一对应——"
     "而它并不是 tasks/armor.hpp 注释里写的那一个（注释写的是「左上、左下、右下、右上」，是错的）。"
     "详见配套文档 lecture4/yolo/docs/keypoint_order.md。", size=10)
code_block("""static const std::vector<cv::Point3f> object_points {
    { -ARMOR_WIDTH / 2, -LIGHTBAR_LENGTH / 2, 0 },  // 点 1  左上
    {  ARMOR_WIDTH / 2, -LIGHTBAR_LENGTH / 2, 0 },  // 点 2  右上
    {  ARMOR_WIDTH / 2,  LIGHTBAR_LENGTH / 2, 0 },  // 点 3  右下
    { -ARMOR_WIDTH / 2,  LIGHTBAR_LENGTH / 2, 0 }   // 点 4  左下
};""")

h2("Task 02：img_points（像素坐标系）")
para("YOLO 版直接把 4 个关键点回归出来了，就在 armor.points 里，顺序已由检测器规范为 左上/右上/右下/左下。"
     "注意不要用 armor.left / armor.right——那两个成员在本讲走的 YOLO 构造函数里从未被赋值，"
     "取出来是四个 (0,0)，solvePnP 会失败或返回垃圾位姿，而且不会报错。", size=10)
code_block("""std::vector<cv::Point2f> img_points{
    armor.points.at(0),  // 点 1  左上
    armor.points.at(1),  // 点 2  右上
    armor.points.at(2),  // 点 3  右下
    armor.points.at(3)   // 点 4  左下
};""")

h2("Task 03：调用 solvePnP")
code_block("""cv::Mat rvec, tvec;
cv::solvePnP(object_points, img_points, camera_matrix, distort_coeffs, rvec, tvec);""")

h2("Task 04：显示 tvec / rvec")
code_block("""tools::draw_text(img, fmt::format("tvec:  x{: .2f} y{: .2f} z{: .2f}",
    tvec.at<double>(0), tvec.at<double>(1), tvec.at<double>(2)),
    cv::Point(10, 60), cv::Scalar(0, 255, 255), 1.7, 3);
tools::draw_text(img, fmt::format("rvec:  x{: .2f} y{: .2f} z{: .2f}",
    rvec.at<double>(0), rvec.at<double>(1), rvec.at<double>(2)),
    cv::Point(10, 120), cv::Scalar(0, 255, 255), 1.7, 3);""")

h2("Task 05：rvec → rmat → 欧拉角")
code_block("""cv::Mat rmat;
cv::Rodrigues(rvec, rmat);
double yaw   = atan2(rmat.at<double>(0, 2), rmat.at<double>(2, 2));
double pitch = -asin(rmat.at<double>(1, 2));
double roll  = atan2(rmat.at<double>(1, 0), rmat.at<double>(1, 1));
tools::draw_text(img, fmt::format("euler angles:  yaw{: .2f} pitch{: .2f} roll{: .2f}",
    yaw, pitch, roll), cv::Point(10, 180), cv::Scalar(0, 255, 255), 1.7, 3);""")

para("注：atan2 / asin 的输出是弧度，本工程直接显示弧度（与 answer/main.cpp 一致，未乘 57.3）；"
     "画面上的三个角是很小的数（如 0.12）。需要度数时乘 57.3（≈180/π）换算。", size=10)

h2("附：重投影误差自查（不属学生任务，但教师必须会讲）")
para("把 object_points 用解得的位姿投影回图像，和检测到的 img_points 比距离。顺序写对时是个位数像素；"
     "写反会跳到几十上百。参考实现 answer/main.cpp 已经把这一行画在画面上（reproj err），"
     "工具函数在 tools/pnp_check.hpp。实测参考值：中位约 2.7 px。", size=10)
code_block("""double reproj = tools::reprojection_error(
    object_points, img_points, rvec, tvec, camera_matrix, distort_coeffs);""")

doc.add_page_break()

# ================= 四、板书/演示清单 =================
h1("四、演示与教具清单")
para("⚠ 依赖与工作目录必须课前准备好——课上补不回来。", size=10)
for t in [
    "【课前必做】在授课镜像里跑通一遍：cd lecture4/yolo && cmake -B build && cmake --build build -j，"
    "确认生成 build/main 与 build/answer，再 ./build/answer 确认出图且 reproj err 在个位数像素。"
    "只验编译不验运行，模型/视频问题仍会在课堂上第一次暴露。",
    "【依赖清单】CMake ≥ 3.16、OpenCV4（含 dnn 与 calib3d）、fmt、Eigen3、yaml-cpp、spdlog、OpenVINO 2024.6.0。"
    "OpenVINO 装在别处时只改 lecture4/yolo/CMakeLists.txt 里的 set(OpenVINO_DIR ...) 一处。"
    "注意 CMakeLists 把 CMAKE_BUILD_TYPE 写死为 Debug，OpenVINO 在 Debug 下推理明显更慢，课堂帧率低是正常现象。",
    "【工作目录】程序按相对路径找 configs/、assets/、logs/ 四样，必须站在 lecture4/yolo/ 下运行。"
    "课前一分钟确认：cd lecture4/yolo && cmake -B build 2>&1 | tail -3。",
    "【分发】lecture4/yolo/assets/ 约 60MB（video.avi 55MB + yolov5.bin 4.3MB + yolov5.xml 200KB），"
    "已随仓库分发。拷贝后确认目录下有 configs/ 与 assets/；若看到 class/ 与 answer/ 并列则是拷错了版本。"
    "video.avi 与 lecture4/class/video.avi 是同一段视频（md5 相同），可以对学生说「还是上次那段」。",
    "【实物演示·可选】装甲板实物 + 工业相机 + MVS SDK（需 -DWITH_HIKROBOT=ON 重新配置）。"
    "⚠ 默认配置是 source: video 读录像，改相机需同时改 configs/yolo.yaml 与重新 cmake。"
    "相机一路随时可弃，切回 source: video 即可继续上课，不影响任何 Task。",
    "【备用】若现场故障，程序本身就能循环播放 video.avi（loop: true，25 秒一轮），无需额外降级方案。",
    "投影分屏：一路放 PPT，一路放代码/终端，便于学生对照。",
]:
    bullet(t)

h1("五、作业布置")
h2("① 必做")
para("完成 Task 01~05（课上未完成部分），本地编译运行通过，画面上能正确显示 tvec / rvec / yaw / pitch / roll。")
para("验收判据：tvec.z 在 0.2~0.7 之间、跟着画面里装甲板的远近连续变化、不乱跳；"
     "三个欧拉角都是零点几的小数（单位弧度）。不要用「框画出来了」当判据——画框那行代码在 Task 02 之前，"
     "一个字不填它也画。", size=10)
h2("② 进阶（二选一）")
para("A（需 HikRobot 相机与 MVS SDK）：把 source 改成 camera 并 -DWITH_HIKROBOT=ON 重新配置，"
     "跑通真实相机；然后用自己标定的内参替换 src/main.cpp 顶部的 camera_matrix 与 distort_coeffs"
     "（现成内参是给 assets/video.avi 那台相机标的，换相机后不替换会让 reproj err 暴涨）。")
para("B（零硬件，人人可做）：补上 lecture4/homework/ 里 Buff_Solver::solvePnP() 的空函数体——"
     "那是一个已经搭好脚手架的能量机关位姿解算工程。做之前先读它的 tasks/CMakeLists.txt，"
     "OpenVINO 路径与 yolo/ 工程写的不一样，需要改成你机器上的实际路径。")
para("另（可选自查练习）：故意把 object_points 的第 2、4 点对调，记录 reproj err 从多少变成多少，"
     "并解释为什么 tvec 仍然「看起来像个正常数字」。", size=10)
h2("③ 思考题（下节课抽查）")
para("什么姿态下欧拉角会出现万向锁？用 quaternions.online 交互验证你的猜想，并简述观察到的现象。")

h1("六、教学反思（课后填写）")
para("1. 学生完成 Task01~05 的平均耗时是否与预期（24+16min）一致？哪个 Task 卡壳最多？")
para("2. “转一转看一看”改成看视频里手持装甲板转动后，引导提问是否仍能让学生自己猜出 rvec 的含义？")
para("3. 点序陷阱（armor.hpp 的错误注释）讲完后，有多少学生真的去改了 object_points 的点序？"
     "这个「注释会撒谎」的实例是否比预想的更有共鸣？")
para("4. 坐标系全景（P6）部分学生反馈是否偏抽象？仓库里 lecture4/reprojection/ 有现成的真实标定数值"
     "（R_camera2gimbal 等）可以替换掉抽象讲法，本轮未采用，评估是否值得纳入。")
para("5. 下一讲是《Hello Kalman && Target》（目标在动，需要预测下一刻位置）；"
     "手眼标定是自瞄绕不过去的一步，但不会单独占一讲，评估是否需要在结尾预告里调整措辞。")

out_path = os.path.join(OUT_DIR, "Lecture4_HelloArmor_教案.docx")
doc.save(out_path)
print("Saved:", out_path)
print("提示：请用 git diff 复核生成的 docx，确认没有把手工修正覆盖掉。")
