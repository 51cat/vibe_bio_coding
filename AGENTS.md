# AGENTS.md

This document provides guidance for agentic coding agents working in this repository.

## Project Overview

This is a Python-based multi-agent system for bioinformatics file format conversion. The project uses LangChain for agent orchestration.

## Build/Lint/Test Commands

### Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Testing

```bash
# Run all tests
pytest

# Run a single test file
pytest tests/test_agent.py

# Run a single test function
pytest tests/test_agent.py::test_function_name

# Run tests with verbose output
pytest -v

# Run tests with coverage
pytest --cov=agents tests/
```

### Linting and Formatting

```bash
# Run ruff linter (recommended)
ruff check .

# Run ruff with auto-fix
ruff check --fix .

# Format code with ruff
ruff format .

# Run type checking with mypy
mypy agents/

# Run all checks (lint + format check + typecheck)
ruff check . && ruff format --check . && mypy agents/
```

## Project Structure

```
agents/
├── config_base.json         # Global configuration (API keys, base URLs)
├── format_transfer/         # Agent: bioinformatics format conversion
│   ├── config.json          # Agent-specific config (overrides global)
│   ├── agent.py             # Agent main logic and orchestration
│   ├── llm.py               # LLM API wrapper
│   ├── promopt.py           # Prompt template management
│   └── tools.py             # Tool functions for this agent
└── utils/                   # Shared utilities for all agents
```

## Code Style Guidelines

### Imports

```python
# Standard library imports first
import os
import json
from typing import Dict, List, Optional, Any

# Third-party imports second
from langchain.agents import AgentExecutor, create_react_agent
from langchain.schema import HumanMessage

# Local imports last
from utils.config import load_config
from tools import parse_fasta, convert_format
```

### Naming Conventions

- **Files**: lowercase with underscores (e.g., `format_transfer.py`)
- **Classes**: PascalCase (e.g., `FormatTransferAgent`)
- **Functions/Methods**: snake_case (e.g., `convert_fasta_to_fastq`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_TIMEOUT_SECONDS`)
- **Private methods**: prefix with underscore (e.g., `_validate_input`)
- **Config keys**: lowercase with underscores in JSON

### Type Annotations

Always use type hints for function signatures:

```python
def convert_format(
    input_file: str,
    output_format: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Convert file to specified format.
    
    Args:
        input_file: Path to input file
        output_format: Target format (fasta, fastq, vcf, bed)
        options: Optional conversion parameters
        
    Returns:
        Dictionary with conversion results
        
    Raises:
        ValueError: If format is not supported
        FileNotFoundError: If input file does not exist
    """
    pass
```

### Error Handling

- Raise specific exceptions with descriptive messages
- Use custom exception classes for agent-specific errors
- Log errors before re-raising when appropriate

```python
class FormatConversionError(Exception):
    """Raised when format conversion fails."""
    pass

def convert_file(input_path: str, target_format: str) -> str:
    if target_format not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format: {target_format}. "
            f"Supported formats: {', '.join(SUPPORTED_FORMATS)}"
        )
    try:
        result = _do_conversion(input_path, target_format)
    except IOError as e:
        raise FormatConversionError(f"Failed to read {input_path}: {e}") from e
    return result
```

### Configuration Management

1. Global config in `agents/config_base.json` contains shared settings (API keys, base URLs)
2. Agent-specific config in `agents/<agent_name>/config.json` overrides global settings
3. Never hardcode sensitive values (API keys, passwords)
4. Add config files to `.gitignore`

### Agent Module Structure

Each agent module must follow this pattern:

| File | Purpose |
|------|---------|
| `config.json` | Agent-specific configuration |
| `agent.py` | Main agent class and entry point |
| `llm.py` | LLM client wrapper |
| `promopt.py` | Prompt templates |
| `tools.py` | Callable tool functions |

### Adding a New Agent

1. Create directory: `agents/<agent_name>/`
2. Add required files: `config.json`, `agent.py`, `llm.py`, `promopt.py`, `tools.py`
3. Update `config.json` to override any global settings needed
4. Import shared utilities from `agents/utils/`

## Dependencies

Core dependencies (add to requirements.txt):
- langchain
- langchain-openai
- pydantic

Dev dependencies:
- pytest
- pytest-cov
- ruff
- mypy

## Important Notes

- Configuration files may contain sensitive API keys - never commit them
- The README is in Chinese; maintain bilingual documentation when extending
- Use the `agents/utils/` directory for shared code across agents
- Each agent should be self-contained and independently runnable
