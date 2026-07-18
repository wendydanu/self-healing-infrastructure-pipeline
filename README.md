# Self-Healing Infrastructure Pipeline (S.H.I.P) Engine

An autonomous self-healing infrastructure pipeline powered by FastAPI and Gemini AI. This system is architected to automatically intercept server error logs, dynamically analyze root causes, sanitize output via Regex, and execute automated production hotfix injections to minimize system downtime.

---

## The Value Proposition: Why S.H.I.P Engine?

In traditional production environments, resolving a server crash is slow, manual, and costly. S.H.I.P Engine completely redefines this workflow:

* **Immediate MTTR Reduction (From Hours to Seconds):** Instead of waiting for an on-call engineer to wake up, read logs, and write a hotfix, the pipeline detects, debugs, and patches the system autonomously in less than 3 seconds.
* **Zero-Downtime Resilience:** By executing runtime file injections directly into the faulty production scripts, the system heals itself dynamically without requiring a full server redeployment or service interruption.
* **Cost & Operational Efficiency:** Minimizes production downtime losses and frees development teams from repetitive, stress-inducing debugging tasks, allowing them to focus purely on building core features.
* **Secured AI Execution & Sandboxing:** Unlike raw AI code generation, our built-in Regex Sanitizer acts as a strict firewall, while our newly implemented Sandbox Isolation layer ensures code patches are jailed within safe directory boundaries.
* **Visual Telemetry & Multi-Agent Collaboration:** Fully orchestrates complex root-cause diagnostic chains across multiple specialized AI models while streaming operational matrix updates live via high-frequency network streams.

---

## Project Roadmap & Sprint Progress

* [x] **DevDay 1:** FastAPI Core Architecture & Asynchronous Database Setup (SQLAlchemy + SQLite)
* [x] **DevDay 2:** Error Log Interceptor Development & Strict Regex Output Sanitizer Engine
* [x] **DevDay 3:** Gemini AI Prompt Engineering & Autonomous Production File Patch Injector
* [x] **DevDay 4:** Automated Unit Testing Framework & Seamless Git Automation Pipeline
* [x] **DevDay 5:** Security Hardening, Token Validation, and Environment Isolation Layer
* [x] **DevDay 6:** Multi-agent AI Integration & Real-time WebSockets Telemetry Dashboard
* [ ] **DevDay 7:** Distributed Logging, Distributed Tracing, and Production Monitoring Clusters

---

## Tech Stack

* **Language:** Python 3.10+ (Running Python 3.13+)
* **Framework:** FastAPI (Asynchronous Python WebSockets Core)
* **Testing & Security:** Pytest, Pytest-Asyncio, & `pip-audit`
* **AI Core:** Google Gemini AI API (`gemini-2.5-flash` Multi-Agent Configuration)
* **Database:** Profiled SQLAlchemy (Async SQLite via `aiosqlite`)
* **UI & Rendering Framework:** Jinja2 HTML5, Tailwind CSS, and Chart.js
* **Environment Management:** Pydantic Settings & Dotenv
* **Version Control:** Git & GitHub

---

## How It Was Built: Step-by-Step Development

This project was developed through a highly structured sprint methodology, transitioning from a local prototype to a robust cloud-managed repository:

### 1. Architectural Initialization
The development began with scaffolding the FastAPI core structure. To ensure high performance and non-blocking I/O operations, an asynchronous database layer was established using SQLAlchemy alongside `aiosqlite` to log every system interception securely.

### 2. Log Interception & Regex Sanitization
A specialized ingest endpoint was engineered to act as a production webhook for broken servers. When a crash occurs, the raw log is captured. To protect the system from malicious AI output or invalid syntax, a strict Regex Sanitizer was implemented to filter out everything except pure executable Python code.

### 3. AI Core & Injection Logic
Integration of the Google Gemini AI engine was achieved by designing precise prompt payloads that force the model to behave purely as an autonomous debugging compiler. Once a valid patch is generated and sanitized, the engine invokes the `File Patch Injector` to overwrite the faulty local script (e.g., `server_math.py`) in real-time.

### 4. Git Synchronization & Cloud Deployment
To ensure proper version control and portfolio visibility, Git was natively integrated into the workspace. After handling Windows environment path alignment and authenticating securely via Git Credential Manager, the clean codebase milestone was pushed directly to GitHub under the main branch.

### 5. Automated Unit Testing & Self-Healing Loop (DevDay 4 Special)
An autonomous reliability loop was engineered to catch and patch logical failures under 3 seconds. The system flow executes as follows:
* **Detection:** A silent logical bug in `server_math.py` triggered a pipeline halt on `pytest` execution (`AssertionError`).
* **Telemetry & Recovery:** The pipeline captured the stack trace, dispatched it to S.H.I.P's dynamic `/api/v1/intercept-log` endpoint, and stored the Gemini-compiled patch inside the SQLite database.
* **Autonomous Injection:** Pinging the `/api/v1/deploy-patch` endpoint automatically wrote the hotfix back to the server environment, restoring the system to a **100% Green** state with zero manual code modifications.

### 6. Enterprise Security Hardening & Isolation Layer (DevDay 5 Special)
To upgrade the pipeline for mission-critical production environments, a rigorous multi-layered defense matrix was engineered:
* **Automated Startup Vulnerability Scanning:** Programmatic integration of `pip-audit` into the FastAPI Lifespan architecture. The server automatically conducts a full dependency compliance audit upon initialization, successfully detecting real-world vulnerabilities (e.g., `PYSEC-2026-3444` in `httplib2`) before opening communication ports.
* **Token Validation Middleware Gate:** Implementation of a strict custom header authentication protocol using FastAPI `Depends` and Pydantic Settings. Any unauthenticated telemetry attempts or missing tokens are immediately blocked at the perimeter with automated `422 Unprocessable Content` / `403 Forbidden` compliance barriers.
* **Path Traversal Protection (Sandbox Jail Guard):** Refactoring of the hotfix injection core using `pathlib.Path.resolve()`. The system forces strict boundary evaluation, preventing malicious *path traversal* attacks. If a patch attempts to break out of the defined `SAFE_SANDBOX_DIR`, the transaction is killed instantly.

### 7. Multi-Agent AI Core & Real-time WebSockets Dashboard (DevDay 6 Special)
The pipeline evolved from a single-model infrastructure into a collaborative, decoupled intelligent system equipped with a full visual monitoring interface:
* **Decoupled Multi-Agent Reasoning Chain:** Upgrading of the AI layer by decoupling operations into two distinct, specialized agents running on `gemini-2.5-flash`. *Agent 1 (Root Cause Analyst)* processes error stack traces to diagnose failure parameters without writing code. *Agent 2 (Patching Compiler)* ingests the diagnostic payload and synthesizes high-fidelity, isolated Python remediation code.
* **Bi-directional WebSockets Telemetry Core:** Engineering of a `ConnectionManager` event broadcaster utilizing asynchronous non-blocking connection lines (`@app.websocket("/ws/telemetry")`). The API broadcasts incident lifecycles dynamically as they occur without thread pools stalling.
* **Single-Stack Operational Dashboard Layout:** Implementation of a real-time event monitoring workspace built via Jinja2 templates, Tailwind CSS, and Chart.js. The interface dynamically renders live incident logs, historical chart flows, and agent processing timelines instantly without web browser reloads.

---

*Developed iteratively to advance the standards of autonomous DevOps and self-healing systems.*