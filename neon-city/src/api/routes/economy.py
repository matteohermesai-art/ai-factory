"""Economy management routes."""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException

from src.api.schemas import (
    EconomyStats,
    ErrorResponse,
)

router = APIRouter(prefix="/api/v1/economy", tags=["economy"])

# In-memory economy state
_wallets: dict[str, dict] = {}
_market_prices: dict[str, float] = {
    "food": 10.0,
    "energy": 5.0,
    "data_chip": 50.0,
    "weapon": 200.0,
    "shield": 150.0,
    "cred_chip": 100.0,
}
_order_book: dict[str, list[dict]] = {
    item: [] for item in _market_prices
}
_transaction_count: int = 0


@router.get("/wallets")
async def get_wallets() -> dict:
    """Get a summary of all wallets."""
    return {
        "wallets": {
            agent_id: balances for agent_id, balances in _wallets.items()
        },
        "total_agents": len(_wallets),
    }


@router.get("/wallets/{agent_id}")
async def get_wallet(agent_id: str) -> dict:
    """Get the wallet for a specific agent."""
    wallet = _wallets.get(agent_id)
    if wallet is None:
        raise HTTPException(status_code=404, detail=f"Wallet for agent {agent_id} not found")
    return {"agent_id": agent_id, "balances": wallet}


@router.get("/market")
async def get_market() -> dict:
    """Get the full order books for all items."""
    return {
        "order_books": {
            item: {"bids": [], "asks": []} for item in _order_book
        },
        "last_prices": _market_prices,
    }


@router.get("/market/{item}")
async def get_market_item(item: str) -> dict:
    """Get the order book for a specific item."""
    if item not in _order_book:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown item: {item}. Available: {list(_order_book.keys())}",
        )
    return {
        "item": item,
        "bids": [o for o in _order_book[item] if o.get("order_type") == "buy"],
        "asks": [o for o in _order_book[item] if o.get("order_type") == "sell"],
        "last_price": _market_prices.get(item),
    }


class _OrderRequest:
    """Internal placeholder — real implementation uses body model below."""
    pass


@router.post("/market/order")
async def place_order(body: dict) -> dict:
    """Place a market order.

    Expected body fields: agent_id, order_type (buy/sell), item, quantity, price, currency.
    """
    global _transaction_count
    agent_id = body.get("agent_id")
    order_type = body.get("order_type")
    item = body.get("item")
    quantity = body.get("quantity", 1)
    price = body.get("price", 0.0)
    currency = body.get("currency", "credits")

    if item not in _order_book:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown item: {item}. Available: {list(_order_book.keys())}",
        )
    if order_type not in ("buy", "sell"):
        raise HTTPException(status_code=400, detail="order_type must be 'buy' or 'sell'")

    order_id = str(uuid.uuid4())
    order = {
        "order_id": order_id,
        "agent_id": agent_id,
        "order_type": order_type,
        "item": item,
        "quantity": quantity,
        "price": price,
        "currency": currency,
    }
    _order_book[item].append(order)
    _transaction_count += 1

    return {"order_id": order_id, "status": "placed", "order": order}


@router.get("/transactions")
async def get_transactions(limit: int = 100) -> dict:
    """Get transaction history."""
    return {
        "transaction_count": _transaction_count,
        "transactions": [],
        "limit": limit,
    }


@router.get("/stats", response_model=EconomyStats)
async def get_economy_stats() -> EconomyStats:
    """Get aggregate economy statistics."""
    wallets_total: dict[str, float] = {}
    for agent_id, balances in _wallets.items():
        for currency, amount in balances.items():
            wallets_total[currency] = wallets_total.get(currency, 0.0) + amount

    return EconomyStats(
        wallets_total=wallets_total,
        market_prices=_market_prices,
        transaction_count=_transaction_count,
    )
