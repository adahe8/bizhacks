# backend/agents/execution_agent.py
from crewai import Agent
from langchain_openai import ChatOpenAI

class CampaignExecutionAgent:
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.3,
            api_key=api_key
        )
        
        self.agent = Agent(
            role="Campaign Execution Manager",
            goal="Execute approved campaigns across all channels efficiently",
            backstory="""You are a campaign execution specialist who ensures all approved 
            content is published correctly across channels. You manage timing, formatting, 
            and technical requirements for each platform.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )