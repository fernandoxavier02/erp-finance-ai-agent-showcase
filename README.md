<div align="center">

<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:1e3a5f,100:0f766e&height=200&section=header&text=FinanceOps%20Copilot&fontSize=44&fontColor=ffffff&animation=fadeIn&fontAlignY=35&desc=MCP%20%C2%B7%20Local%20Agent%20%C2%B7%20RAG%20%C2%B7%20Finance%20Automation&descAlignY=55&descSize=16"/>

<p>
  <img src="https://img.shields.io/badge/Python-1e3a5f?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/MCP-0f766e?style=for-the-badge&logo=anthropic&logoColor=white"/>
  <img src="https://img.shields.io/badge/RAG-1e3a5f?style=for-the-badge&logo=langchain&logoColor=white"/>
  <img src="https://img.shields.io/badge/Local%20LLM-0f766e?style=for-the-badge&logo=ollama&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-1e3a5f?style=for-the-badge&logo=fastapi&logoColor=white"/>
</p>

<p>
  <img src="https://img.shields.io/badge/Status-Showcase-0f766e?style=flat-square"/>
  <img src="https://img.shields.io/badge/Data-100%25%20Synthetic-1e3a5f?style=flat-square"/>
  <img src="https://img.shields.io/badge/License-Proprietary-1e3a5f?style=flat-square"/>
</p>

</div>

---

> **Type:** Architectural technical showcase  
> **Status:** Proprietary production system · This showcase contains an educational prototype  
> **Author:** Fernando Xavier  
> **Domain:** ERP Integration · Financial Department Automation  
> **License:** Proprietary — All rights reserved. Showcase for professional portfolio evaluation only.

---

*As a finance executive and AI solutions architect, I built local AI agents that connect to company ERPs and automate finance-department work. This showcase demonstrates the problem mastery and the business outcome — the production system is proprietary and confidential.*

---

## 🎯 The Business Problem

Finance teams need answers and actions that span **ERP data** (AP/AR, general ledger, invoices) **and internal policies** — but the ERP is a silo:

- **Queries are manual** — someone logs in, navigates, and digs for every answer
- **Exports are re-keyed** — data leaves the ERP as a spreadsheet and is retyped elsewhere
- **Approvals wait in inboxes** — invoices sit until a human notices them
- **Answers require a person** — there is no way to simply *ask* the ERP a question

On top of that, **cloud AI tools are often off-limits** for confidential financial data: sending the general ledger or vendor master to an external API is a non-starter for most controllership and treasury teams.

Result: slow answers, manual re-keying, late approvals, and an AI capability gap exactly where confidentiality matters most.

---

## 🏗️ The Solution

A **local, privacy-preserving AI agent** that talks to the ERP through an **MCP (Model Context Protocol — an open standard for connecting AI models to tools and data) tool server**, combines that live data with **RAG (Retrieval-Augmented Generation — grounding the model's answers in your own documents) over internal finance policies**, and automates finance-department tasks. Data never leaves the company network.

### Core Capabilities

| Capability | Description | Impact |
|---|---|---|
| **ERP MCP Tool Server** | Exposes the ERP as typed tools: read invoices, read GL balances, post journal entries | ~1,248 invoices & documents processed |
| **Document Intelligence Pipeline** | Parses and extracts fields from invoices/documents before they reach the agent | 96.7% extraction accuracy |
| **Local Privacy-Preserving Agent** | Runs on-prem against a local LLM; confidential data never leaves the network | Cloud-AI risk removed for financial data |
| **AP Approval Automation** | Auto-approves invoices that are within policy; routes the rest to a human | $2.34M AP approved within policy |
| **Cash & Reconciliation** | Triggers reconciliation and forecasts the cash position without a person watching | $12.8M cash position forecast |
| **RAG over Finance Policies + Variance** | Grounds answers in the company's own policies and drafts budget-variance commentary | ~156 hours/month saved |

### MCP Tools Exposed

| Tool | Input | Returns |
|---|---|---|
| `get_invoices` | `status` (OPEN/OVERDUE/PAID), `vendor` | List of invoices matching the filter |
| `get_gl_balance` | `account` (GL code, e.g. `2.1.01`) | Account code, name and current balance |
| `post_journal_entry` | `entry` (with `approved_by_human` flag) | Posts to the GL — **blocked** until a human approves |
| `search_policy` *(RAG)* | `query` (natural-language question) | The most relevant internal-policy passage |

### Supported Connector Targets

The MCP server sits in front of common market ERPs through a single connector abstraction:

- **Primary connector targets (shown in the product):** SAP · Oracle · NetSuite · TOTVS Protheus · Microsoft Dynamics 365 · REST APIs · MCP Server
- **Connector-ready (broader targets):** Odoo · Bling · Omie

> The connector targets shown reflect the product's integration surface; this showcase does not assert a specific production deployment for any individual ERP.

---

## 📈 Results

![FinanceOps Copilot — MCP-connected ERPs, document intelligence pipeline & AI assistant](assets/screenshots/01-financeops-copilot-dashboard.png)

| Dashboard KPI | Value |
|---|---|
| **Invoices & documents processed** | ~1,248 |
| **Extraction accuracy** | 96.7% |
| **AP approved** | $2.34M |
| **Cash forecast** | $12.8M |
| **Hours saved** | 156 |

> *Figures mirror the product dashboard and are illustrative showcase values (synthetic data), not audited client numbers. See [RESULTS.md](./RESULTS.md) for the sanitized case narrative.*

---

## 🏛️ Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed diagrams, the MCP tool schema design, the connector abstraction, and the ADRs.

```
┌──────────────────┐      ┌──────────────────────┐      ┌────────────────────┐
│  Finance Team    │      │   Local Agent        │      │  MCP Tool Server   │
│  (User)          │─────►│   · Router / LLM     │─────►│  · get_invoices    │
│  "show overdue   │      │   · Tool selection   │      │  · get_gl_balance  │
│   invoices..."   │◄─────│   · Answer compose   │◄─────│  · post_journal... │
└──────────────────┘      └──────────┬───────────┘      │  · search_policy   │
                                     │                  └─────────┬──────────┘
                          ┌──────────▼───────────┐                │
                          │  RAG over Policies   │      ┌─────────▼──────────┐
                          │  docs → embed →      │      │ Connector          │
                          │  vector store        │      │ Abstraction        │
                          └──────────────────────┘      └─────────┬──────────┘
                                                                  │
                        ┌──────────┬──────────┬──────────┬────────┴───┬──────────┐
                       SAP     Oracle    NetSuite     TOTVS      Dynamics   REST APIs
```
> Primary connector targets shown above; Odoo and Bling/Omie are connector-ready.

> The connector targets shown reflect the product's integration surface; this showcase does not assert a specific production deployment for any individual ERP.

---

## 🧪 Educational Prototype

A pure-Python prototype (standard library only, runs fully offline) demonstrates the end-to-end loop on 100% fictitious in-memory data:

- An **MCP-style tool registry** (each tool = a function + a JSON-schema-like spec)
- A **rule-based router** standing in for the tool-calling LLM
- A **toy embedding + brute-force retriever** standing in for RAG
- A **human-in-the-loop guard** that blocks any GL write without approval

```bash
cd prototype
python main.py
```

See [DEMO.md](./DEMO.md) for the run walkthrough and the prototype-vs-production map.

---

## ⚠️ Legal Notice

**© 2026 Fernando Xavier. All rights reserved.**

The production system is proprietary, commercially licensed, and confidential. This repository contains only high-level architectural documentation, sanitized narratives, an educational prototype with 100% fictitious data, and synthetically generated images.

Reproduction, distribution, or commercial use of the production code is prohibited.

---

<details>
<summary><sub>Tech stack (for technical reviewers)</sub></summary>

- **Agent:** Local LLM (Llama 3 / Claude) with tool-calling
- **Integration:** Model Context Protocol (MCP) tool server
- **RAG:** sentence-transformers (MiniLM) embeddings + FAISS vector store
- **API:** FastAPI service layer
- **ERP connectors:** Pluggable adapters behind a single connector abstraction
- **Deployment:** On-prem / private network — data never leaves the company

</details>

---

## 📬 Contact

**Fernando Xavier**  
Finance Executive & AI Solutions Architect · Founder @ FX Studio AI  
São Paulo, BR · PT / EN (C2) / ES (C1)  

[LinkedIn](https://linkedin.com/in/fernandoxavier02) · contato@fxstudioai.com · [fxstudioai.com](https://fxstudioai.com)

---

<div align="center">
<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:1e3a5f,100:0f766e&height=100&section=footer"/>
</div>
