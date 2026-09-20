# Lecture4「Hello Armor」YOLO 版教学程序 — 设计文档

日期：2026-09-20
状态：待评审

## 1. 背景与目标

第四讲现有两种材料：

- `lecture4/class/` — 学生起步代码。`tasks/detector.{hpp,cpp}` 是一个**手写的传统 CV 检测器**（灰度阈值 → 找轮廓 → 配对灯条 → `tiny_resnet.onnx` 分类数字），`src/main.cpp` 里有 5 个填空任务，内容**全部是 PnP 位姿解算**。
- `lecture4/answer/main.cpp` — 上述 5 个任务的参考实现。
- `lecture4/homework/` — 另一个无关主题（能量机关 buff）的作业，已示范了 OpenVINO + YOLO11 的用法和 `io/tasks/tools` 工程骨架。

**目标**：新增一份**基于 YOLO 的同一讲教学程序**，放在 `lecture4/yolo/`，与 `class/` 并列共存。

**核心教学主张**：`class/` 里那个手写 `Detector` 交给 `main.cpp` 的东西，本质上只有**装甲板的 4 个角点**。把 `Detector` 换成 YOLO 实现后，公开接口一字不改、输出的还是 4 个角点 —— 于是 Task01/03/04/05 一个字都不用动。这让学生直观看到「检测是可替换的前端，位姿解算是那个不变的核心」。

**学生动手范围**：只有 PnP。YOLO 检测器作为黑盒完整提供（与 `class/` 版一致，学生也不曾需要实现传统检测器）。

## 2. 已验证的关键事实

以下事实通过临时 Python venv（`opencv-python 5.0.0` + `openvino 2026.4.0`）在 `assets/yolov8c.xml` 和 `class/video.avi` 上实测得到，非推测。

### 2.1 视频

`lecture4/class/video.avi`：**752 帧、1280×1024、30 fps**（约 25 秒）。内容是实验室里一个人手持一块数字「2」的装甲板。**适合本讲**。

### 2.2 模型

`sp_vision_26/assets/yolov8c.xml`：

- IR 输入：`float32 [1, 3, 640, 640]`（NCHW）
- IR 输出：`float32 [1, 19, 1600]`
- `19 = 4 (box: cx,cy,w,h) + 7 (类别) + 8 (4 个关键点的 x,y)`
- 7 个类别 id：`0=sentry, 1=one, 2=two, 3=three, 4=four, 5=outpost, 6=base`
- **输入应为灰度**：训练时用的就是灰度图。调用方需做 `BGR → GRAY → BGR`（三通道灰度），否则属于分布外输入。

### 2.3 检测效果

抽帧（每 5 帧取 1 帧）统计：

- 151 个抽样帧中 **148 帧检出装甲板**（3 帧漏检，出现在手持板快速移动的运动模糊处）
- 置信度范围 **0.733 – 0.931**，均值 0.880
- 每帧最多 1 个目标（视频里始终只有一块装甲板；`main.cpp` 取 `armors.front()`，够用）

### 2.4 关键点顺序（本设计最关键的一条）

模型**原始输出**的 4 个关键点顺序是：

```
kp[0] = 左灯条顶部    (TL)
kp[1] = 左灯条底部    (BL)
kp[2] = 右灯条底部    (BR)
kp[3] = 右灯条顶部    (TR)
```

**不是** `[TL, TR, BR, BL]`。`sp_vision_26/tasks/auto_aim/yolos/yolov8c.cpp` 里的 `sort_keypoints()` 正是做这件事：

```cpp
swap(keypoints[1], keypoints[3]);   // [TL,BL,BR,TR] -> [TL,TR,BR,BL]
```

在这 148 个检出帧上逐帧校验排序规则，**违规 0 次**：

| 校验项 | 违规次数 |
|---|---|
| `TL.y < BL.y` | 0 |
| `TR.y < BR.y` | 0 |
| `TL.x < TR.x` | 0 |
| `BL.x < BR.x` | 0 |

同时，按该顺序计算图像上四边形「上边 / 左边」的像素长度比，均值 **2.30**；而 `object_points` 蕴含的 `ARMOR_WIDTH / LIGHTBAR_LENGTH = 0.135 / 0.056 = 2.41`，**偏差 4.4%**（范围 1.85–3.10，由透视和观测角度解释）。这证实了尺寸对应关系成立：

- 四边形的**上边**（TL→TR）对应装甲板宽度 `0.135 m`
- 四边形的**左边**（TL→BL）对应灯条长度 `0.056 m`

**结论：`class/main.cpp` 与 `answer/main.cpp` 里的 `object_points` 可以原样复用，无需修改。**

## 3. 目录结构

```
lecture4/yolo/
├── CMakeLists.txt          # OpenCV + fmt + OpenVINO，两个 target
├── assets/
│   ├── yolov8c.xml         # 从 sp_vision_26/assets/ 复制
│   ├── yolov8c.bin         # 从 sp_vision_26/assets/ 复制
│   └── video.avi           # 从 lecture4/class/video.avi 复制
├── tools/
│   └── img_tools.hpp       # 从 lecture4/class/tools/ 复制（header-only，未改动）
├── tasks/
│   ├── armor.hpp           # 精简版 Armor
│   ├── yolo.hpp            # 公开接口 = class/tasks/detector.hpp 完全一致
│   └── yolo.cpp            # OpenVINO 推理 + 后处理（学生不动，~140 行）
├── src/
│   └── main.cpp            # 学生填空版：Task01–05
└── answer/
    └── main.cpp            # 参考实现
```

`class/`、`answer/`、`homework/` 完全不动。

## 4. 组件设计

### 4.1 `tasks/armor.hpp`

YOLO 直接回归角点，不需要灯条配对，所以 `Lightbar`、`Color`、`ArmorType`、`ArmorPriority` 全部删除。

```cpp
namespace auto_aim
{
// 与 yolov8c 的 7 个类别 id 一一对应
const std::vector<std::string> ARMOR_NAMES = {
  "sentry", "one", "two", "three", "four", "outpost", "base"};

struct Armor
{
  int class_id;
  double confidence;
  cv::Rect box;
  std::vector<cv::Point2f> points;  // 4 个关键点，顺序固定为 TL, TR, BR, BL
  cv::Point2f center;
  cv::Point2f center_norm;
};
}  // namespace auto_aim
```

### 4.2 `tasks/yolo.hpp`

**公开接口与 `class/tasks/detector.hpp` 逐字一致**，这是整个教学主张的载体。

```cpp
namespace auto_aim
{
class Detector
{
public:
  Detector();
  std::list<Armor> detect(const cv::Mat & bgr_img);

private:
  struct Transform { double scale; int pad_left; int pad_top; };

  static Transform make_letterbox(const cv::Size & size);
  static cv::Mat apply_letterbox(const cv::Mat & mono_img, const Transform & t);
  static cv::Point2f to_source(const cv::Point2f & pt, const Transform & t);
  static void sort_keypoints(std::vector<cv::Point2f> & kpts);
  std::list<Armor> parse(const cv::Mat & output, const Transform & t);
  static void draw(const cv::Mat & img, const std::list<Armor> & armors);

  ov::Core core_;
  ov::CompiledModel compiled_model_;
  ov::InferRequest infer_request_;
};
}  // namespace auto_aim
```

命名说明：文件/目录叫 `yolo.*` 点明技术，类名保持 `Detector` 让 `main.cpp` 的调用形式不变。若更希望类名体现技术，可改为 `YOLO` 并同步改 `main.cpp` 一处 —— 由评审决定。

### 4.3 `tasks/yolo.cpp`

流程（照搬 `yolov8c.cpp` 的推理路径，去掉教学无关部分）：

1. `Detector::Detector()`：`core_.read_model("assets/yolov8c.xml")`，用 `ov::preprocess::PrePostProcessor` 把输入声明为 `u8 / NHWC / {1,640,640,3} / BGR`，内部 `f32 + RGB + scale(255)`，再 `compile_model(..., "CPU")`。
2. `detect(bgr_img)`：
   - `cv::cvtColor(bgr, gray, COLOR_BGR2GRAY)` 再 `cv::cvtColor(gray, mono, COLOR_GRAY2BGR)` —— **模型训练时输入是灰度**，这一步不能省。
   - letterbox 到 640×640（保比例 resize + **灰色 114 填充**，与 `yolov8c.cpp` 的默认 padding 一致）。
   - `ov::Tensor(ov::element::u8, {1,640,640,3}, mono.data)` → `infer()`。
   - `parse()`：输出 `[1, 19, 1600]`。对每个 anchor 取第 4–10 行的类别最大分；`score > 0.5` 则取第 0–3 行做 box、第 11–18 行做 4 个关键点；全部反 letterbox 映射回原图坐标。
   - `cv::dnn::NMSBoxes`，`nms_threshold = 0.3`。
   - `sort_keypoints()`（`swap(kp[1], kp[3])`）把关键点规范成 `[TL, TR, BR, BL]`。
   - 组装 `Armor`，`center` 取 box 中心，`center_norm` 取归一化坐标。
   - 画框 + 画点（调 `tools::draw_points` / `tools::draw_text`），便于学生肉眼确认。
3. 常量：`kClassNum = 7`、`kInputSize = 640`、`kConfThreshold = 0.5`、`kNmsThreshold = 0.3`。

**与队内真实代码的有意差异**（教学简化，需在讲解时说明）：

| 队内 `yolov8c` | 教学版 | 原因 |
|---|---|---|
| ROI / 动态 ROI（强制开启） | 取消，全图推理 | 少一个与 PnP 无关的概念；模型本身不依赖 ROI |
| `armor_color_estimator` + 32 项 `armor_properties` 查表 | 取消，类别名用 7 项 vector | 本讲只需要 4 个角点，不需要颜色 |
| `Classifier` / 传统 `Detector` 成员 | 无依赖 | 教学版是自包含的 |
| 配置从 yaml 读 | 常量硬编码 | 学生不用理解配置层 |

### 4.4 `src/main.cpp`

结构与 `class/src/main.cpp` 一一对应，保留 `// #### Task 0N ####` 注释块和提示写法。

| Task | class/ 版（传统 CV） | yolo/ 版（YOLO） |
|---|---|---|
| 01 `object_points` | `±ARMOR_WIDTH/2, ±LIGHTBAR_LENGTH/2` | **完全相同，不变** |
| 02 `img_points` | `armor.left.top, armor.right.top, armor.right.bottom, armor.left.bottom` | `armor.points.at(0..3)` |
| 03 `solvePnP` | `cv::solvePnP(object_points, img_points, camera_matrix, distort_coeffs, rvec, tvec)` | **完全相同，不变** |
| 04 打印 `tvec` / `rvec` | `tvec.at<double>(0..2)` | **完全相同，不变** |
| 05 `Rodrigues` + 欧拉角 | 不变 | **完全相同，不变** |

Task02 的提示文案要相应改写：仍然强调「像素点与物体点必须**一一对应**」，但取点来源从两根灯条改成模型输出的 4 个关键点，并说明顺序已由检测器规范为 `[左上, 右上, 右下, 左下]`。

骨架（学生版留下填空）：

```cpp
static const double LIGHTBAR_LENGTH = 0.056; // 灯条长度    单位：米
static const double ARMOR_WIDTH = 0.135;     // 装甲板宽度  单位：米

// #### Task 01 ####
// static const std::vector<cv::Point3f> object_points{ ... };

int main()
{
    auto_aim::Detector detector;
    cv::VideoCapture cap("assets/video.avi");
    cv::Mat img;
    while (true) {
        cap >> img;
        if (img.empty()) break;
        auto armors = detector.detect(img);
        if (!armors.empty()) {
            auto armor = armors.front();
            tools::draw_points(img, armor.points);
            // Task 02 img_points / Task 03 solvePnP / Task 04 打印 / Task 05 欧拉角
        }
        cv::imshow("press q to quit", img);
        if (cv::waitKey(20) == 'q') break;
    }
    cv::destroyAllWindows();
    return 0;
}
```

相机内参与畸变系数沿用 `class/src/main.cpp` 顶部那份，原样复制。

### 4.5 `CMakeLists.txt`

```cmake
cmake_minimum_required(VERSION 3.16.3)
project(Lecture_4_YOLO)
set(CMAKE_CXX_STANDARD 17)
find_package(OpenCV REQUIRED)
find_package(fmt REQUIRED)
find_package(OpenVINO REQUIRED)
include_directories(${OpenCV_INCLUDE_DIRS} ${PROJECT_SOURCE_DIR})

# 配置期把 assets/ 拷到构建目录，使程序在源码目录或 build/ 下运行都能找到资源
file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/assets DESTINATION ${CMAKE_CURRENT_BINARY_DIR})

add_executable(main src/main.cpp tasks/yolo.cpp)
target_link_libraries(main ${OpenCV_LIBS} fmt::fmt openvino::runtime)

add_executable(answer answer/main.cpp tasks/yolo.cpp)   # 便于在开发机上验证
target_link_libraries(answer ${OpenCV_LIBS} fmt::fmt openvino::runtime)
```

比 `class/CMakeLists.txt` 多出的：`openvino` 依赖、`file(COPY assets)`、以及一个 `answer` target（`class/` 的 answer 只是参考文件、不参与构建；这里编出来是为了能在真机上跑通验证）。

## 5. 数据流

```
assets/video.avi
  └─ cv::VideoCapture → cv::Mat(BGR, 1280x1024)
       └─ Detector::detect()
            ├─ 灰度化 (BGR→GRAY→BGR)
            ├─ letterbox → 640x640 (u8 NHWC)
            ├─ OpenVINO infer → [1,19,1600]
            ├─ 阈值 + NMS + 反 letterbox + sort_keypoints
            └─ → Armor{ points = [TL,TR,BR,BL] }
       └─ main.cpp: 取 armor.points 组成 img_points
            └─ cv::solvePnP(object_points, img_points, K, D) → rvec, tvec
                 ├─ Task04: 打印 tvec / rvec
                 └─ cv::Rodrigues(rvec) → rmat → 欧拉角 (yaw/pitch/roll)
```

## 6. 验收标准

在 **Linux 开发机**（需 OpenCV、fmt、OpenVINO）上：

1. `cmake -B build && cmake --build build -j` 在 `lecture4/yolo/` 下无错通过。
2. 运行 `./build/answer`，窗口内应能看到：
   - 装甲板被绿色四边形勾勒（4 个关键点落在两根灯条的上/下端点）
   - `tvec` / `rvec` / 欧拉角三行文字数值随视频变化，且**量级合理**
     （`z` 应在几十厘米到几米量级，欧拉角在 ±π 内）
3. 关键点落点肉眼校验：编号点必须落在灯条端点；若落到装甲板四角外侧或错位，说明 `sort_keypoints` 顺序假设在该模型上不成立，需重新校准。
4. 学生版 `./build/main` 编译通过但运行结果不正确（因为有 `Task01–05` 待填），符合教学预期。

第 3 条已在 Python 侧用 148 帧验证通过（见 §2.4），C++ 侧只需复现同样结论。

## 7. 明确不做

- 不改动 `lecture4/class/`、`lecture4/answer/`、`lecture4/homework/`。
- 不改动 `Lecture4 Hello Armor&PnP.pptx`、`Lecture4_HelloArmor_装甲板位姿解算.pptx`、`Lecture4_HelloArmor_教案.docx`，以及 `output/` 下的逐字讲稿。
- 不训练、不导出新模型，直接使用现成的 `yolov8c.xml`。
- 不引入 ROI、颜色估计、分类器、yaml 配置层。

## 8. 剩余风险

| 风险 | 影响 | 应对 |
|---|---|---|
| 本机（Windows）无 OpenVINO / cv2 / WSL，无法编译验证 C++ | C++ 代码的编译错误无法提前发现 | Python 侧已验证算法与模型（§2）；C++ 侧按 §6 在开发机验收。验证用的临时 venv 位于 `%TEMP%/yolo_probe_venv`，用完删除 |
| `main.cpp` 首帧可能读不到装甲板 | 首帧无显示 | 与 `class/` 版行为一致，`if (!armors.empty())` 已兜住 |
| 视频中 3/151 帧因运动模糊漏检 | 画面短暂无框 | 属正常现象，可作课堂讨论点 |
| 类名 `Detector` 与文件名 `yolo` 不完全呼应 | 轻微认知摩擦 | 已在 §4.2 说明；如需改为 `YOLO` 类名，改动仅 2 处 |
