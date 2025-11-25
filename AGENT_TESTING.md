# Agent Testing Plan

## Overview

This document tracks EvalView's compatibility testing with popular agent frameworks.

## Testing Goals

1. **Compatibility**: Verify EvalView works with each framework
2. **Accuracy**: Ensure evaluators correctly assess agent behavior
3. **Documentation**: Create working examples for each framework
4. **Bug Discovery**: Identify and fix issues

## Framework Support Matrix

### Currently Supported

| Framework | Status | Adapter | Example | Notes |
|-----------|--------|---------|---------|-------|
| **LangGraph** | ✅ Supported | `HTTPAdapter` | [examples/langgraph/](examples/langgraph/) | Most popular for production |
| **CrewAI** | ✅ Supported | `HTTPAdapter` | [examples/crewai/](examples/crewai/) | Multi-agent systems |
| **AutoGen** | ✅ Supported | `HTTPAdapter` | [examples/autogen/](examples/autogen/) | Enterprise multi-agent |
| **Dify** | ✅ Supported | `HTTPAdapter` | [examples/dify/](examples/dify/) | Visual workflow builder |
| **OpenAI Assistants** | ✅ Supported | `HTTPAdapter` | [examples/openai-assistants/](examples/openai-assistants/) | Official OpenAI framework |

### Planned Frameworks

| Framework | Status | Adapter | Notes |
|-----------|--------|---------|-------|
| **LangChain** | ⏳ Planned | `HTTPAdapter` | Community contribution welcome |
| **LlamaIndex** | ⏳ Planned | `HTTPAdapter` | RAG-focused agents |
| **Anthropic Claude** | ⏳ Planned | `HTTPAdapter` | Tool use via Messages API |
| **Haystack** | ⏳ Planned | `HTTPAdapter` | NLP pipelines, agents |

### Community Requested (Contributions Welcome)

| Framework | Status | Notes |
|-----------|--------|-------|
| **Semantic Kernel** | ⏳ Planned | Microsoft's framework |
| **Langroid** | ⏳ Planned | Multi-agent, good docs |
| **Phidata** | ⏳ Planned | Growing community |
| **MetaGPT** | ⏳ Planned | Multi-agent for code |
| **MemGPT** | ⏳ Planned | Memory management |
| **Custom REST APIs** | ✅ Supported | Use `HTTPAdapter` |

[Request framework support →](https://github.com/hidai25/EvalView/discussions)

## Test Scenarios

For each framework, test these scenarios:

### 1. Simple Single-Tool Call
```yaml
name: "Simple tool call test"
input:
  query: "What's 2+2?"
expected:
  tools: [calculator]
  output:
    contains: ["4"]
thresholds:
  min_score: 80
```

### 2. Multi-Tool Sequence
```yaml
name: "Multi-step reasoning"
input:
  query: "Get weather for New York and convert temp to Celsius"
expected:
  tools: [get_weather, convert_temperature]
  sequence: [get_weather, convert_temperature]
  output:
    contains: ["celsius", "temperature"]
thresholds:
  min_score: 75
```

### 3. Error Handling
```yaml
name: "Invalid input handling"
input:
  query: "Get weather for XYZ123INVALID"
expected:
  tools: [get_weather]
  output:
    contains: ["error", "not found", "invalid"]
thresholds:
  min_score: 70
```

### 4. Cost & Latency Thresholds
```yaml
name: "Performance test"
input:
  query: "Simple query"
expected:
  tools: [some_tool]
thresholds:
  min_score: 80
  max_cost: 0.10
  max_latency: 3000
```

## Testing Process

### Step 1: Setup Framework
```bash
# Create virtual environment
python -m venv venv-{framework}
source venv-{framework}/bin/activate

# Install framework
pip install {framework}

# Create minimal agent
# See examples/{framework}/agent.py
```

### Step 2: Create Test Agent
Each agent should have:
- REST API endpoint (for HTTPAdapter)
- At least 2-3 tools/functions
- Proper error handling
- Cost/latency tracking (if possible)

### Step 3: Write Test Cases
```bash
mkdir -p examples/{framework}/test-cases
# Create YAML test cases
```

### Step 4: Run Tests
```bash
# Start agent backend
python examples/{framework}/agent.py

# Run EvalView tests
evalview run examples/{framework}/.evalview/config.yaml
```

### Step 5: Document Results
- Update testing matrix above
- Note any issues or limitations
- Document setup instructions
- Create example in `examples/{framework}/`

## Documentation per Framework

For each tested framework, create:

```
examples/{framework}/
├── README.md              # Setup and running instructions
├── agent.py              # Sample agent implementation
├── requirements.txt      # Framework dependencies
├── .evalview/
│   └── config.yaml      # EvalView configuration
└── test-cases/
    ├── simple.yaml      # Basic test
    ├── multi-tool.yaml  # Complex test
    └── error.yaml       # Error handling
```

## Success Criteria

A framework passes testing if:

✅ All test scenarios execute without errors
✅ Tool call evaluation works correctly
✅ Output evaluation produces reasonable scores
✅ Cost/latency tracking works (if applicable)
✅ Example code is documented and runs
✅ Any framework-specific quirks are documented

## Known Issues Tracking

| Issue | Framework | Severity | Status | Workaround |
|-------|-----------|----------|--------|------------|
| - | - | - | - | - |

## Testing Roadmap

We're actively expanding framework support based on community feedback.

**Current priorities:**
- LangChain integration
- LlamaIndex support
- Additional adapter types

## Notes

- Focus on production-ready frameworks first
- Document setup complexity (easy, medium, hard)
- Track which adapters work best
- Gather user pain points for future features

## Contributing

Want to add support for a framework?

1. Create example in `examples/{framework}/`
2. Add test cases
3. Submit PR
4. Update this document

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
