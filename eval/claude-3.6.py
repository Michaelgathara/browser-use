from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

from browser_use import Agent, Browser

load_dotenv()


async def run_agent(task: str, browser: Browser | None = None, max_steps: int = 38):
	browser = browser or Browser()
	llm = ChatAnthropic(
		model_name='claude-3-5-sonnet-20241022',
		temperature=0.0,
		timeout=100,
		stop=None,
	)
	agent = Agent(task=task, llm=llm, browser=browser)
	result = await agent.run(max_steps=max_steps)
	return result
