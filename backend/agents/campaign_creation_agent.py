# backend/agents/campaign_creation_agent.py
from crewai import Agent
from langchain_openai import ChatOpenAI

class CampaignCreationAgent:
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.8,
            api_key=api_key
        )
        
        self.agent = Agent(
            role="Creative Campaign Strategist",
            goal="Develop innovative and effective marketing campaign ideas",
            backstory="""You are a creative marketing strategist with years of experience 
            in omnichannel campaigns. You understand how to craft compelling messages 
            that resonate with specific customer segments across different platforms.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )