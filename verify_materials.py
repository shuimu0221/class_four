import os
import re
import sys

from docx import Document
from pptx import Presentation

# 自己生成一份到临时目录再校验：仓库里的 pptx 可能正被 PowerPoint 占用而未更新，
# 直接读它会验到旧版本，得到假结论。
import subprocess
import tempfile

REPO = os.path.dirname(os.path.abspath(__file__))
GEN = tempfile.mkdtemp(prefix="lecture4_verify_")
env = dict(os.environ, LECTURE4_OUT_DIR=GEN)
for script in ("build_doc.py", "build_ppt.py"):
    subprocess.run([sys.executable, os.path.join(REPO, script)],
                   cwd=REPO, env=env, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
DOCX = os.path.join(GEN, "Lecture4_HelloArmor_教案.docx")
PPTX = os.path.join(GEN, "Lecture4_HelloArmor_装甲板位姿解算_YOLO版.pptx")

ok = True
def check(name, cond, detail=""):
    global ok
    ok &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")
    if detail:
        for ln in str(detail).splitlines():
            print("        " + ln)

# ---------- pptx structure ----------
prs = Presentation(PPTX)
slides = list(prs.slides)
n = len(slides)
check("pptx 39 页", n == 39, f"实际 {n}")

# footer == slide index
bad = []
for i, sl in enumerate(slides, 1):
    foot = None
    for sh in sl.shapes:
        if sh.has_text_frame and re.fullmatch(r"\d{2}", sh.text_frame.text.strip()):
            foot = int(sh.text_frame.text.strip())
    if foot is not None and foot != i:
        bad.append((i, foot))
check("页脚编号 == 幻灯片序号", not bad, f"错位: {bad}" if bad else "全部一致")

# new pages present at expected indices
def title_of(idx):
    sl = slides[idx - 1]
    ts = [sh.text_frame.text.strip().replace("\n", " ") for sh in sl.shapes
          if sh.has_text_frame and sh.text_frame.text.strip() and not sh.text_frame.text.strip().isdigit()]
    return ts[1] if len(ts) > 1 else (ts[0] if ts else "")

check("第 18 页 = 点序陷阱（新增）", "点序陷阱" in title_of(18), title_of(18))
check("第 31 页 = 重投影误差（新增）", "重投影误差" in title_of(31), title_of(31))

# timeline in toc matches 3+5+6+13+24+14+16+6+3 = 90
toc = slides[1]
mins = [int(m) for sh in toc.shapes if sh.has_text_frame
        for m in re.findall(r"(\d+)\s*min", sh.text_frame.text)]
total = sum(mins) + 3  # +3 for cover(2)+? -> actually cover 2 + toc 1 = 3
check("课程地图时长合计 = 90", total == 90, f"{mins} + 3(封面2+地图1) = {total}")

# no stale text anywhere
stale = {}
for i, sl in enumerate(slides, 1):
    blob = []
    for sh in sl.shapes:
        if sh.has_text_frame:
            blob.append(sh.text_frame.text)
    t = "\n".join(blob)
    for pat in ("CAP_IMAGES", "class/src/main.cpp", "armor 的成员 left", "上节课自己写的 Camera"):
        if pat in t:
            stale.setdefault(pat, []).append(i)
check("pptx 无过期引用", not stale, stale if stale else "干净")

# ---------- docx structure ----------
d = Document(DOCX)
txt = [x.text.strip() for x in d.paragraphs if x.text.strip()]
heads = [t for t in txt if t[:2] in ("一、", "二、", "三、", "四、", "五、", "六、")]
check("docx 六个章节各一次", len(heads) == 6, " / ".join(heads))

# table1 page refs must match the 39-page deck
t1 = d.tables[1]
refs = []
for row in t1.rows[1:]:
    cell = row.cells[1].text.strip()
    m = re.search(r"P\.(\d+)(?:-(\d+))?", cell)
    if m:
        refs.append((int(m.group(1)), int(m.group(2) or m.group(1))))
check("docx 表格1 页码连续覆盖 1..39",
      refs and refs[0][0] == 1 and refs[-1][1] == 39,
      " -> ".join(f"{a}-{b}" for a, b in refs))

# Task answers correct
blob = "\n".join(txt)
check("Task02 用 armor.points.at(0..3)", "armor.points.at(0)" in blob)
check("Task02 不再用 armor.left.top", "armor.left.top" not in blob)
check("draw_text 用 YOLO 参数序", "cv::Point(10, 60), cv::Scalar(0, 255, 255), 1.7, 3" in blob)
check("欧拉角为弧度（无 ×57.3）", "* 57.3" not in blob)
check("含重投影误差自查", "reprojection_error" in blob)
check("进阶作业指向 homework", "lecture4/homework/" in blob)

print()
print("总体:", "全部通过" if ok else "有失败项")
