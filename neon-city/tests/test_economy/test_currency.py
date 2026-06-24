"""Tests for currency module."""

import pytest

from src.economy.currency import Wallet, CurrencyType


class TestWalletCreation:
    """Test wallet creation."""

    def test_wallet_creation(self):
        wallet = Wallet(owner_id="agent_001")
        assert wallet.owner_id == "agent_001"
        assert wallet.balances == {}

    def test_wallet_with_initial_balance(self):
        wallet = Wallet(
            owner_id="agent_002",
            balances={CurrencyType.CREDITS: 500.0}
        )
        assert wallet.balance(CurrencyType.CREDITS) == 500.0

    def test_wallet_with_string_balance(self):
        wallet = Wallet(
            owner_id="agent_003",
            balances={"credits": 1000.0}
        )
        assert wallet.balance(CurrencyType.CREDITS) == 1000.0

    def test_wallet_multiple_currencies(self):
        wallet = Wallet(
            owner_id="agent_004",
            balances={
                CurrencyType.CREDITS: 100.0,
                CurrencyType.DATA: 50.0,
            }
        )
        assert wallet.balance(CurrencyType.CREDITS) == 100.0
        assert wallet.balance(CurrencyType.DATA) == 50.0


class TestCreditDebit:
    """Test credit/debit operations."""

    def test_credit(self, wallet):
        wallet.credit(CurrencyType.CREDITS, 500.0)
        assert wallet.balance(CurrencyType.CREDITS) == 1500.0  # Started with 1000

    def test_credit_new_currency(self, wallet):
        wallet.credit(CurrencyType.DATA, 100.0)
        assert wallet.balance(CurrencyType.DATA) == 100.0

    def test_credit_negative_raises(self, wallet):
        with pytest.raises(ValueError):
            wallet.credit(CurrencyType.CREDITS, -10.0)

    def test_debit_success(self, wallet):
        result = wallet.debit(CurrencyType.CREDITS, 500.0)
        assert result is True
        assert wallet.balance(CurrencyType.CREDITS) == 500.0

    def test_debit_insufficient_funds(self, wallet):
        result = wallet.debit(CurrencyType.CREDITS, 2000.0)
        assert result is False
        assert wallet.balance(CurrencyType.CREDITS) == 1000.0

    def test_debit_negative_raises(self, wallet):
        with pytest.raises(ValueError):
            wallet.debit(CurrencyType.CREDITS, -10.0)

    def test_debit_exact_amount(self, wallet):
        result = wallet.debit(CurrencyType.CREDITS, 1000.0)
        assert result is True
        assert wallet.balance(CurrencyType.CREDITS) == 0.0

    def test_debit_zero(self, wallet):
        result = wallet.debit(CurrencyType.CREDITS, 0.0)
        assert result is True
        assert wallet.balance(CurrencyType.CREDITS) == 1000.0


class TestTransfer:
    """Test transfer operations."""

    def test_transfer_success(self, wallet):
        other = Wallet(owner_id="other_agent")
        result = wallet.transfer_to(other, CurrencyType.CREDITS, 300.0)
        assert result is True
        assert wallet.balance(CurrencyType.CREDITS) == 700.0
        assert other.balance(CurrencyType.CREDITS) == 300.0

    def test_transfer_insufficient_funds(self, wallet):
        other = Wallet(owner_id="other_agent")
        result = wallet.transfer_to(other, CurrencyType.CREDITS, 2000.0)
        assert result is False
        assert wallet.balance(CurrencyType.CREDITS) == 1000.0
        assert other.balance(CurrencyType.CREDITS) == 0.0

    def test_transfer_negative_raises(self, wallet):
        other = Wallet(owner_id="other_agent")
        with pytest.raises(ValueError):
            wallet.transfer_to(other, CurrencyType.CREDITS, -10.0)

    def test_transfer_zero(self, wallet):
        other = Wallet(owner_id="other_agent")
        result = wallet.transfer_to(other, CurrencyType.CREDITS, 0.0)
        assert result is True
        assert wallet.balance(CurrencyType.CREDITS) == 1000.0
        assert other.balance(CurrencyType.CREDITS) == 0.0

    def test_transfer_different_currency(self, wallet):
        other = Wallet(owner_id="other_agent")
        wallet.credit(CurrencyType.DATA, 100.0)
        result = wallet.transfer_to(other, CurrencyType.DATA, 50.0)
        assert result is True
        assert wallet.balance(CurrencyType.DATA) == 50.0
        assert other.balance(CurrencyType.DATA) == 50.0


class TestSerialization:
    """Test serialization round-trip."""

    def test_wallet_to_dict(self, wallet):
        d = wallet.to_dict()
        assert d["owner_id"] == "test_wallet"
        assert "credits" in d["balances"]
        assert d["balances"]["credits"] == 1000.0

    def test_wallet_from_dict(self):
        d = {
            "owner_id": "agent_005",
            "balances": {"credits": 500.0, "data": 25.0},
        }
        wallet = Wallet.from_dict(d)
        assert wallet.owner_id == "agent_005"
        assert wallet.balance(CurrencyType.CREDITS) == 500.0
        assert wallet.balance(CurrencyType.DATA) == 25.0

    def test_wallet_round_trip(self, wallet):
        d = wallet.to_dict()
        restored = Wallet.from_dict(d)
        assert restored.owner_id == wallet.owner_id
        assert restored.balance(CurrencyType.CREDITS) == 1000.0

    def test_wallet_round_trip_multiple_currencies(self):
        w = Wallet(
            owner_id="multi",
            balances={
                CurrencyType.CREDITS: 100.0,
                CurrencyType.DATA: 50.0,
                CurrencyType.CORP_SHARES: 200.0,
            },
        )
        d = w.to_dict()
        restored = Wallet.from_dict(d)
        assert restored.balance(CurrencyType.CREDITS) == 100.0
        assert restored.balance(CurrencyType.DATA) == 50.0
        assert restored.balance(CurrencyType.CORP_SHARES) == 200.0

    def test_balance_with_string_currency(self, wallet):
        # Test that string currency values work
        assert wallet.balance("credits") == 1000.0
