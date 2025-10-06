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

from unifierController import uniController
import shutil
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

    #              #
    # Herramientas # LANGCHAIN
    #              #

    # Cargar PDF y guarda la data en una BDD vectorial
    def loadPDFAndSaveToVectorDB(pdf_path):
        directorioCache = "./MEDIAStrial"
        #Si ya viene el directorio, borrarlo
        if os.path.exists(directorioCache):
            shutil.rmtree(directorioCache, ignore_errors=True)

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
        directorioCache = "./ImagenDescripcion_db"
        #Si ya viene el directorio, borrarlo
        if os.path.exists(directorioCache):
            shutil.rmtree(directorioCache, ignore_errors=True)

        # Codificar la imagen a Base64 
        try:
            with open(img_path, "rb") as image_file:
                image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo de imagen en la ruta: {img_path}")
            return None

        # Usar un modelo de visión para describir la imagen 
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

        # Guardar la descripción en vectorDB
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
        directorioCache = "./json_vectordb"
        #Si ya viene el directorio, borrarlo
        if os.path.exists(directorioCache):
            shutil.rmtree(directorioCache, ignore_errors=True)

        # Convierte el diccionario de JSON a un string formateado
        json_content = json.dumps(json_dict, indent=2, ensure_ascii=False)
        
        # Crea un documento de LangChain directamente desde el contenido del JSON
        # La metadata puede ayudar a identificar la fuente del documento si es necesario
        doc = [Document(page_content=json_content, metadata={"source": "unifier_report"})]

        embeddings = OpenAIEmbeddings()
        vectordb = Chroma.from_documents(documents=doc, embedding=embeddings, persist_directory="./json_vectordb")

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

    def operaUnifierUDR(nomReporte):
        print("Se cargara reporte Unifier")
        token = uniController.getTokenUnifier()
        jsonUnifier = uniController.loadReportUnifier(token,nomReporte)

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
        # Elige primer reporte de Unifier que trae nombre de todos los otros 
        """
        token = uniController.getTokenUnifier()
        loadReportes = uniController.loadReportUnifier(token,"Nom_Reportes_Unifier") # Esto es solo de prueba por mientras
        dataReportes = json.loads(loadReportes)[0]['report_row']
        for reports in dataReportes:
            print("Lista de nombres de reportes.")
        
        """

        # Permite a usuario elegir cualquiera de los reportes que vienen


        # LLM lee reporte y permite hacerle una pregunta
        qa = reporteLoader.operaUnifierUDR()
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
