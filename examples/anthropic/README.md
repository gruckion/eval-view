# Anthropic Claude Example

Test Anthropic Claude models with tool use in EvalView.

## Setup

### 1. Set Environment Variables

```bash
export ANTHROPIC_API_KEY=your-api-key
```

### 2. Define Tools (Optional)

For tool use testing, define tools in your test case or create a tool executor:

```python
# tools.py
def execute_tool(name: str, input: dict) -> str:
    """Execute a tool and return result."""
    if name == "get_weather":
        city = input.get("city", "unknown")
        return f"Weather in {city}: 72F, sunny"
    elif name == "calculator":
        op = input.get("operation")
        a, b = input.get("a", 0), input.get("b", 0)
        if op == "add":
            return str(a + b)
        elif op == "multiply":
            return str(a * b)
    return f"Unknown tool: {name}"
```

### 3. Run EvalView Test

```bash
evalview run --pattern examples/anthropic/test-case.yaml
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
