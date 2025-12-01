# Anthropic Claude Example

Test Anthropic Claude models with tool use in EvalView.

## Quick Start

### First Time Setup

```bash
# 1. Go to EvalView root directory
cd /path/to/EvalView

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate it
source venv/bin/activate

# 4. Install EvalView + Anthropic SDK
pip install -e .
pip install anthropic

# 5. Set your API key (in .env.local or environment)
export ANTHROPIC_API_KEY=your-api-key
# Or add to examples/anthropic/.env.local

# 6. Run the test (from root directory)
evalview run examples/anthropic
```

### Already Set Up?

```bash
cd /path/to/EvalView
source venv/bin/activate
evalview run examples/anthropic
```

That's it! EvalView will:
- Auto-detect your Anthropic API key
- Run the test case against Claude
- Evaluate tool usage and output quality

## Setup Details

### Environment Variables

```bash
# Required: Anthropic API key
export ANTHROPIC_API_KEY=your-api-key

# Optional: Choose evaluation provider (if you have multiple API keys)
export EVAL_PROVIDER=anthropic  # or openai, gemini, grok

# Optional: Override evaluation model
export EVAL_MODEL=claude-haiku-4-5-20251001  # faster/cheaper for eval
```

### Custom Tool Executor (Optional)

For real tool execution, create a tool executor:

```python
# tools.py
def execute_tool(name: str, input: dict) -> str:
    """Execute a tool and return result."""
    if name == "get_weather":
        city = input.get("city", "unknown")
        return f"Weather in {city}: 72F, sunny"
    elif name == "convert_temperature":
        value = input.get("value", 0)
        from_unit = input.get("from_unit", "celsius")
        if from_unit == "celsius":
            return str(value * 9/5 + 32) + "F"
        return str((value - 32) * 5/9) + "C"
    return f"Unknown tool: {name}"
```

## Supported Models (November 2025)

| Model | API ID | Input/MTok | Output/MTok |
|-------|--------|------------|-------------|
| **Opus 4.5** | `claude-opus-4-5-20251101` | $5 | $25 |
| **Sonnet 4.5** | `claude-sonnet-4-5-20250929` | $3 | $15 |
| **Haiku 4.5** | `claude-haiku-4-5-20251001` | $1 | $5 |
| Opus 4.1 | `claude-opus-4-1-20250805` | $15 | $75 |

## Tool Use

The adapter supports Anthropic's native tool use format:

```yaml
adapter: anthropic
model: claude-sonnet-4-5-20250929

tools:
  - name: get_weather
    description: Get current weather for a city
    input_schema:
      type: object
      properties:
        city:
          type: string
          description: City name
      required:
        - city
```

## Links

- **Anthropic Docs**: https://docs.anthropic.com/
- **Tool Use Guide**: https://docs.anthropic.com/en/docs/build-with-claude/tool-use
- **API Reference**: https://docs.anthropic.com/en/api/messages
