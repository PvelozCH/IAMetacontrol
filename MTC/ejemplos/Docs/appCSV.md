
# Explicación del Script `appCSV.py`

Este script de Python implementa un bot de Telegram que responde a preguntas utilizando información extraída de un archivo CSV. A diferencia del script `appAgentCSV.py`, este enfoque no utiliza un "agente" con herramientas, sino una cadena de recuperación conversacional (`ConversationalRetrievalChain`). Este método se centra en encontrar los fragmentos de texto más relevantes dentro del documento CSV para responder a una pregunta.

A continuación, se detalla el funcionamiento del código.

## 1. Importaciones

- **`os`, `logging`, `dotenv`**: Para gestión del sistema operativo, registro de eventos y carga de variables de entorno, respectivamente.
- **`langchain`**: Se importan varios componentes:
  - **`document_loaders`**: `PyPDFLoader` (no utilizado) y `CSVLoader` para cargar documentos desde archivos PDF y CSV.
  - **`embeddings`**: `OpenAIEmbeddings` para convertir el texto de los documentos en vectores numéricos (embeddings).
  - **`vectorstores`**: `Chroma` se utiliza como la base de datos vectorial para almacenar y buscar eficientemente los embeddings.
  - **`chains`**: `ConversationalRetrievalChain` es la cadena principal que orquesta la recuperación de información y la generación de respuestas.
  - **`memory`**: `ConversationBufferMemory` se importa pero no se utiliza explícitamente en la cadena; la gestión del historial se hace manualmente.
  - **`llms`**: `OpenAI` se utiliza como el modelo de lenguaje para generar las respuestas.
- **`telegram`**: Componentes de `python-telegram-bot` para la funcionalidad del bot.

## 2. Configuración y Variables Globales

- **`logging.basicConfig(...)`**: Configura el sistema de logging.
- **`load_dotenv(find_dotenv())`**: Carga las variables de entorno (como la clave de la API de Telegram).
- **`global qa`, `global history`**: Se declaran las variables `qa` (que contendrá la cadena conversacional) e `history` (que almacenará el historial del chat) como globales para que puedan ser accedidas y modificadas por diferentes funciones a lo largo del script.

## 3. Funciones Principales

### `loadPDFFileAndSaveToVectorDB()`

Esta función está definida en el código pero **no se utiliza**. Su propósito sería cargar un archivo PDF, dividirlo en páginas, generar embeddings para cada página y guardarlos en una base de datos vectorial Chroma. Es un remanente de una posible funcionalidad anterior o diferente.

### `loadCSVFileAndSaveToVectorDB()`

Esta es una función crucial para la inicialización.

1.  **`loader = CSVLoader(...)`**: Crea un cargador de CSV, especificando la ruta del archivo (`../unibot/Reporte Contratos y Facturas Pendientes Chatbot.csv`), la codificación de caracteres (`utf-8`) y los argumentos específicos del formato CSV (delimitador y carácter de comillas).
2.  **`pages = loader.load_and_split()`**: Carga el contenido del CSV. Cada fila del CSV se trata como un "documento" separado. La función también los divide si es necesario.
3.  **`embeddings = OpenAIEmbeddings()`**: Inicializa el modelo de embeddings de OpenAI.
4.  **`vectordb = Chroma.from_documents(...)`**: Crea la base de datos vectorial. Toma los documentos (las filas del CSV), los convierte en vectores usando `OpenAIEmbeddings` y los almacena en un directorio local (`./unifier1`) para su persistencia. Esto permite que la base de datos no tenga que ser reconstruida cada vez que se inicia el script.
5.  **`vectordb.persist()`**: Guarda la base de datos en el disco.

### `retrieveConversationalChain(vector)`

Esta función construye la cadena de pregunta-respuesta.

1.  Utiliza `ConversationalRetrievalChain.from_llm` para crear la cadena.
2.  **`OpenAI(temperature=0)`**: Se le pasa el modelo de lenguaje de OpenAI, con `temperatura` 0 para respuestas consistentes.
3.  **`vector.as_retriever()`**: Convierte la base de datos vectorial en un "recuperador" (retriever). El retriever es el componente que busca en la base de datos los documentos más relevantes para una pregunta dada.
4.  **`return_source_documents=True`**: Configura la cadena para que, además de la respuesta, devuelva también los documentos fuente que utilizó para generarla.

### `askAndReturnTheQuestionAndHistory(question, history)`

Esta función maneja la lógica de una sola interacción de pregunta y respuesta.

1.  **`result = qa(...)`**: Llama a la cadena `qa` pasándole la pregunta actual (`question`) y el historial de la conversación (`chat_history`). La cadena utiliza tanto la pregunta como el historial para formular una mejor consulta al recuperador de documentos.
2.  **`history = [(question, result["answer"])]`**: Actualiza el historial. En esta implementación, el historial solo contiene el último par de pregunta y respuesta, no la conversación completa.
3.  Devuelve únicamente el texto de la respuesta (`result["answer"]`).

## 4. Inicialización y Flujo Principal

Estas líneas de código se ejecutan en el flujo principal del script, justo antes de definir la función `main`.

- **`v = loadCSVFileAndSaveToVectorDB()`**: Se llama a la función para cargar el CSV y crear la base de datos vectorial.
- **`qa = retrieveConversationalChain(v)`**: Se crea la cadena conversacional usando la base de datos recién creada.
- **`history = []`**: Se inicializa el historial de la conversación como una lista vacía.

## 5. Integración con Telegram

### `answerTheQuestion(update: Update, context: ContextTypes.DEFAULT_TYPE)`

Es la función asíncrona que maneja los mensajes de Telegram.

1.  Recibe el mensaje del usuario (`update.message.text`).
2.  Llama a `askAndReturnTheQuestionAndHistory` para obtener la respuesta de la cadena de LangChain.
3.  Envía la respuesta al usuario a través de Telegram.

### `main()`

Configura y ejecuta el bot de Telegram de la misma manera que en el script anterior, asociando los mensajes de texto entrantes con la función `answerTheQuestion`.

## 6. Bloque de Ejecución Principal

- **`if __name__ == "__main__":`**: Asegura que la función `main()` se llame para iniciar el bot cuando el script se ejecuta directamente.

En resumen, este script carga un archivo CSV en una base de datos de vectores. Luego, utiliza una cadena de LangChain para buscar en esa base de datos la información más relevante a la pregunta de un usuario de Telegram y genera una respuesta basada en esos datos, manteniendo un historial simple de la última interacción.
