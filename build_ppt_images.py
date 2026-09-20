"""从 video.avi 抽帧并生成 PPT 配图（能自动生成的那部分）。

产出到 lecture4/yolo/docs/ppt_images/，供 build_ppt.py 使用。
"""
import os
import sys

import cv2
import numpy as np
import openvino as ov

R = r"C:/Users/ziang.xu/Documents/sp/class_four"
YOLO = os.path.join(R, "lecture4/yolo")
VIDEO = os.path.join(YOLO, "assets/video.avi")
MODEL = os.path.join(YOLO, "assets/yolov5.xml")
OUT = os.path.join(YOLO, "docs/ppt_images")
os.makedirs(OUT, exist_ok=True)

# 与 class_four/lecture4/class/src/main.cpp 顶部一致的相机内参
K = np.array([[1286.307063384126, 0, 645.34450819155256],
              [0, 1288.1400736562441, 483.6163720308021],
              [0, 0, 1]], dtype=np.float64)
D = np.array([-0.47562935060124745, 0.21831745829617311,
              0.0004957613589406044, -0.00034617769548693592, 0], dtype=np.float64)
W, L = 0.135, 0.056
OBJ = np.array([[-W/2, -L/2, 0], [W/2, -L/2, 0], [W/2, L/2, 0], [-W/2, L/2, 0]], np.float64)

CONF_THR = 0.7
FONT = cv2.FONT_HERSHEY_SIMPLEX
GREEN = (80, 220, 80)
YELLOW = (0, 220, 255)
RED = (60, 60, 235)
WHITE = (255, 255, 255)


def build():
    core = ov.Core()
    m = core.read_model(MODEL)
    ppp = ov.preprocess.PrePostProcessor(m)
    i = ppp.input()
    i.tensor().set_element_type(ov.Type.u8).set_shape([1, 640, 640, 3]) \
     .set_layout("NHWC").set_color_format(ov.preprocess.ColorFormat.BGR)
    i.model().set_layout("NCHW")
    i.preprocess().convert_element_type(ov.Type.f32) \
     .convert_color(ov.preprocess.ColorFormat.RGB).scale(255.0)
    return core.compile_model(ppp.build(), "CPU").create_infer_request()


def detect(req, frame):
    """返回 (points[4], confidence, box) 或 None。复刻 YOLOV5::parse 的取点顺序。"""
    s = min(640.0 / frame.shape[0], 640.0 / frame.shape[1])
    h, w = int(frame.shape[0] * s), int(frame.shape[1] * s)
    inp = np.zeros((640, 640, 3), np.uint8)
    inp[0:h, 0:w] = cv2.resize(frame, (w, h))
    req.set_input_tensor(ov.Tensor(np.ascontiguousarray(inp)[None]))
    req.infer()
    out = np.array(req.get_output_tensor().data)[0]
    best, bs = -1, 0.0
    for r in range(out.shape[0]):
        sc = 1.0 / (1.0 + np.exp(-float(out[r, 8])))
        if sc > bs:
            best, bs = r, sc
    if bs < CONF_THR:
        return None
    r = best
    pts = np.array([[out[r, 0] / s, out[r, 1] / s],
                    [out[r, 6] / s, out[r, 7] / s],
                    [out[r, 4] / s, out[r, 5] / s],
                    [out[r, 2] / s, out[r, 3] / s]], np.float64)
    x1, y1 = pts[:, 0].min(), pts[:, 1].min()
    x2, y2 = pts[:, 0].max(), pts[:, 1].max()
    return pts, bs, (int(x1), int(y1), int(x2 - x1), int(y2 - y1))


def solve(pts, obj=OBJ):
    ok, rvec, tvec = cv2.solvePnP(obj, pts, K, D, flags=cv2.SOLVEPNP_ITERATIVE)
    if not ok:
        return None
    proj, _ = cv2.projectPoints(obj, rvec, tvec, K, D)
    err = float(np.mean(np.linalg.norm(proj.reshape(-1, 2) - pts, axis=1)))
    return rvec, tvec, err


def draw_points(img, pts, labels=("0", "1", "2", "3"), color=GREEN, r=11):
    for p, lb in zip(pts, labels):
        c = (int(round(p[0])), int(round(p[1])))
        cv2.circle(img, c, r, color, -1, cv2.LINE_AA)
        cv2.circle(img, c, r, WHITE, 2, cv2.LINE_AA)
        cv2.putText(img, lb, (c[0] + 16, c[1] - 12), FONT, 1.1, color, 3, cv2.LINE_AA)


def banner(img, text, color=YELLOW, y=52, scale=1.35):
    cv2.putText(img, text, (26, y), FONT, scale, (0, 0, 0), 8, cv2.LINE_AA)
    cv2.putText(img, text, (26, y), FONT, scale, color, 3, cv2.LINE_AA)


def main():
    req = build()
    cap = cv2.VideoCapture(VIDEO)
    if not cap.isOpened():
        sys.exit("cannot open video")

    frames = []          # (idx, frame, pts, conf, box, err)
    idx = 0
    while True:
        ok, f = cap.read()
        if not ok:
            break
        idx += 1
        if idx % 6:
            continue
        d = detect(req, f)
        if not d:
            continue
        pts, conf, box = d
        sol = solve(pts)
        if not sol:
            continue
        rvec, tvec, err = sol
        frames.append((idx, f, pts, conf, box, tvec.ravel(), err))
    cap.release()
    sys.stderr.write(f"detected frames: {len(frames)}\n")
    if not frames:
        sys.exit("no detections")

    # ---------- slide 6: 不同距离 / 不同角度 三帧 ----------
    by_z = sorted(frames, key=lambda x: x[5][2])
    picks = [by_z[0], by_z[len(by_z) // 2], by_z[-1]]
    tiles = []
    for _i, f, pts, conf, box, t, err in picks:
        v = f.copy()
        x, y, w, h = box
        cv2.rectangle(v, (x, y), (x + w, y + h), GREEN, 3, cv2.LINE_AA)
        cv2.putText(v, f"z = {t[2]:.2f} m", (x, max(38, y - 14)), FONT, 1.0, GREEN, 3, cv2.LINE_AA)
        tiles.append(cv2.resize(v, (640, 512)))
    # 第四格放一句字幕，避免看起来像没做完
    cap_panel = np.full_like(tiles[2], 32)
    lines = ["同一块装甲板，三个距离", "", "程序怎么知道哪个更远？", "", "答案在 tvec 的 z 上"]
    for k, ln in enumerate(lines):
        sz = 1.15 if k in (0, 2, 4) else 0.9
        col = (235, 235, 235) if k in (0, 2, 4) else (150, 150, 150)
        (tw, _th), _ = cv2.getTextSize(ln, FONT, sz, 2)
        cv2.putText(cap_panel, ln, ((cap_panel.shape[1] - tw) // 2, 210 + k * 52),
                    FONT, sz, col, 2, cv2.LINE_AA)
    combo = np.vstack([np.hstack(tiles[:2]), np.hstack([tiles[2], cap_panel])])
    cv2.imwrite(os.path.join(OUT, "s06_distance_angle.png"), combo)
    sys.stderr.write(f"s06: z = {[f'{p[5][2]:.2f}' for p in picks]}\n")

    # ---------- slide 16: 实物装甲板 + 0/1/2/3 标注 ----------
    _i, f, pts, conf, box, t, err = max(frames, key=lambda x: x[3])
    v = f.copy()
    draw_points(v, pts)
    cv2.rectangle(v, (box[0], box[1]), (box[0] + box[2], box[1] + box[3]), GREEN, 3, cv2.LINE_AA)
    banner(v, f"conf {conf:.2f}   z {t[2]:.2f} m", GREEN)
    cv2.imwrite(os.path.join(OUT, "s16_armor_points.png"), v)
    sys.stderr.write(f"s16: conf={conf:.2f} z={t[2]:.3f} err={err:.2f}\n")

    # ---------- slide 18 / 31: 点序正确 vs 写反 ----------
    # 用同一帧、同一批检测点，只把 object_points 的第 2、4 点对调
    OBJ_BAD = OBJ[[0, 3, 2, 1]]
    _i, f, pts, conf, box, t, err_good = max(frames, key=lambda x: x[3])
    bad = solve(pts, OBJ_BAD)
    err_bad = bad[2]
    sys.stderr.write(f"reproj: good={err_good:.2f}  bad={err_bad:.2f}\n")

    def panel(frame, points, obj, tag, tag_color):
        v = frame.copy()
        sol = solve(points, obj)
        proj, _ = cv2.projectPoints(obj, sol[0], sol[1], K, D)
        proj = proj.reshape(-1, 2)
        # 原始检测点（实心）
        for k, p in enumerate(points):
            c = (int(round(p[0])), int(round(p[1])))
            cv2.circle(v, c, 9, GREEN, -1, cv2.LINE_AA)
            cv2.putText(v, str(k), (c[0] + 14, c[1] - 10), FONT, 0.9, GREEN, 2, cv2.LINE_AA)
        # 重投影点（空心）+ 连线
        for k, p in enumerate(proj):
            c = (int(round(p[0])), int(round(p[1])))
            cv2.circle(v, c, 15, RED, 3, cv2.LINE_AA)
            cv2.line(v, (int(round(points[k][0])), int(round(points[k][1]))), c, RED, 2, cv2.LINE_AA)
        banner(v, tag, tag_color)
        banner(v, f"reproj err  {sol[2]:.1f} px", tag_color, y=104, scale=1.2)
        return v

    left = panel(f, pts, OBJ, "object_points 顺序正确", GREEN)
    right = panel(f, pts, OBJ_BAD, "object_points 点序写反", RED)
    both = np.hstack([cv2.resize(left, (640, 512)), cv2.resize(right, (640, 512))])
    cv2.imwrite(os.path.join(OUT, "s18_order_compare.png"), both)
    cv2.imwrite(os.path.join(OUT, "s31_reproj_compare.png"), both)

    # ---------- slide 23 / 32: 程序运行画面示意 ----------
    # 我们没有 OpenVINO 的 C++ 程序可跑，用真实一帧 + 真实解算数值叠出"画面上会看到什么"
    _i, f, pts, conf, box, t, err = max(frames, key=lambda x: x[3])
    rvec, tvec, _ = solve(pts)
    rvec = np.asarray(rvec).ravel()
    tvec = np.asarray(tvec).ravel()
    Rm, _ = cv2.Rodrigues(rvec)
    yaw = float(np.arctan2(Rm[0, 2], Rm[2, 2]))
    pitch = float(-np.arcsin(np.clip(Rm[1, 2], -1, 1)))
    roll = float(np.arctan2(Rm[1, 0], Rm[1, 1]))
    v = f.copy()
    cv2.rectangle(v, (box[0], box[1]), (box[0] + box[2], box[1] + box[3]), GREEN, 3, cv2.LINE_AA)
    for p in pts:
        cv2.circle(v, (int(round(p[0])), int(round(p[1]))), 9, (0, 0, 255), -1, cv2.LINE_AA)
    lines = [
        f"tvec:  x{tvec[0]: .2f} y{tvec[1]: .2f} z{tvec[2]: .2f}",
        f"rvec:  x{rvec[0]: .2f} y{rvec[1]: .2f} z{rvec[2]: .2f}",
        f"euler angles:  yaw{yaw: .2f} pitch{pitch: .2f} roll{roll: .2f}",
        f"reproj err:  {err:.2f} px",
    ]
    for k, s in enumerate(lines):
        cv2.putText(v, s, (18, 56 + k * 52), FONT, 1.25, (0, 0, 0), 7, cv2.LINE_AA)
        cv2.putText(v, s, (18, 56 + k * 52), FONT, 1.25, YELLOW, 2, cv2.LINE_AA)
    cv2.imwrite(os.path.join(OUT, "s23_s32_runtime_overlay.png"), v)
    sys.stderr.write(f"overlay: tvec={tvec.ravel()} yaw={yaw:.3f} pitch={pitch:.3f} roll={roll:.3f} err={err:.2f}\n")

    sys.stderr.write(f"\nwrote to {OUT}\n")
    for fn in sorted(os.listdir(OUT)):
        sys.stderr.write(f"  {fn}\n")


if __name__ == "__main__":
    main()
