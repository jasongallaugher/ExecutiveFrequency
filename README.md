# ExecutiveFrequency

Python scraper that finds CEO/founder engineering problems on HackerNews and Reddit. Identifies and scores executive pain signals to discover potential consulting opportunities.

## What It Does

Searches HackerNews and Reddit for posts from CEOs/founders discussing engineering challenges, then scores them based on urgency and pain signals.

**Scoring System (0-100):**
- +30 points: CEO/founder identity or flair
- +25 points: Urgency indicators (timeline, money, crisis)
- +20 points: Transition keywords (hiring, replacing, need)
- +15 points: Velocity/shipping issues
- +10 points: Each pain keyword (technical debt, scaling, outages, etc.) - max 3

**Search Keywords:**
- CTO, VP Engineering
- Engineering team, technical debt
- Can't ship, slow development
- Hiring engineers

## Installation

1. Install [uv](https://github.com/astral-sh/uv):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone and install:
```bash
git clone https://github.com/yourusername/ExecutiveFrequency.git
cd ExecutiveFrequency
uv sync
```

3. (Optional) Set up Reddit API credentials:
```bash
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"
export REDDIT_USER_AGENT="ExecutiveFrequency/0.1.0"
```

To get Reddit credentials:
1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Select "script" type
4. Use `http://localhost:8080` as redirect URI
5. Copy the client ID and secret

**Note:** HackerNews search works without any API credentials. Reddit is optional.

## Usage

### Basic Search

Search last 7 days and export to CSV:
```bash
uv run python main.py search
```

### Custom Options

```bash
# Search last 14 days
uv run python main.py search --days 14

# Only show posts with score >= 50
uv run python main.py search --min-score 50

# Custom output file
uv run python main.py search --output executives.csv

# Only search HackerNews (no Reddit API needed)
uv run python main.py search --hn-only

# Only search Reddit
uv run python main.py search --reddit-only

# Show top 20 results
uv run python main.py search --show-top 20
```

### View Results

Display results from a saved CSV:
```bash
uv run python main.py show results.csv
```

## Output Format

CSV columns:
- `score`: Total pain signal score (0-100)
- `source`: "HackerNews" or "Reddit"
- `title`: Post title
- `link`: URL to discussion
- `author`: Username
- `excerpt`: First 200 chars of post text
- `date`: Post date/time
- `score_breakdown`: Which signals triggered (e.g., "CEO/Founder (+30), Urgency (+25)")

## Example Output

```
TOP 10 RESULTS
================================================================================

1. [ 75] Need to hire VP Engineering - company stuck on legacy Rails app
   Source: HackerNews | Author: startup_ceo
   Signals: CEO/Founder (+30), Urgency (+25), Transition/Hiring (+20)
   Link: https://news.ycombinator.com/item?id=12345678

2. [ 70] Our engineering team can't ship features fast enough
   Source: Reddit | Author: saas_founder
   Signals: CEO/Founder (+30), Velocity Issues (+15), Pain Keywords x2 (+20)
   Link: https://reddit.com/r/startups/comments/abc123

3. [ 55] CTO left, need technical leadership ASAP
   Source: Reddit | Author: entrepreneur
   Signals: Urgency (+25), Transition/Hiring (+20), Pain Keywords x1 (+10)
   Link: https://reddit.com/r/entrepreneur/comments/xyz789
```

## How It Works

1. **Scraping**
   - **HackerNews**: Uses Algolia HN Search API (no auth required)
   - **Reddit**: Uses PRAW library (requires API credentials)

2. **Filtering**
   - Searches for engineering leadership keywords
   - Filters to last N days (default: 7)
   - Deduplicates by URL

3. **Scoring**
   - Analyzes post title, text, and author info
   - Applies scoring rules based on pain signals
   - Sorts by total score (highest first)

4. **Export**
   - Saves to CSV for easy review
   - Displays top results in terminal

## Target Subreddits

- r/startups
- r/entrepreneur
- r/SaaS
- r/smallbusiness
- r/programming
- r/cscareerquestions
- r/ExperiencedDevs
- r/webdev
- r/devops

## Use Cases

- **Consulting**: Find potential clients with urgent engineering needs
- **Recruiting**: Identify companies hiring senior engineering leaders
- **Market Research**: Understand common engineering pain points
- **Sales**: Discover prospects struggling with technical challenges

## Limitations

- Reddit requires API credentials (free but requires registration)
- HackerNews Algolia API has rate limits (respectful usage recommended)
- Score is heuristic-based, not ML-powered
- Only searches English-language posts
- May miss posts with non-standard phrasing

## Privacy & Ethics

- Only searches public posts
- Does not interact with users
- Does not store personal data beyond what's in posts
- Respects platform rate limits
- Use responsibly and don't spam people

## Future Enhancements

Potential improvements:
- [ ] Add LinkedIn scraping
- [ ] ML-based scoring model
- [ ] Email digest of daily results
- [ ] Slack/Discord notifications
- [ ] Web dashboard for viewing results
- [ ] Track trends over time
- [ ] Company identification and enrichment

## License

MIT License - Use responsibly

## Credits

Built for finding engineering leadership opportunities through social signals.
