import os
import logging

from langchain.document_loaders import PyPDFLoader 
from langchain.embeddings import OpenAIEmbeddings 
from langchain.vectorstores import Chroma 
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI
from langchain.document_loaders.csv_loader import CSVLoader 

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import __version__ as TG_VER

from dotenv import load_dotenv,find_dotenv

load_dotenv(find_dotenv())

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

global qa       #: ConversationalRetrievalChain
global history

def loadPDFFileAndSaveToVectorDB():
    pdf_path = "./MEDIAStrial.pdf"
    loader = PyPDFLoader(pdf_path)

    pages = loader.load_and_split()

    embeddings = OpenAIEmbeddings()
    vectordb = Chroma.from_documents(pages, embedding=embeddings, 
                                    persist_directory="./MEDIAStrial")
    vectordb.persist()
    return vectordb


def loadCSVFileAndSaveToVectorDB():
    
    loader = CSVLoader(file_path="../unibot/Reporte Contratos y Facturas Pendientes Chatbot.csv", 
                   encoding="utf-8", 
                   csv_args={'delimiter': ',', 
                             'quotechar':'"',
                             })

    pages = loader.load_and_split()

    embeddings = OpenAIEmbeddings()
    vectordb = Chroma.from_documents(pages, embedding=embeddings, 
                                    persist_directory="./unifier1")
    vectordb.persist()
    return vectordb


def retrieveConversationalChain(vector): 
    qa = ConversationalRetrievalChain.from_llm(
                OpenAI(temperature=0),
                vector.as_retriever(),
                return_source_documents=True)
    return qa

def askAndReturnTheQuestionAndHistory(question, history): 
    result = qa({"question": question, "chat_history": history})
    history = [(question, result["answer"])]
    print(history)
    return result["answer"]

 

 
async def answerTheQuestion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    answr = askAndReturnTheQuestionAndHistory(update.message.text, history)
    await update.message.reply_text(answr)

 

v = loadCSVFileAndSaveToVectorDB()
qa = retrieveConversationalChain(v)
history = []

def main() -> None:

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.getenv('TELEGRAM_API_KEY_MTCUNIFIERBOT2')).build()
    
    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answerTheQuestion))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

 

if __name__ == "__main__":
    main()