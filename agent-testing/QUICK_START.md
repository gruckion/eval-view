# Quick Start: Testing EvalView with 20+ Agents

## Prerequisites

Before testing, you need:

1. **OpenAI API Key** (for LLM-as-judge evaluation)
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```

2. **Python 3.9+** and pip

3. **EvalView installed**
   ```bash
   cd /path/to/EvalView
   pip install -e .
   ```

## Step 1: Test Reference Agent (Validation)

The reference agent validates that EvalView works correctly before testing other frameworks.

### Start the Agent

```bash
# Terminal 1
cd agent-testing/reference-agent
pip install -r requirements.txt
python agent.py
```

Expected output:
```
🚀 Starting Reference Test Agent on http://localhost:8000
📚 API docs available at http://localhost:8000/docs
🔧 Available tools: ['calculator', 'get_weather', 'search_web', 'convert_temperature', 'get_stock_price']
```

### Run Tests

```bash
# Terminal 2
cd agent-testing/reference-agent
export OPENAI_API_KEY="sk-..."  # Your OpenAI API key
evalview run
```

### Expected Results

All 6 tests should PASS:
```
✅ Simple Calculator - Addition (score: 95.0)
✅ Weather Query - Single Tool (score: 92.5)
✅ Multi-Tool Sequence - Weather & Conversion (score: 88.0)
✅ Error Handling - Invalid City (score: 85.0)
✅ Stock Price Query (score: 90.0)
✅ Calculator - Multiplication (score: 95.0)

Overall: 6/6 tests passed 🎉
```

If all tests pass → **EvalView is working correctly!**

## Step 2: Test Real Agent Frameworks

Now test with production frameworks in priority order:

### Priority 1 (Must Test Before Launch)

1. **LangGraph** - Most popular for production
2. **LangChain** - Widely used
3. **CrewAI** - Multi-agent systems
4. **OpenAI Assistants** - Official framework
5. **AutoGen** - Microsoft's framework
6. **LlamaIndex** - RAG-focused agents
7. **Anthropic Claude** - Tool use via Messages API
8. **Haystack** - NLP pipelines

### Testing Process for Each Framework

```bash
# 1. Create directory
mkdir -p agent-testing/{framework-name}
cd agent-testing/{framework-name}

# 2. Implement agent (or use framework's server)
# Create agent.py that exposes REST API

# 3. Create config
mkdir -p .evalview tests/test-cases
# Create .evalview/config.yaml
# Create test cases in tests/test-cases/

# 4. Start agent and test
python agent.py  # Terminal 1
evalview run     # Terminal 2

# 5. Document results
# Update AGENT_TESTING.md with status
```

## Step 3: Automated Testing

Once you have multiple frameworks set up:

```bash
cd agent-testing
./test-runner.sh
```

This will:
- Test all frameworks automatically
- Generate summary report
- Save logs for debugging

## Framework Testing Checklist

For each framework, ensure:

- [ ] Agent starts and responds to queries
- [ ] Tool calls are detected correctly
- [ ] Output evaluation produces reasonable scores
- [ ] Cost/latency tracking works (if applicable)
- [ ] At least 3 test scenarios pass
- [ ] Setup documented in README
- [ ] Results added to AGENT_TESTING.md

## Common Issues

### "OpenAI API key required"
```bash
export OPENAI_API_KEY="sk-..."
```

### "Port already in use"
```bash
lsof -ti:8000 | xargs kill -9
```

### "evalview: command not found"
```bash
cd /path/to/EvalView
pip install -e .
```

### Tests fail unexpectedly
```bash
# Run with verbose mode
evalview run --verbose

# Check agent logs
tail -f /tmp/agent.log
```

## Launch Criteria

Before public launch, achieve:

- [x] Reference agent: 6/6 tests pass ✅
- [ ] At least 5 major frameworks tested
- [ ] Any bugs discovered are fixed
- [ ] Compatibility matrix documented
- [ ] Example agents published

## Timeline

**Realistic timeline for 20+ frameworks:**

- **Day 1-2**: Reference agent + 3 major frameworks (LangGraph, LangChain, CrewAI)
- **Day 3-5**: 5 more frameworks (OpenAI, AutoGen, LlamaIndex, Anthropic, Haystack)
- **Day 6-10**: 10 additional frameworks (Priority 2 & 3)
- **Day 11-12**: Documentation, bug fixes, examples
- **Day 13**: Final validation and launch preparation

**Fast track (minimum viable):**
- Test 5-8 major frameworks (Priority 1 only)
- Document known limitations
- Launch with "tested with" badge
- Add more frameworks post-launch

## Next Steps

1. ✅ **Validate setup**: Test reference agent
2. 🔄 **Pick framework**: Start with LangGraph or LangChain
3. 📝 **Document**: Add results to AGENT_TESTING.md
4. 🔁 **Repeat**: Test 4-7 more frameworks
5. 🚀 **Launch**: When comfortable with coverage

## Resources

- **Testing Plan**: [AGENT_TESTING.md](../AGENT_TESTING.md)
- **Reference Agent**: [reference-agent/](reference-agent/)
- **Test Runner**: [test-runner.sh](test-runner.sh)
- **Main Docs**: [../README.md](../README.md)

## Questions?

- Check [agent-testing/README.md](README.md) for detailed instructions
- Review [reference-agent/README.md](reference-agent/README.md) for template
- See [AGENT_TESTING.md](../AGENT_TESTING.md) for complete matrix

---

**Ready to start?** Run the reference agent test now! 🚀
