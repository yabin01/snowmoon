# Snowmoon 中文翻译规范（所有译者必须严格遵守）

## 一、任务

把 `src/chNN.md`（英文抽取稿）逐块翻译成 `zh/chNN.md`（中文），**不改变任何结构标记**。

## 二、文件格式（极其重要）

源文件由若干「块」组成，每个块以 `@@ID|类型[|参数]` 开头（单独一行），后面跟内容行，块之间空行分隔。

你必须：

1. **原样保留每一个 `@@...` 标记行**（ID、类型、参数全部不变，一个都不能漏、不能改顺序、不能合并或拆分）。
2. 只翻译标记行**下面**的内容文字。
3. 没有任何内容的标记（`@@ID|hr`、`@@ID|raw`、`@@ID|raw-svg`、`|device` 的子块 `raw-svg`）只输出标记行本身，不要加内容。
4. 空行分隔保持与原文件一致（每个内容块后跟一个空行；`@@ID|hr` 后面紧跟下一个标记，无需空行，照抄原样即可）。

### 块类型说明

| 标记 | 含义 | 处理方式 |
|---|---|---|
| `@@ID\|h1` | 章标题 `Chapter N` | 译为 `第 N 章` |
| `@@ID\|h2` | 二级标题 | 翻译 |
| `@@ID\|open\|place=X\|date=Y` | 章首时地行 | 地名音译，月名按术语表译；格式 `@@ID\|open\|place=梅尔丹，维里迪亚\|date=3724 雪月 3` |
| `@@ID\|scene\|place=X\|date=Y` | 场景切换时地行 | 同上 |
| `@@ID\|p` | 正文段 | 翻译 |
| `@@ID\|q` | 引用块 | 翻译（多行则逐行） |
| `@@ID\|list\|ul` / `\|ol` | 列表，其后每行以 `- ` 开头 | 逐条翻译，保留 `- ` 前缀 |
| `@@ID\|hr` | 分隔线 | 只保留标记行 |
| `@@ID\|raw` / `@@ID\|raw-svg` | 图形（SVG/特殊卡片），无需翻译 | 只保留标记行 |
| `@@ID\|device\|wide` 或 `\|narrow`（可再加 `\|left`） | 一个「设备屏幕」容器 | 只保留标记行；其内部子块见下 |
| `@@ID.K\|table` | 设备里的表格 | 见下 |
| `@@ID.K\|dvtext` | 设备里的文字 | 翻译 |
| `@@ID.K\|dvlist` | 设备里的列表 | 逐条翻译，保留 `- ` |

### 表格格式

```
@@1.18.0|table
| Vote on: Badra St #1103
| Emerald AI summary: Five-storey apartment building.
| [slider]  -5 0 5
```

- 每行以 `| ` 开头；**多列时单元格之间用 ` ‖ `（U+2016 双竖线）分隔**，必须原样保留分隔符数量与顺序。
- 单元格若以 `<c2>`、`<c3>` 开头，表示该格跨列，**必须原样保留前缀**再接译文（例：`<c2>巴德拉街 1103 号`）。
- 单元格若以 `<r2>` 开头，同理保留。
- 第一行常常是表头（`<th>`），照译即可。

## 三、行内标记（必须原样保留结构）

- **对话着色**：原文 `{{26.666666666666664|"Five points for me!"}}`
  → 译文 `{{26.666666666666664|“五分归我！”}}`
  **色相数字一个字都不能改**，只替换竖线后面的文字；中文对话使用全角引号 `“ ”`。
  注意：有时着色片段只是句子的一部分，后面还有叙述文字，例如
  `{{93.33|"Pause, I want to enjoy the view"}}, Gladias said...`
  → `{{93.33|“暂停，我想看看风景”}}，格拉迪亚斯说……`
- `*斜体*` → 保留 `*...*`，翻译内部文字。
- `` `代码` `` → 保留反引号。
- `[button: Select]` → `[button: 选择]`（保留 `[button: ...]` 外壳）。
- `[slider]` → 原样保留，不翻译。
- `[input: xxx]` → 原样保留。

## 四、文风要求

- 用**自然、流畅的现代汉语书面语**，不要翻译腔、不要欧化长句的僵硬直译；长句可适当拆分，但**不要增删情节内容**。
- 保留原文那种平静、克制、细节丰富的叙事语气；Vitalik 的文风偏说明性，不要过度文学化或加油添醋。
- 对话要口语化、符合说话人身份（孩子、老人、官员等）。
- **不要添加译注、括号说明或任何原文没有的内容。**
- 专有名词首次出现不必加注。

## 五、专有名词术语表（必须统一使用）

### 人物
Zei 泽伊 · Gladias 格拉迪亚斯 · Bai 白 · Seila 塞拉 · Delwart 德尔瓦特 · Deluin 德卢因 · Fin 芬 · Den 登 · Mov 莫夫 · Zven 兹文 · Lily 莉莉 · Jahn 扬 · Verdow 韦尔多 · Hreda 赫雷达 · Vil 维尔 · Pan 潘 · Mu 穆 · Fe 费 · Dza 扎 · Dze 泽 · Sylka 希尔卡 · Daia 代亚 · Tafindel 塔芬德尔 · Evelor 埃韦洛尔 · Gallowar 加洛瓦尔 · Thaldur 塔尔杜尔 · Febric 费布里克 · Telroy 特尔罗伊 · Telpo 特尔波 · Utaku 乌塔库 · Balme 巴尔姆 · Lektor 莱克托

### 地理与政体
Veridia 维里迪亚（Veridian 维里迪亚的；Veridians 维里迪亚人） · Meldan 梅尔丹（首都） · Kalimar 卡利马尔（城区） · Northglade 北林 · Elenar Forest 埃莱纳尔森林 · Redshire 雷德希尔 · Northshore 北岸 · Plum Harbor 梅港 · Dzego 泽戈（国） · Sadzu Du 萨祖都（泽戈都城） · Pafogai Du 帕福盖都 · Dzegoban 泽戈语 · Dzegojan 泽戈人 · Freetown 自由城 · United Cities 联合城邦 · Arctics 北极邦（Arctic 北极的） · Empire 帝国 · Parliament 议会 · Senator 参议员 · Courts 法院

### 组织与事物
Emerald 翡翠（本地 AI） · hand device 手持设备 · drone 无人机 · glider 滑翔翼 · helisport 旋翼运动 · Silverchat 银聊 · Hydrafill 海德拉菲尔 · Bluewhale 蓝鲸 · Dreadknot 德雷德诺特 · Minpentai 明盆泰（棋戏） · rubric 评分细则 · Min 明（货币） · TAU 保留 TAU · GPH 保留 GPH · Sentinels 哨兵 · Keepers 守护者 · Keeper 守护者 · Heralds 传令官 · Acolyte 侍从 · Order 教团 · Steering Group 指导小组 · Institute 学院 · Graph 图谱

### 概念
zero-knowledge 零知识 · cryptographic attestation 密码学证明 · sortition 抽签遴选 · public aesthetics tax 公共审美税 · land tax 土地税 · composite land tax 综合土地税 · quadratic funding 二次方资助 · negentropy 负熵 · privacy 隐私 · autobus 自动驾驶巴士 · sky bridge 天桥

### 月份名
Snowmoon 雪月 · Rainmoon 雨月 · Firemoon 火月 · Fruitmoon 果月 · Harvestmoon 收获月 · Windmoon 风月 · Bloomtime 花时 · Frostime 霜时 · Mistime 雾时 · Grasstime 草时 · Grapetime 葡萄时

### 街道/地址
`Badra St #1103` → `巴德拉街 1103 号`（St 译作「街」）

## 六、遇到术语表以外的新专名

按音译规则自行翻译，保持全篇一致，并在**最后回复中列出**你新造的译名（格式：`原文 -> 译文`），供全篇统一。

## 七、完成后

用 Write 工具把译文写入 `zh/chNN.md`（UTF-8）。不要改动 `src/` 下任何文件。
