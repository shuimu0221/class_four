# 2025视觉组培训第五课【装甲板位姿解算】— Keyframe Notes

Source: 42 scene-change keyframes (`f_0001.jpg`–`f_0042.jpg`) extracted from a screen recording of a TJ-SuperPower战队 (Tongji University RoboMaster vision group) training lecture slideshow + live code/VM demo, with a picture-in-picture webcam of the presenter and a second classroom display in the corner of most frames. Notes below follow the frames strictly in order (encodes the lecture's narrative/demo sequence). Near-duplicate frames (same slide, cursor/animation state changed, or VM/IDE window shuffling) are grouped and described rather than re-transcribed verbatim.

---

## 1. Motivating question: why do we need 3D pose, not just a 2D box? (f_0001–f_0004)

**f_0001 — Slide: "直观感受：距离" (Intuitive feel: distance)**
Photo of two real robots in the team's workshop, numbered "3" and "4". Caption: **"相比于4号车，3号车离我们更远"** ("Compared to car #4, car #3 is farther from us"). Sets up the idea that a human can intuitively judge distance/depth just from an image.

**f_0002 — Slide: "装甲板的'朝向'：怎样描述'旋转'" (Armor plate "orientation": how to describe "rotation")**
Three photos of the same armor plate (number "2", blue light bars) at different orientations. Caption: **"图片中的三块装甲板有什么不同？"** ("What's different about the three armor plates in the picture?") — motivating that orientation, not just position, matters.

**f_0003 — Slide: "按特定顺序旋转的欧拉角" (Euler angles rotated in a specific order)**
- Stock diagram (watermark "MakeAGIF.com") of an airplane showing the three rotation axes: **Yaw/偏航** (blue, vertical axis, arrow labeled "Odchylenie" in Polish), **Pitch/俯仰** (red, lateral axis, "Pochylenie"), **Roll/横滚** (green, longitudinal/forward axis, "Przechylenie").
- Body text (order matters, each defined relative to the *result* of the previous rotation):
  - **偏航角 yaw**：先绕"上下的轴"旋转，改变"前进方向" (rotate around the "up-down axis" first, changes heading/forward direction)
  - **俯仰角 pitch**：再绕"左右的轴"旋转，改变"俯仰程度" (then rotate around the "left-right axis", changes pitch/tilt)
  - **横滚角 roll**：最后绕"前进/后退方向的轴"旋转，改变"倾斜程度" (finally rotate around the "forward/backward axis", changes lean/roll)
- Below: two photos of the armor plate "2" with hand-drawn axis overlays (x, y, z) and curved arrows showing a rotation being applied around one axis at a time (first around x, then around z with "x" circled), plus a third photo shown at an angle.
- Partially obscured (by the webcam PiP) text at bottom: "yaw: 45° p…" — an example numeric yaw value being discussed (rest cut off).

**f_0004 — Slide: "'看出'装甲板在三维空间的信息" ("Reading out" the armor plate's 3D information)**
Bullets:
- 距离：远近 (distance: near/far)
- 朝向：向左 / 向右 (orientation: left/right)

Image: armor plate "3" with drawn axes Z (pointing up/out), X (right), Y (down), illustrating the plate's own local coordinate frame attached to it.

*(This exact slide/content reappears standalone later as f_0010.)*

---

## 2. Title slide & switch to editor/VM (f_0005–f_0006)

**f_0005 — PowerPoint editor ("hello PnP.pptx")**
Slide-thumbnail panel (slides 1–7) visible at left. Main canvas shows **slide 2 selected**: a black slide with the small centered title **"装甲板位姿解算"** (Armor Plate Pose Estimation) next to the team's green lightning-bolt "SP" logo — this is the lecture's own section-title slide, confirming the lecture identity. (Slide 1 in the panel appears blank/black — likely an intro/black slide.)

**f_0006 — VMware Workstation window, blank black screen.** Transitional frame — Ubuntu VM loading/switching, no content.

---

## 3. Recap + "can a program compute this?" (f_0007–f_0010)

**f_0007 — PPT editor, slide 14 (thumbnail panel shows slides 10–16)**
Builds on the earlier recap slide with animated bullets (each tagged with a numbered animation order ①①①②):
- "看出"装甲板在三维空间的信息：距离：远近 / 朝向：向左/向右 (repeated from f_0004)
- ① **更准确地描述装甲板的位姿：** (More precisely describing the armor's pose:)
  - ① **位置：用一个三维向量来表示** (Position: represented with a 3D vector)
  - ① **旋转：可以用欧拉角来表示** (Rotation: can be represented with Euler angles)
- ② **程序能解算这些信息吗？** (Can a program solve/compute this information?)

Bottom-right label: **"演示"** (Demo). Armor image with Z/X/Y axes repeated at right.

**f_0008 / f_0009 — Live VM screen-recording, transition into a demo**
A cropped PowerPoint window ("hello PnP.pptx - PowerPoint (Cropped)") floats over the desktop, showing a zoomed reference photo of the armor plate with Z/X/Y axis labels; an OpenCV **`img`** display window is visible behind it (mostly black/empty at this point). Windows taskbar clock reads "9月27 19:05". In f_0009 the same floating photo window is shown overlapping the full PPT editor behind it, with slide 14's bullet text peeking out underneath. These are setup/transition frames for the presenter's physical camera + armor-plate demo rig.

**f_0010 — Standalone (presentation-mode) slide**, content identical to f_0004 ("看出"装甲板在三维空间的信息 / 距离：远近 / 朝向：向左、向右) — a repeat, likely the presenter returning to this slide.

---

## 4. Perspective-n-Points concept (f_0011)

**f_0011 — Slide: "Perspective n Points"**
Bullets:
- 相对应的 n 个点 (n corresponding points)
- 已知相对位置的三维点 (3D points with known relative positions)
- 以及 **对应的** 图像上二维点 (and the **corresponding** 2D points on the image)

Diagram (classic PnP textbook figure): a **camera coordinate system** on the left with focal length **f**, principal point **(u₀, v₀)**, an image plane containing yellow sample points and a labeled point **uᵢ**; a **"World coordinate system"** on the right with orange 3D points **c₁, c₂, c₃, c₄** and a point **Pᵢ**; a red curved arrow labeled **"R, t"** connecting the two frames — illustrating that solving PnP recovers the rotation **R** and translation **t** between camera and object/world frame.

Below-right: a photo of a plain wall with an electrical outlet/switch panel — this becomes the fixed background used for the live demo in later frames (armor plate + camera rig placed in front of it).

---

## 5. `cv::solvePnP` signature (f_0012)

**f_0012 — Slide: "cv::solvePnP"**
Function-reference card:
```
solvePnP()
bool cv::solvePnP (
  InputArray   objectPoints,
  InputArray   imagePoints,
  InputArray   cameraMatrix,
  InputArray   distCoeffs,
  OutputArray  rvec,
  OutputArray  tvec,
  bool         useExtrinsicGuess = false,
  int          flags = SOLVEPNP_ITERATIVE
)
```
Labeled **输入 (Input)**: objectPoints, imagePoints, cameraMatrix, distCoeffs. Labeled **输出 (Output)**: rvec, tvec. Green arrows annotate the inputs:
- objectPoints → **物体局部坐标系的n个点** (n points in the object's own/local coordinate frame)
- imagePoints → **图像上的n个点** (n points on the image)
- cameraMatrix & distCoeffs → **与相机有关的参数。我们会提供给你。** (camera-related parameters — we will provide these to you)

---

## 6. What does solvePnP actually output? (f_0013–f_0016)

**f_0013 / f_0016 — Slide: "solvePnP 解出了什么" (What does solvePnP solve for?)**
- **tvec 是一个3\*1的向量** (tvec is a 3×1 vector)
  - 装甲板坐标系的原点在相机坐标系下的位置 (the position of the armor coordinate frame's origin, expressed in the camera coordinate frame)
  - 平移向量 (translation vector)
- **rvec 也是一个3\*1的向量** (rvec is also a 3×1 vector)
  - **rvec是什么？** (What is rvec?)
  - **先写代码，留个悬念，后面再来解答这个问题。** (Write the code first — leave it as a cliffhanger, answer this question later.)

Photo: armor plate with its Z/X/Y axes, and below it a photo of the physical camera/lens with its **own** coordinate axes drawn (camera frame). Red laser-pointer dots are visible on the wall in the background — apparently used as a physical aiming/alignment reference for the demo rig.

**f_0014 —** PPT editor revisit of the f_0007 slide (same "看出…/更准确地描述…/程序能解算" content) — near-duplicate, no new information.

**f_0015 — Live terminal demo (VMware, path `~/Desktop/show`)**
Scrolling console output of live yaw/pitch/roll numbers as the physical rig is moved, e.g.:
```
yaw: 14.36, pitch: 1.68, roll: 3.66
yaw: 14.29, pitch: 3.31, roll: 6.33
yaw: 13.40, pitch: 2.14, roll: 8.33
...
yaw: 2.05, pitch: -35.62, roll: -29.66
```
(This is a preview of the final Task-05 output shown early, before the code that produces it is walked through.)

---

## 7. Coding Time — Task 01–04 (f_0017–f_0024)

**f_0017 — VS Code, `main.cpp` (project "Lesson_5")**
```cpp
int main(int argc, char *argv[])
...
// tvec 和 tvec 用于存储 solvePnP 输出的结果
// 你需要在下面填写 输入给 solvePnP 的参数：
//
cv::solvePnP(object_points, img_points, camera_matrix, distort_coeffs, rvec, tvec);
```
A floating cropped PowerPoint reference window is pinned over the editor, showing the tail of a slide bullet ("…和rvec显示出来出来") and the armor-plate reference photo with 4 numbered keypoints; a sliver of a `fmt::format` call reading `tvec.at<double>(0), tvec.at<double>...` / `rvec.at<double>(0), rvec.at<double>...` and the comment "首个元素的值。" (the value of the first element) is visible at the frame's right edge.

**f_0018 — Slide: "写代码时间！" (Coding time!)**
- 完成代码中的 **Task 01 ~ 04** (Complete Task 01–04 in the code)
  - 按特定的点的顺序，初始化 **object_points** 和 **img_points** (Initialize object_points and img_points, in a specific point order)
  - 调用 **solvePnP** (Call solvePnP)
  - 把解得的 **tvec** 和 **rvec** 显示出来 (Display the solved tvec and rvec)

Photo: armor plate with 4 numbered keypoints marked with green dots at the light-bar corners — **1 (top-left), 2 (top-right), 3 (bottom-right), 4 (bottom-left)** — Z/X/Y axes drawn on the plate, red laser dots on the wall.

**f_0019 / f_0021 / f_0023 — PPT editor**, repeatedly showing/editing the same slide 18 (the keypoint photo with points 1–4 numbered, selection/resize handles visible) — presenter adjusting the slide, no new content.

**f_0020 — VMware VM-manager home screen** showing two VM thumbnails (Ubuntu-0911, Ubuntu 64位) — transition frame.

**f_0022 — Standalone duplicate of the f_0018 "写代码时间!" slide** (full-screen presentation mode).

**f_0024 — VS Code, `main.cpp`, Task 04 code block**
```cpp
// #### Task 04 ####################################
// 现在，draw_text 只打印 0.0
// 请你改写下面draw_text的参数，把解得的 tvec 和 rvec 打印出来
//
tools::draw_text(img, fmt::format("tvec:  x{: .2f} y{: .2f} z{: .2f}", tvec.at<double>(0), tvec.at<double>(1), tvec.at<double>(2)), ...);
tools::draw_text(img, fmt::format("rvec:  x{: .2f} y{: .2f} z{: .2f}", rvec.at<double>(0), rvec.at<double>(1), rvec.at<double>(2)), ...);
//
// 提示：
// - 使用 tvec.at<double>(0)，可以得到一个double变量，它是tvec中首个元素的值。
//
// #### Task 05 ####################################
```
Uses the team's `tools::draw_text` helper together with `fmt::format` (fmtlib) to overlay the solved x/y/z components of `tvec`/`rvec` onto the displayed image. VMware task-switcher thumbnails (Ubuntu-0911, Ubuntu 64位) visible at the bottom of the frame.

---

## 8. Answering the "what is rvec?" cliffhanger (f_0025–f_0028)

**f_0025 — Slide: "rvec是什么？" (What is rvec?)**
Single bullet: **"转动装甲板，观察rvec的方向和大小。"** (Rotate the armor plate and observe the direction and magnitude of rvec.) — the question is answered experimentally rather than by formula at this point.

**f_0026 — Live demo**
Floating cropped PPT window (top-left) with the keypoint reference photo (points 1–4); a large `img` OpenCV window (dark/near-empty) behind it; a terminal on the right scrolling live **roll** values as the plate is rotated, e.g.:
```
roll: 2.01
roll: 2.30
roll: 2.32
roll: 2.26
...
roll: 6.40
```
VS Code visible bottom-right with the same `rvec.at<double>(...)` fragment and "首个元素的值。" comment as before.

**f_0027 —** PPT editor, large view of the keypoint reference photo (armor + points 1–4 + camera axes) with "单击此处添加备注" (click to add notes) visible at the bottom — continuation of the same demo/slide-review, no new textual content.

**f_0028 — Standalone duplicate of the "写代码时间!" (Task 01–04) slide** shown again for reference/recap.

---

## 9. Other representations of rotation: rvec → rmat → Euler angles / quaternion (f_0029–f_0036)

**f_0029 — PPT editor, Animation pane populated (build order of the next slide)**
Entries listed (with icons) in order: 文本框7: 旋转向量 (rotation vector) → 文本框12: rvec → 文本框8: 旋转矩阵 (rotation matrix) → 文本框13: rmat → 文本框11: cv::Rodrigues → 直接箭头连接符2 (arrow) → 文本框14: 罗德里格斯 (Rodrigues) → 直接箭头连接符15 (arrow) → 文本框16: 反三角函数 (inverse trigonometric functions) → 图片3 → 文本框10: 四元数 (quaternion). This is the presenter's animation build sequence for the upcoming diagram slide (canvas still shows the earlier demo photo underneath).

**f_0030 — Same slide, mid-build**
Headers visible: **"反三角函数"** (inverse trig functions), **"欧拉用"** (truncated — "欧拉角"/Euler angle), **"四元数"** (quaternion), connected with a blue arrow. Partial formula visible at the bottom: **"…) = arctan2(m.., m..)"**, plus a reference URL: `https://docs.opencv.org/4.x/d4/d4a/classcv_1_1Quat.html#a5fa902f27a084399249384db77e03d9b` (OpenCV's `cv::Quat` class documentation).

**f_0031 — VS Code + floating formula box**
Floating PPT window shows the explicit Euler-angle extraction formula for order **INT_YXZ**:

| INT_YXZ | θ₁ = arctan2(m₁₃, m₃₃)  θ₂ = −arcsin(m₂₃)  θ₃ = arctan2(m₂₁, m₂₂) |
|---|---|

Code behind (end of `main.cpp`'s loop):
```cpp
cv::imshow("img", img);
if (cv::waitKey(30) == 'q')
    break;
}
cv::destroyAllWindows();
return 0;
}
```

**f_0032 — VS Code, the actual Euler-angle computation code**
```cpp
double yaw   = atan2(rmat.at(0, 2), rmat.at(2, 2));
double pitch = -asin(rmat.at(1, 2));
double roll  = atan2(rmat.at(1, 0), rmat.at(1, 1));

fmt::print("yaw: {:.2f}, pitch: {:.2f}, roll: {:.2f}\n", yaw * 57.3, pitch * 57.3, roll * 57.3);

// tools::draw_text(img, fmt::format("euler angles: yaw{: .2f} pitch{: .2f} roll{: .2f}", yaw * 57.3, pitch * 57.3, roll * 57.3), cv::Po...
```
(Note: multiplying by **57.3** ≈ 180/π converts radians → degrees.) Terminal below shows the corresponding live yaw/pitch/roll printout, matching the earlier preview in f_0015.

**f_0033 — Windows desktop transition frame** (desktop icons: IntelliJ IDEA, VMware Workstation, PyCharm, Visual Studio 2022, Visual Studio Code, AutoCAD, MATLAB, etc.; two minimized cropped-PPT windows at bottom-left). No content.

**f_0034 — VS Code, Task 05 instructions (full)**
```cpp
// #### Task 05 ####################################
// 使用 cv::Rodrigues，把 rvec 旋转向量转换为 rmat 旋转矩阵。
// 再使用反三角函数，把旋转矩阵 rmat 中的元素化为欧拉角，并在画面上显示。
//
cv::Mat rmat;
cv::Rodrigues(rvec, rmat);
tools::draw_text(img, fmt::format("euler angles: yaw{: .2f} pitch{: .2f} roll{: .2f}", 0.0, 0.0, 0.0), ...);
//
// 提示：
// - cv::Mat 的下标从0开始，而不是1。
// - 从cv::Mat中取元素的方法和上面的 tvec 类似。如：rmat.at<double>(0, 2)
```
The floating PPT window with the INT_YXZ formula box remains visible for reference.

**f_0035 — Full slide reveal: "旋转 还有什么别的表示方法？" (Rotation — what other ways to represent it are there?)**
Diagram (matching the animation-build order seen in f_0029/f_0030), described as a flow:
- ① **旋转向量 (rotation vector)** → box **`rvec`**
- arrow ③ labeled **"罗德里格斯公式 / cv::Rodrigues"** (Rodrigues' formula) leads to
- ② **旋转矩阵 (rotation matrix)** → box **`rmat`**
- arrow ④ labeled **"反三角函数"** (inverse trigonometric functions) leads to
- **欧拉角 (Euler angles)**, with the formula box below it: `INT_YXZ | θ₁=arctan2(m₁₃,m₃₃)  θ₂=−arcsin(m₂₃)  θ₃=arctan2(m₂₁,m₂₂)`
- a second branch labeled ⑥ from `rmat` leads to **四元数 (quaternion)**

Bottom: the same OpenCV `cv::Quat` documentation URL as f_0030. Right side: the armor + camera demo photo. This slide is essentially a concept map: **rvec ⇄ rmat** via Rodrigues' formula (`cv::Rodrigues`, invertible both ways), and **rmat → Euler angles** (via inverse trig functions/arctan2, arcsin) or **rmat → quaternion**.

**f_0036 — Same slide, an earlier/partial animation state** — only the **"欧拉角"** label and a faint background photo (with keypoints 1, 2 visible) are shown, i.e. a less-built version of the f_0035 diagram (captured out of strict build order, likely the presenter stepping back through animations).

---

## 10. Task 05 demo and practice (f_0037–f_0039)

**f_0037 — Slide: "演示" (Demonstration)**
Shows only the INT_YXZ Euler-angle formula box (`θ₁=arctan2(m₁₃,m₃₃)  θ₂=−arcsin(m₂₃)  θ₃=arctan2(m₂₁,m₂₂)`) — presenter about to demo the Task 05 result live.

**f_0038 — Slide: "实践" (Practice / exercise)**
Bullet: **"完成Task 05"** (Complete Task 05). The INT_YXZ formula box is shown again as the reference formula students need to implement.

**f_0039 — PPT editor, same "实践" slide, with an added text box: `std::atan2(double, double)`**
Presenter highlights the **C++ standard-library** `std::atan2` function signature (two `double` arguments) as an implementation hint for computing the Euler angles in Task 05.

---

## 11. Closing (f_0040–f_0042)

**f_0040 — Final slide: "Thanks"** — black slide with the team's green lightning-bolt "SP" logo and white text "Thanks".

**f_0041 — PPT editor, end-of-deck slide panel** (slides 23–27 visible as thumbnails):
- Slide 23: "演示"
- Slide 24: "实践" (formula + `std::atan2` hint)
- Slide 25: thumbnail shows a small flow-chart/pipeline diagram (text too small to read precisely in the thumbnail, but appears to be a recap diagram of the detection→pose pipeline, e.g. boxes/arrows leading toward `cv::solvePnP` and `tvec`/`rvec`)
- Slide 26: thumbnail bullet list, legible as a **course syllabus recap**:
  - Lesson 1 Ubuntu shell g++
  - Lesson 2 CMake
  - Lesson 3 OpenCV
  - Lesson 4 OOP
  - Lesson 5 PnP
- Slide 27 (selected, shown in main canvas): "Thanks"

**f_0042 — Wide classroom shot.** Both the projector screen and the secondary display show the "Thanks" slide; the presenter stands at the podium with a second student near the display screen; students are seated in the foreground with laptops open. Wall clock reads **20:01:36**. This is the closing shot of the recording.

---

## Topic flow summary

1. **Motivation** — why 2D detection isn't enough: intuitively judging distance (直观感受：距离) and orientation/"rotation" (装甲板的"朝向") from images; introduces yaw/pitch/roll via the airplane Euler-angle diagram.
2. **Recap of the goal** — describing an armor plate's pose as (a) a 3D position vector and (b) Euler-angle rotation; poses the question "can a program compute this?"
3. **Perspective-n-Points (PnP)** — formal definition: n corresponding 3D object points and 2D image points, camera frame vs. world frame, recovering rotation **R** and translation **t**.
4. **`cv::solvePnP` API** — function signature: inputs `objectPoints`, `imagePoints`, `cameraMatrix`, `distCoeffs`; outputs `rvec`, `tvec`; default `flags = SOLVEPNP_ITERATIVE`.
5. **What solvePnP outputs** — `tvec` (3×1 translation vector = armor-frame origin in camera frame) and `rvec` (3×1 vector, meaning deferred as a "cliffhanger").
6. **Coding Time (Task 01–04)** — initialize `object_points`/`img_points` in a fixed keypoint order (1–4 around the armor plate), call `cv::solvePnP`, and use `tools::draw_text` + `fmt::format` to display the solved `tvec`/`rvec` components on screen; live terminal demo of yaw/pitch/roll.
7. **Answering "what is rvec?"** — empirically, by rotating the physical armor plate and observing how `rvec` changes.
8. **Other rotation representations** — map of `rvec` (rotation vector) ⇄ `rmat` (rotation matrix) via **Rodrigues' formula** (`cv::Rodrigues`), then `rmat` → **Euler angles** via inverse trig functions (`atan2`, `asin`, order **INT_YXZ**) or `rmat` → **quaternion** (reference to OpenCV's `cv::Quat` docs).
9. **Task 05** — use `cv::Rodrigues(rvec, rmat)` to get the rotation matrix, then compute yaw/pitch/roll with `atan2`/`asin` (radians × 57.3 → degrees) and display them; hint toward `std::atan2(double, double)`.
10. **Practice/demo** of Task 05 and formula recap.
11. **Closing** — "Thanks" slide; end-of-deck recap of the full course syllabus so far (Lesson 1 Ubuntu shell/g++, Lesson 2 CMake, Lesson 3 OpenCV, Lesson 4 OOP, Lesson 5 PnP).
