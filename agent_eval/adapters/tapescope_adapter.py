"""Custom adapter for TapeScope streaming API."""

from datetime import datetime
from typing import Any, Optional, Dict, List
import httpx
import json
from agent_eval.adapters.base import AgentAdapter
from agent_eval.core.types import (
    ExecutionTrace,
    StepTrace,
    StepMetrics,
    ExecutionMetrics,
)


class TapeScopeAdapter(AgentAdapter):
    """Adapter for TapeScope's streaming JSONL API."""

    def __init__(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 60.0,
    ):
        """
        Initialize TapeScope adapter.

        Args:
            endpoint: API endpoint URL (e.g., http://localhost:3000/api/unifiedchat)
            headers: Optional HTTP headers
            timeout: Request timeout in seconds
        """
        self.endpoint = endpoint
        self.headers = headers or {}
        self.timeout = timeout

    @property
    def name(self) -> str:
        return "tapescope"

    async def execute(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> ExecutionTrace:
        """Execute agent via TapeScope API and capture trace."""
        start_time = datetime.now()

        # Default context if not provided
        if context is None:
            context = {}

        # Prepare request payload (TapeScope expects 'message' not 'query')
        payload = {
            "message": query,
            "prompt": query,
            "route": context.get("route", "conversational"),
            "userId": context.get("userId", "test-user"),
            **context
        }

        events = []
        steps = []
        final_output = ""

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                self.endpoint,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    **self.headers,
                },
            ) as response:
                response.raise_for_status()

                # Read JSONL stream line by line
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue

                    try:
                        event = json.loads(line)
                        events.append(event)

                        # Parse different event types
                        event_type = event.get("type", "")

                        if event_type == "tool_call":
                            # Tool execution step
                            tool_data = event.get("data", {})
                            step = StepTrace(
                                step_id=f"tool-{len(steps)}",
                                step_name=tool_data.get("name", "unknown"),
                                tool_name=tool_data.get("name", "unknown"),
                                parameters=tool_data.get("args", {}),
                                output=None,  # Will be filled by tool_result
                                success=True,
                                error=None,
                                metrics=StepMetrics(latency=0.0, cost=0.0, tokens=None),
                            )
                            steps.append(step)

                        elif event_type == "tool_result":
                            # Update last step with result
                            if steps:
                                result_data = event.get("data", {})
                                steps[-1].output = result_data.get("result", "")
                                steps[-1].success = result_data.get("success", True)
                                steps[-1].error = result_data.get("error")

                        elif event_type == "final_message":
                            # Final agent response
                            final_output = event.get("data", {}).get("text", "")

                        elif event_type == "token":
                            # Accumulate streaming tokens
                            token = event.get("data", {}).get("token", "")
                            final_output += token

                        elif event_type == "error":
                            # Error occurred
                            final_output = f"Error: {event.get('error', 'Unknown error')}"

                    except json.JSONDecodeError:
                        # Skip invalid JSON lines
                        continue

        end_time = datetime.now()

        # Calculate metrics
        total_latency = (end_time - start_time).total_seconds() * 1000
        total_cost = sum(step.metrics.cost for step in steps)
        total_tokens = sum(step.metrics.tokens or 0 for step in steps)

        return ExecutionTrace(
            session_id=f"tapescope-{int(start_time.timestamp())}",
            start_time=start_time,
            end_time=end_time,
            steps=steps,
            final_output=final_output.strip() if final_output else "No response",
            metrics=ExecutionMetrics(
                total_cost=total_cost,
                total_latency=total_latency,
                total_tokens=total_tokens,
            ),
        )

    async def health_check(self) -> bool:
        """Check if the TapeScope endpoint is reachable."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(self.endpoint)
                return response.status_code == 200
        except Exception:
            return False
