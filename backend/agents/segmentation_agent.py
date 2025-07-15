# backend/agents/segmentation_agent.py
from crewai import Agent
from langchain_openai import ChatOpenAI

class SegmentationAgent:
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=api_key
        )
        
        self.agent = Agent(
            role="Customer Segmentation Specialist",
            goal="Identify and define distinct customer segments based on data analysis",
            backstory="""You are an expert in customer analytics and market segmentation. 
            You excel at finding patterns in customer data and creating actionable segments 
            that drive marketing success.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )