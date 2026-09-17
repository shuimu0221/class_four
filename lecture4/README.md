# Lecture 4 装甲板位姿解算

本工程服务于第四讲的课堂练习。课程目标是把上一讲 Detector 输出的 4 个二维灯条端点，转换为装甲板相对相机的三维位姿，并用重投影确认结果可信。

## 课堂中使用的目录

- `class/`：学生填写版。只修改 `src/main.cpp` 和 `tasks/pose_solver.cpp` 中标出的 Task 区域。
- `answer/`：教师参考答案。使用和学生版相同的检测器、视频和测试接口，便于逐文件比对。
- `class/video.avi`：课堂回放视频，分辨率为 1280 x 1024。
- `class/tiny_resnet.onnx`：数字分类模型。检测器会在程序启动时加载一次。

`homework/` 是后续能量机关识别的独立工程，依赖 OpenVINO 与工业相机 SDK，不属于本讲练习。`reprojection/` 是手眼标定和 IMU 重投影的演示脚本，也不属于本讲必做内容。

## 构建与运行

在 Ubuntu 终端进入 `lecture4/class` 后运行：

```bash
cmake -S . -B build
cmake --build build --target lecture4_class
./build/lecture4_class
```

构建脚本会把 `video.avi` 和 `tiny_resnet.onnx` 自动复制到 `build/`。教师可运行下列命令查看参考答案：

```bash
cmake --build build --target lecture4_answer
./build/lecture4_answer
```

## 任务顺序

1. **Task 01**：在 `tasks/pose_solver.cpp` 中填写小装甲板的四个 3D 点。点序为左上、右上、右下、左下，单位为米。
2. **Task 02**：在 `src/main.cpp` 中按相同顺序构造四个 2D 像素点。
3. **Task 03**：调用 `cv::solvePnP`，得到 `rvec` 和 `tvec`。
4. **Task 04**：用 `cv::projectPoints` 把 3D 点投回图像，计算重投影 RMS 误差。红色点是检测结果，绿色点是重投影结果。
5. **Task 05**：从 `tvec` 计算距离、水平瞄准角和俯仰瞄准角。相机坐标系采用 x 向右、y 向下、z 向前的约定。

课上的成功标准是：绿色重投影点与红色观测点基本重合，画面能够显示 `tvec`、距离、瞄准 yaw/pitch 和重投影 RMS。若点序或相机标定参数不匹配，重投影结果会立刻偏离。

## 自动检查

学生完成任务后运行：

```bash
cmake --build build --target lecture4_pose_test
ctest --test-dir build -R lecture4_pose_test --output-on-failure
```

该检查使用独立的合成 3D-2D 对应点验证以下内容：小装甲板物理尺寸和点序、平移恢复、重投影误差、瞄准角公式，以及少于四个点时是否拒绝求解。

教师课前可单独验证参考答案：

```bash
cmake --build build --target lecture4_answer_test
ctest --test-dir build -R lecture4_answer_test --output-on-failure
```

## 进阶任务

用 `cv::Rodrigues` 将 `rvec` 转为旋转矩阵，并在明确旋转顺序和坐标系约定的前提下提取装甲板的欧拉角。这个结果描述的是装甲板自身的朝向，和本讲 Task 05 的“相机指向目标的 yaw/pitch”不同。
