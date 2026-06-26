"""Tools - MCP-style tool registry for the ERP Finance AI Agent prototype.

Each tool is a plain Python function paired with a ToolSpec carrying a
JSON-schema-like descriptor (name / description / inputSchema). The agent
discovers tools via list_tools() and invokes them via call_tool(name, args) -
the same shape a real MCP server exposes.

# PRODUCTION: expose via the real MCP server SDK
"""

from typing import Any, Callable, Dict, List

import erp_mock
import rag
from models import GLAccount, Invoice, JournalEntry, ToolSpec


# --- Tool implementations -------------------------------------------------

def get_invoices(status: str = "", vendor: str = "") -> List[Invoice]:
    return erp_mock.query_invoices(status=status or None, vendor=vendor or None)


def get_gl_balance(account: str) -> Dict[str, Any]:
    acct: GLAccount | None = erp_mock.query_gl_balance(account)
    if acct is None:
        return {"status": "NOT_FOUND", "account": account}
    return {"status": "OK", "account": acct.code, "name": acct.name, "balance": acct.balance}


def post_journal_entry(entry: JournalEntry) -> Dict[str, Any]:
    # Human-in-the-loop guard: a write to the GL never happens without approval.
    if not entry.approved_by_human:
        return {
            "status": "BLOCKED",
            "reason": "Journal entry requires explicit human approval before posting.",
        }
    return erp_mock.insert_journal_entry(entry)


def search_policy(query: str) -> List[Dict[str, Any]]:
    return rag.retrieve(query, k=1)


# --- MCP-style registry ---------------------------------------------------

def _spec(name: str, description: str, input_schema: Dict[str, Any]) -> ToolSpec:
    return ToolSpec(name=name, description=description, input_schema=input_schema)


TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {
    "get_invoices": {
        "spec": _spec(
            "get_invoices",
            "Read invoices from the ERP, optionally filtered by status and/or vendor.",
            {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["OPEN", "OVERDUE", "PAID"],
                        "description": "Filter by invoice status.",
                    },
                    "vendor": {"type": "string", "description": "Filter by vendor name."},
                },
                "required": [],
            },
        ),
        "fn": get_invoices,
    },
    "get_gl_balance": {
        "spec": _spec(
            "get_gl_balance",
            "Read the current balance of a general-ledger account by its code.",
            {
                "type": "object",
                "properties": {
                    "account": {"type": "string", "description": "GL account code, e.g. 2.1.01."},
                },
                "required": ["account"],
            },
        ),
        "fn": get_gl_balance,
    },
    "post_journal_entry": {
        "spec": _spec(
            "post_journal_entry",
            "Post a journal entry to the GL. Requires a human-approval flag; "
            "blocked otherwise (human-in-the-loop).",
            {
                "type": "object",
                "properties": {
                    "entry": {
                        "type": "object",
                        "description": "JournalEntry with description, debit_account, "
                        "credit_account, amount and approved_by_human.",
                    },
                },
                "required": ["entry"],
            },
        ),
        "fn": post_journal_entry,
    },
    "search_policy": {
        "spec": _spec(
            "search_policy",
            "Retrieve the most relevant internal finance policy passage for a question (RAG).",
            {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Natural-language policy question."},
                },
                "required": ["query"],
            },
        ),
        "fn": search_policy,
    },
}


def list_tools() -> List[ToolSpec]:
    """MCP-style discovery: the specs an LLM (or this prototype's router) sees."""
    return [entry["spec"] for entry in TOOL_REGISTRY.values()]


def call_tool(name: str, arguments: Dict[str, Any]) -> Any:
    """MCP-style invocation by name with keyword arguments."""
    if name not in TOOL_REGISTRY:
        raise KeyError(f"Unknown tool: {name}")
    fn: Callable = TOOL_REGISTRY[name]["fn"]
    return fn(**arguments)
