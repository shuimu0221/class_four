# Lecture 4 教学材料审计报告 —— 对照 YOLO 版程序

日期：2026-09-20
状态：待用户拍板（见 §8 待决策问题）

## 0. 这份文档是什么

`lecture4/yolo/`（基于 YOLO 的新版教学程序）已实现完毕。本报告审计现有的全套教学材料
——教案 docx、两份 PPT、逐字讲稿、历史视频笔记——**假设 YOLO 版成为课堂上实际讲授的那一版**，
逐条找出会变成错的、过时的、或者缺失的内容。

**怎么用**：§2 是必须先做的前置闸门；§3 按「不改会出什么事」排序，从上往下做；
§8 的决策必须先拍板，它影响每一条的落地方式。

**审计方法**：11 份材料并行分析 → 每份的全部发现由「事实核查」与「教学影响」两个
独立视角批量核验（事实视角是准入门槛，影响视角调整严重度并可否决）→ 跨材料合并去重 →
完整性批判。76 条原始发现中 73 条通过核验。

**其中两条由人工独立验证过**（非 agent 结论）：

- Task02 的 `armor.left/right` 问题：`grep` 确认 `left(left), right(right)` 只出现在
  `tasks/armor.cpp:35` 的传统构造函数，YOLOV5 用的构造函数（`armor.cpp:148`）不初始化它们
- `draw_text` 参数顺序：直接比对两版 `tools/img_tools.hpp` 的签名确认

---

## 1. 总判断

需要改，且改动量很大：73 条存活发现合并后归为 6 个阻断级根因 + 10 个重要项。教案、主 PPT、逐字讲稿三份核心材料全部 yes-heavy（讲稿最重，约 40 处锚点）；两个生成脚本在改之前先得修好自己（输出路径已失效、且都落后于各自成品）；半成品 PPT 的改动量取决于一个尚未拍板的模板决策。

---

## 2. 阻断级问题（BLOCKER）

> 第 1 条是**前置闸门**：不先做掉它，后面所有「改 build_doc.py 第 N 行」类的改动都落不了地。

### B1. 【前置闸门】两个生成脚本现在跑不起来，且都已落后于各自成品——先修脚本，再谈内容

**位置**：build_doc.py:266 与 build_ppt.py:610（输出路径写死为 C:\Users\ziang.xu\Documents\class_four\，缺 sp\ 一级，目录已不存在）；build_doc.py:203-208/223-237/176-183 落后于已发布的 Lecture4_HelloArmor_教案.docx（[p0028] object_points、[p0034]/[p0036] draw_text、[p0036] 弧度注、表格1 整列 PPT 页码）；build_ppt.py:467/261 落后于 37 页成品 pptx（Task01「请用 ± ARMOR_WIDTH/2 表达式填写，模板已被注释，先解注释再填」这句只在成品里；P7 成品 3 min vs 脚本 4 min）

**问题**：两条独立失效叠在一起。(1) 脚本一执行就 FileNotFoundError（save 到不存在的目录，WinError 3），本轮所有「改 build_doc.py:211 / build_ppt.py:451」类建议一条都落不了地。(2) 就算修好路径直接重跑，会把成品里已有的手工修正静默抹掉——最要命的是 build_ppt.py:467 丢失的那句是 Task01 唯一一条操作指令（学生版 src/main.cpp:29-33 的模板整段是注释掉的，不解注释无从下手），以及教案表格1 的 PPT 页码会整表回退到与现行 37 页系统性错位的旧编号（不止已知 3 处，P1 起每行差 1~2 页，教师照表翻页全程翻错）。已知漂移只有这几处，是因为只抽查了这几处，并未逐页比对。

**改法**：严格按此顺序：①两个脚本的 out_path 改为 os.path.join(os.path.dirname(os.path.abspath(__file__)), "...")，并加一行 assert os.path.isdir(os.path.join(HERE,"lecture4")) 防止被拷到别处安静生成；②机械对账：用 python-pptx / python-docx 把现成品全文抽出，再把脚本生成一份到临时路径，两份 diff，把所有「成品有、脚本没有」的片段补回脚本；③对账唯一的例外是 docx 的 [p0034]/[p0036] 三处 draw_text——那三处本身就是坏的（见 blocker 4），不要回流，直接按 YOLO 签名重写；④对账完成后再开始 YOLO 版内容改动；⑤把生成的 docx/pptx 纳入 git 跟踪，脚本末尾 print 一句提示 git diff 复核。

### B2. 全套材料把学生和教师指向 lecture4/class/——会整堂课跑在旧工程上，而且全程没有任何错误信号

**位置**：逐字讲稿第 5、464、486、612、618、629、631、633、885 行（8 处路径 + 一句「tasks/ 下的 Detector 上节课我们已经写好了」）；build_ppt.py:448「项目结构：class/src/main.cpp 是你要填空的文件；tasks/ 下的 Detector 已经帮你写好」（幻灯片16）；build_doc.py:112 表格0「配套代码 = LECTURE4 工程（class/ 学生填空版 + answer/ 参考答案版）」、:178 学生活动「打开 LECTURE4 工程」、:246 教具清单「class/ 与 answer/ 两份提前拷到桌面」；armor_lecture_notes.md:50-69 的目录树

**问题**：这是唯一一条能让其余全部修复整体归零的路径。lecture4/class/ 与 lecture4/answer/ 在仓库里真实存在、与这些描述严丝合缝、自身可编译可运行、答案也自洽——教师照做不会遇到任何阻力，会顺利教完一整节旧课，现场没有任何信号提示拷错了。同时 YOLO 版的 tasks/ 下根本没有叫 Detector 的类（只有 auto_aim::YOLO，且必须带 "configs/yolo.yaml" 构造），按图索骥的学生会找不到文件。

**改法**：全篇一次性批量替换，禁止部分替换（会造成「P3 说 yolo/、P5 说 class/」的版本分裂，比全错更糟）。讲稿 464 行整段改为「打开 lecture4/yolo，所有填空都在 src/main.cpp 一个文件里；tasks/ 下的 YOLO 检测器是你们 lecture2 作业里那一份，一个字没改」；486 行〔操作〕写全「打开 lecture4/yolo/src/main.cpp，光标停到 Task01 注释处（约 23 行）」。build_ppt.py:448 拆成两条 bullet（填空文件 + auto_aim::YOLO 构造调用 / configs、assets、io、answer、docs 目录说明）。build_doc.py:112 写成两行（class/ 一行、yolo/ 一行）并加可执行自检：「拷贝后确认目录下有 configs/ 与 assets/；若看到 class/ 与 answer/ 并列则是拷错了版本」；:246 用同一套措辞，避免两处说法不一致。注意 build_ppt.py:448 与 :450（见 blocker 3）在同一个 slide_content(447-452) 调用里，一次编辑改完。

### B3. Task02 标准答案用 armor.left/right——YOLO 版拿到四个 (0,0)，程序当场崩或解出垃圾位姿

**位置**：【代码答案】教案 [p0030] / build_doc.py:211-216；主 PPT 幻灯片18 提示「看看 Armor 结构体有哪些成员；left 和 right 是两根灯条」/ build_ppt.py:469-486；讲稿 552/554/556（老师明令「我的要求是——你自己从 armor.left / armor.right 里挑」）、562、571；armor_lecture_notes.md:124-125、129、333。【上游铺垫，同批必改】主 PPT 幻灯片5 / build_ppt.py:382-387；幻灯片16「1=左灯条上端」/ build_ppt.py:449-450；教案 P0 导入 t1r3 / build_doc.py:175；讲稿 143/147/155、337、472、476、657；armor_lecture_notes.md:7 的 Scope note（把 .left/.right 写进「代码已假定存在」，是生成脚本抄错的源头）；半成品 slide3（缺 4 点来源交代，补写时禁止照抄生成版第 5 页的灯条说法）

**问题**：tasks/armor.cpp:148 起的 YOLOV5 构造函数只初始化 confidence/box/points，left/right 走 armor.hpp:88 的 Lightbar(){} 默认构造，四个 cv::Point2f 全是 (0,0)。结构体里仍有这两个成员，所以旧答案能编译通过，失败纯在运行期——这正是它比编译错误更危险的原因。四点重合是退化输入：大概率 cv::solvePnP 抛 cv::Exception，而两个 main 都没有 try/catch，进程直接 terminate（现象是一跑就闪退 + 终端一行 terminate called after throwing）；也可能返回数值巨大的 rvec/tvec。更坑的是 src/main.cpp:62 的 draw_points 在 Task02 之前执行，照常把 4 个真实关键点画在装甲板上——学生看到点标得好好的，几乎不可能自己定位到 img_points 上。上游铺垫必须同批改：P0 讲了灯条配对、幻灯片5 讲了 left/right→4 点，学生写 armor.left.top 是被教出来的，不是猜错的。

**改法**：答案统一改为 armor.points.at(0)~at(3)（与 answer/main.cpp:59-63 逐字一致，注释保留「左上/右上/右下/左下」），不要并列两版代码块（并列正是教师拷错版本的来源），只留 YOLO 版 + 一句「class/ 版此处为 armor.left.top 等四项，本讲不使用」。上游同步改：幻灯片5 改为「detect 返回 Armor 列表 → Armor.points 是 YOLO 直接回归的 4 个关键点，YOLO-pose 端到端、没有中间的灯条步骤；Armor 里虽然还留着 left/right，走 YOLO 这条路从未被赋值，全是 (0,0)，是历史包袱」；幻灯片16 的「1=左灯条上端」改为「points[0]=左上…」但保留实物锚点（「物理上就是左灯条顶端，但程序里没有『左灯条』这个对象」）；教案 P0 导入改为衔接 lecture2 的 YOLO 作业，并建议教师当场翻 tasks/armor.cpp:148 的初始化列表给学生看（比口头断言有说服力，顺带示范「看构造函数判断哪些成员有效」）。教师预警话术要写实症状：「画面上点画对了但程序一跑就崩/数值乱跳 = 你填的是 left/right，不是 points」。armor_lecture_notes.md:7 与 :129 就地加括注（横幅式提醒挡不住会被脚本当事实抄走的具体断言）。

### B4. tools::draw_text 参数顺序反了——Task04/Task05 共 3 处调用在 YOLO 版编译不过

**位置**：已发布的 Lecture4_HelloArmor_教案.docx [p0034]、[p0036]（产物本身就是坏的，不是「旧版待更新」）；build_doc.py:223-226、236-237（当前是 3 参数旧写法，属前置对账范围）；逐字讲稿 895-898（幻灯片28 Task04 代码块）。不涉及主 PPT：build_ppt.py:552/555/567 把实参省略成了 `), ...);`，顺序差异未暴露

**问题**：yolo/tools/img_tools.hpp:21-23 的签名是 (img, text, point, color, font_scale, thickness)——color 在 font_scale 之前；class/tools/img_tools.hpp:29-31 正好相反。照材料写，第 4 个实参 1.7 会被 cv::Scalar_(_Tp v0) 悄悄吞成 Scalar，第 5 个实参 cv::Scalar(0,255,255) 没有到 double 的转换路径，GCC 报 cannot convert 'cv::Scalar' to 'double' + no known conversion for argument 5。Task04/05 三处全中，16 分钟的实验二会全班卡在同一个看不懂的模板错误上。讲稿那处还有次生伤害：第 893 行说「你现在看到的是这个」，而学生文件里是另一种排列，会当场怀疑打开错了版本。

**改法**：统一改为 cv::Point(10, 60), cv::Scalar(0, 255, 255), 1.7, 3（与 answer/main.cpp:72-73、82 一致）。提示 para 放在教案第三节开头（紧跟「请教师课前自行验证工程可编译运行」之后），不要只放 Task04 标题下（Task05 也中招）：「本讲 draw_text 的参数顺序是 (img, text, point, color, font_scale, thickness)，与 lecture4/class/ 版相反；写反会在第 5 个实参上报 cannot convert cv::Scalar to double」。讲稿在代码块正下方加括注并补一句止损指令：「你不需要动这几个参数，只改 fmt::format 里的三个 0.0」——这是本条性价比最高的一笔。

### B5. 课前环境清单缺 OpenVINO 2024.6.0 等新依赖——上课当天 cmake 第一步就失败，现场零补救余地

**位置**：教案表格0 第3行 t0r2「教具/环境」/ build_doc.py:111（只写了 OpenCV4+CMake，连 class/ 版必需的 fmt 都没列）；主 PPT 幻灯片20 / build_ppt.py:496-501（未提任何新依赖）；逐字讲稿 460-466（整段叫「实验环境」，却只讲了动哪个文件）、661-667（巡场话术库只有「编译不过」卡点，没有「cmake 配置失败」分支）

**问题**：yolo/CMakeLists.txt:9-19 要求 OpenCV / fmt / Eigen3 / yaml-cpp / spdlog / OpenVINO，第 18 行把 OpenVINO 路径写死为 /opt/intel/openvino_2024.6.0/runtime/cmake。按现清单准备镜像，cmake -B build 会在第 11 行起的 find_package 串上依次失败（最先卡 Eigen3），全班一行代码跑不了——而 OpenVINO 装一次要几十分钟，是课堂上绝对补不回来的。巡场话术教的「报错先看第一行、查分号」对 CMake Error 完全不沾边。

**改法**：build_doc.py:111 改为完整清单并标出唯一可调点：「CMake ≥ 3.16、OpenCV4、fmt、Eigen3（Ubuntu 下 libeigen3-dev，CMakeLists.txt:21 用 ${EIGEN3_INCLUDE_DIR}，conda 版容易找不到）、yaml-cpp、spdlog、OpenVINO 2024.6.0（装在别处只改 CMakeLists.txt:18 的 set(OpenVINO_DIR ...) 一处）、HikRobot 相机需 MVS SDK 且 -DWITH_HIKROBOT=ON」，并注明 CMakeLists.txt:7 把 CMAKE_BUILD_TYPE 写死为 Debug、OpenVINO 推理在 Debug 下明显更慢，课堂帧率低是正常现象。教具清单验收标准写成可勾选：「课前在镜像里 cd lecture4/yolo && cmake -B build && cmake --build build -j，确认生成 build/main 与 build/answer，再跑 ./build/answer 确认出图且 reproj err 在 2~3 px」——只验编译不验运行，模型/视频问题仍会在课堂上第一次暴露。build_ppt.py:496-501 同步补依赖行与 cd 行。讲稿在 462 行之前插 30 秒环境确认，并给一条比 ls /opt/intel/... 更准的自检命令 cmake -B build 2>&1 | tail -3（Eigen3/yaml-cpp/spdlog 缺失的报错与 OpenVINO 完全不同）；巡场话术库新增一条排在最前的卡点「cmake -B build 就过不去」，含三个分支：分清 CMake Error（配置期，别改 main.cpp）/ OpenVINO 路径改一处 / 缺依赖别把 find_package 注释掉，另加运行期 error while loading shared libraries: libopenvino.so.* → source setupvars.sh。强调这段必须课前完成、课上只做 30 秒确认——把 OpenVINO 安装塞进 20 分钟上机不现实。

### B6. Hello Armor&Solver.pptx 的 34 页正文与全部 37 份备注仍是 Lecture3 原文

**位置**：Lecture4 Hello Armor&Solver.pptx：slide2、slide5~slide37 与 Lecture3 逐页字节相同（仅 slide1/3/4 被改过）；notesSlides 1~37 全部字节相同，其中约 20 页带 Lecture3 实质口播（第 1 页备注写着「第三次培训…本次课程主要会讲 OOP 相关」，而 slide1 正文已改成「Hello Armor / 第四次培训」）；重灾点：slide2 目录页（宣告本课讲 CMake 和 OOP）、slide37 作业页（布置的是上一讲的作业）

**问题**：全文检索本讲核心术语命中数全部为 0：PnP=0、solvePnP=0、rvec=0、tvec=0、Rodrigues=0、欧拉角=0、Task=0、位姿=0、坐标系=0。拿这份上课，90 分钟里 34 页在重讲上一讲，本讲要教的 solvePnP 一个字都讲不到。主讲人若开演讲者视图，开场第一句就自报「第三次培训，本次主要讲 OOP」，与投影上的「Hello Armor / 第四次培训」当场打架；最后一页把上一讲的作业当本讲作业布置，学生课后根本不会去碰 solvePnP。

**改法**：取决于 openQuestions 第 2 条的模板决策（先定模板再搬文字，否则做两遍）。若选它作承载模板：①先做三个可独立完成的小动作——第 1 页备注重写、slide2 目录页换成本讲 8 段路线图（P0 7/P1 7/P2 14/P3 20/P4 14/P5 16/P6 6/P7 3 min）、slide37 作业页改成本讲三档作业；这三页不依赖整体替换，且矛盾最刺眼/影响最久。②再用生成版 37 页文字替换第 5~37 页中的 33 页，**显式豁免 slide33 并前移到 P0**（「传统：先找灯条→判断→识别数字 vs YOLO*：丢进图片直接输出 id + 4 个关键点」，是这 34 页里唯一对 YOLO 版有正面价值的一页；写成「整体替换 34 页」执行者会连它一起删）。③搬运时挂两条禁令：生成版第 5 页的 left/right 灯条说法禁止原样搬运（见 blocker 3）、第 36 页作业②「接入自己写的 Camera+Detector」禁止原样搬运（见 major 4）。④36 页备注用逐字讲稿对应【幻灯片 N】小节机械灌入（页码口径一致：P0=3-6…P7=34-37），只有第 1 页开场白需人工写。⑤评估删掉 media1.mp4（30MB 体积主因，与本讲无关）。

---

## 3. 重要问题（MAJOR）

### M1. 「转动装甲板实时观察」全线落空——两版程序默认都只播录像

**位置**：逐字讲稿 711/713/715/717/721/734/740/748（幻灯片22 P4 核心实验）、922（Task04 唯一验收标准第二条「拿手把装甲板往前推一推」）、983/985/989/991/993/1009/1011（幻灯片30 P5 互动，含「请同学上台自己动这块板子」）；教案 t1r7/t1r8 / build_doc.py:179-180；主 PPT / build_ppt.py:506；历史笔记 pnp_lecture_notes.md:176、179-187

**问题**：configs/yolo.yaml:19 默认 source: video 读 assets/video.avi、loop: true；切真相机要同时改 yaml + -DWITH_HIKROBOT=ON 重新配置 + 装 MVS SDK，否则 io/camera.cpp:31-34 直接抛异常。class/ 版更没得选（src/main.cpp:42 写死 VideoCapture）。老师举着装甲板转，画面数字跟他的手毫无关系；学生按 922 行「推一推」发现没反应，会怀疑自己 Task03 写错，产生假故障、白占巡场时间。关键是 io/camera.cpp 只有 video 与 HikRobot 两条路径，没有普通 USB 摄像头入口——class/ 版改成 cap(0) 还能用笔记本摄像头交差，YOLO 版反而变成硬件门槛题。

**改法**：全部改成 A（默认，零门槛）+ B（可选旁注）两档，且必须一次改完所有锚点——只改主干不改应答分支会出现「前面说看视频、后面又说我再转一点」。A：video.avi 本身就是手持数字「2」的装甲板在动（752 帧/30fps≈25 秒循环），把「我转这块板子」改成「我们一起盯着视频里那只手」；「转三四个来回」改成「视频 25 秒循环一次，等它转回来再看一遍」；「把视频拖到某几帧」改成「等它转回到他往前推的那几秒」——程序没有暂停/拖拽能力（src/main.cpp:114-117 只有 waitKey(20) 和 q 退出，video_camera 读完自动 seek 回 0），照「拖」操作教师会当场卡壳。零成本补回体感闭环：让学生遮挡装甲板一角、或对比 tvec.z 与画面里装甲板的视觉大小。922 行验收标准改为可现场验证的三条性质（z 在 0.2~0.7 之间、跟着画面里的手连续变、不乱跳），不要写死「大概 1 米」这类未实测数字。B：旁注写明「若教师机课前已验证过接得上 hikrobot 相机」，并提示换相机后内参不匹配会让 reproj err 从 2~3 px 暴涨，老师若不预先知道会误以为是点序错了。教案里明确写出退路：「相机一路随时可弃，切回 source: video 即可继续上课，不影响任何 Task」。

### M2. 现场调试演示的报错文本对不上——照稿念会当场穿帮，且归因教错

**位置**：逐字讲稿 620-629（〔演示〕cd 进 build/ 让 CAP_IMAGES 报错刷出来 + 629 行归因「video.avi 在项目根目录」）；主 PPT 幻灯片20 / build_ppt.py:499-500；教案 t1r6 / build_doc.py:178「讲解 video.avi 找不到的经典报错」；armor_lecture_notes.md:157-169

**问题**：YOLO 版第一个碰相对路径的不是 VideoCapture 而是 src/main.cpp:45 的 auto_aim::YOLO detector("configs/yolo.yaml")，走 tasks/yolo.cpp:11 的裸 YAML::LoadFile（不是会打日志再 exit 的 tools::load），main 无 try/catch → 未捕获的 YAML::BadFile 导致 terminate，根本走不到 io::Camera。屏幕上是 terminate called after throwing an instance of 'YAML::BadFile' / what(): bad file: configs/yolo.yaml / Aborted (core dumped) 三行，学生按 PPT 搜 CAP_IMAGES 什么也搜不到。这一环恰恰是材料写明要「通过报错培养调试能力」的设计，教学效果直接归零。附带问题：教学价值也下降了——CAP_IMAGES 对新手可读，YAML::BadFile 不含「找不到」字样，新手推不出根因。

**改法**：报错分两条写：①跑错目录 → YAML::BadFile（三行照实抄），解决 cd 回 lecture4/yolo；②目录对了但 assets 缺失 → Failed to open video: assets/video.avi（io/video_camera.cpp:17-20）。课前必须在 Linux 构建机上实跑 cd lecture4/yolo/build && ./main 把真实输出抄进材料——不要留推导出来的报错文本，那正是本条要修的错误本身；讲稿该处先加编者注〔待实测替换〕。归因要讲清「为什么第一个报错是模型不是视频：报错顺序反映的是构造顺序」，这本身是很好的调试教学点。相对路径依赖是四样不是三样：configs/yolo.yaml、assets/yolov5.xml、assets/video.avi、logs/（tools/logger.cpp:17 建 basic_file_sink，CMakeLists.txt:30 在源码树建 logs/）。另建议把 io/camera.cpp:31-34 那条自带解法的异常拿来做正面教材，对比讲「好的错误信息长什么样」。可选加强：给 tasks/yolo.cpp:11 包一层 try/catch 转成「请确认你在 lecture4/yolo/ 目录下运行」，把这个教学点的可读性补回来。

### M3. 讲稿把 rvec 说成「终端滚动的 2.01→6.40」——与画面上的零点几量级差两个数量级

**位置**：逐字讲稿 697、711、713、717、719（「终端里那一列数一直在往上滚」「从 2.01 一直慢慢涨到 6.40」）、769（「这正好解释了刚才那个数从 2.01 一路涨上去的现象」）；素材源 output/script_parts/_context.md:411；同文 script_parts/05_p4_rvec.md:5/19/21/25/27/77

**问题**：两版程序都不往终端打 rvec/tvec，只用 draw_text 画在 imshow 窗口上（数值原地刷新，不滚动）；全目录 grep std::cout / fmt::print / printf 零命中。老师按 697 行把投影切到终端，只会停在一条 VideoCamera 启动日志然后一片空白。数值也对不上：本讲程序打印弧度且不乘 57.3（讲稿 849 行自己也这么说），实测 yaw ±0.22 / pitch ±0.07 / roll ±0.33 rad，屏幕上是「0.18」这种数。719 行带「原视频课演示到这个环节时」的限定语，属转述；769 行用「刚才」把旧课数值冒充成学生本节课的观察，是最硬的一处错。

**改法**：L719 是三条发现共同的落点，只改一次、一次做完四件事：终端→画面左上角、去掉「往上滚」改「原地刷新」、删掉 2.01/6.40、补「都是零点几这种小数（单位弧度），你们只看哪一个在明显地动」。769 行删掉整个回指半句。697 行〔操作〕写死 cd lecture4/yolo && ./build/answer。在 _context.md:411 就地标注「原视频课口播数值（疑为角度制的 roll），本讲程序打印弧度、实测零点几——重新生成讲稿时不得引用」，堵死回流路径。改稿理由要写准：不要写「6.40 物理上不可能」（对 rvec 成立、对角度制的 roll 不成立），只写「本讲打弧度、实测零点几」。

### M4. 进阶作业失效：让学生去接一个他从来没写过的 Detector，而真正要做的事一个字没提

**位置**：逐字讲稿 1148 / script_parts/08_p7_summary.md:45；build_ppt.py:605（幻灯片36 课后作业②）；build_doc.py:256（教案五、作业布置②）；上游前提在讲稿 46、102、464 行

**问题**：三个前提全不成立：(1) io::Camera 已由工程提供（src/main.cpp:46 直接构造）；(2) 学生从来没写过 Detector——lecture2 作业里留空的只有 io/camera.{hpp,cpp}（0 字节），tasks/yolo.cpp 与 yolos/yolov5.cpp 是随作业发下去的成品，class/tasks/detector.cpp 也是成品，所以这半句对两版都是假话；(3)「跑真实摄像头」已不是编程任务而是配置 + CMake 开关，而且没有 USB 摄像头入口，多数学生做不了。

**改法**：改成二选一并明确 A 有条件、B 保底：A（需 HikRobot）三步走——-DWITH_HIKROBOT=ON 重新配置 / 改 source: camera / 用自己标定的内参替换 main.cpp 顶部的 camera_matrix 与 distort_coeffs（这才是真正剩下的有效工作量，README.md:63-66 已写明现成内参是给 assets/video.avi 那台相机标的）；B（零硬件，人人可做）——用 docs/verify_keypoint_order.py 验证模型关键点顺序，再故意把 object_points 第 2、4 点对调，记录 reproj err 从多少变成多少，并解释为什么 tvec 仍然「看起来像个正常数字」。B 比「证明排对了」强：可提交、可批改、答案不唯一、抄不了。讲 class/ 版时也要把「自己写的 Detector」改成「自己写的 Camera 类（Detector 用课程给的）」。同步改上游：讲稿 46/102/464 行统一口径，否则学生听完全课仍带着「我写过 Detector」的错误记忆去做作业。build_ppt.py:605 与 build_doc.py:256 一并改，两处 -DWITH_HIKROBOT=ON 写法要逐字一致。

### M5. 前置知识与课程脉络指错了上一讲——课前摸底会摸错东西，收尾脉络图缺了最关键的一环

**位置**：build_doc.py:110-111 表格0「适用对象」「前置知识」；逐字讲稿 3、46、102、125、1130 行；build_ppt.py:378-379（幻灯片4 上节课回顾）

**问题**：两层错。(1) 真正的前置是 lecture2 的 YOLO 装甲板检测作业——README.md:3/90 明确写 tasks/ 与 tools/ 是从 lecture2 作业逐字复制过来的；教师去确认学生的 Camera/Detector 类写完没有，而决定学生能否跑起来的是「lecture2 的 YOLO 作业做完没有、拿到的是完整仓库还是只拷了源码目录」（assets/ 约 60MB，已在 git 跟踪，最容易被 U 盘拷漏）。(2) 课程编号本身错了且两版都错：按 sp_vision_tutorial_27/README.md，Lecture 2 是「Hello C++&&OOP」、Lecture 3 是「Hello Modern C++」（lecture3/hw 是多线程流水线作业，与 OOP/Camera/Detector 无关），所以讲稿里「上节课的面向对象」「上一讲 Hello OOP」是错的，OOP 是上上节课。讲稿 125 行「今天用的就是灯条法」更是直接说反。

**改法**：build_doc.py:110-111 改为「已完成 Lecture 1~3 且完成 Lecture 2 YOLO 装甲板检测作业」+「…、Lecture 2 的 YOLO 装甲板检测器（Armor 结构体与它的 4 个关键点）；并确认拿到的是完整仓库含 assets/（约 60MB），而非只拷了源码目录」——把这半句写进「前置知识」单元格本身，不要塞进教师侧的教具清单。课前群里发一行 ls -l lecture4/yolo/assets/（应看到 yolov5.xml、yolov5.bin、video.avi）比任何文字都有效。讲稿 125 行改为「今天用的是 YOLO-pose 这条」；1130 行脉络回顾补上「你们在 lecture2 作业里跑通的那套 YOLO 推理——今天画面上那四个关键点就是它吐出来的」并把「上节课的面向对象」改为「面向对象，再到上节课的 Modern C++」；第 3、46、102 行的 Lecture 编号一并核对。build_ppt.py:379 改为「传统灯条法 / YOLO-pose 端到端（今天用这条）」，并在 379 行之后、380 行作业那条之前追加一条「今天直接用你作业里那份检测器，tasks/ 和 tools/ 一行没改」——注意行号，照「改 380 行」会误伤作业那条。

### M6. 给了学生一个假的通过判据：「框画出来了就说明 Task01-03 走通了」

**位置**：逐字讲稿 637 行（幻灯片20 演示收尾）

**问题**：两版都错。src/main.cpp:62 的 tools::draw_points(img, armor.points) 位于 Task02 代码块（64-73 行）之前，与学生填没填、填得对不对完全无关——Task01 模板继续注释着、Task02/03 一字不填，程序照样编译、照样画框（class/src/main.cpp:56 同理）。Task02 写成四个 (0,0) 或点序写反的学生，看见框画出来就以为自己对了，带着错误一路做到 Task04/05 才发现数值离谱，返工成本翻倍。

**改法**：637 行改为先打预防针：「这个框跟你 Task01 到 03 填没填一点关系都没有，画框那行代码在 Task02 前面，你一个字不填它也画——别拿『框出来了』当作做对了的证据」；真正的验收放到 Task04/05，用「z 跟着画面里的手连续变大变小、不为 0、不乱跳」这类可现场验证的性质，不要写死具体米数（仓库里没有 assets/video.avi 拍摄距离的任何依据，写死一个数等于用新假判据替换旧假判据）。末尾埋线到重投影误差。

### M7. answer/ 默认参与编译、就摆在学生工程里，而全套材料只字未提

**位置**：逐字讲稿 462-466（幻灯片16 项目结构）；CMakeLists.txt:38 的 add_executable(answer answer/main.cpp)；README.md:37 已主动把 ./build/answer 写给学生

**问题**：20 分钟上机一开始，任何学生打开自己的工程目录就能看到 answer/main.cpp 里填好的 Task01~05，敲一次 cmake --build 就同时得到 ./build/main 和 ./build/answer，整段练习直接作废；老师事先不知道这件事，巡场时也没法判断学生是自己推的还是抄的。反过来 ./build/answer 是很好的教学资源（画面上多一行 reproj err），应当被有意识地使用，而不是以意外方式暴露。

**改法**：两条路二选一，需拍板。①工程侧（推荐，一次性解决）：CMakeLists.txt 把 answer 目标包进 option(BUILD_ANSWER ... OFF)，教师演示时 -DBUILD_ANSWER=ON；README.md:22-39 的构建/运行两节同步改，否则 README 说能跑而实际跑不出来会变成新的课堂问题。②讲稿侧（无论选哪条都要写）：在幻灯片16 加一段约法三章——「这 20 分钟不许打开 answer/main.cpp，卡住了举手；等你自己的 ./build/main 跑起来了，我在投影上跑参考版给你们对照：它画面上比你多一行 reproj err，顺序排对时是个位数像素，这个数待会儿讲点序要用」，顺势把 reproj err 埋成钩子。

### M8. 巡场话术引导学生去调两个调了没用的参数

**位置**：逐字讲稿 669-675（卡点四「画面里没有装甲板轮廓」，讲纯灯条法与二值化阈值 170）；相关配置 configs/yolo.yaml:7、:15

**问题**：阈值 170 出自 class/tasks/detector.cpp:17，YOLO 版没有灯条法。而且 configs/yolo.yaml:15 写的是 150（老师口述 170 与学生看到的对不上，直接损害可信度），这个值读进 yolov5.cpp:20 后根本没被用过——唯一消费者 yolov5.cpp:184 是注释掉的；同理 yolo.yaml:7 的 use_traditional: true 也是失效字段。老师引导学生调死参数，学生改完毫无变化、反复困惑，而真正管用的一个字没提。另外 loop: true 让「画面在动说明视频没问题」这条检查恒为真、失去鉴别力。

**改法**：整段替换成四句：①视频是 loop 循环播的，一直在动是正常的，不代表检测没问题；②别去调 threshold 和 use_traditional，它们是 lecture2 留下的历史字段，代码里已经不用了（yolov5.cpp:184 那行是注释掉的）；③真正管用的是 configs/yolo.yaml 的 min_confidence: 0.8，想先看到框调到 0.7 试试，但别往 0.7 以下调——yolov5.hpp:30 还有一道写死的 const score_threshold_ = 0.7 更早一步把低分全滤掉了（yolov5.cpp:111-114），要再往下得改头文件重编译；④再往下是 check_name/check_type 的类别筛选，写好的不用动。顺带把「配置文件里的参数不一定是最终生效的那个」讲成一个教学点，与「注释会撒谎」是同一条主线。

### M9. 教案教学过程表里的 PPT 页码整表错位，教师照表翻页会全程翻错

**位置**：build_doc.py:176-183 的表格1（P.7-9 vs docx 的 P.7-10、P.10-13 vs P.11-14、P.33 vs P.34-35 等，P1 起每一行差 1~2 页）

**问题**：这不是三处孤立笔误，而是 build_doc.py 的页码基准整体落后于现行 37 页 PPT。若不在前置对账阶段修掉，重新生成后教案与 PPT 全程对不上。

**改法**：统一改为 docx 现有的 P.7-10 / P.11-14 / P.15-20 / P.21-26 / P.27-30 / P.31-33 / P.34-35 / P.36-37；PPT 新增页（关键点顺序坑、重投影自查）之后页码要重新核对一遍，两份材料的页码基准以最终生成的 pptx 为准。

### M10. P4 教师机投影比学生画面多两行，其中一行是下一个 Task 的答案剧透，全套材料无人解释

**位置**：逐字讲稿 699（幻灯片21）、920、983、1039（「画面上是三行字」「三行数字」）；answer/main.cpp:82 的 euler angles 与 :86-88 的 reproj err

**问题**：学生版 src/main.cpp 画三行（tvec/rvec/euler，且都是 0.0），教师机的 ./build/answer 画四行。落差有两层：(1) euler angles 是 P5 Task05 才让学生自己算的，P4 投 answer 等于答案已经在屏幕上；(2) reproj err 是本讲最有价值的新工具，讲稿全篇零提及（grep reproj|重投影 命中 0），学生看到必然会问，老师临场解释不好反而削弱后面的重点。同时老师嘴里念「三行」、投影上是四行，学生第一反应是自己少做了一个 Task。

**改法**：在 699 行一句话同时盖住两行：「画面最下面还多了两行——euler angles 是下一节你们自己要算的，我先不解释，别急着抄；reproj err 是参考实现多加的自查，它把算出来的位姿投影回图像量像素差，顺序写对是个位数像素、写反会跳到几十上百；你们自己那份没有这两行。」920/983/1039 行的「三行」统一加括注「（我投影上多一行 reproj err，参考版的自查，你们那份没有）」。注意 920 行与 983 行各被两条独立修改点命中，必须合并成一次改写，否则后改的会覆盖先改的。

---

## 4. 次要问题（MINOR）

### m1. 下一讲预告写了一门排课表上没有的课

**位置**：逐字讲稿 1162、1176 行；build_ppt.py:360；build_doc.py:264 的教学反思第 4 条

**改法**：sp_vision_tutorial_27/README.md 的大纲里 Lecture 5 是「Hello Kalman && Target」，没有单独的手眼标定一讲（lecture5/ 下只有空的 note.txt）。改为「下一讲：Hello Kalman && Target——目标还在动，你得预测它下一刻在哪」；手眼标定措辞收到可证范围内：「它是自瞄绕不过去的一步，但不会单独占一讲」——不要写死「不在排课表里」，Lecture 5 内容尚未成形，完全可能被并进去。build_doc.py:264 那条教学反思既已有结论，应从待办改成陈述。

### m2. center 的成因描述在 YOLO 版是错的

**位置**：逐字讲稿 540 行（「center 是两根灯条中心点的平均」）

**改法**：YOLO 版走 armor.cpp:153 的 center = (points[0]+points[1]+points[2]+points[3]) / 4，是四个关键点的算术平均。改为「在这份 YOLO 版里，它是那 4 个关键点的平均值，也就是四边形的形心——算出来的虚拟点，不是四个角里的任何一个」。不要补「就是对角线交点」（顶点算术平均等于两条中位线交点，只有平行四边形才与对角线交点重合，透视下会差几像素）。这段与点序坑同在 538-540 行、都要求切到 armor.hpp，必须合并成一整段连贯讲词（顺序：指 points 错注释 → 现场证据 → 顺带点出 left/right 是空的 → center 是形心不能凑 PnP），否则三次「切到 armor.hpp」会把 5 分钟的 Task01 讲爆。

### m3. 历史视频笔记缺版本适用性声明，且第 3 行的素材路径已失效

**位置**：armor_lecture_notes.md 第 1 行下方、第 3 行、第 7 行 Scope note；pnp_lecture_notes.md 第 1 行下方

**改法**：正文一律不动（它是往届录像的忠实史料，改成 YOLO 版等于伪造，且 class/ 版仍需要它）。各加一段四行横幅：说明这是历史记录、不随程序更新、本届有 class/ 与 yolo/ 两份程序、据此生成材料前先全文搜索「【2027 版编者注】」逐条核对，不要直接照抄代码段——把搜索标记定为硬动作，比在横幅里枚举 6 条冲突更可靠（枚举必然与就地注释漂移）。横幅里保留一条正向背书：「object_points 的内容两版完全相同，无需分版本」，防止改材料的人出于谨慎把对的也改坏。armor L3 的 Documents\class_four\frames\armor\ 改为指向仍存在的 extracted_ppt/armor_slides/ 与 armor_manifest.md，并注明只有 8 帧可恢复、不是 33 帧的完整替代。

### m4. 点位编号基准 1-based / 0-based 全篇不统一

**位置**：逐字讲稿 472、556、562、571、657 及 PPT 幻灯片16/18 相关文案

**改法**：学生实际写的是 at(0)~at(3)，但实物讲解用「1 号是左灯条上端」更有画面感。统一口径：保留 1-based 的物理讲法，每次给出换算——「点 1 是 armor.points.at(0)，点 2 是 at(1)…差一位不会报错，但位姿整个转过去」。657 行照此改，并把结尾的「眼睛盯着那四个成员名」换成可操作动作：「把 object_points 和 img_points 两段代码上下并排，第 i 行对第 i 行，四行注释一行一行对」。

### m5. 幻灯片4 上节课回顾把两条识别路线并列摆着，不交代今天走哪条

**位置**：build_ppt.py:378-379（成品 ppt_pnp.txt:53-54）

**改法**：见 major 5 的同一处改动（379 行加粗「今天用这条」+ 追加 tasks/tools 逐字复制的说明）。YOLO 版下这一页是唯一的衔接点，不点名的话幻灯片5 讲 armor.points 会显得突兀。

### m6. 半成品 slide4「制造疑问」页零配图，主讲人会指向空白

**位置**：Hello Armor&Solver.pptx slide4；逐字讲稿 169-180 行已写好指 3 号车/4 号车对比图的台词

**改法**：页上的 AutoShape 5/6/7 是从 Lecture3 继承的无填充无边框残留矩形（0.68×0.5 in，放映时不可见），不是图片占位符，数量与生成版要求的三张照片吻合是巧合——直接删掉，新插入三张图片形状自由排版。配图用 assets/video.avi 抽帧：远/近各一帧（「哪块更远？程序怎么知道？」）、正对/侧倾各一帧（「像素位置几乎没变，但朝向变了」），再加一张 ./build/answer 叠了 tvec 与 euler angles 的截图作钩子。注意 slide1/3/4 是仅有的三张已改页，不会被整体替换覆盖，需单独排期，最容易在执行时漏掉。

### m7. 半成品 slide3 的伪代码图把取帧 API 的形状教反了

**位置**：Hello Armor&Solver.pptx slide3 的 media/image4.png（Camera camera(..); cv::Mat image = camera.read(..);）

**改法**：三个版本的 read 都是 void + 出参：yolo/io/camera.hpp:32 与 homework 版都是 void read(cv::Mat&, std::chrono::steady_clock::time_point&)，class 版是 void read(cv::Mat&)；构造函数也是 explicit Camera(const std::string& config_path) 而非 Camera(int exposure)。这张图未被裁剪、位置醒目，是本页唯一完全可见的代码示意图，实际独自承担着「告诉学生怎么取帧」的全部职责（同页另一张 camera >> img 被裁剪隐藏了），且它是本次新插入的图（md5 在 Lecture3 素材库里找不到），不能用「继承自上一讲」解释。改成与 src/main.cpp:46-53 逐字对齐的出参形式并加一行红字：「read 不返回图像，图像从出参带回来」，旁注「读视频还是读相机由 configs/yolo.yaml 的 source 决定」。本页需与「补 4 个点的来源交代」一次性重做。

---

## 5. 需要新增的内容

这些是 YOLO 版引入的、现有材料里**完全没有**的知识点。

### 关键点顺序陷阱：tasks/armor.hpp:97 的注释是错的

**为什么要讲**：本讲 YOLO 版刻意保留的核心教学点，也是唯一一类「有数、不报错、画面正常、但全错」的故障。注释写「左上、左下、右下、右上」，真实顺序是「左上、右上、右下、左下」；而材料又主动把学生赶去读这个文件（PPT 幻灯片18「看看 Armor 结构体有哪些成员」、讲稿 552「先去看一眼 tasks/armor.hpp 里的结构体」）。全套材料对此零覆盖——37 页 PPT 命中 0、讲稿全文命中 0。真正的教学价值不是背顺序，是「注释是人写的会过期，代码和数据不会撒谎，冲突时信实测」。注意这条在 class/ 版不存在（class/tasks/armor.hpp:87 的 points 没有任何顺序注释、学生也不碰 points），属 YOLO 版专属。另：注释在 armor.hpp 里出现两次（文件头注释块第 6 行 + 成员上第 97 行），正好可以现场讲「错误注释会被复制」。

**插入位置**：主讲位置在 P3：PPT 在 build_ppt.py:468 之后（Task01 页与 Task02 页之间）新增一页；讲稿主改在 552 行（学生正打开 armor.hpp 的那一刻）与 538 行的〔操作〕处展开；教案在教学重点 build_doc.py:152 加一条 bullet、教学难点 :154 加一条。总结页（讲稿 1114-1132、build_ppt.py:594-602）加一条回扣，七条改八条（1114 与 1132 行的「七条」同步改）。现场第一证据用 draw_points 在画面上按下标标 0/1/2/3（三秒讲完），第二证据用当场把 object_points 换成注释那个顺序重编、看 reproj err 暴涨；ratio≈2.41 的推导留作课后阅读。

**预计用时**：4 分钟（P3 内），总结回扣 20 秒

### 重投影误差自查（tools/pnp_check.hpp 的 reproj err）

**为什么要讲**：材料在 4 处反复强调「点序错了 solvePnP 不报错、最难查」，却从未给出任何排查手段——巡场时老师只能说「你再对一遍」。新程序已经造好了唯一能一眼判死的工具（answer/main.cpp:86-88 画在画面上），不讲等于白造，而且学生看到教师机上那行数字必然会问。它与上一条是配对的：一个说坑、一个给出路，拆开会让坑变成一句吓唬人的话。必须同时解决「学生够不够得着」：src/main.cpp 没有 include tools/pnp_check.hpp，学生自己跑的 ./build/main 不显示这个数。（pnp_check.hpp 是 header-only 且 CMakeLists.txt:23 有 include_directories，加一行 include 即可，不需要改 CMake。）

**插入位置**：PPT 在 build_ppt.py:571 之后（Task05 页与「现场演示&互动」之间）新增一页，与上一条排成呼应的两页；讲稿在 659 行（卡点二「点序搞反了」）之后补 30 秒，并在 699/920 行一句带过；教案必做作业验收标准（build_doc.py:254）与 PPT 作业页（build_ppt.py:604）写进判据。判读口径统一成「个位数像素就是对的，两位数就是错的，中间没有灰色地带」，不要在口播稿里报死 2~3 px（本机无 OpenVINO 无法实测，现场跑出 5 px 老师会下不来台）。

**预计用时**：3 分钟（P5 或 P3 末），巡场时反复用

### 构建依赖与工作目录约束（OpenVINO 2024.6.0 + cd lecture4/yolo）

**为什么要讲**：两版材料都没有这块——class/ 版只要 OpenCV + fmt，随手在哪跑都差不多；YOLO 版多了 5 个依赖、OpenVINO 路径写死在 CMakeLists.txt:18，且模型/视频/配置/日志四样全是相对路径，必须站在 lecture4/yolo/ 下运行。这是唯一一块「课前不做、课上必炸且补不回来」的内容。

**插入位置**：教案教具清单与表格0（build_doc.py:111、245-247）；PPT 幻灯片20（build_ppt.py:496-501）；讲稿幻灯片16 在 462 行之前插入 30 秒环境确认 + 巡场话术库新增最前一条卡点。课上只做 30 秒确认，安装本身必须课前完成，没装的同学先用助教机器。

**预计用时**：课上 2 分钟（含现场确认），课前教师侧另计

### YOLO-pose 端到端：模型直出 4 个关键点，没有灯条中间步骤

**为什么要讲**：整条叙事线的地基，替换原来的「灯条配对→Armor」讲解。不讲清楚，Task02 改成 armor.points 学生会觉得与前面自相矛盾；讲清楚了还能顺带解释「Armor 里为什么还留着 left/right」（传统路径的历史包袱），避免学生看到结构体里有这俩成员、材料又说别用而反过来怀疑自己。

**插入位置**：P0 复习导入（教案 build_doc.py:175、PPT 幻灯片4-5、讲稿 125/143-155 行），替换原有的灯条流程铺垫——这一条是净腾出时间的。半成品 PPT 的 slide33「传统 vs YOLO 对比页」正好前移到这里复用。「3 号车 vs 4 号车」「同一装甲板三种朝向」两组提问照片与检测器无关，务必保留。

**预计用时**：2 分钟（替换原灯条讲解的 4 分钟，净省 2 分钟）

### configs/yolo.yaml 的取帧切换与 answer 目标

**为什么要讲**：两件学生第一分钟就会撞到、材料却完全没提的事：(1) 读视频还是读相机由一行配置决定（source: video|camera，loop: true），相机路径另需 -DWITH_HIKROBOT=ON + MVS SDK，否则 io/camera.cpp:31-34 抛出明确异常——这条异常写得很好、自带解法，正好拿来做「好的错误信息长什么样」的正面教材；(2) 工程里有 answer/ 目录、默认会编出 ./build/answer，必须由老师主动定规矩而不是被学生意外发现。

**插入位置**：讲稿幻灯片16 项目结构段（与环境检查、路径改动合并成一次重写，顺序：环境检查 → 打开 lecture4/yolo 只填 src/main.cpp → answer/ 约法三章 → 运行目录伏笔）；PPT 幻灯片16 的目录说明 bullet；教案表格0「配套代码」格。

**预计用时**：1.5 分钟（并入 P3 开头那段，不单独占时）

---

## 6. 时间表影响

需要重排，但总量仍能压在 90 分钟内，且不必牺牲任何原有教学目标——因为要删的内容和要加的内容体量相当。

现状 3+7+7+14+20+14+16+6+3=90。建议改为 3+5+6+13+24+14+16+6+3=90。

腾出时间（共 -4 min）：
• P0 复习导入 7→5（-2）：删掉「灯条配对→Armor→4 个 2D 点」的整条铺垫（在 YOLO 版是错的，且是 Task02 那个 blocker 的直接致因），换成「回顾你们 lecture2 的 YOLO 作业：模型吐出 class_id/confidence/box/4 个关键点」。「3 号车 vs 4 号车」「同一装甲板三种朝向」两组提问照片与检测器无关，务必保留。半成品 PPT 的 slide33 传统 vs YOLO 对比页前移到这里，正好补上「为什么换成 YOLO」。
• P1 为什么需要位姿 7→6（-1）、P2 PnP 原理与 API 14→13（-1）：这两段纯概念/纯数学，两版通用、质量也高，只做轻度压缩腾时间，不删内容。

吃掉时间（共 +4 min，全部进 P3）：
• P3 动手实验一 20→24（+4）。内部再分配：新增「关键点顺序陷阱」4 min、新增「重投影误差自查」3 min（若放 P3 末；也可挪到 P5 巡场时用）、新增「环境确认 + answer/ 约法三章 + 取帧方式」约 2 min；压缩「讲解 video.avi 找不到的经典报错」2 min（YOLO 版这个桥段的教学价值实质下降了——YAML::BadFile 不含「找不到」字样，新手推不出根因，不值得再占原来的篇幅）、压缩原「讲解项目结构与点序约定」1 min（点序约定并入新增那页）。注意讲稿原标「幻灯片16 ⏱4 分钟」在合并三条改动后会涨到 6 分钟左右，这 2 分钟已含在 P3 的 +4 里。

不变：P4 14 min（「转一转看一看」改成看 loop 播放的视频，教学目的达成、时长不变）、P5 16 min（reproj err 主要在巡场答疑时用，不额外占讲授时间；但 Task04/05 的 draw_text 参数顺序坑若不修，这 16 分钟会全班卡死，属于时间表之外的风险）、P6 6 min、P7 3 min。

课前另计（不占课堂）：OpenVINO 2024.6.0 + Eigen3/yaml-cpp/spdlog 的镜像准备与一次完整构建 + 运行验证；若要做实物相机演示，MVS SDK 与 -DWITH_HIKROBOT=ON 的构建也必须课前完成并验证过 USB 直通；现场演示用的两条真实报错文本需在 Linux 构建机上实跑抄录。

---

## 7. 按材料的结论

| 材料 | 改动量 | 改哪里 |
|---|---|---|
| Lecture4_HelloArmor_教案.docx（已发布产物） | `yes-heavy` | 改生成脚本 build_doc.py 后重新生成——但必须先做反向对账（见 blocker 1），否则会把 [p0028] object_points 表达式写法与 [p0036] 的弧度注静默回退；对账时唯一豁免的是那三处 draw_text。不要手工改 docx，否则分叉会再发生一次。 |
| build_doc.py | `yes-heavy` | 改脚本本身，严格顺序：修 :266 路径（+ 仓库位置断言）→ 反向对账 → :110-112 表格0、:151-154 重点难点、:175-183 教学过程表、:211-216 Task02、:223-237 Task04/05、:245-247 教具清单、:254-256 作业、:264 教学反思 → 重新生... |
| Lecture4_HelloArmor_装甲板位姿解算.pptx（37 页成品） | `yes-heavy` | 改生成脚本 build_ppt.py 后重新生成，但先做全文 diff 回流（成品比脚本新，至少 :467 的 Task01 操作指令与 :261 的 P7 时长已漂移，且未逐页比对过）。生成后把 pptx 纳入 git 跟踪——当前 pptx 全是未跟踪状态，正是这次分叉的根因。注意幻灯片28/29 的 dra... |
| build_ppt.py | `yes-heavy` | 改脚本本身。:448 与 :450 在同一个 slide_content(447-452) 调用里，一次编辑改完；:378-379 的行号要核准（「两种识别思路」在 379 不在 380，照 380 改会误伤作业那条）。新增两页后，教案表格1 的页码基准要以最终 pptx 重新核对。 |
| Lecture4 Hello Armor&Solver.pptx（半成品） | `yes-heavy` | 只能手工改这份产物——它没有生成脚本，且它承载的是队里真实的视觉设计（母版/版式/主题/队徽）与 37 个备注位，生成版没有这些。改动量取决于模板决策（openQuestions 第 2 条）。若选它：先独立做掉三个小动作（第 1 页备注、slide2 目录页、slide37 作业页），再做 33 页正文替换（豁... |
| output/Lecture4_HelloArmor_逐字讲稿.md | `yes-heavy` | 改产物 output/Lecture4_HelloArmor_逐字讲稿.md，同时同步 output/script_parts/*.md——两者是同一份内容的两处副本（已逐字比对 1100-1188 与 08_p7_summary.md 完全一致），只改一处，下次重新拼装会把修改覆盖回去。另需在 output/s... |
| armor_lecture_notes.md / pnp_lecture_notes.md（历史视频笔记） | `yes-light` | 改产物，但只做加法：①各加一段四行版本适用性横幅（把「全文搜索【2027 版编者注】」定为硬动作，不枚举冲突以免漂移，但保留「object_points 两版相同」这条正向背书）；②在 6 个冲突点就地插入【2027 版编者注】（取点方式、×57.3、CAP_IMAGES、目录树、转动装甲板、点序+重投影这条「本... |

各材料详述：

### Lecture4_HelloArmor_教案.docx（已发布产物）  —— `yes-heavy`

表格0 的四个单元格（适用对象/前置知识/教具环境/配套代码）、表格1 的教师学生活动与整列页码、Task02 与 Task04/05 的标准答案、教学重点难点、作业布置全部要改；特别注意 [p0034]/[p0036] 现有的 6 参数 draw_text 是 class/ 顺序、本身就是坏的，不是「已修正、别覆盖」。

**改哪里**：改生成脚本 build_doc.py 后重新生成——但必须先做反向对账（见 blocker 1），否则会把 [p0028] object_points 表达式写法与 [p0036] 的弧度注静默回退；对账时唯一豁免的是那三处 draw_text。不要手工改 docx，否则分叉会再发生一次。

### build_doc.py  —— `yes-heavy`

本轮 12 条改动的落点，但脚本自己先坏了：:266 输出路径写死到已不存在的目录，一跑就 FileNotFoundError；:203-237 与 :176-183 整体落后于已发布 docx。

**改哪里**：改脚本本身，严格顺序：修 :266 路径（+ 仓库位置断言）→ 反向对账 → :110-112 表格0、:151-154 重点难点、:175-183 教学过程表、:211-216 Task02、:223-237 Task04/05、:245-247 教具清单、:254-256 作业、:264 教学反思 → 重新生成 → git diff 复核。

### Lecture4_HelloArmor_装甲板位姿解算.pptx（37 页成品）  —— `yes-heavy`

幻灯片 4/5/16/18/20 要改（回顾页点名、灯条叙述、项目结构与点位约定、Task02 答案、构建与报错），另需新增两页（关键点顺序坑、重投影自查）与作业页改写；Task01/03、P1/P2/P4/P6 与欧拉角公式页两版通用，不动。

**改哪里**：改生成脚本 build_ppt.py 后重新生成，但先做全文 diff 回流（成品比脚本新，至少 :467 的 Task01 操作指令与 :261 的 P7 时长已漂移，且未逐页比对过）。生成后把 pptx 纳入 git 跟踪——当前 pptx 全是未跟踪状态，正是这次分叉的根因。注意幻灯片28/29 的 draw_text 实参被省略成 `), ...);`，参数顺序问题不落在这份材料上。

### build_ppt.py  —— `yes-heavy`

:610 输出路径失效（需 import os）；:378-387、:447-452、:469-486、:496-501、:605 要改；:468 后与 :571 后各插一页新内容；:360 下一讲预告要改。

**改哪里**：改脚本本身。:448 与 :450 在同一个 slide_content(447-452) 调用里，一次编辑改完；:378-379 的行号要核准（「两种识别思路」在 379 不在 380，照 380 改会误伤作业那条）。新增两页后，教案表格1 的页码基准要以最终 pptx 重新核对。

### Lecture4 Hello Armor&Solver.pptx（半成品）  —— `yes-heavy`

37 页里 34 页正文 + 全部 37 份备注仍是 Lecture3（slide2 目录页宣告讲 CMake/OOP、slide37 布置上一讲的作业、第 1 页备注自报「第三次培训讲 OOP」）；已改的 slide3 把取帧 API 形状教反、slide4 零配图。

**改哪里**：只能手工改这份产物——它没有生成脚本，且它承载的是队里真实的视觉设计（母版/版式/主题/队徽）与 37 个备注位，生成版没有这些。改动量取决于模板决策（openQuestions 第 2 条）。若选它：先独立做掉三个小动作（第 1 页备注、slide2 目录页、slide37 作业页），再做 33 页正文替换（豁免并前移 slide33），备注用逐字讲稿机械灌入。若不选它：仅保留 slide33 与母版/队徽素材，其余归档。

### output/Lecture4_HelloArmor_逐字讲稿.md  —— `yes-heavy`

改动最重的一份，约 40 处锚点：8 处 class/ 路径、Task02 整段（552-571）、Task04 代码块（895-898）、演示段（611-637）、巡场话术库（645-675）、P4 观察实验（697-769）、P5 互动（979-1013）、总结与作业（1114-1176）、课程编号（3/46/102/125/1130）。多处出现同一行被 2~3 条修改命中（L719、L556、L637、L920、L983、L464），必须合并成一次改写。

**改哪里**：改产物 output/Lecture4_HelloArmor_逐字讲稿.md，同时同步 output/script_parts/*.md——两者是同一份内容的两处副本（已逐字比对 1100-1188 与 08_p7_summary.md 完全一致），只改一处，下次重新拼装会把修改覆盖回去。另需在 output/script_parts/_context.md:411 就地标注弃用，防止旧数值回流。若讲稿本身有生成脚本则改脚本；否则改产物并把两处副本纳入同一次提交。

### armor_lecture_notes.md / pnp_lecture_notes.md（历史视频笔记）  —— `yes-light`

正文是往届录像的忠实史料，不改正文；但它是 build_doc.py/build_ppt.py 的素材来源，已确认至少 3 处污染流进了生成脚本（armor.left.top、CAP_IMAGES、×57.3），不加标记下一轮会再复制一次。

**改哪里**：改产物，但只做加法：①各加一段四行版本适用性横幅（把「全文搜索【2027 版编者注】」定为硬动作，不枚举冲突以免漂移，但保留「object_points 两版相同」这条正向背书）；②在 6 个冲突点就地插入【2027 版编者注】（取点方式、×57.3、CAP_IMAGES、目录树、转动装甲板、点序+重投影这条「本届新增、笔记无素材」）；③armor L7 的 Scope note 与 L129 的 Task02 英文说明必须就地加括注（它们是会被脚本当事实抄走的具体断言，横幅挡不住）；④唯一建议直接改正文的是 armor L3 的失效素材路径（那是元数据指针，不是历史内容）。

---

## 8. 待决策问题

> 第 1 条必须最先拍板——它决定其余每一条的落地方式。

1. 【最关键】class/ 传统版与 yolo/ 版是各自维护一套完整材料，还是材料整体切到 YOLO 版、class/ 只作为代码保留不再有配套材料？73 条里有近一半是「对 class/ 版仍然正确、只对 YOLO 版错」——若选「各一套」，改法是到处加版本标注（维护成本翻倍，且教师拷错版本的风险长期存在）；若选「整体切」，改法是直接覆盖（更干净，但 class/ 版将来无法单独开课）。这个决定影响每一条 blocker 的具体落地方式，必须最先拍板。

2. 最终交付的 PPT 用哪一份作承载？Lecture4 Hello Armor&Solver.pptx 有真实视觉设计、母版主题、队徽和 37 个备注位，但正文是 Lecture3；Lecture4_HelloArmor_装甲板位姿解算.pptx 有完整的本讲内容，但 media 目录为空、无备注、配图全是「🖼 …示意图」占位。两者是模板 vs 内容的互补关系，不是新旧替代。（补充两条供判断：两份文件都有 PowerPoint 锁文件，「正在被编辑」不能作为选型依据；半成品的 44 个 media 里绝大多数是 Lecture3 的 g++/CMake 截图，加一个 30MB 的 media1.mp4，随正文替换后都会丢弃，真正不可再生的只有队徽和母版/主题。）

3. 欧拉角统一用弧度还是角度？当前两版 answer/main.cpp 都直接打印弧度（不乘 57.3），而历史笔记与 build_ppt.py:531 都是角度制。改程序（两版各 3 行加 ×57.3）还是改材料？教学上倾向角度——P4 有 14 分钟的「转一转看一看」直觉建立环节，yaw 从 0.25 变 0.50 远不如 14° 变 28° 直观，P1 的飞机 yaw/pitch/roll 比喻在学生认知里也是度。但这是改代码，需要拍板。

4. answer 目标是否改成默认不编译（option(BUILD_ANSWER ... OFF)）？现在学生一敲 cmake --build 就得到填好答案的 ./build/answer，且 README.md:37 已主动告知。改则需同步改 README 的构建/运行两节；不改则只能靠讲稿约法三章。

5. 是否在学生版 src/main.cpp 预置 #include "tools/pnp_check.hpp" 并显示 reproj err（标注为「非学生任务的自查显示」）？不预置，学生自己跑的 ./build/main 看不到这个数，「我们给了你一把尺」就是空头支票，只能排队到教师机前看；预置则学生填完立刻能自查，能把本讲最隐蔽的坑降成可自愈问题。（若改为必做作业项，answer/main.cpp:85 那句「不属学生任务」的注释要同步改口径。）

6. 授课教室到底有没有 HikRobot 相机 + 装好 MVS SDK 的机器？这决定 P4「转一转看一看」与 P5 上台互动写成 A 方案（全班看 loop 视频）还是 A+B 双轨（教师机实物、学生机视频）。若不确定，默认按 A 写并把 B 作为旁注——把「弃用相机不影响教学闭环」明确写进教案，能大幅降低现场决策压力。

7. 是否给程序加一个空格暂停（int k=cv::waitKey(20); if(k=='q')break; if(k==' ')cv::waitKey(0);）？现在程序没有任何暂停/拖拽能力，讲稿里凡是「把视频拖到某几帧对照」的演示都做不出来，只能靠 25 秒 loop 等它转回来。加这一行能让 P4/P5 的对照演示可控得多，但属于代码改动。

---

## 9. 完整性批判

**置信度**：`medium`

这次审计在「YOLO 版 vs class 版的内容冲突」这条主轴上做得相当扎实——6 条 blocker 我抽查的核心事实全部复现得上（left/right 为空、draw_text 参数序、class/ 路径 8 处、生成脚本输出路径失效、半成品 PPT 的 Lecture3 残留），误报率低。漏的不是「更多同类冲突」，而是**三类结构性盲区**：

一是**覆盖面**：`lecture4/homework/`（一份带空 `solvePnP()` 的 YOLO11 buff 进阶作业脚手架，直接推翻了 Major 里「进阶作业失效」那条的改法）、`lecture4/reprojection/`（重投影 + 完整 IMU 变换链的现成素材）、以及 `output/script_parts/` 下 `_context.md`/`_style.md`/`_header.md` 三份「唯一事实来源」元文件，都不在审计范围内。其中元文件那条最要命——清单为两个生成脚本设了前置闸门，却漏了讲稿这条生产线的闸门，不修就会把已修好的 blocker 原样复活，而且是以「红线，违反即作废」的强制力复活。

二是**双份结构**：9 份分段讲稿里有 6 份已和合并稿漂移，清单的所有讲稿锚点只给了合并稿行号，每条 blocker 都有一个没被点名的孪生体。

三是**跨材料重算**：时间预算整类缺席（P0 段和 P3 段的 ⏱ 都已顶满 `_style.md` 的硬约束，清单却要往里塞两页新 PPT 加三处展开）；PPT 页脚印刷页码比幻灯片序号整体少 1（清单只查了教案表格的页码，没查 PPT 自己印的数字），而新增页会让这个偏移继续叠加；37 页成品的 15 张配图全是灰色占位框，一张真图都没有——这份「成品」其实根本不能直接上课。

另有三条建议撤销或降级：`center` 那条在 YOLO 版数学上依然成立（`(kp0+kp3)/2` 与 `(kp1+kp2)/2` 的平均恒等于四点均值）；「教师机多两行」实际只多一行，且被指为剧透的 euler 行在学生文件里本来就有、讲稿对它的描述完全正确；「排课表上没有的课」在仓库里找不到那份排课表。

置信度定在 medium：我用 Read/Grep/Glob 实测了代码侧的每一条断言和材料侧的大部分锚点，但有两处没法本地验证——docx/pptx 成品与生成脚本的逐条对账（清单声称产物已落后于脚本，我只抽查了 Task01 那句和 P7 时长，都对得上），以及半成品 PPT 里几张图片的画面内容。

### 发现的遗漏（9 条）

**1. 整个 `lecture4/homework/` 工程完全没被审计到——它是一份 YOLO11 能量机关（buff）项目，里面 `tasks/buff_solver.cpp:6-8` 的 `Buff_Solver::solvePnP()` 是一个**空函数体**，显然就是为本讲准备的进阶作业脚手架。它自带 `assets/yolo11_buff_int8.xml/.bin`、`src/video.cpp`、完整的 io/tasks/tools，CMake 目标是 `main` 和 `video`（CMakeLists.txt:34-35，project 名字叫 `Lesson4`）。全套教学材料（build_doc.py、build_ppt.py、逐字讲稿、两份历史笔记）里**一次都没提到 homework、buff、能量机关**（已 grep 验证，零命中）。**

- 为什么重要：清单里的 Major 条「进阶作业失效：让学生去接一个他从来没写过的 Detector，而真正要做的事一个字没提」诊断对了病症，但开错了药——它以为进阶作业需要重新设计，实际上仓库里**已经躺着一份写好的脚手架**，只差一个 `solvePnP()` 空壳等学生填。这属于「必须改」且改法完全不同：不是删掉旧作业换个说法，而是把学生指向 `lecture4/homework/`。顺带两个硬冲突：homework 的 `io::Camera` 构造签名是 `Camera(double exposure_ms, double gain, const std::string & vid_pid)`（io/camera.hpp:21），和 yolo 版的 `Camera(const std::string & config_path)` **不是同一个 API**——这是本讲要面对的**第三套**取帧接口；homework 的 CMakeLists.txt 里**没有 find_package(OpenVINO)**（只有 OpenCV/Eigen3/fmt/spdlog），但 tasks/yolo11_buff 显然需要它，学生课后第一步 cmake 就会失败。
- 怎么查证：`ls C:/Users/ziang.xu/Documents/sp/class_four/lecture4/homework`；读 `C:/Users/ziang.xu/Documents/sp/class_four/lecture4/homework/tasks/buff_solver.cpp`（全文 10 行，solvePnP 是空的）与 `.../homework/CMakeLists.txt`（对比 `lecture4/yolo/CMakeLists.txt:15-19` 的 OpenVINO 块）；再 `grep -rn "homework\|buff\|能量机关" build_doc.py build_ppt.py output/ armor_lecture_notes.md pnp_lecture_notes.md` 确认零命中。

**2. `output/script_parts/_context.md`(615 行)、`_style.md`(141 行)、`_header.md`(33 行) 这三份**驱动讲稿生成的元文件**不在审计覆盖列表里，而它们正是几乎每一条 blocker 的上游源头，且 `_style.md:102` 把这些内容定性为「技术准确性（红线，违反即作废）」。具体命中：`_style.md:106`「Task 01~05 全部在 `lecture4/class/src/main.cpp` 一个文件里」、`:109`「Task 02 的点：`armor.left.top`、`armor.right.top`、`armor.right.bottom`、`armor.left.bottom`」、`:116`「`cd lecture4/class` … 会报 `CAP_IMAGES: can't find … video.avi`」、`:117`「Detector 是**纯灯条法**（二值化阈值 170…），**没有 ONNX/神经网络**——巡场话术里不要提分类置信度、模型加载」；`_context.md:8`、`:16`、`:31`、`:129`、`:350-353`、`:454-480`（整棵 class/ 目录树 + CAP_IMAGES 报错原文）、`:528`、`:605-606`。另外 `_header.md:30` 还有一条**对当前成品就已失实**的注：它说第 2 页印刷时长是「7/7/13/19/12/17/6/6」，而实际 pptx 第 2 页印的是 7/7/14/20/14/16/6/3。**

- 为什么重要：属于「必须改」。清单把 `armor_lecture_notes.md:7` 的 Scope note 点名为「生成脚本抄错的源头」，但真正的唯一事实来源是这个 context 包——`_context.md:5` 自称「本文件是撰写逐字讲稿的唯一素材来源」。只要这三份文件不改，任何人重新生成或补写任一讲稿分段，都会**原样复活** class/ 路径、armor.left/right 答案、CAP_IMAGES 报错、阈值 170 巡场话术这四条 blocker——而且是以「红线，违反即作废」的强制力复活。清单里的两个「前置闸门」只锁了 build_doc.py 和 build_ppt.py，漏了讲稿这条生产线的闸门。
- 怎么查证：`grep -n "lecture4/class\|armor\.left\|armor\.right\|CAP_IMAGES\|170\|纯灯条法" C:/Users/ziang.xu/Documents/sp/class_four/output/script_parts/_style.md C:/Users/ziang.xu/Documents/sp/class_four/output/script_parts/_context.md`；`_header.md:30` 的印刷时长与 `python -c "from pptx import Presentation; [print(sh.text_frame.text) for sh in Presentation('Lecture4_HelloArmor_装甲板位姿解算.pptx').slides[1].shapes if sh.has_text_frame]"` 的输出对照。

**3. `output/script_parts/0*.md` 这 9 份分段讲稿是合并稿之外的**独立副本，且已经和合并稿漂移**。逐段 diff：00 差 4 行、02 差 2 行、04 差 2 行、05 差 2 行、06 差 6 行、07 差 2 行（01/03/08 完全一致）。清单里所有讲稿锚点都只给了合并稿 `output/Lecture4_HelloArmor_逐字讲稿.md` 的行号，但每一条都有一个分段孪生体，例如那句「我的要求是——你自己从 `armor.left` / `armor.right` … 挑」同时存在于合并稿 :556 和 `04_p3_task01_03.md:107`；「二值化的**阈值是 170**」同时在合并稿 :673 和 `04_p3_task01_03.md:224`。**

- 为什么重要：属于「必须改」。这是一个纯粹的**改漏风险**，与 YOLO/class 无关：按清单只改合并稿，分段文件里的旧答案原封不动留着，下一次任何形式的重新合并或分段补写都会把已修好的 blocker 覆盖回去。清单已经为两个生成脚本设了「先修脚本再谈内容」的前置闸门，讲稿这条链路存在同样的双份结构却没有对应条目。
- 怎么查证：逐段做 difflib：把每份 `output/script_parts/0*.md` 的首行在合并稿里定位，取等长切片比对（00/02/04/05/06/07 有差异）；再 `grep -n "我的要求是" output/script_parts/*.md output/Lecture4_HelloArmor_逐字讲稿.md` 看同一句话的两个落点。

**4. **37 页成品 PPT 的印刷页码比幻灯片序号整体少 1**，而讲稿全篇 35 处〔操作〕都按幻灯片序号报页。根因在 `build_ppt.py:35` 的 `_slide_no = [0]` 与 `:103-104` 的 `add_footer` —— 封面不调用 add_footer，所以计数从第 2 张幻灯片才开始加 1。实测：第 2 张印「01」、第 17 张（Task 01）印「16」、第 28 张（Task 04）印「27」，第 1 张和第 37 张无页码。讲稿写的是「翻到第 17 页」「看第 28 页，Task 04」。**

- 为什么重要：属于「必须改」（两版都错，与 YOLO 无关）。清单只抓了教案表格 1 的 PPT 页码错位（build_doc.py:176-183），没有检查 PPT **自己印在页脚上的数字**。结果是：老师照讲稿念「翻到第 17 页」，学生低头看投影右下角是「16」；更糟的是在「新增关键点顺序页」之后，这个 off-by-one 会叠加成 off-by-two，而清单给出的插入位置（build_ppt.py:468 之后、:571 之后）会让 Task 02 之后的所有页码再移位一次。改材料前必须先决定 footer 的编号基准，否则讲稿、教案、PPT 三套页码要对三次。
- 怎么查证：`python -c` 用 python-pptx 遍历 `Lecture4_HelloArmor_装甲板位姿解算.pptx`，打印每页里形如纯数字的文本框（结果：slide 2→'01' … slide 36→'35'，slide 1 与 37 为空）；再读 `build_ppt.py:35`、`:103-104`、`:117` 确认 `_slide_no` 的递增时机。

**5. **整个「时间预算重算」这一类冲突没有任何条目。** 新增内容清单要求加 4 处实质内容（关键点顺序 1 新 PPT 页 + 讲稿 552/538 两处展开；重投影自查 1 新 PPT 页 + 讲稿 659 处 30 秒 + 699/920 各一句；环境确认 30 秒 + 巡场新卡点；configs/answer 项目结构重写），删 1 处（P0 灯条流程铺垫，自称「净腾出时间」），但**没有一条说明这些增删后时长怎么配平**。受影响的是四套互相约束的时间表：讲稿每页 ⏱（37 处，合并稿里逐页可查）、`_style.md:54-68` 的分段总时长表（`:49` 明文规定「各页时长之和**必须**精确等于该分段的总时长」、`:68`「九段合计正好 90 分钟」）、`_header.md:13-28` 的时间轴总表、build_ppt.py:254-261 的路线图页与 build_doc.py:173-183 教案表格 1 的时钟列。**

- 为什么重要：属于「必须改」。P3 那一段（幻灯片 15-20）现在是 0.5+4+5+4+3+3.5 = 20 分钟，刚好顶满 `_style.md:62` 给的 20 分钟预算，没有一秒余量；清单要往这一段里塞一整页新 PPT（关键点顺序）外加两处讲稿展开。P0 段（幻灯片 3-6）是 0.5+2.5+2+2 = 7 分钟，刚好顶满 `:59` 的 7 分钟。也就是说**任何一处新增都会当场违反 `_style.md:49` 那条硬性约束**，而清单里没有任何一条提示改材料的人去重算。落到课堂上就是：90 分钟的课按材料讲会超时，且超时集中在两段上机时间——最先被挤掉的恰恰是学生自己敲代码的时间。
- 怎么查证：`grep -n "⏱" C:/Users/ziang.xu/Documents/sp/class_four/output/Lecture4_HelloArmor_逐字讲稿.md` 取出 37 个页时长逐段求和，与 `output/script_parts/_style.md:54-68` 的表、`_header.md:13-28` 的表、`build_ppt.py:254-261`、`build_doc.py:173-183` 四处逐段对照。

**6. **37 页成品 PPT 里 15 张配图全是灰色占位框，一张真图都没有。** `build_ppt.py:190-204` 的 `add_image_placeholder` 只画一个浅灰圆角矩形 + 斜体说明文字（`run.text = "🖼  " + label`），脚本里**没有任何 `add_picture` 调用**（已 grep 确认）。实测成品 pptx 第 1/5/6/8/9/10/12/14/16/20/22/24/30/32/33 页各有一个「🖼 …」文本框，例如第 5 页是「🖼 Armor / Lightbar 结构体关系图（left/right → top/bottom → 4 个像素点）」、第 16 页是「🖼 实物装甲板照片，绿点标注 1/2/3/4 号点位置」、第 20 页是「🖼 终端截图：报错信息 + cd 回根目录后正常运行」。**

- 为什么重要：混合型。(b) 必须改的部分：这份「已发布的 37 页成品」**根本不能直接上课**，15 处会投出灰框——清单的 Minor 只点了半成品 PPT 的 slide4 零配图，完全没发现生成版整份是占位图。(a) 需要分版本的部分：其中 3 张占位图的**图片需求本身**在 YOLO 版下作废——第 5 页要的是 left/right→top/bottom 结构图（YOLO 版 left/right 为空）、第 16 页要的是「绿点标注 1/2/3/4」（编号基准与新的 0/1/2/3 下标演示冲突）、第 20 页要的是 CAP_IMAGES 报错截图（YOLO 版不会出这个错）。也就是说补图工作不能照着现有 label 做，得先改 label 再补图。
- 怎么查证：`grep -n "add_picture" build_ppt.py`（零命中）+ 读 `build_ppt.py:190-204`；再用 python-pptx 遍历成品 pptx，筛出 text 含 '🖼' 的形状，得到 15 页清单。

**7. **在错误目录下运行 YOLO 版时的实际失败形态，没有任何材料描述，而它比旧版的报错凶得多。** 链路：`./build/main` 在 `build/` 下跑 → `configs/yolo.yaml` 相对路径找不到 → `tools::load()`（tools/yaml.hpp:12-22）先调 `logger()` → `set_logger()`（tools/logger.cpp:17-18）去创建 `logs/{时间}.log` 的 basic_file_sink → 而 `logs/` 是 `CMakeLists.txt:32` 在**源码目录**建的，`build/` 下不存在 → spdlog 抛异常 → 因为发生在 catch 之外，程序直接 terminate。**

- 为什么重要：属于「必须改」。清单的 Major「现场调试演示的报错文本对不上——照稿念会当场穿帮」只说了旧的 CAP_IMAGES 文本不会出现，没说**取而代之的是什么**，所以按清单修完，讲稿 620-629 那段〔演示〕仍然没有可念的台词，教案 build_doc.py:178「讲解 video.avi 找不到的经典报错」也没有替代品。更关键的是归因教学点变了：旧版是「视频文件在项目根目录」（一句话讲完），新版是「配置、模型、视频、日志目录**四样**都按相对路径找」——这是 README.md:34 明文写的约定，值得单独讲，但现在没有一条材料承载它。
- 怎么查证：顺着读 `lecture4/yolo/tools/yaml.hpp:12-22`（load 的 catch 里先 logger 后 exit）、`lecture4/yolo/tools/logger.cpp:15-27`（basic_file_sink_mt 写 `logs/…`，无 try）、`lecture4/yolo/CMakeLists.txt:30-32`（在 CMAKE_CURRENT_SOURCE_DIR 建 logs/）、`lecture4/yolo/README.md:34`。

**8. **`lecture4/reprojection/` 目录完全没被审计到**，而它的内容和本讲两个新增知识点直接对口：`record.py:7-13` 的 `world2pixel()` 用 `cv.projectPoints` 做重投影并把网格投回画面（正是新增的 `tools/pnp_check.hpp` 要教的东西）；`config.py:22-35` 的 `R_gimbal2imubody` / `R_camera2gimbal` / `t_camera2gimbal` 就是 P6「像素→相机→本体→IMU」整条链的**真实数值**；`record.py:50` 用 `R.from_matrix(...).as_euler("ZYX", degrees=True)` 算 yaw/pitch/roll 并叠加到画面上，和 Task 05 是同一件事的另一种写法。同目录还有 `2024-05-14_10-27-48.txt`（每帧四元数时序）和 `video.py`。全套材料对它零引用。**

- 为什么重要：属于「必须改」的机会成本项。新增内容清单里写着「重投影误差判读口径……本机无 OpenVINO 无法实测，现场跑出 5 px 老师会下不来台」——而这份 Python 脚手架不依赖 OpenVINO（只要 cv2 + scipy），本来可以用来预生成一段重投影演示素材来兜底；P6 那段现在全是口头 + 板书（讲稿 1092 是〔板书〕画四个方框），而这里有现成的真实标定数值可以替换掉抽象讲法（教案 build_doc.py:181 的设计意图里也自承「学生反馈是否偏抽象」）。至少要决定：要么在材料里用起来，要么明确标注「非本讲内容」，否则它就是仓库里一个会误导下一个接手人的孤儿目录。
- 怎么查证：`ls C:/Users/ziang.xu/Documents/sp/class_four/lecture4/reprojection`；读 `config.py:1-40` 与 `record.py:1-60`；再 `grep -rn "reprojection\|重投影" build_doc.py build_ppt.py output/ armor_lecture_notes.md pnp_lecture_notes.md` —— 唯一命中是 `_context.md:28` 和 `_style.md:111/122` 的**禁止条款**（「工程里没有 cv::projectPoints」「不要把上一版讲稿的重投影内容带回来」），与新增的 pnp_check.hpp 正面冲突，这也说明这条禁令本身必须撤销。

**9. **59 MB 的 `assets/` 怎么发到学生手上，没有任何材料交代，而教具清单给的分发方案对 YOLO 版是错的。** `lecture4/yolo/assets/` 有 `video.avi`(54.9 MB)、`yolov5.bin`(4.3 MB)、`yolov5.xml`(200 KB)，三者当前**都是 git 跟踪的**（`git ls-files` 确认），但 README.md:78 写着「`assets/` 不在 lecture2 仓库里（那边 .gitignore 忽略了 assets/），模型与视频是线下分发的」，:85 还建议「若仓库体积吃紧，可以把 assets/ 也加进 .gitignore 改为线下分发」。教案教具清单 build_doc.py:246 写的是「LECTURE4 工程（class/ 与 answer/ 两份）提前拷贝到桌面」。另：`lecture4/yolo/assets/video.avi` 与 `lecture4/class/video.avi` 的 md5 完全相同（335e8050f613636e28238b8727c0d470）。**

- 为什么重要：属于「必须改」，且是清单里环境 blocker 的一个**未覆盖分支**。那条 blocker 只管到 OpenVINO/Eigen3/yaml-cpp/spdlog 这些「装得上就行」的依赖，但即使依赖全装好，学生拿不到 yolov5.xml/.bin 就是 `YOLO detector("configs/yolo.yaml")` 构造失败、一帧都跑不出来。而 README 自己留了一个「可能改成线下分发」的活口，意味着课前必须拍板一个分发方案并写进教具清单；同时 build_doc.py:246 那句「class/ 与 answer/ 两份拷到桌面」在新结构下连目录名都不对（YOLO 版是 `yolo/` 一个目录，answer 在它下面）。视频 md5 相同这点是好消息：可以对学生说「还是上次那段视频」，省一次分发。
- 怎么查证：`ls -la lecture4/yolo/assets/`；`git ls-files lecture4/yolo/assets/`（三个文件都在）；`git check-ignore -v lecture4/yolo/assets/video.avi`（无输出=未被忽略）；读 `lecture4/yolo/README.md:76-86` 与 `build_doc.py:243-248`；`md5sum lecture4/class/video.avi lecture4/yolo/assets/video.avi`。

### 误报风险

清单里我判断最可能是误报的三条，按把握从高到低：

**1）Minor「center 的成因描述在 YOLO 版是错的 @ 讲稿 540 行」—— 几乎可以确定是误报。**
讲稿 540 行原话是「`Armor` 结构体里那个 `center`，不是装甲板四边形的角点。它是两根灯条中心点的平均」。YOLO 构造函数（`tasks/armor.cpp:153`）算的是 `center = (kp[0]+kp[1]+kp[2]+kp[3]) / 4`；而同一个构造函数在 :161-162 定义 `left_center = (kp[0]+kp[3])/2`、`right_center = (kp[1]+kp[2])/2`。这两个式子的平均正好等于四点均值——**「两根灯条中心点的平均」在 YOLO 版仍然数值上成立**，只是那两个中心点不再由 Lightbar 对象承载。更重要的是这句话的教学目的（「别拿 center 去凑 PnP 的四个点」）两版都 100% 正确。按任务纪律「如果某段内容其实两版都适用，就不要报成冲突」，这条该撤。

**2）Major「P4 教师机投影比学生画面多两行，其中一行是下一个 Task 的答案剧透」—— 数错了，且剧透指控不成立。**
学生版 `src/main.cpp` 里 draw_text 有 3 处：:93 tvec、:94 rvec、:106 euler angles（全打 0.0）。参考版 `answer/main.cpp` 有 4 处：:72 tvec、:73 rvec、:82 euler、:88 reproj err。**教师机只多一行（reproj err），不是两行。** 而被说成「下一个 Task 的答案剧透」的那行 euler angles，**学生自己文件里本来就有**（:106，作为 Task 05 的占位符）。讲稿 920 行「画面上是三行字，前两行才是 tvec 和 rvec，第三行是下一个 Task 的，别改错行」描述的正是学生文件，**完全正确，不该被当成待改锚点**。这条的有效内核只剩下「reproj err 这一行全套材料没解释」，而那件事已经被「新增：重投影误差自查」覆盖了——存在重复计数。

**3）Minor「下一讲预告写了一门排课表上没有的课」—— 无法从仓库证实，证据链断在仓库外。**
我在整个 `sp/class_four` 下找不到任何排课表 / 课程表文件（`grep -rl \"排课\\|课程表\\|第五讲\\|lecture5\"` 零命中）。讲稿 1162 行预告的是「相机-云台手眼标定」+「卡尔曼滤波」两项，build_doc.py:264 的教学反思第 4 条也只是自问「是否需要调整预告」。这条断言依赖一份仓库里不存在的排课表，要么证据来自仓库外（那就该注明出处），要么是推断。

**另外两条我核过、确认**不是**误报，不要误撤：**
- Major「巡场话术引导学生去调两个调了没用的参数」**成立**：`use_traditional_` 在 `tasks/yolos/yolov5.cpp:28` 读入，唯一使用处 :184 是注释掉的（`// if (use_traditional_) detector_.detect(...)`）；`binary_threshold_` 在 :20 读入，除 .hpp:31 的声明外全工程无第二处引用。
- Blocker「Task02 标准答案用 armor.left/right」**成立**：`tasks/armor.cpp:148-151` 的 YOLOV5 构造函数初始化列表只有 `confidence(confidence), box(box), points(armor_keypoints)`，left/right 走 `armor.hpp:88` 的 `Lightbar() {};`。

我未能独立核验的一条：Minor「半成品 slide3 的伪代码图把取帧 API 的形状教反了」依赖对 `media/image4.png` 这张截图内容的判读，我没有读该图。方向上可信（yolo 版 `io/camera.hpp:32` 是 `void read(cv::Mat&, timestamp&)`，不返回 Mat），但「图里到底印的什么」需要本人复核。

---

## 10. 人工复核（本节手写，非 agent 结论）

§9 的批判会改变 §3 的若干建议，因此对其关键论断做了独立复核。**以下每一条都是直接跑命令得到的，不是采信 agent 的说法。**

| 论断 | 核实结果 | 证据 |
|---|---|---|
| `homework/tasks/buff_solver.cpp` 的 `solvePnP()` 是空壳 | **成立** | 全文 10 行，函数体为空字符串 |
| homework 的 `io::Camera` 是第三套 API | **成立** | homework: `Camera(double, double, const std::string&)`；yolo: `Camera(const std::string&)` |
| `_style.md` / `_context.md` 含过期事实 | **成立** | `_style.md` 命中 `lecture4/class`×3、`armor.left`×2、`CAP_IMAGES`×1、`纯灯条法`×1；`_context.md` 分别为 5/3/3/2 |
| 分段讲稿与合并稿已漂移 | **成立** | 6/9 份有差异（00:2 行、02:1、04:1、05:1、06:3、07:1；01/03/08 一致） |
| PPT 页脚比幻灯片序号少 1 | **成立** | 第 17 张印 `16`、第 28 张印 `27`；**35/35 页全部错位** |
| 37 页 PPT 配图全是占位框 | **成立** | 15 页含 `🖼` 文本框；`build_ppt.py` 中 `add_picture` **零命中** |
| `lecture4/reprojection/` 未被审计且与本讲对口 | **成立** | 目录存在，`record.py` 确实调用 `projectPoints` |
| `assets/` 已被 git 跟踪（与 README 说法矛盾） | **成立** | `git ls-files` 列出全部三个文件 |
| 误报①：`center` 那条 | **确属误报** | `((kp0+kp3)/2 + (kp1+kp2)/2)/2 ≡ (kp0+kp1+kp2+kp3)/4`，恒等，两版都成立 |
| 误报②：「教师机多两行」 | **确属误报** | 学生版 3 处 `draw_text`、参考版 4 处，**只多一行**；且学生版本身已含 `euler angles`，不构成剧透 |

### 一处修正

批判称「homework 的 CMakeLists.txt 没有 `find_package(OpenVINO)`，学生课后第一步 cmake 就会失败」——**这半句不成立**。顶层确实没有，但 `homework/CMakeLists.txt:15` 有 `add_subdirectory(tasks)`，而 `homework/tasks/CMakeLists.txt:3` 有 `find_package(OpenVINO REQUIRED)`。构建不会因此失败。

### 复核时新发现的一条

两个工程把 OpenVINO 路径写死成了**不同的值**：

- `lecture4/yolo/CMakeLists.txt:18` → `/opt/intel/openvino_2024.6.0/runtime/cmake`
- `lecture4/homework/tasks/CMakeLists.txt:2` → `/usr/lib/cmake/openvino2024.6.0`

同一台机器上不可能两个都对。若 §3-B5 的环境清单按 yolo 版写，学生做进阶作业（homework）时仍会卡住，反之亦然。**教具清单必须同时给出两个路径的改法**，或统一成一个。

### 复核结论

批判的可信度高于它自报的 `medium`：10 条抽查全部复现，仅 1 条有局部偏差。§9 提出的 9 条遗漏应当全部纳入，其中两条要**提升为前置闸门**（与 §2-B1 并列）：

1. **`_context.md` / `_style.md` 必须先改** —— 它们自称「唯一素材来源」且带「红线，违反即作废」的强制力，不改就会把修好的 blocker 原样复活。
2. **分段讲稿与合并稿必须同批改** —— 两处副本，只改一处等于没改。

§3-M4（进阶作业）的改法要按 §9-1 重写：不是重新设计作业，而是把学生指向已经写好的 `lecture4/homework/` 脚手架。

