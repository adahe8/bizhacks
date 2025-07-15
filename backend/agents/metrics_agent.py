# backend/agents/metrics_agent.py
from crewai import Agent
from langchain_openai import ChatOpenAI

class MetricsGatherAgent:
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.3,
            api_key=api_key
        )
        
        self.agent = Agent(
            role="Analytics and Metrics Specialist",
            goal="Gather and analyze campaign performance metrics across all channels",
            backstory="""You are a data analyst specializing in marketing metrics. 
            You know how to collect, process, and interpret data from various marketing 
            channels to provide actionable insights.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )