"""Tests - ERP Finance AI Agent Prototype."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from decimal import Decimal

import agent
import tools
from models import JournalEntry


def test_router_picks_correct_tool():
    assert agent.route("Show overdue invoices for Vendor A")[0] == "get_invoices"
    assert agent.route("What's the GL balance of account 2.1.01?")[0] == "get_gl_balance"
    assert agent.route("Can I auto-approve a $4,000 invoice with a PO?")[0] == "search_policy"
    assert agent.route("Post the monthly accrual journal entry")[0] == "post_journal_entry"


def test_get_invoices_filters():
    overdue_a = tools.call_tool("get_invoices", {"status": "OVERDUE", "vendor": "Vendor A"})
    assert len(overdue_a) >= 1
    assert all(i.status == "OVERDUE" and i.vendor == "Vendor A" for i in overdue_a)


def test_get_gl_balance():
    result = tools.call_tool("get_gl_balance", {"account": "2.1.01"})
    assert result["status"] == "OK"
    assert result["name"] == "Accounts Payable"


def test_post_journal_entry_blocked_without_approval():
    draft = JournalEntry("accrual", "4.1.01", "2.1.01", Decimal("8500.00"), approved_by_human=False)
    blocked = tools.call_tool("post_journal_entry", {"entry": draft})
    assert blocked["status"] == "BLOCKED"

    approved = JournalEntry("accrual", "4.1.01", "2.1.01", Decimal("8500.00"), approved_by_human=True)
    posted = tools.call_tool("post_journal_entry", {"entry": approved})
    assert posted["status"] == "POSTED"


def test_search_policy_retrieves_relevant_chunk():
    hits = tools.call_tool("search_policy", {"query": "auto-approve invoice with purchase order"})
    assert hits[0]["section"] == "AP Invoice Approval Thresholds"


if __name__ == "__main__":
    test_router_picks_correct_tool()
    print("[PASS] test_router_picks_correct_tool")
    test_get_invoices_filters()
    print("[PASS] test_get_invoices_filters")
    test_get_gl_balance()
    print("[PASS] test_get_gl_balance")
    test_post_journal_entry_blocked_without_approval()
    print("[PASS] test_post_journal_entry_blocked_without_approval")
    test_search_policy_retrieves_relevant_chunk()
    print("[PASS] test_search_policy_retrieves_relevant_chunk")
    print("\n[SUCCESS] All tests passed!")
