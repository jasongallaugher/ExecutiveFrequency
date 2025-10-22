"""
Twitter/X scraper for finding CEOs seeking engineering leaders.

Searches for #startupCEO/#founder + hiring/seeking language.
Note: Requires Twitter API credentials or uses alternative methods.
"""

import httpx
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os


class TwitterScraper:
    """Scraper for Twitter/X using search."""

    def __init__(self, days: int = 7):
        """
        Initialize Twitter scraper.

        Args:
            days: Number of days to look back
        """
        self.days = days

        # Search queries combining hashtags with hiring signals
        self.search_queries = [
            "#startupCEO (need OR looking for OR recommend) (CTO OR \"VP Engineering\" OR \"VP Eng\")",
            "#founder (need OR looking for OR recommend) (CTO OR \"VP Engineering\" OR \"engineering leader\")",
            "#startupCEO (hiring OR seeking) (CTO OR \"VP Engineering\")",
            "#founder fractional CTO",
            "\"I'm a CEO\" (need OR looking for) (CTO OR \"VP Engineering\")",
            "\"startup CEO\" recommend (CTO OR \"engineering leader\")",
        ]

    def search_twitter_nitter(self, query: str) -> List[Dict]:
        """
        Search Twitter using Nitter instances (no API key needed).

        Nitter is a privacy-focused Twitter frontend that can be scraped.

        Args:
            query: Search query

        Returns:
            List of tweets
        """
        results = []

        # Try multiple Nitter instances
        nitter_instances = [
            "https://nitter.net",
            "https://nitter.1d4.us",
            "https://nitter.kavin.rocks",
        ]

        for instance in nitter_instances:
            try:
                with httpx.Client(timeout=15, follow_redirects=True) as client:
                    # Nitter search URL format
                    url = f"{instance}/search"
                    params = {
                        "f": "tweets",
                        "q": query,
                        "since": (datetime.now() - timedelta(days=self.days)).strftime("%Y-%m-%d"),
                    }

                    response = client.get(url, params=params)

                    if response.status_code == 200:
                        # Simple HTML parsing - look for tweet content
                        # This is a simplified version; real implementation would parse better
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(response.text, 'html.parser')

                        # Nitter uses .timeline-item for tweets
                        tweets = soup.find_all('div', class_='timeline-item')

                        for tweet in tweets[:20]:  # Limit to 20 per query
                            try:
                                # Extract tweet text
                                tweet_text_elem = tweet.find('div', class_='tweet-content')
                                if not tweet_text_elem:
                                    continue

                                tweet_text = tweet_text_elem.get_text(strip=True)

                                # Extract username
                                username_elem = tweet.find('a', class_='username')
                                username = username_elem.get_text(strip=True) if username_elem else "unknown"

                                # Extract tweet link
                                link_elem = tweet.find('a', class_='tweet-link')
                                tweet_url = instance + link_elem['href'] if link_elem and link_elem.get('href') else ""

                                results.append({
                                    'type': 'tweet',
                                    'title': f"Tweet from {username}",
                                    'text': tweet_text,
                                    'url': tweet_url,
                                    'twitter_url': tweet_url,
                                    'author': username,
                                    'created_at': datetime.now(),  # Nitter doesn't always show dates clearly
                                    'source_detail': 'Twitter/X',
                                })
                            except Exception as e:
                                continue

                        # If we got results, stop trying other instances
                        if results:
                            break

            except Exception as e:
                print(f"Error searching Nitter instance {instance}: {e}")
                continue

        return results

    def scrape(self) -> List[Dict]:
        """
        Scrape Twitter for CEO/founder hiring signals.

        Returns:
            List of matching tweets with metadata
        """
        all_tweets = []
        seen_urls = set()

        print(f"Scraping Twitter/X (last {self.days} days)...")
        print("Note: Twitter scraping uses Nitter (may be limited)")

        for query in self.search_queries:
            print(f"  Searching for: {query[:60]}...")
            tweets = self.search_twitter_nitter(query)

            # Deduplicate by URL
            for tweet in tweets:
                tweet_url = tweet.get("twitter_url", "")
                if tweet_url and tweet_url not in seen_urls:
                    seen_urls.add(tweet_url)

                    # Standardize date field
                    tweet["date"] = tweet.get("created_at", datetime.now())

                    # Add source
                    tweet["source"] = "Twitter"

                    all_tweets.append(tweet)

        print(f"  Found {len(all_tweets)} unique tweets")
        return all_tweets
