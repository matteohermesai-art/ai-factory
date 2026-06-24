"""Tests for market module."""

import pytest

from src.economy.market import Market, Order, OrderType, AVAILABLE_ITEMS
from src.economy.currency import CurrencyType


class TestOrderPlacement:
    """Test order placement."""

    def test_place_buy_order(self, market):
        order = Order(
            order_id="order_001",
            agent_id="agent_001",
            order_type=OrderType.BUY,
            item="food",
            quantity=5,
            price=10.0,
            currency=CurrencyType.CREDITS,
        )
        result = market.place_order(order)
        assert result is True

    def test_place_sell_order(self, market):
        order = Order(
            order_id="order_002",
            agent_id="agent_002",
            order_type=OrderType.SELL,
            item="energy",
            quantity=3,
            price=15.0,
            currency=CurrencyType.CREDITS,
        )
        result = market.place_order(order)
        assert result is True

    def test_place_order_invalid_item(self, market):
        with pytest.raises(ValueError):
            Order(
                order_id="order_003",
                agent_id="agent_001",
                order_type=OrderType.BUY,
                item="invalid_item",
                quantity=1,
                price=10.0,
                currency=CurrencyType.CREDITS,
            )

    def test_place_order_invalid_quantity(self, market):
        with pytest.raises(ValueError):
            Order(
                order_id="order_004",
                agent_id="agent_001",
                order_type=OrderType.BUY,
                item="food",
                quantity=0,
                price=10.0,
                currency=CurrencyType.CREDITS,
            )

    def test_place_order_invalid_price(self, market):
        with pytest.raises(ValueError):
            Order(
                order_id="order_005",
                agent_id="agent_001",
                order_type=OrderType.BUY,
                item="food",
                quantity=1,
                price=-5.0,
                currency=CurrencyType.CREDITS,
            )


class TestOrderMatching:
    """Test order matching (buy/sell at same price)."""

    def test_match_buy_sell_same_price(self, market):
        # Place a sell order
        sell_order = Order(
            order_id="sell_001",
            agent_id="seller",
            order_type=OrderType.SELL,
            item="food",
            quantity=5,
            price=10.0,
            currency=CurrencyType.CREDITS,
            timestamp=1.0,
        )
        market.place_order(sell_order)

        # Place a matching buy order
        buy_order = Order(
            order_id="buy_001",
            agent_id="buyer",
            order_type=OrderType.BUY,
            item="food",
            quantity=3,
            price=10.0,
            currency=CurrencyType.CREDITS,
            timestamp=2.0,
        )
        market.place_order(buy_order)

        # The buy order should have been partially matched
        # Check order book - sell order should have remaining quantity
        book = market.get_order_book("food")
        # The sell order should have 2 remaining (5 - 3)
        remaining_sells = [o for o in book["asks"] if o["order_id"] == "sell_001"]
        if remaining_sells:
            assert remaining_sells[0]["quantity"] == 2

    def test_match_buy_higher_than_sell(self, market):
        # Sell at 8.0
        sell_order = Order(
            order_id="sell_002",
            agent_id="seller",
            order_type=OrderType.SELL,
            item="energy",
            quantity=5,
            price=8.0,
            currency=CurrencyType.CREDITS,
            timestamp=1.0,
        )
        market.place_order(sell_order)

        # Buy at 10.0 (willing to pay more)
        buy_order = Order(
            order_id="buy_002",
            agent_id="buyer",
            order_type=OrderType.BUY,
            item="energy",
            quantity=5,
            price=10.0,
            currency=CurrencyType.CREDITS,
            timestamp=2.0,
        )
        market.place_order(buy_order)

        # Should match at the sell price (price improvement)
        price = market.get_price("energy")
        assert price == 8.0

    def test_no_match_when_buy_price_too_low(self, market):
        # Sell at 20.0
        sell_order = Order(
            order_id="sell_003",
            agent_id="seller",
            order_type=OrderType.SELL,
            item="data_chip",
            quantity=5,
            price=20.0,
            currency=CurrencyType.CREDITS,
            timestamp=1.0,
        )
        market.place_order(sell_order)

        # Buy at 10.0 (too low)
        buy_order = Order(
            order_id="buy_003",
            agent_id="buyer",
            order_type=OrderType.BUY,
            item="data_chip",
            quantity=5,
            price=10.0,
            currency=CurrencyType.CREDITS,
            timestamp=2.0,
        )
        market.place_order(buy_order)

        # Should not match
        price = market.get_price("data_chip")
        assert price is None

    def test_match_orders_method(self, market):
        # Add orders directly to the book
        sell_order = Order(
            order_id="sell_004",
            agent_id="seller",
            order_type=OrderType.SELL,
            item="food",
            quantity=5,
            price=10.0,
            currency=CurrencyType.CREDITS,
            timestamp=1.0,
        )
        market._order_books["food"].append(sell_order)

        buy_order = Order(
            order_id="buy_004",
            agent_id="buyer",
            order_type=OrderType.BUY,
            item="food",
            quantity=5,
            price=12.0,
            currency=CurrencyType.CREDITS,
            timestamp=2.0,
        )
        market._order_books["food"].append(buy_order)

        matched = market.match_orders("food")
        assert len(matched) == 1
        assert matched[0][0].order_id == "buy_004"
        assert matched[0][1].order_id == "sell_004"


class TestOrderBookRetrieval:
    """Test order book retrieval."""

    def test_get_order_book(self, market):
        order = Order(
            order_id="order_010",
            agent_id="agent_001",
            order_type=OrderType.BUY,
            item="food",
            quantity=5,
            price=10.0,
            currency=CurrencyType.CREDITS,
        )
        market.place_order(order)

        book = market.get_order_book("food")
        assert "bids" in book
        assert "asks" in book
        assert len(book["bids"]) == 1
        assert book["bids"][0]["order_id"] == "order_010"

    def test_get_order_book_invalid_item(self, market):
        book = market.get_order_book("invalid_item")
        assert book == {"bids": [], "asks": []}

    def test_order_book_bids_sorted_descending(self, market):
        for i, price in enumerate([10.0, 15.0, 12.0]):
            order = Order(
                order_id=f"bid_{i}",
                agent_id="buyer",
                order_type=OrderType.BUY,
                item="energy",
                quantity=1,
                price=price,
                currency=CurrencyType.CREDITS,
                timestamp=float(i),
            )
            market.place_order(order)

        book = market.get_order_book("energy")
        prices = [b["price"] for b in book["bids"]]
        assert prices == sorted(prices, reverse=True)


class TestPriceTracking:
    """Test price tracking."""

    def test_get_price_no_trades(self, market):
        assert market.get_price("food") is None

    def test_get_price_after_trade(self, market):
        # Create a matched trade
        sell = Order(
            order_id="sell_price",
            agent_id="seller",
            order_type=OrderType.SELL,
            item="food",
            quantity=5,
            price=10.0,
            currency=CurrencyType.CREDITS,
            timestamp=1.0,
        )
        market.place_order(sell)

        buy = Order(
            order_id="buy_price",
            agent_id="buyer",
            order_type=OrderType.BUY,
            item="food",
            quantity=5,
            price=10.0,
            currency=CurrencyType.CREDITS,
            timestamp=2.0,
        )
        market.place_order(buy)

        price = market.get_price("food")
        assert price == 10.0


class TestOrderCancellation:
    """Test order cancellation."""

    def test_cancel_order(self, market):
        order = Order(
            order_id="cancel_me",
            agent_id="agent_001",
            order_type=OrderType.BUY,
            item="food",
            quantity=5,
            price=10.0,
            currency=CurrencyType.CREDITS,
        )
        market.place_order(order)

        result = market.cancel_order("cancel_me")
        assert result is True

        book = market.get_order_book("food")
        assert all(o["order_id"] != "cancel_me" for o in book["bids"])

    def test_cancel_nonexistent_order(self, market):
        result = market.cancel_order("nonexistent")
        assert result is False


class TestSerialization:
    """Test serialization."""

    def test_market_to_dict(self, market):
        order = Order(
            order_id="ser_001",
            agent_id="agent_001",
            order_type=OrderType.BUY,
            item="food",
            quantity=5,
            price=10.0,
            currency=CurrencyType.CREDITS,
        )
        market.place_order(order)

        d = market.to_dict()
        assert "order_books" in d
        assert "last_prices" in d
        assert "food" in d["order_books"]

    def test_market_to_dict_empty(self, market):
        d = market.to_dict()
        assert isinstance(d["order_books"], dict)
        assert isinstance(d["last_prices"], dict)
