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

* Use an LLM with function/tool calling (e.g. OpenAI)
* Convert user intent → MCP tool call

Key flows:

* `check_product_availability`
* `place_order`
* `get_order_history`
* `authenticate_user`

---

#### 3. Chat Interface (Minimum Requirement)

Use:

* Gradio

Features:

* Chat input/output
* Session memory
* Tool execution feedback (transparent responses)

---

#### 4. Execution Loop

Core logic:

```ts
User → LLM → Tool → MCP Call → Response → LLM → User
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