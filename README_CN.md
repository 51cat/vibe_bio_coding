# Vibe Bio Coding

基于 LangChain 的生物信息学文件格式转换智能助手。

## 项目简介

本项目是一个多 Agent 系统，专门用于生物信息学文件格式转换。通过自然语言交互，用户可以轻松完成 FASTQ/FASTA 格式转换、索引创建、工作目录管理等操作。

## 功能特性

- **格式转换**: FASTQ 转 FASTA（支持压缩输出）
- **索引创建**: 为 FASTA 文件创建 FAI 索引
- **工作目录管理**: 自动创建带时间戳的工作目录
- **文件打包**: 将目录压缩为 ZIP 文件
- **流式输出**: 实时显示大模型响应

## 项目结构

```
agents/
├── config_base.json         # 全局配置（API密钥等）
├── public_tools.py          # 公共工具函数
└── format_transfer/         # 格式转换 Agent
    ├── agent.py             # Agent 主程序
    ├── config.json          # Agent 专属配置
    ├── llm.py               # LLM 封装类
    ├── promopt.py           # 系统提示词
    └── tools.py             # 格式转换工具
```

## 安装

### 依赖安装

```bash
pip install langchain langchain-core langchain-openai
conda install -c bioconda seqkit
```

### 配置

编辑 `agents/config_base.json`:

```json
{
    "llm": {
        "model": "your-model-name",
        "temperature": 0.1,
        "api_key": "your-api-key",
        "base_url": "your-api-base-url"
    }
}
```

## 使用方法

### 交互模式

```bash
cd agents/format_transfer
python agent.py
```

### 示例对话

```
用户: 把 /path/to/reads.fq.gz 转成 FASTA 格式，输出到 ./output/

[调用工具: fastq2fasta]
  结果: {"success": true, "output_file": "./output/reads.fa"}...

已成功将文件转换为 FASTA 格式，输出路径: ./output/reads.fa
```

### 可用工具

| 工具 | 功能 | 参数 |
|------|------|------|
| `fastq2fasta` | FASTQ 转 FASTA | input_file, output_file, compress, force |
| `index_fasta` | 创建 FAI 索引 | input_file, force |
| `create_workdir` | 创建工作目录 | workdir_name, parent_dir, prefix |
| `create_output_dir` | 创建输出目录 | dir_path, exist_ok |
| `zip_directory` | 打包目录 | source_dir, output_file, force |

## 开发指南

### 添加新工具

1. 在 `tools.py` 或 `public_tools.py` 中使用 `@tool` 装饰器定义函数
2. 在 `agent.py` 中将工具添加到 `self.tools` 列表

### 添加新 Agent

```bash
mkdir agents/your_agent
touch agents/your_agent/{agent.py,config.json,llm.py,promopt.py,tools.py}
```

## 注意事项

- 配置文件包含敏感信息，请勿提交到版本控制
- FASTA 索引仅支持未压缩的 FASTA 文件
- 所有文件操作会检查路径存在性，防止意外覆盖

## 许可证

MIT License
