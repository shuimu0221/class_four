# Armor Slides Manifest — "视觉组第四讲：Hello Armor"

Reconstructed from 33 scene-change keyframes extracted from the screen-recorded
lecture. Only frames that substantially show an actual presentation slide were
kept; frames showing VS Code, the Ubuntu VM terminal, a browser-based
quaternion demo, or the live camera/OpenCV demo window were discarded as
code/demo content with no slide to recover. Where the same slide recurred
across multiple frames (revisited by the presenter, shown with WPS window
chrome/popups, or at a different animation-build stage), the single cleanest
/ most complete instance was kept.

| # | New file | Source frame | Slide title / description |
|---|----------|-------------|-----------------------------|
| 01 | 01.jpg | f_0001.jpg | Title slide: `cv::solvePnP` (Perspective n Points) — function signature and PnP geometry diagram (camera/world coordinate systems) |
| 02 | 02.jpg | f_0004.jpg | "动手试一试" (Try it yourself) — practice slide: light-bar corner point numbering convention (1–4 clockwise from top-left), armor plate dimensions (0.135 m × 0.056 m), simplified `solvePnP` call signature, with annotated armor-board camera photo |
| 03 | 03.jpg | f_0018.jpg | "旋转的另一种表示方法：欧拉角" (Another way to represent rotation: Euler angles) — yaw/pitch/roll definitions with aircraft diagram, note on gimbal lock |
| 04 | 04.jpg | f_0023.jpg | "还有什么别的表示方法？" (What other representations are there?) — rotation vector → rotation matrix (Rodrigues' formula, `cv::Rodrigues`) → Euler angles (inverse trig) → quaternion pipeline, with INT_YXZ formula table |
| 05 | 05.jpg | f_0028.jpg | "我真的对准了吗？" (Am I really aligned?) — camera coordinate system definition (origin at lens optical center), question about camera tilt/offset from barrel, with annotated axes photo of gimbal + armor board |
| 06 | 06.jpg | f_0030.jpg | "为什么我们需要装甲板姿态？" (Why do we need armor plate pose?) — motivation slide: real robot motion is varied, armor pose lets us derive the rotation center and fit motion, with omni-wheel robot photo |
| 07 | 07.jpg | f_0032.jpg | "手眼标定" (Hand-eye calibration) — obtaining the transform from robot-body coordinate system to camera coordinate system, with robotic-arm/camera calibration diagram |
| 08 | 08.jpg | f_0033.jpg | Robot body control depends on IMU (gyroscope) — need the IMU-to-body-frame transform; full coordinate chain: pixel → camera → robot body → IMU coordinate systems, with annotated multi-sensor robot photo |

## Notes on discarded/duplicate frames

- f_0002 was an earlier build state of slide 02 (showed the full `solvePnP`
  signature with default `useExtrinsicGuess`/`flags` params, likely a
  transition artifact from the preceding title slide); f_0004 is the
  resting/final state of that slide and was used instead.
- f_0006, f_0009, f_0011, f_0015 are repeated views of slide 02 (some with a
  WPS floating-preview popup or title-bar text overlaying the frame).
- f_0021, f_0025, f_0027 are repeated clean/obstructed views of slides 03 and
  04 respectively.
- f_0031 is a repeated view of slide 05.
- f_0003, f_0005, f_0007, f_0008, f_0010, f_0012, f_0014, f_0024, f_0026 show
  VS Code editing `main.cpp`/`armor.hpp` in the Ubuntu VM — code-along
  content, no slide visible.
- f_0013, f_0029 show the live OpenCV demo window (webcam feed with
  tvec/rvec/euler-angle overlay) — not a slide.
- f_0016, f_0017, f_0019, f_0020 show a browser tab (quaternions.online
  interactive visualizer) used as a live demo — not a slide.
- f_0022 is a blank/black VM window during a transition — no content.
