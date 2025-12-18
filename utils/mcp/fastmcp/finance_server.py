"""finance_server.py

FastMCP server providing financial data tools using yfinance library.
Provides stock quotes, company info, and investment calculations.
"""
from fastmcp import FastMCP

mcp = FastMCP("Finance")


@mcp.tool()
def get_stock_quote(symbol: str) -> str:
    """
    Get current stock quote for a given ticker symbol using yfinance.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, GOOGL, MSFT, NVDA)
        
    Returns:
        Current stock price and basic quote information
    """
    import yfinance as yf
    
    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info
        
        # Get key quote data
        price = info.get("regularMarketPrice") or info.get("currentPrice", "N/A")
        prev_close = info.get("previousClose", "N/A")
        currency = info.get("currency", "USD")
        name = info.get("shortName") or info.get("longName", symbol)
        market_cap = info.get("marketCap", 0)
        volume = info.get("volume", 0)
        day_high = info.get("dayHigh", "N/A")
        day_low = info.get("dayLow", "N/A")
        
        # Calculate change
        if price != "N/A" and prev_close != "N/A" and prev_close > 0:
            change = price - prev_close
            change_pct = (change / prev_close) * 100
            change_str = f"{'+' if change >= 0 else ''}{change:.2f} ({'+' if change_pct >= 0 else ''}{change_pct:.2f}%)"
        else:
            change_str = "N/A"
        
        # Format market cap
        if market_cap >= 1e12:
            market_cap_str = f"${market_cap/1e12:.2f}T"
        elif market_cap >= 1e9:
            market_cap_str = f"${market_cap/1e9:.2f}B"
        elif market_cap >= 1e6:
            market_cap_str = f"${market_cap/1e6:.2f}M"
        else:
            market_cap_str = f"${market_cap:,.0f}"
        
        return (
            f"Stock: {name} ({symbol.upper()})\n"
            f"Price: {price} {currency}\n"
            f"Change: {change_str}\n"
            f"Previous Close: {prev_close} {currency}\n"
            f"Day Range: {day_low} - {day_high}\n"
            f"Volume: {volume:,}\n"
            f"Market Cap: {market_cap_str}"
        )
    except Exception as e:
        return f"Error fetching stock quote for {symbol}: {e}"


@mcp.tool()
def get_company_info(symbol: str) -> str:
    """
    Get detailed company information for a stock ticker using yfinance.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, GOOGL)
        
    Returns:
        Company name, sector, industry, description, and key metrics
    """
    import yfinance as yf
    
    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info
        
        name = info.get("shortName") or info.get("longName", symbol)
        sector = info.get("sector", "N/A")
        industry = info.get("industry", "N/A")
        country = info.get("country", "N/A")
        employees = info.get("fullTimeEmployees", "N/A")
        website = info.get("website", "N/A")
        summary = info.get("longBusinessSummary", "No description available.")
        
        # Financial metrics
        pe_ratio = info.get("trailingPE", "N/A")
        eps = info.get("trailingEps", "N/A")
        dividend_yield = info.get("dividendYield", 0)
        if dividend_yield and dividend_yield != "N/A":
            dividend_yield = f"{dividend_yield * 100:.2f}%"
        else:
            dividend_yield = "N/A"
        
        # Truncate summary if too long
        if len(summary) > 300:
            summary = summary[:300] + "..."
        
        return (
            f"Company: {name} ({symbol.upper()})\n"
            f"Sector: {sector}\n"
            f"Industry: {industry}\n"
            f"Country: {country}\n"
            f"Employees: {employees:,}\n" if isinstance(employees, int) else f"Employees: {employees}\n"
            f"Website: {website}\n"
            f"\nKey Metrics:\n"
            f"  P/E Ratio: {pe_ratio}\n"
            f"  EPS: {eps}\n"
            f"  Dividend Yield: {dividend_yield}\n"
            f"\nDescription:\n{summary}"
        )
    except Exception as e:
        return f"Error fetching company info for {symbol}: {e}"


@mcp.tool()
def get_stock_history(symbol: str, period: str = "1mo") -> str:
    """
    Get historical stock price data using yfinance.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)
        period: Time period - 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        
    Returns:
        Historical price summary with high, low, and average
    """
    import yfinance as yf
    
    valid_periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
    if period not in valid_periods:
        return f"Invalid period. Choose from: {', '.join(valid_periods)}"
    
    try:
        ticker = yf.Ticker(symbol.upper())
        hist = ticker.history(period=period)
        
        if hist.empty:
            return f"No historical data found for {symbol}"
        
        # Calculate statistics
        start_price = hist['Close'].iloc[0]
        end_price = hist['Close'].iloc[-1]
        high_price = hist['High'].max()
        low_price = hist['Low'].min()
        avg_price = hist['Close'].mean()
        total_volume = hist['Volume'].sum()
        
        change = end_price - start_price
        change_pct = (change / start_price) * 100
        
        return (
            f"Historical Data: {symbol.upper()} ({period})\n"
            f"Period: {hist.index[0].strftime('%Y-%m-%d')} to {hist.index[-1].strftime('%Y-%m-%d')}\n"
            f"Data Points: {len(hist)}\n"
            f"\nPrice Summary:\n"
            f"  Start: ${start_price:.2f}\n"
            f"  End: ${end_price:.2f}\n"
            f"  Change: {'+' if change >= 0 else ''}{change:.2f} ({'+' if change_pct >= 0 else ''}{change_pct:.2f}%)\n"
            f"  High: ${high_price:.2f}\n"
            f"  Low: ${low_price:.2f}\n"
            f"  Average: ${avg_price:.2f}\n"
            f"  Total Volume: {total_volume:,}"
        )
    except Exception as e:
        return f"Error fetching history for {symbol}: {e}"


@mcp.tool()
def calculate_investment_return(
    principal: float,
    annual_rate: float,
    years: int,
    compound_frequency: int = 12
) -> str:
    """
    Calculate compound interest investment return.
    
    Args:
        principal: Initial investment amount
        annual_rate: Annual interest rate as percentage (e.g., 7.5 for 7.5%)
        years: Investment period in years
        compound_frequency: Times interest compounds per year (default 12 for monthly)
        
    Returns:
        Final amount and total return
    """
    rate = annual_rate / 100
    n = compound_frequency
    t = years
    
    # Compound interest formula: A = P(1 + r/n)^(nt)
    final_amount = principal * (1 + rate / n) ** (n * t)
    total_return = final_amount - principal
    return_pct = (total_return / principal) * 100
    
    return (
        f"Investment Calculator\n"
        f"---------------------\n"
        f"Principal: ${principal:,.2f}\n"
        f"Annual Rate: {annual_rate}%\n"
        f"Period: {years} years\n"
        f"Compounding: {compound_frequency}x/year\n"
        f"---------------------\n"
        f"Final Amount: ${final_amount:,.2f}\n"
        f"Total Return: ${total_return:,.2f} ({return_pct:.1f}%)"
    )


if __name__ == "__main__":
    mcp.run(transport="streamable-http", port=8001)
