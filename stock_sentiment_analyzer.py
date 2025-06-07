import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import requests
from datetime import datetime
import time
import re

def clean_text_for_sentiment(text):
    """
    Clean and prepare text for sentiment analysis.
    
    Args:
        text (str): Raw text to clean
    
    Returns:
        str: Cleaned text ready for sentiment analysis
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove URLs (but keep the text around them)
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Keep punctuation as it's important for VADER
    return text.strip()

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

def test_vader_sentiment():
    """Test VADER with known examples to ensure it's working."""
    analyzer = SentimentIntensityAnalyzer()
    
    test_cases = [
        "This stock is performing amazingly well! Great results!",
        "Terrible earnings report. Stock price crashed badly.",
        "The company reported quarterly results.",
        "BREAKING: Stock soars 20% on excellent earnings beat!",
        "WARNING: Major losses reported, investors fleeing"
    ]
    
    print("🧪 Testing VADER Sentiment Analysis:")
    for text in test_cases:
        scores = analyzer.polarity_scores(text)
        print(f"   Text: {text}")
        print(f"   Scores: {scores}")
        print()

def analyze_sentiment_enhanced(news_articles):
    """
    Enhanced sentiment analysis with multiple text sources and debugging.
    """
    if not news_articles:
        print("❌ No news articles to analyze")
        return [], {'compound': 0, 'pos': 0, 'neu': 0, 'neg': 0}
    
    # Test VADER first
    test_vader_sentiment()
    
    analyzer = SentimentIntensityAnalyzer()
    sentiments = []
    
    print(f"🔬 Analyzing sentiment for {len(news_articles)} articles...")
    
    for i, article in enumerate(news_articles):
        try:
            # Extract content from the nested structure
            content = article.get('content', article)  # Handle both nested and direct structures
            
            # Get title
            title = content.get('title', '')
            
            # Get description and summary
            description = content.get('description', '')
            summary = content.get('summary', '')
            
            # Build text for analysis
            text_parts = []
            
            if title:
                cleaned_title = clean_text_for_sentiment(title)
                if cleaned_title:
                    text_parts.append(cleaned_title)
            
            if description and description != title:
                cleaned_desc = clean_text_for_sentiment(description)
                if cleaned_desc:
                    text_parts.append(cleaned_desc)
            
            if summary and summary != title and summary != description:
                cleaned_summary = clean_text_for_sentiment(summary)
                if cleaned_summary:
                    text_parts.append(cleaned_summary)
            
            # Combine all text parts
            combined_text = '. '.join(text_parts)
            
            if not combined_text:
                print(f"   ⚠️  Article {i+1}: No analyzable text found")
                print(f"      Raw title: {title[:50]}...")
                print(f"      Raw description: {description[:50]}...")
                print(f"      Raw summary: {summary[:50]}...")
                continue
            
            # Analyze sentiment
            sentiment = analyzer.polarity_scores(combined_text)
            
            # Get publisher information
            provider = content.get('provider', {})
            publisher = provider.get('displayName', 'Unknown') if isinstance(provider, dict) else str(provider)
            
            # Get link
            canonical_url = content.get('canonicalUrl', {})
            link = canonical_url.get('url', 'No link available') if isinstance(canonical_url, dict) else str(canonical_url)
            
            # Get publish date
            pub_date = content.get('pubDate', content.get('displayTime', 'Unknown'))
            
            sentiments.append({
                'title': title[:100] + "..." if len(title) > 100 else title,
                'full_text': combined_text,
                'publisher': publisher,
                'link': link,
                'sentiment': sentiment,
                'publish_time': pub_date,
                'text_length': len(combined_text)
            })
            
            # Debug output
            print(f"   📝 Article {i+1}:")
            print(f"      Title: {title[:60]}...")
            print(f"      Combined Text ({len(combined_text)} chars): {combined_text[:80]}...")
            print(f"      Sentiment: Compound={sentiment['compound']:.3f}, Pos={sentiment['pos']:.3f}, Neg={sentiment['neg']:.3f}")
            print(f"      Publisher: {publisher}")
            print()
            
        except Exception as e:
            print(f"   ❌ Error processing article {i+1}: {e}")
            print(f"      Article structure: {type(article)}")
            if isinstance(article, dict):
                print(f"      Available keys: {list(article.keys())}")
            continue
    
    if not sentiments:
        print("❌ No articles could be processed for sentiment analysis")
        return [], {'compound': 0, 'pos': 0, 'neu': 0, 'neg': 0}
    
    # Calculate overall sentiment
    sentiment_scores = [s['sentiment'] for s in sentiments]
    overall_sentiment = pd.DataFrame(sentiment_scores).mean().to_dict()
    
    print(f"✅ Successfully analyzed {len(sentiments)} articles")
    return sentiments, overall_sentiment

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

def display_results(stock, news, sentiments, overall_sentiment):
    """Enhanced results display with better debugging information."""
    
    # Display stock information
    stock_data = get_stock_price_info(stock)
    
    print("\n" + "="*70)
    print(f"📊 STOCK ANALYSIS: {stock_data['name']}")
    print("="*70)
    print(f"Symbol: {stock_data['symbol']}")
    
    if stock_data['current_price']:
        print(f"Current Price: ₹{stock_data['current_price']:.2f}")
        if stock_data['previous_close']:
            change = stock_data['current_price'] - stock_data['previous_close']
            change_pct = (change / stock_data['previous_close']) * 100
            change_indicator = "📈" if change > 0 else "📉" if change < 0 else "➡️"
            print(f"Change: {change:+.2f} ({change_pct:+.2f}%) {change_indicator}")
    else:
        print("Current Price: Not available")
    
    if stock_data['day_high'] and stock_data['day_low']:
        print(f"Day Range: ₹{stock_data['day_low']:.2f} - ₹{stock_data['day_high']:.2f}")
    
    if stock_data['market_cap']:
        market_cap_cr = stock_data['market_cap'] / 10000000  # Convert to crores
        print(f"Market Cap: ₹{market_cap_cr:,.0f} Cr")
    
    print(f"Sector: {stock_data['sector']}")
    print(f"Industry: {stock_data['industry']}")
    
    # Display news and sentiment analysis
    print("\n" + "="*70)
    print("📰 NEWS SENTIMENT ANALYSIS")
    print("="*70)
    
    if not news:
        print("❌ No recent news articles found for this stock.")
        print("\n💡 This could mean:")
        print("   • The stock ticker is not widely covered")
        print("   • Yahoo Finance has limited news for this stock") 
        print("   • Network connectivity issues")
    elif not sentiments:
        print("❌ Could not analyze sentiment for available news.")
        print(f"   Found {len(news)} articles but couldn't process them.")
    else:
        print(f"📊 Analyzed {len(sentiments)} recent news articles:\n")
        
        for i, sentiment_data in enumerate(sentiments, 1):
            compound = sentiment_data['sentiment']['compound']
            
            # More granular sentiment classification
            if compound >= 0.5:
                emoji = "🚀"
                sentiment_label = "Very Positive"
            elif compound >= 0.1:
                emoji = "😊"
                sentiment_label = "Positive"
            elif compound > -0.1:
                emoji = "😐"
                sentiment_label = "Neutral"
            elif compound > -0.5:
                emoji = "😟"
                sentiment_label = "Negative"
            else:
                emoji = "💥"
                sentiment_label = "Very Negative"
            
            print(f"{i}. {sentiment_data['title']}")
            print(f"   📰 Publisher: {sentiment_data['publisher']}")
            print(f"   📝 Analysis Text Length: {sentiment_data['text_length']} characters")
            print(f"   🎯 Sentiment: {sentiment_label} {emoji} (Score: {compound:.3f})")
            print(f"   📊 Breakdown: Pos: {sentiment_data['sentiment']['pos']:.2f} | "
                  f"Neu: {sentiment_data['sentiment']['neu']:.2f} | "
                  f"Neg: {sentiment_data['sentiment']['neg']:.2f}")
            print(f"   🔗 Link: {sentiment_data['link']}")
            print()
    
    # Display overall sentiment with enhanced interpretation
    print("="*70)
    print("🎯 OVERALL NEWS SENTIMENT SUMMARY")
    print("="*70)
    
    compound_score = overall_sentiment.get('compound', 0)
    print(f"📊 Overall Compound Score: {compound_score:.4f}")
    print(f"📈 Positive: {overall_sentiment.get('pos', 0):.3f} | "
          f"😐 Neutral: {overall_sentiment.get('neu', 0):.3f} | "
          f"📉 Negative: {overall_sentiment.get('neg', 0):.3f}")
    
    # Enhanced sentiment interpretation
    if compound_score >= 0.5:
        print("\n🚀 OVERALL SENTIMENT: VERY POSITIVE")
        print("   News coverage is highly favorable - strong bullish signals!")
    elif compound_score >= 0.1:
        print("\n📈 OVERALL SENTIMENT: POSITIVE")
        print("   News coverage appears generally favorable.")
    elif compound_score > -0.1:
        print("\n😐 OVERALL SENTIMENT: NEUTRAL")
        print("   News coverage appears balanced or limited.")
    elif compound_score > -0.5:
        print("\n😟 OVERALL SENTIMENT: NEGATIVE")
        print("   News coverage appears somewhat concerning.")
    else:
        print("\n💥 OVERALL SENTIMENT: VERY NEGATIVE")
        print("   News coverage is highly unfavorable - strong bearish signals!")
    
    # Additional insights
    if len(sentiments) > 0:
        pos_articles = sum(1 for s in sentiments if s['sentiment']['compound'] > 0.1)
        neg_articles = sum(1 for s in sentiments if s['sentiment']['compound'] < -0.1)
        neu_articles = len(sentiments) - pos_articles - neg_articles
        
        print(f"\n📈 Article Breakdown:")
        print(f"   Positive Articles: {pos_articles}/{len(sentiments)}")
        print(f"   Neutral Articles: {neu_articles}/{len(sentiments)}")
        print(f"   Negative Articles: {neg_articles}/{len(sentiments)}")
    
    print("\n" + "="*70)
    print("⚠️  DISCLAIMER")
    print("="*70)
    print("🔔 This analysis is based on news headlines and summaries only.")
    print("🔔 Sentiment analysis has limitations and may not capture context perfectly.")
    print("🔔 This should NOT be used as the sole basis for investment decisions.")
    print("🔔 Always do your own research and consult financial advisors.")
    print("="*70)

def main():
    """Enhanced main function with better user guidance."""
    print("🇮🇳 ENHANCED Indian Stock Sentiment Analyzer")
    print("=" * 50)
    print("💡 This tool analyzes recent news sentiment for Indian stocks")
    print("🔍 Supports NSE (.NS) and BSE (.BO) listed stocks")
    print("=" * 50)
    
    # Get ticker from user with examples
    print("\n📝 Popular Indian Stock Tickers:")
    print("   • RELIANCE.NS (Reliance Industries)")
    print("   • TCS.NS (Tata Consultancy Services)")  
    print("   • HDFCBANK.NS (HDFC Bank)")
    print("   • INFY.NS (Infosys)")
    print("   • ITC.NS (ITC Limited)")
    
    ticker = input("\n🎯 Enter Indian stock ticker: ").strip().upper()
    
    # Add .NS suffix if not present
    if not ticker.endswith('.NS') and not ticker.endswith('.BO'):
        ticker += '.NS'
        print(f"   Added .NS suffix: {ticker}")
    
    print(f"\n🔍 Analyzing {ticker}...")
    print("⏳ This may take 10-15 seconds...")
    
    try:
        # Get stock data and news
        stock, news = get_stock_data(ticker)
        
        if stock is None:
            print(f"❌ Could not fetch data for ticker '{ticker}'")
            print("💡 Please check:")
            print("   • Ticker symbol spelling")
            print("   • Internet connection")
            print("   • Try with .BO suffix for BSE stocks")
            return
        
        # If no news from yfinance, try alternative sources
        if not news:
            print("🔄 Trying alternative news sources...")
            news = get_alternative_news(ticker)
        
        # Analyze sentiment
        print("🧠 Performing advanced sentiment analysis...")
        sentiments, overall_sentiment = analyze_sentiment_enhanced(news)
        
        # Display comprehensive results
        display_results(stock, news, sentiments, overall_sentiment)
        
    except KeyboardInterrupt:
        print("\n\n👋 Analysis interrupted by user.")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        print("💡 Please try:")
        print("   • Check your internet connection")
        print("   • Verify the ticker symbol")
        print("   • Try again in a few minutes")

if __name__ == "__main__":
    main()