from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from typing import Dict, Any, List
import os
from app.utils.logger import logger

class ReviewerAgent:
    """Self-correction and quality control agent."""
    
    def __init__(self):
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model=os.getenv("LLM_MODEL", "llama3-70b-8192"),
            temperature=0.1
        )
        
        self.review_prompt = PromptTemplate(
            input_variables=["topic", "report", "analysis"],
            template="""
            You are a Critical Reviewer. Evaluate the following research report for quality and accuracy.
            
            Topic: {topic}
            
            Report to Review:
            {report}
            
            Analysis Results:
            {analysis}
            
            Evaluate the report on:
            1. Accuracy of facts (0-100)
            2. Completeness of coverage
            3. Quality of reasoning
            4. Proper use of citations
            5. Overall quality (0-100)
            
            Provide specific feedback:
            1. What's good about the report?
            2. What needs improvement?
            3. Are there any factual errors or hallucinations?
            4. How can the report be improved?
            
            Format response as JSON:
            {{
                "score": 85,
                "accuracy_score": 90,
                "completeness_score": 85,
                "reasoning_score": 80,
                "citation_score": 90,
                "strengths": ["strength1", "strength2"],
                "weaknesses": ["weakness1", "weakness2"],
                "errors": ["error1", "error2"],
                "improvements": ["improvement1", "improvement2"],
                "approved": true
            }}
            """
        )
        
        self.chain = self.review_prompt | self.llm | StrOutputParser()
    
    async def review(self, topic: str, report: str, analysis: Dict) -> Dict[str, Any]:
        """Review and score the research report."""
        try:
            logger.info(f"Reviewing report for: {topic}")
            
            formatted_analysis = self._format_analysis(analysis)
            response = await self._invoke_chain(topic, report, formatted_analysis)
            
            import json
            try:
                review = json.loads(response)
            except:
                review = self._extract_review_from_text(response)
            
            # Apply threshold for approval
            threshold = 70
            review["approved"] = review.get("score", 0) >= threshold
            
            logger.info(f"Review complete: Score {review.get('score', 0)}")
            return review
            
        except Exception as e:
            logger.error(f"Review error: {str(e)}")
            return {
                "score": 0,
                "accuracy_score": 0,
                "completeness_score": 0,
                "reasoning_score": 0,
                "citation_score": 0,
                "strengths": [],
                "weaknesses": [],
                "errors": [str(e)],
                "improvements": [],
                "approved": False
            }
    
    async def _invoke_chain(self, topic: str, report: str, analysis: str) -> str:
        """Invoke chain asynchronously."""
        return await asyncio.to_thread(
            self.chain.invoke,
            {"topic": topic, "report": report, "analysis": analysis}
        )
    
    def _format_analysis(self, analysis: Dict) -> str:
        """Format analysis for prompt."""
        return f"Key Insights: {', '.join(analysis.get('key_insights', []))}\nCredibility: {analysis.get('credibility_score', 0)}"
    
    def _extract_review_from_text(self, text: str) -> Dict:
        """Extract review from text response."""
        lines = text.strip().split('\n')
        review = {
            "score": 70,
            "accuracy_score": 70,
            "completeness_score": 70,
            "reasoning_score": 70,
            "citation_score": 70,
            "strengths": [],
            "weaknesses": [],
            "errors": [],
            "improvements": [],
            "approved": False
        }
        
        for line in lines:
            line = line.strip()
            if 'score' in line.lower():
                try:
                    # Try to extract number
                    import re
                    numbers = re.findall(r'\d+', line)
                    if numbers:
                        review["score"] = int(numbers[0])
                except:
                    pass
            elif 'strength' in line.lower() and (line.startswith('-') or line.startswith('*')):
                review["strengths"].append(line.strip('-* '))
            elif 'weakness' in line.lower() and (line.startswith('-') or line.startswith('*')):
                review["weaknesses"].append(line.strip('-* '))
            elif 'error' in line.lower() and (line.startswith('-') or line.startswith('*')):
                review["errors"].append(line.strip('-* '))
            elif 'improvement' in line.lower() and (line.startswith('-') or line.startswith('*')):
                review["improvements"].append(line.strip('-* '))
        
        review["approved"] = review["score"] >= 70
        return review
    
    async def improve_report(self, topic: str, report: str, review: Dict) -> str:
        """Improve report based on review feedback."""
        try:
            logger.info("Improving report based on review")
            
            improve_prompt = PromptTemplate(
                input_variables=["topic", "report", "review"],
                template="""
                You are a Report Editor. Improve the following report based on the review feedback.
                
                Topic: {topic}
                
                Original Report:
                {report}
                
                Review Feedback:
                {review}
                
                Please revise the report to address the weaknesses and errors identified.
                Maintain the overall structure and citations while making improvements.
                """
            )
            
            chain = improve_prompt | self.llm | StrOutputParser()
            
            formatted_review = self._format_review_feedback(review)
            improved = await asyncio.to_thread(
                chain.invoke,
                {"topic": topic, "report": report, "review": formatted_review}
            )
            
            logger.info("Report improved successfully")
            return improved
            
        except Exception as e:
            logger.error(f"Report improvement error: {str(e)}")
            return report
    
    def _format_review_feedback(self, review: Dict) -> str:
        """Format review feedback for improvement."""
        lines = [
            f"Score: {review.get('score', 0)}",
            f"Weaknesses: {', '.join(review.get('weaknesses', []))}",
            f"Errors: {', '.join(review.get('errors', []))}",
            f"Improvements suggested: {', '.join(review.get('improvements', []))}"
        ]
        return "\n".join(lines)