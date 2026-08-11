from crewai import Agent, Task, Crew
from typing import List, Dict, Any
from app.agents.researcher_agent import ResearcherAgent
from app.agents.analyst_agent import AnalystAgent
from app.agents.editor_agent import EditorAgent
from app.utils.logger import logger

class CrewSetup:
    """Setup and coordinate CrewAI agents."""
    
    def __init__(self):
        self.researcher = ResearcherAgent()
        self.analyst = AnalystAgent()
        self.editor = EditorAgent()
    
    async def run_research_crew(self, topic: str, queries: List[str]) -> Dict[str, Any]:
        """Run the research crew for a topic."""
        try:
            logger.info(f"Starting research crew for: {topic}")
            
            # Run research tasks
            research_results = []
            for query in queries:
                result = await self.researcher.research(query)
                research_results.append(result)
            
            # Analyze results
            analysis = await self.analyst.analyze(topic, research_results)
            
            # Write report
            report_data = await self.editor.write_report(
                topic,
                {"unified_understanding": "Synthesized from research"},
                analysis,
                research_results
            )
            
            return {
                "research_results": research_results,
                "analysis": analysis,
                "report": report_data
            }
            
        except Exception as e:
            logger.error(f"Crew execution error: {str(e)}")
            raise
    
    def create_crew(self, topic: str) -> Crew:
        """Create a CrewAI crew for research."""
        # Define agents
        researcher_agent = Agent(
            role="Researcher",
            goal=f"Gather comprehensive information about {topic}",
            backstory="Expert researcher with access to multiple search tools",
            allow_delegation=False,
            verbose=True
        )
        
        analyst_agent = Agent(
            role="Analyst",
            goal=f"Analyze and extract insights from research about {topic}",
            backstory="Data analyst expert at finding patterns and insights",
            allow_delegation=False,
            verbose=True
        )
        
        editor_agent = Agent(
            role="Editor",
            goal=f"Write a comprehensive research report about {topic}",
            backstory="Professional editor and writer",
            allow_delegation=False,
            verbose=True
        )
        
        # Define tasks
        research_task = Task(
            description=f"Research {topic} and gather information",
            agent=researcher_agent,
            expected_output="Research findings with sources"
        )
        
        analysis_task = Task(
            description=f"Analyze research findings for {topic}",
            agent=analyst_agent,
            expected_output="Analysis with insights and patterns",
            context=[research_task]
        )
        
        report_task = Task(
            description=f"Write final research report for {topic}",
            agent=editor_agent,
            expected_output="Professional research report",
            context=[research_task, analysis_task]
        )
        
        # Create crew
        crew = Crew(
            agents=[researcher_agent, analyst_agent, editor_agent],
            tasks=[research_task, analysis_task, report_task],
            verbose=2
        )
        
        return crew