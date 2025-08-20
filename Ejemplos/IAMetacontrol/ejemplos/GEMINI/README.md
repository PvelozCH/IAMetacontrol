# Chat con Documentos Locales usando LangChain y Hugging Face

Esta es una aplicación de escritorio simple que te permite conversar con tus propios archivos de texto. Utiliza modelos de lenguaje (LLM) de Hugging Face que se ejecutan de forma local en tu máquina, lo que garantiza la privacidad de tus datos y elimina la necesidad de claves API de servicios de pago como OpenAI.

## Características

- **Interfaz Gráfica Simple**: Creada con Tkinter, la librería de GUI estándar de Python.
- **Carga de Archivos Locales**: Permite al usuario seleccionar un archivo de texto (`.txt`) desde su sistema.
- **Modelos de IA Locales y Gratuitos**: Utiliza un modelo de Hugging Face para la generación de lenguaje y otro para los embeddings, sin coste alguno.
- **Privacidad**: Todo el procesamiento se realiza en tu propia computadora. Tus documentos nunca abandonan tu máquina.
- **Manejo de Conversación**: La aplicación recuerda el historial del chat para mantener conversaciones contextuales.
- **UI Reactiva**: El procesamiento de la IA se ejecuta en hilos separados para que la interfaz gráfica no se congele mientras el modelo "piensa".

---

## ¿Cómo Funciona el Código? (`appGUI.py`)

El script se puede dividir en dos partes principales: la lógica de la Inteligencia Artificial con LangChain y la Interfaz Gráfica de Usuario (GUI) con Tkinter.

### Lógica de la IA (LangChain)

La magia ocurre dentro de la función `create_conversational_chain(file_path)`. Estos son los pasos que sigue:

1.  **Carga del Documento**:
    -   `TextLoader(file_path)`: Carga el contenido del archivo de texto que el usuario seleccionó.

2.  **División del Texto**:
    -   `CharacterTextSplitter(...)`: Un documento grande no puede ser procesado de una sola vez por el modelo. Este objeto divide el texto en fragmentos (o *chunks*) más pequeños y manejables, con una ligera superposición para no perder contexto entre ellos.

3.  **Creación de Embeddings**:
    -   `HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")`: Este es un paso crucial. Un "embedding" es una representación numérica (un vector) del significado semántico de un texto. Esta línea carga un modelo especializado de Hugging Face que convierte cada fragmento de texto en uno de estos vectores. La primera vez que se ejecute, se descargará este modelo.

4.  **Almacenamiento en un VectorStore**:
    -   `FAISS.from_documents(...)`: Todos los vectores creados en el paso anterior se almacenan en una base de datos vectorial llamada FAISS. FAISS es extremadamente eficiente para buscar vectores. Cuando haces una pregunta, la aplicación primero la convierte en un vector y luego usa FAISS para encontrar los fragmentos de texto del documento original cuyos vectores son más "similares" a la pregunta.

5.  **Carga del Modelo de Lenguaje (LLM)**:
    -   `HuggingFacePipeline.from_model_id(model_id="google/flan-t5-base", ...)`: Aquí se carga el "cerebro" de la aplicación. `google/flan-t5-base` es un modelo de lenguaje de Google, disponible en Hugging Face, capaz de entender y generar texto. Se configura para una tarea de "texto a texto". La primera vez que se ejecute, también se descargará este modelo (es más grande que el de los embeddings).

6.  **Creación de la Cadena Conversacional**:
    -   `ConversationalRetrievalChain.from_llm(...)`: LangChain une todo en un objeto llamado "cadena". Esta cadena específica está diseñada para conversaciones y recuperación de información. Sabe cómo:
        a. Tomar tu pregunta.
        b. Buscar los fragmentos de texto relevantes en el `VectorStore` (FAISS).
        c. Enviar tu pregunta, los fragmentos relevantes y el historial del chat al `LLM` (flan-t5-base).
        d. Recibir la respuesta del `LLM` y devolvértela.
        e. Guardar la interacción en su memoria (`ConversationBufferMemory`).

### Interfaz Gráfica (Tkinter)

La GUI está diseñada para ser simple y funcional. Las funciones clave son:

-   **`load_file()`**: Se activa con el botón "Cargar Archivo de Texto". Abre un explorador de archivos para que elijas un `.txt`. Para evitar que la aplicación se congele mientras se procesa el archivo (lo que puede tardar), inicia la función `create_conversational_chain` en un **hilo de ejecución separado** (`threading.Thread`).
-   **`process_question()`**: Se activa cuando presionas "Enviar" o la tecla Enter. Toma la pregunta del campo de texto y, de manera similar a la carga de archivos, pasa la pregunta a la cadena de IA en un **hilo separado**. Una vez que la IA genera la respuesta, el hilo actualiza la ventana del chat. Este enfoque garantiza que siempre puedas interactuar con la ventana, incluso durante el procesamiento.

---

## Guía de Instalación y Uso

Sigue estos pasos para poner en marcha la aplicación.

### 1. Requisitos Previos

-   Tener instalado **Python 3.8** o una versión superior.

### 2. Configuración del Entorno

Abre una terminal y sigue estos comandos.

**a. Navega al directorio del proyecto:**
```bash
cd /home/pvos/Escritorio/Proyectos/PvOS/IAMetacontrol/ejemplos
```

**b. Crea un entorno virtual:**
Esto crea una carpeta `venv` que contendrá todas las librerías necesarias, manteniendo tu sistema limpio.
```bash
python3 -m venv venv
```

**c. Activa el entorno virtual:**
Debes hacer esto cada vez que abras una nueva terminal para trabajar en el proyecto.
```bash
source venv/bin/activate
```
Tu prompt de la terminal debería cambiar para mostrar `(venv)`.

### 3. Instalación de Dependencias

Con el entorno activado, instala todas las librerías necesarias con un solo comando:
```bash
pip install langchain torch transformers sentence-transformers faiss-cpu
```

### 4. Ejecución de la Aplicación

Una vez instaladas las dependencias, ejecuta el script de la GUI:
```bash
python appGUI.py
```

### 5. ¡A Chatear!

1.  Se abrirá la ventana de la aplicación.
2.  Haz clic en **"Cargar Archivo de Texto"** y selecciona un archivo `.txt`.
3.  **Espera un momento.** La etiqueta de estado te indicará que está "Cargando...".
4.  Cuando el estado cambie a **"Cadena creada exitosamente. ¡Listo para chatear!"**, escribe tu pregunta en la caja de texto inferior y presiona "Enviar".

> **NOTA MUY IMPORTANTE: Descarga de Modelos**
> La **primera vez** que cargues un archivo, la aplicación necesitará descargar los modelos de Hugging Face. Esto puede tardar varios minutos y requiere una conexión a internet. Los modelos se guardarán en una caché en tu disco duro para usos futuros, por lo que las siguientes veces que uses la aplicación será mucho más rápido.
