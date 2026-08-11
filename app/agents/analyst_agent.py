from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from typing import List, Dict, Any
import os
from app.utils.logger import logger

class AnalystAgent:
    """Quality assurance and insight extraction agent."""
    
    def __init__(self):
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model=os.getenv("LLM_MODEL", "llama3-70b-8192"),
            temperature=0.1
        )
        
        self.analysis_prompt = PromptTemplate(
            input_variables=["topic", "research_data"],
            template="""
            You are a Research Analyst. Analyze the following research data and provide deep insights.
            
            Topic: {topic}
            
            Research Data:
            {research_data}
            
            Provide a comprehensive analysis including:
            1. Key insights and main findings
            2. Patterns and trends observed
            3. Any contradictions or conflicting information
            4. Credibility assessment of sources
            5. Gaps in the research
            
            Format your response as structured JSON:
            {{
                "key_insights": ["insight1", "insight2", ...],
                "patterns": ["pattern1", "pattern2", ...],
                "contradictions": [{{"point": "...", "sources": ["source1", "source2"]}}],
                "credibility_score": 0.85,
                "confidence_level": 0.80,
                "research_gaps": ["gap1", "gap2", ...]
            }}
            """
        )
        
        self.chain = self.analysis_prompt | self.llm | StrOutputParser()
    
    async def analyze(self, topic: str, research_data: List[Dict]) -> Dict[str, Any]:
        """Analyze research data."""
        try:
            logger.info(f"Analyzing research data for: {topic}")
            
            # Format research data
            formatted_data = "\n\n".join([
                f"Source: {r.get('query', 'Unknown')}\nSummary: {r.get('summary', '')}\nFindings: {r.get('findings', [])}"
                for r in research_data
            ])
            
            response = await self._invoke_chain(topic, formatted_data)
            
            import json
            try:
                analysis = json.loads(response)
            except:
                analysis = self._extract_analysis_from_text(response)
            
            logger.info(f"Analysis complete: {len(analysis.get('key_insights', []))} insights")
            return analysis
            
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            return {
                "key_insights": ["Analysis failed"],
                "patterns": [],
                "contradictions": [],
                "credibility_score": 0.5,
                "confidence_level": 0.5,
                "research_gaps": []
            }
    
    async def _invoke_chain(self, topic: str, data: str) -> str:
        """Invoke the chain asynchronously."""
        return await asyncio.to_thread(
            self.chain.invoke,
            {"topic": topic, "research_data": data}
        )
    
    def _extract_analysis_from_text(self, text: str) -> Dict:
        """Extract analysis from text response."""
        lines = text.strip().split('\n')
        analysis = {
            "key_insights": [],
            "patterns": [],
            "contradictions": [],
            "credibility_score": 0.7,
            "confidence_level": 0.7,
            "research_gaps": []
        }
        
        current_key = None
        for line in lines:
            line = line.strip()
            if 'insight' in line.lower() or 'finding' in line.lower():
                current_key = 'key_insights'
            elif 'pattern' in line.lower():
                current_key = 'patterns'
            elif 'contradiction' in line.lower():
                current_key = 'contradictions'
            elif 'gap' in line.lower():
                current_key = 'research_gaps'
            elif line.startswith('-') or line.startswith('*') or line.startswith('"'):
                if current_key and line:
                    item = line.strip('-* "\'')
                    if item:
                        analysis[current_key].append(item)
        
        return analysis