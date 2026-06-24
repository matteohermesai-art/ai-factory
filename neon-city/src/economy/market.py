"""Market module for the Neon City Simulation Engine."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

from .currency import CurrencyType


# Available items in the market
AVAILABLE_ITEMS = {"food", "energy", "data_chip", "weapon", "shield", "cred_chip"}


class OrderType(Enum):
    """Whether the order is a buy or sell."""
    BUY = "buy"
    SELL = "sell"


@dataclass
class Order:
    """Represents a buy or sell order on the market."""
    order_id: str
    agent_id: str
    order_type: OrderType
    item: str
    quantity: int
    price: float
    currency: CurrencyType
    timestamp: float = 0.0

    def __post_init__(self):
        if self.item not in AVAILABLE_ITEMS:
            raise ValueError(f"Unknown item: {self.item}. Available: {AVAILABLE_ITEMS}")
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.price < 0:
            raise ValueError("Price must be non-negative")
        if isinstance(self.order_type, str):
            self.order_type = OrderType(self.order_type)
        if isinstance(self.currency, str):
            self.currency = CurrencyType(self.currency)

    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "agent_id": self.agent_id,
            "order_type": self.order_type.value,
            "item": self.item,
            "quantity": self.quantity,
            "price": self.price,
            "currency": self.currency.value,
            "timestamp": self.timestamp,
        }


class Market:
    """Order-book based market for trading items."""

    def __init__(self):
        # item -> list of orders
        self._order_books: Dict[str, List[Order]] = {item: [] for item in AVAILABLE_ITEMS}
        # order_id -> (item, index) for fast lookup
        self._order_index: Dict[str, Tuple[str, int]] = {}
        # last traded price per item
        self._last_price: Dict[str, float] = {}

    def place_order(self, order: Order) -> bool:
        """Places an order and attempts to match it. Returns True if order was placed."""
        if order.item not in AVAILABLE_ITEMS:
            return False

        # Try to match first
        self._match_single(order)

        # If the order still has remaining quantity, add to book
        if order.quantity > 0:
            idx = len(self._order_books[order.item])
            self._order_books[order.item].append(order)
            self._order_index[order.order_id] = (order.item, idx)

        return True

    def _match_single(self, incoming: Order) -> List[Tuple[Order, Order]]:
        """Matches a single incoming order against the book. Returns matched pairs."""
        matched: List[Tuple[Order, Order]] = []
        book = self._order_books[incoming.item]

        if incoming.order_type == OrderType.BUY:
            # Match against SELL orders (asks): sell price <= buy price
            # Sort asks by price ascending, then time ascending
            asks = [o for o in book if o.order_type == OrderType.SELL and o.price <= incoming.price]
            asks.sort(key=lambda o: (o.price, o.timestamp))

            remaining_qty = incoming.quantity
            for ask in asks:
                if remaining_qty <= 0:
                    break
                if ask.quantity <= 0:
                    continue

                trade_qty = min(remaining_qty, ask.quantity)
                trade_price = ask.price  # price improvement: use ask price

                remaining_qty -= trade_qty
                ask.quantity -= trade_qty
                incoming.quantity -= trade_qty

                self._last_price[incoming.item] = trade_price
                matched.append((incoming, ask))

                # Update index for the ask
                if ask.quantity == 0:
                    self._remove_order_from_index(ask.order_id)

            # Clean up fully filled asks
            self._order_books[incoming.item] = [
                o for o in self._order_books[incoming.item] if o.quantity > 0
            ]
            self._rebuild_index(incoming.item)

        else:  # SELL
            # Match against BUY orders (bids): buy price >= sell price
            bids = [o for o in book if o.order_type == OrderType.BUY and o.price >= incoming.price]
            bids.sort(key=lambda o: (-o.price, o.timestamp))

            remaining_qty = incoming.quantity
            for bid in bids:
                if remaining_qty <= 0:
                    break
                if bid.quantity <= 0:
                    continue

                trade_qty = min(remaining_qty, bid.quantity)
                trade_price = bid.price  # price improvement: use bid price

                remaining_qty -= trade_qty
                bid.quantity -= trade_qty
                incoming.quantity -= trade_qty

                self._last_price[incoming.item] = trade_price
                matched.append((bid, incoming))

                if bid.quantity == 0:
                    self._remove_order_from_index(bid.order_id)

            # Clean up fully filled bids
            self._order_books[incoming.item] = [
                o for o in self._order_books[incoming.item] if o.quantity > 0
            ]
            self._rebuild_index(incoming.item)

        return matched

    def match_orders(self, item: str) -> List[Tuple[Order, Order]]:
        """Matches all possible buy/sell orders for an item (price-time priority)."""
        if item not in AVAILABLE_ITEMS:
            return []

        book = self._order_books[item]
        bids = sorted(
            [o for o in book if o.order_type == OrderType.BUY and o.quantity > 0],
            key=lambda o: (-o.price, o.timestamp),
        )
        asks = sorted(
            [o for o in book if o.order_type == OrderType.SELL and o.quantity > 0],
            key=lambda o: (o.price, o.timestamp),
        )

        matched: List[Tuple[Order, Order]] = []
        bid_idx = 0
        ask_idx = 0

        while bid_idx < len(bids) and ask_idx < len(asks):
            bid = bids[bid_idx]
            ask = asks[ask_idx]

            if bid.price < ask.price:
                break

            trade_qty = min(bid.quantity, ask.quantity)
            trade_price = (bid.price + ask.price) / 2.0

            bid.quantity -= trade_qty
            ask.quantity -= trade_qty

            self._last_price[item] = trade_price
            matched.append((bid, ask))

            if bid.quantity == 0:
                bid_idx += 1
            if ask.quantity == 0:
                ask_idx += 1

        # Clean up fully filled orders
        self._order_books[item] = [o for o in self._order_books[item] if o.quantity > 0]
        self._rebuild_index(item)

        return matched

    def get_order_book(self, item: str) -> dict:
        """Returns the order book for an item with bids and asks."""
        if item not in AVAILABLE_ITEMS:
            return {"bids": [], "asks": []}

        book = self._order_books[item]
        bids = [
            {"order_id": o.order_id, "agent_id": o.agent_id, "quantity": o.quantity, "price": o.price, "currency": o.currency.value}
            for o in book if o.order_type == OrderType.BUY and o.quantity > 0
        ]
        asks = [
            {"order_id": o.order_id, "agent_id": o.agent_id, "quantity": o.quantity, "price": o.price, "currency": o.currency.value}
            for o in book if o.order_type == OrderType.SELL and o.quantity > 0
        ]

        # Sort bids by price descending, asks by price ascending
        bids.sort(key=lambda x: (-x["price"], x.get("timestamp", 0)))
        asks.sort(key=lambda x: (x["price"], x.get("timestamp", 0)))

        return {"bids": bids, "asks": asks}

    def get_price(self, item: str) -> Optional[float]:
        """Returns the last traded price for an item, or None if no trades."""
        return self._last_price.get(item)

    def cancel_order(self, order_id: str) -> bool:
        """Cancels an order by ID. Returns True if found and cancelled."""
        if order_id not in self._order_index:
            return False

        item, _ = self._order_index[order_id]
        book = self._order_books[item]
        new_book = [o for o in book if o.order_id != order_id]

        if len(new_book) == len(book):
            return False

        self._order_books[item] = new_book
        del self._order_index[order_id]
        self._rebuild_index(item)
        return True

    def to_dict(self) -> dict:
        """Returns a serializable state of the market."""
        order_books = {}
        for item, orders in self._order_books.items():
            order_books[item] = [o.to_dict() for o in orders if o.quantity > 0]

        return {
            "order_books": order_books,
            "last_prices": {k: v for k, v in self._last_price.items()},
        }

    def _remove_order_from_index(self, order_id: str) -> None:
        """Removes an order from the index."""
        if order_id in self._order_index:
            del self._order_index[order_id]

    def _rebuild_index(self, item: str) -> None:
        """Rebuilds the order index for an item."""
        # Remove old entries for this item
        to_remove = [oid for oid, (it, _) in self._order_index.items() if it == item]
        for oid in to_remove:
            del self._order_index[oid]

        # Rebuild
        for idx, order in enumerate(self._order_books[item]):
            self._order_index[order.order_id] = (item, idx)
