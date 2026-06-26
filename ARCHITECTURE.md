# Architecture — FinanceOps Copilot

---

## 1. Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          USER (Finance Team)                                │
│        "Show overdue invoices for Vendor A"   ·   "Can I auto-approve...?"   │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │
                    ┌───────────────▼────────────────┐
                    │     LOCAL AGENT (on-prem)        │
                    │  · Router / tool-calling LLM     │
                    │  · Tool selection + arguments    │
                    │  · Answer composition            │
                    └───────┬──────────────────┬───────┘
                            │                  │
         ┌──────────────────▼───────┐   ┌──────▼───────────────────────────────┐
         │   RAG: Finance Policies  │   │        MCP TOOL SERVER               │
         │  ┌────────────────────┐  │   │  ┌────────────┐ ┌────────────────┐   │
         │  │ Policy docs        │  │   │  │get_invoices│ │ get_gl_balance │   │
         │  │   → embed          │  │   │  └────────────┘ └────────────────┘   │
         │  │   → vector store   │  │   │  ┌────────────────┐ ┌─────────────┐  │
         │  │   → retrieve top-k │  │   │  │post_journal_entry│ │search_policy│ │
         │  └────────────────────┘  │   │  └────────────────┘ └─────────────┘  │
         └──────────────────────────┘   └──────────────────┬───────────────────┘
                                                           │
                                       ┌───────────────────▼───────────────────┐
                                       │      ERP CONNECTOR ABSTRACTION         │
                                       │  one contract · pluggable adapters     │
                                       └───────────────────┬───────────────────┘
                                                           │
        ┌──────────┬──────────┬──────────────┬────────────┴─────┬──────────────┐
   ┌────▼───┐ ┌────▼────┐ ┌───▼────────┐ ┌───▼──────────┐ ┌─────▼───┐ ┌────────▼────┐
   │  SAP   │ │ Oracle  │ │  NetSuite  │ │    TOTVS     │ │Dynamics │ │  REST APIs  │
   │        │ │         │ │            │ │   Protheus   │ │   365   │ │   (HTTP)    │
   └────────┘ └─────────┘ └────────────┘ └──────────────┘ └─────────┘ └─────────────┘
```

> The connector targets shown reflect the product's integration surface; this showcase does not assert a specific production deployment for any individual ERP.

---

## 2. MCP Tool Schema Design

Every ERP capability is exposed as a **tool** with a JSON-schema-like descriptor — the same shape a real MCP server advertises via `list_tools()` and invokes via `call_tool(name, arguments)`. The LLM never touches the ERP directly; it only sees typed tools.

| Tool | Input schema (required) | Returns |
|---|---|---|
| `get_invoices` | `status` (enum), `vendor` — both optional | Invoices matching the filter |
| `get_gl_balance` | `account` (required) | Account code, name, balance |
| `post_journal_entry` | `entry` (required, carries `approved_by_human`) | Posts to GL — gated by human approval |
| `search_policy` | `query` (required) | Top policy passage (RAG) |

**Why JSON-schema descriptors:** they make every tool self-documenting and let any tool-calling model select and fill arguments without bespoke glue per ERP.

---

## 3. Connector Abstraction

A single internal contract sits between the MCP tool server and the concrete ERPs. Each ERP gets a **pluggable adapter** that maps the contract's operations (read invoices, read GL, post entry) onto that ERP's native API.

| Concern | Rule |
|---|---|
| **Contract** | Tools speak the abstraction, never an ERP-specific API |
| **Adapters** | One adapter per ERP, versioned independently |
| **Isolation** | A failing adapter degrades one ERP, not the agent |
| **Primary targets** | SAP · Oracle · NetSuite · TOTVS Protheus · Dynamics 365 · REST APIs · MCP Server |
| **Connector-ready** | Odoo · Bling · Omie |

> The connector targets shown reflect the product's integration surface; this showcase does not assert a specific production deployment for any individual ERP.

---

## 4. Local / Private Deployment & Security

The defining constraint: **confidential financial data never leaves the company network.**

| Domain | Decision |
|---|---|
| **Inference** | Local LLM (e.g. Llama 3) running on-prem — no external API call with financial data |
| **Data residency** | ERP data, GL, vendor master and policy docs stay inside the network boundary |
| **Writes** | Any GL-mutating action requires an explicit human-approval flag (see ADR-003) |
| **Least privilege** | Connector credentials scoped per ERP; read vs. write separated |
| **Auditability** | Every tool call and its arguments are logged for the finance audit trail |

---

## 5. Architecture Decisions (ADRs)

### ADR-001 — MCP as the Integration Contract
**Context:** Finance teams run many different ERPs, each with its own API; bespoke point-to-point integrations do not scale.
**Decision:** Expose every ERP capability as an MCP tool with a JSON-schema descriptor; the agent talks only to MCP.
**Consequence:** New ERPs are added by writing an adapter behind the contract — the agent and its prompts are untouched.

### ADR-002 — Local LLM for Data Confidentiality
**Context:** Cloud AI services are frequently prohibited for confidential financial data (GL, vendor master, payroll-adjacent figures).
**Decision:** Run inference on a local/on-prem LLM so confidential data never leaves the network.
**Consequence:** Stronger confidentiality and compliance posture; trade-off is operating local model infrastructure instead of a managed API.

### ADR-003 — Human-in-the-Loop for Any Write/Post Action
**Context:** Posting to the general ledger is irreversible and audit-sensitive; an autonomous agent must not write unsupervised.
**Decision:** Read operations run autonomously, but any write (e.g. `post_journal_entry`) is **blocked** until a human sets the approval flag.
**Consequence:** Safety and auditability by construction; trade-off is that fully unattended posting is intentionally not supported.
