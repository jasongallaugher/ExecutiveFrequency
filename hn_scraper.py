"""
HackerNews scraper for finding engineering problems.

Uses the Algolia HN Search API to find relevant posts and comments.
"""

import httpx
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dateutil import parser as date_parser


class HNScraper:
    """Scraper for HackerNews using Algolia API."""

    ALGOLIA_API = "https://hn.algolia.com/api/v1"

    def __init__(self, days: int = 7):
        """
        Initialize HN scraper.

        Args:
            days: Number of days to look back
        """
        self.days = days
        self.search_keywords = [
            "CTO",
            "VP Engineering",
            "engineering team",
            "technical debt",
            "can't ship",
            "slow development",
            "hiring engineers",
            "eng manager",
            "engineering manager",
            "tech lead",
        ]

    def _get_timestamp_filter(self) -> int:
        """Get Unix timestamp for filtering posts."""
        cutoff = datetime.now() - timedelta(days=self.days)
        return int(cutoff.timestamp())

    def search_posts(self, keyword: str) -> List[Dict]:
        """
        Search HN posts (stories + comments) for a keyword.

        Args:
            keyword: Search term

        Returns:
            List of matching posts
        """
        timestamp = self._get_timestamp_filter()

        results = []

        # Search stories
        try:
            with httpx.Client(timeout=30) as client:
                response = client.get(
                    f"{self.ALGOLIA_API}/search",
                    params={
                        "query": keyword,
                        "tags": "story",
                        "numericFilters": f"created_at_i>{timestamp}",
                        "hitsPerPage": 100,
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    for hit in data.get("hits", []):
                        results.append({
                            "type": "story",
                            "title": hit.get("title", ""),
                            "text": hit.get("story_text", ""),
                            "url": hit.get("url", ""),
                            "hn_url": f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}",
                            "author": hit.get("author", ""),
                            "created_at": hit.get("created_at", ""),
                            "points": hit.get("points", 0),
                            "num_comments": hit.get("num_comments", 0),
                        })
        except Exception as e:
            print(f"Error searching HN stories for '{keyword}': {e}")

        # Search comments
        try:
            with httpx.Client(timeout=30) as client:
                response = client.get(
                    f"{self.ALGOLIA_API}/search",
                    params={
                        "query": keyword,
                        "tags": "comment",
                        "numericFilters": f"created_at_i>{timestamp}",
                        "hitsPerPage": 100,
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    for hit in data.get("hits", []):
                        results.append({
                            "type": "comment",
                            "title": hit.get("story_title", "Comment"),
                            "text": hit.get("comment_text", ""),
                            "url": "",
                            "hn_url": f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}",
                            "author": hit.get("author", ""),
                            "created_at": hit.get("created_at", ""),
                            "points": hit.get("points", 0),
                            "num_comments": 0,
                        })
        except Exception as e:
            print(f"Error searching HN comments for '{keyword}': {e}")

        return results

    def scrape(self) -> List[Dict]:
        """
        Scrape HN for all configured keywords.

        Returns:
            List of all matching posts with metadata
        """
        all_posts = []
        seen_urls = set()

        print(f"Scraping HackerNews (last {self.days} days)...")

        for keyword in self.search_keywords:
            print(f"  Searching for: {keyword}")
            posts = self.search_posts(keyword)

            # Deduplicate by HN URL
            for post in posts:
                hn_url = post.get("hn_url", "")
                if hn_url and hn_url not in seen_urls:
                    seen_urls.add(hn_url)

                    # Parse date
                    try:
                        post["date"] = date_parser.parse(post["created_at"])
                    except:
                        post["date"] = datetime.now()

                    # Add source
                    post["source"] = "HackerNews"

                    all_posts.append(post)

        print(f"  Found {len(all_posts)} unique HN posts/comments")
        return all_posts
