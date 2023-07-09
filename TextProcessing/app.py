from dotenv import load_dotenv
import os
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryMemory
from langchain.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain.utilities import WikipediaAPIWrapper, SerpAPIWrapper, DuckDuckGoSearchAPIWrapper
from langchain.memory.chat_message_histories import FirestoreChatMessageHistory
from langchain.agents import initialize_agent, Tool, AgentType, load_tools
from langchain.chains.llm_math.base import LLMMathChain

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# llms
llm = OpenAI(temperature=0.9)

# custom template
template = """The following is a friendly conversation between a human and an AI. The name of the AI is IntelliTutor. The AI is talkative and provides lots of specific details from its context. AI is a personalized tutor and helps in educations, serves as a teacher. The AI always assumes its senior and tries to provide the most accurate and trusted information. If the AI does not know the answer to a question, it truthfully says it does not know. When you write code, wrap the entire code with three back-ticks (```), and after the first three back-tick specify the extension of the lanuage. 
for example: 
    ```py
    print('hello world')
    ```
Current conversation:
{history}
Human: {input}
IntelliTutor:"""
PROMPT = PromptTemplate(input_variables=["history", "input"], template=template)


#  tools
search = DuckDuckGoSearchAPIWrapper()
wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=2000))

tools = [
    Tool(
        name = "Current Search",
        func=search.run,
        description="useful for when you need to answer questions about current events or the current state of the world"
    ),
    Tool(
        name = "Wikipedia Search",
        func=wikipedia.run,
        description="useful for when you need to answer accurate answer for academic questions from wikipedia"
    ),
    Tool(
        name="Calculator",
        description="Useful for when you need to answer questions about math.",
        func=LLMMathChain.from_llm(llm=llm).run,
        coroutine=LLMMathChain.from_llm(llm=llm).arun,
    )
]

class CustomAgent:
    def __init__(self):
        self.memory = ConversationSummaryMemory(
            llm=llm, max_token_limit=20, ai_prefix="IntelliTutor", return_messages=True, memory_key="chat_history"
        )
        message_history = FirestoreChatMessageHistory("users", '2021', '2021')
        self.memory = ConversationSummaryMemory.from_messages(
                    llm=llm,
                    max_token_limit=50,
                    ai_prefix="IntelliTutor",
                    chat_memory=message_history,
                    memory_key="chat_history",
                    return_messages=True
                )
        self.agent_chain = initialize_agent(tools, llm, agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION, verbose=True, memory=self.memory)

    def respond(self, prompt, uid):
        response = self.agent_chain.run(input=prompt)
        return response
    
    def wikipedia_search(self, topic):
        response = wikipedia.run(topic)
        return response