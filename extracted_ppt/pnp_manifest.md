# PnP Lecture Slide Deck — Reconstruction Manifest

Source: 42 scene-change keyframes (`f_0001.jpg`–`f_0042.jpg`) extracted from the screen
recording of "2025视觉组培训第五课【装甲板位姿解算】" (slide deck `hello PnP.pptx`).

Of the 42 raw frames, 27 contained some form of slide content, but most were either
duplicates (the presenter lingering on / revisiting the same slide, causing repeated
scene-change triggers) or PowerPoint-editor views of a slide already captured cleanly
elsewhere, or partial in-slide animation build states superseded by a more complete
capture of the same slide (editor view always renders the full slide content regardless
of animation progress, so an editor screenshot was preferred whenever it showed strictly
more of a slide's final content than any presentation-mode screenshot of that same
slide). The remaining ~15 frames were VS Code / terminal / VMware / Windows-desktop /
live-camera-demo content or a photo of the physical room, with no real slide visible,
and were discarded. After merging duplicates/build-stages, 14 distinct slides could be
recovered from this frame set (some slides visible only as small side-panel thumbnails —
e.g. "rvec 旋转向量", "还有什么别的表示方法？解出了旋转向量rvec，怎样得到欧拉角？", the
closing process-diagram slide, and the course-outline recap slide — never appeared as a
usable full frame anywhere in the 42 keyframes, so they could not be reconstructed).

| # | File | Source frame | Slide title / description |
|---|------|--------------|----------------------------|
| 01 | 01.jpg | f_0005.jpg | Title slide: 装甲板位姿解算 (editor view; only instance available) |
| 02 | 02.jpg | f_0001.jpg | 直观感受：距离 — two robot photos, "相比于4号车，3号车离我们更远" |
| 03 | 03.jpg | f_0002.jpg | 装甲板的"朝向"：怎样描述"旋转" — three armor-plate "2" photos at different tilts |
| 04 | 04.jpg | f_0003.jpg | 按特定顺序旋转的欧拉角 — yaw/pitch/roll airplane diagram + armor-plate axis photos |
| 05 | 05.jpg | f_0007.jpg | "看出"装甲板在三维空间的信息 — distance/orientation, then 位置(3D向量)/旋转(欧拉角), "程序能解算这些信息吗？" (final build state, editor view) |
| 06 | 06.jpg | f_0011.jpg | Perspective n Points — n-point correspondence diagram (camera/world coords) |
| 07 | 07.jpg | f_0012.jpg | cv::solvePnP — function signature with inputs/outputs annotated |
| 08 | 08.jpg | f_0013.jpg | solvePnP 解出了什么 — tvec (3x1 translation) and rvec (3x1, "留个悬念") |
| 09 | 09.jpg | f_0018.jpg | 写代码时间！— Task 01~04: 初始化object_points/img_points, 调用solvePnP, 显示tvec/rvec |
| 10 | 10.jpg | f_0025.jpg | rvec是什么？— "转动装甲板，观察rvec的方向和大小" (editor view; only instance available) |
| 11 | 11.jpg | f_0035.jpg | 旋转：还有什么别的表示方法？— rvec →(cv::Rodrigues)→ rmat →(反三角函数)→ 欧拉角 / 四元数 diagram, plus INT_YXZ Euler-angle formula table (final build state, editor view) |
| 12 | 12.jpg | f_0037.jpg | 演示 — INT_YXZ Euler-angle extraction formula (θ1,θ2,θ3 from rotation matrix) |
| 13 | 13.jpg | f_0039.jpg | 实践 — 完成Task 05, same INT_YXZ formula table + std::atan2(double,double) hint (final build state, editor view) |
| 14 | 14.jpg | f_0040.jpg | Thanks — closing slide with TJ-SuperPower logo |

## Notes on discarded/superseded frames

- **Duplicates of a slide already selected**: f_0004, f_0010, f_0014 (partial/duplicate
  builds of "看出装甲板在三维空间的信息", superseded by f_0007); f_0016 (duplicate of
  "solvePnP解出了什么", superseded by f_0013); f_0022, f_0023, f_0027, f_0028, f_0029
  (duplicates / partial or scrolled editor views of "写代码时间！", superseded by
  f_0018); f_0030, f_0036 (partial-build views of "还有什么别的表示方法？", superseded
  by f_0035); f_0038 (partial-build view of "实践", superseded by f_0039); f_0041
  (duplicate editor view of "Thanks", superseded by f_0040).
- **No usable slide visible** (VS Code / terminal / VMware Workstation / Windows desktop
  / small floating "cropped" PPT preview window over other content / photo of the
  lecture room): f_0006, f_0008, f_0009, f_0015, f_0017, f_0019, f_0020, f_0021, f_0024,
  f_0026, f_0031, f_0032, f_0033, f_0034, f_0042.
- **Slides referenced only in the editor's side thumbnail panel but never shown as a
  usable full frame** (so not recoverable from this keyframe set): "回顾：上节课我们学
  了什么？", "还差了什么？", "直观感受：朝向", "rvec 旋转向量", "还有什么别的表示方法？
  解出了旋转向量rvec，怎样得到欧拉角？", a process-flow summary diagram (cv::Mat Image →
  detector → … → cv::solvePnP → Euler angles), and a course-outline recap slide
  (Lesson 1–5 list).
