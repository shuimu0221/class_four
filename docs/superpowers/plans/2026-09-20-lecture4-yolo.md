# Lecture4「Hello Armor」YOLO 版教学程序 — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `class_four/lecture4/yolo/` 建出一份基于 YOLO 的 PnP 教学程序，复用 lecture2 作业里学生已经写好的检测器，让学生把 `object_points` 与 `img_points` 的对应关系写对。

**Architecture:** 逐字复制 `sp_vision_tutorial_27/lecture2/homework/` 的 `tasks/`（YOLO + Armor）与 `tools/`，保证与学生机器上的代码一致；新增一套 `io/`（`CameraBase` + `VideoCamera` + 按 config 选路的门面）把取帧接口钉死；`src/main.cpp` 留 Task01–05 五个 PnP 填空，`answer/main.cpp` 给参考实现。

**Tech Stack:** C++17、OpenCV、fmt、Eigen3、yaml-cpp、spdlog、OpenVINO 2024.6.0、CMake 3.16+。验证侧用 Python（opencv-python + openvino）。

**Spec:** `docs/superpowers/specs/2026-09-20-lecture4-yolo-design.md`

## Global Constraints

- **编译验证在本机做不了。** 本机（Windows）**没有任何 C++ 工具链**：已确认 `g++`、`gcc`、`clang++`、`cl`、`cmake`、`make`、`ninja` 全部不存在，也没有 OpenCV/OpenVINO 开发包与 WSL。所以**不要声称 C++ 编译或运行通过**。所有 C++ 编译/运行验收集中在 Task 8，由用户在 Linux 开发机上执行。本机能做的验证只有：文件结构、逐字复制保真度（`diff`）、YAML 可解析、以及 Python 侧算法验证。
- **路径常量**（下文用这些名字指代）：
  - `TARGET` = `C:/Users/ziang.xu/Documents/sp/class_four/lecture4/yolo`
  - `LECTURE2` = `C:/Users/ziang.xu/Documents/sp/sp_vision_tutorial_27/lecture2/homework`
  - `MODEL_SRC` = `C:/Users/ziang.xu/Documents/sp/sp_vision_26/assets`
  - `VIDEO_SRC` = `C:/Users/ziang.xu/Documents/sp/class_four/lecture4/class/video.avi`
  - `VENV` = `$TEMP/yolo_probe_venv`（已存在，内含 `cv2 5.0.0` + `openvino 2026.4.0`）
- **`tasks/` 与 `tools/` 下的 `.hpp`/`.cpp` 必须与 `LECTURE2` 逐字一致**，包括 `tasks/armor.hpp:97` 那条**错误的**关键点顺序注释 —— 原样保留，不要"顺手修正"。CMakeLists 除外（见 Task 1/2/3 的说明）。
- **派生出的硬事实**：`Armor::points` 顺序是 **左上、右上、右下、左下**（`[TL,TR,BR,BL]`），与注释写的相反。`object_points` 必须按这个顺序排。
- **不改 `sp_vision_tutorial_27/` 的任何文件**，也不改 `lecture4/class/`、`lecture4/answer/`、`lecture4/homework/`。
- OpenVINO 路径 `set(OpenVINO_DIR "...")` **只在顶层 `CMakeLists.txt` 出现一次**，不要再散落到子目录。
- 提交信息结尾必须带 `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`。

---

## File Structure

```
class_four/lecture4/yolo/
├── CMakeLists.txt              新增
├── .gitignore                  新增
├── README.md                   新增
├── configs/yolo.yaml           新增
├── docs/keypoint_order.md      新增
├── docs/verify_keypoint_order.py  新增
├── assets/yolov5.xml/.bin      复制自 MODEL_SRC
├── assets/video.avi            复制自 VIDEO_SRC
├── tools/                      复制自 LECTURE2（+1 个补充文件）
├── tasks/                      复制自 LECTURE2（逐字，CMakeLists 微调）
├── io/camera.hpp               新增
├── io/camera.cpp               新增
├── io/video_camera.hpp         新增
├── io/video_camera.cpp         新增
├── io/CMakeLists.txt           重写
├── io/hikrobot/                复制自 LECTURE2
├── src/main.cpp                新增（学生填空）
└── answer/main.cpp             新增（参考实现）
```

**与 `LECTURE2` 的有意差异**（都必须照做，并在 README 里说明）：

1. `tools/thread_safe_queue.hpp` **新增** —— `io/hikrobot/hikrobot.hpp` 里 `#include "tools/thread_safe_queue.hpp"`，但 `LECTURE2/tools/` 里**没有这个文件**（所以 `hikrobot.cpp` 在 lecture2 里从未被编译过）。从 `sp_vision_26/tools/thread_safe_queue.hpp` 复制过来补上。
2. `tasks/CMakeLists.txt`、`io/CMakeLists.txt` 里原有的 `set(OpenVINO_DIR ...)` 硬编码**删除**，统一由顶层提供。
3. 顶层 `CMakeLists.txt` **必须 `find_package(spdlog REQUIRED)` 并链 `spdlog::spdlog`** —— `LECTURE2/CMakeLists.txt` 里这一行是**注释掉的**，而 `tools/logger.cpp` 真的用了 spdlog 的编译期 sink，所以 lecture2 作业按本仓库原样是**编译不过**的。
4. `io/CMakeLists.txt` 不再无条件链 `MvCameraControl`，改为 `WITH_HIKROBOT` 开关（默认 OFF）。

---

## Task 1: 项目骨架、config、素材，与逐字复制

**Files:**
- Create: `TARGET/configs/yolo.yaml`
- Create: `TARGET/assets/yolov5.xml`, `TARGET/assets/yolov5.bin`, `TARGET/assets/video.avi`
- Create: `TARGET/tools/{img_tools.hpp,img_tools.cpp,logger.hpp,logger.cpp,yaml.hpp,thread_safe_queue.hpp,CMakeLists.txt}`
- Create: `TARGET/tasks/{armor.hpp,armor.cpp,yolo.hpp,yolo.cpp,CMakeLists.txt}`
- Create: `TARGET/tasks/yolos/{yolov5.hpp,yolov5.cpp}`
- Create: `TARGET/io/hikrobot/**`（8 个头文件 + 2 个 .so + hikrobot.{hpp,cpp}）

**Interfaces:**
- Consumes: 无（第一个任务）
- Produces: 后续任务依赖的文件路径：`configs/yolo.yaml` 的键 `source` / `video.path` / `video.loop` / `camera.{exposure_ms,gain,vid_pid}`；`tasks/` 提供 `auto_aim::YOLO(const std::string&, bool)` 与 `auto_aim::Armor`；`tools/img_tools.hpp` 提供 `tools::draw_points(cv::Mat&, const std::vector<cv::Point2f>&, const cv::Scalar&, int)` 与 `tools::draw_text(cv::Mat&, const std::string&, const cv::Point&, const cv::Scalar&, double, int)`

- [ ] **Step 1: 建目录**

```bash
TARGET=/c/Users/ziang.xu/Documents/sp/class_four/lecture4/yolo
mkdir -p "$TARGET"/{configs,docs,assets,tools,tasks/yolos,io,src,answer}
```

- [ ] **Step 2: 复制 tasks/（逐字）与 io/hikrobot/（逐字）**

```bash
LECTURE2=/c/Users/ziang.xu/Documents/sp/sp_vision_tutorial_27/lecture2/homework
TARGET=/c/Users/ziang.xu/Documents/sp/class_four/lecture4/yolo
cp "$LECTURE2"/tasks/armor.hpp "$LECTURE2"/tasks/armor.cpp \
   "$LECTURE2"/tasks/yolo.hpp  "$LECTURE2"/tasks/yolo.cpp   "$TARGET/tasks/"
cp "$LECTURE2"/tasks/yolos/yolov5.hpp "$LECTURE2"/tasks/yolos/yolov5.cpp "$TARGET/tasks/yolos/"
cp -r "$LECTURE2"/io/hikrobot "$TARGET/io/"
```

- [ ] **Step 3: 复制 tools/（逐字）并补上缺失的 thread_safe_queue.hpp**

```bash
LECTURE2=/c/Users/ziang.xu/Documents/sp/sp_vision_tutorial_27/lecture2/homework
TARGET=/c/Users/ziang.xu/Documents/sp/class_four/lecture4/yolo
cp "$LECTURE2"/tools/img_tools.hpp "$LECTURE2"/tools/img_tools.cpp \
   "$LECTURE2"/tools/logger.hpp    "$LECTURE2"/tools/logger.cpp \
   "$LECTURE2"/tools/yaml.hpp      "$LECTURE2"/tools/CMakeLists.txt "$TARGET/tools/"
# LECTURE2/tools 里没有 thread_safe_queue.hpp，但 io/hikrobot/hikrobot.hpp 需要它
cp /c/Users/ziang.xu/Documents/sp/sp_vision_26/tools/thread_safe_queue.hpp "$TARGET/tools/"
```

- [ ] **Step 4: 复制素材**

```bash
MODEL_SRC=/c/Users/ziang.xu/Documents/sp/sp_vision_26/assets
VIDEO_SRC=/c/Users/ziang.xu/Documents/sp/class_four/lecture4/class/video.avi
TARGET=/c/Users/ziang.xu/Documents/sp/class_four/lecture4/yolo
cp "$MODEL_SRC"/yolov5.xml "$MODEL_SRC"/yolov5.bin "$TARGET/assets/"
cp "$VIDEO_SRC" "$TARGET/assets/video.avi"
```

- [ ] **Step 5: 写 `TARGET/configs/yolo.yaml`**

前半段与 `LECTURE2/configs/yolo.yaml` 完全一致（原样保留），只追加 `source` 段：

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

- [ ] **Step 6: 写 `TARGET/tasks/CMakeLists.txt`（= LECTURE2 版本，删掉硬编码的 OpenVINO_DIR）**

```cmake
cmake_minimum_required(VERSION 3.16)

# OpenVINO_DIR 由顶层 CMakeLists.txt 统一提供

find_package(OpenVINO REQUIRED COMPONENTS Runtime)

add_library(auto_aim OBJECT 
    armor.cpp
    yolo.cpp
    yolos/yolov5.cpp
)

target_link_libraries(auto_aim io openvino::runtime )
```

- [ ] **Step 7: 验证逐字复制保真度（本机可执行）**

对 `.hpp`/`.cpp` 逐个 `diff`，期望**全部无输出**：

```bash
LECTURE2=/c/Users/ziang.xu/Documents/sp/sp_vision_tutorial_27/lecture2/homework
TARGET=/c/Users/ziang.xu/Documents/sp/class_four/lecture4/yolo
for f in tasks/armor.hpp tasks/armor.cpp tasks/yolo.hpp tasks/yolo.cpp \
         tasks/yolos/yolov5.hpp tasks/yolos/yolov5.cpp \
         tools/img_tools.hpp tools/img_tools.cpp tools/logger.hpp tools/logger.cpp \
         tools/yaml.hpp tools/CMakeLists.txt; do
  diff -q "$LECTURE2/$f" "$TARGET/$f" || echo "DIFFERS: $f"
done
echo "--- io/hikrobot 全量 ---"
diff -r "$LECTURE2/io/hikrobot" "$TARGET/io/hikrobot" && echo "hikrobot identical"
echo "--- tools 的清单差异（期望只多出 thread_safe_queue.hpp）---"
diff <(ls "$LECTURE2/tools") <(ls "$TARGET/tools")
```

Expected:

```
--- io/hikrobot 全量 ---
hikrobot identical
--- tools 的清单差异（期望只多出 thread_safe_queue.hpp）---
5a6
> thread_safe_queue.hpp
```

前面的 `for` 循环不应有任何 `DIFFERS:` 行。若出现，说明复制错了文件，修掉重来。

- [ ] **Step 8: 验证素材与 config（本机可执行）**

`yaml` 模块不在已有的验证 venv 里，先装上（venv 是临时的一次性环境）：

```bash
"$TEMP/yolo_probe_venv/Scripts/python.exe" -m pip install --quiet pyyaml
```

```bash
TARGET=/c/Users/ziang.xu/Documents/sp/class_four/lecture4/yolo
ls -l "$TARGET/assets/"
"$TEMP/yolo_probe_venv/Scripts/python.exe" - <<'PY'
import yaml
p = r"C:/Users/ziang.xu/Documents/sp/class_four/lecture4/yolo/configs/yolo.yaml"
c = yaml.safe_load(open(p, encoding="utf-8"))
need = ["yolo_name", "yolov5_model_path", "device", "min_confidence", "use_roi",
        "source", "video", "camera"]
missing = [k for k in need if k not in c]
assert not missing, f"missing keys: {missing}"
assert c["yolo_name"] == "yolov5"
assert c["source"] in ("video", "camera")
assert c["video"]["path"] == "assets/video.avi"
assert c["video"]["loop"] is True
for k in ("exposure_ms", "gain", "vid_pid"):
    assert k in c["camera"], f"camera.{k} missing"
print("yaml OK; source =", c["source"])
PY
```

Expected: 列出 `video.avi`（约 55 MB）、`yolov5.xml`（约 200 KB）、`yolov5.bin`（约 4.3 MB）；最后打印 `yaml OK; source = video`。这一步同时验证了 YAML 语法（缩进错了会直接抛异常）。

- [ ] **Step 9: 提交**

```bash
cd /c/Users/ziang.xu/Documents/sp/class_four
git add lecture4/yolo/configs lecture4/yolo/assets lecture4/yolo/tools lecture4/yolo/tasks lecture4/yolo/io/hikrobot
git commit -m "feat(lecture4/yolo): vendor lecture2 YOLO stack, config and assets" \
           -m "Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 2: `io/` 取帧层（video / camera 由 config 切换）

**Files:**
- Create: `TARGET/io/camera.hpp`
- Create: `TARGET/io/video_camera.hpp`, `TARGET/io/video_camera.cpp`
- Create: `TARGET/io/camera.cpp`
- Create: `TARGET/io/CMakeLists.txt`
- Create: `TARGET/.gitignore`

**Interfaces:**
- Consumes: `tools/yaml.hpp` 的 `tools::load(path)` 与 `tools::read<T>(node, key)`；`tools/logger.hpp` 的 `tools::logger()`；`configs/yolo.yaml` 的 `source` / `video.*`
- Produces: `io::CameraBase`（纯虚 `read` / `try_read_for` / `is_alive`）、`io::Camera(const std::string& config_path)` 门面、`io::VideoCamera(const std::string& config_path)`。Task 4/5 的 `main.cpp` 只依赖 `io::Camera`

- [ ] **Step 1: 写 `TARGET/io/camera.hpp`**

接口刻意与 `sp_vision_26/io/camera.hpp` 一致，这样 `LECTURE2/io/hikrobot/hikrobot.hpp`（`class HikRobot : public CameraBase`）能原样编译。

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

- [ ] **Step 2: 写 `TARGET/io/video_camera.hpp`**

```cpp
#ifndef IO__VIDEO_CAMERA_HPP
#define IO__VIDEO_CAMERA_HPP

#include <chrono>
#include <opencv2/opencv.hpp>
#include <string>

#include "camera.hpp"

namespace io
{
// 从视频文件取帧，当作相机用。目的是让每个学生都能跑出同样的画面和同样的位姿数值。
class VideoCamera : public CameraBase
{
public:
  explicit VideoCamera(const std::string & config_path);

  void read(cv::Mat & img, std::chrono::steady_clock::time_point & timestamp) override;

  bool try_read_for(
    cv::Mat & img, std::chrono::steady_clock::time_point & timestamp,
    std::chrono::milliseconds timeout) override;

  bool is_alive() const override;

private:
  cv::VideoCapture cap_;
  bool loop_;
};

}  // namespace io

#endif  // IO__VIDEO_CAMERA_HPP
```

- [ ] **Step 3: 写 `TARGET/io/video_camera.cpp`**

```cpp
#include "video_camera.hpp"

#include <stdexcept>

#include "tools/logger.hpp"
#include "tools/yaml.hpp"

namespace io
{
VideoCamera::VideoCamera(const std::string & config_path)
{
  auto yaml = tools::load(config_path);
  auto path = tools::read<std::string>(yaml["video"], "path");
  loop_ = yaml["video"]["loop"] ? yaml["video"]["loop"].as<bool>() : true;

  cap_.open(path);
  if (!cap_.isOpened()) {
    tools::logger()->error("[VideoCamera] Failed to open video: {}", path);
    throw std::runtime_error("Failed to open video: " + path);
  }

  tools::logger()->info(
    "[VideoCamera] {} ({}x{}, {} frames, loop={})", path,
    static_cast<int>(cap_.get(cv::CAP_PROP_FRAME_WIDTH)),
    static_cast<int>(cap_.get(cv::CAP_PROP_FRAME_HEIGHT)),
    static_cast<int>(cap_.get(cv::CAP_PROP_FRAME_COUNT)), loop_);
}

void VideoCamera::read(cv::Mat & img, std::chrono::steady_clock::time_point & timestamp)
{
  cap_ >> img;
  if (img.empty() && loop_) {
    cap_.set(cv::CAP_PROP_POS_FRAMES, 0);
    cap_ >> img;
  }
  timestamp = std::chrono::steady_clock::now();
}

bool VideoCamera::try_read_for(
  cv::Mat & img, std::chrono::steady_clock::time_point & timestamp, std::chrono::milliseconds)
{
  // 视频没有"等一帧"的语义，直接读，用返回值表达成功与否
  read(img, timestamp);
  return !img.empty();
}

bool VideoCamera::is_alive() const { return cap_.isOpened(); }

}  // namespace io
```

- [ ] **Step 4: 写 `TARGET/io/camera.cpp`**

```cpp
#include "camera.hpp"

#include <stdexcept>

#include "tools/yaml.hpp"
#include "video_camera.hpp"

#ifdef WITH_HIKROBOT
#include "hikrobot/hikrobot.hpp"
#endif

namespace io
{
Camera::Camera(const std::string & config_path)
{
  auto yaml = tools::load(config_path);
  auto source = tools::read<std::string>(yaml, "source");

  if (source == "video") {
    camera_ = std::make_unique<VideoCamera>(config_path);
    return;
  }

  if (source == "camera") {
#ifdef WITH_HIKROBOT
    camera_ = std::make_unique<HikRobot>(
      yaml["camera"]["exposure_ms"].as<double>(), yaml["camera"]["gain"].as<double>(),
      yaml["camera"]["vid_pid"].as<std::string>());
    return;
#else
    throw std::runtime_error(
      "source is 'camera' but this build has no HikRobot support. "
      "Reconfigure with -DWITH_HIKROBOT=ON after installing the MVS SDK, "
      "or set source: video in configs/yolo.yaml.");
#endif
  }

  throw std::runtime_error("Unknown source: " + source + " (expected 'video' or 'camera')");
}

void Camera::read(cv::Mat & img, std::chrono::steady_clock::time_point & timestamp)
{
  camera_->read(img, timestamp);
}

bool Camera::try_read_for(
  cv::Mat & img, std::chrono::steady_clock::time_point & timestamp,
  std::chrono::milliseconds timeout)
{
  return camera_->try_read_for(img, timestamp, timeout);
}

bool Camera::is_alive() const { return camera_->is_alive(); }

}  // namespace io
```

- [ ] **Step 5: 写 `TARGET/io/CMakeLists.txt`**

```cmake
cmake_minimum_required(VERSION 3.16)

find_package(yaml-cpp REQUIRED)

add_library(io STATIC
    camera.cpp
    video_camera.cpp
)

# 相机路径默认关闭：hikrobot.cpp 要链 MVS SDK 的 .so，多数学生机器上没有。
# 关掉它才能保证 video 路径人人能编。需要真相机时用 -DWITH_HIKROBOT=ON 打开。
option(WITH_HIKROBOT "Build the HikRobot camera source (requires the MVS SDK)" OFF)

if(WITH_HIKROBOT)
  target_sources(io PRIVATE hikrobot/hikrobot.cpp)
  target_compile_definitions(io PUBLIC WITH_HIKROBOT)
  target_include_directories(io PUBLIC hikrobot/include)

  if(CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64")
    target_link_directories(io PUBLIC hikrobot/lib/amd64)
  elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64")
    target_link_directories(io PUBLIC hikrobot/lib/arm64)
  else()
    message(FATAL_ERROR "Unsupported architecture: ${CMAKE_SYSTEM_PROCESSOR}!")
  endif()

  target_link_libraries(io PUBLIC MvCameraControl usb-1.0)
endif()

target_link_libraries(io PUBLIC yaml-cpp tools)
```

- [ ] **Step 6: 写 `TARGET/.gitignore`**

`logs/` 是 `tools/logger.cpp` 运行时写的；`imgs/` 是 `YOLOV5` 构造函数里 `std::filesystem::create_directory("imgs")` 建的。

```
build/
logs/
imgs/
```

- [ ] **Step 7: 验证接口自洽（本机可执行）**

证明 `camera.cpp` 读的 yaml 键、以及 `hikrobot.hpp` 依赖的头文件都真实存在：

```bash
TARGET=/c/Users/ziang.xu/Documents/sp/class_four/lecture4/yolo
echo "--- camera.cpp 用到的 config 键 ---"
grep -o 'yaml\["camera"\]\["[a-z_]*"\]' "$TARGET/io/camera.cpp" | sort -u
echo "--- hikrobot.hpp 的项目内 include 是否都能找到 ---"
grep -o '#include "[^"]*"' "$TARGET/io/hikrobot/hikrobot.hpp"
ls "$TARGET/tools/thread_safe_queue.hpp" "$TARGET/io/camera.hpp"
echo "--- 新增文件的项目内 include 是否都能找到 ---"
for f in io/camera.cpp io/video_camera.cpp io/video_camera.hpp io/camera.hpp; do
  grep -o '#include "[^"]*"' "$TARGET/$f" | sed 's/#include "//;s/"//' | while read -r inc; do
    [ -f "$TARGET/$inc" ] || [ -f "$TARGET/io/$inc" ] || echo "MISSING include in $f: $inc"
  done
done
echo "(以上不应出现 MISSING)"
```

Expected: 打印出 `camera` 段的 `exposure_ms` / `gain` / `vid_pid` 三个键；`hikrobot.hpp` 的两条项目内 include（`io/camera.hpp`、`tools/thread_safe_queue.hpp`）都能被 `ls` 找到；没有任何 `MISSING`。

- [ ] **Step 8: 提交**

```bash
cd /c/Users/ziang.xu/Documents/sp/class_four
git add lecture4/yolo/io/camera.hpp lecture4/yolo/io/camera.cpp \
        lecture4/yolo/io/video_camera.hpp lecture4/yolo/io/video_camera.cpp \
        lecture4/yolo/io/CMakeLists.txt lecture4/yolo/.gitignore
git commit -m "feat(lecture4/yolo): config-switched camera/video frame source" \
           -m "Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 3: 顶层构建文件

**Files:**
- Create: `TARGET/CMakeLists.txt`

**Interfaces:**
- Consumes: Task 1 的 `tools/`、`tasks/`；Task 2 的 `io/`
- Produces: 目标 `main`（`src/main.cpp`）与 `answer`（`answer/main.cpp`），供 Task 4/5/8 使用

- [ ] **Step 1: 写 `TARGET/CMakeLists.txt`**

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

add_executable(answer answer/main.cpp)
target_link_libraries(answer
    ${OpenCV_LIBS} fmt::fmt yaml-cpp spdlog::spdlog tools io auto_aim)
```

- [ ] **Step 2: 验证构建骨架与 spdlog（本机可执行）**

本步**只看骨架**，不检查 `src/main.cpp` / `answer/main.cpp` —— 那两个文件要到 Task 4/5 才创建，
它们的 include 自洽性由 Task 4 Step 2 与 Task 5 Step 3 各自负责。

```bash
TARGET=/c/Users/ziang.xu/Documents/sp/class_four/lecture4/yolo
echo "--- 子目录是否都存在 ---"
for d in tools io tasks; do [ -d "$TARGET/$d" ] && echo "ok: $d" || echo "MISSING dir: $d"; done
echo "--- 各子目录 CMakeLists ---"
ls "$TARGET"/{tools,io,tasks}/CMakeLists.txt
echo "--- spdlog 是否已显式启用（lecture2 里这行是注释掉的）---"
grep -n "spdlog" "$TARGET/CMakeLists.txt"
echo "--- OpenVINO_DIR 是否只在顶层出现一次 ---"
grep -rn "OpenVINO_DIR" "$TARGET/CMakeLists.txt" "$TARGET"/{tools,io,tasks}/CMakeLists.txt
echo "--- 两个可执行目标是否都已声明 ---"
grep -n "add_executable" "$TARGET/CMakeLists.txt"
```

Expected:
- 三个 `ok:`，无 `MISSING dir`
- 三个子 CMakeLists 都被列出
- `grep spdlog` 命中 **3** 行：`find_package(spdlog REQUIRED)` + `main`/`answer` 各一处 `spdlog::spdlog`
- `grep OpenVINO_DIR` **只命中顶层 1 行**（`set(OpenVINO_DIR ...)`）；子目录里不应再有
- `add_executable` 命中 2 行（`main`、`answer`）

- [ ] **Step 3: 提交**

```bash
cd /c/Users/ziang.xu/Documents/sp/class_four
git add lecture4/yolo/CMakeLists.txt
git commit -m "build(lecture4/yolo): top-level CMake with spdlog and unified OpenVINO_DIR" \
           -m "Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 4: 学生版 `src/main.cpp`（Task01–05 填空）

**Files:**
- Create: `TARGET/src/main.cpp`

**Interfaces:**
- Consumes: `io::Camera(config_path)`（Task 2）、`auto_aim::YOLO(config_path, debug)` 与 `auto_aim::Armor`（Task 1）、`tools::draw_points` / `tools::draw_text`（Task 1）
- Produces: 可执行目标 `main` 的入口。Task 5 的 `answer/main.cpp` 与它结构一一对应

注意 `tools::draw_text` 在 lecture2 里的签名是
`draw_text(cv::Mat&, const std::string&, const cv::Point&, const cv::Scalar&, double, int)` ——
**颜色在 font_scale 之前**，与 `class_four/lecture4/class/tools/img_tools.hpp` 那份顺序相反，别抄错。

- [ ] **Step 1: 写 `TARGET/src/main.cpp`**

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

        cv::imshow("press q to quit", img);

        if (cv::waitKey(20) == 'q')
            break;
    }

    cv::destroyAllWindows();
    return 0;
}
```

- [ ] **Step 2: 验证 include 与关键约束（本机可执行）**

```bash
TARGET=/c/Users/ziang.xu/Documents/sp/class_four/lecture4/yolo
echo "--- 项目内 include 是否都能找到 ---"
grep -o '#include "[^"]*"' "$TARGET/src/main.cpp" | sed 's/#include "//;s/"//' | while read -r inc; do
  [ -f "$TARGET/$inc" ] || echo "MISSING: $inc"
done
echo "--- Task01 必须仍是注释状态（学生要自己填）---"
grep -c "^// static const std::vector<cv::Point3f> object_points" "$TARGET/src/main.cpp"
echo "--- Task02 必须没有未注释的 img_points 定义 ---"
if grep -q "^ *std::vector<cv::Point2f> img_points" "$TARGET/src/main.cpp"; then
  echo "FAIL: img_points 被提前实现了"; else echo "ok: Task02 仍是空";
fi
echo "--- solvePnP 必须只出现在注释里 ---"
grep -n "solvePnP" "$TARGET/src/main.cpp"
echo "--- draw_text 参数顺序应为 (img, text, point, color, font_scale, thickness) ---"
grep -c 'cv::Scalar(0, 255, 255), 1.7, 3' "$TARGET/src/main.cpp"
```

Expected: 无 `MISSING`；`grep -c` 打印 `1`（Task01 仍是注释）；打印 `ok: Task02 仍是空`；`solvePnP` 只命中注释行（含 `// cv::solvePnP(, , , , rvec, tvec);`）；`draw_text` 的三处调用匹配 `cv::Scalar(0, 255, 255), 1.7, 3` 共 **3** 次。

- [ ] **Step 3: 提交**

```bash
cd /c/Users/ziang.xu/Documents/sp/class_four
git add lecture4/yolo/src/main.cpp
git commit -m "feat(lecture4/yolo): student main.cpp with PnP tasks 01-05" \
           -m "Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 5: 参考实现 `answer/main.cpp` 与 `tools/pnp_check.hpp`

**Files:**
- Create: `TARGET/tools/pnp_check.hpp`
- Create: `TARGET/answer/main.cpp`

**Interfaces:**
- Consumes: Task 4 的结构；`cv::solvePnP`、`cv::Rodrigues`、`cv::projectPoints`
- Produces: `tools::reprojection_error(const std::vector<cv::Point3f>&, const std::vector<cv::Point2f>&, const cv::Mat& rvec, const cv::Mat& tvec, const cv::Mat& camera_matrix, const cv::Mat& distort_coeffs) -> double`（返回平均重投影误差，单位像素）

- [ ] **Step 1: 写 `TARGET/tools/pnp_check.hpp`**

放在 `tools/` 但它**不是**从 lecture2 复制的文件，属于教学新增（Task 1 的 `diff` 校验只看 lecture2 那批文件，不受影响）。

```cpp
#ifndef TOOLS__PNP_CHECK_HPP
#define TOOLS__PNP_CHECK_HPP

#include <opencv2/opencv.hpp>
#include <vector>

namespace tools
{
// 把 object_points 用解得的位姿投影回图像，返回平均重投影误差（像素）。
// 用途：自查 object_points 与 img_points 的对应顺序有没有写反。
// 顺序正确时约 2~3 px；顺序写反（例如镜像）会暴涨到几十像素以上。
inline double reprojection_error(
  const std::vector<cv::Point3f> & object_points, const std::vector<cv::Point2f> & img_points,
  const cv::Mat & rvec, const cv::Mat & tvec, const cv::Mat & camera_matrix,
  const cv::Mat & distort_coeffs)
{
  std::vector<cv::Point2f> reprojected;
  cv::projectPoints(object_points, rvec, tvec, camera_matrix, distort_coeffs, reprojected);

  double sum = 0.0;
  for (std::size_t i = 0; i < img_points.size(); i++) {
    sum += cv::norm(reprojected[i] - img_points[i]);
  }
  return sum / static_cast<double>(img_points.size());
}

}  // namespace tools

#endif  // TOOLS__PNP_CHECK_HPP
```

- [ ] **Step 2: 写 `TARGET/answer/main.cpp`**

```cpp
#include <chrono>
#include <cmath>
#include <opencv2/opencv.hpp>

#include "fmt/core.h"
#include "io/camera.hpp"
#include "tasks/yolo.hpp"
#include "tools/img_tools.hpp"
#include "tools/pnp_check.hpp"

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
// 点序：左上、右上、右下、左下（自左上顺时针），与 Armor::points 一致。
// 注意 tasks/armor.hpp 里的注释写的是「左上、左下、右下、右上」，那是错的 ——
// 见 docs/keypoint_order.md。
static const std::vector<cv::Point3f> object_points{
    {-ARMOR_WIDTH / 2, -LIGHTBAR_LENGTH / 2, 0}, // 点 1 左上
    {ARMOR_WIDTH / 2, -LIGHTBAR_LENGTH / 2, 0},  // 点 2 右上
    {ARMOR_WIDTH / 2, LIGHTBAR_LENGTH / 2, 0},   // 点 3 右下
    {-ARMOR_WIDTH / 2, LIGHTBAR_LENGTH / 2, 0}   // 点 4 左下
};
// #########################################################

int main(int argc, char *argv[])
{
    auto_aim::YOLO detector("configs/yolo.yaml");
    io::Camera camera("configs/yolo.yaml");

    cv::Mat img;
    std::chrono::steady_clock::time_point timestamp;

    while (true)
    {
        camera.read(img, timestamp);
        if (img.empty())
            break;

        auto armors = detector.detect(img);

        if (!armors.empty())
        {
            auto armor = armors.front();
            tools::draw_points(img, armor.points);

            // #### Task 02 ############################################
            std::vector<cv::Point2f> img_points{
                armor.points.at(0),  // 左上
                armor.points.at(1),  // 右上
                armor.points.at(2),  // 右下
                armor.points.at(3)}; // 左下
            // #########################################################

            // #### Task 03 ############################################
            cv::Mat rvec, tvec;
            cv::solvePnP(object_points, img_points, camera_matrix, distort_coeffs, rvec, tvec);
            // #########################################################

            // #### Task 04 ############################################
            tools::draw_text(img, fmt::format("tvec:  x{: .2f} y{: .2f} z{: .2f}", tvec.at<double>(0), tvec.at<double>(1), tvec.at<double>(2)), cv::Point(10, 60), cv::Scalar(0, 255, 255), 1.7, 3);
            tools::draw_text(img, fmt::format("rvec:  x{: .2f} y{: .2f} z{: .2f}", rvec.at<double>(0), rvec.at<double>(1), rvec.at<double>(2)), cv::Point(10, 120), cv::Scalar(0, 255, 255), 1.7, 3);
            // #########################################################

            // #### Task 05 ############################################
            cv::Mat rmat;
            cv::Rodrigues(rvec, rmat);
            double yaw = std::atan2(rmat.at<double>(0, 2), rmat.at<double>(2, 2));
            double pitch = -std::asin(rmat.at<double>(1, 2));
            double roll = std::atan2(rmat.at<double>(1, 0), rmat.at<double>(1, 1));
            tools::draw_text(img, fmt::format("euler angles:  yaw{: .2f} pitch{: .2f} roll{: .2f}", yaw, pitch, roll), cv::Point(10, 180), cv::Scalar(0, 255, 255), 1.7, 3);
            // #########################################################

            // 额外的自查显示（不属学生任务）：顺序写对时约 2~3 px
            double reproj = tools::reprojection_error(
                object_points, img_points, rvec, tvec, camera_matrix, distort_coeffs);
            tools::draw_text(img, fmt::format("reproj err:  {:.2f} px", reproj), cv::Point(10, 240), cv::Scalar(0, 255, 255), 1.7, 3);
        }

        cv::imshow("press q to quit", img);

        if (cv::waitKey(20) == 'q')
            break;
    }

    cv::destroyAllWindows();
    return 0;
}
```

- [ ] **Step 3: 验证答案文件自洽（本机可执行）**

```bash
TARGET=/c/Users/ziang.xu/Documents/sp/class_four/lecture4/yolo
echo "--- answer 的项目内 include ---"
grep -o '#include "[^"]*"' "$TARGET/answer/main.cpp" | sed 's/#include "//;s/"//' | while read -r inc; do
  [ -f "$TARGET/$inc" ] || echo "MISSING: $inc"
done
echo "--- object_points 顺序：点1 与 点4 的 x 都应为负 (左上/左下) ---"
grep -n "ARMOR_WIDTH / 2" "$TARGET/answer/main.cpp"
echo "--- 两个 main.cpp 的 ObjectPoint 顺序必须一致（点2 的 x 为正）---"
grep -c "^{ARMOR_WIDTH / 2, -LIGHTBAR_LENGTH / 2, 0}" "$TARGET/answer/main.cpp"
echo "--- pnp_check.hpp 的符号被 answer 正确调用 ---"
grep -n "reprojection_error" "$TARGET/answer/main.cpp" "$TARGET/tools/pnp_check.hpp"
```

Expected: 无 `MISSING`；`ARMOR_WIDTH / 2` 命中 4 行，顺序为 `-、+、+、-`（左上、右上、右下、左下）；`grep -c` 打印 `1`；`reprojection_error` 在 `pnp_check.hpp` 里是定义（`inline double`），在 `answer/main.cpp` 里是调用。

- [ ] **Step 4: 提交**

```bash
cd /c/Users/ziang.xu/Documents/sp/class_four
git add lecture4/yolo/answer/main.cpp lecture4/yolo/tools/pnp_check.hpp
git commit -m "feat(lecture4/yolo): answer implementation plus reprojection-error self-check" \
           -m "Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 6: 关键点顺序验证脚本，并在本机跑通

**Files:**
- Create: `TARGET/docs/verify_keypoint_order.py`

**Interfaces:**
- Consumes: `VENV` 的 Python（`cv2`、`openvino`、`numpy`）；`TARGET/assets/yolov5.xml`、`TARGET/assets/video.avi`
- Produces: 退出码 0 表示顺序符合 `[左上,右上,右下,左下]`，非 0 表示不符合。这是**唯一**能排除"实际分发的 yolov5.xml 与我测的不是同一份"的手段，Task 7 的文档要引用它

- [ ] **Step 1: 写 `TARGET/docs/verify_keypoint_order.py`**

```python
#!/usr/bin/env python3
"""验证 YOLO 检测器给出的 Armor::points 顺序。

复刻 tasks/yolos/yolov5.cpp 里 YOLOV5::parse 的取点逻辑，在若干帧上统计
4 个关键点的几何排布，检查是否恒为 左上、右上、右下、左下。

用法（在 lecture4/yolo/ 下）：
    python docs/verify_keypoint_order.py [模型路径] [视频路径]
退出码 0 = 顺序符合预期；1 = 不符合或没检出目标。
"""
import sys
import collections

import cv2
import numpy as np
import openvino as ov

CONF_THR = 0.7
NMS_THR = 0.3
LIGHTBAR_LEN, ARMOR_WIDTH = 0.056, 0.135
EXPECTED_RATIO = ARMOR_WIDTH / LIGHTBAR_LEN  # 2.41


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def build_model(model_path):
    core = ov.Core()
    model = core.read_model(model_path)
    ppp = ov.preprocess.PrePostProcessor(model)
    inp = ppp.input()
    inp.tensor().set_element_type(ov.Type.u8).set_shape([1, 640, 640, 3]) \
       .set_layout("NHWC").set_color_format(ov.preprocess.ColorFormat.BGR)
    inp.model().set_layout("NCHW")
    inp.preprocess().convert_element_type(ov.Type.f32) \
       .convert_color(ov.preprocess.ColorFormat.RGB).scale(255.0)
    return core.compile_model(ppp.build(), "CPU").create_infer_request()


def parse_points(out_row, scale):
    """与 YOLOV5::parse 完全一致的取点顺序。"""
    return np.array([
        [out_row[0] / scale, out_row[1] / scale],  # armor.points[0]
        [out_row[6] / scale, out_row[7] / scale],  # armor.points[1]
        [out_row[4] / scale, out_row[5] / scale],  # armor.points[2]
        [out_row[2] / scale, out_row[3] / scale],  # armor.points[3]
    ], dtype=np.float64)


def main():
    model_path = sys.argv[1] if len(sys.argv) > 1 else "assets/yolov5.xml"
    video_path = sys.argv[2] if len(sys.argv) > 2 else "assets/video.avi"

    req = build_model(model_path)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"FAIL: cannot open video {video_path}")
        return 1

    labels_seen = collections.Counter()
    violations = collections.Counter()
    ratios = []
    total = detected = 0
    idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        total += 1
        if idx % 25:
            idx += 1
            continue
        idx += 1

        # 与 yolov5.cpp 一致：左上对齐 + 黑色填充的 resize
        scale = min(640.0 / frame.shape[0], 640.0 / frame.shape[1])
        h, w = int(frame.shape[0] * scale), int(frame.shape[1] * scale)
        inp = np.zeros((640, 640, 3), np.uint8)
        inp[0:h, 0:w] = cv2.resize(frame, (w, h))

        req.set_input_tensor(ov.Tensor(np.ascontiguousarray(inp)[None]))
        req.infer()
        out = np.array(req.get_output_tensor().data)[0]
        if out.shape[0] != 25200 and out.shape[1] == 25200:
            out = out.T

        best, best_score = -1, 0.0
        for r in range(out.shape[0]):
            score = sigmoid(float(out[r, 8]))
            if score > best_score:
                best, best_score = r, score
        if best_score < CONF_THR:
            continue

        detected += 1
        pts = parse_points(out[best], scale)

        # 标签：按每个点相对质心的方位命名。与"期望顺序"无关，因此能区分不同排布。
        centroid = pts.mean(axis=0)
        labels = []
        for p in pts:
            vert = "T" if p[1] < centroid[1] else "B"
            horiz = "L" if p[0] < centroid[0] else "R"
            labels.append(vert + horiz)
        labels_seen[tuple(labels)] += 1

        # 不依赖质心的独立几何校验：这四条必须同时成立
        p0, p1, p2, p3 = pts
        violations["p0.y < p3.y (左上在左下之上)"] += 0 if p0[1] < p3[1] else 1
        violations["p0.x < p1.x (左上在右上之左)"] += 0 if p0[0] < p1[0] else 1
        violations["p1.y < p2.y (右上在右下之上)"] += 0 if p1[1] < p2[1] else 1
        violations["p3.x < p2.x (左下在右下之左)"] += 0 if p3[0] < p2[0] else 1

        top = np.linalg.norm(p1 - p0)   # 上边 -> 装甲板宽
        left = np.linalg.norm(p3 - p0)  # 左边 -> 灯条长
        if left > 1:
            ratios.append(top / left)

    cap.release()

    print(f"frames: {total}, detected: {detected}")
    if not labels_seen:
        print("FAIL: 没有检出任何装甲板，无法判定顺序")
        return 1

    print("armor.points 的几何顺序统计（期望只有一行 TL,TR,BR,BL）：")
    for k, v in labels_seen.most_common():
        print(f"  {k}  x{v}")

    print("\n不依赖质心的四条不等式校验（期望全部为 0）：")
    bad = 0
    for k, v in violations.items():
        print(f"  {k}: {v}")
        bad += v

    if ratios:
        r = np.array(ratios)
        dev = abs(r.mean() - EXPECTED_RATIO) / EXPECTED_RATIO * 100
        print(f"\n上边/左边 像素比: mean={r.mean():.2f} (期望 {EXPECTED_RATIO:.2f}, 偏差 {dev:.1f}%)")

    expected = ("TL", "TR", "BR", "BL")
    actual = labels_seen.most_common(1)[0][0]
    ok = actual == expected and len(labels_seen) == 1 and bad == 0

    print()
    if ok:
        print(f"PASS: 顺序恒为 左上、右上、右下、左下 {expected}")
        return 0
    print(f"FAIL: 期望恒为 {expected}，实际最常见为 {actual}，不等式违例 {bad} 次")
    print("      若顺序不符，说明实际分发的模型与设计验证用的不是同一份，")
    print("      需要据此重算 object_points 的点序。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: 在 `TARGET` 下用 venv 跑它（本机可执行）**

```bash
cd /c/Users/ziang.xu/Documents/sp/class_four/lecture4/yolo
"$TEMP/yolo_probe_venv/Scripts/python.exe" docs/verify_keypoint_order.py
echo "exit=$?"
```

Expected（这是本计划里**最强的一条本机验证**，必须亲自跑出来。以下输出是用同一份模型与视频实测得到的真实结果）：

```
frames: 752, detected: 31
armor.points 的几何顺序统计（期望只有一行 TL,TR,BR,BL）：
  ('TL', 'TR', 'BR', 'BL')  x31

不依赖质心的四条不等式校验（期望全部为 0）：
  p0.y < p3.y (左上在左下之上): 0
  p0.x < p1.x (左上在右上之左): 0
  p1.y < p2.y (右上在右下之上): 0
  p3.x < p2.x (左下在右下之左): 0

上边/左边 像素比: mean=2.49 (期望 2.41, 偏差 3.2%)

PASS: 顺序恒为 左上、右上、右下、左下 ('TL', 'TR', 'BR', 'BL')
exit=0
```

注：`detected` 的**具体数字**会随抽样步长与模型版本小幅浮动（31 上下），
**只要顺序统计只有一行且不等式违例全为 0 就算通过**。
另外在 Windows 终端上中文可能显示成乱码（控制台代码页问题），看数字和 `exit=0` 即可，
在 Linux 开发机上输出正常。

若打印 `FAIL`，**停下来**：说明 `assets/yolov5.xml` 与设计假定不符，必须回到 spec §3.2 重新推导 `object_points`，而不是继续往下做。

- [ ] **Step 3: 提交**

```bash
cd /c/Users/ziang.xu/Documents/sp/class_four
git add lecture4/yolo/docs/verify_keypoint_order.py
git commit -m "test(lecture4/yolo): keypoint-order verification script" \
           -m "Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 7: 文档 —— `README.md` 与 `docs/keypoint_order.md`

**Files:**
- Create: `TARGET/docs/keypoint_order.md`
- Create: `TARGET/README.md`

**Interfaces:**
- Consumes: Task 6 脚本的输出（引用它）、spec §3.2 的证据链
- Produces: 学生与老师看得懂的操作说明与那个坑的完整解释

- [ ] **Step 1: 写 `TARGET/docs/keypoint_order.md`**

````markdown
# Armor::points 的真实顺序 —— 一个会坑死人的注释

## 结论

`auto_aim::Armor::points` 的顺序是 **左上、右上、右下、左下**（自左上顺时针），
即 `[TL, TR, BR, BL]`。

## 但是注释是反的

`tasks/armor.hpp` 里写着：

```cpp
std::vector<cv::Point2f> points;  // 关键点的图像坐标，顺序为左上、左下、右下、右上
```

**这条注释是错的。** 实际顺序是左上、右上、右下、左下。注释保留原样，是为了和
lecture2 作业发到同学手上的那份代码保持一致 —— 请不要"顺手改掉"，它是本讲的一个教学点。

## 怎么证明

用 `docs/verify_keypoint_order.py`（复刻 `tasks/yolos/yolov5.cpp` 的取点逻辑）在
`assets/video.avi` 上抽帧统计：

1. **把 4 个点按顺序编号画到图上**，肉眼可见 `0:左上 1:右上 2:右下 3:左下`。
2. **几何一致性**：19/19 帧同时满足
   `p0.y < p3.y`、`p0.x < p1.x`、`p1.y < p2.y`、`p3.x < p2.x`，零违例。
3. **尺寸比**：图像上"上边 / 左边"的像素长度比均值约 **2.5**，而 `object_points` 蕴含
   `ARMOR_WIDTH / LIGHTBAR_LENGTH = 0.135 / 0.056 = 2.41`，偏差约 3%。
   这说明四边形上边对应装甲板宽度、左边对应灯条长度 —— 尺寸对应关系成立。

## 为什么会错

`tasks/yolos/yolov5.cpp` 里是这样取点的：

```cpp
armor_key_points.push_back(cv::Point2f(output.at<float>(r, 0) / scale, output.at<float>(r, 1) / scale));
armor_key_points.push_back(cv::Point2f(output.at<float>(r, 6) / scale, output.at<float>(r, 7) / scale));
armor_key_points.push_back(cv::Point2f(output.at<float>(r, 4) / scale, output.at<float>(r, 5) / scale));
armor_key_points.push_back(cv::Point2f(output.at<float>(r, 2) / scale, output.at<float>(r, 3) / scale));
```

也就是对模型的原始 4 个关键点做了 `[0, 3, 2, 1]` 的置换 —— 一个 `swap(1, 3)`。

问题在于：**yolov5 这个模型的原生输出顺序已经是「左上、左下、右下、右上」**，
这个 swap 恰好把它拧成了「左上、右上、右下、左下」。

同样的 `swap(1, 3)` 在队内参考实现 `sp_vision_26/tasks/auto_aim/yolos/yolov8c.cpp` 里是**对的** ——
因为 **yolov8c 的原生顺序和 yolov5 正好相反**。两处代码长得一样、结论相反，很容易踩。
（`yolov5.cpp` 这段极可能是从 `yolov8c` 抄过来时没有改。）

## 为什么代码是对的、只有注释错

`tasks/armor.cpp` 的**传统**构造函数（由两根灯条构造）给出：

```
ratio = 装甲板宽 / 灯条长 ≈ 0.135 / 0.056 ≈ 2.41
```

而 **YOLO** 构造函数算的是 `ratio = max_length / max_width`。
只有在点序为 `[TL, TR, BR, BL]` 时，`max_length` 才是装甲板宽、`max_width` 才是灯条长，
结果才等于 2.41；若按注释那个顺序，会得到 0.41。

**所以代码行为与 `[TL,TR,BR,BL]` 自洽，只有注释（以及 `left_width` / `top_length`
这组变量名）是陈旧的。**

## 对你的影响

`object_points` 必须按 **左上、右上、右下、左下** 排：

```cpp
static const std::vector<cv::Point3f> object_points{
    {-ARMOR_WIDTH / 2, -LIGHTBAR_LENGTH / 2, 0},  // 点1 左上
    { ARMOR_WIDTH / 2, -LIGHTBAR_LENGTH / 2, 0},  // 点2 右上
    { ARMOR_WIDTH / 2,  LIGHTBAR_LENGTH / 2, 0},  // 点3 右下
    {-ARMOR_WIDTH / 2,  LIGHTBAR_LENGTH / 2, 0}   // 点4 左下
};
```

物体系：`+x` 向右、`+y` 向下，四点共面 `z = 0`。

## 怎么自查

如果 `object_points` 和 `img_points` 的顺序没对上，解出来的位姿会**有数、但完全不对**，
而且看着不像报错，极难发现。用**重投影误差**一眼就能看出来：

把 `object_points` 用解得的位姿投影回图像，和检测到的 `img_points` 比距离。
顺序正确时约 **2~3 px**；顺序写反（比如镜像）会暴涨到几十像素以上。

参考实现在教室里直接把这个误差画在画面上（`answer/main.cpp` 的 `reproj err` 一行），
工具函数在 `tools/pnp_check.hpp`。
````

- [ ] **Step 2: 写 `TARGET/README.md`**

````markdown
# Lecture 4 · 自瞄：Hello Armor && PnP（YOLO 版）

本讲在 lecture2 作业的 YOLO 装甲板检测器之上，实现对装甲板的**位姿解算**。

**你只需要填 `src/main.cpp` 里的 Task01–05**（object_points / img_points / solvePnP /
打印 tvec,rvec / Rodrigues 求欧拉角）。检测部分是现成的，不用你写。

## 目录

```
configs/yolo.yaml   检测与取帧的配置
assets/             模型与测试视频（线下分发，见下）
docs/               关键点顺序的说明与验证脚本
tools/ tasks/       来自 lecture2 作业的代码，未改动
io/                 取帧：按配置在 视频 / 相机 之间切换
src/main.cpp        学生填空（Task01–05）
answer/main.cpp     参考实现
```

## 构建

依赖：OpenCV、fmt、Eigen3、yaml-cpp、spdlog、OpenVINO 2024.6.0、CMake ≥ 3.16。

```bash
cd lecture4/yolo
cmake -B build
cmake --build build -j
```

## 运行

**在工作目录 `lecture4/yolo/` 下运行** —— 模型、视频、配置都按相对路径找：

```bash
./build/answer      # 参考实现
./build/main        # 学生版（Task01–05 未填，画面上全是 0.0）
```

按 `q` 退出。

## 取帧方式：视频 or 相机

`configs/yolo.yaml` 里的 `source` 决定：

```yaml
source: video     # 默认。从 video.path 读视频，loop: true 循环播放
source: camera    # 用 hikrobot 相机
```

- **`video`（默认）**：人人能跑、同一段视频、位姿数值可比，课上方便对答案。
- **`camera`**：需要装好 MVS SDK，并且**重新配置时打开开关**：

  ```bash
  cmake -B build -DWITH_HIKROBOT=ON
  cmake --build build -j
  ```

  没打开开关却在配置里写了 `source: camera`，程序会**报一条明确的错误**并提示你加开关，
  不会静默失败。相机的曝光/增益/USB VID:PID 也在 `configs/yolo.yaml` 的 `camera:` 段。

## 相机内参

`src/main.cpp` 顶部的 `camera_matrix` 与 `distort_coeffs` 是**给 `assets/video.avi`
那台相机标的**。如果你改用自带相机，这两组数需要自己标定，否则位姿数值没有意义。

## 一个必须知道的坑

`tasks/armor.hpp` 里关于 `Armor::points` 顺序的那条注释**是错的**。
真实顺序是**左上、右上、右下、左下**。`object_points` 必须按这个顺序排，
否则解出的位姿会错得很隐蔽。

完整解释、证明过程、以及怎么用重投影误差自查：**见 [`docs/keypoint_order.md`](docs/keypoint_order.md)**。

## assets/ 的来源

`assets/` 不在 lecture2 仓库里（那边 `.gitignore` 忽略了 `assets/`），模型与视频是线下分发的。
本目录为了自成一体把它们收进来了：

- `yolov5.xml` / `yolov5.bin` —— 与 lecture2 作业 `configs/yolo.yaml` 里 `yolov5_model_path`
  指向的模型同源（取自 `sp_vision_26/assets/`）
- `video.avi` —— 1280×1024、752 帧、30 fps，内容是手持数字「2」的装甲板

若仓库体积吃紧，可以把 `assets/` 也加进 `.gitignore` 改为线下分发 —— 代码不用改，
只要保证运行时能找到 `configs/yolo.yaml` 里写的相对路径即可。

## 关于 tasks/ 与 tools/

这两个目录是从 lecture2 作业**逐字复制**过来的（`tasks/armor.hpp` 里那条错误注释也原样保留），
目的是保证你手上的代码和课堂上讲的是同一份。`tools/thread_safe_queue.hpp` 是额外补的
（`io/hikrobot/hikrobot.hpp` 需要它，但 lecture2 的 `tools/` 里没有这个文件）。
````

- [ ] **Step 3: 验证文档里的路径与断言（本机可执行）**

```bash
TARGET=/c/Users/ziang.xu/Documents/sp/class_four/lecture4/yolo
echo "--- README 里引用的相对路径是否都存在 ---"
for p in docs/keypoint_order.md configs/yolo.yaml src/main.cpp answer/main.cpp \
         assets/video.avi assets/yolov5.xml; do
  [ -e "$TARGET/$p" ] && echo "ok: $p" || echo "MISSING: $p"
done
echo "--- TODO / TBD / FIXME 残留检查 ---"
grep -rn "TODO\|TBD\|FIXME" "$TARGET/README.md" "$TARGET/docs/keypoint_order.md" || echo "clean"
echo "--- README 引用的脚本命令是否可跑（--help 形式不存在，改用语法检查）---"
"$TEMP/yolo_probe_venv/Scripts/python.exe" -m py_compile "$TARGET/docs/verify_keypoint_order.py" && echo "py syntax ok"
echo "--- 文档里引用的仓库内文件是否存在 ---"
ls "$TARGET/tasks/armor.hpp" "$TARGET/tasks/yolos/yolov5.cpp" "$TARGET/tools/pnp_check.hpp" \
   "$TARGET/io/hikrobot/hikrobot.hpp" >/dev/null && echo "all referenced files exist"
```

Expected: 全部 `ok:`、`clean`、`py syntax ok`、`all referenced files exist`，没有 `MISSING`。

- [ ] **Step 4: 提交**

```bash
cd /c/Users/ziang.xu/Documents/sp/class_four
git add lecture4/yolo/README.md lecture4/yolo/docs/keypoint_order.md
git commit -m "docs(lecture4/yolo): README and the keypoint-order trap writeup" \
           -m "Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 8: 交付给开发机做编译与运行验收（本机做不了）

**本机没有任何 C++ 工具链**，所以这一步**必须由用户在 Linux 开发机上执行**。
执行者不要把这一步标记为"通过" —— 应当把下面的命令与预期输出交给用户，等真实结果回来。

**Files:**
- 无（纯验收）

**Interfaces:**
- Consumes: Task 1–7 的全部产物
- Produces: 对 spec §9 验收标准的实测结论

- [ ] **Step 1: 把这份清单交给用户，在 Linux 开发机上逐条跑**

```bash
# 0) 确认依赖存在（OpenVINO 路径按实际安装改，默认 2024.6.0）
cd class_four/lecture4/yolo
cmake -B build
cmake --build build -j
```

期望：配置与编译**无错误**，产出 `build/main` 与 `build/answer`。

需要预先确认的依赖：`OpenCV`、`fmt`、`Eigen3`、`yaml-cpp`、`spdlog`、`OpenVINO 2024.6.0`。
若 `find_package(spdlog REQUIRED)` 报找不到，装 `libspdlog-dev`；
若 OpenVINO 版本不同，改顶层 `CMakeLists.txt` 里的 `set(OpenVINO_DIR ...)` 一处即可。

- [ ] **Step 2: 跑参考实现，检查 spec §9.3–§9.5**

```bash
cd class_four/lecture4/yolo
./build/answer
```

逐条核对：

1. 装甲板被绿色四边形勾勒，**4 个点落在两根灯条的上/下端点**（不是装甲板外沿四角）
2. 画面上三行数字随视频变化：`tvec` / `rvec` / `euler angles`
3. **`reproj err` 一行中位应在 5 px 以内**（Python 侧实测中位 2.70 px、最大 12.15 px）
4. `tvec.z` 大致落在 **0.23–0.72 m**（中位约 0.35 m），`|tvec.x|`、`|tvec.y|` < 0.15 m
5. 欧拉角各分量 |值| ≲ 0.35 rad
6. 按 `q` 能正常退出

- [ ] **Step 3: 验证那个"坑"的自查确实有效（spec §9.5）**

把 `answer/main.cpp` 里 `object_points` 的**第 2 行与第 4 行对调**（即把点2/点4 互换，模拟镜像写错），
重新编译运行。期望：画面仍能跑，但 **`reproj err` 从 2~3 px 暴涨到几十像素以上**。
确认后**把改动还原**。

若误差没涨，说明自查工具没能捕捉顺序错误，需要回头检查 `tools/pnp_check.hpp`。

- [ ] **Step 4: 验证学生版符合预期（spec §9.6）**

```bash
./build/main
```

期望：**编译通过**，运行起来画面上 `tvec` / `rvec` / `euler angles` 三行全是 `0.00`
（因为 Task01–05 还没填），但装甲板框和 4 个关键点照常显示 —— 说明除 PnP 之外的部分都已经可用。

- [ ] **Step 5: 验证 `source: camera` 的两条路径（spec §9.7）**

先在**默认构建**（没有 `-DWITH_HIKROBOT`）下把 `configs/yolo.yaml` 的 `source` 改成 `camera`：

```bash
./build/answer
```

期望：**报一条明确错误**，提示需要 `-DWITH_HIKROBOT=ON` 并装 MVS SDK —— 不应崩溃或静默失败。

然后（有相机与 SDK 时）打开开关重编并运行：

```bash
cmake -B build -DWITH_HIKROBOT=ON && cmake --build build -j && ./build/answer
```

期望：能出图并正常解算。**若 `io/hikrobot/hikrobot.cpp` 编译不过**（它从未在 lecture2 里被编译过），
按 spec §11 的退路处理：把相机路径退化为"只留接口"，把编译报错贴出来再决定下一步 ——
**不要**为了让它编过去而删掉 `video` 路径的任何东西。

最后把 `source` 改回 `video`。

- [ ] **Step 6: 全部通过后提交验收记录**

```bash
cd /c/Users/ziang.xu/Documents/sp/class_four
git status --short
```

若 Step 3 的临时改动已还原干净，此时应无未提交改动。若有，说明改动没还干净，先还原。

---

## Self-Review

**1. Spec coverage**

| spec 章节 | 落在哪个 Task |
|---|---|
| §0 v1→v2 变更（模型改 yolov5、逐字复制、config 切换） | Task 1/2/3 |
| §2 前置：逐字复制 tasks/、tools/；不能依赖学生 Camera | Task 1（复制 + `diff` 校验）、Task 2（自带 io/） |
| §3.1 模型输出格式（左上对齐黑填充、BGR） | Task 6 脚本里复刻 |
| §3.2 关键点顺序 `[TL,TR,BR,BL]` | Task 5（`object_points`）、Task 6（脚本验证）、Task 7（文档） |
| §3.3 端到端数值（2.70 px、tz≈0.35 m） | Task 6 脚本 + Task 8 Step 2 核对 |
| §3.4 视频 1280×1024 752 帧 | Task 1 Step 4（复制）、Task 6（脚本跑它） |
| §4 目录结构 | Task 1/2/3/4/5/6/7 逐项覆盖 |
| §4 与 LECTURE2 的有意差异 1–4 | Task 1 Step 3/6、Task 2 Step 5、Task 3 Step 1 |
| §5.1–5.3 `io/camera.hpp`、`video_camera`、config | Task 2（Step 1–5）、Task 1 Step 5 |
| §5.4 `src/main.cpp` | Task 4 |
| §5.5 `answer/main.cpp` | Task 5 |
| §5.6 CMakeLists（含 WITH_HIKROBOT 默认关） | Task 2 Step 5、Task 3 Step 1 |
| §6 数据流 | Task 2/4/5 串起来 |
| §7 Task 对照表与 `object_points` | Task 4（空）、Task 5（答案） |
| §8 那个坑怎么讲（文档 + 自查工具 + 脚本 + 课堂讨论点） | Task 5 Step 1、Task 6、Task 7 |
| §9 验收标准 1–7 | Task 1 Step 7（§9.1）、Task 8（§9.2–9.7） |
| §10 明确不做 | Global Constraints + Task 8 Step 5 的"不要删 video 路径" |
| §11 剩余风险 | Task 6 Step 2、Task 7（assets 说明）、Task 8 Step 5 |

无遗漏。

**2. Placeholder scan**

无 `TBD` / `TODO` / "稍后实现" / "类似 Task N"。所有新增文件都给了完整内容；
复制类步骤给了确切源路径与 `diff` 校验命令。唯一的 `TODO` 字样出现在 Task 7 Step 3 的
**检查命令**里（用于确认文档本身没有残留 TODO），不是计划里的占位。

**3. Type consistency**

- `io::CameraBase::read(cv::Mat&, std::chrono::steady_clock::time_point&)` —— 在 Task 2 的
  `camera.hpp`、`video_camera.hpp`、`video_camera.cpp`、`camera.cpp` 四处签名一致。
- `io::HikRobot` 构造签名 `(double, double, const std::string&, int = 0)` 取自 Task 1 复制的
  `hikrobot.hpp`，Task 2 Step 4 的调用传 3 个参数，与该默认参数一致。
- `tools::draw_text` 参数序 `(Mat&, string, Point, Scalar, double, int)` —— Task 4 与 Task 5
  的所有调用都是 `(img, text, cv::Point(...), cv::Scalar(0,255,255), 1.7, 3)`，与 Task 1 复制的
  `tools/img_tools.hpp` 一致。
- `tools::reprojection_error` 的 6 个参数类型在 Task 5 的 `pnp_check.hpp` 定义与
  `answer/main.cpp` 调用处一致。
- `object_points` 类型 `std::vector<cv::Point3f>`，`img_points` 类型 `std::vector<cv::Point2f>`
  —— 与 `cv::solvePnP`、`cv::projectPoints` 的要求一致。
- YAML 键名 `source` / `video.path` / `video.loop` / `camera.exposure_ms` / `camera.gain` /
  `camera.vid_pid` 在 Task 1 Step 5（写入）、Task 1 Step 8（校验）、Task 2 Step 3/4（读取）
  三处拼写一致。
- 目标名 `main` / `answer` 在 Task 3（定义）与 Task 8（运行）一致。
