#!/usr/bin/env python3
"""
ExecutiveFrequency - Find CEO/founder engineering problems on HN + Reddit

Main CLI application.
"""

import click
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from hn_scraper import HNScraper
from reddit_scraper import RedditScraper
from twitter_scraper import TwitterScraper
from linkedin_scraper import LinkedInScraper
from job_board_scraper import JobBoardScraper
from scorer import PostScorer


def create_excerpt(text: str, max_length: int = 200) -> str:
    """Create a short excerpt from text."""
    if not text:
        return ""

    # Clean up whitespace
    text = " ".join(text.split())

    if len(text) <= max_length:
        return text

    return text[:max_length] + "..."


def export_to_csv(posts: List[Dict], output_file: str):
    """
    Export scored posts to CSV.

    Args:
        posts: List of scored post dictionaries
        output_file: Path to output CSV file
    """
    if not posts:
        print("No posts to export")
        return

    fieldnames = [
        "score",
        "source",
        "title",
        "link",
        "author",
        "excerpt",
        "date",
        "score_breakdown",
        "evidence",
    ]

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for post in posts:
            # Determine the link (prefer Reddit/HN URL, fallback to article URL)
            link = post.get("reddit_url") or post.get("hn_url") or post.get("url", "")

            # Create excerpt from text
            excerpt = create_excerpt(post.get("text", ""))

            # Format date
            date = post.get("date")
            if isinstance(date, datetime):
                date_str = date.strftime("%Y-%m-%d %H:%M")
            else:
                date_str = str(date)

            writer.writerow({
                "score": post.get("score", 0),
                "source": post.get("source", ""),
                "title": post.get("title", "")[:200],  # Truncate long titles
                "link": link,
                "author": post.get("author", ""),
                "excerpt": excerpt,
                "date": date_str,
                "score_breakdown": post.get("score_breakdown", ""),
                "evidence": post.get("evidence", ""),
            })

    print(f"\nExported {len(posts)} posts to {output_file}")


def display_top_results(posts: List[Dict], limit: int = 10):
    """Display top scoring posts in terminal."""
    if not posts:
        print("\nNo posts found.")
        return

    print(f"\n{'='*80}")
    print(f"TOP {min(limit, len(posts))} RESULTS")
    print(f"{'='*80}\n")

    for i, post in enumerate(posts[:limit], 1):
        score = post.get("score", 0)
        source = post.get("source", "")
        title = post.get("title", "")
        author = post.get("author", "")
        breakdown = post.get("score_breakdown", "")
        evidence = post.get("evidence", "")
        link = post.get("reddit_url") or post.get("hn_url") or post.get("url", "")

        print(f"{i}. [{score:3d}] {title[:70]}")
        print(f"   Source: {source} | Author: {author}")
        print(f"   Signals: {breakdown}")
        if evidence and evidence != "No evidence extracted":
            print(f"   Evidence: {evidence}")
        print(f"   Link: {link}")
        print()


@click.group()
def cli():
    """ExecutiveFrequency - Find CEO/founder engineering problems on HN + Reddit."""
    pass


@cli.command()
@click.option('--days', default=7, help='Number of days to look back (default: 7)')
@click.option('--output', default='results.csv', help='Output CSV file (default: results.csv)')
@click.option('--min-score', default=0, help='Minimum score to include (default: 0)')
@click.option('--show-top', default=10, help='Number of top results to display (default: 10)')
@click.option('--reddit-only', is_flag=True, help='Only scrape Reddit')
@click.option('--hn-only', is_flag=True, help='Only scrape HackerNews')
@click.option('--twitter-only', is_flag=True, help='Only scrape Twitter/X')
@click.option('--jobs-only', is_flag=True, help='Only scrape job boards')
@click.option('--skip-twitter', is_flag=True, help='Skip Twitter/X scraping')
@click.option('--skip-jobs', is_flag=True, help='Skip job board scraping')
def search(days: int, output: str, min_score: int, show_top: int, reddit_only: bool, hn_only: bool,
           twitter_only: bool, jobs_only: bool, skip_twitter: bool, skip_jobs: bool):
    """Search for executive engineering pain signals across all sources."""

    print(f"\n{'='*80}")
    print(f"ExecutiveFrequency - Engineering Pain Signal Finder")
    print(f"{'='*80}\n")
    print(f"Lookback period: {days} days")
    print(f"Minimum score: {min_score}")
    print()

    all_posts = []
    source_counts = {}

    # Determine which sources to scrape
    scrape_all = not any([reddit_only, hn_only, twitter_only, jobs_only])

    # Scrape HackerNews
    if scrape_all or hn_only:
        hn_scraper = HNScraper(days=days)
        hn_posts = hn_scraper.scrape()
        all_posts.extend(hn_posts)
        source_counts['HackerNews'] = len(hn_posts)

    # Scrape Reddit
    if scrape_all or reddit_only:
        reddit_scraper = RedditScraper(days=days)
        reddit_posts = reddit_scraper.scrape()
        all_posts.extend(reddit_posts)
        source_counts['Reddit'] = len(reddit_posts)

    # Scrape Twitter/X
    if (scrape_all or twitter_only) and not skip_twitter:
        twitter_scraper = TwitterScraper(days=days)
        twitter_posts = twitter_scraper.scrape()
        all_posts.extend(twitter_posts)
        source_counts['Twitter'] = len(twitter_posts)

    # Scrape Job Boards
    if (scrape_all or jobs_only) and not skip_jobs:
        job_scraper = JobBoardScraper(days=days)
        job_posts = job_scraper.scrape()
        all_posts.extend(job_posts)
        source_counts['YC Jobs'] = len(job_posts)

    print(f"\nTotal posts found: {len(all_posts)}")

    # Score posts
    print("\nScoring posts...")
    scorer = PostScorer()
    scored_posts = scorer.score_posts(all_posts)

    # Filter by minimum score
    filtered_posts = [p for p in scored_posts if p["score"] >= min_score]
    print(f"Posts with score >= {min_score}: {len(filtered_posts)}")

    # Display top results
    display_top_results(filtered_posts, limit=show_top)

    # Export to CSV
    export_to_csv(filtered_posts, output)

    # Summary statistics
    if filtered_posts:
        avg_score = sum(p["score"] for p in filtered_posts) / len(filtered_posts)
        max_score = max(p["score"] for p in filtered_posts)

        # Count by source
        source_breakdown = {}
        for post in filtered_posts:
            source = post.get("source", "Unknown")
            source_breakdown[source] = source_breakdown.get(source, 0) + 1

        print(f"\n{'='*80}")
        print(f"STATISTICS")
        print(f"{'='*80}")
        print(f"Total posts analyzed: {len(all_posts)}")

        # Show source breakdown
        if source_counts:
            print(f"\nPosts found by source:")
            for source, count in source_counts.items():
                print(f"  {source}: {count}")

        print(f"\nPosts with signals: {len(filtered_posts)}")

        # Show scored posts by source
        if source_breakdown:
            print(f"\nScored posts by source:")
            for source, count in sorted(source_breakdown.items(), key=lambda x: x[1], reverse=True):
                print(f"  {source}: {count}")

        print(f"\nAverage score: {avg_score:.1f}")
        print(f"Maximum score: {max_score}")
        print(f"\nResults saved to: {output}")


@cli.command()
@click.argument('csv_file')
@click.option('--limit', default=20, help='Number of results to show (default: 20)')
def show(csv_file: str, limit: int):
    """Display results from a CSV file."""

    if not Path(csv_file).exists():
        click.echo(f"Error: File not found: {csv_file}", err=True)
        return

    posts = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            posts.append(row)

    if not posts:
        print("No posts in file")
        return

    print(f"\n{'='*80}")
    print(f"SHOWING {min(limit, len(posts))} of {len(posts)} RESULTS from {csv_file}")
    print(f"{'='*80}\n")

    for i, post in enumerate(posts[:limit], 1):
        score = post.get("score", "0")
        source = post.get("source", "")
        title = post.get("title", "")
        author = post.get("author", "")
        breakdown = post.get("score_breakdown", "")
        evidence = post.get("evidence", "")
        link = post.get("link", "")

        print(f"{i}. [{score:>3}] {title[:70]}")
        print(f"   Source: {source} | Author: {author}")
        print(f"   Signals: {breakdown}")
        if evidence and evidence != "No evidence extracted":
            print(f"   Evidence: {evidence}")
        print(f"   Link: {link}")
        print()


if __name__ == '__main__':
    cli()
