---
name: Adapter Request
about: Request support for a new AI agent framework
title: '[ADAPTER] '
labels: adapter, enhancement
assignees: ''
---

## Framework Name
Name of the AI agent framework (e.g., AutoGPT, AgentGPT, Semantic Kernel)

## Framework Links
- **Documentation**:
- **GitHub**:
- **API Reference**:

## API Details

### Endpoint Format
```
POST /api/endpoint
```

### Request Format
```json
{
  "query": "user input",
  "context": {}
}
```

### Response Format
```json
{
  "output": "agent response",
  "steps": [],
  "tokens": 0
}
```

## Why This Framework?
- How popular/widely used is it?
- What's your use case?

## Would You Contribute?
- [ ] I'm willing to help implement this adapter
- [ ] I can help test the adapter
- [ ] I can provide sample API responses

## Additional Context
- Any special authentication requirements?
- Streaming vs batch responses?
- Known quirks or edge cases?
