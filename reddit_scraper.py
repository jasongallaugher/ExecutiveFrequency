"""
Reddit scraper for finding CEO/founder engineering problems.

Uses PRAW (Python Reddit API Wrapper) to search relevant subreddits.
"""

import praw
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os


class RedditScraper:
    """Scraper for Reddit using PRAW."""

    # Subreddits where CEOs/founders discuss engineering
    TARGET_SUBREDDITS = [
        "startups",
        "entrepreneur",
        "SaaS",
        "Entrepreneur",
        "smallbusiness",
        "programming",
        "cscareerquestions",
        "ExperiencedDevs",
        "webdev",
        "devops",
    ]

    def __init__(self, days: int = 7, client_id: Optional[str] = None,
                 client_secret: Optional[str] = None, user_agent: Optional[str] = None):
        """
        Initialize Reddit scraper.

        Args:
            days: Number of days to look back
            client_id: Reddit API client ID (or set REDDIT_CLIENT_ID env var)
            client_secret: Reddit API client secret (or set REDDIT_CLIENT_SECRET env var)
            user_agent: User agent string (or set REDDIT_USER_AGENT env var)
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
            "need technical leader",
            "eng manager",
        ]

        # Get credentials from args or environment
        self.client_id = client_id or os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("REDDIT_CLIENT_SECRET")
        self.user_agent = user_agent or os.getenv("REDDIT_USER_AGENT", "ExecutiveFrequency/0.1.0")

        self.reddit = None
        if self.client_id and self.client_secret:
            try:
                self.reddit = praw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent=self.user_agent,
                )
            except Exception as e:
                print(f"Warning: Could not initialize Reddit client: {e}")
                print("Reddit scraping will be skipped. Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET env vars.")

    def _is_recent(self, timestamp: float) -> bool:
        """Check if a post is within the lookback period."""
        post_date = datetime.fromtimestamp(timestamp)
        cutoff = datetime.now() - timedelta(days=self.days)
        return post_date >= cutoff

    def search_subreddit(self, subreddit_name: str, keyword: str) -> List[Dict]:
        """
        Search a subreddit for posts matching a keyword.

        Args:
            subreddit_name: Name of subreddit
            keyword: Search term

        Returns:
            List of matching posts
        """
        if not self.reddit:
            return []

        results = []

        try:
            subreddit = self.reddit.subreddit(subreddit_name)

            # Search posts
            for submission in subreddit.search(keyword, time_filter="week", limit=100):
                if self._is_recent(submission.created_utc):
                    results.append({
                        "type": "post",
                        "title": submission.title,
                        "text": submission.selftext,
                        "url": submission.url if not submission.is_self else "",
                        "reddit_url": f"https://reddit.com{submission.permalink}",
                        "author": str(submission.author) if submission.author else "[deleted]",
                        "author_flair": submission.author_flair_text or "",
                        "subreddit": subreddit_name,
                        "created_at": datetime.fromtimestamp(submission.created_utc),
                        "score": submission.score,
                        "num_comments": submission.num_comments,
                    })

        except Exception as e:
            print(f"Error searching r/{subreddit_name} for '{keyword}': {e}")

        return results

    def scrape(self) -> List[Dict]:
        """
        Scrape Reddit for all configured keywords and subreddits.

        Returns:
            List of all matching posts with metadata
        """
        if not self.reddit:
            print("Reddit scraping skipped (no credentials)")
            return []

        all_posts = []
        seen_urls = set()

        print(f"Scraping Reddit (last {self.days} days)...")

        for subreddit in self.TARGET_SUBREDDITS:
            for keyword in self.search_keywords:
                print(f"  Searching r/{subreddit} for: {keyword}")
                posts = self.search_subreddit(subreddit, keyword)

                # Deduplicate by Reddit URL
                for post in posts:
                    reddit_url = post.get("reddit_url", "")
                    if reddit_url and reddit_url not in seen_urls:
                        seen_urls.add(reddit_url)

                        # Standardize date field
                        post["date"] = post["created_at"]

                        # Add source
                        post["source"] = "Reddit"

                        all_posts.append(post)

        print(f"  Found {len(all_posts)} unique Reddit posts")
        return all_posts
