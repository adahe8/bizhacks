# backend/agents/compliance_agent.py
from crewai import Agent
from langchain_openai import ChatOpenAI

class ComplianceAgent:
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.2,
            api_key=api_key
        )
        
        self.agent = Agent(
            role="Brand Compliance Officer",
            goal="Ensure all content adheres to brand guidelines and legal requirements",
            backstory="""You are a meticulous brand guardian who ensures all marketing 
            content meets brand standards, legal requirements, and ethical guidelines. 
            You have a keen eye for detail and never let substandard content through.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
