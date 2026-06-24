"""Transaction logging module for the Neon City Simulation Engine."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .currency import CurrencyType


@dataclass
class Transaction:
    """Represents a single transaction between two agents."""
    transaction_id: str
    from_id: str
    to_id: str
    currency: CurrencyType
    amount: float
    timestamp: float
    metadata: Dict = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.currency, str):
            self.currency = CurrencyType(self.currency)
        if self.amount < 0:
            raise ValueError("Transaction amount must be non-negative")

    def to_dict(self) -> dict:
        return {
            "transaction_id": self.transaction_id,
            "from_id": self.from_id,
            "to_id": self.to_id,
            "currency": self.currency.value,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


class TransactionLog:
    """Records and queries all transactions in the economy."""

    def __init__(self):
        self._transactions: List[Transaction] = []
        # agent_id -> list of transaction indices
        self._agent_index: Dict[str, List[int]] = {}

    def record(self, tx: Transaction) -> None:
        """Records a transaction."""
        idx = len(self._transactions)
        self._transactions.append(tx)

        # Index by both parties
        if tx.from_id not in self._agent_index:
            self._agent_index[tx.from_id] = []
        self._agent_index[tx.from_id].append(idx)

        if tx.to_id not in self._agent_index:
            self._agent_index[tx.to_id] = []
        self._agent_index[tx.to_id].append(idx)

    def get_for_agent(self, agent_id: str) -> List[Transaction]:
        """Returns all transactions involving a given agent."""
        indices = self._agent_index.get(agent_id, [])
        return [self._transactions[i] for i in indices]

    def get_total_flow(self, agent_id: str, currency: CurrencyType) -> float:
        """Returns the net flow for an agent in a given currency.
        
        Positive = net gain (received more than sent).
        Negative = net loss (sent more than received).
        """
        if isinstance(currency, str):
            currency = CurrencyType(currency)

        total = 0.0
        for tx in self.get_for_agent(agent_id):
            if tx.currency == currency:
                if tx.to_id == agent_id:
                    total += tx.amount
                if tx.from_id == agent_id:
                    total -= tx.amount
        return total

    @property
    def transactions(self) -> List[Transaction]:
        """Return the list of recorded transactions."""
        return list(self._transactions)

    def to_dict(self) -> dict:
        """Returns a serializable representation of the transaction log."""
        return {
            "transactions": [tx.to_dict() for tx in self._transactions],
        }

    def __len__(self) -> int:
        return len(self._transactions)

    def __repr__(self) -> str:
        return f"TransactionLog(count={len(self._transactions)})"
