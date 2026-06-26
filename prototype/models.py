"""Models - ERP Finance AI Agent Prototype."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, List


@dataclass
class Invoice:
    id: str
    vendor: str
    amount: Decimal
    status: str  # OPEN, OVERDUE, PAID
    due_date: str
    has_po: bool  # backed by a matching purchase order


@dataclass
class GLAccount:
    code: str
    name: str
    balance: Decimal


@dataclass
class JournalEntry:
    description: str
    debit_account: str
    credit_account: str
    amount: Decimal
    approved_by_human: bool = False  # human-in-the-loop gate for any write


@dataclass
class PolicyChunk:
    doc: str
    section: str
    text: str


@dataclass
class ToolSpec:
    """MCP-style tool descriptor: name + description + JSON-schema-like inputSchema."""
    name: str
    description: str
    input_schema: Dict[str, Any]


@dataclass
class AgentTurn:
    query: str
    tool: str
    arguments: Dict[str, Any]
    result: Any
    answer: str


@dataclass
class RunSummary:
    total_turns: int
    distinct_tools: List[str]
    writes_blocked: int
    policy_lookups: int
