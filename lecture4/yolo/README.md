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

依赖：OpenCV4（含 `dnn` 与 `calib3d`）、fmt、Eigen3、yaml-cpp、spdlog、OpenVINO 2024.6.0、CMake ≥ 3.16。

```bash
cd lecture4/yolo
cmake -B build
cmake --build build -j
```

若 OpenVINO 装在别处，改顶层 `CMakeLists.txt` 里的 `set(OpenVINO_DIR ...)` 一处即可。

**`answer` 目标默认不编译** —— `answer/main.cpp` 里就是填好的 Task 01~05，学生敲一次
`cmake --build` 就拿到答案，整段练习会作废。教师演示时打开它：

```bash
cmake -B build -DBUILD_ANSWER=ON && cmake --build build -j
```

## 运行

**在工作目录 `lecture4/yolo/` 下运行** —— configs、assets、logs 都按相对路径找：

```bash
./build/main        # 学生版（Task01–05 未填，画面上全是 0.0）
./build/answer      # 参考实现（需先 -DBUILD_ANSWER=ON 构建）
```

按 `q` 退出，按**空格**暂停（再按任意键继续，方便停在某一帧上对照讲解）。

参考版比学生版多一行 `reproj err`（重投影误差自查）：点序写对时是个位数像素，
写反会跳到几十上百。学生版没有这一行，想自查就在 `src/main.cpp` 里加
`#include "tools/pnp_check.hpp"`（header-only，不用改 CMake）。

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

完整解释、证明过程、以及怎么用重投影误差自查：**见 [docs/keypoint_order.md](docs/keypoint_order.md)**。

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
