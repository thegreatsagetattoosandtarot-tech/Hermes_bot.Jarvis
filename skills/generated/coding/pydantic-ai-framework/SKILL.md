---
name: pydantic-ai-framework
description: PydanticAI v2.4.0 integration for type-safe agent workflows in The Great Sage JARVIS OS
owners: [MICHAEL, RAPHAEL]
tags: [coding, agents, pydantic, type-safety, python]
version: 1.0.0
created: 2026-07-03
---

# PydanticAI Framework Integration

## Overview
PydanticAI v2.4.0 is a production-grade Python agent framework that adds type-safe tool definitions and evaluators to LLM workflows. Released July 2, 2026, it adds `ToolCorrectness` and `GEval LLM-judge` evaluators for production agent pipelines.

## Installation
```bash
pip install pydantic-ai
```

## Key Use Cases for The Great Sage
1. **Booking data validation** — enforce required fields (name, date, design idea) before writing to Setmore
2. **Client intake forms** — structured intake with Pydantic models ensuring clean CRM data
3. **Lead scoring** — validate and score inbound DM leads against defined criteria

## Core Pattern

```python
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

class BookingRequest(BaseModel):
    client_name: str
    preferred_date: str
    design_description: str
    budget_range: str
    contact_info: str

class BookingResponse(BaseModel):
    confirmed: bool
    booking_id: str
    setmore_link: str
    message: str

booking_agent = Agent(
    model='anthropic:claude-sonnet-4-6',
    result_type=BookingResponse,
    system_prompt="You are JARVIS booking assistant for The Great Sage Tattoos & Tarot."
)

@booking_agent.tool
async def validate_booking(ctx: RunContext, request: BookingRequest) -> str:
    """Validate and create a booking request."""
    # Type-safe — Pydantic enforces all fields
    return f"Booking created for {request.client_name} on {request.preferred_date}"
```

## Evaluators (v2.4.0)
```python
from pydantic_ai.evaluators import ToolCorrectness, GEval

# Check tools are called correctly
evaluator = ToolCorrectness()
result = evaluator.evaluate(agent_run)

# LLM-judge for response quality
llm_judge = GEval(criteria="booking confirmation is polite and complete")
score = llm_judge.evaluate(response)
```

## Integration with Archangel Fleet
- **RAPHAEL** uses PydanticAI for structured research reports
- **MICHAEL** uses it for project brief validation
- **SARAQAEL** uses it for CRM intake forms
- All archangel tool calls should define Pydantic input/output models

## Activation Triggers
- "create structured agent"
- "type-safe tool"
- "validate booking data"
- "pydantic agent"
- "intake form validation"
