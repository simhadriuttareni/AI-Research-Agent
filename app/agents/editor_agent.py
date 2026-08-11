from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from typing import List, Dict, Any
import os
from app.utils.logger import logger
from datetime import datetime

class EditorAgent:
    """Report generation and editing agent."""
    
    def __init__(self):
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model=os.getenv("LLM_MODEL", "llama3-70b-8192"),
            temperature=0.2
        )
        
        self.report_prompt = PromptTemplate(
            input_variables=["topic", "synthesis", "analysis", "research_data"],
            template="""
            You are a Professional Research Report Writer. Create a comprehensive, well-structured research report.
            
            Topic: {topic}
            
            Synthesis Results:
            {synthesis}
            
            Analysis Results:
            {analysis}
            
            Research Data:
            {research_data}
            
            Write a detailed research report that includes:
            1. Executive Summary (150-200 words)
            2. Introduction to the topic
            3. Key Findings (with supporting evidence)
            4. Analysis and Discussion
            5. Conclusions and Implications
            6. References/Citations
            
            Format the report with clear sections and proper citations.
            The report should be 1000-1500 words, well-organized, and professional.
            
            Include in-text citations like [1], [2] etc. and a references section at the end.
            """
        )
        
        self.chain = self.report_prompt | self.llm | StrOutputParser()
    
    async def write_report(self, topic: str, synthesis: Dict, analysis: Dict, research_data: List[Dict]) -> Dict[str, Any]:
        """Write a comprehensive research report."""
        try:
            logger.info(f"Writing report for: {topic}")
            
            # Format data for the report
            formatted_synthesis = self._format_synthesis(synthesis)
            formatted_analysis = self._format_analysis(analysis)
            formatted_data = self._format_research_data(research_data)
            
            report = await self._invoke_chain(topic, formatted_synthesis, formatted_analysis, formatted_data)
            
            # Extract citations
            citations = self._extract_citations(report)
            
            return {
                "report": report,
                "citations": citations,
                "word_count": len(report.split()),
                "sections": self._extract_sections(report),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Report writing error: {str(e)}")
            return {
                "report": f"Error writing report: {str(e)}",
                "citations": [],
                "word_count": 0,
                "sections": [],
                "timestamp": datetime.now().isoformat()
            }
    
    async def _invoke_chain(self, topic: str, synthesis: str, analysis: str, data: str) -> str:
        """Invoke chain asynchronously."""
        return await asyncio.to_thread(
            self.chain.invoke,
            {
                "topic": topic,
                "synthesis": synthesis,
                "analysis": analysis,
                "research_data": data
            }
        )
    
    def _format_synthesis(self, synthesis: Dict) -> str:
        """Format synthesis for prompt."""
        lines = [
            f"Unified Understanding: {synthesis.get('unified_understanding', '')}",
            f"Key Conclusions: {', '.join(synthesis.get('key_conclusions', []))}",
            f"Connections: {', '.join(synthesis.get('connections', []))}"
        ]
        return "\n".join(lines)
    
    def _format_analysis(self, analysis: Dict) -> str:
        """Format analysis for prompt."""
        lines = [
            f"Key Insights: {', '.join(analysis.get('key_insights', []))}",
            f"Patterns: {', '.join(analysis.get('patterns', []))}",
            f"Credibility Score: {analysis.get('credibility_score', 0)}"
        ]
        return "\n".join(lines)
    
    def _format_research_data(self, data: List[Dict]) -> str:
        """Format research data for prompt."""
        formatted = []
        for i, item in enumerate(data[:10], 1):
            formatted.append(
                f"Query {i}: {item.get('query', '')}\n"
                f"Summary: {item.get('summary', '')}\n"
                f"Sources: {len(item.get('sources', []))} sources"
            )
        return "\n\n".join(formatted)
    
    def _extract_citations(self, report: str) -> List[Dict]:
        """Extract citations from report."""
        citations = []
        lines = report.split('\n')
        in_references = False
        
        for line in lines:
            if 'references' in line.lower() or 'citations' in line.lower():
                in_references = True
                continue
            if in_references and line.strip() and (line.strip().startswith('[') or line.strip().startswith('')):
                citations.append({"text": line.strip()})
        
        return citations
    
    def _extract_sections(self, report: str) -> List[Dict]:
        """Extract sections from report."""
        sections = []
        current_section = {"title": "", "content": ""}
        
        for line in report.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check if line is a section header
            if any(header in line.lower() for header in ['executive summary', 'introduction', 'findings', 'analysis', 'conclusion']):
                if current_section["title"] or current_section["content"]:
                    sections.append(current_section)
                    current_section = {"title": "", "content": ""}
                current_section["title"] = line
            else:
                if current_section["title"]:
                    current_section["content"] += line + " "
        
        if current_section["title"] or current_section["content"]:
            sections.append(current_section)
        
        return sections