# Agent Testing Plan

## Overview

Before launching EvalView publicly, we need to validate it works with the most popular agent frameworks in production use.

## Testing Goals

1. **Compatibility**: Verify EvalView works with each framework
2. **Accuracy**: Ensure evaluators correctly assess agent behavior
3. **Documentation**: Create working examples for each framework
4. **Bug Discovery**: Find and fix issues before public launch

## Testing Matrix

### Priority 1: Core Frameworks (Must Test)

| Framework | Status | Adapter | Example | Notes |
|-----------|--------|---------|---------|-------|
| **LangGraph** | ⏳ Pending | `LangGraphAdapter` | - | Most popular for production |
| **LangChain** | ⏳ Pending | `HTTPAdapter` | - | Widely used, REST API |
| **CrewAI** | ⏳ Pending | `CrewAIAdapter` | - | Multi-agent systems |
| **OpenAI Assistants** | ⏳ Pending | `OpenAIAssistantsAdapter` | - | Official OpenAI framework |
| **AutoGen (Microsoft)** | ⏳ Pending | `HTTPAdapter` | - | Enterprise multi-agent |
| **LlamaIndex** | ⏳ Pending | `HTTPAdapter` | - | RAG-focused agents |
| **Anthropic Claude** | ⏳ Pending | `HTTPAdapter` | - | Tool use via Messages API |
| **Haystack** | ⏳ Pending | `HTTPAdapter` | - | NLP pipelines, agents |

### Priority 2: Emerging Frameworks (Should Test)

| Framework | Status | Adapter | Example | Notes |
|-----------|--------|---------|---------|-------|
| **Semantic Kernel** | ⏳ Pending | `HTTPAdapter` | - | Microsoft's framework |
| **Langroid** | ⏳ Pending | `HTTPAdapter` | - | Multi-agent, good docs |
| **Phidata** | ⏳ Pending | `HTTPAdapter` | - | Growing community |
| **AGiXT** | ⏳ Pending | `HTTPAdapter` | - | Open source platform |
| **BabyAGI** | ⏳ Pending | `HTTPAdapter` | - | Task-driven autonomous |
| **AgentGPT** | ⏳ Pending | `HTTPAdapter` | - | Web-based autonomous |

### Priority 3: Specialized Frameworks (Nice to Test)

| Framework | Status | Adapter | Example | Notes |
|-----------|--------|---------|---------|-------|
| **MetaGPT** | ⏳ Pending | `HTTPAdapter` | - | Multi-agent for code |
| **MemGPT** | ⏳ Pending | `HTTPAdapter` | - | Memory management |
| **SuperAGI** | ⏳ Pending | `HTTPAdapter` | - | Infrastructure focused |
| **ix** | ⏳ Pending | `HTTPAdapter` | - | Visual agent builder |
| **Botpress** | ⏳ Pending | `HTTPAdapter` | - | Conversational AI |
| **Rasa** | ⏳ Pending | `HTTPAdapter` | - | Open source chatbots |

### Priority 4: Custom/API-Based (Validation)

| Type | Status | Adapter | Example | Notes |
|------|--------|---------|---------|-------|
| **Custom FastAPI** | ⏳ Pending | `HTTPAdapter` | - | Generic REST API |
| **Custom Express** | ⏳ Pending | `HTTPAdapter` | - | Node.js backend |
| **Custom Flask** | ⏳ Pending | `HTTPAdapter` | - | Python backend |
| **AWS Lambda** | ⏳ Pending | `HTTPAdapter` | - | Serverless agents |

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

## Timeline

- **Week 1**: Priority 1 frameworks (8 frameworks)
- **Week 2**: Priority 2 frameworks (6 frameworks)
- **Week 3**: Priority 3 + Custom (10 frameworks)
- **Week 4**: Documentation, examples, bug fixes

**Total**: ~24 frameworks tested

## Notes

- Focus on production-ready frameworks first
- Document setup complexity (easy, medium, hard)
- Note any EvalView bugs discovered
- Track which adapters work best
- Gather user pain points for future features

## Next Steps After Testing

1. Update README with compatibility matrix
2. Add tested framework badges
3. Publish example repositories
4. Write blog post: "We tested EvalView with 20+ agent frameworks"
5. Create video demos for top 5 frameworks
