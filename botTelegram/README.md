# Bot de Telegram para Análisis de Documentos

Este proyecto implementa un bot de Telegram capaz de analizar el contenido de diversos tipos de archivos (PDF, JPG) y reportes de sistemas (Unifier). El bot utiliza modelos de lenguaje avanzados para permitir a los usuarios realizar preguntas en lenguaje natural sobre la información contenida en los documentos proporcionados.

## Funcionalidades Principales

- **Análisis de PDF**: Extrae y procesa texto de archivos PDF para responder preguntas sobre su contenido.
- **Análisis de Imágenes**: Interpreta el contenido de imágenes JPG, incluyendo la extracción de texto visible.
- **Integración con Unifier**: Carga y procesa reportes directamente desde la plataforma Unifier.
- **Interacción Conversacional**: Permite un diálogo fluido para realizar múltiples preguntas sobre un mismo documento.

## Funcionamiento Detallado del Código

### `reporteLoader.py`

Esta clase centraliza toda la lógica de procesamiento de datos. Su función es tomar un archivo (PDF, imagen) o datos de una API (Unifier), procesarlo utilizando LangChain y prepararlo para que un modelo de lenguaje pueda responder preguntas sobre él.

-   **`loadPDFAndSaveToVectorDB(pdf_path)`**:
    -   Recibe la ruta de un archivo PDF.
    -   Utiliza `PyPDFLoader` de LangChain para cargar y dividir el documento en páginas.
    -   Emplea `OpenAIEmbeddings` para convertir el texto de cada página en vectores numéricos (embeddings).
    -   Almacena estos vectores en una base de datos vectorial `Chroma`. Este proceso permite realizar búsquedas de similitud semántica.

-   **`loadImageAndSaveToVectorDB(img_path)`**:
    -   Recibe la ruta de un archivo de imagen.
    -   Codifica la imagen en `base64` para poder enviarla a un modelo de visión.
    -   Utiliza el modelo `gpt-4o` de OpenAI para generar una descripción textual detallada de la imagen.
    -   Esta descripción se convierte en un `Document` de LangChain.
    -   Al igual que con el PDF, la descripción se vectoriza y se guarda en una base de datos `Chroma`.

-   **`loadJsonandSaveToVectorDB(json_dict)`**:
    -   Toma un diccionario JSON (obtenido de la API de Unifier).
    -   Lo guarda en un archivo JSON temporal.
    -   Usa `JSONLoader` para cargar los datos estructurados del JSON.
    -   Convierte los datos en documentos, los vectoriza y los almacena en una base de datos `Chroma`.

-   **`operaPDF(pdf_path)`, `operaIMG(img_path)`, `operaUnifierUDR()`**:
    -   Estos son los métodos de orquestación que el bot de Telegram llama.
    -   Cada uno invoca al método de carga correspondiente (`load...AndSaveToVectorDB`).
    -   Luego, crean y devuelven una `ConversationalRetrievalChain`. Esta cadena de LangChain es el objeto principal que:
        1.  Toma una pregunta del usuario.
        2.  La convierte en un vector.
        3.  Busca los fragmentos más relevantes en la base de datos vectorial (`retriever`).
        4.  Envía estos fragmentos junto con la pregunta al modelo de lenguaje para generar una respuesta coherente.

### `botTelegram.py`

Este script gestiona la interfaz con el usuario a través de Telegram. Maneja los comandos, botones, y el flujo de la conversación.

-   **Inicialización**:
    -   Importa las librerías necesarias y carga las variables de entorno (Token y API Key) desde el archivo `.env`.
    -   Define un diccionario `user_sessions = {}` para mantener el estado de cada usuario (ej: si está esperando un archivo o si ya puede hacer preguntas).

-   **`start(update, context)`**:
    -   Se activa con el comando `/start`.
    -   Muestra un menú principal con botones (`InlineKeyboardButton`) para que el usuario elija qué tipo de archivo desea procesar.

-   **`button_handler(update, context)`**:
    -   Maneja las pulsaciones de los botones del menú.
    -   Identifica qué botón se presionó (`query.data`).
    -   Actualiza el estado (`mode`) del usuario en `user_sessions`.
    -   Edita el mensaje para solicitar al usuario la acción correspondiente (ej: "Por favor, envía tu archivo PDF:").
    -   Si se elige "Cargar Unifier", llama directamente a `reporteLoader.operaUnifierUDR()` y prepara la sesión para las preguntas.

-   **`handle_document(update, context)` y `handle_photo(update, context)`**:
    -   Se activan cuando el usuario envía un archivo.
    -   Verifican si el usuario está en el modo correcto.
    -   Descargan el archivo a una ubicación temporal (`tempfile`).
    -   Llaman al método de `reporteLoader` correspondiente (`operaPDF` o `operaIMG`).
    -   Almacenan la `qa_chain` devuelta en la sesión del usuario y cambian su modo a `ready`.
    -   Notifican al usuario que el procesamiento ha finalizado.

-   **`handle_message(update, context)`**:
    -   Se activa con cada mensaje de texto que no es un comando.
    -   Verifica si el usuario está en modo `ready`.
    -   Extrae la `qa_chain` de la sesión del usuario.
    -   Pasa el texto del mensaje a la cadena con `qa_chain({"question": message_text, ...})`.
    -   Envía la respuesta (`result['answer']`) de vuelta al usuario.

-   **`cancel(update, context)`**:
    -   Se activa con el comando `/cancel`.
    -   Elimina la entrada del usuario del diccionario `user_sessions` y borra el archivo temporal asociado.

-   **`main()`**:
    -   Es la función principal que inicia el bot.
    -   Registra todos los manejadores que conectan las acciones del usuario (comandos, botones, mensajes) con las funciones correspondientes.
    -   Inicia el bot en modo `polling`.

1.  **Iniciar Conversación**: Envíe el comando `/start` al bot. Se desplegará un menú con las opciones disponibles.
2.  **Seleccionar Fuente de Datos**:
    - **📄 Subir PDF**: Pulse este botón y envíe el archivo PDF que desea analizar.
    - **🖼️ Subir Imagen JPG**: Pulse este botón y envíe la imagen que desea analizar.
    - **🔗 Cargar Unifier**: Pulse este botón para que el bot procese el reporte preconfigurado de Unifier.
3.  **Realizar Preguntas**: Una vez que el bot confirme que el archivo ha sido procesado, puede enviar sus preguntas como mensajes de texto simples.
4.  **Limpiar Sesión**: Use el comando `/cancel` en cualquier momento para finalizar la sesión actual, eliminar los datos y archivos temporales, y empezar de nuevo.