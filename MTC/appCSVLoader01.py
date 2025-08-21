import os

from langchain.embeddings import OpenAIEmbeddings 
from langchain.vectorstores import Chroma 
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI
from langchain.document_loaders.csv_loader import CSVLoader 
from langchain.vectorstores import Chroma 


from dotenv import load_dotenv,find_dotenv

load_dotenv(find_dotenv())


documents = []

loader = CSVLoader(file_path="./cdic/Inspecciones_2023-2024_04-08-23_18_09.csv", 
                   encoding="utf-8", 
                   csv_args={'delimiter': ',', 
                             'quotechar':'"',
                             })

# Lee documento csv
docs = loader.load()
print(docs)
embeddings = OpenAIEmbeddings()
db3 = Chroma.from_documents(docs, embedding=embeddings, 
                                 persist_directory="./saved9")

db3.persist()


"""
pdf_qa = ConversationalRetrievalChain.from_llm(OpenAI(temperature=0) , db3.as_retriever(), return_source_documents=True)


chat_history = []
print(len(docs))
 


load_dotenv(find_dotenv())

pdf_path = "./paper.pdf"
loader = PyPDFLoader(pdf_path)

pages = loader.load_and_split()

embeddings = OpenAIEmbeddings()
vectordb = Chroma.from_documents(pages, embedding=embeddings, 
                                 persist_directory="./saved0")

vectordb.persist()
#memory = ConversationBufferMemory(return_messages=True)
pdf_qa = ConversationalRetrievalChain.from_llm(OpenAI(temperature=0) , vectordb.as_retriever(), return_source_documents=True)
 
chat_history = []

query = "resume el documento en breves palabras"
result = pdf_qa({"question": query, "chat_history": chat_history})
print("Answer:")
print(result["answer"])

chat_history = [(query, result["answer"])]

query2 = "qué tipo de ataques podrían ejecutarse?"

result = pdf_qa({"question": query2, "chat_history": chat_history})

print("Answer:")
print(result["answer"])
"""