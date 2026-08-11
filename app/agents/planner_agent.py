from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from typing import Dict, Any, List
import os
from dotenv import load_dotenv
from app.utils.logger import logger
import json
import asyncio

load_dotenv()

class PlannerAgent:
    """Research planning and strategy agent."""
    
    def __init__(self):
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model=os.getenv("LLM_MODEL", "llama-3.1-70b-versatile"),
            temperature=0.1,
            max_retries=3
        )
        
        self.planning_prompt = PromptTemplate(
            input_variables=["topic", "depth"],
            template="""
            You are a Research Planning Expert. Create a comprehensive research plan for the following topic.
            
            Topic: {topic}
            Research Depth: {depth}
            
            You must provide:
            1. 3-5 specific search queries to get comprehensive coverage
            2. Key focus areas to explore
            3. Types of sources to prioritize (academic, news, industry, etc.)
            4. Potential research angles and perspectives
            
            Format your response as structured JSON:
            {{
                "queries": ["query1", "query2", ...],
                "focus_areas": ["area1", "area2", ...],
                "source_types": ["type1", "type2", ...],
                "perspectives": ["perspective1", "perspective2", ...]
            }}
            
            Ensure queries are specific, diverse, and designed to gather comprehensive information.
            """
        )
        
        self.chain = self.planning_prompt | self.llm | StrOutputParser()
    
    def plan(self, topic: str, depth: str = "standard") -> Dict[str, Any]:
        """Create a research plan for the given topic."""
        try:
            logger.info(f"Creating research plan for: {topic} (depth: {depth})")
            response = self.chain.invoke({"topic": topic, "depth": depth})
            
            # Parse JSON response
            try:
                plan = json.loads(response)
            except:
                # Fallback: extract from text
                plan = self._extract_plan_from_text(response)
            
            logger.info(f"Research plan created: {len(plan.get('queries', []))} queries")
            return plan
            
        except Exception as e:
            logger.error(f"Planning error: {str(e)}")
            # Return a default plan
            return {
                "queries": [topic, f"{topic} latest", f"{topic} trends", f"{topic} research"],
                "focus_areas": ["Overview", "Key developments", "Current state"],
                "source_types": ["Academic", "News", "Industry"],
                "perspectives": ["Technical", "Business", "Social"]
            }
    
    def _extract_plan_from_text(self, text: str) -> Dict[str, Any]:
        """Extract plan from text response if JSON parsing fails."""
        lines = text.strip().split('\n')
        plan = {
            "queries": [],
            "focus_areas": [],
            "source_types": [],
            "perspectives": []
        }
        
        current_key = None
        for line in lines:
            line = line.strip()
            if 'queries' in line.lower():
                current_key = 'queries'
            elif 'focus' in line.lower():
                current_key = 'focus_areas'
            elif 'source' in line.lower():
                current_key = 'source_types'
            elif 'perspective' in line.lower():
                current_key = 'perspectives'
            elif line.startswith('-') or line.startswith('*') or line.startswith('"'):
                if current_key and line:
                    item = line.strip('-* "\'')
                    if item:
                        plan[current_key].append(item)
        
        return plan