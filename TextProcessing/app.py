from dotenv import load_dotenv
import os
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryMemory
from langchain.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain.utilities import WikipediaAPIWrapper
from langchain.memory.chat_message_histories import FirestoreChatMessageHistory

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

wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(top_k_results=1))


class Responder:
    def __init__(self):
        self.memory = ConversationSummaryMemory(
            llm=llm, max_token_limit=20, ai_prefix="IntelliTutor", return_messages=True
        )
        self.conversation = ConversationChain(
            prompt=PROMPT, llm=llm, verbose=True, memory=self.memory,
        )

    def respond(self, prompt, uid):
        message_history = FirestoreChatMessageHistory("users", uid, uid)
        # print(message_history)
        self.memory = ConversationSummaryMemory.from_messages(
            llm=llm,
            max_token_limit=20,
            ai_prefix="IntelliTutor",
            chat_memory=message_history,
            return_messages=True
        )
        self.conversation = ConversationChain(
            prompt=PROMPT, llm=llm, verbose=True, memory=self.memory,
        )
        response = self.conversation.predict(input=prompt)
        return response


def wikipedia_search(topic):
    response = wikipedia.run(topic)
    return response
