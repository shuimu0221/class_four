# Lecture4「Hello Armor」YOLO 版教学程序 — 设计文档（v2）

日期：2026-09-20
状态：待评审
位置：`class_four/lecture4/yolo/`（`class/`、`answer/`、`homework/` 均保留不动）

## 0. v1 → v2 变更摘要

v1 把 lecture4 当成一个**自成一套检测器**的独立程序（自己实现 `armor.hpp`、手写 yolov8c 的 OpenVINO 后处理）。拿到 lecture2 作业实际内容后，这个前提不成立 —— 学生**已经有**一套完整可用的 YOLO 装甲板检测器。v2 据此改写：

| | v1 | v2 | 原因 |
|---|---|---|---|
| 模型 | `yolov8c.xml`（7 类 + 4 关键点，灰度） | **`yolov5.xml`**（与 lecture2 作业一致） | 学生手上的就是这个 |
| 检测器 | 新写一个精简 `Detector` | **逐字复制 lecture2 作业的 `tasks/`** | 保证与学生环境一致，且"检测是白盒交给他们"的教学前提成立 |
| `armor.points` 顺序 | 假设 `[TL,TR,BR,BL]` | **实测确认 `[TL,TR,BR,BL]`**，且发现 lecture2 注释是错的 | 见 §3.2 |
| 工程结构 | 单 CMakeLists，OpenCV+fmt+OpenVINO | **完整工程**（io/tasks/tools 子目录，+Eigen/yaml-cpp） | 要复制 lecture2 的代码，还要加 video/camera 切换 |
| 取帧 | 固定读 `video.avi` | **config 切换 video / camera** | 用户决定 |
| 相机内参 | 未涉及 | 常量置于 `main.cpp` 顶部（沿用 `class/` 那份） | PnP 必需 |

`object_points` 的**内容**没有变（v1 的结论仍然成立），但 v2 现在有实测证据支撑，而不是假设。

## 1. 背景与目标

`class_four/lecture4/` 现有：

- `class/` — 学生起步代码，`tasks/detector.{hpp,cpp}` 是**手写的传统 CV 检测器**（阈值 → 轮廓 → 配对灯条 → `tiny_resnet` 分类），`src/main.cpp` 里 5 个填空任务**全部是 PnP**。
- `answer/main.cpp` — 上述任务的参考实现。
- `homework/` — 另一个无关主题（能量机关 buff）的作业。

**目标**：新增 `class_four/lecture4/yolo/` —— 一份基于 YOLO 的同一讲教学程序，与 `class/` 并列共存。

**教学主张**：`class/` 里那个手写 `Detector` 交给 `main.cpp` 的，本质上只有**装甲板的 4 个角点**。换成 YOLO 之后，公开接口不变、输出的还是 4 个角点 —— 于是 Task01/03/04/05 一字不动。这让学生看到「检测是可替换的前端，位姿解算是那个不变的核心」。

**学生动手范围**：只有 PnP。YOLO 检测器作为既定条件完整提供 —— 因为学生**在 lecture2 作业里已经自己写完了**（写的是 `io::Camera` 与 `main.cpp`，检测器本身是发给他们的）。所以 lecture4 不再教学检测，只教学位姿。

## 2. 前置：lecture2 作业给了学生什么

来源：`sp_vision_tutorial_27/lecture2/homework/`（同济 SuperPower 2027 赛季算法组招新仓库）。

| 部分 | 状态 | 内容 |
|---|---|---|
| `tasks/` | **已提供、完整、参与编译** | `auto_aim::YOLO(config_path, debug)` → `detect(img, frame_count)` → `std::list<Armor>`；`yolos/yolov5.cpp` 全套 OpenVINO 推理；`armor.{hpp,cpp}` 五个 `Armor` 构造函数 |
| `tools/` | **已提供、完整、参与编译** | `img_tools`（`draw_point/draw_points/draw_text`）、`logger`（spdlog）、`yaml`（`load/read`）、`thread_safe_queue` |
| `configs/yolo.yaml` | 已提供 | `yolov5.xml`、`score_threshold 0.7`、`min_confidence 0.8`、`use_roi: false` |
| `io/hikrobot/**`、`io/example.cpp` | **仅作参考，不参与编译** | 队内真实相机实现 + 裸 hikrobot API 用法示例 |
| `io/camera.{hpp,cpp}` | **空文件** | 学生自己写 —— 所以接口因人而异 |
| `main.cpp` | 骨架 | 注释提示四步：初始化相机与 yolo 类 / 读图 / 识别装甲板 / 显示 |
| 构建 | OpenCV、fmt、Eigen3、yaml-cpp、**OpenVINO 2024.6.0**（`/opt/intel/openvino_2024.6.0`） | 目标 `main`、`example`、`opencv` |
| `assets/` | **被 `.gitignore` 忽略** | 模型与视频线下分发，不在仓库里 |

**由此得到两条设计约束：**

1. **不能依赖学生的 `io::Camera`。** `io/camera.hpp` 是空的，每个学生的接口都不一样，而 `io/hikrobot/*` 又不进编译。所以 lecture4 必须自带一套 `io/`，把接口钉死。
2. **`tasks/` 要逐字复制，不能改写。** 目录里的 `armor.hpp`、`yolov5.cpp` 就是学生机器上的那一份，包括那条错误的注释（见 §3.2）。只有逐字复制，"你手上那份代码 + 一次 PnP 而已"的叙事才成立，那个坑也才讲得通。

## 3. 已验证的关键事实

全部通过临时 Python venv（`opencv-python 5.0.0` + `openvino 2026.4.0`）在 `sp_vision_26/assets/yolov5.xml` 与
`class_four/lecture4/class/video.avi` 上实测得到，非推测。

> 说明：lecture2 仓库里 `assets/` 被 gitignore，我无法取得它实际分发的那份 `yolov5.xml`，用的是 `sp_vision_26/assets/yolov5.xml`。两者几乎必然是同一个模型（输出 `[1,25200,22]` 与 `class_num_=13`、22 特征列完全吻合）。**若分发的是另一个模型，需用 §8 的自查脚本重跑一遍。**

### 3.1 模型与输出格式

- IR 输入：`float32 [1, 3, 640, 640]`（NCHW）
- IR 输出：`float32 [1, 25200, 22]` —— YOLOv5 锚框式，8400 网格 × 3 锚框 = 25200
- 22 个特征列：`0–7` 四个关键点（x,y 各一）、`8` objectness、`9–12` 四色独热、`13–21` 九类数字独热
- 注意：**输出里没有独立的 `cx,cy,w,h`**，`YOLOV5::parse` 是用 4 个关键点的外接矩形当 box 的（`yolov5.cpp:138-150`）
- 推理预处理与 `yolov8c` **不同**：`yolov5.cpp:84-86` 是**左上对齐 + 黑色填充**（不是居中、不是灰 114），且 `scale` 是单一 min-scale，回算时统一除以 `scale`
- 输入为 **BGR 三通道彩色**（`ppp` 里 `.set_color_format(BGR)`，没有灰度化）

### 3.2 `armor.points` 的真实顺序 —— lecture2 注释是错的

`lecture2/homework/tasks/armor.hpp:97` 写着：

```cpp
std::vector<cv::Point2f> points;  // 关键点的图像坐标，顺序为左上、左下、右下、右上
```

**实测不是这样，真实顺序是 左上、右上、右下、左下（`[TL, TR, BR, BL]`，自左上顺时针）。** 三条独立证据：

**(a) 肉眼** —— 把 4 个点按 `armor.points` 顺序编号画在原图上，得到 `0:左上 1:右上 2:右下 3:左下`。

**(b) 几何一致性** —— 19/19 帧、逐帧校验四条不等式全部成立：

| 校验项 | 违规 |
|---|---|
| `p0.y < p3.y`（左上在左下之上） | 0 |
| `p0.x < p1.x`（左上在右上之左） | 0 |
| `p1.y < p2.y`（右上在右下之上） | 0 |
| `p3.x < p2.x`（左下在右下之左） | 0 |

**(c) 尺寸比** —— 151 帧上量 `|p1−p0| / |p3−p0|`（上边 / 左边），均值 **2.48**；而 `object_points` 蕴含
`ARMOR_WIDTH / LIGHTBAR_LENGTH = 0.135 / 0.056 = 2.41`，**偏差 2.7%**（范围 1.95–3.28，由透视解释）。

**根因**：`yolov5.cpp:129-136` 按 `[raw0, raw3, raw2, raw1]` 取点 —— 也就是套用了 `swap(1,3)`。
但 yolov5 模型**原生**输出就已经是 `[左上, 左下, 右下, 右上]`（我单独画过原始 4 个关键点确认），
这个 swap **恰好把要的顺序拧反了**。旁证：`yolov8c` 的原生顺序**也是** `[左上, 左下, 右下, 右上]`，
其 `parse` 里的 `swap(1,3)` 是对的（把它变成 `[TL,TR,BR,BL]`）—— 所以 `yolov5.cpp` 里这段极可能是
从 `yolov8c` 抄过来时没改。

**代码本身是自洽的，只有注释和变量名陈旧**：传统构造函数（`armor.cpp:49`）给出
`ratio = 装甲板宽 / 灯条长 ≈ 2.41`；YOLO 构造函数（`armor.cpp:84`）的
`ratio = max_length / max_width` 只有在 `[TL,TR,BR,BL]` 下才等于 2.41（否则是 0.41）。
也就是说 `left_width` / `top_length` 这组变量名与实际语义是反的，但**行为正确**。

**对 lecture4 的影响**：`object_points` 必须按 `[TL,TR,BR,BL]` 排列。这**正好等于**
`class_four/lecture4/answer/main.cpp` 里那份，可以直接复用。但**学生若信了注释**，会写出镜像的
`object_points`，PnP 解出的位姿"有数但完全不对"，且极难自查 —— 这是讲 PnP 时最容易卡死人的坑，
必须讲。

### 3.3 端到端验证（检测 → PnP）

用 §3.2 的顺序、§7 的 `object_points`、以及 `class/src/main.cpp` 顶部那份相机内参/畸变，在 video.avi 上跑通：

- `tvec`：`x` ∈ [−0.11, 0.11] m，`y` ∈ [−0.08, 0.07] m，`z` ∈ [0.23, 0.72] m（中位 **0.35 m**）
- 欧拉角：yaw ±0.22 rad、pitch ±0.07 rad、roll ±0.33 rad
- **重投影误差：中位 2.70 px，最大 12.15 px**

数值合理（手持装甲板距相机约 35 cm，近似正对光轴）；**重投影误差中位不到 3 px，是关键点 ↔ 物点
对应关系正确的强证据** —— 若顺序错（例如镜像），该值会跳到几十到几百像素。所以重投影误差既验证了
本设计，也正好是给学生自查那个坑的现成工具（见 §8）。

### 3.4 视频

`class_four/lecture4/class/video.avi`：**752 帧、1280×1024、30 fps**（约 25 秒），内容是实验室里一个人
手持数字「2」的装甲板。yolov5 在其上检出置信度最高 **0.98**、均值约 0.97。**适合本讲**。

## 4. 目录结构

```
class_four/lecture4/yolo/
├── CMakeLists.txt              # OpenCV + fmt + Eigen3 + yaml-cpp + OpenVINO
├── README.md                   # 构建与运行、取帧切换、内参说明、指向 docs/
├── docs/
│   ├── keypoint_order.md       # 关键点顺序那个坑的完整证据链（§3.2）
│   └── verify_keypoint_order.py# 对着实际分发的模型重跑顺序验证
├── configs/
│   └── yolo.yaml               # lecture2 的原样 + lecture4 新增的 source 段
├── assets/                     # 线下分发（不入 git）：yolov5.xml/.bin + video.avi
├── tools/                      # ← 逐字复制 lecture2 作业
│   ├── img_tools.{hpp,cpp}
│   ├── logger.{hpp,cpp}
│   ├── yaml.hpp
│   ├── thread_safe_queue.hpp
│   └── CMakeLists.txt
├── io/
│   ├── camera.hpp              # 新增：CameraBase 抽象 + Camera 门面
│   ├── camera.cpp              # 新增：按 config 选 VideoCamera / HikRobot
│   ├── video_camera.hpp/.cpp   # 新增：VideoCamera : CameraBase
│   ├── hikrobot/               # ← 逐字复制 lecture2 作业（SDK 头 + .so）
│   ├── CMakeLists.txt          # 改：加入 camera.cpp / video_camera.cpp，hikrobot 受开关控制
├── tasks/                      # ← 逐字复制 lecture2 作业，一个字都不改
│   ├── armor.{hpp,cpp}         #    包括那条错误的注释，原样保留
│   ├── yolo.{hpp,cpp}
│   ├── yolos/yolov5.{hpp,cpp}
│   └── CMakeLists.txt
├── src/
│   └── main.cpp                # 学生填空：Task01–05
└── answer/
    └── main.cpp                # 参考实现（含可选的重投影误差自查）
```

「逐字复制」是硬约束：`tasks/` 与 `tools/` 必须与学生 lecture2 机器上的文件完全一致（可用 `diff -r` 核对），
否则"你手上那份代码"的说法不成立。

## 5. 组件设计

### 5.1 新增：`io/camera.hpp` —— 把接口钉死

学生那份是空的，所以这里必须自己定义，且要能被 `hikrobot.hpp`（`class HikRobot : public CameraBase`）直接复用：

```cpp
namespace io
{
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

class Camera                       // 门面，按 config 决定实现
{
public:
  Camera(const std::string & config_path);
  void read(cv::Mat & img, std::chrono::steady_clock::time_point & timestamp);
  bool try_read_for(...);
  bool is_alive() const;
private:
  std::unique_ptr<CameraBase> camera_;
};
}  // namespace io
```

接口与 `sp_vision_26/io/camera.hpp`（队内正式版）一致，这样 `hikrobot.{hpp,cpp}` 可以原样编译通过。

### 5.2 新增：`io/video_camera.{hpp,cpp}`

`VideoCamera : CameraBase`，用 `cv::VideoCapture` 读 `video.path`：

- `read()` 取下一帧；`loop: true` 时读到底自动 `set(CAP_PROP_POS_FRAMES, 0)` 重头，让课堂演示不会跑完就黑屏
- `timestamp` 用 `std::chrono::steady_clock::now()` 填（PnP 不需要它，但接口要求）
- `is_alive()` 返回 `cap_.isOpened()`
- 打不开时用 `tools::logger()->error` 报出路径，别静默失败

选它当默认是因为**人人能跑、同一段视频、位姿数值可比、课上能对答案**。

### 5.3 新增：`configs/yolo.yaml`

lecture2 的部分原样保留，只追加 `source` 段：

```yaml
# ---------- 以下原样来自 lecture2 作业 ----------
yolo_name: yolov5
yolov5_model_path: assets/yolov5.xml
device: CPU
min_confidence: 0.8
use_traditional: true
use_roi: false
threshold: 150
roi:
  x: 420
  y: 50
  width: 600
  height: 600

# ---------- lecture4 新增：取帧方式 ----------
source: video            # video | camera
video:
  path: assets/video.avi
  loop: true
camera:
  exposure_ms: 2.5
  gain: 16.9
  vid_pid: "2bdf:0001"
```

### 5.4 新增：`src/main.cpp` —— 学生填空

结构对齐 `class/lecture4/class/src/main.cpp`，保留 `// #### Task 0N ####` 注释块与提示写法。

顶部给定（非任务，与 `class/` 那份相同）：

```cpp
static const cv::Mat camera_matrix = (cv::Mat_<double>(3,3) <<
    1286.307063384126, 0,                645.34450819155256,
    0,                1288.1400736562441, 483.6163720308021,
    0,                0,                1);
static const cv::Mat distort_coeffs = (cv::Mat_<double>(1,5) <<
    -0.47562935060124745, 0.21831745829617311, 0.0004957613589406044,
    -0.00034617769548693592, 0);
static const double LIGHTBAR_LENGTH = 0.056;  // 灯条长度   单位：米
static const double ARMOR_WIDTH     = 0.135;  // 装甲板宽度 单位：米
```

主干（已给定）：

```cpp
int main()
{
    auto_aim::YOLO detector("configs/yolo.yaml");
    io::Camera camera("configs/yolo.yaml");

    cv::Mat img;
    std::chrono::steady_clock::time_point timestamp;
    while (true) {
        camera.read(img, timestamp);           // 视频或相机，由 config 决定
        if (img.empty()) break;

        auto armors = detector.detect(img);
        if (!armors.empty()) {
            auto armor = armors.front();
            tools::draw_points(img, armor.points);
            // Task 02 / 03 / 04 / 05 在这里
        }
        cv::imshow("press q to quit", img);
        if (cv::waitKey(20) == 'q') break;
    }
    cv::destroyAllWindows();
    return 0;
}
```

相机内参放在 `main.cpp` 顶部而不是 yaml：它们是**给定值**、不是学生任务，且 `class/` 版就是这么做的。
（若学生改用自带相机，这组内参不再适用，需要自己标定 —— 写进 README。）

### 5.5 新增：`answer/main.cpp`

Task01–05 的参考实现。与 `class_four/lecture4/answer/main.cpp` 相比只有 Task02 的取点来源不同。

### 5.6 `CMakeLists.txt`

顶层按 lecture2 作业的骨架（`add_subdirectory(io/tasks/tools)` + `add_executable`），依赖
`OpenCV`、`fmt`、`Eigen3`、`yaml-cpp`、`OpenVINO`。目标：

- `main` ← `src/main.cpp`（学生版）
- `answer` ← `answer/main.cpp`（`class/` 的 answer 不参与构建，这里编出来是为了能在真机上验收）

`io/CMakeLists.txt` 里 hikrobot 用开关控制，默认关：

```cmake
option(WITH_HIKROBOT "Build the HikRobot camera source (requires the MVS SDK)" OFF)
add_library(io STATIC camera.cpp video_camera.cpp)
if(WITH_HIKROBOT)
  target_sources(io PRIVATE hikrobot/hikrobot.cpp)
  target_include_directories(io PUBLIC hikrobot/include)
  # 按架构选 amd64/arm64 的 .so 目录
  target_link_libraries(io MvCameraControl usb-1.0)
endif()
target_link_libraries(io PUBLIC yaml-cpp tools)
```

理由：`hikrobot.cpp` 要链 MVS SDK 的 `.so`，多数学生机器上没有。默认关掉能保证**视频路径人人能编**；
`source: camera` 而开关没开时，`io::Camera` 抛一条明确的错误并提示加 `-DWITH_HIKROBOT=ON`，而不是静默失败。
这满足"两种取帧方式都支持、config 切换"，又不会让主路径被 SDK 拖死。

## 6. 数据流

```
configs/yolo.yaml ─┬─ source: video → io::VideoCamera ─┐
                   └─ source: camera → io::HikRobot ───┤
                                                       └→ io::Camera::read() → cv::Mat(BGR)
tasks/yolo.yaml ────→ auto_aim::YOLO
                                                          │
                       detect(img) ─→ [1,25200,22] ─ 阈值/NMS ─→ Armor{points=[TL,TR,BR,BL]}
                                                          │
              main.cpp: 取 armor.points 组成 img_points ──┤
                                                          ▼
                    cv::solvePnP(object_points, img_points, K, D) → rvec, tvec
                              ├─ Task04: 打印 tvec / rvec
                              └─ cv::Rodrigues(rvec) → rmat → 欧拉角(yaw/pitch/roll)
```

## 7. Task 对照表与 `object_points`

| Task | `class/` 版（传统 CV） | `yolo/` 版（YOLO） |
|---|---|---|
| 01 `object_points` | `±ARMOR_WIDTH/2, ±LIGHTBAR_LENGTH/2` | **完全相同，不变** |
| 02 `img_points` | `armor.left.top, armor.right.top, armor.right.bottom, armor.left.bottom` | `armor.points` 的 4 个元素 |
| 03 `solvePnP` | `cv::solvePnP(object_points, img_points, camera_matrix, distort_coeffs, rvec, tvec)` | **完全相同，不变** |
| 04 打印 `tvec` / `rvec` | `tvec.at<double>(0..2)` | **完全相同，不变** |
| 05 `Rodrigues` + 欧拉角 | 不变 | **完全相同，不变** |

Task01 的答案（顺序 `[左上, 右上, 右下, 左下]`，与 §3.2 实测的 `armor.points` 一一对应）：

```cpp
static const std::vector<cv::Point3f> object_points{
    {-ARMOR_WIDTH / 2, -LIGHTBAR_LENGTH / 2, 0},  // 点1 左上
    { ARMOR_WIDTH / 2, -LIGHTBAR_LENGTH / 2, 0},  // 点2 右上
    { ARMOR_WIDTH / 2,  LIGHTBAR_LENGTH / 2, 0},  // 点3 右下
    {-ARMOR_WIDTH / 2,  LIGHTBAR_LENGTH / 2, 0}   // 点4 左下
};
```

物体系：`+x` 向右、`+y` 向下、四点共面 `z=0`；`y` 方向跨度即灯条长度。
这与 `class_four/lecture4/answer/main.cpp` 完全一致 —— **无需改动**。

学生版 Task02 的提示要写清"顺序必须与 `object_points` 一一对应"，并**明确给出真实顺序**
（因为 lecture2 的注释是错的，见 §3.2）。

## 8. 那个坑怎么讲（重要）

用户决定：**不改 lecture2 的材料，只在 lecture4 的文档里说明。** 所以：

1. `tasks/armor.hpp` 里的错误注释**原样保留**（保持与学生机器一致）。
2. 写 `lecture4/yolo/docs/keypoint_order.md`，把 §3.2 的证据链讲清楚：
   注释说什么、实测是什么、怎么证明（编号画点 + 几何不等式 + 尺寸比 + 重投影误差）、根因在哪一行。
   `README.md` 指向它。
3. 提供一个**可选的自查工具**，让"顺序写错"从"极难发现"变成"一眼看见"：

   ```cpp
   // tools/pnp_check.hpp（新增，不属学生任务）
   // 把 object_points 用解得的位姿投影回图像，返回平均重投影误差（像素）
   double reprojection_error(
       const std::vector<cv::Point3f> & object_points,
       const std::vector<cv::Point2f> & img_points,
       const cv::Mat & rvec, const cv::Mat & tvec,
       const cv::Mat & camera_matrix, const cv::Mat & distort_coeffs);
   ```

   `answer/main.cpp` 把误差显示在画面上。实测正常值 **中位 2.70 px**；顺序写错时会暴涨到几十像素以上。
   建议把这个"自查"作为 Task05 之后的口头延伸，**不作为学生必做任务**（不扩大原定范围）。

4. 把 `yolov5.cpp` 里 `swap` 那一段作为课堂讨论点：同一段 `swap(1,3)` 在 `yolov8c` 里是对的、
   在 `yolov5` 里是错的 —— 因为它依赖的是"模型原生顺序"，而两个模型恰好相反。

5. 保留验证用的 Python 脚本（`docs/verify_keypoint_order.py`），学生或老师可用它对着**实际分发的模型**
   重跑一遍 —— 这是唯一能排除"分发的是另一个 yolov5.xml"的手段。

## 9. 验收标准

在 **Linux 开发机**（OpenCV、fmt、Eigen3、yaml-cpp、OpenVINO；MVS SDK 可选）上：

1. `diff -r` 核对 `lecture4/yolo/{tasks,tools}` 与 `sp_vision_tutorial_27/lecture2/homework/{tasks,tools}` 一致。
2. `cmake -B build && cmake --build build -j` 在 `lecture4/yolo/` 下无错通过，产出 `main` 与 `answer`。
3. `./build/answer`（`source: video`）窗口中：
   - 装甲板被绿色四边形勾勒，**4 个点落在两根灯条的上/下端点**（不是装甲板外沿四角）
   - `tvec` / `rvec` / 欧拉角三行随视频变化
4. 数值落在我实测过的区间内（§3.3）：
   - `tvec.z` ∈ [0.23, 0.72] m，中位约 **0.35 m**；`|tvec.x|`、`|tvec.y|` < 0.15 m
   - 欧拉角各分量 |值| ≲ 0.35 rad
   - **重投影误差中位 < 5 px**
5. 把 Task01 的 `object_points` 故意改成镜像顺序（点2/点4 对调），重投影误差应显著暴涨 ——
   确认这个自查确实能抓到那个坑。（这条同时验证了 §8 的教学有效性。）
6. `./build/main` 编译通过但运行显示 0.0（Task01–05 待填），符合教学预期。
7. `source: camera` + `-DWITH_HIKROBOT=ON` 且插着相机时能出图；开关未开时应报明确错误而非崩溃。

第 3、4 条已在 Python 侧用 31 帧验证通过（§3.3），C++ 侧只需复现同样结论。

## 10. 明确不做

- 不改动 `class_four/lecture4/class/`、`lecture4/answer/`、`lecture4/homework/`。
- **不改动 `sp_vision_tutorial_27/` 的任何文件** —— 包括 `armor.hpp` 那条错误注释（用户决定）。
- 不改动 PPT / 教案 / `output/` 下的逐字讲稿。
- 不训练、不导出新模型，直接用现成的 `yolov5.xml`。
- 不实现 `Solver` 类、不加 ROI/动态 ROI 逻辑、不做颜色二次估计（`use_traditional` 保持原样传参即可）。

## 11. 剩余风险与待确认

| 风险 | 影响 | 应对 |
|---|---|---|
| 本机（Windows）无 OpenVINO / cv2 / WSL | C++ 编译错误无法提前发现 | 算法层已用 Python venv 全链路验证（§3.3）；C++ 侧按 §9 在开发机验收。venv 位于 `%TEMP%/yolo_probe_venv`，收尾删除 |
| lecture2 实际分发的 `yolov5.xml` 可能与我测的不是同一份 | §3.2 的顺序结论可能不适用 | §8 保留自查脚本，对着实际模型重跑一遍即可判定 |
| `io/hikrobot/hikrobot.cpp` 从未在 lecture2 里被编译过 | 打开 `WITH_HIKROBOT` 后可能有编译问题 | 默认关；开启后按 §9.7 单独验收。若修不动，退化为"相机路径只留接口" |
| 相机内参是给 video.avi 那台相机标的 | 学生用自带相机时数值不对 | README 写明需自行标定 |
| `tasks/` 逐字复制会让仓库里存在两份 YOLO 代码 | 以后要同步 | 已知代价，用户已选；README 里注明来源与同步方式 |
| path：视频/模型靠相对路径 `assets/...` | 从别的目录运行会找不到 | 与 lecture2 一致（同样靠相对路径）；README 写明在 `lecture4/yolo/` 下运行 |
