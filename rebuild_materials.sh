#!/usr/bin/env bash
# 重建 Lecture 4 的全部教学产物。
#
#   ./rebuild_materials.sh
#
# 产物：
#   Lecture4_HelloArmor_教案.docx
#   Lecture4_HelloArmor_装甲板位姿解算_YOLO版.pptx
#   output/Lecture4_HelloArmor_逐字讲稿.md  与 output/script_parts/*
#   lecture4/yolo/docs/ppt_images/*（仅在显式传 --images 时重跑）
#
# 依赖：python3 + python-docx + python-pptx（生成 docx/pptx）
#       pillow（概念示意图）；opencv-python + openvino（从视频抽帧的真图）
#
# ⚠ 生成 pptx 前请先关闭 PowerPoint —— 文件被占用时会 PermissionError。

set -euo pipefail
cd "$(dirname "$0")"

PY=${PY:-python}

echo "==> 1/4 教案 (docx)"
"$PY" build_doc.py

echo "==> 2/4 课件 (pptx)"
"$PY" build_ppt.py

echo "==> 3/4 讲稿分段（从合并稿切分，保证两处副本一致）"
"$PY" build_script_parts.py

echo "==> 4/4 讲稿上下文包（从 docx/pptx/yolo 源码重建）"
"$PY" build_context.py

if [ "${1:-}" = "--images" ]; then
  echo "==> 附加：重新生成配图"
  "$PY" build_ppt_images.py       # 需要 opencv-python + openvino
  "$PY" build_ppt_diagrams.py     # 需要 pillow
  echo "    （配图变了，重跑一次 build_ppt.py 才能进 PPT）"
  "$PY" build_ppt.py
fi

echo
echo "==> 校验"
"$PY" verify_script.py
"$PY" verify_materials.py

echo
echo "完成。请用 git diff 复核 docx/pptx —— 它们曾经落后于生成脚本，反向对账过一次。"
