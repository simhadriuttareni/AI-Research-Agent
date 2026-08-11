from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
from app.utils.logger import logger
import asyncio
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

class WebSearchTool:
    """Web search tool using Tavily API."""
    
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            logger.warning("TAVILY_API_KEY not found in environment")
            self.client = None
        else:
            try:
                from tavily import TavilyClient
                self.client = TavilyClient(api_key=self.api_key)
            except ImportError:
                logger.warning("tavily-python not installed")
                self.client = None
        
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Perform web search synchronously."""
        if not self.client:
            logger.warning("Tavily client not available")
            return []
            
        try:
            logger.info(f"Searching: {query}")
            response = self.client.search(
                query=query,
                max_results=max_results,
                include_answer=False,
                search_depth="advanced"
            )
            
            results = []
            for result in response.get("results", []):
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "score": result.get("score", 0.0),
                    "raw_content": result.get("raw_content", "")
                })
            
            logger.info(f"Found {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return []
    
    async def asearch(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Perform web search asynchronously."""
        if not self.client:
            return []
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.search,
            query,
            max_results
        )

    def search_news(self, topic: str, days: int = 7) -> List[Dict[str, Any]]:
        """Search for news articles on a topic."""
        if not self.client:
            return []
        try:
            query = f"{topic} news"
            return self.search(query, max_results=5)
        except Exception as e:
            logger.error(f"News search error: {str(e)}")
            return []

class DuckDuckGoSearch:
    """Alternative free search using DuckDuckGo."""
    
    def __init__(self):
        try:
            from duckduckgo_search import DDGS
            self.ddgs = DDGS()
        except ImportError:
            logger.warning("duckduckgo-search not installed")
            self.ddgs = None
    
    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        if not self.ddgs:
            return []
        
        try:
            results = []
            for r in self.ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "content": r.get("body", ""),
                    "score": 1.0
                })
            return results
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {str(e)}")
            return []