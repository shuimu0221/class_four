import re
import sys

P = r"C:/Users/ziang.xu/Documents/sp/class_four/output/Lecture4_HelloArmor_逐字讲稿.md"
src = open(P, encoding="utf-8").read()
lines = src.splitlines()

ok = True
def check(name, cond, detail=""):
    global ok
    ok &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")
    if detail:
        for ln in str(detail).splitlines():
            print("        " + ln)

# --- headings ---
heads = [(int(m.group(1)), m.group(2).strip(), m.group(3))
         for m in re.finditer(r"^### 【幻灯片 (\d+)】(.+?)　⏱ (.+)$", src, re.M)]
nums = [h[0] for h in heads]
check("39 个幻灯片标题", len(heads) == 39, f"实际 {len(heads)}")
check("编号连续 1..39", nums == list(range(1, 40)),
      f"missing={[i for i in range(1,40) if i not in nums]} dup={[n for n in set(nums) if nums.count(n)>1]}")

# --- section time sums ---
def mins(s):
    m = re.match(r"([\d.]+)\s*分钟", s)
    return float(m.group(1)) if m else None

SECTIONS = {
    "00 开场+地图": (1, 2, 3.0),
    "01 P0": (3, 6, 5.0),
    "02 P1": (7, 10, 6.0),
    "03 P2": (11, 14, 13.0),
    "04 P3": (15, 21, 24.0),
    "05 P4": (22, 27, 14.0),
    "06 P5": (28, 32, 16.0),
    "07 P6": (33, 35, 6.0),
    "08 P7": (36, 39, 3.0),
}
total = 0.0
for name, (a, b, want) in SECTIONS.items():
    got = 0.0
    detail = []
    for n, title, t in heads:
        if a <= n <= b:
            v = mins(t)
            if v is None:
                detail.append(f"slide {n}: 非数值时长 {t!r}")
                continue
            got += v
            detail.append(f"{n}:{v}")
    total += got
    check(f"{name} 各页之和 = {want}", abs(got - want) < 1e-6,
          " ".join(detail) + f"  => {got} (want {want})")

check("九段合计 = 90", abs(total - 90.0) < 1e-6, f"实际 {total}")

# --- stale refs (excluding intentional "don't do this" warnings) ---
# These patterns legitimately appear when the script is warning students NOT to
# use them, or when it names the old program to contrast against it.
INTENTIONAL = [
    "不再讲授",          # names lecture4/class as the retired version
    "不要用 armor.left",  # warning
    "不要。**",           # warning
    "你要是写 `armor.left.top`",   # warning
    "你是不是写了 `armor.left.top`",  # 巡场 warning
    "我用了 armor.left.top",        # Q&A warning
    "与 lecture4/class/ 版正好相反", # contrast note
    "是不是应该从",              # rhetorical warning
    "改用 `armor.points",         # the fix right after the warning
]
STALE = {
    "lecture4/class": "应指向 lecture4/yolo",
    "class/src": "旧路径",
    "CAP_IMAGES": "旧报错",
    "阈值 170": "旧巡场话术",
    "纯灯条法": "旧检测器描述",
    "2.01": "原课终端数值",
    "6.40": "原课终端数值",
    "Hello OOP": "旧课程编号",
    "上节课自己写": "旧作业措辞",
}
found = {}
for pat, why in STALE.items():
    hits = []
    for i, l in enumerate(lines):
        if pat not in l:
            continue
        if any(k in l for k in INTENTIONAL):
            continue
        hits.append(i + 1)
    if hits:
        found[pat] = (why, hits[:5])
check("无过期引用（已排除有意的对照/警告语）", not found,
      "\n".join(f"{k} ({v[0]}) @ 行 {v[1]}" for k, v in found.items()) or "干净")

# armor.left/right may only appear inside warning context
bad_left = []
for i, l in enumerate(lines):
    if ("armor.left" in l or "armor.right" in l) and not any(k in l for k in INTENTIONAL):
        bad_left.append(i + 1)
check("armor.left/right 只出现在警告语境", not bad_left, f"可疑行: {bad_left}")

# 七条/八条: only as part of 第七条/第八条
bad_seven = [i + 1 for i, l in enumerate(lines)
             if re.search(r"(?<![第])七条", l) or "七条对完" in l]
check("回顾条数口径为八条", not bad_seven, f"可疑行: {bad_seven}")

# --- required new content ---
must = {
    "armor.points.at(0)": "Task02 新答案",
    "`.at(3)`": "Task02 新答案",
    "cv::Scalar(0, 255, 255), 1.7, 3": "draw_text 新参数序",
    "reprojection_error": "重投影自查",
    "YAML::BadFile": "新报错",
    "lecture4/yolo": "新工程路径",
    "lecture4/homework": "进阶作业 B",
    "空格": "空格暂停",
    "Hello Kalman": "下一讲",
    "左手": "占位",
}
for pat, why in must.items():
    if why == "占位":
        continue
    n = src.count(pat)
    check(f"含 {pat!r} ({why})", n > 0, f"出现 {n} 次")

print()
print("总体:", "全部通过" if ok else "有失败项")
sys.exit(0 if ok else 1)
