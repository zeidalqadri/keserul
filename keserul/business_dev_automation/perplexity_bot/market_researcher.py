"""
Market Researcher module for PerplexityMCP-Bot.
Uses Perplexity API to gather market insights on dev-tools adoption in SE Asia.
"""

import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

# Add core directory to path to use the perplexity_mcp module
core_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "core"))
if core_path not in sys.path:
    sys.path.append(core_path)

try:
    from core.tools.perplexity_mcp import (PerplexityMCPError,
                                           perplexity_answer,
                                           perplexity_search)
except ImportError:
    # Alternative import approach if the above fails
    from core.tools.perplexity_mcp import (PerplexityMCPError, perplexity_answer,
                                           perplexity_search)

# Define constants
DEFAULT_CACHE_DIR = os.path.join(
    os.path.dirname(__file__), "..", "output", "research_cache"
)
DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")


class MarketResearchError(Exception):
    """Custom exception for market research errors."""


class MarketResearcher:
    """Market research automation using Perplexity API."""

    def __init__(self, cache_dir: str = DEFAULT_CACHE_DIR, enable_caching: bool = True):
        """
        Initialize the market researcher.

        Parameters:
        -----------
        cache_dir : str
            Directory to store cached search results
        enable_caching : bool
            Whether to cache search results to avoid redundant API calls
        """
        self.cache_dir = cache_dir
        self.enable_caching = enable_caching

        # Create cache directory if it doesn't exist
        if enable_caching and not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)

        # Track queries and results for the session
        self.session_queries = []
        self.session_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    def search(
        self,
        query: str,
        market_segment: str = "all",
        top_k: int = 15,
        force_refresh: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Perform a market research search using Perplexity.

        Parameters:
        -----------
        query : str
            The research query to send to Perplexity
        market_segment : str
            Target market segment (e.g., "singapore_sme", "malaysia_enterprise")
        top_k : int
            Number of results to return
        force_refresh : bool
            Whether to force a new search instead of using cache

        Returns:
        --------
        List[Dict[str, Any]]
            Search results with metadata
        """
        cache_key = f"{market_segment}_{self._normalize_query(query)}"
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")

        # Try to load from cache if enabled
        if self.enable_caching and not force_refresh and os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)
                    print(f"Loaded cached results for query: {query[:50]}...")
                    return cached_data.get("results", [])
            except Exception as e:
                print(f"Cache read error: {e}")

        # Enhance query with market segment information
        enhanced_query = query
        if market_segment and market_segment != "all":
            if "singapore" in market_segment.lower():
                enhanced_query = (
                    f"{query} in Singapore small and medium enterprises (SMEs)"
                )
            elif "malaysia" in market_segment.lower():
                enhanced_query = (
                    f"{query} in Malaysian small and medium enterprises (SMEs)"
                )
            else:
                enhanced_query = (
                    f"{query} in Southeast Asian small and medium enterprises (SMEs)"
                )

        try:
            # Call perplexity search API
            results = perplexity_search(enhanced_query, top_k=top_k)

            # Track query
            self.session_queries.append(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "query": enhanced_query,
                    "market_segment": market_segment,
                    "results_count": len(results),
                    "top_domains": self._extract_top_domains(results),
                }
            )

            # Cache results if enabled
            if self.enable_caching:
                cache_data = {
                    "query": enhanced_query,
                    "timestamp": datetime.utcnow().isoformat(),
                    "market_segment": market_segment,
                    "results": results,
                }
                try:
                    with open(cache_file, "w", encoding="utf-8") as f:
                        json.dump(cache_data, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    print(f"Cache write error: {e}")

            return results

        except PerplexityMCPError as e:
            raise MarketResearchError(f"Perplexity search failed: {e}")

    def get_market_insight(
        self, question: str, market_segment: str = "all", depth: str = "detailed"
    ) -> Dict[str, Any]:
        """
        Get a direct market insight answer from Perplexity.

        Parameters:
        -----------
        question : str
            The research question to ask
        market_segment : str
            Target market segment (e.g., "singapore_sme", "malaysia_enterprise")
        depth : str
            Answer depth: "concise" or "detailed"

        Returns:
        --------
        Dict[str, Any]
            Structured answer with metadata
        """
        # Enhance question with market context
        enhanced_question = question
        if market_segment and market_segment != "all":
            if market_segment == "singapore_sme":
                enhanced_question = (
                    f"{question} Focus specifically on Singapore small and "
                    "medium enterprises with 5-30 developers."
                )
            elif market_segment == "malaysian_sme":
                enhanced_question = (
                    f"{question} Focus specifically on Malaysian small and "
                    "medium enterprises with 5-30 developers."
                )
            else:
                enhanced_question = (
                    f"{question} Focus specifically on Southeast Asian small "
                    "and medium enterprises with 5-30 developers."
                )

        try:
            answer = perplexity_answer(enhanced_question, depth=depth)

            result = {
                "question": enhanced_question,
                "answer": answer,
                "timestamp": datetime.utcnow().isoformat(),
                "market_segment": market_segment,
                "depth": depth,
            }

            # Track this query
            self.session_queries.append(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "query": enhanced_question,
                    "type": "direct_answer",
                    "market_segment": market_segment,
                }
            )

            return result

        except PerplexityMCPError as e:
            raise MarketResearchError(f"Perplexity answer failed: {e}")

    def analyze_search_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze search results to extract key insights.

        Parameters:
        -----------
        results : List[Dict[str, Any]]
            Search results from perplexity_search

        Returns:
        --------
        Dict[str, Any]
            Analysis of the results
        """
        if not results:
            return {"error": "No results to analyze"}

        try:
            # Extract domains and publication years
            domains = []
            years = []
            titles = []

            for result in results:
                url = result.get("url", "")
                title = result.get("title", "")
                snippet = result.get("snippet", "")

                # Extract domain
                if url:
                    domain = self._extract_domain(url)
                    if domain:
                        domains.append(domain)

                # Extract year if available in title or snippet
                year = self._extract_year(title + " " + snippet)
                if year:
                    years.append(year)

                titles.append(title)

            # Calculate domain and year frequencies
            domain_counts = pd.Series(domains).value_counts().to_dict()
            year_counts = pd.Series(years).value_counts().to_dict() if years else {}

            # Get most common topics from titles
            common_topics = self._extract_common_topics(titles)

            return {
                "total_results": len(results),
                "top_domains": dict(
                    sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                ),
                "year_distribution": dict(sorted(year_counts.items())),
                "common_topics": common_topics,
                "freshness_score": self._calculate_freshness(years) if years else None,
            }

        except Exception as e:
            return {"error": f"Analysis error: {str(e)}"}

    def save_session_summary(self, output_file: Optional[str] = None) -> str:
        """
        Save session summary to a JSON file.

        Parameters:
        -----------
        output_file : Optional[str]
            Path to output file, defaults to output/research_session_{session_id}.json

        Returns:
        --------
        str
            Path to the saved file
        """
        if not output_file:
            if not os.path.exists(DEFAULT_OUTPUT_DIR):
                os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)
            output_file = os.path.join(
                DEFAULT_OUTPUT_DIR, f"research_session_{self.session_id}.json"
            )

        session_data = {
            "session_id": self.session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "query_count": len(self.session_queries),
            "queries": self.session_queries,
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

        return output_file

    def _normalize_query(self, query: str) -> str:
        """Normalize a query for caching purposes."""
        return query.lower().strip().replace(" ", "_")[:50]

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse

            parsed = urlparse(url)
            domain = parsed.netloc
            return domain.replace("www.", "")
        except Exception:
            return ""

    def _extract_year(self, text: str) -> Optional[int]:
        """Extract year from text (looking for years between 2010 and current year)."""
        import re

        current_year = datetime.utcnow().year
        years = re.findall(r"\b(20[1-2][0-9])\b", text)
        if years:
            for year_str in years:
                year = int(year_str)
                if 2010 <= year <= current_year:
                    return year
        return None

    def _extract_top_domains(self, results: List[Dict[str, Any]]) -> List[str]:
        """Extract top domains from results."""
        domains = []
        for result in results:
            url = result.get("url", "")
            if url:
                domain = self._extract_domain(url)
                if domain:
                    domains.append(domain)
        return domains[:5] if domains else []

    def _extract_common_topics(self, titles: List[str]) -> List[str]:
        """Extract common topics from titles."""
        import re
        from collections import Counter

        # Join all titles
        all_text = " ".join(titles).lower()

        # Remove common stop words
        stop_words = {
            "and",
            "the",
            "for",
            "in",
            "on",
            "to",
            "of",
            "a",
            "is",
            "with",
            "by",
        }
        words = re.findall(r"\b[a-z][a-z]{2,}\b", all_text)
        filtered_words = [w for w in words if w not in stop_words]

        # Count occurrences
        word_counts = Counter(filtered_words)

        # Return top topics
        return [word for word, count in word_counts.most_common(10)]

    def _calculate_freshness(self, years: List[int]) -> float:
        """Calculate freshness score based on years (0.0 to 1.0)."""
        if not years:
            return 0.0

        current_year = datetime.utcnow().year
        avg_year = sum(years) / len(years)

        # Scale: 0.0 (all 2010 or older) to 1.0 (all current year)
        freshness = (avg_year - 2010) / (current_year - 2010)
        return max(0.0, min(1.0, freshness))  # Clamp between 0.0 and 1.0
