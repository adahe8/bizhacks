from crewai import Crew
from typing import Dict, Any
import logging
from concurrent.futures import ThreadPoolExecutor
import asyncio

from core.config import settings

logger = logging.getLogger(__name__)

class CrewService:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=settings.MAX_CONCURRENT_CAMPAIGNS)
    
    async def execute_crew(self, crew: Crew, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a CrewAI crew asynchronously"""
        try:
            # Run crew execution in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                crew.kickoff,
                inputs
            )
            
            return {
                "status": "success",
                "result": result,
                "outputs": crew.output if hasattr(crew, 'output') else None
            }
            
        except Exception as e:
            logger.error(f"Error executing crew: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def shutdown(self):
        """Shutdown the executor"""
        self.executor.shutdown(wait=True)