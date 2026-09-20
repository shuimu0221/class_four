# 讲稿撰写 · 上下文包（唯一事实来源）v4 —— YOLO 版

本文件是撰写《Lecture 4 Hello Armor 装甲板位姿解算》逐字讲稿的唯一素材来源。

> ⚠️ **基准材料**（以本文件为准，不得引用其他版本）：
> - **课件**：根目录《Lecture4_HelloArmor_装甲板位姿解算_YOLO版.pptx》（**39 页**）
> - **教案**：根目录《Lecture4_HelloArmor_教案.docx》
> - **工程代码**：`lecture4/yolo`（学生版 `src/main.cpp` + 参考版 `answer/main.cpp`，同一个 CMake 工程）
> - **配套文档**：`lecture4/yolo/docs/keypoint_order.md`（点序陷阱的完整证据链）、`lecture4/yolo/README.md`
> - **内容覆盖要求**：两份原视频 PPT《2025装甲板位姿解算_原视频PPT提取》《Hello_Armor_原视频PPT提取》的内容**全部都要讲**（含欧拉角、万向锁、四元数——这些是本讲核心教学内容，不是了解内容）
> - **本届改用 YOLO 版程序**：旧的手写传统 CV 版 `lecture4/class/` **不再讲授**，只作为代码保留。
>   `lecture4/yolo/tasks/` 与 `tools/` 是从学生 lecture2 作业**逐字复制**过来的，一行没改。
> - `output/` 目录下带 `_v4/_v5/_v2` 后缀的旧修订版 PPT/教案**已废弃**，与当前代码不符，不得引用。

---

## 〇、任务白名单（最高优先级约束）

**本讲只有 5 个 Task，全部位于同一个文件 `lecture4/yolo/src/main.cpp`（学生版）。**
（`answer/main.cpp` 是教师参考答案，与学生版逐 Task 对应；它**默认不编译**，教师需 `-DBUILD_ANSWER=ON`。）

| Task | 学生要做什么 |
|---|---|
| **Task 01** | 填写 `object_points`：装甲板局部坐标系下 4 个点的 3D 坐标（模板被注释着，要先解注释再填）。点序：左上、右上、右下、左下 |
| **Task 02** | 填写 `img_points`：4 个 2D 像素点，**取自 `armor.points.at(0)`~`at(3)`** |
| **Task 03** | 调用 `cv::solvePnP(object_points, img_points, camera_matrix, distort_coeffs, rvec, tvec);` |
| **Task 04** | 改写 `draw_text` 参数，把解得的 tvec / rvec 打印到画面上（现在只打印 0.0） |
| **Task 05** | 用 `cv::Rodrigues(rvec, rmat)` 转旋转矩阵，再用反三角函数从 rmat 提取欧拉角 yaw/pitch/roll 并显示 |

**工程里没有的东西（讲稿不得布置、不得要求实现）：**
- ❌ 距离 / 瞄准角 `distance_m` / `aim_angles_deg`
- ❌ `PoseSolver` 类、`pose_solver_test`、ctest 验收
- ❌ ROI、动态 ROI、颜色二次估计（`configs/yolo.yaml` 里的 `threshold` 与 `use_traditional` 是历史遗留字段，代码已不用）
- ❌ 学生要自己实现检测器（`tasks/` 是发的成品，与 lecture2 作业里那份一致）

**本届新增、必须讲到的两页：**
- **第 18 页 · 点序陷阱**：`tasks/armor.hpp` 里 `Armor::points` 的注释是错的
- **第 31 页 · 重投影误差自查**：`tools/pnp_check.hpp`，判读口径「个位数像素=对，两位数=错」

---

## 一、PPT 全文（共 39 页，逐页）

### 第 1 页 —— 装甲板位姿解算

视觉组第四讲 · HELLO ARMOR
装甲板位姿解算
从 2D 识别结果到 3D 位姿：cv::solvePnP 全流程实战
主讲人：______　　助教：______　　时长：90 分钟　　承接 Lecture 3《Hello Modern C++》
🖼  SP 队徽

### 第 2 页 —— 今天 90 分钟，我们要走完这条链路

课程地图 · Roadmap
今天 90 分钟，我们要走完这条链路
P0
复习导入：你 lecture2 作业里那套 YOLO 检测器
5 min
P1
为什么装甲板需要“位姿”而不只是位置
6 min
P2
PnP 原理与 cv::solvePnP 接口精讲
13 min
P3
动手实验一：Task 01~03，解出 tvec / rvec
24 min
P4
rvec 揭秘：旋转向量／矩阵／欧拉角／四元数
14 min
P5
动手实验二：Task 04~05，把旋转变成角度
16 min
P6
坐标系全景：从像素到机器人本体 / IMU
6 min
P7
总结、答疑与作业布置
3 min

### 第 3 页 —— 复习导入

P0
复习导入
上节课我们手里有了什么？

### 第 4 页 —— 上节课回顾（Hello Modern C++）

P0 · 复习导入
上节课回顾（Hello Modern C++）
· C/C++ 编译与 CMake：会写 CMakeLists.txt，能编译、运行自己的工程
· 面向对象：类 = 属性 + 方法；构造/析构函数；封装——数据安全、隐藏实现、便于协作、防止耦合
· 已经写好的两个类：
‑ Camera 类：封装取图细节，对外只给一帧图像 + 时间戳
‑ YOLO 检测器：目标是识别装甲板并分类（位置、颜色、数字）
‑ 今天用的就是你在 lecture2 作业里跑通的那套检测器——tasks/ 和 tools/ 一行没改
· 作业：连接工业相机，封装相机类，用神经网络识别装甲板

### 第 5 页 —— 现在，程序手里已经有了什么？

P0 · 复习导入
现在，程序手里已经有了什么？
· detector.detect(img) 返回 armors（一个 Armor 列表）
· Armor.points 就是 YOLO 直接回归出来的 4 个关键点（左上、右上、右下、左下）
· YOLO-pose 是端到端的一步：图片进去，类别 + 4 个关键点出来，中间没有“灯条配对”这个步骤
· ⚠ Armor 里虽然还留着 left / right 两个成员，但走 YOLO 这条路从未给它们赋值，取出来全是 (0,0)——那是传统灯条法的历史包袱
· 也就是说：识别这一步，已经把“装甲板在哪张图的哪个位置”这件事解决了

### 第 6 页 —— 只有这 4 个 2D 点，够瞄准吗？

P0 · 复习导入
只有这 4 个 2D 点，够瞄准吗？
· 看两张图：3 号车比 4 号车离我们更远 —— 人眼一眼就能判断距离，程序呢？
· 再看三张图：同一块装甲板，角度都不一样 —— 这是“朝向”的差异
· 提问互动：仅凭图像上 4 个像素点的坐标，你能猜出装甲板离相机多远、朝哪个方向偏吗？
引导学生讨论后再进入下一部分

### 第 7 页 —— 为什么需要位姿

P1
为什么需要位姿
位置够不够？朝向怎么描述？

### 第 8 页 —— 位姿 = 位置 + 朝向

P1 · 为什么需要位姿
位姿 = 位置 + 朝向
· 位置（Position）：一个三维向量 (x, y, z)，装甲板中心在相机坐标系下的坐标
· 朝向（Orientation / Rotation）：装甲板“转了多少度、往哪边转”
· 直观理解朝向——借用飞机的三个转动自由度：
‑ 偏航 yaw：绕“上下轴”转，改变朝向左右
‑ 俯仰 pitch：绕“左右轴”转，改变抬头低头
‑ 横滚 roll：绕“前后轴”转，改变侧向倾斜

### 第 9 页 —— 先认清两个坐标系

P1 · 为什么需要位姿
先认清两个坐标系
· 装甲板局部坐标系：原点在装甲板中心，x 向右、y 向下、z 指向板外
‑ 物理尺寸（今天要用到）：ARMOR_WIDTH = 0.135 m（灯条间宽），LIGHTBAR_LENGTH = 0.056 m（单根灯条长）
· 相机坐标系：原点是镜头光心，随相机刚体一起平移、旋转
· 我们的目标：算出“装甲板坐标系”相对“相机坐标系”的 旋转 R 和 平移 t

### 第 10 页 —— 工程上为什么必须要“姿态”，不只是“位置”

P1 · 为什么需要位姿
工程上为什么必须要“姿态”，不只是“位置”
· ① 相机和枪管往往不重合、不共轴 —— 只用 2D 画面中心瞄准，会有系统性偏差
· ② 真实机器人会自转、会移动，姿态千变万化 —— 需要用装甲板姿态反推它的旋转中心，才能预测它下一刻在哪
· 一句话：2D 检测解决“看见”，3D 位姿解决“打中”
🖼  相机与枪管不共轴示意图 +
机器人自转底盘照片

### 第 11 页 —— PnP 原理与 API

P2
PnP 原理与 API
从对应点到位姿

### 第 12 页 —— Perspective-n-Points 问题

P2 · PnP 原理与 API
Perspective-n-Points 问题
· 已知 n 组对应点：
‑ 物体局部坐标系下的 n 个三维点（我们知道装甲板多大、点在哪）
‑ 图像上对应的 n 个二维像素点（检测器已经给出来了）
· 再加上相机的 内参（焦距、主点）和畸变系数
· 求解：物体相对相机的 旋转 R 和 平移 t

### 第 13 页 —— cv::solvePnP 函数签名精讲

P2 · PnP 原理与 API
cv::solvePnP 函数签名精讲
· OpenCV 已经把 PnP 问题的求解封装成了一个函数，我们只管“喂数据”：
bool cv::solvePnP(
InputArray  objectPoints,   // 输入：物体局部坐标系下的 n 个点
InputArray  imagePoints,    // 输入：图像上对应的 n 个点
InputArray  cameraMatrix,   // 输入：相机内参矩阵（我们会提供）
InputArray  distCoeffs,     // 输入：畸变系数（我们会提供）
OutputArray rvec,           // 输出：旋转向量
OutputArray tvec,           // 输出：平移向量
bool useExtrinsicGuess = false,
int  flags = SOLVEPNP_ITERATIVE
);

### 第 14 页 —— 输出到底是什么？

P2 · PnP 原理与 API
输出到底是什么？
· tvec：一个 3×1 向量 —— 装甲板坐标系原点，在相机坐标系下的位置（平移向量）
· rvec：也是一个 3×1 向量，代表旋转……
· rvec 具体是什么？先卖个关子 —— 我们先把代码跑起来，等会儿亲手转一转装甲板，你就懂了
🖼  装甲板坐标轴照片 + 相机坐标轴照片
（并排对比）

### 第 15 页 —— 动手实验一

P3
动手实验一
Task 01~03：解出 tvec / rvec

### 第 16 页 —— 实验环境 & 点位约定

P3 · 动手实验一
实验环境 & 点位约定
· 打开 lecture4/yolo 工程：所有填空都在 src/main.cpp 一个文件里；`tasks/` 下的 YOLO 检测器就是你 lecture2 作业里那一份，一个字没改
‑ 先确认环境：`cd lecture4/yolo && cmake -B build`。这一步课前已经验过，课上只花 30 秒确认
‑ 运行目录有约束：configs / assets / logs 都按相对路径找，必须在 `lecture4/yolo/` 下运行
‑ 约法三章：这 20 分钟不要打开 `answer/main.cpp`；卡住了举手。等你自己的跑起来，我在投影上跑参考版对照
· 关键约定：4 个关键点的顺序 —— 左上、右上、右下、左下（自左上顺时针）
‑ 物理上它们就是左灯条顶端 / 右灯条顶端 / 右灯条底端 / 左灯条底端，但程序里没有“灯条”这个对象了
· 这个顺序在 object_points 和 img_points 里必须完全一致，否则解出来的位姿是错的

### 第 17 页 —— Task 01 · 填写 object_points

P3 · 动手实验一
Task 01 · 填写 object_points
TASK 01
· 在装甲板局部坐标系下写出 4 个点的 (x, y, 0) 坐标，结合 ARMOR_WIDTH / LIGHTBAR_LENGTH 和上一页的点序
static const double LIGHTBAR_LENGTH = 0.056;  // 灯条长度  单位: 米
static const double ARMOR_WIDTH     = 0.135;  // 装甲板宽度 单位: 米
// #### Task 01 ####################################
// object_points 是 物体局部坐标系下 n 个点 的坐标，
// 也就是装甲板坐标系下 4 个点的坐标。
static const std::vector<cv::Point3f> object_points {
{      ,      , 0 },  // 点 1  左上
{      ,      , 0 },  // 点 2  右上
{      ,      , 0 },  // 点 3  右下
{      ,      , 0 }   // 点 4  左下
};
· 提示：原点在板中心，x 向右为正、y 向下为正，半宽 = ARMOR_WIDTH/2，半高 = LIGHTBAR_LENGTH/2；请用 ± ARMOR_WIDTH / 2 这样的表达式填写（代码中的模板已被注释，先解注释再填）

### 第 18 页 —— 点序陷阱：注释是错的

P3 · 动手实验一
点序陷阱：注释是错的
· `tasks/armor.hpp` 里关于 `Armor::points` 的注释写的是「左上、左下、右下、右上」
· 实测下来是「左上、右上、右下、左下」 —— 注释和真实顺序正好反了
‑ 怎么证明（现场 3 秒）：`draw_points` 已经在画那 4 个点了，按下标标上 0/1/2/3 就能看出来
‑ 更硬的办法：把 object_points 换成注释里那个顺序，重编一次，看 `reproj err` 从个位数跳到几十
· 这是本讲最值得带走的一条：注释是人写的、会过期；代码和数据不会撒谎，冲突时信实测
顺序写错不会报错、画面也正常，只有重投影误差能一眼判死

### 第 19 页 —— Task 02 · 填写 img_points

P3 · 动手实验一
Task 02 · 填写 img_points
TASK 02
· 把检测器已经给出的 2D 像素点，按同样的 1→2→3→4 顺序装进 img_points
auto armors = detector.detect(img);
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
// ###########################################################

### 第 20 页 —— Task 03 · 调用 cv::solvePnP

P3 · 动手实验一
Task 03 · 调用 cv::solvePnP
TASK 03
· camera_matrix / distort_coeffs 已经在代码里为你准备好，直接传入即可
// #### Task 03 ##############################################
cv::Mat rvec, tvec;
// 所有要传入的值都已经具备了。现在调用 solvePnP 解算装甲板位姿，
// rvec 和 tvec 用于存储 solvePnP 输出的结果：
cv::solvePnP( , , , , rvec, tvec);
// ############################################################

### 第 21 页 —— 现场演示 & Debug 小贴士

P3 · 动手实验一
现场演示 & Debug 小贴士
· 编译运行：`cd lecture4/yolo && cmake -B build && cmake --build build`，再 `./build/main`
· 跑通后画面上会打印出 tvec 的数值（还未显示，下一环节我们再打出来）
· 常见报错 ①：`YAML::BadFile` / `what(): bad file: configs/yolo.yaml`
‑ 原因：在错误的目录下运行了可执行文件。注意第一个报错的不是视频、是模型——报错顺序反映的是构造顺序
‑ 解决：`cd` 回 `lecture4/yolo/`，再 `./build/main`
· 常见报错 ②：`Failed to open video: assets/video.avi`
‑ 原因：目录对了但 assets/ 缺失（多半是拷贝时漏了，约 60MB）。解决：补齐 assets/ 三个文件
· 常见报错 ③：`error while loading shared libraries: libopenvino.so.*`
‑ 解决：`source /opt/intel/openvino_2024.6.0/setupvars.sh`
🖼  终端截图：YAML::BadFile 报错 +
cd 回根目录后正常运行

### 第 22 页 —— rvec 揭秘

P4
rvec 揭秘
旋转向量 / 矩阵 / 欧拉角 / 四元数

### 第 23 页 —— 转一转，看一看

P4 · rvec 揭秘
转一转，看一看
· 观察环节：盯着画面左上角那三行数字，看视频里那只手转动装甲板时它们怎么变
‑ （程序默认循环播放 `assets/video.avi`——里面就是手持装甲板在动，25 秒一轮，不用等很久）
· 引导提问：
‑ 只绕一个轴转，rvec 的哪个分量在变？
‑ 转得越多，rvec 的数值变化有什么规律？
· 先靠直觉猜一猜，再看下一页的数学定义

### 第 24 页 —— rvec 到底是什么

P4 · rvec 揭秘
rvec 到底是什么
· 旋转向量（rotation vector）：一种紧凑的旋转表示法
‑ 方向 = 旋转轴方向
‑ 模长（大小） = 绕这根轴旋转的角度（弧度）
· 好处：只用 3 个数就能表示任意旋转，比 3×3 的旋转矩阵更省

### 第 25 页 —— 旋转的几种表示法，一张图看懂

P4 · rvec 揭秘
旋转的几种表示法，一张图看懂
· 旋转向量 rvec  --[ cv::Rodrigues，可逆 ]-->  旋转矩阵 rmat
· 旋转矩阵 rmat  --[ 反三角函数 ]-->  欧拉角（yaw / pitch / roll）
· 旋转矩阵 rmat  --[ 转换公式 ]-->  四元数 quaternion
· 三种表示法本质等价，只是在不同场景下各有优劣（下一页展开）

### 第 26 页 —— 从旋转矩阵提取欧拉角（INT_YXZ 约定）

P4 · rvec 揭秘
从旋转矩阵提取欧拉角（INT_YXZ 约定）
· 拿到 rmat（旋转矩阵）之后，用反三角函数把 yaw / pitch / roll 解出来：
// rmat 的第 i 行第 j 列元素记作 m_ij
yaw   = atan2( m13, m33 )
pitch = -asin( m23 )
roll  = atan2( m21, m22 )
// 注意：atan2 / asin 算出来是弧度。本讲程序直接显示弧度（画面上的角是很小的数，如 0.12），
// 需要度数时再乘 57.3 (≈180/π) 换算

### 第 27 页 —— 欧拉角的坑：万向锁（Gimbal Lock）

P4 · rvec 揭秘
欧拉角的坑：万向锁（Gimbal Lock）
欧拉角
四元数
· 直观、好理解（yaw / pitch / roll）
· 表示不唯一：不同旋转顺序结果不同
· 特定姿态下会丢失一个自由度（万向锁）
· 4 个数 (w, x, y, z)，无奇异点
· 插值、连续旋转更稳健
· 不直观，本讲不展开推导
· 课后可用 quaternions.online 交互体验两者关系

### 第 28 页 —— 动手实验二

P5
动手实验二
Task 04~05：把旋转变成看得懂的角度

### 第 29 页 —— Task 04 · 把 tvec / rvec 打印到画面上

P5 · 动手实验二
Task 04 · 把 tvec / rvec 打印到画面上
TASK 04
· 现在 draw_text 只会打印 0.0，改写参数把真实解出来的值显示出来
// #### Task 04 ####################################
// 现在，draw_text 只打印 0.0
// 请你改写下面 draw_text 的参数，把解得的 tvec 和 rvec 打印出来
tools::draw_text(img, fmt::format(
"tvec:  x{:.2f} y{:.2f} z{:.2f}",
tvec.at<double>(0), tvec.at<double>(1), tvec.at<double>(2)), ...);
tools::draw_text(img, fmt::format(
"rvec:  x{:.2f} y{:.2f} z{:.2f}",
rvec.at<double>(0), rvec.at<double>(1), rvec.at<double>(2)), ...);
· 提示：`tvec.at<double>(0)` 取出的是一个 double，即 tvec 的第一个元素

### 第 30 页 —— Task 05 · rvec → rmat → 欧拉角

P5 · 动手实验二
Task 05 · rvec → rmat → 欧拉角
TASK 05
· 用 cv::Rodrigues 把 rvec 转成 rmat，再套用上一环节的反三角函数公式
// #### Task 05 ####################################
// 使用 cv::Rodrigues，把 rvec 旋转向量转换为 rmat 旋转矩阵，
// 再用反三角函数把 rmat 中的元素转化为欧拉角，并显示在画面上。
cv::Mat rmat;
cv::Rodrigues(rvec, rmat);
tools::draw_text(img, fmt::format(
"euler angles:  yaw{:.2f} pitch{:.2f} roll{:.2f}",
yaw, pitch, roll), ...);
// 提示：
// - cv::Mat 下标从 0 开始；
// - 取元素方式和 tvec 类似，例如 rmat.at<double>(0, 2)。

### 第 31 页 —— 重投影误差：给点序配一把尺

P5 · 动手实验二
重投影误差：给点序配一把尺
· 前面反复说「点序错了不报错、最难查」——现在给你一个一眼判死的工具
· 做法：把 object_points 用解得的位姿投影回图像，和检测到的 img_points 比像素距离
· 判读口径：个位数像素 = 对的；两位数 = 错的。中间没有灰色地带
‑ 参考实现 `./build/answer` 已经把这一行画在画面上（`reproj err`），比学生版多这一行
‑ 学生自己那份没有这一行——想自查就 `#include "tools/pnp_check.hpp"` 加上（header-only，不用改 CMake）
· 这条和上一页的点序陷阱是配对的：一个说坑在哪，一个给出路

### 第 32 页 —— 现场演示 & 互动

P5 · 动手实验二
现场演示 & 互动
· 观察画面左上角：视频里那只手转动装甲板时，yaw / pitch / roll 数值实时变化
‑ （按空格键可以暂停，停在某一帧上慢慢看；再按一次继续）
· 邀请 1~2 位同学上台演示，说说自己观察到的变化规律
· 提问：把装甲板前后移动（不转动），tvec 和 rvec 分别会怎么变？
· 验收判据：tvec.z 在 0.2~0.7 之间、跟着画面里的远近连续变、不乱跳。别用「框画出来了」当判据——画框那行在 Task 02 之前，一个字不填它也画

### 第 33 页 —— 坐标系全景

P6
坐标系全景
从像素到机器人本体 / IMU

### 第 34 页 —— 我真的对准了吗？

P6 · 坐标系全景
我真的对准了吗？
· 相机坐标系：与相机刚性连接的坐标系，随相机一起平移、旋转；原点 = 镜头光心
· 思考：如果相机安装时有倾斜，并且和枪管不在同一个位置，会发生什么？
· 答案：仅靠“装甲板在相机坐标系下的位姿”还不够，还要知道相机相对枪管/机器人本体的安装关系
🖼  相机与枪管不共轴的实拍照片
（两套坐标轴叠加标注）

### 第 35 页 —— 完整的坐标变换链条

P6 · 坐标系全景
完整的坐标变换链条
· 像素坐标系 --（今天学的 solvePnP）--> 相机坐标系
· 相机坐标系 --（手眼标定，进阶内容）--> 机器人本体坐标系
· 机器人本体坐标系 --（实际测量安装）--> IMU 坐标系
· 今天我们打通了第一环；手眼标定和运动预测（卡尔曼滤波）留给后续课程
🖼  实物机器人标注 imu / base_link /
camera 三套坐标轴的照片

### 第 36 页 —— 总结与作业

P7
总结与作业
回顾、答疑、布置任务

### 第 37 页 —— 本讲回顾

P7 · 总结与作业
本讲回顾
· 位姿 = 位置（3D 向量） + 朝向（旋转）
· PnP 问题：n 组 3D-2D 对应点 + 相机内参 → 解出 R, t
· cv::solvePnP：输入 4 类数据，输出 rvec / tvec
· tvec = 装甲板原点在相机坐标系下的位置
· rvec --Rodrigues--> rmat --反三角函数--> 欧拉角 / 四元数
· 欧拉角存在万向锁问题，四元数更稳健
· object_points 与 img_points 必须一一对应；写错了不报错、画面正常、数值有值，但位姿全错
· 自查手段：重投影误差（个位数像素=对，两位数=错）；顺带记住「注释会过期，实测不会撒谎」
· 完整链条：像素 → 相机（solvePnP）→ 机器人本体（手眼标定）→ IMU（安装测量）

### 第 38 页 —— 课后作业

P7 · 总结与作业
课后作业
· ① 必做：完成 Task 01~05（课上未完成的部分），跑通并正确显示 tvec / rvec / yaw / pitch / roll
· ② 进阶（二选一）：A 接 HikRobot 真相机（需 MVS SDK，用自己标定的内参替换 main.cpp 顶部那两组）；B 补上 `lecture4/homework/` 里 `Buff_Solver::solvePnP()` 的空函数体（能量机关脚手架已经搭好，注意它的 OpenVINO 路径与 yolo/ 工程不同）
· ③ 思考题：什么姿态下欧拉角会出现万向锁？用 quaternions.online 验证你的猜想，下节课抽查
· （可选自查练习）故意把 object_points 第 2、4 点对调，记录 reproj err 从多少变成多少，并解释为什么 tvec 仍然「看起来像个正常数字」

### 第 39 页 —— 下一讲：Hello Kalman && Target —— 目标还在动，你得预测它下一刻在哪

Thanks · Q&A
下一讲：Hello Kalman && Target —— 目标还在动，你得预测它下一刻在哪
（手眼标定是自瞄绕不过去的一步，但不会单独占一讲）

---

## 二、教案（教学设计与时间分配）

### 基本信息

- 课程名称：视觉组第四讲：Hello Armor —— 装甲板位姿解算
- 授课时长：90 分钟（1.5 小时）
- 适用对象：已完成 Lecture 1~3、且完成 Lecture 2《Hello C++&&OOP》YOLO 装甲板检测作业的视觉组新成员
- 授课形式：讲授 + 现场演示 + 随堂编程练习
- 前置知识：C++ 基础语法、类与对象、OpenCV 基本 API；Lecture 2 作业里那套 YOLO 装甲板检测器（Armor 结构体与它的 4 个关键点）。另需确认学生拿到的是完整仓库（含 assets/ 约 60MB），而非只拷了源码目录
- 教具/环境：Ubuntu 虚拟机、VS Code、投影。依赖：CMake ≥ 3.16、OpenCV4、fmt、Eigen3、yaml-cpp、spdlog、OpenVINO 2024.6.0。实物相机演示另需装甲板 + 工业相机 + MVS SDK
- 素材来源：本教案整合自《2025 视觉组培训第五课·装甲板位姿解算》与《视觉组第四讲·Hello Armor》两版历史课程录像，统一为本届 Lecture 4
- 配套代码：lecture4/yolo 工程（学生填空版 src/main.cpp + 参考版 answer/main.cpp，同一个 CMake 工程）

### 教学过程与时间分配（共 90 分钟；页码为 39 页课件实际页序）

| 时间 | 环节 / PPT 页 | 教师活动 | 学生活动 | 设计意图 |
| 0:00-0:02 / (2min) | 开场 / P.1 封面 | 说明本讲目标：从“看到装甲板”到“算出装甲板在哪、朝哪”。 | 明确本讲定位与产出。 | 建立学习期待，承上启下。 |
| 0:02-0:03 / (1min) | 课程地图 / P.2 | 过一遍今天 8 个环节的顺序和大致用时。 | 了解节奏，便于自我把控练习进度。 | 让学生对 90 分钟有整体预期。 |
| 0:03-0:08 / (5min) | P0 复习导入 / P.3-6 | 回顾 Lecture 2 的 YOLO 装甲板检测作业：模型直接吐出 class_id / confidence / box / 4 个关键点，是端到端的一步，中间没有灯条配对；提问“程序现在手里有什么”，引出 Armor.points 的 4 个 2D 点；用“3号车 vs 4号车”“同一装甲板三种朝向”两组照片提问引入。 | 回答提问，讨论仅凭 2D 点能否判断距离与朝向。 | 确认前置知识到位，制造认知冲突，引出本讲必要性。 |
| 0:08-0:14 / (6min) | P1 为什么需要位姿 / P.7-10 | 讲解“位姿=位置+朝向”；用飞机比喻讲 yaw/pitch/roll；介绍装甲板局部坐标系与相机坐标系；讲两条工程理由（相机枪管不共轴、机器人会自转）。 | 记录两个坐标系的定义与 ARMOR_WIDTH/LIGHTBAR_LENGTH 数值。 | 让学生带着“为什么要学”的动机进入数学/API部分。 |
| 0:14-0:27 / (13min) | P2 PnP 原理与 API / P.11-14 | 讲解 PnP 问题定义；逐参数讲解 cv::solvePnP 签名；讲解 tvec 含义；rvec 留悬念。 | 对照 PPT 抄写函数签名到自己代码注释里，标出每个参数对应关系。 | 把“黑箱函数”拆解成学生能看懂的输入输出，降低后续编程门槛。 |
| 0:27-0:51 / (24min) | P3 动手实验一 Task01-03 / P.15-21 | 讲解项目结构（打开 lecture4/yolo，填空全在 src/main.cpp 一个文件）、运行目录约束与依赖确认；讲 answer/ 的约法三章；逐个 Task 讲解思路（不直接给答案）；讲点序陷阱（armor.hpp 的注释是错的）；巡场答疑；现场跑通演示。 | 打开 lecture4/yolo 工程，依次完成 Task01(object_points)→Task02(img_points)→Task03(solvePnP调用)，编译运行验证 tvec 是否被正确解出。 | 第一次编程实操，把“坐标系”这一抽象概念落到 4 个具体数字上；通过报错与“注释会撒谎”培养调试能力。 |
| 0:51-1:05 / (14min) | P4 rvec揭秘与旋转表示法 / P.22-27 | 组织“转一转看一看”小实验（看视频里手持装甲板转动），引导学生观察 rvec 分量变化规律；讲解 rvec 定义（轴+角）；讲 rvec⇄rmat（Rodrigues）与 rmat→欧拉角公式（INT_YXZ）；讲万向锁与四元数（点到为止）。 | 观察视频里装甲板转动时的数值变化，口头描述规律；记录 INT_YXZ 公式。 | 用实验建立直觉，再给出数学表达，符合“具体到抽象”的学习曲线；埋下四元数伏笔。 |
| 1:05-1:21 / (16min) | P5 动手实验二 Task04-05 / P.28-32 | 讲解 Task04(打印tvec/rvec)、Task05(Rodrigues+反三角函数算欧拉角)的思路与提示；提示 draw_text 的参数顺序与 class/ 版相反；讲重投影误差自查；巡场答疑；邀请1-2名学生上台演示、描述观察到的yaw/pitch/roll变化。 | 完成 Task04、Task05，编译运行，观察角度实时变化；被邀请学生上台演示并回答提问。 | 完成本讲的完整编程闭环：从像素点到人类可读的角度；用提问巩固对 tvec 不变/rvec 变化等边界情况的理解。 |
| 1:21-1:27 / (6min) | P6 坐标系全景 / P.33-35 | 提出“我真的对准了吗”的问题，讲相机与枪管不共轴场景；讲完整变换链条：像素→相机(solvePnP)→机器人本体(手眼标定)→IMU(实际安装)。 | 跟随讲解建立全局坐标链条的心智图，明确今天只完成了第一环。 | 把今天的内容放进整个自瞄系统的大图景里，衔接后续课程（手眼标定、卡尔曼滤波）。 |
| 1:27-1:30 / (3min) | P7 总结 / P.36-37 | 带学生过一遍 8 条知识点回顾。 | 对照自己的笔记/代码自查是否都掌握。 | 巩固记忆，暴露遗漏点。 |
| 1:30 / (结束前1min内完成，可延展至课后) | 作业布置 & Q&A / P.38-39 | 布置必做/进阶/思考题三档作业（进阶指向 lecture4/homework 的 buff 脚手架），说明下节课会抽查思考题；开放提问。 | 记录作业要求，提出遗留问题。 | 分层作业兼顾进度不同的学生；思考题为下节课内容（四元数/滤波）预热。 |

### 教学目标、重点与难点

一、教学目标
1. 知识与理解
理解为什么 2D 检测结果不足以支撑自动瞄准，必须求解装甲板的 3D 位姿（位置 + 朝向）。
理解 PnP（Perspective-n-Points）问题的数学含义：已知 n 组三维-二维对应点及相机内参，求解旋转 R 与平移 t。
理解 tvec、rvec 的物理意义，以及旋转向量、旋转矩阵、欧拉角、四元数之间的转换关系与适用场景（含万向锁问题）。
理解 object_points 与 img_points 必须一一对应，以及顺序写错时的表现：编译通过、画面正常、数值有值，但位姿全错。
理解从像素坐标到机器人本体/IMU坐标系的完整变换链条（solvePnP → 手眼标定 → 物理安装测量）在自瞄系统中的位置。
2. 技能与实践
能正确调用 cv::solvePnP，按约定顺序构造 objectPoints / imagePoints。
能使用 cv::Rodrigues 完成 rvec 与 rmat 的相互转换，并用反三角函数公式提取欧拉角。
能独立完成 Task 01~05 编程练习并现场调试运行（含常见的工作目录类报错排查）。
能用重投影误差自查点序是否写对（个位数像素=对，两位数=错）。
3. 情感与工程素养
建立“检测只是第一步，位姿才是可用信息”的工程直觉，为后续手眼标定、卡尔曼滤波预测课程埋下伏笔。
养成先猜想、再验证的实验习惯（如“转一转，看一看”环节）。
建立“注释是人写的、会过期，代码和数据不会撒谎”的判断力——本讲以 Armor::points 的错误注释为实例。
教学重点
cv::solvePnP 的输入输出含义与调用方式；四点坐标的顺序约定与对应关系。
object_points 与 img_points 的一一对应；用重投影误差验证对应关系是否正确。
教学难点
rvec/rmat/欧拉角/四元数之间的转换关系与万向锁问题的理解；坐标系变换链条的整体把握。
点序写错时没有任何错误信号，必须靠重投影误差这类主动自查手段才能发现。

### Task 01~05 参考答案（教师用，**不对学生展示**；讲稿只讲思路与提示）

注：PPT 学生版仅给出填空模板与提示，不含以下答案；请教师课前自行验证工程可编译运行。
⚠ 本讲用的是 lecture4/yolo 工程，它的 tools::draw_text 参数顺序是 (img, text, point, color, font_scale, thickness)——color 在 font_scale 之前，与 lecture4/class/ 版正好相反。写反会在第 5 个实参上报 cannot convert 'cv::Scalar' to 'double'。Task 04 与 Task 05 都涉及，别只改一处。
Task 01：object_points（装甲板局部坐标系，单位：米）
约定：原点在装甲板中心，x 轴向右为正，y 轴向下为正；半宽 = ARMOR_WIDTH/2 = 0.0675，半高 = LIGHTBAR_LENGTH/2 = 0.028。按代码注释的要求，学生应当用 ± ARMOR_WIDTH / 2 这样的表达式填写，不要写死小数。
点序：左上、右上、右下、左下（自左上顺时针）。这个顺序必须与 Task 02 的 img_points 一一对应——而它并不是 tasks/armor.hpp 注释里写的那一个（注释写的是「左上、左下、右下、右上」，是错的）。详见配套文档 lecture4/yolo/docs/keypoint_order.md。
static const std::vector<cv::Point3f> object_points {
    { -ARMOR_WIDTH / 2, -LIGHTBAR_LENGTH / 2, 0 },  // 点 1  左上
    {  ARMOR_WIDTH / 2, -LIGHTBAR_LENGTH / 2, 0 },  // 点 2  右上
    {  ARMOR_WIDTH / 2,  LIGHTBAR_LENGTH / 2, 0 },  // 点 3  右下
    { -ARMOR_WIDTH / 2,  LIGHTBAR_LENGTH / 2, 0 }   // 点 4  左下
};
Task 02：img_points（像素坐标系）
YOLO 版直接把 4 个关键点回归出来了，就在 armor.points 里，顺序已由检测器规范为 左上/右上/右下/左下。注意不要用 armor.left / armor.right——那两个成员在本讲走的 YOLO 构造函数里从未被赋值，取出来是四个 (0,0)，solvePnP 会失败或返回垃圾位姿，而且不会报错。
std::vector<cv::Point2f> img_points{
    armor.points.at(0),  // 点 1  左上
    armor.points.at(1),  // 点 2  右上
    armor.points.at(2),  // 点 3  右下
    armor.points.at(3)   // 点 4  左下
};
Task 03：调用 solvePnP
cv::Mat rvec, tvec;
cv::solvePnP(object_points, img_points, camera_matrix, distort_coeffs, rvec, tvec);
Task 04：显示 tvec / rvec
tools::draw_text(img, fmt::format("tvec:  x{: .2f} y{: .2f} z{: .2f}",
    tvec.at<double>(0), tvec.at<double>(1), tvec.at<double>(2)),
    cv::Point(10, 60), cv::Scalar(0, 255, 255), 1.7, 3);
tools::draw_text(img, fmt::format("rvec:  x{: .2f} y{: .2f} z{: .2f}",
    rvec.at<double>(0), rvec.at<double>(1), rvec.at<double>(2)),
    cv::Point(10, 120), cv::Scalar(0, 255, 255), 1.7, 3);
Task 05：rvec → rmat → 欧拉角
cv::Mat rmat;
cv::Rodrigues(rvec, rmat);
double yaw   = atan2(rmat.at<double>(0, 2), rmat.at<double>(2, 2));
double pitch = -asin(rmat.at<double>(1, 2));
double roll  = atan2(rmat.at<double>(1, 0), rmat.at<double>(1, 1));
tools::draw_text(img, fmt::format("euler angles:  yaw{: .2f} pitch{: .2f} roll{: .2f}",
    yaw, pitch, roll), cv::Point(10, 180), cv::Scalar(0, 255, 255), 1.7, 3);
注：atan2 / asin 的输出是弧度，本工程直接显示弧度（与 answer/main.cpp 一致，未乘 57.3）；画面上的三个角是很小的数（如 0.12）。需要度数时乘 57.3（≈180/π）换算。
附：重投影误差自查（不属学生任务，但教师必须会讲）
把 object_points 用解得的位姿投影回图像，和检测到的 img_points 比距离。顺序写对时是个位数像素；写反会跳到几十上百。参考实现 answer/main.cpp 已经把这一行画在画面上（reproj err），工具函数在 tools/pnp_check.hpp。实测参考值：中位约 2.7 px。
double reproj = tools::reprojection_error(
    object_points, img_points, rvec, tvec, camera_matrix, distort_coeffs);

### 演示与教具

⚠ 依赖与工作目录必须课前准备好——课上补不回来。
【课前必做】在授课镜像里跑通一遍：cd lecture4/yolo && cmake -B build && cmake --build build -j，确认生成 build/main 与 build/answer，再 ./build/answer 确认出图且 reproj err 在个位数像素。只验编译不验运行，模型/视频问题仍会在课堂上第一次暴露。
【依赖清单】CMake ≥ 3.16、OpenCV4（含 dnn 与 calib3d）、fmt、Eigen3、yaml-cpp、spdlog、OpenVINO 2024.6.0。OpenVINO 装在别处时只改 lecture4/yolo/CMakeLists.txt 里的 set(OpenVINO_DIR ...) 一处。注意 CMakeLists 把 CMAKE_BUILD_TYPE 写死为 Debug，OpenVINO 在 Debug 下推理明显更慢，课堂帧率低是正常现象。
【工作目录】程序按相对路径找 configs/、assets/、logs/ 四样，必须站在 lecture4/yolo/ 下运行。课前一分钟确认：cd lecture4/yolo && cmake -B build 2>&1 | tail -3。
【分发】lecture4/yolo/assets/ 约 60MB（video.avi 55MB + yolov5.bin 4.3MB + yolov5.xml 200KB），已随仓库分发。拷贝后确认目录下有 configs/ 与 assets/；若看到 class/ 与 answer/ 并列则是拷错了版本。video.avi 与 lecture4/class/video.avi 是同一段视频（md5 相同），可以对学生说「还是上次那段」。
【实物演示·可选】装甲板实物 + 工业相机 + MVS SDK（需 -DWITH_HIKROBOT=ON 重新配置）。⚠ 默认配置是 source: video 读录像，改相机需同时改 configs/yolo.yaml 与重新 cmake。相机一路随时可弃，切回 source: video 即可继续上课，不影响任何 Task。
【备用】若现场故障，程序本身就能循环播放 video.avi（loop: true，25 秒一轮），无需额外降级方案。
投影分屏：一路放 PPT，一路放代码/终端，便于学生对照。

### 作业布置（三档）

① 必做
完成 Task 01~05（课上未完成部分），本地编译运行通过，画面上能正确显示 tvec / rvec / yaw / pitch / roll。
验收判据：tvec.z 在 0.2~0.7 之间、跟着画面里装甲板的远近连续变化、不乱跳；三个欧拉角都是零点几的小数（单位弧度）。不要用「框画出来了」当判据——画框那行代码在 Task 02 之前，一个字不填它也画。
② 进阶（二选一）
A（需 HikRobot 相机与 MVS SDK）：把 source 改成 camera 并 -DWITH_HIKROBOT=ON 重新配置，跑通真实相机；然后用自己标定的内参替换 src/main.cpp 顶部的 camera_matrix 与 distort_coeffs（现成内参是给 assets/video.avi 那台相机标的，换相机后不替换会让 reproj err 暴涨）。
B（零硬件，人人可做）：补上 lecture4/homework/ 里 Buff_Solver::solvePnP() 的空函数体——那是一个已经搭好脚手架的能量机关位姿解算工程。做之前先读它的 tasks/CMakeLists.txt，OpenVINO 路径与 yolo/ 工程写的不一样，需要改成你机器上的实际路径。
另（可选自查练习）：故意把 object_points 的第 2、4 点对调，记录 reproj err 从多少变成多少，并解释为什么 tvec 仍然「看起来像个正常数字」。
③ 思考题（下节课抽查）
什么姿态下欧拉角会出现万向锁？用 quaternions.online 交互验证你的猜想，并简述观察到的现象。

---

## 三、两份原视频课的「必须覆盖清单」（用户硬性要求：内容都要讲）

以下内容来自《2025装甲板位姿解算_原视频PPT提取》与《Hello_Armor_原视频PPT提取》两份原始课件/录课，
**讲稿必须全部覆盖**。括号里给出对应幻灯片的**标题**（不是页码——页码会随课件改版变化，
按标题在 `一、PPT 全文` 里检索即可）：

**动机与直观（P0/P1）**
- 3 号车 vs 4 号车："相比于 4 号车，3 号车离我们更远"——人眼能判断距离（「只有这 4 个 2D 点，够瞄准吗？」）
- 同一块装甲板三种角度："图片中的三块装甲板有什么不同？"——朝向差异（同上页）
- 欧拉角按特定顺序定义：先偏航（绕上下轴）、再俯仰（绕左右轴）、后横滚（绕前后轴），每一步相对前一步的结果（「位姿 = 位置 + 朝向」）
- "看出"三维信息 = 距离远近 + 朝向左右 → 更准确地说：位置用三维向量、旋转用欧拉角 → "程序能解算这些信息吗？"（「位姿 = 位置 + 朝向」「先认清两个坐标系」）

**PnP 与 API（P2）**
- PnP：n 组一一对应的点 + 相机内参/畸变 → 解 R、t（「Perspective-n-Points 问题」）
- solvePnP 逐参数讲解（「cv::solvePnP 函数签名精讲」）
- tvec = 装甲板坐标系原点在相机系下的位置；**rvec 留悬念："先写代码，留个悬念，后面再来解答"**（「输出到底是什么？」）

**rvec 揭秘（P4）——核心章节，必须讲透**
- "转一转，看一看"：观察装甲板转动时 rvec 方向和大小怎么变（「转一转，看一看」）
  ⚠ 原课是在**终端**滚动打印、且数值量级是 `roll: 2.01 → 6.40`（疑为角度制的 roll）。
  **本届程序不往终端打任何东西**，tvec/rvec/欧拉角都画在**画面左上角**、原地刷新，且**打的是弧度**。
  讲稿**不得**引用 2.01/6.40 这类数值，也不得说"终端在滚动"。
- rvec 定义：方向 = 旋转轴，模长 = 转角（弧度）；3 个数表示任意旋转（「rvec 到底是什么」）
- 概念图：旋转向量 rvec --罗德里格斯公式/cv::Rodrigues（可逆）--> 旋转矩阵 rmat --反三角函数--> 欧拉角；rmat --> 四元数（「旋转的几种表示法，一张图看懂」）
- **INT_YXZ 欧拉角公式：θ₁ = arctan2(m₁₃, m₃₃)，θ₂ = −arcsin(m₂₃)，θ₃ = arctan2(m₂₁, m₂₂)**（「从旋转矩阵提取欧拉角（INT_YXZ 约定）」）
- 关键对应关系：公式里的 m₁₃ 是 rmat 第 1 行第 3 列，但 **cv::Mat 下标从 0 开始**，所以代码里写 `rmat.at<double>(0, 2)`——这是学生最容易错的地方（同上页）
- `std::atan2(double, double)` 是 C++ 标准库函数（原课专门给过这个提示）（同上页）
- 弧度换算：**本届程序打弧度**；57.3 (≈180/π) 只作为"想看度数就这么换算"的补充（同上页注释）
- 万向锁：欧拉角表示不唯一、特定姿态丢一个自由度；四元数 (w,x,y,z) 无奇异点、插值稳健、不直观（「欧拉角的坑：万向锁（Gimbal Lock）」）
- **quaternions.online 现场交互演示**：Quaternion 的 W/X/Y/Z 输入框 + Euler Angles 的 X/Y/Z 和 XYZ-Order 下拉框，红 x / 绿 y / 蓝 z 的 3D 网格实时联动——原 Hello Armor 课现场演示过浏览器这个网站（同上页，讲稿应作为现场/课后演示展开）

**动手实验（P3/P5）**
- 点序约定：左上、右上、右下、左下（自左上顺时针）；两个点集顺序必须一致（「实验环境 & 点位约定」）
- **点序陷阱**：`tasks/armor.hpp` 里 `Armor::points` 的注释是**错的**（写的是左上、左下、右下、右上）。
  本届新增一整页专讲这件事（「点序陷阱：注释是错的」），并配一个自查工具「重投影误差」（「重投影误差：给点序配一把尺」）
- Task 01~03 填空思路与提示，不给答案（「Task 01 · 填写 object_points」至「Task 03 · 调用 cv::solvePnP」）
- 经典报错：本届程序的第一个报错**不是视频、是配置**——`YAML::BadFile` / `what(): bad file: configs/yolo.yaml`，
  在 build/ 目录里直接 ./main 导致；`cd` 回 `lecture4/yolo` 再 `./build/main`（「现场演示 & Debug 小贴士」）
- Task 04：`tvec.at<double>(0)` 取出 double；fmt::format 与 draw_text（「Task 04 · 把 tvec / rvec 打印到画面上」）
- Task 05：Rodrigues + 反三角函数 + 显示（「Task 05 · rvec → rmat → 欧拉角」）
- 观察 yaw/pitch/roll 实时变化；邀请学生上台；提问"前后移动（不转动）装甲板，tvec 和 rvec 分别怎么变？"
  ——答：tvec 变、rvec 基本不变（「现场演示 & 互动」）

**坐标系全景（P6）**
- 相机坐标系：与相机刚性连接、随相机平移旋转、原点 = 镜头光心；"如果相机安装有倾斜，并且和枪管不在同一个位置，会怎么样？"（「我真的对准了吗？」）
- "实际车的运动状态千奇百怪，我们需要装甲板姿态来推算出它的旋转中心，进而对运动进行拟合"（「工程上为什么必须要"姿态"，不只是"位置"」）
- 手眼标定：获取机器人本体坐标系→相机坐标系的变换（机械臂 AX=XB 标定环）（「完整的坐标变换链条」）
- IMU："机器人本体控制依赖于 imu（陀螺仪），需要知道 imu 到本体坐标系之间的变换"（同上页）
- 完整链条：像素坐标系 → 相机坐标系 → 机器人本体坐标系 → IMU 坐标系，分别靠 solvePnP / 手眼标定 / 实际安装（同上页）

**收尾（P7）**
- 8 条回顾（「本讲回顾」）；三档作业（「课后作业」）；Thanks + 下一讲预告（「Thanks · Q&A」）
- 原课收尾还带过一遍课程大纲（可作 P7 口头回顾素材）。注意**本届的编号不同**：
  Lecture 2 = Hello C++&&OOP、Lecture 3 = Hello Modern C++、Lecture 4 = 本讲、Lecture 5 = Hello Kalman && Target。
  不要说"上一讲是 OOP"——OOP 是上上讲。

**可引用的课后参考链接（原课件出现过，可作"放群里"的口头补充）**
- 万向锁知乎文章：https://zhuanlan.zhihu.com/p/9135205633
- 线性代数（旋转矩阵背景）B 站视频：https://www.bilibili.com/video/BV1ns41167b9
- OpenCV 四元数类文档 `cv::Quat`：https://docs.opencv.org/4.x/d4/d4a/classcv_1_1Quat.html
- 交互演示网站：quaternions.online

---

## 四、工程代码（讲稿涉及代码必须与这里一致）

### 4.1 目录与构建

```
lecture4/yolo/
├── CMakeLists.txt      # 顶层；依赖 OpenCV/fmt/Eigen3/yaml-cpp/spdlog/OpenVINO
├── configs/yolo.yaml   # 检测与取帧配置
├── assets/             # yolov5.xml/.bin + video.avi（约 60MB）
├── docs/               # keypoint_order.md + verify_keypoint_order.py
├── tools/  tasks/      # 逐字复制自 lecture2 作业，未改动
├── io/                 # 取帧：按 config 在 video / camera 间切换
├── src/main.cpp        # 学生填空（Task 01~05）
└── answer/main.cpp     # 参考实现（默认不编译）
```

```bash
cd lecture4/yolo
cmake -B build                 # 教师演示另加 -DBUILD_ANSWER=ON
cmake --build build -j
./build/main                  # 必须在 lecture4/yolo/ 下运行
```

顶层 CMakeLists.txt 要点：

```cmake
cmake_minimum_required(VERSION 3.16.3)

project(lecture4_yolo)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_BUILD_TYPE Debug)

find_package(OpenCV REQUIRED)
find_package(fmt REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(yaml-cpp REQUIRED)
# lecture2 的 CMakeLists 把这一行注释掉了，但 tools/logger.cpp 真的用了 spdlog 的编译期 sink，
# 所以必须显式打开，否则链接不过。
find_package(spdlog REQUIRED)

# OpenVINO 路径只在顶层定义一次，子目录不再各自硬编码
set(OpenVINO_DIR "/opt/intel/openvino_2024.6.0/runtime/cmake")
find_package(OpenVINO REQUIRED)

include_directories(${EIGEN3_INCLUDE_DIR})
include_directories(${OpenCV_INCLUDE_DIRS})
include_directories(${PROJECT_SOURCE_DIR})

# tools 要在 io 之前，io 链接 tools
add_subdirectory(tools)
add_subdirectory(io)
add_subdirectory(tasks)

# tools/logger.cpp 会往 logs/ 写文件，spdlog 在目录不存在时会抛异常。
# 在配置期就把源码树里的 logs/ 建好（程序约定从本目录运行）。
file(MAKE_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/logs)

add_executable(main src/main.cpp)
target_link_libraries(main
    ${OpenCV_LIBS} fmt::fmt yaml-cpp spdlog::spdlog tools io auto_aim)

# 参考实现默认不编译：answer/main.cpp 里就是填好的 Task 01~05，
# 学生敲一次 cmake --build 就拿到答案，整段练习会作废。
# 教师演示时用 -DBUILD_ANSWER=ON 打开。
option(BUILD_ANSWER "Build the reference answer executable (teacher only)" OFF)
if(BUILD_ANSWER)
  add_executable(answer answer/main.cpp)
  target_link_libraries(answer
      ${OpenCV_LIBS} fmt::fmt yaml-cpp spdlog::spdlog tools io auto_aim)
endif()
```

### 4.2 `src/main.cpp`（学生版全文）

```cpp
#include <chrono>
#include <opencv2/opencv.hpp>

#include "fmt/core.h"
#include "io/camera.hpp"
#include "tasks/yolo.hpp"
#include "tools/img_tools.hpp"

// clang-format off
//  相机内参
static const cv::Mat camera_matrix =
    (cv::Mat_<double>(3, 3) <<  1286.307063384126 , 0                  , 645.34450819155256,
                                0                 , 1288.1400736562441 , 483.6163720308021 ,
                                0                 , 0                  , 1                   );
// 畸变系数
static const cv::Mat distort_coeffs =
    (cv::Mat_<double>(1, 5) << -0.47562935060124745, 0.21831745829617311, 0.0004957613589406044, -0.00034617769548693592, 0);
// clang-format on

static const double LIGHTBAR_LENGTH = 0.056; // 灯条长度    单位：米
static const double ARMOR_WIDTH = 0.135;     // 装甲板宽度  单位：米

// #### Task 01 ############################################
// object_points 是 物体局部坐标系下 n个点 的坐标。
// 对于我们而言，也就是装甲板坐标系下4个点的坐标。
// 请你填写下面的 object_points:
//
// static const std::vector<cv::Point3f> object_points {
//     {          ,           , 0 },  // 点 1
//     {          ,           , 0 },  // 点 2
//     {          ,           , 0 },  // 点 3
//     {          ,           , 0 }   // 点 4
// };
//
// 提示：
// - 装甲板坐标系是三维的坐标系，但是四个点都在 z 坐标为 0 的平面上，所以已经为你填写了四个 0 。
// - 在上方定义有 灯条长度 和 装甲板宽度，你应当用 "± ARMOR_WIDTH / 2" 这样的写法来填写。
// - 点序规定：左上、右上、右下、左下（自左上顺时针）。这个顺序必须和 Task02 的 img_points 一一对应。
//   ⚠ Armor::points 的真实顺序就是上面这个，**不是** tasks/armor.hpp 注释里写的那个。
//     详见 docs/keypoint_order.md —— 顺序写反了位姿会错得非常隐蔽。
// #########################################################

int main(int argc, char *argv[])
{
    auto_aim::YOLO detector("configs/yolo.yaml");
    io::Camera camera("configs/yolo.yaml");

    cv::Mat img;
    std::chrono::steady_clock::time_point timestamp;

    while (true)
    {
        camera.read(img, timestamp);   // 读视频还是读相机，由 configs/yolo.yaml 的 source 决定
        if (img.empty())               // 读取失败 或 视频结尾（loop: true 时不会发生）
            break;

        auto armors = detector.detect(img);

        if (!armors.empty())
        {
            auto armor = armors.front();           // 取第一个装甲板
            tools::draw_points(img, armor.points); // 绘制装甲板 4 个关键点

            // #### Task 02 ############################################
            // img_points 是 像素坐标系下 n个点 的坐标，也就是照片上装甲板 4 个点的坐标。
            // 请你填写下面的 img_points:
            //
            // std::vector<cv::Point2f> img_points{ , , , };
            //
            // 提示：
            // - armor.points 就是 YOLO 给出的那 4 个关键点。
            // - 顺序必须与 Task01 的 object_points 一一对应：左上、右上、右下、左下。
            // #########################################################



            // #### Task 03 ############################################
            cv::Mat rvec, tvec;
            // 所有要传入的值都已经具备了。现在调用 solvePnP 解算装甲板位姿，
            // rvec 和 tvec 用于存储 solvePnP 输出的结果。
            // 你需要在下面填写 输入给 solvePnP 的参数：
            //
            // cv::solvePnP(, , , , rvec, tvec);
            //
            // #########################################################



            // #### Task 04 ############################################
            // 现在，draw_text 只打印 0.0
            // 请你改写下面draw_text的参数，把解得的 tvec 和 rvec 打印出来
            //
            tools::draw_text(img, fmt::format("tvec:  x{: .2f} y{: .2f} z{: .2f}", 0.0, 0.0, 0.0), cv::Point(10, 60), cv::Scalar(0, 255, 255), 1.7, 3);
            tools::draw_text(img, fmt::format("rvec:  x{: .2f} y{: .2f} z{: .2f}", 0.0, 0.0, 0.0), cv::Point(10, 120), cv::Scalar(0, 255, 255), 1.7, 3);
            //
            // 提示：
            // - 使用 tvec.at<double>(0)，可以得到一个double变量，它是tvec中首个元素的值。
            // #########################################################



            // #### Task 05 ############################################
            // 使用 cv::Rodrigues ，把 rvec 旋转向量转换为 rmat 旋转矩阵。
            // 再使用反三角函数，把旋转矩阵 rmat 中的元素转化为欧拉角，并在画面上显示。
            //
            tools::draw_text(img, fmt::format("euler angles:  yaw{: .2f} pitch{: .2f} roll{: .2f}", 0.0, 0.0, 0.0), cv::Point(10, 180), cv::Scalar(0, 255, 255), 1.7, 3);
            //
            // 提示：
            // - cv::Mat 的下标从0开始，而不是1。
            // - 从cv::Mat 中取元素的方法和上面的 tvec 类似。如： rmat.at<double>(0, 2)
            // #########################################################
        }

        cv::imshow("press q to quit, space to pause", img);

        int key = cv::waitKey(20);
        if (key == 'q')
            break;
        if (key == ' ')                 // 空格暂停，再按任意键继续
            cv::waitKey(0);
    }

    cv::destroyAllWindows();
    return 0;
}
```

### 4.3 `io/camera.hpp`（取帧接口）

```cpp
#ifndef IO__CAMERA_HPP
#define IO__CAMERA_HPP

#include <chrono>
#include <memory>
#include <opencv2/opencv.hpp>
#include <string>

namespace io
{
// 取帧源的抽象接口。队内的 HikRobot 与教学用的 VideoCamera 都实现它。
class CameraBase
{
public:
  virtual ~CameraBase() = default;

  virtual void read(cv::Mat & img, std::chrono::steady_clock::time_point & timestamp) = 0;

  virtual bool try_read_for(
    cv::Mat & img, std::chrono::steady_clock::time_point & timestamp,
    std::chrono::milliseconds timeout) = 0;

  virtual bool is_alive() const = 0;
};

// 门面：按 configs 里的 source 决定用哪个实现，调用方不用关心
class Camera
{
public:
  explicit Camera(const std::string & config_path);

  void read(cv::Mat & img, std::chrono::steady_clock::time_point & timestamp);

  bool try_read_for(
    cv::Mat & img, std::chrono::steady_clock::time_point & timestamp,
    std::chrono::milliseconds timeout);

  bool is_alive() const;

private:
  std::unique_ptr<CameraBase> camera_;
};

}  // namespace io

#endif  // IO__CAMERA_HPP
```

### 4.4 `configs/yolo.yaml`

```yaml
#需要自行将配置文件中的相机参数补全

yolo_name: yolov5
yolov5_model_path: assets/yolov5.xml
device: CPU
min_confidence: 0.8
use_traditional: true
roi: 
  x: 420
  y: 50
  width: 600
  height: 600

use_roi: false
threshold: 150
# ---------------- 以下为 lecture4 新增：取帧方式 ----------------
# video  : 从 video.path 读视频（默认，人人能跑，便于课上对答案）
# camera : 用 hikrobot 相机（需要 -DWITH_HIKROBOT=ON 且装好 MVS SDK）
source: video
video:
  path: assets/video.avi
  loop: true          # 读到结尾自动重头，避免课堂演示跑到黑屏
camera:
  exposure_ms: 2.5
  gain: 16.9
  vid_pid: "2bdf:0001"
```

### 4.5 检测器与关键点顺序

`tasks/yolos/yolov5.cpp` 走 OpenVINO 推理 `assets/yolov5.xml`，输出 `[1, 25200, 22]`：
`0–7` 四个关键点、`8` objectness、`9–12` 颜色独热、`13–21` 类别独热。
`parse()` 用 4 个关键点的外接矩形当 box，并按 `[0,3,2,1]` 置换后交给 `Armor` 构造函数。

**最终 `Armor.points` 的顺序是 左上、右上、右下、左下**（自左上顺时针）。
`tasks/armor.hpp` 里的注释写的是「左上、左下、右下、右上」——**注释是错的**，原样保留（与学生机器上一致）。
证据链见 `lecture4/yolo/docs/keypoint_order.md`；实测重投影误差中位约 2.7 px。

**`armor.left` / `armor.right` 在本讲是空的**：YOLO 构造函数只初始化 `confidence` / `box` / `points`，
`left`/`right` 走 `Lightbar() {}` 默认构造，四个 `cv::Point2f` 全是 `(0,0)`。
照旧材料写 `armor.left.top` 会拿到四个 `(0,0)`，solvePnP 失败或返回垃圾，**且不报错**。

### 4.6 跑通后的画面

学生版画三行（tvec / rvec / euler angles，未填空时全是 0.0）；参考版多一行 `reproj err`。
程序**不往终端打任何数值**。取帧默认读 `assets/video.avi`（`loop: true`，25 秒一轮，内容是手持数字「2」的装甲板）。
按 `q` 退出，按**空格**暂停。
