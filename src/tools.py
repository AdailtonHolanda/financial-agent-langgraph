import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional
from langchain.tools import tool

@tool
def retrieve_realtime_stock_price(ticker: str) -> str:
    """Retrieve current real-time stock price for a ticker symbol."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        current_price = info.get('currentPrice') or info.get('regularMarketPrice')
        market_cap = info.get('marketCap')
        day_high = info.get('dayHigh')
        day_low = info.get('dayLow')
        volume = info.get('volume')
        
        result = f"Real-time stock data for {ticker}:\n"
        result += f"Current Price: ${current_price:.2f}\n"
        if market_cap:
            result += f"Market Cap: ${market_cap:,.0f}\n"
        if day_high and day_low:
            result += f"Day Range: ${day_low:.2f} - ${day_high:.2f}\n"
        if volume:
            result += f"Volume: {volume:,}\n"
        
        return result
    except Exception as e:
        return f"Error retrieving real-time stock price for {ticker}: {str(e)}"


@tool
def retrieve_historical_stock_price(
    ticker: str, 
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None,
    period: Optional[str] = None
) -> str:
    """Retrieve historical stock prices. Use period ('1mo', '3mo', '1y') or start_date/end_date."""
    try:
        stock = yf.Ticker(ticker)
        
        if period:
            hist = stock.history(period=period)
        elif start_date:
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            hist = stock.history(start=start_date, end=end_date)
        else:
            hist = stock.history(period='3mo')
        
        if hist.empty:
            return f"No historical data found for {ticker}"
        
        result = f"Historical stock data for {ticker}:\n"
        result += f"Period: {hist.index[0].strftime('%Y-%m-%d')} to {hist.index[-1].strftime('%Y-%m-%d')}\n\n"
        
        result += f"Opening Price: ${hist['Open'].iloc[0]:.2f}\n"
        result += f"Closing Price: ${hist['Close'].iloc[-1]:.2f}\n"
        result += f"Highest Price: ${hist['High'].max():.2f}\n"
        result += f"Lowest Price: ${hist['Low'].min():.2f}\n"
        result += f"Average Price: ${hist['Close'].mean():.2f}\n"
        
        price_change = hist['Close'].iloc[-1] - hist['Open'].iloc[0]
        price_change_pct = (price_change / hist['Open'].iloc[0]) * 100
        result += f"Price Change: ${price_change:.2f} ({price_change_pct:+.2f}%)\n"
        
        result += f"\nTotal Volume: {hist['Volume'].sum():,}\n"
        result += f"Average Daily Volume: {hist['Volume'].mean():,.0f}\n"
        
        return result
    except Exception as e:
        return f"Error retrieving historical stock price for {ticker}: {str(e)}"
