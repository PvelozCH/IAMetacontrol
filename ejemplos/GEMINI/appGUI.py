
import tkinter as tk
from tkinter import filedialog, scrolledtext
import threading
import os

# Langchain
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# Hugging Face Local
from langchain.llms import HuggingFacePipeline
from langchain.embeddings import HuggingFaceEmbeddings

# --- Variables Globales ---
chain = None
chat_history = []

# --- Lógica Principal de LangChain ---

def create_conversational_chain(file_path):
    """
    Crea la cadena de recuperación conversacional a partir de un archivo de texto.
    """
    global chain
    
    try:
        # 1. Cargar el documento de texto
        loader = TextLoader(file_path, encoding='utf-8')
        documents = loader.load()

        # 2. Dividir el texto en chunks
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        texts = text_splitter.split_documents(documents)

        # 3. Crear embeddings locales (usará sentence-transformers)
        # La primera vez que se ejecute, descargará el modelo de embeddings.
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        # 4. Crear el VectorStore (FAISS) para búsquedas de similitud eficientes
        vectorstore = FAISS.from_documents(texts, embeddings)

        # 5. Cargar el modelo LLM local de Hugging Face
        # Se usará un pipeline de 'text2text-generation'.
        # La primera vez, descargará el modelo (puede tardar y ocupar espacio en disco).
        llm = HuggingFacePipeline.from_model_id(
            model_id="google/flan-t5-base",
            task="text2text-generation",
            model_kwargs={"temperature": 0.6, "max_length": 512},
        )

        # 6. Crear la cadena de conversación
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(),
            memory=memory
        )
        return "Cadena creada exitosamente. ¡Listo para chatear!"
    except Exception as e:
        return f"Error al crear la cadena: {e}"

# --- Funciones de la Interfaz Gráfica ---

def load_file():
    """
    Abre un diálogo para seleccionar un archivo y luego crea la cadena.
    """
    file_path = filedialog.askopenfilename(
        title="Selecciona un archivo de texto (.txt)",
        filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
    )
    if not file_path:
        return

    # Limpiar la GUI para el nuevo archivo
    chat_display.config(state=tk.NORMAL)
    chat_display.delete(1.0, tk.END)
    chat_display.config(state=tk.DISABLED)
    question_entry.delete(0, tk.END)
    
    status_label.config(text=f"Cargando: {os.path.basename(file_path)}...")
    
    # Ejecutar la creación de la cadena en un hilo separado para no bloquear la GUI
    def task():
        result = create_conversational_chain(file_path)
        status_label.config(text=result)
    
    threading.Thread(target=task).start()

def process_question():
    """
    Procesa la pregunta del usuario y muestra la respuesta.
    """
    global chat_history
    question = question_entry.get()
    if not question:
        return
    if not chain:
        status_label.config(text="Por favor, carga un archivo primero.")
        return

    # Mostrar la pregunta del usuario
    chat_display.config(state=tk.NORMAL)
    chat_display.insert(tk.END, f"Tú: {question}\n\n")
    chat_display.config(state=tk.DISABLED)
    question_entry.delete(0, tk.END)
    
    status_label.config(text="Procesando...")

    # Ejecutar la pregunta en un hilo para no congelar la GUI
    def task():
        global chat_history
        # El historial se gestiona automáticamente por el objeto `memory` en la cadena
        result = chain({"question": question, "chat_history": chat_history})
        answer = result['answer']
        
        # Actualizar el historial
        chat_history.append((question, answer))

        # Mostrar la respuesta en la GUI
        chat_display.config(state=tk.NORMAL)
        chat_display.insert(tk.END, f"Bot: {answer}\n\n")
        chat_display.config(state=tk.DISABLED)
        chat_display.see(tk.END) # Auto-scroll
        status_label.config(text="Listo.")

    threading.Thread(target=task).start()


# --- Configuración de la Ventana Principal ---
root = tk.Tk()
root.title("Chat con Documentos (Local)")
root.geometry("700x600")

# Frame principal
main_frame = tk.Frame(root, padx=10, pady=10)
main_frame.pack(fill=tk.BOTH, expand=True)

# Botón para cargar archivo
load_button = tk.Button(main_frame, text="Cargar Archivo de Texto", command=load_file)
load_button.pack(fill=tk.X, pady=5)

# Etiqueta de estado
status_label = tk.Label(main_frame, text="Por favor, carga un archivo para empezar.", anchor="w")
status_label.pack(fill=tk.X, pady=5)

# Área de visualización del chat
chat_display = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, state=tk.DISABLED, font=("Arial", 11))
chat_display.pack(fill=tk.BOTH, expand=True, pady=5)

# Frame para la entrada de preguntas
input_frame = tk.Frame(main_frame)
input_frame.pack(fill=tk.X, pady=5)

# Campo de texto para la pregunta
question_entry = tk.Entry(input_frame, font=("Arial", 11))
question_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
question_entry.bind("<Return>", lambda event: process_question())

# Botón de envío
send_button = tk.Button(input_frame, text="Enviar", command=process_question)
send_button.pack(side=tk.RIGHT, padx=5)

# Iniciar el bucle de la GUI
root.mainloop()
