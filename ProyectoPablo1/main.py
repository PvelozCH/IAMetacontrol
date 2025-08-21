# pip install -qU "langchain[anthropic]" to call the model
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from dotenv import load_dotenv,find_dotenv

import pycurl
import requests
import os

# Carga .env
load_dotenv()

#api de openAI y modelo

# Necesita archivo .env en donde esta el valor de la API 
api_key = os.getenv("OPENAI_API_KEY")
modelo = "gpt-4.1-nano"

#Modelo a usar
model = ChatOpenAI(api_key = api_key,model = modelo)

#                 #
# Metodos Unifier #
#                 #

# Trae Token de Unifier
def getTokenUnifier():
    token = ""
    data = ""
    url = os.getenv("tokenUrlUNIFIER")
    username = os.getenv("UserUNIFIER")
    password = os.getenv("PasswordUNIFIER")

    response = requests.get(url, auth=(username,password))

    if response.status_code == 200:
        data = response.json()
        token = data['token']
    else:
        print("ERROR",response.status_code,response.text)
    
    return token
# Carga reporte y devuelve el json
def loadReportUnifier(token):
    data =""
    report_header =""
    report_row = ""
    nombreReporte = os.getenv("nomReporteUNIFIER")
    url = os.getenv("udrUrlUNIFIER")

    headers = {
         "Authorization": f"Bearer {token}",
         "Content-Type": "application/json"
    }
    payload = {
        "reportname":nombreReporte
    }
    response = requests.post(url,json=payload,headers=headers)

    if response.status_code == 200:
        # Json que contiene la data completa
        data = response.json()
        # Json que contiene solo las cabeceras
        report_header = response.json()['data'][0]['report_header']
        # Json que contiene los datosdel reporte
        report_row = response.json()['data'][0]['report_row']
    else:
        print("ERROR",response.status_code,response.text)
    
    return data

#              #
# Herramientas # LANGCHAIN
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

def loadJsonandSaveToVectorDB(json):

    embeddings = OpenAIEmbeddings()

    vectordb = Chroma.from_documents

    # Se crea una base de datos Chroma con todos los datos del PDF
    vectordb = Chroma.from_documents(json,embedding=embeddings)
    vectordb.persist() # Se guarda la BDD
    return vectordb

#                    #
# Ejecucion programa #
#                    # 

# Metodo de prueba para API
def main():
    vector_db = ""

    #MENU# -- permite subir PDF o leer reporte desde Unifier
    print("MENU OPCIONES ")
    print("1) Subir PDF Local")
    print("2) Elegir reporte de Unifier ")
    opc = input("Seleccione OPCION :")

    if opc == '1':
        print("Se cargara PDF local.")

        # Carga PDF y crea BDD vectorial
        vector_db = loadFileAndSaveToVectorDB()
        # cadena de conversacion
        qa = ConversationalRetrievalChain.from_llm(
            llm=model,
            retriever=vector_db.as_retriever(),
            return_source_documents=True)

        pregunta = input("Ingresa pregunta del archivo:")
        chat_history = []

        result = qa({"question": pregunta, "chat_history": chat_history})

        print("\nRespuesta:")
        print(result['answer'])

    elif opc == '2':
        print("Se cargara reporte de Unifier.")
        token = getTokenUnifier()
        jsonUnifier = loadJsonandSaveToVectorDB(loadReportUnifier(token))

        # Carga JSON y crea BDD vectorial
        vector_db = loadFileAndSaveToVectorDB()
        # cadena de conversacion
        qa = ConversationalRetrievalChain.from_llm(
            llm=model,
            retriever=vector_db.as_retriever(),
            return_source_documents=True)

        pregunta = input("Ingresa pregunta del archivo:")
        chat_history = []

        result = qa({"question": pregunta, "chat_history": chat_history})

        print("\nRespuesta:")
        print(result['answer'])



if __name__ == "__main__":
    main()