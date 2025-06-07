from dotenv import load_dotenv
import os

from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun

# Load environment variables
load_dotenv()
base_url = os.getenv("NVIDIA_API_BASE_URL")
api_key  = os.getenv("NVIDIA_API_KEY")
model    = os.getenv("NVIDIA_API_MODEL")

# Initialize the NVIDIA LLM
llm = ChatOpenAI(
    base_url   = base_url,
    api_key    = api_key,
    model_name = model,
    streaming  = True,
    temperature= 0.5,
    max_tokens = 1024,
)

# Initialize the DuckDuckGo search tool
search_tool = DuckDuckGoSearchRun()

# Define the tool for the agent
tools = [
    Tool(
        name        = "web_search",
        func        = search_tool.run,
        description = (
            "Useful for searching the web for current facts, news, or URLs. "
            "Takes a query string and returns the top results."
        ),
    )
]

# Initialize the agent with the tool
agent = initialize_agent(
    tools      = tools,
    llm        = llm,
    agent      = AgentType.OPENAI_FUNCTIONS,
    verbose    = True,
)

# Run the agent with a sample query
response = agent.run("Who is the current RBI governor and what was his last public speech about?")
print(response)
