import os
import logging

from dotenv import load_dotenv,find_dotenv

import langchain
from langchain.document_loaders import PyPDFLoader 
from langchain.embeddings import OpenAIEmbeddings 
from langchain.vectorstores import Chroma 
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import __version__ as TG_VER

from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain.agents import create_csv_agent, Tool, load_tools

from telegram import __version_info__

import pandas as pd


langchain.debug = False

load_dotenv(find_dotenv())

csv_memory = ConversationBufferMemory(return_messages=True)

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)
 
 

def returnLangChainAgent():
    llm=ChatOpenAI(temperature=0,model='gpt-4-0314')
    tools = load_tools(["python_repl"])

    return  create_csv_agent(
                llm=llm,
                path="../unibot/Report (2).csv",
                verbose=True,
                agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION, #ZERO_SHOT_REACT_DESCRIPTION,
                memory=csv_memory,
                tool=tools,
                handle_parsing_errors="Check your output and make sure it conforms!",
                 
            )
    
def answerTheQuestionFromConversationalChain(conversation, question): 
    try:
        answer = conversation.run(input=question)   
    except Exception as e: 
    #   print("eliminando el caracter ... ")
        answer = str(e)
    #    if answer.startswith("Could not parse LLM output: `"): 
    #       answer = answer.removeprefix("Could not parse LLM output: `").removesuffix("`")            
    return answer



conversationalAgent = returnLangChainAgent()


async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    respuesta = answerTheQuestionFromConversationalChain(conversationalAgent, update.message.text)

    await update.message.reply_text(respuesta)


def main() -> None:
    
    app = Application.builder().token(os.getenv('TELEGRAM_API_KEY_MTCUNIFIERBOT')).build()

 
    # on non command i.e message - echo the message on Telegram
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))

    # Run the bot until the user presses Ctrl-C 
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()