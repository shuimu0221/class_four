# Armor::points 的真实顺序 —— 一个会坑死人的注释

## 结论

`auto_aim::Armor::points` 的顺序是 **左上、右上、右下、左下**（自左上顺时针），
即 `[TL, TR, BR, BL]`。

## 但是注释是反的

`tasks/armor.hpp` 里写着：

```cpp
std::vector<cv::Point2f> points;  // 关键点的图像坐标，顺序为左上、左下、右下、右上
```

**这条注释是错的。** 实际顺序是左上、右上、右下、左下。注释保留原样，是为了和
lecture2 作业发到同学手上的那份代码保持一致 —— 请不要"顺手改掉"，它是本讲的一个教学点。

## 怎么证明

用 `docs/verify_keypoint_order.py`（复刻 `tasks/yolos/yolov5.cpp` 的取点逻辑）在
`assets/video.avi` 上抽帧统计：

1. **把 4 个点按顺序编号画到图上**，肉眼可见 `0:左上 1:右上 2:右下 3:左下`。
2. **几何一致性**：31/31 帧同时满足
   `p0.y < p3.y`、`p0.x < p1.x`、`p1.y < p2.y`、`p3.x < p2.x`，零违例。
3. **尺寸比**：图像上"上边 / 左边"的像素长度比均值约 **2.5**，而 `object_points` 蕴含
   `ARMOR_WIDTH / LIGHTBAR_LENGTH = 0.135 / 0.056 = 2.41`，偏差约 3%。
   这说明四边形上边对应装甲板宽度、左边对应灯条长度 —— 尺寸对应关系成立。

## 为什么会错

`tasks/yolos/yolov5.cpp` 里是这样取点的：

```cpp
armor_key_points.push_back(cv::Point2f(output.at<float>(r, 0) / scale, output.at<float>(r, 1) / scale));
armor_key_points.push_back(cv::Point2f(output.at<float>(r, 6) / scale, output.at<float>(r, 7) / scale));
armor_key_points.push_back(cv::Point2f(output.at<float>(r, 4) / scale, output.at<float>(r, 5) / scale));
armor_key_points.push_back(cv::Point2f(output.at<float>(r, 2) / scale, output.at<float>(r, 3) / scale));
```

也就是对模型的原始 4 个关键点做了 `[0, 3, 2, 1]` 的置换 —— 一个 `swap(1, 3)`。

问题在于：**yolov5 这个模型的原生输出顺序已经是「左上、左下、右下、右上」**，
这个 swap 恰好把它拧成了「左上、右上、右下、左下」。

同样的 `swap(1, 3)` 在队内参考实现 `sp_vision_26/tasks/auto_aim/yolos/yolov8c.cpp` 里是**对的** ——
因为 **yolov8c 的原生顺序和 yolov5 正好相反**。两处代码长得一样、结论相反，很容易踩。
（`yolov5.cpp` 这段极可能是从 `yolov8c` 抄过来时没有改。）

## 为什么代码是对的、只有注释错

`tasks/armor.cpp` 的**传统**构造函数（由两根灯条构造）给出：

```
ratio = 装甲板宽 / 灯条长 ≈ 0.135 / 0.056 ≈ 2.41
```

而 **YOLO** 构造函数算的是 `ratio = max_length / max_width`。
只有在点序为 `[TL, TR, BR, BL]` 时，`max_length` 才是装甲板宽、`max_width` 才是灯条长，
结果才等于 2.41；若按注释那个顺序，会得到 0.41。

**所以代码行为与 `[TL,TR,BR,BL]` 自洽，只有注释（以及 `left_width` / `top_length`
这组变量名）是陈旧的。**

## 对你的影响

`object_points` 必须按 **左上、右上、右下、左下** 排：

```cpp
static const std::vector<cv::Point3f> object_points{
    {-ARMOR_WIDTH / 2, -LIGHTBAR_LENGTH / 2, 0},  // 点1 左上
    { ARMOR_WIDTH / 2, -LIGHTBAR_LENGTH / 2, 0},  // 点2 右上
    { ARMOR_WIDTH / 2,  LIGHTBAR_LENGTH / 2, 0},  // 点3 右下
    {-ARMOR_WIDTH / 2,  LIGHTBAR_LENGTH / 2, 0}   // 点4 左下
};
```

物体系：`+x` 向右、`+y` 向下，四点共面 `z = 0`。

## 怎么自查

如果 `object_points` 和 `img_points` 的顺序没对上，解出来的位姿会**有数、但完全不对**，
而且看着不像报错，极难发现。用**重投影误差**一眼就能看出来：

把 `object_points` 用解得的位姿投影回图像，和检测到的 `img_points` 比距离。
顺序正确时约 **2~3 px**；顺序写反（比如镜像）会暴涨到几十像素以上。

参考实现在画面上直接把这个误差画出来（`answer/main.cpp` 的 `reproj err` 一行），
工具函数在 `tools/pnp_check.hpp`。

## 换模型时怎么办

上面所有结论都是针对**当前这一份 `assets/yolov5.xml`** 得出的。如果你换了模型、
或者不确定 lecture2 实际分发的是哪一份，直接跑：

```bash
cd lecture4/yolo
python docs/verify_keypoint_order.py
```

它会打印实际的点序统计和四条不等式校验结果，退出码 0 表示仍是「左上、右上、右下、左下」。
若顺序变了，`object_points` 的点序要跟着改。
