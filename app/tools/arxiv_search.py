import arxiv
from typing import List, Dict, Any
from app.utils.logger import logger

class ArxivSearchTool:
    """Search academic papers on ArXiv."""
    
    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search ArXiv for papers."""
        try:
            logger.info(f"Searching ArXiv: {query}")
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            results = []
            for paper in search.results():
                results.append({
                    "title": paper.title,
                    "summary": paper.summary,
                    "url": paper.entry_id,
                    "pdf_url": paper.pdf_url,
                    "authors": [str(a) for a in paper.authors],
                    "published": paper.published.strftime("%Y-%m-%d"),
                    "categories": paper.categories,
                    "primary_category": paper.primary_category
                })
            
            logger.info(f"Found {len(results)} ArXiv papers")
            return results
        except Exception as e:
            logger.error(f"ArXiv search error: {str(e)}")
            return []