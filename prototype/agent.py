"""Agent - rule-based router standing in for a tool-calling LLM.

Maps a natural-language finance query to one MCP-style tool plus arguments
using ordered keyword rules, executes the tool through the registry, and
composes a plain-language answer. Deterministic and dependency-free.

# PRODUCTION: replace rule-based router with a tool-calling LLM (local Llama 3 / Claude)
"""

import re
from decimal import Decimal
from typing import Any, Dict, Tuple

import erp_mock
import tools
from models import AgentTurn, JournalEntry

# Keyword groups, evaluated top to bottom. Policy questions are checked before
# the literal "invoice" rule so "can I auto-approve this invoice?" routes to RAG.
_POLICY_KW = ("policy", "auto-approve", "auto approve", "allowed", "within policy", "can i")
_POST_KW = ("post ", "journal entry", "accrual", "book the", "record entry")
_BALANCE_KW = ("balance", "general ledger", " gl ", "ledger account", "account ")
_INVOICE_KW = ("invoice", "overdue", "open ", "payable", "vendor")

_STATUS_BY_KW = {"overdue": "OVERDUE", "open": "OPEN", "paid": "PAID"}
_ACCOUNT_RE = re.compile(r"\b\d+(?:\.\d+)+\b")


def _extract_status(q: str) -> str:
    for kw, status in _STATUS_BY_KW.items():
        if kw in q:
            return status
    return ""


def _extract_vendor(q: str) -> str:
    for vendor in erp_mock._VENDORS:
        if vendor.lower() in q:
            return vendor
    return ""


def _extract_account(q: str) -> str:
    match = _ACCOUNT_RE.search(q)
    return match.group(0) if match else ""


def route(query: str) -> Tuple[str, Dict[str, Any]]:
    """Return (tool_name, arguments) for a natural-language query."""
    q = f" {query.lower()} "

    if any(kw in q for kw in _POLICY_KW):
        return "search_policy", {"query": query}

    if any(kw in q for kw in _POST_KW):
        # Agent drafts the entry but never sets the human-approval flag itself.
        entry = JournalEntry(
            description="Monthly accrual (agent draft)",
            debit_account="4.1.01",
            credit_account="2.1.01",
            amount=Decimal("8500.00"),
            approved_by_human=False,
        )
        return "post_journal_entry", {"entry": entry}

    if any(kw in q for kw in _BALANCE_KW):
        return "get_gl_balance", {"account": _extract_account(query)}

    if any(kw in q for kw in _INVOICE_KW):
        return "get_invoices", {"status": _extract_status(q), "vendor": _extract_vendor(q)}

    # Default: treat anything else as a policy lookup (safe, read-only).
    return "search_policy", {"query": query}


def compose_answer(tool: str, arguments: Dict[str, Any], result: Any) -> str:
    if tool == "get_invoices":
        flt = []
        if arguments.get("status"):
            flt.append(arguments["status"])
        if arguments.get("vendor"):
            flt.append(arguments["vendor"])
        label = (" / ".join(flt)) or "all"
        total = sum((i.amount for i in result), Decimal("0"))
        return f"Found {len(result)} invoice(s) [{label}] totaling USD {total:,.2f}."

    if tool == "get_gl_balance":
        if result.get("status") != "OK":
            return f"No GL account found for code {arguments.get('account')!r}."
        return f"GL account {result['account']} ({result['name']}) balance: USD {result['balance']:,.2f}."

    if tool == "post_journal_entry":
        if result.get("status") == "BLOCKED":
            return f"Write blocked - {result['reason']}"
        return f"Journal entry posted as {result['journal_id']}."

    if tool == "search_policy":
        top = result[0]
        return f"Policy '{top['section']}': {top['text']}"

    return "No answer."


def run_turn(query: str) -> AgentTurn:
    tool, arguments = route(query)
    result = tools.call_tool(tool, arguments)
    answer = compose_answer(tool, arguments, result)
    return AgentTurn(query=query, tool=tool, arguments=arguments, result=result, answer=answer)
