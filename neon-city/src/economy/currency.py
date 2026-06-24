"""Currency and Wallet module for the Neon City Simulation Engine."""

from __future__ import annotations

import uuid
from enum import Enum
from typing import Dict, Optional


class CurrencyType(Enum):
    """Types of currency available in the Neon City economy."""
    CREDITS = "credits"
    DATA = "data"
    CORP_SHARES = "corp_shares"
    BLACK_MARKET = "black_market"


class Wallet:
    """A wallet that holds balances in multiple currency types."""

    def __init__(self, owner_id: str, balances: Optional[Dict[CurrencyType, float]] = None):
        self.owner_id: str = owner_id
        self.balances: Dict[CurrencyType, float] = {}
        if balances:
            for currency, amount in balances.items():
                if isinstance(currency, str):
                    currency = CurrencyType(currency)
                self.balances[currency] = float(amount)

    def balance(self, currency: CurrencyType) -> float:
        """Returns the balance for a given currency."""
        if isinstance(currency, str):
            currency = CurrencyType(currency)
        return self.balances.get(currency, 0.0)

    def credit(self, currency: CurrencyType, amount: float) -> None:
        """Adds funds to the wallet."""
        if isinstance(currency, str):
            currency = CurrencyType(currency)
        if amount < 0:
            raise ValueError("Credit amount must be non-negative")
        self.balances[currency] = self.balances.get(currency, 0.0) + amount

    def debit(self, currency: CurrencyType, amount: float) -> bool:
        """Subtracts funds from the wallet. Returns False if insufficient balance."""
        if isinstance(currency, str):
            currency = CurrencyType(currency)
        if amount < 0:
            raise ValueError("Debit amount must be non-negative")
        current = self.balances.get(currency, 0.0)
        if current < amount:
            return False
        self.balances[currency] = current - amount
        return True

    def transfer_to(self, other: "Wallet", currency: CurrencyType, amount: float) -> bool:
        """Atomic transfer of funds to another wallet. Returns success."""
        if isinstance(currency, str):
            currency = CurrencyType(currency)
        if amount < 0:
            raise ValueError("Transfer amount must be non-negative")
        current = self.balances.get(currency, 0.0)
        if current < amount:
            return False
        self.balances[currency] = current - amount
        other.balances[currency] = other.balances.get(currency, 0.0) + amount
        return True

    def to_dict(self) -> dict:
        """Returns a serializable dict representation."""
        return {
            "owner_id": self.owner_id,
            "balances": {currency.value: amount for currency, amount in self.balances.items()},
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Wallet":
        """Creates a Wallet from a serialized dict."""
        balances = {}
        for key, value in data.get("balances", {}).items():
            balances[CurrencyType(key)] = float(value)
        return cls(owner_id=data["owner_id"], balances=balances)

    def __repr__(self) -> str:
        bal_str = ", ".join(f"{k.value}: {v:.2f}" for k, v in self.balances.items())
        return f"Wallet(owner_id={self.owner_id!r}, balances={{{bal_str}}})"
