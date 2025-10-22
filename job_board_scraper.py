"""
Job board scraper for finding VP Engineering/CTO roles at young startups.

Signals internal struggle when <2yr old company posts senior eng role.
Scrapes YC companies and AngelList.
"""

import httpx
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from bs4 import BeautifulSoup


class JobBoardScraper:
    """Scraper for job boards (YC, AngelList)."""

    def __init__(self, days: int = 7):
        """
        Initialize job board scraper.

        Args:
            days: Number of days to look back
        """
        self.days = days

    def scrape_yc_jobs(self) -> List[Dict]:
        """
        Scrape Y Combinator's Work at a Startup for senior eng roles.

        YC job board: https://www.ycombinator.com/companies/jobs

        Returns:
            List of job postings
        """
        results = []

        try:
            with httpx.Client(timeout=30, follow_redirects=True) as client:
                # YC jobs API endpoint
                url = "https://www.ycombinator.com/api/companies/jobs"

                response = client.get(url)

                if response.status_code == 200:
                    jobs = response.json()

                    for job in jobs:
                        try:
                            title = job.get('title', '')
                            company_name = job.get('company_name', '')

                            # Filter for senior engineering roles
                            senior_roles = [
                                'VP Engineering', 'VP Eng', 'VP of Engineering',
                                'Head of Engineering', 'Head of Eng',
                                'CTO', 'Chief Technology Officer',
                                'Director of Engineering', 'Engineering Director',
                            ]

                            if any(role.lower() in title.lower() for role in senior_roles):
                                # Check company age (YC batch year)
                                batch = job.get('batch', '')
                                is_young = self._is_young_company(batch)

                                results.append({
                                    'type': 'job_posting',
                                    'title': title,
                                    'text': job.get('description', ''),
                                    'url': job.get('url', ''),
                                    'job_url': job.get('url', ''),
                                    'author': company_name,
                                    'company': company_name,
                                    'company_batch': batch,
                                    'is_young_company': is_young,
                                    'created_at': datetime.now(),
                                    'date': datetime.now(),
                                    'source': 'YC Jobs',
                                    'source_detail': 'Y Combinator Work at a Startup',
                                })

                        except Exception as e:
                            print(f"Error processing YC job: {e}")
                            continue

        except Exception as e:
            print(f"Error scraping YC jobs: {e}")

        return results

    def scrape_angellist(self) -> List[Dict]:
        """
        Scrape AngelList (now Wellfound) for senior eng roles at young startups.

        Note: AngelList requires authentication for most data.
        This is a simplified implementation.

        Returns:
            List of job postings
        """
        results = []

        print("AngelList/Wellfound scraping requires auth - skipping for now")
        print("Recommend using their API or manual search")

        # In production, you would:
        # 1. Use Wellfound API with credentials
        # 2. Or provide CSV import from manual searches

        return results

    def _is_young_company(self, batch: str) -> bool:
        """
        Check if YC batch indicates a young company (<2 years).

        Args:
            batch: YC batch string like "W23", "S24"

        Returns:
            True if company is <2 years old
        """
        if not batch:
            return False

        try:
            # Parse batch: W23 = Winter 2023, S24 = Summer 2024
            season = batch[0]  # W or S
            year = int("20" + batch[1:])  # 23 -> 2023

            # Add months based on season
            # W = Winter (January), S = Summer (June)
            month = 1 if season == 'W' else 6

            batch_date = datetime(year, month, 1)
            age_days = (datetime.now() - batch_date).days

            # <2 years = <730 days
            return age_days < 730

        except:
            return False

    def scrape(self) -> List[Dict]:
        """
        Scrape all job boards for senior eng roles at young startups.

        Returns:
            List of matching job postings
        """
        all_jobs = []

        print(f"Scraping job boards for senior eng roles...")

        # YC Jobs
        print("  Searching Y Combinator jobs...")
        yc_jobs = self.scrape_yc_jobs()
        all_jobs.extend(yc_jobs)

        # AngelList (currently skipped)
        angellist_jobs = self.scrape_angellist()
        all_jobs.extend(angellist_jobs)

        print(f"  Found {len(all_jobs)} senior eng job postings")

        return all_jobs
