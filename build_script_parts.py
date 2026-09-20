import os
import re
import sys

R = r"C:/Users/ziang.xu/Documents/sp/class_four"
MERGED = os.path.join(R, "output/Lecture4_HelloArmor_逐字讲稿.md")
PARTS = os.path.join(R, "output/script_parts")

src = open(MERGED, encoding="utf-8").read()

# split into: preamble, then one chunk per slide, then trailing
slide_re = re.compile(r"^### 【幻灯片 (\d+)】", re.M)
marks = [(int(m.group(1)), m.start()) for m in slide_re.finditer(src)]
assert len(marks) == 39, f"expected 39 slides, got {len(marks)}"

preamble = src[: marks[0][1]]
chunks = {}
for i, (n, pos) in enumerate(marks):
    end = marks[i + 1][1] if i + 1 < len(marks) else len(src)
    chunks[n] = src[pos:end]

# 结束语 lives inside the last chunk (slide 39) -- keep it there.

SEGMENTS = [
    ("00_opening.md", "开场 + 课程地图", range(1, 3)),
    ("01_p0_review.md", "P0 复习导入", range(3, 7)),
    ("02_p1_why_pose.md", "P1 为什么需要位姿", range(7, 11)),
    ("03_p2_pnp_api.md", "P2 PnP 原理与 API", range(11, 15)),
    ("04_p3_task01_03.md", "P3 上机一（Task 01~03 + 点序陷阱）", range(15, 22)),
    ("05_p4_rvec.md", "P4 rvec 揭秘", range(22, 28)),
    ("06_p5_task04_05.md", "P5 上机二（Task 04~05 + 重投影自查）", range(28, 33)),
    ("07_p6_frames.md", "P6 坐标系全景", range(33, 36)),
    ("08_p7_summary.md", "P7 总结与作业 + Q&A", range(36, 40)),
]

# --- _header.md : preamble with a segment index ---
idx = "\n".join(f"| {fn} | {name} | {r.start}–{r.stop-1} |" for fn, name, r in SEGMENTS)
header = preamble.rstrip() + "\n\n## 分段索引\n\n| 文件 | 分段 | 幻灯片 |\n|---|---|---|\n" + idx + "\n"
open(os.path.join(PARTS, "_header.md"), "w", encoding="utf-8").write(header)

written = []
for fn, name, rng in SEGMENTS:
    body = "".join(chunks[n] for n in rng if n in chunks)
    open(os.path.join(PARTS, fn), "w", encoding="utf-8").write(body)
    written.append((fn, len(body.splitlines()), list(rng)[0], list(rng)[-1]))

# --- verify round-trip ---
reconcat = header.split("## 分段索引")[0] + "".join(
    open(os.path.join(PARTS, fn), encoding="utf-8").read() for fn, _, _ in SEGMENTS
)
norm = lambda s: re.sub(r"\s+", " ", s).strip()
same = norm(reconcat) == norm(src)
sys.stderr.write(f"round-trip identical: {same}\n")
for fn, n, a, b in written:
    sys.stderr.write(f"  {fn:22s} slides {a:2d}-{b:2d}  {n:4d} lines\n")
if not same:
    a, b = norm(reconcat), norm(src)
    i = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), min(len(a), len(b)))
    sys.stderr.write(f"first divergence at char {i}:\n  concat: {a[max(0,i-80):i+80]}\n  merged: {b[max(0,i-80):i+80]}\n")
    sys.exit(1)
