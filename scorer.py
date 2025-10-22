"""
Scoring engine for evaluating posts based on executive pain signals.

NEW REFINED SCORING (focused on CEO/founder pain only):
- REQUIRED: Must be identifiable CEO/founder (no score without this)
- +40 points: Clear CEO/founder identity (first-person)
- +30 points: Visceral pain/anxiety/frustration
- +20 points: Cultural or velocity problems
- +10 points: Specific engineering pain (debt, quality, team issues)

Only scores posts from CEOs/founders expressing genuine pain.
"""

import re
from typing import Dict, Optional


class PostScorer:
    """Score posts based on executive engineering pain signals."""

    # Strong CEO/Founder identity - first person only (+40 points)
    # Must include "I" or "my" or "our" to prove it's the actual CEO posting
    STRONG_CEO_IDENTITY = [
        r'\bI\'m\s+(?:the\s+)?(?:CEO|founder|co-founder|CTO)\b',
        r'\bI\s+am\s+(?:the\s+)?(?:CEO|founder|co-founder|CTO)\b',
        r'\bas\s+(?:the\s+)?(?:CEO|founder|co-founder)\b',
        r'\bI\s+founded\b',
        r'\bI\s+started\s+(?:this|the|my)\s+company\b',
        r'\bmy\s+startup\b',
        r'\bour\s+startup\b.*\bI\b',  # "our startup" + "I" nearby
        r'\bmy\s+company\b.*\bI\b',   # "my company" + "I" nearby
    ]

    # Weaker CEO identity signals (still valid but lower confidence)
    WEAK_CEO_IDENTITY = [
        r'\bfounder\b.*\bI\b',
        r'\bCEO\b.*\bI\b',
        r'\bI\b.*\bmy\s+company\b',
    ]

    # Visceral pain and anxiety - emotional language (+30 points)
    VISCERAL_PAIN = [
        r'\bfrustrat(?:ed|ing)\b',
        r'\bworried\b',
        r'\banxious\b',
        r'\bstressed\b',
        r'\bkeeps\s+me\s+(?:up|awake)\b',
        r'\bcan\'t\s+sleep\b',
        r'\blosing\s+sleep\b',
        r'\bpanick?(?:ed|ing)\b',
        r'\bdesperate\b',
        r'\bafraid\b',
        r'\bscared\b',
        r'\bterrified\b',
        r'\bat\s+my\s+wits?\s+end\b',
        r'\bdon\'t\s+know\s+what\s+to\s+do\b',
        r'\bpulling\s+my\s+hair\s+out\b',
        r'\bgoing\s+crazy\b',
        r'\bdriving\s+me\s+crazy\b',
        r'\bhate\s+(?:this|it)\b',
        r'\bwant\s+to\s+quit\b',
        r'\bready\s+to\s+give\s+up\b',
    ]

    # Cultural and velocity problems (+20 points)
    CULTURE_VELOCITY_ISSUES = [
        r'\bvelocity\s+(?:is\s+)?(?:terrible|awful|slow|dropping|decreased)\b',
        r'\bcan\'t\s+ship\b',
        r'\bcannot\s+ship\b',
        r'\bnot\s+shipping\b',
        r'\bslow\s+(?:to\s+)?ship\b',
        r'\bmissed?\s+(?:every\s+)?deadline',
        r'\bbehind\s+schedule\b',
        r'\bculture\s+(?:is\s+)?(?:toxic|broken|terrible|bad)\b',
        r'\bteam\s+(?:is\s+)?(?:dysfunctional|broken|not\s+working)\b',
        r'\bno\s+one\s+(?:cares|wants\s+to\s+work)\b',
        r'\bpeople\s+are\s+(?:leaving|quitting)\b',
        r'\bexodus\b',
        r'\bmass\s+resignation\b',
        r'\beveryone\'s?\s+(?:leaving|quitting)\b',
        r'\bmorale\s+is\s+(?:low|terrible|awful)\b',
    ]

    # Specific engineering pain (+10 points)
    ENGINEERING_PAIN = [
        r'\btechnical\s+debt\s+(?:is\s+)?(?:killing|crushing|overwhelming)\b',
        r'\btech\s+debt\s+(?:out\s+of\s+control|massive|huge)\b',
        r'\blegacy\s+(?:codebase|system)\s+(?:is\s+)?(?:unmaintainable|a\s+nightmare)\b',
        r'\bcan\'t\s+(?:scale|grow)\b',
        r'\bscaling\s+(?:problems|issues|crisis)\b',
        r'\bconstant\s+(?:outages|fires|incidents)\b',
        r'\bproduction\s+(?:is\s+)?(?:on\s+fire|constantly\s+breaking|unstable)\b',
        r'\bquality\s+(?:is\s+)?(?:terrible|awful|suffering)\b',
        r'\b(?:critical\s+)?bugs?\s+(?:everywhere|constantly)\b',
        r'\bturnover\s+(?:is\s+)?(?:high|terrible|killing\s+us)\b',
        r'\bcan\'t\s+(?:hire|find|retain)\s+(?:good\s+)?(?:engineers?|developers?)\b',
        r'\barchitecture\s+(?:is\s+)?(?:a\s+mess|terrible|broken)\b',
    ]

    def __init__(self):
        """Initialize scorer with compiled regex patterns."""
        self.strong_ceo_patterns = [re.compile(p, re.IGNORECASE) for p in self.STRONG_CEO_IDENTITY]
        self.weak_ceo_patterns = [re.compile(p, re.IGNORECASE) for p in self.WEAK_CEO_IDENTITY]
        self.visceral_pain_patterns = [re.compile(p, re.IGNORECASE) for p in self.VISCERAL_PAIN]
        self.culture_velocity_patterns = [re.compile(p, re.IGNORECASE) for p in self.CULTURE_VELOCITY_ISSUES]
        self.engineering_pain_patterns = [re.compile(p, re.IGNORECASE) for p in self.ENGINEERING_PAIN]

    def _check_patterns(self, text: str, patterns: list) -> bool:
        """Check if any pattern matches in text."""
        return any(pattern.search(text) for pattern in patterns)

    def _find_pattern_match(self, text: str, patterns: list) -> Optional[str]:
        """Find first matching pattern and return the surrounding context."""
        for pattern in patterns:
            match = pattern.search(text)
            if match:
                # Get context around the match (50 chars before and after)
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 100)

                # Extract and clean up the context
                context = text[start:end].strip()
                # Clean up whitespace
                context = " ".join(context.split())

                # Add ellipsis if we truncated
                if start > 0:
                    context = "..." + context
                if end < len(text):
                    context = context + "..."

                return context
        return None

    def score_post(self, post: Dict) -> Dict:
        """
        Score a post based on executive pain signals.

        NEW LOGIC: Only scores posts from identifiable CEOs/founders expressing pain.

        Args:
            post: Post dictionary with title, text, author, etc.

        Returns:
            Post dictionary with added 'score', 'score_breakdown', and 'evidence' fields
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
        evidence_quotes = []

        # STEP 1: Check for CEO/Founder identity (REQUIRED)
        # Try strong patterns first
        ceo_match = self._find_pattern_match(combined_text, self.strong_ceo_patterns)
        ceo_strength = None

        if ceo_match:
            score += 40
            breakdown.append("CEO/Founder Identity (+40)")
            evidence_quotes.append(f"Identity: \"{ceo_match}\"")
            ceo_strength = "strong"
        else:
            # Try weak patterns
            ceo_match = self._find_pattern_match(combined_text, self.weak_ceo_patterns) or \
                        self._find_pattern_match(combined_author, self.weak_ceo_patterns)
            if ceo_match:
                score += 25
                breakdown.append("CEO/Founder Identity (weak) (+25)")
                evidence_quotes.append(f"Identity: \"{ceo_match}\"")
                ceo_strength = "weak"

        # If no CEO identity found, return score of 0
        if not ceo_strength:
            post["score"] = 0
            post["score_breakdown"] = "Not a CEO/founder post"
            post["evidence"] = "No CEO/founder identity detected"
            return post

        # STEP 2: Check for visceral pain/anxiety (+30)
        pain_match = self._find_pattern_match(combined_text, self.visceral_pain_patterns)
        if pain_match:
            score += 30
            breakdown.append("Visceral Pain/Anxiety (+30)")
            evidence_quotes.append(f"Pain: \"{pain_match}\"")

        # STEP 3: Check for culture/velocity issues (+20)
        culture_match = self._find_pattern_match(combined_text, self.culture_velocity_patterns)
        if culture_match:
            score += 20
            breakdown.append("Culture/Velocity Issues (+20)")
            evidence_quotes.append(f"Culture: \"{culture_match}\"")

        # STEP 4: Check for specific engineering pain (+10)
        eng_pain_match = self._find_pattern_match(combined_text, self.engineering_pain_patterns)
        if eng_pain_match:
            score += 10
            breakdown.append("Engineering Pain (+10)")
            evidence_quotes.append(f"Engineering: \"{eng_pain_match}\"")

        post["score"] = score
        post["score_breakdown"] = ", ".join(breakdown) if breakdown else "CEO/founder but no pain signals"
        post["evidence"] = " | ".join(evidence_quotes) if evidence_quotes else "CEO identity only"

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
