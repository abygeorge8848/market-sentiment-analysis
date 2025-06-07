import yfinance as yf

def get_stock_data(ticker):
    """
    Fetches news and basic stock information for a given Indian stock ticker.
    """
    try:
        stock = yf.Ticker(ticker)
        
        # Try to get basic info first to verify ticker exists
        info = stock.info
        if not info or len(info) < 5:  # Very basic check
            print(f"⚠️  Warning: Limited information available for {ticker}")
        
        # Get news with error handling
        try:
            news = stock.news
            print(f"📰 Found {len(news) if news else 0} news articles")
            
            # Debug: Print first news article structure
            if news and len(news) > 0:
                print("🔍 Debug: First article structure:")
                first_article = news[0]
                content = first_article.get('content', first_article)
                print(f"   Article keys: {list(first_article.keys())}")
                if 'content' in first_article:
                    print(f"   Content keys: {list(content.keys())}")
                    print(f"   Title: {content.get('title', 'N/A')[:100]}...")
                    print(f"   Description: {content.get('description', 'N/A')[:100]}...")
                    print(f"   Summary: {content.get('summary', 'N/A')[:100]}...")
                print()
                        
        except Exception as e:
            print(f"❌ Could not fetch news: {e}")
            news = []
            
        return stock, news
        
    except Exception as e:
        print(f"❌ Error fetching stock data: {e}")
        return None, []
    
def get_alternative_news(ticker_symbol):
    """
    Try to get news from alternative sources if yfinance fails.
    This is a fallback method.
    """
    try:
        # Remove .NS or .BO suffix for search
        clean_symbol = ticker_symbol.replace('.NS', '').replace('.BO', '')
        
        # You could integrate with other news APIs here
        # For now, we'll return empty list as fallback
        print(f"🔄 Attempting alternative news sources for {clean_symbol}...")
        return []
        
    except Exception as e:
        print(f"❌ Alternative news fetch failed: {e}")
        return []

def get_stock_price_info(stock):
    """Get current stock price and basic information with enhanced error handling."""
    try:
        info = stock.info
        hist = stock.history(period="2d")  # Get 2 days to ensure we have data
        
        stock_data = {
            'name': info.get('longName', info.get('shortName', 'Unknown Company')),
            'symbol': info.get('symbol', 'Unknown'),
            'current_price': info.get('regularMarketPrice') or info.get('currentPrice'),
            'currency': info.get('currency', 'INR'),
            'market_cap': info.get('marketCap'),
            'sector': info.get('sector', 'Unknown'),
            'industry': info.get('industry', 'Unknown'),
            'previous_close': info.get('previousClose'),
            'day_high': info.get('dayHigh'),
            'day_low': info.get('dayLow'),
            'volume': info.get('volume')
        }
        
        # If current price not available, try from history
        if not stock_data['current_price'] and not hist.empty:
            stock_data['current_price'] = hist['Close'].iloc[-1]
            
        return stock_data
        
    except Exception as e:
        print(f"⚠️  Error getting stock price info: {e}")
        return {'name': 'Unknown', 'symbol': 'Unknown', 'current_price': None}