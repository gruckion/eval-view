"""
EvalView Demo Agent - A simple FastAPI agent for testing.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import time
import re

app = FastAPI(title="EvalView Demo Agent")


class Message(BaseModel):
    role: str
    content: str


class ExecuteRequest(BaseModel):
    # Support both formats:
    # 1. EvalView HTTPAdapter format: {"query": "...", "context": {...}}
    # 2. OpenAI-style format: {"messages": [...]}
    query: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    messages: Optional[List[Message]] = None
    enable_tracing: bool = True


class ToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]
    result: Any
    # Per-step metrics for EvalView
    latency: float = 0.0
    cost: float = 0.0


class ExecuteResponse(BaseModel):
    output: str
    tool_calls: List[ToolCall]
    cost: float
    latency: float


def calculator(operation: str, a: float, b: float) -> float:
    ops = {"add": a + b, "subtract": a - b, "multiply": a * b, "divide": a / b if b != 0 else 0}
    return ops.get(operation, 0)


def simple_agent(query: str) -> tuple:
    query_lower = query.lower()
    tool_calls = []
    total_cost = 0.0

    # Simulate realistic LLM processing time (10-20ms per tool)
    time.sleep(0.015)  # 15ms base delay

    if any(op in query_lower for op in ["plus", "add", "+", "sum"]):
        numbers = re.findall(r"\d+", query)
        if len(numbers) >= 2:
            start = time.time()
            a, b = float(numbers[0]), float(numbers[1])
            result = calculator("add", a, b)
            latency = (time.time() - start) * 1000
            step_cost = 0.001
            tool_calls.append(ToolCall(name="calculator", arguments={"operation": "add", "a": a, "b": b}, result=result, latency=latency, cost=step_cost))
            total_cost += step_cost
            return f"The result of {a} + {b} = {result}", tool_calls, total_cost

    elif any(op in query_lower for op in ["minus", "subtract", "-"]):
        numbers = re.findall(r"\d+", query)
        if len(numbers) >= 2:
            start = time.time()
            a, b = float(numbers[0]), float(numbers[1])
            result = calculator("subtract", a, b)
            latency = (time.time() - start) * 1000
            step_cost = 0.001
            tool_calls.append(ToolCall(name="calculator", arguments={"operation": "subtract", "a": a, "b": b}, result=result, latency=latency, cost=step_cost))
            total_cost += step_cost
            return f"The result of {a} - {b} = {result}", tool_calls, total_cost

    elif any(op in query_lower for op in ["times", "multiply", "*"]):
        numbers = re.findall(r"\d+", query)
        if len(numbers) >= 2:
            start = time.time()
            a, b = float(numbers[0]), float(numbers[1])
            result = calculator("multiply", a, b)
            latency = (time.time() - start) * 1000
            step_cost = 0.001
            tool_calls.append(ToolCall(name="calculator", arguments={"operation": "multiply", "a": a, "b": b}, result=result, latency=latency, cost=step_cost))
            total_cost += step_cost
            return f"The result of {a} * {b} = {result}", tool_calls, total_cost

    return f"I received your query: {query}", tool_calls, total_cost


@app.post("/execute", response_model=ExecuteResponse)
async def execute(request: ExecuteRequest):
    start = time.time()

    # Support both request formats
    if request.query:
        query = request.query
    elif request.messages:
        user_msgs = [m for m in request.messages if m.role == "user"]
        if not user_msgs:
            raise HTTPException(status_code=400, detail="No user message")
        query = user_msgs[-1].content
    else:
        raise HTTPException(status_code=400, detail="Either query or messages must be provided")

    output, tools, cost = simple_agent(query)
    total_latency = (time.time() - start) * 1000

    # Distribute total latency across steps for more realistic reporting
    if tools:
        per_step_latency = total_latency / len(tools)
        tools = [
            ToolCall(
                name=t.name,
                arguments=t.arguments,
                result=t.result,
                latency=per_step_latency,
                cost=t.cost,
            )
            for t in tools
        ]

    return ExecuteResponse(output=output, tool_calls=tools, cost=cost, latency=total_latency)


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    print("Demo Agent running on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
