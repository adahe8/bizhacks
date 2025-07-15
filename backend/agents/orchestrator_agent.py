# backend/agents/orchestrator_agent.py
from crewai import Agent
from langchain_openai import ChatOpenAI

class OrchestratorAgent:
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.3,
            api_key=api_key
        )
        
        self.agent = Agent(
            role="Budget Optimization Specialist",
            goal="Optimize budget allocation across campaigns based on performance",
            backstory="""You are a data-driven marketing analyst specializing in budget 
            optimization. You use performance metrics to make informed decisions about 
            resource allocation to maximize ROI.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
