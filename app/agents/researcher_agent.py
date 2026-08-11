from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from typing import List, Dict, Any
import os
from app.tools.web_search import WebSearchTool, DuckDuckGoSearch
from app.tools.arxiv_search import ArxivSearchTool
from app.utils.logger import logger
import asyncio

class ResearcherAgent:
    """Research information gathering agent."""
    
    def __init__(self):
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model=os.getenv("LLM_MODEL", "llama3-70b-8192"),
            temperature=0.1
        )
        
        self.web_search = WebSearchTool()
        self.duckduckgo = DuckDuckGoSearch()
        self.arxiv_search = ArxivSearchTool()
        
        self.extraction_prompt = PromptTemplate(
            input_variables=["query", "search_results"],
            template="""
            You are a Research Information Extractor. Analyze the following search results for the query: {query}
            
            Search Results:
            {search_results}
            
            Extract and summarize the key information, focusing on:
            1. Main findings and insights
            2. Important facts and data
            3. Key quotes or statements
            4. Source credibility indicators
            
            Provide a concise summary (2-3 paragraphs) of the most relevant information.
            """
        )
        
        self.chain = self.extraction_prompt | self.llm | StrOutputParser()
    
    async def research(self, query: str) -> Dict[str, Any]:
        """Research a specific query."""
        try:
            logger.info(f"Researching: {query}")
            
            # Gather information from multiple sources
            web_results = await self.web_search.asearch(query, max_results=5)
            arxiv_results = await asyncio.to_thread(self.arxiv_search.search, query, max_results=3)
            
            # Combine and deduplicate results
            all_results = web_results + arxiv_results
            
            if not all_results:
                logger.warning(f"No results found for: {query}")
                return {
                    "query": query,
                    "summary": f"No information found for: {query}",
                    "sources": [],
                    "findings": []
                }
            
            # Extract key information
            summary = await self._extract_summary(query, all_results)
            findings = await self._extract_findings(query, all_results)
            
            return {
                "query": query,
                "summary": summary,
                "sources": all_results[:10],
                "findings": findings
            }
            
        except Exception as e:
            logger.error(f"Research error for query '{query}': {str(e)}")
            return {
                "query": query,
                "summary": f"Error researching: {str(e)}",
                "sources": [],
                "findings": []
            }
    
    async def _extract_summary(self, query: str, results: List[Dict]) -> str:
        """Extract summary from search results."""
        try:
            # Format results for prompt
            formatted_results = "\n\n".join([
                f"Source {i+1}: {r.get('title', '')}\n{r.get('content', '')[:500]}..."
                for i, r in enumerate(results[:5])
            ])
            
            return await asyncio.to_thread(
                self.chain.invoke,
                {"query": query, "search_results": formatted_results}
            )
        except Exception as e:
            logger.error(f"Summary extraction error: {str(e)}")
            return "Summary extraction failed."
    
    async def _extract_findings(self, query: str, results: List[Dict]) -> List[Dict]:
        """Extract key findings from search results."""
        findings = []
        for result in results[:5]:
            if result.get("content"):
                findings.append({
                    "source": result.get("title", ""),
                    "url": result.get("url", ""),
                    "key_points": result.get("content", "")[:200] + "...",
                    "relevance": result.get("score", 0.5)
                })
        return findings