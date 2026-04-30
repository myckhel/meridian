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


### Success Criteria

* Reduce support workload (≥40% automation target)
* Improve response time (instant vs minutes/hours)
* Enable self-service flows:

  * Product lookup
  * Order placement
  * Order history retrieval
  * Customer authentication

# 2) Plan of Attack

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