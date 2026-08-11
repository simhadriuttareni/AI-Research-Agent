import os
import httpx
import json
import logging
from groq import Groq
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResearchEngine:
    def __init__(self):
        # Get API keys from environment variables
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        
        if not self.groq_api_key:
            logger.error("GROQ_API_KEY not found in environment variables")
        if not self.tavily_key:
            logger.error("TAVILY_API_KEY not found in environment variables")
        
        logger.info("=" * 50)
        logger.info("RESEARCH ENGINE INITIALIZED")
        logger.info(f"GROQ Key: {self.groq_api_key[:15] if self.groq_api_key else 'MISSING'}...")
        logger.info(f"TAVILY Key: {self.tavily_key[:15] if self.tavily_key else 'MISSING'}...")
        logger.info("=" * 50)
        
        if self.groq_api_key:
            self.client = Groq(api_key=self.groq_api_key)
        else:
            self.client = None
        
    async def research(self, topic: str) -> dict:
        try:
            logger.info(f"?? Starting research on: {topic}")
            
            if not self.tavily_key or not self.client:
                return {
                    "report": f"# Research Report: {topic}\n\nError: API keys not configured. Please check environment variables.",
                    "citations": [],
                    "score": 0
                }
            
            search_results = await self._search(topic)
            
            if not search_results:
                return {
                    "report": f"# Research Report: {topic}\n\nNo results found. Please try a different topic.",
                    "citations": [],
                    "score": 50
                }
            
            logger.info(f"?? Found {len(search_results)} results")
            
            analysis = await self._analyze(topic, search_results)
            report = await self._generate_report(topic, analysis, search_results)
            citations = self._extract_citations(search_results)
            
            logger.info(f"? Research complete! Report length: {len(report)}")
            
            return {
                "topic": topic,
                "report": report,
                "citations": citations,
                "score": 85
            }
            
        except Exception as e:
            logger.error(f"? Research error: {str(e)}")
            return {
                "report": f"# Research Report: {topic}\n\nError: {str(e)}",
                "citations": [],
                "score": 0
            }
    
    async def _search(self, query: str) -> list:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": self.tavily_key,
                        "query": query,
                        "max_results": 5,
                        "search_depth": "basic"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("results", [])
                else:
                    logger.error(f"Tavily error: {response.status_code}")
                    return []
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return []
    
    async def _analyze(self, topic: str, results: list) -> str:
        try:
            formatted = "\n\n".join([
                f"Source {i+1}: {r.get('title', '')}\n{r.get('content', '')[:300]}..."
                for i, r in enumerate(results[:3])
            ])
            
            prompt = f"""Analyze these search results about "{topic}":

{formatted}

Provide: 1) Key findings 2) Main themes 3) Important facts"""

            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a research analyst. Be concise and informative."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            return "Analysis failed"
    
    async def _generate_report(self, topic: str, analysis: str, results: list) -> str:
        try:
            sources = "\n".join([
                f"[{i+1}] {r.get('title', '')} - {r.get('url', '')}"
                for i, r in enumerate(results[:3])
            ])
            
            prompt = f"""Write a detailed research report about "{topic}".

Analysis:
{analysis}

Sources:
{sources}

Write a comprehensive report with:
1. Executive Summary
2. Introduction
3. Key Findings
4. Analysis and Discussion
5. Conclusion
6. References

Make it professional, well-structured, and informative (600-800 words)."""

            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a professional research report writer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Report error: {str(e)}")
            return f"Report generation failed: {str(e)}"
    
    def _extract_citations(self, results: list) -> list:
        return [
            {"id": i+1, "title": r.get("title", "Unknown"), "url": r.get("url", "")}
            for i, r in enumerate(results[:3])
        ]
