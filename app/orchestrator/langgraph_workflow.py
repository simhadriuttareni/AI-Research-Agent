from typing import Dict, Any, List, TypedDict
from langgraph.graph import StateGraph, END
from app.agents.planner_agent import PlannerAgent
from app.agents.researcher_agent import ResearcherAgent
from app.agents.analyst_agent import AnalystAgent
from app.agents.synthesizer_agent import SynthesizerAgent
from app.agents.editor_agent import EditorAgent
from app.agents.reviewer_agent import ReviewerAgent
from app.utils.logger import logger
import asyncio
import json

class ResearchState(TypedDict):
    """State for the research workflow."""
    topic: str
    depth: str
    plan: Dict[str, Any]
    research_results: List[Dict[str, Any]]
    analysis: Dict[str, Any]
    synthesis: Dict[str, Any]
    report: Dict[str, Any]
    review: Dict[str, Any]
    iterations: int
    max_iterations: int
    complete: bool
    error: str

class LangGraphWorkflow:
    """LangGraph orchestration for research workflow."""
    
    def __init__(self):
        self.planner = PlannerAgent()
        self.researcher = ResearcherAgent()
        self.analyst = AnalystAgent()
        self.synthesizer = SynthesizerAgent()
        self.editor = EditorAgent()
        self.reviewer = ReviewerAgent()
        
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
    
    def _build_workflow(self) -> StateGraph:
        """Build the research workflow graph."""
        workflow = StateGraph(ResearchState)
        
        # Add nodes
        workflow.add_node("plan", self._plan_research)
        workflow.add_node("research", self._conduct_research)
        workflow.add_node("analyze", self._analyze_research)
        workflow.add_node("synthesize", self._synthesize_research)
        workflow.add_node("write_report", self._write_report)
        workflow.add_node("review_report", self._review_report)
        workflow.add_node("improve_report", self._improve_report)
        
        # Add edges
        workflow.set_entry_point("plan")
        workflow.add_edge("plan", "research")
        workflow.add_edge("research", "analyze")
        workflow.add_edge("analyze", "synthesize")
        workflow.add_edge("synthesize", "write_report")
        workflow.add_edge("write_report", "review_report")
        
        # Conditional edge from review
        workflow.add_conditional_edges(
            "review_report",
            self._should_improve,
            {
                "improve": "improve_report",
                "complete": END
            }
        )
        workflow.add_edge("improve_report", "review_report")
        
        return workflow
    
    async def _plan_research(self, state: ResearchState) -> Dict[str, Any]:
        """Planning node."""
        logger.info(f"Planning research for: {state['topic']}")
        plan = await asyncio.to_thread(
            self.planner.plan,
            state['topic'],
            state.get('depth', 'standard')
        )
        return {"plan": plan}
    
    async def _conduct_research(self, state: ResearchState) -> Dict[str, Any]:
        """Research node."""
        logger.info(f"Conducting research for: {state['topic']}")
        queries = state['plan'].get('queries', [state['topic']])
        
        research_results = []
        for query in queries[:5]:  # Limit to 5 queries
            result = await self.researcher.research(query)
            research_results.append(result)
        
        return {"research_results": research_results}
    
    async def _analyze_research(self, state: ResearchState) -> Dict[str, Any]:
        """Analysis node."""
        logger.info(f"Analyzing research for: {state['topic']}")
        analysis = await self.analyst.analyze(
            state['topic'],
            state['research_results']
        )
        return {"analysis": analysis}
    
    async def _synthesize_research(self, state: ResearchState) -> Dict[str, Any]:
        """Synthesis node."""
        logger.info(f"Synthesizing research for: {state['topic']}")
        synthesis = await self.synthesizer.synthesize(
            state['topic'],
            state['analysis'],
            state['research_results']
        )
        return {"synthesis": synthesis}
    
    async def _write_report(self, state: ResearchState) -> Dict[str, Any]:
        """Report writing node."""
        logger.info(f"Writing report for: {state['topic']}")
        report = await self.editor.write_report(
            state['topic'],
            state['synthesis'],
            state['analysis'],
            state['research_results']
        )
        return {"report": report}
    
    async def _review_report(self, state: ResearchState) -> Dict[str, Any]:
        """Review node."""
        logger.info(f"Reviewing report for: {state['topic']}")
        review = await self.reviewer.review(
            state['topic'],
            state['report'].get('report', ''),
            state['analysis']
        )
        return {"review": review, "iterations": state.get('iterations', 0) + 1}
    
    async def _improve_report(self, state: ResearchState) -> Dict[str, Any]:
        """Improvement node."""
        logger.info(f"Improving report for: {state['topic']}")
        improved_report = await self.reviewer.improve_report(
            state['topic'],
            state['report'].get('report', ''),
            state['review']
        )
        
        # Update report with improved version
        report = state['report'].copy()
        report['report'] = improved_report
        return {"report": report}
    
    def _should_improve(self, state: ResearchState) -> str:
        """Determine if report needs improvement."""
        iterations = state.get('iterations', 0)
        max_iterations = state.get('max_iterations', 3)
        review = state.get('review', {})
        
        # Check if review approved or max iterations reached
        if review.get('approved', False) or iterations >= max_iterations:
            return "complete"
        return "improve"
    
    async def run(self, topic: str, depth: str = "standard", max_iterations: int = 3) -> Dict[str, Any]:
        """Run the complete research workflow."""
        try:
            logger.info(f"Starting research workflow for: {topic}")
            
            initial_state = {
                "topic": topic,
                "depth": depth,
                "max_iterations": max_iterations,
                "iterations": 0,
                "plan": {},
                "research_results": [],
                "analysis": {},
                "synthesis": {},
                "report": {},
                "review": {},
                "complete": False,
                "error": ""
            }
            
            # Run workflow
            result = await self.app.ainvoke(initial_state)
            
            # Check for errors
            if result.get('error'):
                logger.error(f"Workflow error: {result['error']}")
                return {
                    "success": False,
                    "error": result['error'],
                    "topic": topic
                }
            
            # Build final response
            final_report = result.get('report', {})
            final_report['analysis'] = result.get('analysis', {})
            final_report['review'] = result.get('review', {})
            
            return {
                "success": True,
                "topic": topic,
                "report": final_report,
                "iterations": result.get('iterations', 0),
                "completed": True
            }
            
        except Exception as e:
            logger.error(f"Workflow execution error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "topic": topic
            }