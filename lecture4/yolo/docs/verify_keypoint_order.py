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
