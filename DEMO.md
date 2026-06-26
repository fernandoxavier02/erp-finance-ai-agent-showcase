# Demo — FinanceOps Copilot Educational Prototype

---

## Prerequisites

- Python 3.11+ (standard library only — no third-party packages required to run)

---

## Run

```bash
cd prototype
python main.py
```

Run the tests (assert-based, no dependencies):

```bash
python prototype/tests/test_agent.py
```

Optional — run the same tests under pytest:

```bash
pip install -r prototype/requirements.txt
python -m pytest prototype/tests/test_agent.py -q
```

---

## What the prototype does

It runs five finance queries end to end, each through the same loop:
**natural-language query → rule-based router → MCP-style tool → composed answer.**

| # | Query | Tool selected | Outcome |
|---|---|---|---|
| 1 | "Show overdue invoices for Vendor A" | `get_invoices` | Filters in-memory invoices by status + vendor |
| 2 | "What's the GL balance of account 2.1.01?" | `get_gl_balance` | Reads the mock general-ledger balance |
| 3 | "Can I auto-approve a $4,000 invoice with a PO?" | `search_policy` | RAG retrieves the AP approval-threshold policy |
| 4 | "Post the monthly accrual journal entry" | `post_journal_entry` | **Blocked** — pending human approval |
| 5 | "List all open invoices" | `get_invoices` | Filters in-memory invoices by status |

All data is 100% synthetic and in-memory. The ERP "connection" is mocked — there is no network call, no credential, and no external model.

---

## Prototype vs. Production

| Concern | Prototype (this repo) | Production (proprietary) |
|---|---|---|
| Tool layer | MCP-**style** registry (function + JSON-schema dict) | Real MCP server SDK |
| Agent | Rule-based keyword router | Tool-calling LLM (local Llama 3 / Claude) |
| ERP data | Mock in-memory invoices & GL | Live connectors (SAP, Oracle, NetSuite, TOTVS, Dynamics, REST APIs; Odoo & Bling/Omie connector-ready) |
| RAG | Toy embedding + brute-force cosine | sentence-transformers (MiniLM) + FAISS |
| Deployment | Single script, offline | On-prem service, data never leaves the network |

> The connector targets shown reflect the product's integration surface; this showcase does not assert a specific production deployment for any individual ERP.
