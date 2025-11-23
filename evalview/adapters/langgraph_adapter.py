"""LangGraph-specific adapter for EvalView.

Supports both LangGraph Cloud API and self-hosted LangGraph agents.
"""

import httpx
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
import logging

from evalview.adapters.base import AgentAdapter
from evalview.core.types import (
    ExecutionTrace,
    StepTrace,
    StepMetrics,
    ExecutionMetrics,
)

logger = logging.getLogger(__name__)


class LangGraphAdapter(AgentAdapter):
    """Adapter for LangGraph agents.

    Supports:
    - LangGraph invoke endpoint (standard)
    - LangGraph streaming endpoint
    - LangGraph Cloud API

    Response formats:
    - {"messages": [...], "steps": [...]}
    - Streaming: data: {"type": "step", "content": "...", ...}
    """

    def __init__(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
        streaming: bool = False,
        verbose: bool = False,
        model_config: Optional[Dict[str, Any]] = None,
    ):
        self.endpoint = endpoint
        self.headers = headers or {"Content-Type": "application/json"}
        self.timeout = timeout
        self.streaming = streaming
        self.verbose = verbose
        self.model_config = model_config or {}

    @property
    def name(self) -> str:
        return "langgraph"

    async def execute(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> ExecutionTrace:
        """Execute LangGraph agent and capture trace."""
        context = context or {}
        start_time = datetime.now()

        if self.streaming:
            return await self._execute_streaming(query, context, start_time)
        else:
            return await self._execute_standard(query, context, start_time)

    async def _execute_standard(
        self, query: str, context: Dict[str, Any], start_time: datetime
    ) -> ExecutionTrace:
        """Execute LangGraph invoke endpoint."""

        # LangGraph typically expects messages format
        payload = {
            "messages": [{"role": "user", "content": query}],
            **context,
        }

        if self.verbose:
            logger.info(f"🚀 Executing LangGraph request: {query}...")
            logger.debug(f"📤 Payload: {json.dumps(payload, indent=2)}")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.endpoint,
                json=payload,
                headers=self.headers,
            )
            response.raise_for_status()
            data = response.json()

        if self.verbose:
            logger.debug(f"📥 Response: {json.dumps(data, indent=2)}")

        end_time = datetime.now()

        # Parse LangGraph response
        steps = self._parse_steps(data)
        final_output = self._extract_output(data)
        metrics = self._calculate_metrics(steps, start_time, end_time)

        return ExecutionTrace(
            session_id=data.get("thread_id", f"langgraph-{start_time.timestamp()}"),
            start_time=start_time,
            end_time=end_time,
            steps=steps,
            final_output=final_output,
            metrics=metrics,
        )

    async def _execute_streaming(
        self, query: str, context: Dict[str, Any], start_time: datetime
    ) -> ExecutionTrace:
        """Execute LangGraph streaming endpoint."""

        payload = {
            "messages": [{"role": "user", "content": query}],
            **context,
        }

        if self.verbose:
            logger.info(f"🚀 Executing LangGraph streaming request: {query}...")

        steps: List[StepTrace] = []
        final_output = ""
        thread_id = None

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                self.endpoint,
                json=payload,
                headers=self.headers,
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            event = json.loads(line[6:])
                            event_type = event.get("type")

                            if event_type == "step":
                                # Parse step event
                                step = self._parse_step_event(event)
                                if step:
                                    steps.append(step)

                            elif event_type == "message":
                                # Accumulate output
                                content = event.get("content", "")
                                final_output += content

                            elif event_type == "metadata":
                                thread_id = event.get("thread_id")

                        except json.JSONDecodeError:
                            continue

        end_time = datetime.now()
        metrics = self._calculate_metrics(steps, start_time, end_time)

        return ExecutionTrace(
            session_id=thread_id or f"langgraph-{start_time.timestamp()}",
            start_time=start_time,
            end_time=end_time,
            steps=steps,
            final_output=final_output.strip(),
            metrics=metrics,
        )

    def _parse_steps(self, data: Dict[str, Any]) -> List[StepTrace]:
        """Parse steps from LangGraph response."""
        steps = []

        # LangGraph may include intermediate_steps or actions
        if "intermediate_steps" in data:
            for i, step_data in enumerate(data["intermediate_steps"]):
                step = self._create_step_from_intermediate(step_data, i)
                if step:
                    steps.append(step)

        elif "steps" in data:
            for i, step_data in enumerate(data["steps"]):
                step = self._create_step_from_data(step_data, i)
                if step:
                    steps.append(step)

        return steps

    def _create_step_from_intermediate(
        self, step_data: Any, index: int
    ) -> Optional[StepTrace]:
        """Create StepTrace from intermediate_steps format."""
        # intermediate_steps is usually [(AgentAction, output), ...]
        if isinstance(step_data, (list, tuple)) and len(step_data) >= 2:
            action, output = step_data[0], step_data[1]

            # Extract tool info
            if hasattr(action, 'tool'):
                tool_name = action.tool
                parameters = getattr(action, 'tool_input', {})
            else:
                tool_name = str(action)
                parameters = {}

            return StepTrace(
                step_id=f"step-{index}",
                step_name=f"Step {index + 1}",
                tool_name=tool_name,
                parameters=parameters,
                output=output,
                success=True,
                metrics=StepMetrics(latency=0.0, cost=0.0),
            )
        return None

    def _create_step_from_data(
        self, step_data: Dict[str, Any], index: int
    ) -> Optional[StepTrace]:
        """Create StepTrace from steps format."""
        return StepTrace(
            step_id=step_data.get("id", f"step-{index}"),
            step_name=step_data.get("name", f"Step {index + 1}"),
            tool_name=step_data.get("tool"),
            parameters=step_data.get("parameters", {}),
            output=step_data.get("output"),
            success=step_data.get("success", True),
            metrics=StepMetrics(
                latency=step_data.get("latency", 0.0),
                cost=step_data.get("cost", 0.0),
            ),
        )

    def _parse_step_event(self, event: Dict[str, Any]) -> Optional[StepTrace]:
        """Parse streaming step event."""
        content = event.get("content", "")

        # Try to detect tool usage from content
        # This is heuristic-based since streaming format varies
        if "tool" in event or "action" in event:
            return StepTrace(
                step_id=event.get("id", f"step-{datetime.now().timestamp()}"),
                step_name=content[:50] if content else "Step",
                tool_name=event.get("tool"),
                parameters=event.get("parameters", {}),
                output=content,
                success=True,
                metrics=StepMetrics(latency=0.0, cost=0.0),
            )
        return None

    def _extract_output(self, data: Dict[str, Any]) -> str:
        """Extract final output from LangGraph response."""
        # Try different possible locations
        if "messages" in data and isinstance(data["messages"], list):
            # Get last message content
            messages = data["messages"]
            if messages:
                last_msg = messages[-1]
                if isinstance(last_msg, dict):
                    return last_msg.get("content", "")
                elif hasattr(last_msg, 'content'):
                    return last_msg.content

        if "output" in data:
            return str(data["output"])

        if "result" in data:
            return str(data["result"])

        return ""

    def _calculate_metrics(
        self, steps: List[StepTrace], start_time: datetime, end_time: datetime
    ) -> ExecutionMetrics:
        """Calculate execution metrics."""
        total_latency = (end_time - start_time).total_seconds() * 1000
        total_cost = sum(step.metrics.cost for step in steps)
        total_tokens = sum(step.metrics.tokens or 0 for step in steps)

        return ExecutionMetrics(
            total_cost=total_cost,
            total_latency=total_latency,
            total_tokens=total_tokens if total_tokens > 0 else None,
        )

    async def health_check(self) -> bool:
        """Check if LangGraph endpoint is reachable."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Try a simple request
                response = await client.post(
                    self.endpoint,
                    json={"messages": [{"role": "user", "content": "test"}]},
                    headers=self.headers,
                )
                return response.status_code in [200, 201, 422]
        except Exception:
            return False
