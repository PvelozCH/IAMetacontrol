# La aplicación puede funcionar sin telegram iniciando 'reporteLoader.py' por si solo

# Flujo de funcionamiento del Bot de Telegram
## Paso a Paso

1.  **Inicio y Autenticación**:
    *   El usuario inicia la interacción con el bot mediante el comando `/start`.
    *   El sistema verifica si el ID de usuario de Telegram está en la lista de usuarios autorizados definida en las variables de entorno. Si la lista está vacía, permite el acceso a cualquier usuario.

2.  **Menú de Opciones**:
    *   Una vez autorizado, el bot presenta un menú con tres opciones principales:
        *   **Subir PDF**: Para analizar un documento PDF.
        *   **Subir Imagen JPG**: Para analizar una imagen.
        *   **Cargar Unifier**: Para consultar datos de un reporte predefinido del sistema Unifier.

3.  **Selección del Usuario y Espera de Archivo**:
    *   El bot registra la selección del usuario y entra en un modo de "espera".
    *   Solicita al usuario que envíe el archivo correspondiente (PDF o JPG) según la opción elegida.

4.  **Procesamiento de Archivos**:
    *   **Recepción**: El bot recibe el archivo enviado por el usuario.
    *   **Guardado Temporal**: El archivo se guarda en una ubicación temporal en el servidor.
    *   **Análisis y Vectorización**:
        *   **PDF**: Se extrae el texto del documento.
        *   **Imagen**: Se utiliza un modelo de visión para generar una descripción textual del contenido de la imagen.
        *   **Unifier**: Se carga un reporte específico desde Unifier.
    *   **Creación de la Cadena de QA**: El texto extraído o generado se procesa y se carga en una cadena de preguntas y respuestas (`ConversationalRetrievalChain`), que queda lista para recibir consultas.

5.  **Interacción con el Usuario (Preguntas y Respuestas)**:
    *   El bot notifica al usuario que el procesamiento ha finalizado y que ya puede hacer preguntas.
    *   El usuario envía preguntas en lenguaje natural.
    *   El bot utiliza la cadena de QA para buscar la información más relevante en el documento procesado y generar una respuesta.
    *   La respuesta se envía de vuelta al usuario.

6.  **Finalización de la Sesión**:
    *   El usuario puede usar el comando `/cancel` para finalizar la sesión.
    *   El bot elimina los datos de la sesión del usuario, incluido el archivo temporal almacenado, liberando los recursos.
