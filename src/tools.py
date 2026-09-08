from datetime import datetime
from typing import Optional

import yfinance as yf
from langchain.tools import tool


def _normalize_ticker(ticker: str) -> str:
    normalized = (ticker or "").strip().upper()
    if not normalized:
        raise ValueError("Ticker cannot be empty.")
    return normalized


@tool
def retrieve_realtime_stock_price(ticker: str) -> str:
    """Retrieve current market data for a ticker symbol."""
    try:
        ticker = _normalize_ticker(ticker)
        stock = yf.Ticker(ticker)
        info = stock.info

        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        if current_price is None:
            return f"No current price data found for {ticker}."

        market_cap = info.get("marketCap")
        day_high = info.get("dayHigh")
        day_low = info.get("dayLow")
        volume = info.get("volume")

        result = f"Real-time stock data for {ticker}:\n"
        result += f"Current Price: ${current_price:.2f}\n"
        if market_cap:
            result += f"Market Cap: ${market_cap:,.0f}\n"
        if day_high is not None and day_low is not None:
            result += f"Day Range: ${day_low:.2f} - ${day_high:.2f}\n"
        if volume:
            result += f"Volume: {volume:,}\n"

        return result
    except Exception as exc:
        return f"Error retrieving real-time stock price for {ticker}: {exc}"


@tool
def retrieve_historical_stock_price(
    ticker: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    period: Optional[str] = None,
) -> str:
    """Retrieve historical stock prices using a period or explicit date range."""
    try:
        ticker = _normalize_ticker(ticker)
        stock = yf.Ticker(ticker)

        if period:
            hist = stock.history(period=period)
        elif start_date:
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            hist = stock.history(start=start_date, end=end_date)
        else:
            hist = stock.history(period="3mo")

        if hist.empty:
            return f"No historical data found for {ticker}."

        opening_price = hist["Open"].iloc[0]
        closing_price = hist["Close"].iloc[-1]

        result = f"Historical stock data for {ticker}:\n"
        result += (
            f"Period: {hist.index[0].strftime('%Y-%m-%d')} "
            f"to {hist.index[-1].strftime('%Y-%m-%d')}\n\n"
        )
        result += f"Opening Price: ${opening_price:.2f}\n"
        result += f"Closing Price: ${closing_price:.2f}\n"
        result += f"Highest Price: ${hist['High'].max():.2f}\n"
        result += f"Lowest Price: ${hist['Low'].min():.2f}\n"
        result += f"Average Price: ${hist['Close'].mean():.2f}\n"

        if opening_price != 0:
            price_change = closing_price - opening_price
            price_change_pct = (price_change / opening_price) * 100
            result += f"Price Change: ${price_change:.2f} ({price_change_pct:+.2f}%)\n"

        result += f"\nTotal Volume: {hist['Volume'].sum():,}\n"
        result += f"Average Daily Volume: {hist['Volume'].mean():,.0f}\n"

        return result
    except Exception as exc:
        return f"Error retrieving historical stock price for {ticker}: {exc}"
