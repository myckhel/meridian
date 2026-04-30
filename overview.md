# 1) Business Problem for Meridian

Meridian Electronics is facing a **scalability and efficiency bottleneck in customer support**.

### Core Problems

* **High operational cost**
  Human agents handle repetitive queries (availability, order status, authentication).

* **Slow response times**
  Phone/email queues introduce latency → poor customer experience.

* **Limited availability (non-24/7)**
  Customers expect real-time support, especially for e-commerce flows.

* **Underutilized backend systems**
  Meridian already has structured services exposed via MCP, but no intelligent interface to leverage them.

---

### Strategic Framing

This is not just a chatbot problem — it’s a **service orchestration problem**.

The real opportunity:

> Build an AI layer that translates natural language → structured MCP tool calls → reliable business actions.

---

### Success Criteria

* Reduce support workload (≥40% automation target)
* Improve response time (instant vs minutes/hours)
* Enable self-service flows:

  * Product lookup
  * Order placement
  * Order history retrieval
  * Customer authentication

---

# 2) Plan of Attack

You’re under time pressure, so this must be **incremental, risk-driven, and demo-optimized**.

---

## Phase 1 — Core Foundation (Must Work)

### Goal:

A working **LLM + MCP tool-calling chatbot**

### What you build first:

#### 1. MCP Client Layer

* Connect to:

  ```
  https://order-mcp-74afyau24q-uc.a.run.app/mcp
  ```
* Discover tools dynamically
* Abstract into a **Tool Registry**

```ts
interface MCPTool {
  name: string;
  description: string;
  inputSchema: any;
}
```

---

#### 2. Tool-Calling Agent

* Use an LLM with function/tool calling (e.g. OpenAI / compatible)
* Convert user intent → MCP tool call

Key flows:

* `check_product_availability`
* `place_order`
* `get_order_history`
* `authenticate_user`

---

#### 3. Chat Interface (Minimum Requirement)

Use:

* Streamlit or Gradio

Features:

* Chat input/output
* Session memory
* Tool execution feedback (transparent responses)

---

#### 4. Execution Loop

Core logic:

```ts
User → LLM → Tool निर्णय → MCP Call → Response → LLM → User
```

Add:

* Retry logic
* Tool validation
* Error fallback

---

#### 5. Deployment (Baseline)

* Deploy to Hugging Face Spaces
* Ensure:

  * Public access
  * Stable API calls
  * Clear demo instructions

---

## Phase 2 — High-Impact Enhancements (If Time Allows)

### 1. Authentication Flow

* Persist session identity
* Token-based user state
* Enable:

  * Order history
  * Personalized responses

---

### 2. Conversational Memory

* Short-term memory buffer
* Example:

  > “Order that same keyboard again”

---

### 3. Structured UI Upgrade

If time permits:

* Build frontend in Next.js
* Add:

  * Product cards
  * Order summaries
  * Status indicators

---

### 4. Observability

* Logging (tool calls, failures)
* Basic analytics:

  * % successful tool calls
  * fallback rate

---

### 5. Guardrails

* Input validation
* Tool schema enforcement
* Prevent invalid orders

---

# 3) What You’ll Cut If Time Runs Out

Be ruthless — prioritize demo reliability over completeness.

### Cut Order (in priority)

#### ❌ First to Cut

* Fancy UI (Next.js frontend)
* Advanced styling

#### ❌ Next

* Persistent memory across sessions
* Deep analytics dashboard

#### ❌ Then

* Complex authentication flows

---

### What MUST NOT be cut

* MCP integration
* Tool-calling reliability
* Chat UX clarity
* Deployment

If these fail, the demo fails.

---

# 4) Architecture Overview

### Clean, Production-Ready Design

```
/app
  /ui              → Streamlit UI
  /agent           → LLM orchestration
  /mcp             → MCP client + tool registry
  /services        → business logic wrappers
  /schemas         → tool validation
  /utils           → logging, retry, errors
```

---

### Key Engineering Decisions

* **Loose coupling**
  MCP tools abstracted → easy to swap backend

* **Schema-driven execution**
  Prevents malformed tool calls

* **Deterministic fallback**
  If tool fails:
  → graceful LLM response

---

# 5) Demo Narrative (What You Show Stakeholders)

Walk them through:

1. “Do you have this monitor in stock?”
2. “Order it for me”
3. “Show my past orders”
4. “Authenticate returning user”

Then emphasize:

> “This is not a scripted bot — it dynamically discovers and uses Meridian’s internal systems via MCP.”

---

# 6) Strategic Positioning (For VP)

Frame it like this:

* Not just cost reduction → **revenue enabler**
* Faster purchase decisions
* Always-on sales assistant
* Scales without hiring

---

# Bottom Line

You’re building:

> A production-grade AI orchestration layer that turns Meridian’s MCP server into a fully interactive customer support system.