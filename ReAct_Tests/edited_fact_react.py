import os
from langchain_openai import OpenAI
from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain.agents import AgentType, Tool, initialize_agent
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent

# Load environment variables for API keys
os.environ["OPENAI_API_KEY"] = "1234" #rubbish values
os.environ["GOOGLE_CSE_ID"] = "5678"
os.environ["GOOGLE_API_KEY"] = "9012"


# Initialize the LLM
llm = OpenAI(temperature=0, model_name="gpt-3.5-turbo-instruct") #default temp is 0.7 I believe


# Initialize Google Search API for Web Search
search = GoogleSearchAPIWrapper()

tools = [
    Tool(
        name="Search",
        func=search.run,
        description="useful for when you need to ask with search",
    )
]

# Get the prompt to use - you can modify this!
prompt = hub.pull("hwchase17/react")
print(prompt)

# Construct the ReAct agent
agent = create_react_agent(llm, tools, prompt)

# Create an agent executor by passing in the agent and tools
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

agent_executor.invoke({"input": "You are a professional factchecker with an experience of 10+ years and you MUST provide a response of 'true', 'false', or 'unclear'. Fact check the following statement- Arabic is one of Nigeria's two official languages with English."})