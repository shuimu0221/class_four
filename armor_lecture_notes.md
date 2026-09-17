# 视觉组第四讲：Hello Armor — Lecture Notes (from keyframes f_0001–f_0033)

**Source:** `C:\Users\ziang.xu\Documents\class_four\frames\armor\f_0001.jpg` – `f_0033.jpg`
**Channel/presenter:** TJ-SuperPower战队 (Tongji University RoboMaster vision team), bilibili
**Slide file name shown on screen:** `Lectrue4 Hello Armor.pptx` (sic — typo for "Lecture4", visible in the WPS Presentation taskbar preview)

> **Scope note:** The 33 extracted scene-change keyframes for this lecture cover specifically the **armor-pose-estimation (`cv::solvePnP`) and coordinate-system portion** of "Hello Armor" — not light-bar/HSV segmentation or digit classification. The code already assumes a working `Detector`/`Armor`/`Lightbar` class hierarchy (`detector.detect(img)` returning `armors` with `.points`, `.left`, `.right` members), so armor detection itself (light-bar finding/pairing) is either treated as a given/black box in this segment or was covered in a part of the lecture that did not register as a scene-change keyframe. The narrative actually captured runs: PnP pose solving → rotation representations (Euler angles, rotation matrix, quaternion) → camera/gun coordinate-frame caveats → why pose matters for aiming at moving robots → hand-eye calibration → full sensor coordinate-transform chain (pixel → camera → body → IMU).

---

## 1. Title/intro slide: `cv::solvePnP (Perspective n Points)` (frame 1)

Tongji University logo + "SP" (SuperPower) team logo shown, as on all slides throughout.

Function signature shown verbatim:
```cpp
bool solvePnP( InputArray objectPoints, InputArray imagePoints,
               InputArray cameraMatrix, InputArray distCoeffs,
               OutputArray rvec, OutputArray tvec,
               bool useExtrinsicGuess = false, int flags = SOLVEPNP_ITERATIVE );
```

**Diagram:** Classic PnP schematic — a set of 3D object points (orange/gray dots labeled c1–c4 etc.) in a "World coordinate system" (axes drawn at right), projecting through an image plane (with principal point (u₀,v₀) and pixel u,v) into a "Camera coordinate system" (small camera icon, bottom-left, with its own axes). A red curved arrow labeled **R, t** goes from the world frame back to the camera, indicating solvePnP recovers the rotation R and translation t (i.e., rvec/tvec) that map world points into the camera frame.

This establishes solvePnP as: given known 3D geometry of an object (the armor plate) and its corresponding 2D image points, plus camera intrinsics/distortion, solve for the object's pose (rotation + translation) relative to the camera.

---

## 2. Hands-on exercise: "动手试一试" ("Try it hands-on") — recurring slide (frames 2, 4, 6, 9, 11, 15)

This slide is shown repeatedly (near-identical, just cursor/taskbar differences) as the anchor slide while the instructor alternates with the VS Code demo. Content is stable across all occurrences:

- Heading: **动手试一试**
- Body text:
  > 我们规定输入点集的顺序为以左上角灯条为1，顺时针依次为2、3、4。
  > 灯条的尺寸为宽0.135（m） 长0.056（m）
  
  (Translation: "We define the order of the input point set as: the top-left light bar is point 1, then clockwise 2, 3, 4. Light-bar/armor dimensions: width 0.135 m, length 0.056 m." — matches code constants `ARMOR_WIDTH = 0.135` and `LIGHTBAR_LENGTH = 0.056`.)
- Function signature reminder (shortened, no default args):
  ```cpp
  bool solvePnP( InputArray objectPoints, InputArray imagePoints,
                 InputArray cameraMatrix, InputArray distCoeffs,
                 OutputArray rvec, OutputArray tvec);
  ```
- **Diagram (photo):** A physical armor plate — black plate with a big white digit "**2**" in the center, flanked by two vertical LED light bars (white/blue glow, one on each side). Red dots mark the 4 keypoints used for PnP: point **1** = top of left light bar, point **2** = top of right light bar, point **3** = bottom of right light bar, point **4** = bottom of left light bar (clockwise from top-left, per the rule stated above). A local coordinate frame is drawn on the plate: red arrow = **x** (pointing right), green arrow = **y** (pointing down), origin at plate center.
- One frame (f_0011) shows the WPS Presentation window title bar reading **"Lectrue4 Hello Armor.pptx"**, confirming this is the correct source deck (note the typo "Lectrue").

### 2a. VS Code project structure (visible in Explorer panel throughout the demo)

Project `LECTURE4`, with folders/files:
```
LECTURE4/
  answer/
    main.cpp
  class/
    io/
    src/
      main.cpp          <-- file being edited
    tasks/
      armor.hpp
      detector.cpp
      detector.hpp
      tools/
    CMakeLists.txt
```
Terminal cwd: `mr@mr-virtual-machine:~/桌面/lecture4/class$`
Terminal listing: `CMakeLists.txt  io  src  tasks  tools  video.avi`

So there are two parallel copies of `main.cpp` — a student stub (`class/src/main.cpp`, with tasks to fill in) and a reference `answer/main.cpp`.

### 2b. Code walkthrough — `main.cpp` (student stub), top portion (frames 3, 5)

```cpp
static const cv::Mat distort_coeffs =
    (cv::Mat_<double>(1, 5) << -0.47562935060124745, 0.2183174582961...);
// clang-format on

static const double LIGHTBAR_LENGTH = 0.056;  // 灯条长度   单位: 米
static const double ARMOR_WIDTH = 0.135;      // 装甲板宽度 单位: 米

// #### Task 01 ####################################
// object_points 是 物体局部坐标系下 n个点 的坐标。
// 对于我们而言，也就是装甲板坐标系下4个点的坐标。
// 请填写下面的 object_points:

static const std::vector<cv::Point3f> object_points {
    {      ,      , 0 },  // 点 1
    {      ,      , 0 },  // 点 2
    {      ,      , 0 },  // 点 3
    {      ,      , 0 }   // 点 4
};
```
(In frame 3 this block is still commented out with `//`; in frame 5 the `object_points` declaration is shown uncommented as the fill-in-the-blank template, cursor at line 26.)

**Task 01 (exercise):** Fill in the `{x, y, 0}` coordinates for points 1–4 in the armor's own local/object coordinate system, using `ARMOR_WIDTH` (0.135 m) and `LIGHTBAR_LENGTH` (0.056 m) as the half-extents, consistent with the point-numbering convention shown on the slide (1 = top-left, clockwise) and the drawn local x (right) / y (down) axes.

### 2c. Code walkthrough — `main.cpp`, main loop / Task 02 (frames 7, 8)

```cpp
int main(int argc, char *argv[])
...
while (true)
{
    cap >> img;
    if (img.empty())   // 读取失败 或 视频结尾
        break;

    auto armors = detector.detect(img);

    if (!armors.empty())
    {
        auto armor = armors.front();                 // 如果识别到了大于等于1个装甲板
        tools::draw_points(img, armor.points);        // 绘制装甲板

        // #### Task 02 #############################################
        // img_points 是 像素坐标系下 n个点 的坐标。
        // 对于我们而言，也就是照片上 装甲板 4个点的坐标。
        // 请你填写下面的 img_points:
        //
        // std::vector<cv::Point2f> img_points{ , , , };
        //
        // 提示:
        // - 看看 Armor 结构体有哪些成员。
        // - armor 的成员 left 和 right 是两根灯条(Lightbar)。
        // - 灯条Lightbar也是结构体，灯条的顶部和底部端点就是我们要的点了。
        // ###########################################################
```

**Task 02 (exercise):** Populate `img_points` (a `std::vector<cv::Point2f>`) with the 4 pixel-coordinate keypoints of the detected armor, read off the already-existing `Armor` struct (members `left` and `right`, each a `Lightbar` struct with top/bottom endpoint members) — i.e., wire up the detector's output into the vector solvePnP needs, matching the same point order (1 = top-left, clockwise) established earlier.

### 2d. Code walkthrough — `main.cpp`, Task 03: calling solvePnP (frames 10, 12)

```cpp
// #### Task 03 ##############################################
cv::Mat rvec, tvec;
// 所有要传入的值都已经具备了。现在调用 solvePnP 解算装甲板位姿,
// rvec 和 tvec 用于存储 solvePnP 输出的结果。
// 你需要在下面填写 输入给 solvePnP 的参数:
//
cv::solvePnP( , , , , rvec, tvec);
//
// ############################################################
```

**Task 03 (exercise):** Call `cv::solvePnP(object_points, img_points, camera_matrix, distort_coeffs, rvec, tvec)` (blanks to fill: object points, image points, camera matrix, distortion coefficients) to solve for the armor's pose, storing results in `rvec`/`tvec`.

### 2e. Live demo output (frame 13)

Program run (window titled "Main", console overlay "press q to quit") on a live/recorded camera feed of an armor plate (red-lit light bar visible, red horizontal/vertical reference lines drawn on frame). On-screen text overlay printed by the program:
```
tvec:  x-0.00 y 0.01 z 0.24
rvec:  x-0.06 y 0.00 z 0.01
euler angles:  yaw 0.00 pitch 0.0...
```
(This shows the `tvec`/`rvec` numeric outputs of solvePnP being printed live onto the video via `tools::draw_text`; note "euler angles" line is already present here in a later re-run, ahead of Task 05 being covered — the frame ordering reflects the instructor re-running the finished demo before rewinding to explain internals, or this is actually the post-Task-05 run reused for illustration.)

### 2f. Build/debug moment (frame 14)

Terminal shows a runtime error when re-running after editing:
```
OpenCV exception:
OpenCV(4.5.4) ./modules/videoio/src/cap_images.cpp:253: error: (-5:Bad argument) CAP_IMAGES: can't find starting number (in the name of file): video.avi in function 'icvExtractPattern'
```
Followed by commands fixing the working directory:
```
mr@mr-virtual-machine:~/桌面/lecture4/class/build$ cd ../
mr@mr-virtual-machine:~/桌面/lecture4/class$ ./build/main
```
(Demonstrates a common gotcha: running the compiled binary from the wrong working directory so it can't find `video.avi`; fixed by `cd`-ing back to the project root before invoking `./build/main`.)

---

## 3. Rotation representation #1: Euler angles (frames 16, 18, 21)

**Slide title:** 旋转的另一种表示方法：欧拉角 ("Another way to represent rotation: Euler angles")

**Diagram:** Airplane icon with three colored rotation arrows: blue arrow around the vertical axis labeled **Yaw / Odchylenie**; red arrow around the lateral (wing) axis labeled **Pitch / Pochylenie**; green arrow around the longitudinal (nose-tail) axis labeled **Roll / Przechylenie** (diagram credit "MakeGIF.com"; axis labels appear bilingual English/Polish, likely a stock diagram).

Body text (verbatim, translated inline):
> 偏航角 yaw: 先绕"上下的轴"旋转，改变"前进方向"
> （Yaw: first rotate around the "up-down axis," changing the "forward direction.")
> 俯仰角 pitch: 再绕"左右的轴"旋转，改变"俯仰程度"
> （Pitch: then rotate around the "left-right axis," changing the "degree of pitch.")
> 横滚角 roll: 最后绕"前进/后退方向的轴"旋转，改变"倾斜程度"
> （Roll: finally rotate around the "forward/backward axis," changing the "degree of tilt/lean.")

Bottom caption:
> 欧拉角的表述并不是唯一的，其存在万向死锁
> ("The Euler-angle representation is not unique, and it suffers from gimbal lock.")
> Reference link: `https://zhuanlan.zhihu.com/p/9135205633`

### 3a. Interactive demo: quaternions.online (frames 17, 19, 20)

Browser tour of the site **quaternions.online** (Chrome, tab title "Quaternions - Visualisation"), showing side-by-side panels:
- **Quaternion**: W, X, Y, Z fields (default 1.000, 0.000, 0.000, 0.000) + "Apply Rotation" button.
- **Euler Angles**: X, Y, Z fields (default 0.000 each), an "XYZ - Order" dropdown, a "Degrees" unit dropdown, + "Apply Rotation" button.
- A live 3D grid/axes visualization (red = x, green = y, blue = z) that updates as either representation is edited — used to visually demonstrate how quaternion and Euler-angle rotation representations relate and how rotation order affects orientation.
- Site banner ad: "You've had enough of Quaternions? Check out my NPC Town Building Game!"

---

## 4. Rotation representation #2: comparing rvec / rotation matrix / Euler angles / quaternion (frames 23, 25, 28)

**Slide title:** 还有什么别的表示方法？ ("What other representations are there?")

**Diagram (flow chart):**
```
旋转向量  --罗德里格斯公式 (cv::Rodrigues)-->  旋转矩阵  --反三角函数-->  欧拉角      四元数
 rvec                                          rmat
```
(Rotation vector (rvec) → [Rodrigues' formula, `cv::Rodrigues`] → Rotation matrix (rmat) → [inverse trig functions] → Euler angles; Quaternion shown off to the side as yet another representation, not derived via this chain in the slide.)

**Formula table shown** (for converting rotation-matrix elements to Euler angles under the "INT_YXZ" intrinsic rotation-order convention):
```
INT_YXZ:  θ1 = arctan2(m13, m33)     θ2 = -arcsin(m23)     θ3 = arctan2(m21, m22)
```
(Here mᵢⱼ denotes the (i,j) entry of the rotation matrix `rmat`.)

Bottom reference: "线性代数知识: https://www.bilibili.com/video/BV1ns41167b9" (a linear-algebra background video, presumably covering rotation matrices).

### 4a. Code walkthrough — Task 04: printing tvec/rvec (frame 24)

```cpp
// #### Task 04 ################################################
// 现在, draw_text 只打印 0.0
// 请你改写下面draw_text的参数, 把解得的 tvec 和 rvec 打印出来
//
tools::draw_text(img, fmt::format("tvec:  x{:.2f} y{: ...
tools::draw_text(img, fmt::format("rvec:  x{:.2f} y{: ...
//
// 提示:
// - 使用 tvec.at<double>(0) 可以得到一个double变量，它是tve...
```

**Task 04 (exercise):** Currently `draw_text` just prints the literal `0.0`; rewrite the `fmt::format` arguments so the computed `tvec` and `rvec` values are actually printed onto the frame. Hint given: `tvec.at<double>(0)` extracts a `double` element (the x-component) from the `cv::Mat`.

### 4b. Code walkthrough — Task 05: rvec → rmat → Euler angles (frame 26)

```cpp
// #### Task 05 ####################################################
// 使用 cv::Rodrigues , 把 rvec 旋转向量转换为 rmat 旋转矩阵。
// 再使用反三角函数，把旋转矩阵 rmat 中的元素转化为欧拉角，并在图...
//
cv::Mat rmat;
cv::Rodrigues(rvec, rmat);

tools::draw_text(img, fmt::format("euler angles:  yaw{:...
//
// 提示:
// - cv::Mat 的下标从0开始，而不是1。
// - 从cv::Mat 中取元素的方法和上面的 tvec 类似。如: rmat.at<...
```

**Task 05 (exercise):** Use `cv::Rodrigues(rvec, rmat)` to convert the rotation vector into a rotation matrix, then apply the inverse-trig formulas from the slide (the `INT_YXZ` table) to compute yaw/pitch/roll from `rmat`'s elements, and print them via `draw_text`. Hints: `cv::Mat` indices are 0-based; element access via `rmat.at<double>(row, col)`, analogous to the earlier `tvec.at<double>(...)` usage.

Terminal in this frame shows the program was rebuilt/rerun successfully with no errors (`./build/main` run twice cleanly), confirming the fix from the earlier debugging step (frame 14).

### 4c. Live demo output after Task 05 (frame 27)

Same live camera window as before ("press q to quit"), now showing all three output lines populated:
```
tvec:  x-0.00 y 0.01 z 0.24
rvec:  x-0.02 y 0.00 z 0.01
euler angles:  yaw 0.00 pitch-0....
```

---

## 5. "我真的对准了吗？" ("Am I really aimed correctly?") (frames 29, 31)

Left column, subheading **相机坐标系** ("Camera coordinate system"):
> 与相机刚性连接的坐标系，同相机一起平移、旋转。
> 原点：镜头光心
> (A coordinate system rigidly attached to the camera, translating/rotating together with it. Origin: the optical center of the lens.)

Follow-up prompt (posed as a rhetorical/discussion question):
> 如果相机安装有倾斜而且并不和枪管在同个位置会怎么样？
> ("What happens if the camera is mounted at an angle, and isn't co-located with the gun barrel?")

**Diagram (photo):** An armor-plate target (digit "3", red-lit light bars) mounted on a wall, with its local axes drawn (z pointing out, y down, x right). In the foreground, a camera/sight module on a small gimbal/mount, with its own camera-coordinate axes drawn (z forward, x right, y down) — visually showing the camera's optical axis is offset/rotated relative to the gun barrel/plate normal, motivating the need for careful coordinate-frame bookkeeping (not just "center of image = aim point").

---

## 6. "为什么我们需要装甲板姿态？" ("Why do we need armor-plate pose?") (frame 30)

**Diagram (photo):** A RoboMaster-style ground robot chassis/wheel assembly caught mid-motion (motion-blurred wheel, red LED indicator lights, number "3" visible on a partially-shown armor plate), illustrating a robot spinning or moving unpredictably.

Body text:
> 实际车的运动状态千奇百怪，我们需要装甲板姿态来推算出他的旋转中心，进而对运动进行拟合。
> ("Real robots' motion states vary wildly; we need the armor plate's pose (orientation) to infer its center of rotation, and in turn fit/predict its motion.")

This frames *why* solving for full 6-DoF pose (not just 2D pixel position) matters operationally: it enables estimating a spinning/moving robot's rotation center for predictive aiming, not just where the plate currently appears in the image.

---

## 7. "手眼标定" (Hand-eye calibration) (frame 32)

Left text:
> 获取机器人本体坐标系->相机坐标系的变换
> ("Obtaining the transform from the robot body coordinate system -> camera coordinate system.")

**Diagram:** Classic robot-arm hand-eye calibration schematic (watermarked "eRobotics") — a robotic arm base frame **{B}**, end-effector frame **{E}**, camera frame **{C}** mounted near the arm's end, and a calibration-target/world frame **{K}** off to the side (checkerboard pattern). Red curved arrows labeled **A**, **B**, **C**, **D** trace the loop of coordinate transforms between {B}→{E}→{C}→{K}→{B}, representing the classic `AX = XB`-style hand-eye calibration relationship.

Reference cited: "3D视觉之手眼标定 mp.weixin.qq.com" (a WeChat public-account article on hand-eye calibration for 3D vision).

---

## 8. Closing slide: IMU coordinate transform & full pipeline summary (frame 33)

Body text:
> 机器人本体控制依赖于imu（陀螺仪），需要知道imu到本体坐标系之间的变换。
> ("Robot body control depends on the IMU (gyroscope); we need to know the transform from the IMU frame to the body coordinate frame.")

**Diagram 1 (small inset):** IMU cube diagram showing "force of gravity" (downward arrow, Z axis), and rotation axes labeled Z;Ωz, X;Ωx, Y;Ωy, captioned "Accel; Gyro" — a generic IMU axis-convention illustration.

**Diagram 2 (photo):** An actual robot platform (appears to be an omni-wheel/leg-wheel hybrid chassis with a remote-control transmitter attached) with coordinate frames drawn directly on the hardware and labeled: **imu** (blue axes), **base_link** (red axes, x/y/z), and **camera** (white axes, x/y/z) — showing where each coordinate frame physically sits on the real robot.

Bottom summary line (the lecture's closing synthesis, tying together everything covered):
> 实际坐标系变换流：像素坐标系 -> 相机坐标系 -> 机器人本体坐标系 -> imu坐标系
> solvePnP　　　手眼标定　　　实际安装
>
> ("Actual coordinate-transform pipeline: pixel coordinate system -> camera coordinate system -> robot body coordinate system -> IMU coordinate system, achieved respectively via: solvePnP → hand-eye calibration → actual physical installation/measurement.")

This is the final frame captured and functions as the lecture's wrap-up, chaining together: (1) solvePnP (pixel→camera, what was coded in the exercise), (2) hand-eye calibration (camera→robot body), and (3) physical/measured installation offsets (body→IMU) as the three links needed to go from "a pixel in the image" to "a usable pose in the robot's control frame."

---

## Topic flow summary

1. **`cv::solvePnP` introduction** — function signature and PnP world/camera/image-plane diagram.
2. **Hands-on armor-pose exercise ("动手试一试")** — physical armor plate, 4-point numbering convention (top-left=1, clockwise), light-bar/armor dimensions.
   - Task 01: fill in `object_points` (3D armor-local coordinates).
   - Task 02: fill in `img_points` (2D pixel coordinates from `Armor`/`Lightbar` struct members).
   - Task 03: call `cv::solvePnP(...)` to compute `rvec`, `tvec`.
   - Live camera demo printing `tvec`/`rvec`; debugging a `video.avi`-not-found runtime error (working-directory issue).
3. **Rotation representation: Euler angles** — yaw/pitch/roll definitions, gimbal-lock caveat, interactive quaternions.online demo (quaternion vs. Euler-angle panels).
4. **Comparing rotation representations** — rvec → (Rodrigues) → rotation matrix → (inverse trig) → Euler angles, plus quaternion; `INT_YXZ` conversion formula.
   - Task 04: print computed `tvec`/`rvec` via `draw_text`.
   - Task 05: `cv::Rodrigues(rvec, rmat)` + inverse-trig formulas to compute/print Euler angles.
   - Live demo showing filled-in `tvec`/`rvec`/`euler angles` overlay.
5. **"Am I really aimed correctly?"** — camera coordinate system definition (origin at lens optical center), camera/gun-barrel misalignment problem.
6. **"Why do we need armor-plate pose?"** — motivation: estimating a moving/spinning robot's rotation center from plate pose, for motion fitting/prediction.
7. **Hand-eye calibration** — transform from robot body frame to camera frame; classic {B}/{E}/{C}/{K} calibration-loop diagram.
8. **Closing: full coordinate-transform pipeline** — IMU frame and gyroscope dependency; real robot hardware frame layout (imu / base_link / camera); summary chain: pixel coords → camera coords (solvePnP) → robot body coords (hand-eye calibration) → IMU coords (physical installation).
