from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from typing import List, Dict, Any
import os
from app.utils.logger import logger
import networkx as nx
import json

class SynthesizerAgent:
    """Knowledge graph builder and research synthesizer."""
    
    def __init__(self):
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model=os.getenv("LLM_MODEL", "llama3-70b-8192"),
            temperature=0.1
        )
        
        self.synthesis_prompt = PromptTemplate(
            input_variables=["topic", "analysis", "research_data"],
            template="""
            You are a Research Synthesizer. Create a coherent knowledge synthesis from all research.
            
            Topic: {topic}
            
            Analysis Results:
            {analysis}
            
            Research Data:
            {research_data}
            
            Synthesize all information into:
            1. A unified understanding of the topic
            2. Key conclusions and takeaways
            3. Connections between different pieces of information
            4. Recommendations for further research
            
            Format your response as structured JSON:
            {{
                "unified_understanding": "Comprehensive synthesis text",
                "key_conclusions": ["conclusion1", "conclusion2", ...],
                "connections": ["connection1", "connection2", ...],
                "recommendations": ["recommendation1", "recommendation2", ...],
                "knowledge_graph": {{
                    "nodes": ["node1", "node2", ...],
                    "edges": [["node1", "node2", "relationship"], ...]
                }}
            }}
            """
        )
        
        self.chain = self.synthesis_prompt | self.llm | StrOutputParser()
    
    async def synthesize(self, topic: str, analysis: Dict, research_data: List[Dict]) -> Dict[str, Any]:
        """Synthesize research into knowledge."""
        try:
            logger.info(f"Synthesizing research for: {topic}")
            
            # Format data for synthesis
            formatted_analysis = json.dumps(analysis, indent=2)
            formatted_data = json.dumps([
                {"query": r.get("query", ""), "summary": r.get("summary", "")}
                for r in research_data
            ], indent=2)
            
            response = await self._invoke_chain(topic, formatted_analysis, formatted_data)
            
            import json
            try:
                synthesis = json.loads(response)
            except:
                synthesis = self._extract_synthesis_from_text(response)
            
            # Build knowledge graph
            if "knowledge_graph" not in synthesis:
                synthesis["knowledge_graph"] = self._build_knowledge_graph(
                    topic, analysis, research_data
                )
            
            logger.info(f"Synthesis complete: {len(synthesis.get('key_conclusions', []))} conclusions")
            return synthesis
            
        except Exception as e:
            logger.error(f"Synthesis error: {str(e)}")
            return {
                "unified_understanding": f"Error synthesizing research: {str(e)}",
                "key_conclusions": [],
                "connections": [],
                "recommendations": [],
                "knowledge_graph": {"nodes": [], "edges": []}
            }
    
    async def _invoke_chain(self, topic: str, analysis: str, data: str) -> str:
        """Invoke chain asynchronously."""
        return await asyncio.to_thread(
            self.chain.invoke,
            {"topic": topic, "analysis": analysis, "research_data": data}
        )
    
    def _extract_synthesis_from_text(self, text: str) -> Dict:
        """Extract synthesis from text response."""
        lines = text.strip().split('\n')
        synthesis = {
            "unified_understanding": "",
            "key_conclusions": [],
            "connections": [],
            "recommendations": [],
            "knowledge_graph": {"nodes": [], "edges": []}
        }
        
        current_section = None
        for line in lines:
            line = line.strip()
            if 'understanding' in line.lower():
                current_section = 'unified_understanding'
            elif 'conclusion' in line.lower():
                current_section = 'key_conclusions'
            elif 'connection' in line.lower():
                current_section = 'connections'
            elif 'recommendation' in line.lower():
                current_section = 'recommendations'
            elif line.startswith('-') or line.startswith('*') or line.startswith('"'):
                if current_section and line:
                    item = line.strip('-* "\'')
                    if item:
                        if current_section == 'unified_understanding':
                            synthesis[current_section] += " " + item
                        else:
                            synthesis[current_section].append(item)
        
        return synthesis
    
    def _build_knowledge_graph(self, topic: str, analysis: Dict, research_data: List[Dict]) -> Dict:
        """Build a knowledge graph from research data."""
        try:
            G = nx.Graph()
            G.add_node(topic)
            
            # Add nodes from analysis
            for insight in analysis.get('key_insights', [])[:10]:
                G.add_node(insight[:50])  # Truncate for readability
                G.add_edge(topic, insight[:50])
            
            # Add nodes from research data
            for data in research_data[:10]:
                if data.get('query'):
                    G.add_node(data['query'][:50])
                    G.add_edge(topic, data['query'][:50])
            
            # Convert to JSON-friendly format
            return {
                "nodes": list(G.nodes()),
                "edges": [[u, v] for u, v in G.edges()]
            }
        except Exception as e:
            logger.error(f"Knowledge graph build error: {str(e)}")
            return {"nodes": [], "edges": []}