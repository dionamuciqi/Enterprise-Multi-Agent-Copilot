# Healthcare Agent Copilot

Enterprise-grade Multi-Agent AI System for Healthcare  
Built with **LangGraph + Chroma Retrieval + Verified Citations**

---
##  Live Deployment

This project is publicly deployed and accessible here:

**Healthcare AI Copilot (Streamlit Cloud)**  
https://healthcare-agent-copilot.streamlit.app/

The deployed version includes:
- Multi-agent LangGraph workflow
- Citation-grounded RAG
- Prompt injection protection
- Evaluation test queries
- Enterprise-style UI


## Table of Contents

- [Project Goal](#project-goal)
- [System Workflow](#system-workflow)
- [Agents](#agents)
- [Repository Structure](#repository-structure)
- [Setup Instructions](#setup-instructions)
- [Running the Application](#running-the-application)
- [Data & Retrieval](#data--retrieval)
- [Output Format](#output-format)
- [Security (Prompt Injection Guard)](#security-prompt-injection-guard)
- [Evaluation](#evaluation)
- [Acceptance Criteria](#acceptance-criteria)
- [Industry Scenario](#industry-scenario)

---

## Project Goal

Build an end-to-end multi-agent system that transforms a business request into a structured, decision-ready deliverable using coordinated AI agents grounded in retrieved evidence.

The system must:

- Accept a user task (question + goal)
- Generate an execution plan
- Retrieve grounded research
- Draft structured output
- Verify claims against evidence
- Deliver a citation-supported response

---

## System Workflow

```
Plan → Research → Draft → Verify → Deliver
```

This workflow is implemented using **LangGraph multi-agent routing**.

---

## Agents

### 1. Planner Agent
- Decomposes the task
- Creates structured execution plan

### 2. Research Agent
- Performs vector retrieval using Chroma
- Returns evidence with citations:
  - Document name
  - Page number
  - Chunk ID

### 3. Writer Agent
- Produces final structured deliverable
- Uses only retrieved research notes

### 4. Verifier Agent
- Checks for unsupported claims
- Detects hallucinations
- Blocks output if evidence missing
- Forces: `"Not found in sources."`

---

## Repository Structure

```
/app            → Streamlit UI
/agents         → Agent definitions and prompts
/retrieval      → Document loaders + vector search
/data           → Sample documents + README
/eval           → Evaluation prompts
/utils          → Security (prompt injection guard)
README.md       → Setup and documentation
```

---

## Setup Instructions

### 1. Clone repository

```bash
git clone <your-repo-url>
cd Enterprise-Multi-agent-Copilot
```

---

### 2. Create virtual environment (Windows CMD)

```bash
python -m venv venv
venv\Scripts\activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Create environment variables

Create a `.env` file in project root:

```
OPENAI_API_KEY=your_api_key_here
```

---

## Running the Application

From project root:

```bash
streamlit run app/app.py
```

Then open:

```
http://localhost:8501
```

The project runs locally within 5 minutes.

---

## Data & Retrieval

- Use 5–15 public or synthetic documents
- No confidential or private data
- Documents placed inside:

```
/data
```

If ingestion script is required:

```bash
python retrieval/ingest.py
```

Citations format:

```
DocumentName – page – chunk_id
```

If evidence missing:

```
Not found in sources.
```

---

## Output Format

Each final response includes:

### Executive Summary
- Maximum 150 words

### Client-ready Email

### Action List
- Owner
- Due date
- Confidence level

### Sources & Citations

---

## Security (Prompt Injection Guard)

Implemented in:

```
utils/security.py
```

Detects patterns like:

- "ignore previous instructions"
- "reveal system prompt"
- "override rules"

If triggered:
- The system blocks execution
- UI displays Injection Guard status

---

## Evaluation

Evaluation dataset located in:

```
eval/sample_queries.json
```

To run evaluation:

```bash
python eval/run_eval.py
```

Includes 10 test questions.

---

## Industry Scenario

Healthcare & Life Sciences

Example use cases:

- AI governance in hospitals
- Regulatory compliance for AI tools
- Clinical workflow risk analysis
- AI adoption strategy

---

## Acceptance Criteria

✔ End-to-end multi-agent routing works  
✔ Output includes citations  
✔ Verifier blocks unsupported claims  
✔ Trace logs visible  
✔ Runs locally within 5 minutes  

---

## Author

Diona Muçiqi
- Enterprise Multi-Agent Copilot Project
