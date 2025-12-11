# news_agent.py
import feedparser
from datetime import datetime
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd

analyzer = SentimentIntensityAnalyzer()

class NewsAgent:
    def __init__(self, ticker: str):
        self.ticker = ticker

    def fetch_news(self, start_date: str, end_date: str):
        """
        Fetch news from multiple free RSS sources and combine them.
        """
        print(f"Fetching news for {self.ticker} from {start_date} to {end_date}")

        start_ts = pd.Timestamp(start_date)
        end_ts = pd.Timestamp(end_date)

        articles = []

        # --- 1️ Google News RSS ---
        google_rss = f"https://news.google.com/rss/search?q={self.ticker}+stock&hl=en-US&gl=US&ceid=US:en"
        articles.extend(self._parse_rss(google_rss, start_ts, end_ts))

        # --- 2️ Yahoo Finance RSS ---
        yahoo_rss = f"https://finance.yahoo.com/rss/headline?s={self.ticker}"
        articles.extend(self._parse_rss(yahoo_rss, start_ts, end_ts))

        # --- 3️ Bing News RSS ---
        bing_rss = f"https://www.bing.com/news/search?q={self.ticker}+stock&format=rss"
        articles.extend(self._parse_rss(bing_rss, start_ts, end_ts))

        # --- 4️ Seeking Alpha RSS ---
        seeking_alpha_rss = f"https://seekingalpha.com/api/sa/combined/{self.ticker}.xml"
        articles.extend(self._parse_rss(seeking_alpha_rss, start_ts, end_ts))

        # Remove duplicate titles
        unique_articles = {a["title"]: a for a in articles}.values()
        return list(unique_articles)

    def summarize_sentiment(self, articles):
        """Summarize sentiment score into numeric rating and text summary."""
        if len(articles) == 0:
            return {"news_count": 0, "avg_sentiment": 0, "summary": "No news available"}

        avg_sent = sum(a["sentiment"] for a in articles) / len(articles)

        if avg_sent > 0.4:
            summary = "Strongly Bullish"
        elif avg_sent > 0.1:
            summary = "Bullish"
        elif avg_sent > -0.1:
            summary = "Neutral"
        elif avg_sent > -0.4:
            summary = "Bearish"
        else:
            summary = "Strongly Bearish"

        return {
            "news_count": len(articles),
            "avg_sentiment": avg_sent,
            "summary": summary
        }

    # ------------------ Helper Methods ------------------
    def _parse_rss(self, rss_url, start_ts, end_ts):
        """Parse RSS feed and return articles with sentiment."""
        feed = feedparser.parse(rss_url)
        articles = []
        for entry in feed.entries:
            published_dt = None
            if hasattr(entry, "published_parsed"):
                published_dt = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, "updated_parsed"):
                published_dt = datetime(*entry.updated_parsed[:6])
            if not published_dt:
                continue
            if not (start_ts <= published_dt <= end_ts):
                continue

            score = analyzer.polarity_scores(entry.title)["compound"]
            sentiment = score
            articles.append({
                "title": entry.title,
                "link": entry.link,
                "published": published_dt.strftime("%Y-%m-%d"),
                "sentiment": sentiment
            })
        return articles
