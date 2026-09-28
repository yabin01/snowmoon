# Snowmoon / 《雪月》

Vitalik Buterin 的长篇小说 **Snowmoon** 的中文译本与英文原版，A5 开本排版 PDF。

原著：<https://vitalik.eth.limo/snowmoon/>（32 章，约 10.3 万英文词）

## 文件

| 文件 | 说明 |
| --- | --- |
| `Snowmoon (中文版).pdf` | 中文全译本，248 页 |
| `Snowmoon (English).pdf` | 英文原版全文，307 页 |
| `html/Snowmoon-zh.html` | 中文版单文件 HTML（可直接在浏览器阅读、打印） |
| `html/Snowmoon-en.html` | 英文版单文件 HTML |
| `build/` | 制作流水线：抓取、抽取、译稿、校验、组装、渲染 |

## 内容

故事在维里迪亚（公民格拉迪亚斯）与泽戈（少年泽伊）两条主线之间交替展开，
背景是一个把零知识证明、抽签遴选、二次方资助、土地税与本地 AI 当作日常基础设施的世界。

排版保留了原站的视觉要素：

- 对话按说话人着色
- 「手持设备」深色终端界面表格
- 明盆泰棋局 SVG 图
- 泽戈语段落卡片（原文中的虚构语言，罗马字保留未译）

## 制作流程

1. `build/extract.py` — 抓取 32 章 HTML，解析为带 `@@ID|类型` 标记的结构化文本（`build/src/`）
2. 按 `build/GUIDE.md`（术语表 + 格式规范）分章翻译，产出 `build/zh/`
3. `build/validate.py` — 校验结构完整性；`build/normalize.py` — 统一专名译法
4. `build/assemble.py` — 组装单文件 HTML（目录、扉页、许可声明）
5. `build/render_pdf.py` — Chrome headless 打印为 A5 PDF

## 许可

原著 Snowmoon 由 Vitalik Buterin 以 **GPL v3** 发布。本仓库的译文与排版同样遵循 GPL v3，
本仓库 LICENSE 文件即为该协议原文。

## 声明

原著文字全部由 Vitalik Buterin 本人撰写；本仓库的中文译文为 AI 辅助翻译，
仅供学习交流，如有错译欢迎提 issue 指正。
