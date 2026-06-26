"""Main - ERP Finance AI Agent Prototype.

Runs a handful of finance queries end to end through the local agent:
natural-language query -> rule-based router -> MCP-style tool -> answer.
Everything is in-memory, synthetic, offline and standard-library only.
"""

from typing import Any

import agent
import tools
from models import RunSummary

EXAMPLE_QUERIES = [
    "Show overdue invoices for Vendor A",
    "What's the GL balance of account 2.1.01?",
    "Can I auto-approve a $4,000 invoice with a PO?",
    "Post the monthly accrual journal entry",
    "List all open invoices",
]


def _render_result(tool: str, result: Any) -> str:
    """Compact, human-readable view of a raw tool result."""
    if tool == "get_invoices":
        return f"{len(result)} invoice(s): " + ", ".join(
            f"{i.id}/{i.vendor}/{i.status}" for i in result[:5]
        ) + (" ..." if len(result) > 5 else "")
    if tool == "search_policy":
        top = result[0]
        return f"top chunk='{top['section']}' (score={top['score']})"
    return str(result)


def main() -> None:
    print("=" * 70)
    print("ERP Finance AI Agent - Prototype")
    print("=" * 70)

    print("\n>>> MCP Tools Exposed")
    for spec in tools.list_tools():
        required = ", ".join(spec.input_schema.get("required", [])) or "-"
        print(f"    {spec.name:20} | required: {required}")

    turns = []
    for n, query in enumerate(EXAMPLE_QUERIES, start=1):
        turn = agent.run_turn(query)
        turns.append(turn)
        print(f"\n>>> Turn {n}")
        print(f"    Query : {turn.query}")
        print(f"    Tool  : {turn.tool}")
        print(f"    Result: {_render_result(turn.tool, turn.result)}")
        print(f"    Answer: {turn.answer}")

    distinct = sorted({t.tool for t in turns})
    writes_blocked = sum(
        1 for t in turns
        if t.tool == "post_journal_entry" and t.result.get("status") == "BLOCKED"
    )
    policy_lookups = sum(1 for t in turns if t.tool == "search_policy")
    summary = RunSummary(
        total_turns=len(turns),
        distinct_tools=distinct,
        writes_blocked=writes_blocked,
        policy_lookups=policy_lookups,
    )

    print("\n>>> Run Summary")
    print(f"    Total turns      : {summary.total_turns}")
    print(f"    Distinct tools   : {', '.join(summary.distinct_tools)}")
    print(f"    Writes blocked   : {summary.writes_blocked} (human-in-the-loop)")
    print(f"    Policy lookups   : {summary.policy_lookups}")

    print("\n" + "=" * 70)
    print("Prototype execution completed successfully.")
    print("=" * 70)


if __name__ == "__main__":
    main()
