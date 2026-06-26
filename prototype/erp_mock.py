"""ERP Mock - fictitious in-memory ERP data for the prototype.

100% synthetic. There is no real ERP, connection, credential or secret here.
The agent's tools wrap the read/insert helpers below. A few invoices are
curated so the demo queries are deterministic; a seeded random tail adds volume.

# PRODUCTION: replace with real ERP connectors (SAP, TOTVS Protheus, Oracle
#             NetSuite, Microsoft Dynamics 365, Odoo, Bling/Omie) behind the
#             connector abstraction described in ARCHITECTURE.md
"""

import random
from decimal import Decimal
from typing import Dict, List, Optional

from models import GLAccount, Invoice, JournalEntry

random.seed(42)

_VENDORS = ["Vendor A", "Vendor B", "Vendor C", "Vendor D"]
_STATUSES = ["OPEN", "OVERDUE", "PAID"]


def _seeded_invoices(start_id: int, count: int) -> List[Invoice]:
    """Synthetic volume so the dataset is not trivially small."""
    out: List[Invoice] = []
    for i in range(count):
        out.append(
            Invoice(
                id=f"INV-{start_id + i}",
                vendor=random.choice(_VENDORS),
                amount=Decimal(str(round(random.uniform(500, 8000), 2))),
                status=random.choice(_STATUSES),
                due_date=f"2026-{random.randint(1, 6):02d}-{random.randint(1, 28):02d}",
                has_po=random.random() > 0.30,
            )
        )
    return out


# Curated invoices guarantee deterministic demo results, then seeded volume.
INVOICES: List[Invoice] = [
    Invoice("INV-1001", "Vendor A", Decimal("4000.00"), "OPEN", "2026-07-15", True),
    Invoice("INV-1002", "Vendor A", Decimal("12500.00"), "OVERDUE", "2026-05-02", True),
    Invoice("INV-1003", "Vendor B", Decimal("780.00"), "OVERDUE", "2026-04-20", False),
    Invoice("INV-1004", "Vendor C", Decimal("3200.00"), "PAID", "2026-03-10", True),
    Invoice("INV-1005", "Vendor A", Decimal("9100.00"), "OVERDUE", "2026-05-28", False),
] + _seeded_invoices(start_id=1006, count=8)


GL_ACCOUNTS: Dict[str, GLAccount] = {
    "1.1.01": GLAccount("1.1.01", "Cash and Banks", Decimal("1250000.00")),
    "1.1.02": GLAccount("1.1.02", "Accounts Receivable", Decimal("780000.00")),
    "2.1.01": GLAccount("2.1.01", "Accounts Payable", Decimal("430000.00")),
    "4.1.01": GLAccount("4.1.01", "Revenue", Decimal("2100000.00")),
}

# Append-only mock GL journal so post operations are observable in a run.
JOURNAL: List[JournalEntry] = []


def query_invoices(status: Optional[str] = None, vendor: Optional[str] = None) -> List[Invoice]:
    results = INVOICES
    if status:
        results = [i for i in results if i.status.upper() == status.upper()]
    if vendor:
        results = [i for i in results if i.vendor.lower() == vendor.lower()]
    return results


def query_gl_balance(account: str) -> Optional[GLAccount]:
    return GL_ACCOUNTS.get(account)


def insert_journal_entry(entry: JournalEntry) -> Dict[str, str]:
    """Only ever reached after the human-approval gate in tools.post_journal_entry."""
    JOURNAL.append(entry)
    return {"status": "POSTED", "journal_id": f"JE-{len(JOURNAL):04d}"}
