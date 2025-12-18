"""news_server.py

FastMCP server providing news and information tools.
Uses:
- newsapi-python: Official NewsAPI client (https://newsapi.org/docs/client-libraries/python)
- wikipedia: Wikipedia API wrapper (https://pypi.org/project/wikipedia/)

Requirements:
    pip install newsapi-python wikipedia

Environment:
    NEWS_API_KEY: Your API key from https://newsapi.org

Direct Testing:
    Import the core functions directly (without MCP decoration):
    
    from utils.mcp.fastmcp.news_server import (
        get_current_datetime,
        search_wikipedia,
        get_wikipedia_page,
        get_top_headlines,
        search_news,
        get_news_sources
    )
    
    # These are regular Python functions, call them directly:
    result = get_current_datetime("UTC")
    print(result)
"""
from fastmcp import FastMCP
from datetime import datetime
import os

mcp = FastMCP("News")


# =============================================================================
# INTERNAL HELPER
# =============================================================================

def _get_newsapi_client():
    """Get NewsAPI client instance."""
    from newsapi import NewsApiClient
    
    api_key = os.environ.get("NEWS_API_KEY")
    if not api_key:
        raise ValueError("NEWS_API_KEY not found. Get a free key at https://newsapi.org")
    
    return NewsApiClient(api_key=api_key)


# =============================================================================
# CORE FUNCTIONS (directly callable for testing)
# =============================================================================

def get_current_datetime(timezone: str = "UTC") -> str:
    """
    Get current date and time.
    
    Args:
        timezone: Timezone name (UTC, EST, PST, CET, JST, etc.)
        
    Returns:
        Current date and time in the specified timezone
    """
    from datetime import timezone as tz, timedelta
    
    offsets = {
        "UTC": 0, "GMT": 0,
        "EST": -5, "EDT": -4,
        "CST": -6, "CDT": -5,
        "MST": -7, "MDT": -6,
        "PST": -8, "PDT": -7,
        "CET": 1, "CEST": 2,
        "JST": 9,
        "IST": 5.5,
        "AEST": 10, "AEDT": 11,
        "BST": 1,
    }
    
    offset_hours = offsets.get(timezone.upper(), 0)
    offset = timedelta(hours=offset_hours)
    
    now = datetime.now(tz.utc) + offset
    
    return (
        f"Current Date/Time ({timezone.upper()}):\n"
        f"Date: {now.strftime('%A, %B %d, %Y')}\n"
        f"Time: {now.strftime('%I:%M:%S %p')}\n"
        f"ISO: {now.strftime('%Y-%m-%dT%H:%M:%S')}"
    )


def search_wikipedia(query: str, sentences: int = 3) -> str:
    """
    Search Wikipedia for information on a topic using the wikipedia library.
    
    Args:
        query: Search query (e.g., "artificial intelligence", "Tesla Motors")
        sentences: Number of sentences in summary (1-10)
        
    Returns:
        Wikipedia summary and link
    """
    import wikipedia
    
    sentences = min(max(sentences, 1), 10)
    
    try:
        # Try to get the page directly
        summary = wikipedia.summary(query, sentences=sentences)
        page = wikipedia.page(query)
        
        return (
            f"Wikipedia: {page.title}\n\n"
            f"{summary}\n\n"
            f"Read more: {page.url}"
        )
    
    except wikipedia.exceptions.DisambiguationError as e:
        # Multiple options found
        options = e.options[:5]  # Limit to 5 options
        return (
            f"Multiple results found for '{query}'.\n"
            f"Did you mean one of these?\n"
            f"- " + "\n- ".join(options)
        )
    
    except wikipedia.exceptions.PageError:
        # Try search instead
        try:
            results = wikipedia.search(query, results=5)
            if results:
                return (
                    f"No exact match for '{query}'.\n"
                    f"Related articles:\n"
                    f"- " + "\n- ".join(results)
                )
            return f"No Wikipedia article found for: {query}"
        except:
            return f"No Wikipedia article found for: {query}"
    
    except Exception as e:
        return f"Error searching Wikipedia: {e}"


def get_wikipedia_page(title: str) -> str:
    """
    Get full Wikipedia page content by exact title.
    
    Args:
        title: Exact Wikipedia page title (e.g., "Python (programming language)")
        
    Returns:
        Page summary, sections, and URL
    """
    import wikipedia
    
    try:
        page = wikipedia.page(title)
        
        # Get summary
        summary = wikipedia.summary(title, sentences=5)
        
        # Get section titles
        sections = page.sections[:10] if page.sections else []
        sections_str = ", ".join(sections) if sections else "N/A"
        
        return (
            f"Wikipedia: {page.title}\n\n"
            f"Summary:\n{summary}\n\n"
            f"Sections: {sections_str}\n\n"
            f"URL: {page.url}"
        )
    
    except wikipedia.exceptions.DisambiguationError as e:
        options = e.options[:5]
        return (
            f"'{title}' is ambiguous. Did you mean:\n"
            f"- " + "\n- ".join(options)
        )
    
    except wikipedia.exceptions.PageError:
        return f"Page not found: {title}"
    
    except Exception as e:
        return f"Error: {e}"


def get_top_headlines(
    category: str = "technology",
    country: str = "us",
    query: str = None,
    page_size: int = 5
) -> str:
    """
    Get top news headlines from NewsAPI.
    
    Args:
        category: News category - business, entertainment, general, health, science, sports, technology
        country: Country code (us, gb, de, fr, au, etc.)
        query: Optional search query to filter headlines
        page_size: Number of headlines to return (max 10)
        
    Returns:
        Top headlines with sources and links
    """
    try:
        newsapi = _get_newsapi_client()
    except ValueError as e:
        return str(e)
    
    valid_categories = ["business", "entertainment", "general", "health", "science", "sports", "technology"]
    if category.lower() not in valid_categories:
        return f"Invalid category. Choose from: {', '.join(valid_categories)}"
    
    page_size = min(max(page_size, 1), 10)
    
    try:
        # Use the official client library
        response = newsapi.get_top_headlines(
            q=query,
            category=category.lower(),
            country=country.lower(),
            page_size=page_size
        )
        
        if response.get("status") != "ok":
            return f"NewsAPI error: {response.get('message', 'Unknown error')}"
        
        articles = response.get("articles", [])
        if not articles:
            return f"No headlines found for category: {category}"
        
        headlines = []
        for i, article in enumerate(articles, 1):
            title = article.get("title", "No title")
            source = article.get("source", {}).get("name", "Unknown")
            url = article.get("url", "")
            published = article.get("publishedAt", "")
            description = article.get("description", "")
            
            if published:
                try:
                    dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
                    published = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            
            # Truncate description
            if description and len(description) > 120:
                description = description[:120] + "..."
            
            headlines.append(
                f"{i}. [{source}] {title}\n"
                f"   {description}\n"
                f"   Published: {published}\n"
                f"   {url}"
            )
        
        return f"Top {category.title()} Headlines ({country.upper()}):\n\n" + "\n\n".join(headlines)
    
    except Exception as e:
        return f"Error fetching headlines: {e}"


def search_news(
    query: str,
    page_size: int = 5,
    sort_by: str = "relevancy",
    language: str = "en"
) -> str:
    """
    Search for news articles on any topic using NewsAPI.
    
    Args:
        query: Search query (e.g., "artificial intelligence", "Tesla earnings")
        page_size: Number of articles to return (max 10)
        sort_by: Sort order - relevancy, popularity, publishedAt
        language: Language code (en, de, fr, es, etc.)
        
    Returns:
        Matching news articles with sources and links
    """
    try:
        newsapi = _get_newsapi_client()
    except ValueError as e:
        return str(e)
    
    valid_sort = ["relevancy", "popularity", "publishedAt"]
    if sort_by not in valid_sort:
        sort_by = "relevancy"
    
    page_size = min(max(page_size, 1), 10)
    
    try:
        # Use the official client library
        response = newsapi.get_everything(
            q=query,
            language=language,
            sort_by=sort_by,
            page_size=page_size
        )
        
        if response.get("status") != "ok":
            return f"NewsAPI error: {response.get('message', 'Unknown error')}"
        
        articles = response.get("articles", [])
        total_results = response.get("totalResults", 0)
        
        if not articles:
            return f"No articles found for: {query}"
        
        results = []
        for i, article in enumerate(articles, 1):
            title = article.get("title", "No title")
            source = article.get("source", {}).get("name", "Unknown")
            description = article.get("description", "")
            url = article.get("url", "")
            published = article.get("publishedAt", "")
            
            if published:
                try:
                    dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
                    published = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            
            # Truncate description
            if description and len(description) > 150:
                description = description[:150] + "..."
            
            results.append(
                f"{i}. [{source}] {title}\n"
                f"   {description}\n"
                f"   Published: {published}\n"
                f"   {url}"
            )
        
        header = f"News Search: '{query}' ({total_results} total results, showing {len(articles)})\n\n"
        return header + "\n\n".join(results)
    
    except Exception as e:
        return f"Error searching news: {e}"


def get_news_sources(category: str = None, country: str = None) -> str:
    """
    Get available news sources from NewsAPI.
    
    Args:
        category: Filter by category (business, technology, etc.)
        country: Filter by country code (us, gb, de, etc.)
        
    Returns:
        List of available news sources
    """
    try:
        newsapi = _get_newsapi_client()
    except ValueError as e:
        return str(e)
    
    try:
        response = newsapi.get_sources(
            category=category.lower() if category else None,
            country=country.lower() if country else None
        )
        
        if response.get("status") != "ok":
            return f"NewsAPI error: {response.get('message', 'Unknown error')}"
        
        sources = response.get("sources", [])
        if not sources:
            return "No sources found"
        
        # Limit to 15 sources for readability
        sources = sources[:15]
        
        result = []
        for src in sources:
            name = src.get("name", "Unknown")
            desc = src.get("description", "")
            url = src.get("url", "")
            cat = src.get("category", "")
            
            if len(desc) > 80:
                desc = desc[:80] + "..."
            
            result.append(f"- {name} ({cat})\n  {desc}\n  {url}")
        
        return f"News Sources:\n\n" + "\n\n".join(result)
    
    except Exception as e:
        return f"Error fetching sources: {e}"


# =============================================================================
# MCP TOOL WRAPPERS (call core functions)
# =============================================================================

@mcp.tool()
def mcp_get_current_datetime(timezone: str = "UTC") -> str:
    """Get current date and time in the specified timezone."""
    return get_current_datetime(timezone)


@mcp.tool()
def mcp_search_wikipedia(query: str, sentences: int = 3) -> str:
    """Search Wikipedia for information on a topic."""
    return search_wikipedia(query, sentences)


@mcp.tool()
def mcp_get_wikipedia_page(title: str) -> str:
    """Get full Wikipedia page content by exact title."""
    return get_wikipedia_page(title)


@mcp.tool()
def mcp_get_top_headlines(
    category: str = "technology",
    country: str = "us",
    query: str = None,
    page_size: int = 5
) -> str:
    """Get top news headlines from NewsAPI."""
    return get_top_headlines(category, country, query, page_size)


@mcp.tool()
def mcp_search_news(
    query: str,
    page_size: int = 5,
    sort_by: str = "relevancy",
    language: str = "en"
) -> str:
    """Search for news articles on any topic using NewsAPI."""
    return search_news(query, page_size, sort_by, language)


@mcp.tool()
def mcp_get_news_sources(category: str = None, country: str = None) -> str:
    """Get available news sources from NewsAPI."""
    return get_news_sources(category, country)


if __name__ == "__main__":
    mcp.run(transport="streamable-http", port=8002)
