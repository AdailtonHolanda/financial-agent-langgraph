from unittest.mock import MagicMock, patch

import pandas as pd

from src.tools import retrieve_historical_stock_price, retrieve_realtime_stock_price


def test_realtime_stock_price_formats_market_data():
    ticker = MagicMock()
    ticker.info = {
        "currentPrice": 123.45,
        "marketCap": 1_000_000,
        "dayHigh": 125.0,
        "dayLow": 120.0,
        "volume": 42_000,
    }

    with patch("src.tools.yf.Ticker", return_value=ticker):
        result = retrieve_realtime_stock_price.invoke({"ticker": "amzn"})

    assert "AMZN" in result
    assert "Current Price: $123.45" in result
    assert "Market Cap: $1,000,000" in result


def test_realtime_stock_price_handles_missing_price():
    ticker = MagicMock()
    ticker.info = {}

    with patch("src.tools.yf.Ticker", return_value=ticker):
        result = retrieve_realtime_stock_price.invoke({"ticker": "AMZN"})

    assert result == "No current price data found for AMZN."


def test_historical_stock_price_uses_default_period_and_formats_summary():
    ticker = MagicMock()
    ticker.history.return_value = pd.DataFrame(
        {
            "Open": [100.0, 102.0],
            "Close": [101.0, 110.0],
            "High": [103.0, 112.0],
            "Low": [99.0, 101.0],
            "Volume": [1_000, 2_000],
        },
        index=pd.to_datetime(["2026-01-02", "2026-01-03"]),
    )

    with patch("src.tools.yf.Ticker", return_value=ticker):
        result = retrieve_historical_stock_price.invoke({"ticker": "amzn"})

    ticker.history.assert_called_once_with(period="3mo")
    assert "Historical stock data for AMZN" in result
    assert "Closing Price: $110.00" in result
    assert "Price Change: $10.00 (+10.00%)" in result
