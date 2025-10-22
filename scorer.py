"""
Scoring engine for evaluating posts based on executive pain signals.

Scoring criteria (0-100):
- +30 CEO/founder flair or identity
- +25 urgency indicators (timeline/money mentions)
- +20 transition keywords (hiring, replacing, need to)
- +15 velocity/shipping issues
- +10 per additional pain keyword
"""

import re
from typing import Dict


class PostScorer:
    """Score posts based on executive engineering pain signals."""

    # CEO/Founder indicators (+30 points)
    CEO_FOUNDER_KEYWORDS = [
        r'\bCEO\b',
        r'\bfounder\b',
        r'\bco-founder\b',
        r'\bCTO\b',
        r'\bchief\s+technology\s+officer\b',
        r'\bmy\s+company\b',
        r'\bour\s+startup\b',
        r'\bI\s+founded\b',
        r'\bI\s+started\b',
    ]

    # Urgency indicators (+25 points)
    URGENCY_KEYWORDS = [
        r'\basap\b',
        r'\bimmediately\b',
        r'\burgent\b',
        r'\bcritical\b',
        r'\bburnrate\b',
        r'\bburn\s+rate\b',
        r'\brunway\b',
        r'\$\d+[km]?\b',  # Money mentions
        r'\d+\s+months?\b',  # Timeline mentions
        r'\d+\s+weeks?\b',
        r'\bcrisis\b',
        r'\bemergency\b',
    ]

    # Transition keywords (+20 points)
    TRANSITION_KEYWORDS = [
        r'\bneed\s+to\s+hire\b',
        r'\bhiring\s+a\b',
        r'\blooking\s+for\b',
        r'\breplace\b',
        r'\breplacing\b',
        r'\bneed\s+a\s+CTO\b',
        r'\bneed\s+a\s+VP\b',
        r'\bneed\s+an?\s+eng',
        r'\bmust\s+hire\b',
        r'\bbringing\s+on\b',
    ]

    # Velocity/shipping issues (+15 points)
    VELOCITY_KEYWORDS = [
        r'\bcan\'t\s+ship\b',
        r'\bcannot\s+ship\b',
        r'\bslow\s+development\b',
        r'\bmissed\s+deadline\b',
        r'\bbehind\s+schedule\b',
        r'\btaking\s+too\s+long\b',
        r'\bnot\s+shipping\b',
        r'\bstuck\b',
        r'\bblocked\b',
        r'\bvelocity\b',
        r'\bthroughput\b',
    ]

    # Additional pain keywords (+10 each, max 3)
    PAIN_KEYWORDS = [
        r'\btechnical\s+debt\b',
        r'\btech\s+debt\b',
        r'\blegacy\s+code\b',
        r'\bscaling\s+issues\b',
        r'\bcan\'t\s+scale\b',
        r'\boutage\b',
        r'\bdowntime\b',
        r'\bquality\s+issues\b',
        r'\bbug',
        r'\bbroken\b',
        r'\bfailing\b',
        r'\bturnover\b',
        r'\bquitting\b',
        r'\bleaving\b',
    ]

    def __init__(self):
        """Initialize scorer with compiled regex patterns."""
        self.ceo_patterns = [re.compile(p, re.IGNORECASE) for p in self.CEO_FOUNDER_KEYWORDS]
        self.urgency_patterns = [re.compile(p, re.IGNORECASE) for p in self.URGENCY_KEYWORDS]
        self.transition_patterns = [re.compile(p, re.IGNORECASE) for p in self.TRANSITION_KEYWORDS]
        self.velocity_patterns = [re.compile(p, re.IGNORECASE) for p in self.VELOCITY_KEYWORDS]
        self.pain_patterns = [re.compile(p, re.IGNORECASE) for p in self.PAIN_KEYWORDS]

    def _check_patterns(self, text: str, patterns: list) -> bool:
        """Check if any pattern matches in text."""
        return any(pattern.search(text) for pattern in patterns)

    def _count_pain_keywords(self, text: str) -> int:
        """Count unique pain keywords (max 3 for scoring)."""
        count = sum(1 for pattern in self.pain_patterns if pattern.search(text))
        return min(count, 3)

    def score_post(self, post: Dict) -> Dict:
        """
        Score a post based on executive pain signals.

        Args:
            post: Post dictionary with title, text, author, etc.

        Returns:
            Post dictionary with added 'score' and 'score_breakdown' fields
        """
        # Combine all text for analysis
        title = post.get("title", "")
        text = post.get("text", "")
        author = post.get("author", "")
        author_flair = post.get("author_flair", "")

        combined_text = f"{title} {text}"
        combined_author = f"{author} {author_flair}"

        score = 0
        breakdown = []

        # CEO/Founder indicators (+30)
        if self._check_patterns(combined_text, self.ceo_patterns) or \
           self._check_patterns(combined_author, self.ceo_patterns):
            score += 30
            breakdown.append("CEO/Founder (+30)")

        # Urgency indicators (+25)
        if self._check_patterns(combined_text, self.urgency_patterns):
            score += 25
            breakdown.append("Urgency (+25)")

        # Transition keywords (+20)
        if self._check_patterns(combined_text, self.transition_patterns):
            score += 20
            breakdown.append("Transition/Hiring (+20)")

        # Velocity issues (+15)
        if self._check_patterns(combined_text, self.velocity_patterns):
            score += 15
            breakdown.append("Velocity Issues (+15)")

        # Pain keywords (+10 each, max 3)
        pain_count = self._count_pain_keywords(combined_text)
        if pain_count > 0:
            pain_score = pain_count * 10
            score += pain_score
            breakdown.append(f"Pain Keywords x{pain_count} (+{pain_score})")

        post["score"] = score
        post["score_breakdown"] = ", ".join(breakdown) if breakdown else "No signals"

        return post

    def score_posts(self, posts: list) -> list:
        """
        Score a list of posts.

        Args:
            posts: List of post dictionaries

        Returns:
            List of scored posts, sorted by score (highest first)
        """
        scored = [self.score_post(post) for post in posts]
        return sorted(scored, key=lambda p: p["score"], reverse=True)
