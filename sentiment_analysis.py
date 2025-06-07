from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import re

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