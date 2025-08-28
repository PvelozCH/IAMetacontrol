# Bot de Telegram para Preguntas y Respuestas sobre Documentos

Este proyecto es un bot de Telegram que permite a los usuarios hacer preguntas sobre documentos PDF o reportes de Unifier. El bot utiliza la librería `python-telegram-bot` para la interacción con Telegram y `LangChain` para el procesamiento de lenguaje natural y la búsqueda de respuestas en los documentos.

## Características

- **Carga de Documentos**: Soporta la carga de archivos PDF directamente en el chat.
- **Integración con Unifier**: Puede cargar reportes directamente desde Unifier (la lógica de carga está en `reporteLoader.py`).
- **Conversación Interactiva**: Mantiene una conversación con el usuario a través de diferentes estados (menú principal, carga de archivos, preguntas).
- **Procesamiento de Lenguaje Natural**: Utiliza un modelo de Question-Answering (QA) de LangChain para entender las preguntas y encontrar las respuestas más relevantes dentro del documento cargado.
- **Manejo de Sesiones**: Guarda el contexto de cada usuario para saber sobre qué documento está preguntando.

## ¿Cómo funciona?

El bot está estructurado como una "conversación" con varios pasos o estados:

1.  **Inicio (`/start`)**: El usuario inicia la interacción con el comando `/start`. El bot responde con un menú con dos opciones: "Cargar PDF" o "Cargar Reporte Unifier".
2.  **Selección de Fuente**:
    *   Si el usuario elige **"Cargar PDF"**, el bot le pide que envíe el archivo.
    *   Si el usuario elige **"Cargar Reporte Unifier"**, el bot llama a la lógica de `reporteLoader.py` para obtener los datos.
3.  **Procesamiento del Documento**:
    *   **PDF**: Una vez que el usuario envía el PDF, el bot lo guarda en un archivo temporal y utiliza `reporteLoader.operaPDF()` para procesarlo. Esta función (presumiblemente) usa LangChain para crear una base de datos vectorial de texto a partir del PDF.
    *   **Unifier**: La función `reporteLoader.operaUnifier()` se encarga de la lógica para obtener y procesar el reporte.
    *   En ambos casos, el resultado es una "cadena de QA" (`qa_chain`) de LangChain, que está lista para recibir preguntas.
4.  **Fase de Preguntas y Respuestas**: Una vez que el documento está procesado, el bot le indica al usuario que puede hacer su pregunta.
5.  **Generación de Respuesta**: Cuando el usuario envía una pregunta (como un mensaje de texto), el bot pasa esa pregunta a la `qa_chain` de LangChain, que busca la respuesta en el documento previamente procesado y la devuelve.
6.  **Continuación**: Después de responder, el bot pregunta si el usuario desea hacer otra pregunta sobre el mismo documento o cargar uno nuevo.
7.  **Cancelar (`/cancel`)**: En cualquier momento, el usuario puede usar el comando `/cancel` para terminar la conversación actual, limpiar los datos de su sesión y eliminar cualquier archivo temporal.

## Archivos Principales

-   `botTelegram.py`: Contiene toda la lógica del bot de Telegram, el manejo de los comandos, mensajes, botones y los estados de la conversación.
-   `reporteLoader.py`: Contiene la lógica de procesamiento de los documentos. Se encarga de tomar un archivo PDF o un reporte de Unifier y convertirlo en una cadena de QA de LangChain.
-   `.env`: Archivo (no incluido en el repositorio) que debe contener la variable de entorno `TELEGRAM_KEY` con el token del bot.