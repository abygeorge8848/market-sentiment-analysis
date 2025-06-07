from data_scraper import get_stock_price_info, get_stock_data, get_alternative_news
from sentiment_analysis import analyze_sentiment_enhanced


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