# pip install -qU "langchain[anthropic]" to call the model
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain_community.document_loaders import UnstructuredImageLoader
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain_text_splitters import RecursiveJsonSplitter
from langchain_community.document_loaders import JSONLoader
from dotenv import load_dotenv,find_dotenv
from langchain.document_loaders import JSONLoader
from langchain_core.messages import HumanMessage
from langchain.schema.document import Document

import base64
import tempfile
import pycurl
import requests
import os
import json

class reporteLoader:

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
    def loadPDFAndSaveToVectorDB(pdf_path):
        
        # Carga PDF directamente desde un directorio
        loader = PyPDFLoader(pdf_path)

        pages = loader.load_and_split()

        embeddings = OpenAIEmbeddings()

        # Se crea una base de datos Chroma con todos los datos del PDF
        vectordb = Chroma.from_documents(pages, embedding=embeddings, 
                                        persist_directory="./MEDIAStrial")
        vectordb.persist() # Se guarda la BDD
        return vectordb
    
    # Cargar PDF y guarda la data en una BDD vectorial
    def loadImageAndSaveToVectorDB(img_path):
        # Este método ahora contiene toda la lógica para procesar una imagen correctamente.
        
        # --- 1. Codificar la imagen a Base64 ---
        try:
            with open(img_path, "rb") as image_file:
                image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo de imagen en la ruta: {img_path}")
            return None

        # --- 2. Usar un modelo de visión para describir la imagen ---
        # Se instancia un nuevo modelo localmente aquí porque el modelo de la clase ('gpt-4.1-nano') no soporta visión.
        try:
            vision_model = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o")
            
            message = HumanMessage(
                content=[
                    {"type": "text", "text": "Describe esta imagen en gran detalle. Identifica todos los objetos, personas, el entorno, y extrae cualquier texto visible."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                    },
                ]
            )
            print("Enviando imagen al modelo de visión para su descripción...")
            response = vision_model.invoke([message])
            description = response.content
            print("Descripción recibida.")

        except Exception as e:
            print(f"Error al contactar con el modelo de visión: {e}")
            return None

        # --- 3. Guardar la descripción en la base de datos vectorial ---
        doc = Document(page_content=description, metadata={"source": img_path})

        embeddings = OpenAIEmbeddings()
        vectordb = Chroma.from_documents(
            documents=[doc], 
            embedding=embeddings, 
            persist_directory="./ImagenDescripcion_db"
        )
        vectordb.persist()
        
        print("La descripción de la imagen ha sido guardada en la base de datos vectorial.")
        
        return vectordb

    #  Carga directamente json y lo convierte en un vector
    def loadJsonandSaveToVectorDB(json_dict):
        # Extrae data 
        jq_schema = '.data[0]'
        # toma archivo json como archivo temporal
        with tempfile.NamedTemporaryFile(mode='w+',delete=False,suffix='.json',encoding='utf-8') as tmp_file:
            json.dump(json_dict,tmp_file)
            tmp_file_path = tmp_file.name
        # carga data de json temporal
        loader = JSONLoader(file_path=tmp_file_path,jq_schema=jq_schema,text_content=False)
        
        # Crea documento para transformar a vector
        doc = loader.load()

        os.remove(tmp_file_path) 

        embeddings = OpenAIEmbeddings()
        vectordb = Chroma.from_documents(documents=doc,embedding=embeddings,persist_directory="./json_vectordb")

        return vectordb
    
    def operaPDF(pdf_path):
            print("Se cargara PDF local.")
            # Carga PDF y crea BDD vectorial
            vector_db = reporteLoader.loadPDFAndSaveToVectorDB(pdf_path)
            # cadena de conversacion
            qa = ConversationalRetrievalChain.from_llm(
                llm=reporteLoader.model,
                retriever=vector_db.as_retriever(),
                return_source_documents=True)
            return qa

    def operaUnifier():
        print("Se cargara reporte Unifier")
        token = reporteLoader.getTokenUnifier()
        jsonUnifier = reporteLoader.loadReportUnifier(token)

        # Carga JSON y crea BDD vectorial
        vector_db = reporteLoader.loadJsonandSaveToVectorDB(jsonUnifier)
        # cadena de conversacion
        qa = ConversationalRetrievalChain.from_llm(
                llm=reporteLoader.model,
                retriever=vector_db.as_retriever(),
                return_source_documents=True)
        return qa
    
    def operaIMG(img_path):
        print("Se cargara imagen")
        # Carga JSON y crea BDD vectorial
        vector_db = reporteLoader.loadImageAndSaveToVectorDB(img_path)
        # cadena de conversacion
        qa = ConversationalRetrievalChain.from_llm(
                llm=reporteLoader.model,
                retriever=vector_db.as_retriever(),
                return_source_documents=True)
        return qa
        
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
    print("3) Subir foto local")
    opc = input("Seleccione OPCION :")

    if opc == '1':
        pdf_path = "MEDIAStrial.pdf"
        qa = reporteLoader.operaPDF(pdf_path)
        pregunta = input("Ingresa pregunta del archivo:")
        chat_history = []

        result = qa({"question": pregunta, "chat_history": chat_history})

        print("\nRespuesta:")
        print(result['answer'])

    elif opc == '2':
        qa = reporteLoader.operaUnifier()
        pregunta = input("Ingresa pregunta del archivo:")
        chat_history = []

        result = qa({"question": pregunta, "chat_history": chat_history})

        print("\nRespuesta:")
        print(result['answer'])
    elif opc == '3':
        img_path = "imagenEjemplo.jpg"
        qa = reporteLoader.operaIMG(img_path)
        pregunta = input("Ingresa pregunta de la imagen:")
        chat_history = []

        result = qa({"question": pregunta, "chat_history": chat_history})

        print("\nRespuesta:")
        print(result['answer'])

if __name__ == "__main__":
    main()
