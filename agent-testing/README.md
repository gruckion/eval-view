# Agent Testing for EvalView

## Overview

This directory contains test agents for validating EvalView compatibility with popular agent frameworks.

## Goal

Test EvalView with **20+ agent frameworks** to ensure:
- ✅ Tool call evaluation works correctly
- ✅ Output quality assessment is accurate
- ✅ Cost and latency tracking functions
- ✅ Documentation and examples are complete

## Quick Start

### 1. Test Reference Agent (Validation)

```bash
# Terminal 1: Start reference agent
cd agent-testing/reference-agent
pip install -r requirements.txt
python agent.py

# Terminal 2: Run tests
cd agent-testing/reference-agent
evalview run
```

### 2. Run All Tests (Automated)

```bash
cd agent-testing
./test-runner.sh
```

This will automatically:
- Install dependencies for each framework
- Start agents in background
- Run EvalView tests
- Generate summary report

## Testing Status

See [AGENT_TESTING.md](../AGENT_TESTING.md) for complete testing matrix.

### Quick Status

| Framework | Status | Example |
|-----------|--------|---------|
| Reference Agent | ✅ Ready | `agent-testing/reference-agent/` |
| LangGraph | ✅ Ready | `examples/langgraph/` |
| CrewAI | ✅ Ready | `examples/crewai/` |
| AutoGen | ✅ Ready | `examples/autogen/` |
| Dify | ✅ Ready | `examples/dify/` |
| OpenAI Assistants | ✅ Ready | `examples/openai-assistants/` |

## Directory Structure

```
agent-testing/
├── README.md                    # This file
├── test-runner.sh              # Automated test runner
├── reference-agent/            # FastAPI test agent
│   ├── agent.py
│   ├── requirements.txt
│   ├── .evalview/
│   │   ├── config.yaml
│   │   └── test-cases/
│   └── README.md
├── langchain/                  # LangChain tests
├── langgraph/                  # LangGraph tests
├── crewai/                     # CrewAI tests
└── ...                         # More frameworks
```

## Creating Tests for a New Framework

### Step 1: Create Directory Structure

```bash
mkdir -p agent-testing/{framework-name}/.evalview/test-cases
cd agent-testing/{framework-name}
```

### Step 2: Implement Agent

Create `agent.py` (or use framework's server):

```python
"""
Agent implementation for {Framework Name}
Should expose REST API compatible with EvalView HTTPAdapter
"""

# Your framework-specific code here
# Must expose /execute endpoint or similar
```

### Step 3: Create EvalView Config

Create `.evalview/config.yaml`:

```yaml
adapter:
  type: http
  config:
    endpoint: "http://localhost:8000/execute"
    method: POST
    headers:
      Content-Type: "application/json"
    request_format: |
      {
        "messages": [{"role": "user", "content": "{{query}}"}]
      }
    response_path: "output"
    tool_calls_path: "tool_calls"
    cost_path: "cost"
    latency_path: "latency"

test_cases_dir: "./test-cases"
```

### Step 4: Create Test Cases

Create at least these test cases:

1. **Simple tool call** - `.evalview/test-cases/01-simple.yaml`
2. **Multi-tool sequence** - `.evalview/test-cases/02-multi-tool.yaml`
3. **Error handling** - `.evalview/test-cases/03-error.yaml`

See `reference-agent/test-cases/` for examples.

### Step 5: Test Manually

```bash
# Start agent
python agent.py

# Run tests (new terminal)
evalview run
```

### Step 6: Document Results

Update [AGENT_TESTING.md](../AGENT_TESTING.md) with:
- ✅ or ❌ test status
- Any issues discovered
- Framework-specific notes
- Setup complexity

## Test Case Template

```yaml
name: "Test Name"
description: "What this test validates"

input:
  query: "Your test query here"

expected:
  tools:
    - tool_name_1
    - tool_name_2
  sequence:  # Optional: for sequence testing
    - tool_name_1
    - tool_name_2
  output:
    contains:
      - "expected string 1"
      - "expected string 2"

thresholds:
  min_score: 75
  max_cost: 0.10
  max_latency: 3000
```

## Common Test Scenarios

### 1. Simple Single Tool
Tests basic tool calling functionality.

### 2. Multi-Tool Sequence
Tests agent can use multiple tools in correct order.

### 3. Error Handling
Tests agent handles invalid inputs gracefully.

### 4. Cost & Latency
Tests agent stays within performance thresholds.

### 5. Complex Reasoning
Tests agent can handle multi-step queries.

## Framework Requirements

Each framework test should have:

- [ ] **agent.py** or equivalent server implementation
- [ ] **requirements.txt** with framework dependencies
- [ ] **.evalview/config.yaml** with adapter configuration
- [ ] **At least 3 test cases** covering different scenarios
- [ ] **README.md** with setup and running instructions

## Troubleshooting

### Agent Won't Start

```bash
# Check if port is in use
lsof -ti:8000 | xargs kill -9

# Check dependencies
pip install -r requirements.txt

# Check logs
python agent.py --verbose
```

### Tests Failing

```bash
# Run with verbose output
evalview run --verbose

# Check agent is responding
curl http://localhost:8000/health

# Verify test case YAML syntax
python -c "import yaml; yaml.safe_load(open('test-cases/01-simple.yaml'))"
```

### Adapter Issues

- Verify endpoint URL is correct
- Check request/response format matches framework
- Test with curl to see raw responses
- Add debug logging to agent

## Progress Tracking

Track your progress in [AGENT_TESTING.md](../AGENT_TESTING.md):

```markdown
| Framework | Status | Notes |
|-----------|--------|-------|
| LangGraph | ✅ PASS | All 6 tests passed |
| LangChain | ⚠️ PARTIAL | 4/6 tests pass, tool_calls format issue |
| CrewAI | ❌ FAIL | Endpoint incompatible, need custom adapter |
```

## Current Support

| Framework | Status | Notes |
|-----------|--------|-------|
| Reference Agent | ✅ Supported | Validation baseline |
| LangGraph | ✅ Supported | See [examples/langgraph/](../examples/langgraph/) |
| CrewAI | ✅ Supported | See [examples/crewai/](../examples/crewai/) |
| AutoGen | ✅ Supported | See [examples/autogen/](../examples/autogen/) |
| Dify | ✅ Supported | See [examples/dify/](../examples/dify/) |
| OpenAI Assistants | ✅ Supported | See [examples/openai-assistants/](../examples/openai-assistants/) |
| LangChain | ⏳ Planned | Community contribution welcome |
| LlamaIndex | ⏳ Planned | Community contribution welcome |
| Others | ⏳ Planned | [Request support →](https://github.com/hidai25/EvalView/discussions)

## Resources

- **Testing Plan**: [AGENT_TESTING.md](../AGENT_TESTING.md)
- **Reference Agent**: [reference-agent/](reference-agent/)
- **EvalView Docs**: [../README.md](../README.md)

## Need Help?

Questions about testing a specific framework?

1. Check if framework has REST API or HTTP interface
2. Review reference-agent implementation
3. Check existing adapter implementations in `evalview/adapters/`
4. Create minimal reproduction and document issues
