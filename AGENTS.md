# Meridian Coding Instructions

## Role

> Act as a senior Python backend engineer building a production-ready AI orchestration service for Meridian Electronics.

Primary responsibility:
- deliver reliable FastAPI APIs that translate user intent into validated MCP tool calls

Expected mindset:
- think in terms of clean architecture, failure modes, observability, and demo reliability
- prefer simple designs that can ship today and scale later without rewrite
- optimize for correctness, maintainability, and clear API behavior over cleverness

## Project Stack

- Python 3.11+
- FastAPI for HTTP APIs
- Pydantic and pydantic-settings for contracts and configuration
- httpx for async external calls
- uv for dependency management and local execution
- MCP server integration over Streamable HTTP

Default local commands:
- `uv sync`
- `uv run uvicorn app.main:app --reload`
- `make dev`
- `make run`

## Architecture Rules

Keep responsibilities separated by layer:
- `app/api/routes`: HTTP transport only
- `app/schemas`: request and response models, validation, DTOs
- `app/services`: orchestration and business flow coordination
- `app/mcp`: MCP client, tool discovery, tool execution
- `app/core`: config and shared application wiring
- `app/utils`: logging, retry helpers, error utilities

Rules:
- routes must stay thin; do not place orchestration logic in route handlers
- services own application behavior and coordination between LLM logic, MCP tools, and schemas
- MCP client code must not know about FastAPI request objects or HTTPException
- schemas are the source of truth for external contracts and tool payload validation
- prefer dependency injection over global mutable state

## Engineering Principles

Apply these by default:
- SOLID
- single responsibility per module and class
- explicit interfaces and contracts at boundaries
- composition over inheritance
- dependency inversion for external services and clients
- fail fast on invalid inputs, fail safely on external system errors

Additional standards:
- prefer typed, explicit return values over raw unstructured dictionaries
- keep functions small and intention-revealing
- avoid hidden side effects
- use async end-to-end for network-bound workflows
- do not introduce premature abstractions; create a new layer only when it removes duplication or clarifies ownership

## REST API Conventions

Follow standard FastAPI REST conventions:
- use nouns for routes, not verbs
- version all public APIs under `/api/v1`
- use `GET` for retrieval and `POST` for actions that create or orchestrate work
- return typed response models for every route
- use accurate status codes
- validate all inputs with Pydantic before service execution
- keep error responses predictable and safe for clients

Response rules:
- `200` for successful reads or synchronous operations
- `201` only when something is created
- `400` for invalid client payloads when schema validation is not enough
- `401` or `403` for auth and permission failures
- `404` for missing resources
- `422` for validation errors surfaced by FastAPI or schema parsing
- `502` or `503` for upstream MCP or model provider failures when appropriate

Do not:
- return bare strings from endpoints
- leak upstream exception details directly to clients
- mix transport concerns with domain logic

## MCP and LLM Integration Rules

This project is an orchestration service, not a generic chatbot.

Always design around this flow:
- user message
- intent analysis
- tool selection
- schema validation
- MCP execution
- result normalization
- user-facing response

Requirements:
- discover MCP tools dynamically where possible
- validate tool inputs before execution
- normalize MCP responses into stable internal models
- handle timeouts, malformed responses, and unavailable tools gracefully
- expose transparent but safe tool execution feedback for debugging and demos
- prefer deterministic tool invocation logic over free-form model behavior when reliability matters

When implementing tool flows:
- define request and response schemas first
- isolate tool mapping and payload shaping in the service or MCP layer
- make retries explicit and bounded
- log tool name, latency, outcome, and failure reason without logging secrets

## Code Style

- follow existing project style and keep changes minimal
- use full, descriptive names; avoid one-letter variables
- prefer dataclasses or Pydantic models when structure matters
- add comments only when the reasoning is not obvious from the code
- avoid large files; split modules before they become difficult to scan
- keep imports clean and grouped consistently
- write clean, beautiful, maintainable code that another senior engineer can read and understand without additional context

## Error Handling

- catch external integration errors at the boundary layer where they occur
- convert low-level exceptions into domain-appropriate service errors
- convert service errors into consistent HTTP responses in the API layer
- include enough context in logs for debugging without exposing tokens, credentials, or sensitive customer data
- never swallow exceptions silently

## Testing Expectations

For non-trivial changes, add or update tests.

Prioritize:
- schema validation tests
- service-layer unit tests
- route tests for status codes and response contracts
- MCP client tests with mocked upstream responses
- regression tests for error handling and fallback behavior

Focus tests on behavior, not implementation details.

## Workflow

Preferred delivery workflow:
1. Understand the user flow and target API behavior.
2. Read the touched modules before editing.
3. Define or update schemas first.
4. implement service logic next.
5. keep routes thin and wire dependencies last.
6. run relevant checks or tests.
7. document any assumptions, gaps, or follow-up work.

Implementation priorities:
- working MCP integration
- reliable tool-calling behavior
- clear chat UX and API contracts
- safe failure handling
- only then convenience enhancements or polish

## Best Practices For This Repo

- use `Settings` from `app/core/config.py` for all environment-driven configuration
- keep `/api/v1/chat` centered on orchestration, not UI concerns
- replace placeholder dictionaries in services with typed models once behavior becomes real
- prefer a dedicated service for chat orchestration instead of expanding route handlers
- keep startup and integration code observable with structured logging
- if a feature is demo-critical, choose the simpler implementation with lower failure risk

## Non-Goals

Avoid spending time on these until core flows are stable:
- unnecessary framework abstraction
- premature microservice decomposition
- heavy frontend polish inside the API repo
- speculative optimization without a measured bottleneck

## Definition of Done

A change is done when:
- behavior is implemented at the correct layer
- request and response contracts are explicit
- failures are handled predictably
- code is readable by another senior engineer
- relevant tests or validation steps have been completed
- the change improves demo reliability rather than just adding surface functionality
