# 🌊 ShopWave: Autonomous Support Resolution Agent

**Submission for the Agentic AI Hackathon 2026**

ShopWave is an enterprise-grade agentic pipeline designed to automate high-volume customer support workflows. Unlike traditional chatbots, ShopWave leverages a **ReAct (Reasoning + Acting)** framework powered by **LangGraph** to autonomously classify, investigate, and resolve customer tickets—complete with a human-like audit trail.

---

## 🚀 Key Innovation Features

### 🧠 Stateful Orchestration

Built on **LangGraph**, the agent maintains complex state across multiple reasoning loops, preventing repetitive cycles and enabling deep contextual understanding.

### ⚡ Concurrent Ticket Processing

A custom asynchronous worker pool processes multiple tickets in parallel, significantly reducing latency for batch operations.

### 🛠 Intelligent Tool Calling

Includes a smart **"Nudge" mechanism**:

* Detects missing information when resolution fails
* Guides the LLM to invoke the correct tools (e.g., Knowledge Base vs Order Database)

### 🧾 Resiliency & Logging

* **Dead-Letter Queue (DLQ):** Routes unresolved or edge-case tickets for human review
* **Audit Trail:** Captures every reasoning step, tool call, and decision for transparency

---

## 🛠 Technical Architecture

| Layer         | Technology                         |
| ------------- | ---------------------------------- |
| Core Logic    | Python 3.10+                       |
| Orchestration | LangGraph + LangChain (ReAct Loop) |
| Intelligence  | Llama-3.1-70B (via OpenRouter)     |
| API Layer     | FastAPI                            |
| Interface     | Streamlit                          |
| Environment   | Docker                             |

---

## ⚙️ Environment Configuration

To run the agent, you will need an API key from **OpenRouter**.

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd shopwave
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=meta-llama/llama-3.1-70b-instruct
```

---

## 🏃 Deployment Guide

### Option A: One-Command Setup (Recommended)

The fastest way to evaluate the project is using Docker Compose:

```bash
docker compose up --build
```

* **Dashboard (Streamlit):** http://localhost:8502
* **Interactive API Docs:** http://localhost:8007/docs

---

### Option B: Local Development

#### 1. Start the FastAPI Server

```bash
python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8007
```

#### 2. Launch the Streamlit Dashboard

```bash
streamlit run app.py --server.port 8502
```

---

## 📊 Deliverables & Evaluation Metrics

| File               | Description                                                              |
| ------------------ | ------------------------------------------------------------------------ |
| `architecture.png` | Visual map of LangGraph state machine and tool-calling flow              |
| `audit_log.json`   | Full execution trace of all tickets (reasoning + tool outputs)           |
| `failure_modes.md` | Documentation of edge case handling (invalid IDs, refund policies, etc.) |

👉 To generate a fresh audit log, click **"Process All Tickets"** in the Streamlit dashboard.

---

## 🧩 Project Structure

```
shopwave/
│
├── agents/     # Reasoning nodes, graph definitions, prompt templates
├── tools/      # Mock APIs (Order DB, Refund Gateway, Shipping)
├── db/         # Knowledge base + mock customer data
├── scripts/    # Visualization & utility scripts
├── app.py      # Streamlit dashboard
├── main.py     # FastAPI entrypoint
└── requirements.txt
```

---

## 🔐 Security Note

* API keys are managed via environment variables
* `.env` files are excluded using `.gitignore`
* Never commit sensitive credentials
* Rotate keys regularly and update your local configuration

---





**Built for the Agentic AI Hackathon 2026 🚀**
