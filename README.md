# 临床试验方案助手

[English README](README.en.md)

这是一个用于创建和审查临床试验方案的 Codex Skill，适用于研究者发起研究（IIT）、药物/器械注册上市前临床试验、上市后四期研究，以及真实世界研究/真实世界证据（RWS/RWE）方案。

本 Skill 的核心思路是“先收集必要信息，再设计章节，再逐章生成或审查”。它不会在用户只给出一个题目时直接生成完整方案，而是先通过 P0/P1/P2 信息门和章节确认流程，把方案结构、关键假设和缺失信息理清楚。

## 主要能力

- 创建临床试验方案目录和正文草稿。
- 审查已有临床试验方案，并尽量避免大规模重写用户原文。
- 根据研究类型将章节分为必要、推荐、可选和暂不建议纳入。
- 使用全局和章节级 P0/P1/P2 信息门控制提问节奏。
- 从 Word、Excel、PowerPoint、PDF、CSV/TSV、文本和 Markdown 文件中抽取材料。
- 将用户上传材料用于回答后续问题，并作为正文撰写和审查的依据。
- 在需要时检索 PubMed、ClinicalTrials.gov 和 openFDA label 作为外部证据来源。
- 对生成或审查后的 Word 文档做全局样式统一。

## 安装

```bash
codex skills install https://github.com/mattzhangli008-sys/clinical-trial-protocol-assistant.git
```

如需进行较重的文件抽取，进入 Skill 目录后安装 Python 依赖：

```bash
python -m pip install -r requirements.txt
```

## 典型流程

### 新建方案模式

1. 先询问研究题目/临床问题、研究性质大类，以及是否有已有材料。
2. 如果用户上传 Word、Excel、PPT、PDF 等材料，先抽取为材料索引。
3. 根据研究画像推荐必要、推荐、可选和暂不建议章节。
4. 用户确认要纳入哪些章节后，形成执行计划。
5. 对每个章节分别收集 P0/P1/P2 信息，再逐章生成。
6. 所有章节确认后，进行跨章节一致性检查，并可生成统一样式的 Word 文件。

### 审查模式

1. 抽取已有方案和辅助材料。
2. 形成文档画像，并检查章节覆盖情况。
3. 识别缺失的必要章节，并询问是否纳入推荐或可选章节。
4. 形成审查执行计划。
5. 按章节进行审查，结合文档原文、用户补充信息和必要的外部证据。
6. 输出问题、原文证据、风险说明、修改建议和小范围建议改写。

## 材料抽取

主要脚本：

```bash
python scripts/extract_materials.py file1.docx file2.xlsx file3.pdf --out material_index.json
```

可选生成整篇 Markdown 视图：

```bash
python scripts/extract_materials.py protocol.docx --include-markdown --out material_index.json
```

抽取脚本会优先使用更强的格式处理库：

- `python-docx`：抽取 DOCX 段落和表格。
- `openpyxl`：抽取 XLSX/XLSM 工作表。
- `python-pptx`：抽取 PPTX 幻灯片文本和表格。
- `pdfplumber`、`PyMuPDF`、`pypdf`：按顺序用于 PDF 抽取。
- `markitdown`：可选生成整篇文档的 Markdown 视图。

如果某个依赖不可用，脚本会在输出索引中记录降级方式或错误信息。

## 重要说明

本 Skill 用于辅助临床试验方案撰写和审查，不能替代医学、统计、伦理、法规或法律专业人员的正式审核。

对于医学、法规、终点、安全性、样本量、真实世界研究方法等关键内容，应结合外部证据或用户提供材料，不应只依赖模型记忆。
