# backend/agents/content_agents.py
from crewai import Agent
from langchain_openai import ChatOpenAI

class EmailContentAgent:
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=api_key
        )
        
        self.agent = Agent(
            role="Email Marketing Specialist",
            goal="Create compelling email content that drives engagement and conversions",
            backstory="""You are an email marketing expert who understands how to craft 
            subject lines that get opened and content that converts. You know the best 
            practices for email design, personalization, and CTA placement.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

class FacebookContentAgent:
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.8,
            api_key=api_key
        )
        
        self.agent = Agent(
            role="Social Media Content Creator",
            goal="Create engaging Facebook posts that generate likes, shares, and conversions",
            backstory="""You are a social media expert specializing in Facebook marketing. 
            You understand the platform's algorithm, best posting times, and how to create 
            content that sparks engagement and drives results.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

class GoogleAdsContentAgent:
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.5,
            api_key=api_key
        )
        
        self.agent = Agent(
            role="Google Ads Specialist",
            goal="Create high-converting Google Ads copy that maximizes CTR and quality score",
            backstory="""You are a Google Ads expert who knows how to write compelling 
            ad copy within character limits. You understand keyword relevance, quality 
            scores, and how to create ads that convert.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )