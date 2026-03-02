# Agent 工具说明文档

## 📁 项目结构

```
├── agents/                         # 所有 Agent 模块的根目录
│   ├── config_base.json            # 全局基础配置（API Key、Base URL 等）
│   ├── format_transfer/            # Agent：生物信息文件格式转换
│   │   ├── agent.py                # Agent 主逻辑
│   │   ├── config.json             # 该 Agent 的专属配置
│   │   ├── llm.py                  # LLM 模型调用封装
│   │   ├── promopt.py              # Prompt 模板管理
│   │   └── tools.py                # 工具函数集合
│   └── utils/                      # 所有 Agent 共享的公共工具库
└── README.md                       # 项目说明文档
```

---

## 🏗️ 架构说明

本项目采用 **多 Agent 目录化管理** 的结构：

- `agents/config_base.json` 作为**全局配置中心**，统一管理所有 Agent 的外部服务配置
- `agents/` 目录下每一个子目录代表一个**独立的 Agent**
- 每个 Agent 目录内含独立的 `config.json`，可覆盖全局配置
- `agents/utils/` 作为**公共层**，供所有 Agent 共享调用

```
agents/
├── config_base.json    ← 全局配置（API Key、Base URL 等）
├── format_transfer/    ← Agent 1
│   └── config.json     ← Agent 专属配置
├── another_agent/      ← Agent 2（未来扩展）
│   └── config.json
└── utils/              ← 所有 Agent 共享
```

---

## ⚙️ 配置文件说明

### `config_base.json` — 全局基础配置

统一管理所有 Agent 依赖的外部服务配置，所有 Agent 均从此文件读取默认配置，**避免硬编码**。

```json
{
  "llm": {
    "api_key": "your-api-key",
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-4o",
    "temperature": 0.7,
    "max_tokens": 2048
  }
}
```

### `format_transfer/config.json` — Agent 专属配置

存放该 Agent 个性化的配置项，加载时与 `config_base.json` 合并，**同名字段以此文件为准**。

```json
{
  "llm": {
    "model": "gpt-4o-mini",
    "temperature": 0.3
  },
  "agent": {
    "supported_formats": ["fasta", "fastq", "vcf", "bed"]
  }
}
```

> ⚠️ **注意**：两个配置文件均可能包含敏感信息，请务必加入 `.gitignore`，避免泄露 API Key。
> ```bash
> # .gitignore
> agents/config_base.json
> agents/**/config.json
> ```

---

## 📦 安装

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 可选：安装生物信息工具
conda install -c bioconda seqkit
```

---

## 📦 Agent 内部结构约定

每个 Agent 目录遵循统一的文件结构：

| 文件          | 职责                                             |
| ------------- | ------------------------------------------------ |
| `config.json` | Agent 专属配置，加载时与 `config_base.json` 合并 |
| `agent.py`    | Agent 入口与主流程，协调内部各模块               |
| `llm.py`      | 封装 LLM 调用，读取合并后的配置发起请求          |
| `promopt.py`  | 维护该 Agent 专属的 Prompt 模板                  |
| `tools.py`    | 该 Agent 可调用的具体工具函数                    |

---

## 🤖 现有 Agent

### `format_transfer` — 文件格式转换 Agent

负责将生物信息学文件和表格文件在不同格式之间进行智能转换。

#### 生物信息格式转换

- FASTA ↔ FASTQ
- VCF 格式解析与转换
- BED / GFF / GTF 等注释格式互转

#### 表格格式转换

- CSV ↔ TSV
- CSV ↔ Excel (.xlsx)
- TSV ↔ Excel (.xlsx)
- 查看Excel文件中的所有sheet名称

#### 可用工具

| 工具 | 功能 |
|------|------|
| `fastq2fasta` | FASTQ 转 FASTA |
| `index_fasta` | 创建 FAI 索引 |
| `csv_to_tsv` | CSV 转 TSV |
| `tsv_to_csv` | TSV 转 CSV |
| `csv_to_excel` | CSV 转 Excel |
| `excel_to_csv` | Excel 转 CSV |
| `tsv_to_excel` | TSV 转 Excel |
| `excel_to_tsv` | Excel 转 TSV |
| `convert_table_format` | 通用表格格式转换 |
| `list_excel_sheets` | 列出 Excel 所有 sheet |
| `create_output_dir` | 创建输出目录 |
| `create_workdir` | 创建工作目录 |
| `zip_directory` | 打包目录 |

---

## 🛠️ `utils/` — 公共工具库

所有 Agent 共享的通用能力，避免重复实现，例如：

- 日志记录
- **读取并合并 `config_base.json` 与 Agent 专属 `config.json`**
- 公共数据处理

---

## ➕ 新增 Agent

按照以下规范在 `agents/` 下新建目录，并添加专属 `config.json` 覆盖所需的全局配置：

```bash
agents/
└── your_agent_name/
    ├── config.json      # 按需覆盖 config_base.json 中的配置
    ├── agent.py
    ├── llm.py
    ├── promopt.py
    └── tools.py
```