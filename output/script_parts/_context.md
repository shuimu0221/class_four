# 讲稿撰写 · 上下文包（唯一事实来源）v3

本文件是撰写《Lecture 4 Hello Armor 装甲板位姿解算》逐字讲稿的唯一素材来源。

> ⚠️ **基准材料**（以本文件为准，不得引用其他版本）：
> - **课件**：根目录《Lecture4_HelloArmor_装甲板位姿解算.pptx》（37 页，未修改）
> - **教案**：根目录《Lecture4_HelloArmor_教案.docx》（未修改）
> - **工程代码**：`lecture4/class`（学生版）与 `lecture4/answer`（参考答案）——**用户刚重构过，一切以当前代码为准**
> - **内容覆盖要求**：两份原视频 PPT《2025装甲板位姿解算_原视频PPT提取》《Hello_Armor_原视频PPT提取》的内容**全部都要讲**（含欧拉角、万向锁、四元数——这些是本讲核心教学内容，不是了解内容）
> - `output/` 目录下带 `_v4/_v5/_v2` 后缀的旧修订版 PPT/教案**已废弃**，与当前代码不符，不得引用。

---

## 〇、任务白名单（最高优先级约束）

**本讲只有 5 个 Task，全部位于同一个文件 `lecture4/class/src/main.cpp`（学生版）。**
（`answer/main.cpp` 是教师参考答案，与学生版逐 Task 对应。）

| Task | 位置（main.cpp） | 学生要做什么 |
|---|---|---|
| **Task 01** | 文件顶部（约 20-35 行） | 填写 `object_points`：装甲板局部坐标系下 4 个点的 3D 坐标（模板被注释着，要先解注释再填） |
| **Task 02** | 主循环内（约 59 行） | 填写 `img_points`：按左上、右上、右下、左下顺序的 4 个 2D 像素点 |
| **Task 03** | 主循环内（约 74 行） | 调用 `cv::solvePnP(object_points, img_points, camera_matrix, distort_coeffs, rvec, tvec);` |
| **Task 04** | 主循环内（约 86 行） | 改写 `draw_text` 参数，把解得的 tvec / rvec 打印到画面上（现在只打印 0.0） |
| **Task 05** | 主循环内（约 99 行） | 用 `cv::Rodrigues(rvec, rmat)` 转旋转矩阵，再用反三角函数从 rmat 提取欧拉角 yaw/pitch/roll 并显示 |

**工程里没有的东西（讲稿不得布置、不得要求实现）：**
- ❌ 重投影 / RMS / `cv::projectPoints`（旧的 PoseSolver 重构版内容，已随代码删除）
- ❌ 距离 / 瞄准角 `distance_m` / `aim_angles_deg`（同上）
- ❌ `PoseSolver` 类、`pose_solver_test`、ctest 验收（文件已删除；CMake 只有 `main` 一个目标）
- ❌ 任何 ONNX / 神经网络分类的现场演示（Detector 已改回纯灯条法，`tiny_resnet.onnx` 虽在目录里但不再被加载）

---

## 一、PPT 全文（共 37 页，逐页）

### 第 1 页 —— 封面
- 眉题：视觉组第四讲 · HELLO ARMOR
- 主标题：**装甲板位姿解算**
- 副标题：从 2D 识别结果到 3D 位姿：cv::solvePnP 全流程实战
- 信息行：主讲人：______　助教：______　时长：90 分钟　承接 Lecture 3《Hello OOP》
- 配图：SP 队徽

### 第 2 页 —— 课程地图 · Roadmap
- 副标题：今天 90 分钟，我们要走完这条链路
- 八个环节（幻灯片印刷时长）：**P0** 复习导入 7 min｜**P1** 为什么装甲板需要"位姿"而不只是位置 7 min｜**P2** PnP 原理与 cv::solvePnP 接口精讲 14 min｜**P3** 动手实验一：Task 01~03，解出 tvec / rvec 20 min｜**P4** rvec 揭秘：旋转向量／矩阵／欧拉角／四元数 14 min｜**P5** 动手实验二：Task 04~05，把旋转变成角度 16 min｜**P6** 坐标系全景：从像素到机器人本体 / IMU 6 min｜**P7** 总结、答疑与作业布置 4 min
- 注：幻灯片八个数合计 88，加开场 2 分钟 = 90。教案时间表把 P7 记 3 分钟（开场 2 + 路线图 1 + 7+7+14+20+14+16+6+3 = 90）。**讲稿分段预算以教案表为准**；讲第 2 页时按幻灯片印刷的数字念即可。

### 第 3 页 —— P0 章节页：复习导入 · 上节课我们手里有了什么？

### 第 4 页 —— P0 · 上节课回顾（Hello OOP）
- C/C++ 编译与 CMake：会写 CMakeLists.txt，能编译、运行自己的工程
- 面向对象：类 = 属性 + 方法；构造/析构函数；封装——数据安全、隐藏实现、便于协作、防止耦合
- 已经写好的两个类：
  - Camera 类：封装取图细节，对外只给一帧图像 + 时间戳
  - 识别器 / Detector 类：目标是识别装甲板并分类（位置、颜色、数字）
  - 两种识别思路：传统灯条法 / YOLO-pose 端到端
- 作业：连接工业相机，封装相机类，用神经网络识别装甲板

### 第 5 页 —— P0 · 现在，程序手里已经有了什么？
- `detector.detect(img)` 返回 `armors`（一个 `Armor` 列表）
- `Armor` 结构体里有 `left` / `right` 两根灯条（`Lightbar`）
- 每根 `Lightbar` 有 `top` / `bottom` 两个端点 → 一块装甲板 = **4 个 2D 像素点**
- 也就是说：识别这一步，已经把"装甲板在哪张图的哪个位置"这件事解决了
- 配图：Armor / Lightbar 结构体关系图

### 第 6 页 —— P0 · 只有这 4 个 2D 点，够瞄准吗？
- 看两张图：3 号车比 4 号车离我们更远 —— 人眼一眼就能判断距离，程序呢？
- 再看三张图：同一块装甲板，角度都不一样 —— 这是"朝向"的差异
- 提问互动：仅凭图像上 4 个像素点的坐标，你能猜出装甲板离相机多远、朝哪个方向偏吗？
- 提示条：引导学生讨论后再进入下一部分

### 第 7 页 —— P1 章节页：为什么需要位姿 · 位置够不够？朝向怎么描述？

### 第 8 页 —— P1 · 位姿 = 位置 + 朝向
- 位置（Position）：一个三维向量 (x, y, z)，装甲板中心在相机坐标系下的坐标
- 朝向（Orientation / Rotation）：装甲板"转了多少度、往哪边转"
- 直观理解朝向——借用飞机的三个转动自由度：
  - 偏航 yaw：绕"上下轴"转，改变朝向左右
  - 俯仰 pitch：绕"左右轴"转，改变抬头低头
  - 横滚 roll：绕"前后轴"转，改变侧向倾斜
- 配图：飞机 yaw / pitch / roll 三轴示意图

### 第 9 页 —— P1 · 先认清两个坐标系
- **装甲板局部坐标系**：原点在装甲板中心，x 向右、y 向下、z 指向板外
  - 物理尺寸（今天要用到）：`ARMOR_WIDTH = 0.135 m`（灯条间宽），`LIGHTBAR_LENGTH = 0.056 m`（单根灯条长）
- **相机坐标系**：原点是镜头光心，随相机刚体一起平移、旋转
- 我们的目标：算出"装甲板坐标系"相对"相机坐标系"的 **旋转 R** 和 **平移 t**

### 第 10 页 —— P1 · 工程上为什么必须要"姿态"，不只是"位置"
- ① 相机和枪管往往不重合、不共轴 —— 只用 2D 画面中心瞄准，会有系统性偏差
- ② 真实机器人会自转、会移动，姿态千变万化 —— 需要用装甲板姿态反推它的旋转中心，才能预测它下一刻在哪
- 一句话：**2D 检测解决"看见"，3D 位姿解决"打中"**

### 第 11 页 —— P2 章节页：PnP 原理与 API · 从对应点到位姿

### 第 12 页 —— P2 · Perspective-n-Points 问题
- 已知 n 组对应点：
  - 物体局部坐标系下的 n 个三维点（我们知道装甲板多大、点在哪）
  - 图像上对应的 n 个二维像素点（检测器已经给出来了）
- 再加上相机的 **内参**（焦距、主点）和 **畸变系数**
- 求解：物体相对相机的 **旋转 R** 和 **平移 t**
- 配图：经典 PnP 示意图：世界坐标系 3D 点 → 图像平面 2D 点，(R, t) 箭头连接两个坐标系

### 第 13 页 —— P2 · cv::solvePnP 函数签名精讲
- OpenCV 已经把 PnP 问题的求解封装成了一个函数，我们只管"喂数据"：
```cpp
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
```

### 第 14 页 —— P2 · 输出到底是什么？
- `tvec`：一个 3×1 向量 —— 装甲板坐标系原点，在相机坐标系下的位置（平移向量）
- `rvec`：也是一个 3×1 向量，代表旋转……
- **rvec 具体是什么？先卖个关子 —— 我们先把代码跑起来，等会儿亲手转一转装甲板，你就懂了**
- 配图：装甲板坐标轴照片 + 相机坐标轴照片（并排对比）

### 第 15 页 —— P3 章节页：动手实验一 · Task 01~03：解出 tvec / rvec

### 第 16 页 —— P3 · 实验环境 & 点位约定
- 项目结构：`class/src/main.cpp` 是你要填空的文件；`tasks/` 下的 Detector 已经帮你写好，直接调用即可
- **关键约定：4 个关键点的顺序** —— 以左上角灯条顶点为 1 号，顺时针 1→2→3→4
  - 1 = 左灯条上端　2 = 右灯条上端　3 = 右灯条下端　4 = 左灯条下端
- 这个顺序在 `object_points` 和 `img_points` 里必须**完全一致**，否则解出来的位姿是错的
- 配图：实物装甲板照片，绿点标注 1/2/3/4 号点位置

### 第 17 页 —— P3 · Task 01 · 填写 object_points
- 正文：在装甲板局部坐标系下写出 4 个点的 (x, y, 0) 坐标，结合 `ARMOR_WIDTH` / `LIGHTBAR_LENGTH` 和上一页的点序
- 代码块（学生版模板）：
```cpp
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
```
- 提示：原点在板中心，x 向右为正、y 向下为正，半宽 = `ARMOR_WIDTH/2`，半高 = `LIGHTBAR_LENGTH/2`

### 第 18 页 —— P3 · Task 02 · 填写 img_points
- 正文：把检测器已经给出的 2D 像素点，按同样的 1→2→3→4 顺序装进 `img_points`
- 代码块（学生版）：
```cpp
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
    // - armor 的成员 left 和 right 是两根灯条 (Lightbar)；
    // - Lightbar 的 top / bottom 端点就是我们要的点。
    // ###########################################################
```

### 第 19 页 —— P3 · Task 03 · 调用 cv::solvePnP
- 正文：`camera_matrix` / `distort_coeffs` 已经在代码里为你准备好，直接传入即可
- 代码块（学生版）：
```cpp
// #### Task 03 ##############################################
cv::Mat rvec, tvec;
// 所有要传入的值都已经具备了。现在调用 solvePnP 解算装甲板位姿，
// rvec 和 tvec 用于存储 solvePnP 输出的结果：
cv::solvePnP( , , , , rvec, tvec);
// ############################################################
```

### 第 20 页 —— P3 · 现场演示 & Debug 小贴士
- 编译运行：`cmake -B build && cmake --build build`，再 `./build/main`
- 跑通后画面上会打印出 tvec 的数值（还未显示，下一环节我们再打出来）
- **常见报错**：`CAP_IMAGES: can't find … video.avi`
  - 原因：在错误的目录下运行了可执行文件；解决：`cd` 回项目根目录，再 `./build/main`
- 配图：终端截图：报错信息 + cd 回根目录后正常运行

### 第 21 页 —— P4 章节页：rvec 揭秘 · 旋转向量 / 矩阵 / 欧拉角 / 四元数

### 第 22 页 —— P4 · 转一转，看一看
- 动手环节：拿起装甲板（或转动摄像头），观察终端里 rvec 三个分量如何变化
- 引导提问：
  - 只绕一个轴转，rvec 的哪个分量在变？
  - 转得越多，rvec 的数值变化有什么规律？
- 先靠直觉猜一猜，再看下一页的数学定义
- 配图：终端滚动输出 rvec 数值随装甲板转动变化的截图

### 第 23 页 —— P4 · rvec 到底是什么
- **旋转向量（rotation vector）**：一种紧凑的旋转表示法
  - 方向 = 旋转轴方向
  - 模长（大小）= 绕这根轴旋转的角度（弧度）
- 好处：只用 3 个数就能表示任意旋转，比 3×3 的旋转矩阵更省

### 第 24 页 —— P4 · 旋转的几种表示法，一张图看懂
- 旋转向量 rvec --[ cv::Rodrigues，可逆 ]--> 旋转矩阵 rmat
- 旋转矩阵 rmat --[ 反三角函数 ]--> 欧拉角（yaw / pitch / roll）
- 旋转矩阵 rmat --[ 转换公式 ]--> 四元数 quaternion
- 三种表示法本质等价，只是在不同场景下各有优劣（下一页展开）
- 配图：rvec → rmat → 欧拉角 / 四元数 流程示意图

### 第 25 页 —— P4 · 从旋转矩阵提取欧拉角（INT_YXZ 约定）
- 正文：拿到 rmat（旋转矩阵）之后，用反三角函数把 yaw / pitch / roll 解出来：
```cpp
// rmat 的第 i 行第 j 列元素记作 m_ij
yaw   = atan2( m13, m33 )
pitch = -asin( m23 )
roll  = atan2( m21, m22 )

// 注意：atan2 / asin 算出来是弧度，乘 57.3 (≈180/π) 换算成角度
```

### 第 26 页 —— P4 · 欧拉角的坑：万向锁（Gimbal Lock）
- **欧拉角**：直观、好理解（yaw / pitch / roll）；**表示不唯一**：不同旋转顺序结果不同；特定姿态下会丢失一个自由度（万向锁）
- **四元数**：4 个数 (w, x, y, z)，无奇异点；插值、连续旋转更稳健；不直观，本讲不展开推导；课后可用 quaternions.online 交互体验两者关系

### 第 27 页 —— P5 章节页：动手实验二 · Task 04~05：把旋转变成看得懂的角度

### 第 28 页 —— P5 · Task 04 · 把 tvec / rvec 打印到画面上
- 正文：现在 `draw_text` 只会打印 0.0，改写参数把真实解出来的值显示出来
- 提示：`tvec.at<double>(0)` 取出的是一个 double，即 tvec 的第一个元素
- 代码块（学生版）：
```cpp
// #### Task 04 ####################################
// 现在，draw_text 只打印 0.0
// 请你改写下面 draw_text 的参数，把解得的 tvec 和 rvec 打印出来
tools::draw_text(img, fmt::format(
    "tvec:  x{:.2f} y{:.2f} z{:.2f}",
    tvec.at<double>(0), tvec.at<double>(1), tvec.at<double>(2)), ...);
tools::draw_text(img, fmt::format(
    "rvec:  x{:.2f} y{:.2f} z{:.2f}",
    rvec.at<double>(0), rvec.at<double>(1), rvec.at<double>(2)), ...);
```

### 第 29 页 —— P5 · Task 05 · rvec → rmat → 欧拉角
- 正文：用 `cv::Rodrigues` 把 rvec 转成 rmat，再套用上一环节的反三角函数公式
- 代码块（学生版）：
```cpp
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
```

### 第 30 页 —— P5 · 现场演示 & 互动
- 转动装甲板：画面上 yaw / pitch / roll 数值实时变化
- 邀请 1~2 位同学上台演示，说说自己观察到的变化规律
- **提问：把装甲板前后移动（不转动），tvec 和 rvec 分别会怎么变？**

### 第 31 页 —— P6 章节页：坐标系全景 · 从像素到机器人本体 / IMU

### 第 32 页 —— P6 · 我真的对准了吗？
- 相机坐标系：与相机刚性连接的坐标系，随相机一起平移、旋转；原点 = 镜头光心
- 思考：如果相机安装时有倾斜，并且和枪管不在同一个位置，会发生什么？
- 答案：仅靠"装甲板在相机坐标系下的位姿"还不够，还要知道相机相对枪管/机器人本体的安装关系

### 第 33 页 —— P6 · 完整的坐标变换链条
- 像素坐标系 --（今天学的 solvePnP）--> 相机坐标系
- 相机坐标系 --（手眼标定，进阶内容）--> 机器人本体坐标系
- 机器人本体坐标系 --（实际测量安装）--> IMU 坐标系
- 今天我们打通了第一环；手眼标定和运动预测（卡尔曼滤波）留给后续课程

### 第 34 页 —— P7 章节页：总结与作业 · 回顾、答疑、布置任务

### 第 35 页 —— P7 · 本讲回顾（7 条）
1. 位姿 = 位置（3D 向量） + 朝向（旋转）
2. PnP 问题：n 组 3D-2D 对应点 + 相机内参 → 解出 R, t
3. `cv::solvePnP`：输入 4 类数据，输出 rvec / tvec
4. tvec = 装甲板原点在相机坐标系下的位置
5. rvec --Rodrigues--> rmat --反三角函数--> 欧拉角 / 四元数
6. 欧拉角存在万向锁问题，四元数更稳健
7. 完整链条：像素 → 相机（solvePnP）→ 机器人本体（手眼标定）→ IMU（安装测量）

### 第 36 页 —— P7 · 课后作业（三档）
- ① **必做**：完成 Task 01~05（课上未完成的部分），跑通并正确显示 tvec / rvec / yaw / pitch / roll
- ② **进阶**：把 solvePnP 接入上节课自己写的 Camera + Detector 类，实时显示真实摄像头画面中装甲板的位姿
- ③ **思考题**：什么姿态下欧拉角会出现万向锁？用 quaternions.online 验证你的猜想，下节课抽查

### 第 37 页 —— Thanks · Q&A
- 副标题：下一讲预告：相机 - 云台手眼标定 与 装甲板运动预测（卡尔曼滤波）

---

## 二、教案（教学设计与时间分配）

### 课程信息
- 课程名称：视觉组第四讲：Hello Armor —— 装甲板位姿解算；90 分钟；承接 Lecture 3《Hello OOP》
- 适用对象：已完成 Lecture 1~3 的视觉组新成员；形式：讲授 + 现场演示 + 随堂编程练习
- 教具：Ubuntu 虚拟机、VS Code、OpenCV4、CMake、装甲板实物 + 工业相机、投影分屏（一路 PPT、一路代码/终端）

### 教学目标（摘要）
**知识与理解**：理解 2D 检测不足以支撑自动瞄准，必须求 3D 位姿（位置+朝向）；理解 PnP 的数学含义；理解 tvec、rvec 物理意义，以及**旋转向量、旋转矩阵、欧拉角、四元数之间的转换关系与适用场景（含万向锁）**；理解像素→本体/IMU 的完整变换链条。
**技能与实践**：能正确调用 `cv::solvePnP` 按约定顺序构造两个点集；**能使用 `cv::Rodrigues` 完成 rvec 与 rmat 的相互转换，并用反三角函数公式提取欧拉角**；能独立完成 Task 01~05 并现场调试（含工作目录类报错排查）。
**重点**：`cv::solvePnP` 的输入输出与调用方式；四点顺序约定与对应关系。
**难点**：rvec/rmat/欧拉角/四元数之间的转换关系与万向锁的理解；坐标系变换链条的整体把握。

### 教学过程与时间分配（共 90 分钟；页码为 37 页课件实际页序）

| 时间 | 环节 | 教师活动 | 学生活动 |
|---|---|---|---|
| 0:00-0:02 (2min) | 开场 / P.1 | 说明本讲目标：从"看到装甲板"到"算出装甲板在哪、朝哪" | 明确本讲定位与产出 |
| 0:02-0:03 (1min) | 课程地图 / P.2 | 过一遍 8 个环节的顺序和大致用时 | 了解节奏 |
| 0:03-0:10 (7min) | P0 复习导入 / P.3-6 | 快速回顾 OOP/封装/Camera/Detector；提问"程序现在手里有什么"引出 4 个 2D 点；用"3号车 vs 4号车""同一装甲板三种朝向"两组照片提问引入 | 回答提问，讨论仅凭 2D 点能否判断距离与朝向 |
| 0:10-0:17 (7min) | P1 为什么需要位姿 / P.7-10 | 讲"位姿=位置+朝向"；飞机比喻讲 yaw/pitch/roll；两个坐标系；两条工程理由 | 记录坐标系定义与 ARMOR_WIDTH/LIGHTBAR_LENGTH 数值 |
| 0:17-0:31 (14min) | P2 PnP 原理与 API / P.11-14 | 讲 PnP 定义；逐参数讲签名；讲 tvec；**rvec 留悬念** | 对照 PPT 把函数签名抄进自己代码注释，标出参数对应关系 |
| 0:31-0:51 (20min) | P3 动手实验一 Task01-03 / P.15-20 | 讲项目结构与点序约定；逐 Task 讲思路（不直接给答案）；巡场答疑；现场跑通演示；讲 video.avi 找不到的经典报错 | 打开工程，依次完成 Task01→02→03，编译运行验证 tvec 解出 |
| 0:51-1:05 (14min) | P4 rvec揭秘与旋转表示法 / P.21-26 | 组织"转一转看一看"小实验，引导学生观察 rvec 分量变化规律；讲 rvec 定义（轴+角）；讲 rvec⇄rmat（Rodrigues）与 rmat→欧拉角公式（INT_YXZ）；讲万向锁与四元数（点到为止） | 亲手/观摩转动装甲板，口头描述规律；**记录 INT_YXZ 公式** |
| 1:05-1:21 (16min) | P5 动手实验二 Task04-05 / P.27-30 | 讲 Task04(打印tvec/rvec)、Task05(Rodrigues+反三角函数算欧拉角)思路与提示；巡场答疑；邀请1-2名学生上台演示、描述 yaw/pitch/roll 变化 | 完成 Task04、Task05，编译运行，转动装甲板观察角度实时变化 |
| 1:21-1:27 (6min) | P6 坐标系全景 / P.31-33 | "我真的对准了吗"；相机与枪管不共轴；完整变换链条 | 建立全局坐标链条心智图，明确今天只完成第一环 |
| 1:27-1:30 (3min) | P7 总结 / P.34-36 | 带学生过 7 条知识点回顾 | 对照笔记/代码自查 |
| 1:30（可延展至课后） | 作业布置 & Q&A / P.37 | 布置必做/进阶/思考题三档作业，说明下节课抽查思考题；开放提问 | 记录作业，提出遗留问题 |

### Task 01~05 参考答案（教师用，**不对学生展示**；讲稿只讲思路与提示）

**Task 01：object_points**（约定：原点在板中心，x 向右为正，y 向下为正；半宽 = ARMOR_WIDTH/2，半高 = LIGHTBAR_LENGTH/2）
```cpp
static const std::vector<cv::Point3f> object_points {
    { -ARMOR_WIDTH / 2, -LIGHTBAR_LENGTH / 2, 0 },  // 点 1  左上
    {  ARMOR_WIDTH / 2, -LIGHTBAR_LENGTH / 2, 0 },  // 点 2  右上
    {  ARMOR_WIDTH / 2,  LIGHTBAR_LENGTH / 2, 0 },  // 点 3  右下
    { -ARMOR_WIDTH / 2,  LIGHTBAR_LENGTH / 2, 0 }   // 点 4  左下
};
```

**Task 02：img_points**
```cpp
std::vector<cv::Point2f> img_points{
    armor.left.top,     // 点 1  左上
    armor.right.top,    // 点 2  右上
    armor.right.bottom, // 点 3  右下
    armor.left.bottom   // 点 4  左下
};
```

**Task 03：调用 solvePnP**
```cpp
cv::Mat rvec, tvec;
cv::solvePnP(object_points, img_points, camera_matrix, distort_coeffs, rvec, tvec);
```

**Task 04：显示 tvec / rvec**
```cpp
tools::draw_text(img, fmt::format("tvec:  x{: .2f} y{: .2f} z{: .2f}",
    tvec.at<double>(0), tvec.at<double>(1), tvec.at<double>(2)), cv::Point2f(10, 60), 1.7, cv::Scalar(0, 255, 255), 3);
tools::draw_text(img, fmt::format("rvec:  x{: .2f} y{: .2f} z{: .2f}",
    rvec.at<double>(0), rvec.at<double>(1), rvec.at<double>(2)), cv::Point2f(10, 120), 1.7, cv::Scalar(0, 255, 255), 3);
```

**Task 05：rvec → rmat → 欧拉角**（⚠️ 以当前 `answer/main.cpp` 代码为准——**没有乘 57.3，画面显示的是弧度**）
```cpp
cv::Mat rmat;
cv::Rodrigues(rvec, rmat);
double yaw = atan2(rmat.at<double>(0, 2), rmat.at<double>(2, 2));
double pitch = -asin(rmat.at<double>(1, 2));
double roll = atan2(rmat.at<double>(1, 0), rmat.at<double>(1, 1));
tools::draw_text(img, fmt::format("euler angles:  yaw{: .2f} pitch{: .2f} roll{: .2f}",
    yaw, pitch, roll), cv::Point2f(10, 180), 1.7, cv::Scalar(0, 255, 255), 3);
```
> 讲解口径：画面上的三个角是**弧度**（数值很小，比如 0.12）；PPT 第 25 页注释里那句"乘 57.3 (≈180/π) 换算成角度"是给学生的话——想看度数自己乘 57.3。原视频课的演示代码是打印 `yaw * 57.3` 的度数值（如 yaw: 14.36）。讲稿按当前代码讲弧度，并把 57.3 作为补充说明讲清楚，**不要把两个口径讲混**。

### 演示与教具
- 装甲板实物 1 块（标注 1/2/3/4 号点）；工业相机 + 三脚架/云台接虚拟机
- LECTURE4 工程提前拷到虚拟机桌面；降级方案：answer/ 版预录制运行视频
- 投影分屏：一路 PPT，一路代码/终端

### 作业布置（三档）
- ① 必做：完成 Task 01~05，本地编译运行通过，画面正确显示 tvec / rvec / yaw / pitch / roll
- ② 进阶：将 solvePnP 代码接入上节课自己实现的 Camera + Detector 类，用真实摄像头实时显示装甲板三维位姿（而非固定 video.avi）
- ③ 思考题（下节课抽查）：什么姿态下欧拉角会出现万向锁？用 quaternions.online 交互验证猜想，并简述观察到的现象

---

## 三、两份原视频课的「必须覆盖清单」（用户硬性要求：内容都要讲）

以下内容来自《2025装甲板位姿解算_原视频PPT提取》与《Hello_Armor_原视频PPT提取》两份原始课件/录课，**讲稿必须全部覆盖**（大部分已落在 37 页课件的对应页上，括号内为对应页）：

**动机与直观（P0/P1）**
- 3 号车 vs 4 号车："相比于 4 号车，3 号车离我们更远"——人眼能判断距离（第 6 页）
- 同一块装甲板三种角度："图片中的三块装甲板有什么不同？"——朝向差异（第 6 页）
- 欧拉角按特定顺序定义：先偏航（绕上下轴）、再俯仰（绕左右轴）、后横滚（绕前后轴），每一步相对前一步的结果（第 8 页）
- "看出"三维信息 = 距离远近 + 朝向左右 → 更准确地说：位置用三维向量、旋转用欧拉角 → "程序能解算这些信息吗？"（第 8-9 页）

**PnP 与 API（P2）**
- PnP：n 组一一对应的点 + 相机内参/畸变 → 解 R、t（第 12 页）
- solvePnP 逐参数讲解（第 13 页）
- tvec = 装甲板坐标系原点在相机系下的位置；**rvec 留悬念："先写代码，留个悬念，后面再来解答"**（第 14 页）

**rvec 揭秘（P4）——核心章节，必须讲透**
- "转一转，看一看"：转动装甲板观察 rvec 方向和大小；原课演示过终端滚动输出 `roll: 2.01 → 6.40` 这类数值（第 22 页）
- rvec 定义：方向 = 旋转轴，模长 = 转角（弧度）；3 个数表示任意旋转（第 23 页）
- 概念图：旋转向量 rvec --罗德里格斯公式/cv::Rodrigues（可逆）--> 旋转矩阵 rmat --反三角函数--> 欧拉角；rmat --> 四元数（第 24 页）
- **INT_YXZ 欧拉角公式：θ₁ = arctan2(m₁₃, m₃₃)，θ₂ = −arcsin(m₂₃)，θ₃ = arctan2(m₂₁, m₂₂)**（第 25 页）
- 关键对应关系：公式里的 m₁₃ 是 rmat 第 1 行第 3 列，但 **cv::Mat 下标从 0 开始**，所以代码里写 `rmat.at<double>(0, 2)`——这是学生最容易错的地方（第 25/29 页）
- `std::atan2(double, double)` 是 C++ 标准库函数（原课专门给过这个提示）（第 25 页）
- 弧度 × 57.3 (≈180/π) 换算成角度（第 25 页注释）
- 万向锁：欧拉角表示不唯一、特定姿态丢一个自由度；四元数 (w,x,y,z) 无奇异点、插值稳健、不直观（第 26 页）
- **quaternions.online 现场交互演示**：Quaternion 的 W/X/Y/Z 输入框 + Euler Angles 的 X/Y/Z 和 XYZ-Order 下拉框，红 x / 绿 y / 蓝 z 的 3D 网格实时联动——原 Hello Armor 课现场演示过浏览器这个网站（第 26 页提到，讲稿应作为现场/课后演示展开）

**动手实验（P3/P5）**
- 点序约定 1→2→3→4（左上起顺时针）；两个点集顺序必须一致（第 16 页）
- Task 01~03 填空思路与提示，不给答案（第 17-19 页）
- 经典报错：`CAP_IMAGES: can't find starting number … video.avi`——在 build/ 目录里直接 ./main 导致；`cd` 回项目根目录再 `./build/main`（第 20 页）
- Task 04：`tvec.at<double>(0)` 取出 double；fmt::format 与 draw_text（第 28 页）
- Task 05：Rodrigues + 反三角函数 + 显示（第 29 页）
- 转动装甲板看 yaw/pitch/roll 实时变化；邀请学生上台；提问"前后移动（不转动）装甲板，tvec 和 rvec 分别怎么变？"——答：tvec 变、rvec 基本不变（第 30 页）

**坐标系全景（P6）**
- 相机坐标系：与相机刚性连接、随相机平移旋转、原点 = 镜头光心；"如果相机安装有倾斜，并且和枪管不在同一个位置，会怎么样？"（第 32 页）
- "实际车的运动状态千奇百怪，我们需要装甲板姿态来推算出它的旋转中心，进而对运动进行拟合"（第 10 页）
- 手眼标定：获取机器人本体坐标系→相机坐标系的变换（机械臂 AX=XB 标定环）（第 33 页）
- IMU："机器人本体控制依赖于 imu（陀螺仪），需要知道 imu 到本体坐标系之间的变换"（第 33 页）
- 完整链条：像素坐标系 → 相机坐标系 → 机器人本体坐标系 → IMU 坐标系，分别靠 solvePnP / 手眼标定 / 实际安装（第 33 页）

**收尾（P7）**
- 7 条回顾（第 35 页）；三档作业（第 36 页）；Thanks + 下一讲预告（第 37 页）
- 原课收尾还带过一遍课程大纲：Lesson 1 Ubuntu shell g++ → Lesson 2 CMake → Lesson 3 OpenCV → Lesson 4 OOP → Lesson 5 PnP（可作 P7 口头回顾素材）

**可引用的课后参考链接（原课件出现过，可作"放群里"的口头补充）**
- 万向锁知乎文章：https://zhuanlan.zhihu.com/p/9135205633
- 线性代数（旋转矩阵背景）B 站视频：https://www.bilibili.com/video/BV1ns41167b9
- OpenCV 四元数类文档 `cv::Quat`：https://docs.opencv.org/4.x/d4/d4a/classcv_1_1Quat.html
- 交互演示网站：quaternions.online

---

## 四、工程代码（讲稿涉及代码必须与这里一致）

### 4.1 目录与构建

```
lecture4/
├── class/                  # ★ 学生版（要填空的只有 src/main.cpp）
│   ├── CMakeLists.txt
│   ├── video.avi           # 课堂回放视频（不会被复制进 build/，留在本目录）
│   ├── tiny_resnet.onnx    # 遗留文件，当前 Detector 不再加载
│   ├── io/camera.{hpp,cpp} # 上节课的相机类（本讲不用，进阶作业用）
│   ├── tools/img_tools.hpp # draw_points / draw_text
│   ├── tasks/armor.hpp     # Lightbar / Armor 结构体
│   ├── tasks/detector.{hpp,cpp}  # 已写好的灯条法检测器
│   └── src/main.cpp        # ★ Task 01~05 全在这一个文件
└── answer/main.cpp         # 教师参考答案（与学生版逐 Task 对应）
```

CMake（`lecture4/class/CMakeLists.txt`）：项目 `Lecture_4`，C++17，**唯一可执行目标 `main`**（`src/main.cpp` + `tasks/detector.cpp`，链接 OpenCV 和 fmt）。**没有测试目标、没有资源拷贝**。

构建与运行（Ubuntu 终端，**必须先进入 `lecture4/class` 目录**）：
```bash
cd lecture4/class
cmake -B build
cmake --build build
./build/main        # 从项目根目录运行，才能找到 video.avi
```
在 `build/` 目录里直接 `./main` 会报：
```
OpenCV(4.5.4) error: (-5:Bad argument) CAP_IMAGES: can't find starting number
(in the name of file): video.avi in function 'icvExtractPattern'
```
解决：`cd ..` 回项目根目录，再 `./build/main`。**这是本讲要现场讲的经典坑。**

### 4.2 `class/src/main.cpp`（学生版全文要点）

```cpp
#include "tasks/detector.hpp"
#include "tools/img_tools.hpp"
#include "fmt/core.h"

// 相机内参（3×3）
static const cv::Mat camera_matrix =
    (cv::Mat_<double>(3, 3) << 1286.307063384126, 0, 645.34450819155256,
                                0, 1288.1400736562441, 483.6163720308021,
                                0, 0, 1);
// 畸变系数（1×5）
static const cv::Mat distort_coeffs =
    (cv::Mat_<double>(1, 5) << -0.47562935060124745, 0.21831745829617311,
                                0.0004957613589406044, -0.00034617769548693592, 0);

static const double LIGHTBAR_LENGTH = 0.056; // 灯条长度    单位：米
static const double ARMOR_WIDTH = 0.135;     // 装甲板宽度  单位：米

// #### Task 01 #####（整段模板被 // 注释着，学生要先解注释再填四个坐标）
// static const std::vector<cv::Point3f> object_points {
//     {          ,           , 0 },  // 点 1
//     {          ,           , 0 },  // 点 2
//     {          ,           , 0 },  // 点 3
//     {          ,           , 0 }   // 点 4
// };
// 提示：- 四个点都在 z=0 平面上，0 已填好
//      - "你应当用 ± ARMOR_WIDTH / 2 这样的写法来填写"

int main(int argc, char *argv[])
{
    auto_aim::Detector detector;
    cv::VideoCapture cap("video.avi");
    cv::Mat img;
    while (true)
    {
        cap >> img;
        if (img.empty()) break;
        auto armors = detector.detect(img);
        if (!armors.empty())
        {
            auto armor = armors.front();            // 取第一个装甲板
            tools::draw_points(img, armor.points);  // 绘制装甲板

            // #### Task 02 #####  std::vector<cv::Point2f> img_points{ , , , };
            // 提示：armor.left / armor.right 是两根 Lightbar，
            //      灯条的 top / bottom 端点就是我们要的点

            // #### Task 03 #####  cv::Mat rvec, tvec;
            // cv::solvePnP(, , , , rvec, tvec);

            // #### Task 04 #####（现在只打印 0.0，要改成真实值）
            tools::draw_text(img, fmt::format("tvec:  x{: .2f} y{: .2f} z{: .2f}", 0.0, 0.0, 0.0), cv::Point2f(10, 60), 1.7, cv::Scalar(0, 255, 255), 3);
            tools::draw_text(img, fmt::format("rvec:  x{: .2f} y{: .2f} z{: .2f}", 0.0, 0.0, 0.0), cv::Point2f(10, 120), 1.7, cv::Scalar(0, 255, 255), 3);
            // 提示：tvec.at<double>(0) 得到一个 double，是 tvec 首个元素的值

            // #### Task 05 #####（要自己写 Rodrigues + 欧拉角公式）
            tools::draw_text(img, fmt::format("euler angles:  yaw{: .2f} pitch{: .2f} roll{: .2f}", 0.0, 0.0, 0.0), cv::Point2f(10, 180), 1.7, cv::Scalar(0, 255, 255), 3);
            // 提示：cv::Mat 下标从 0 开始；取元素如 rmat.at<double>(0, 2)
        }
        cv::imshow("press q to quit", img);
        if (cv::waitKey(20) == 'q') break;
    }
    cv::destroyAllWindows();
    return 0;
}
```

### 4.3 `tasks/armor.hpp`（Task 02 要用）

```cpp
struct Lightbar
{
  std::size_t id;
  Color color;
  cv::Point2f center, top, bottom, top2bottom;
  std::vector<cv::Point2f> points;
  double angle, angle_error, length, ratio;
};

struct Armor
{
  Color color;
  const Lightbar left, right;
  cv::Point2f center;       // 不是对角线交点，不能作为实际中心！
  cv::Point2f center_norm;
  std::vector<cv::Point2f> points;   // 已按 左上、右上、右下、左下 排好
  double ratio, side_ratio, rectangular_error;
  ArmorType type;           // big / small
  ArmorName name;           // one/two/.../not_armor
  ArmorPriority priority;
  cv::Mat pattern;
  double confidence;
  bool duplicated;
  double yaw_raw;           // rad

  Armor(const Lightbar & left, const Lightbar & right)
  {
    color = left.color;
    center = (left.center + right.center) / 2;
    points.emplace_back(left.top);
    points.emplace_back(right.top);
    points.emplace_back(right.bottom);
    points.emplace_back(left.bottom);
    // ... ratio / side_ratio / rectangular_error
  }
};
```

### 4.4 `tools/img_tools.hpp` 绘图接口

```cpp
inline void draw_points(cv::Mat &img, const std::vector<cv::Point> &points,
                        const cv::Scalar &color = cv::Scalar(0, 0, 255), int thickness = 2);
inline void draw_points(cv::Mat &img, const std::vector<cv::Point2f> &points, ...);
inline void draw_text(cv::Mat &img, const std::string &text, const cv::Point &point,
                      double font_scale = 1.0,
                      const cv::Scalar &color = cv::Scalar(0, 255, 255), int thickness = 2);
```

### 4.5 Detector（已写好，学生直接用；纯灯条法，无神经网络）

流程：BGR→灰度→`threshold(170)` 二值化→`findContours`→`minAreaRect` 得灯条→几何筛选（灯条角度误差 < 45°、长宽比 1.5~20、长度 > 8 px）→取颜色→灯条从左到右排序→同色配对成 Armor→装甲板几何筛选→分类命名。
巡场提示：画面里检测不到装甲板时，先看视频是否正常播放，再想灯条是否太暗/太亮（阈值 170）、颜色筛选、几何条件是否过滤掉了灯条。**不要提分类置信度——当前 Detector 没有 ONNX。**

### 4.6 跑通后的画面（answer 版）

- 装甲板轮廓被 `draw_points` 画出；三行黄色大字（字号 1.7、线宽 3）从上到下：
  - `tvec:  x{: .2f} y{: .2f} z{: .2f}`（y=60）
  - `rvec:  x{: .2f} y{: .2f} z{: .2f}`（y=120）
  - `euler angles:  yaw{: .2f} pitch{: .2f} roll{: .2f}`（y=180）——**三个角是弧度**
- 窗口标题：`press q to quit`
- 原视频课的实拍样例（度数口径，供老师口头参考）：`tvec: x-0.00 y 0.01 z 0.24`、`yaw: 14.36, pitch: 1.68, roll: 3.66`
