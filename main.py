# pip install -qU "langchain[anthropic]" to call the model
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from dotenv import load_dotenv,find_dotenv

#api de openAI y modelo
api_key=""
modelo = "gpt-4.1-nano"

# Carga .env
load_dotenv()

#Modelo a usar
model = ChatOpenAI(api_key = api_key,model = modelo)

#              #
# Herramientas #
#              #

# Cargar PDF y guarda la data en una BDD vectorial
def loadFileAndSaveToVectorDB():
    pdf_path = "MEDIAStrial.pdf"
    loader = PyPDFLoader(pdf_path)

    pages = loader.load_and_split()

    embeddings = OpenAIEmbeddings()

    # Se crea una base de datos Chroma con todos los datos del PDF
    vectordb = Chroma.from_documents(pages, embedding=embeddings, 
                                    persist_directory="./MEDIAStrial")
    vectordb.persist() # Se guarda la BDD
    return vectordb

#                    #
# Ejecucion programa #
#                    # 

# Carga PDF y crea BDD vectorial
vector_db = loadFileAndSaveToVectorDB()

# cadena de conversacion
qa = ConversationalRetrievalChain.from_llm(
            llm=model,
            retriever=vector_db.as_retriever(),
            return_source_documents=True)

pregunta = input("Ingresa pregunta del PDF:")
chat_history = []

result = qa({"question": pregunta, "chat_history": chat_history})

print("\nRespuesta:")
print(result['answer'])