from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from reporteLoader import reporteLoader
import tempfile
import os
from dotenv import load_dotenv,find_dotenv
from functools import wraps

load_dotenv()

# Configuración de seguridad
TOKEN = os.getenv("TELEGRAM_KEY")
AUTHORIZED_USERS = [int(user_id) for user_id in os.getenv("AUTHORIZED_USERS", "").split(',') if user_id]

# Diccionario para guardar datos de usuarios
user_sessions = {}

def restricted(func):
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        # Si la lista de autorizados NO está vacía y el usuario NO está en la lista
        if AUTHORIZED_USERS and user_id not in AUTHORIZED_USERS:
            print(f"Acceso denegado al usuario no autorizado: {user_id}")
            if update.message:
                await update.message.reply_text("No tienes permiso para usar este bot.")
            elif update.callback_query:
                await update.callback_query.answer("No tienes permiso para usar este bot.", show_alert=True)
            return 
        # Si el usuario está autorizado (o la lista está vacía), ejecuta la función normal.
        return await func(update, context, *args, **kwargs)
    return wrapped

@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra menu principal"""
    print(f"Usuario autorizado iniciando bot. ID: {update.effective_user.id}")
    keyboard = [
        [InlineKeyboardButton("📄 Subir PDF", callback_data="pdf")],
        [InlineKeyboardButton("🖼️ Subir Imagen JPG", callback_data="img")],
        [InlineKeyboardButton("🔗 Cargar Unifier", callback_data="unifier")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Elige una opción:",
        reply_markup=reply_markup
    )

@restricted
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja los botones del menú"""
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    
    if query.data == "pdf":
        user_sessions[user_id] = {"mode": "waiting_pdf"}
        await query.edit_message_text("Por favor, envía tu archivo PDF:")
    
    elif query.data == "img":
        user_sessions[user_id] = {"mode": "waiting_img"}
        await query.edit_message_text("Por favor, envía tu imagen JPG:")
    
    elif query.data == "unifier":
        user_sessions[user_id] = {"mode": "processing_unifier"}

        # Mostrar opciones de los reportes que existen en UNIFIER
        keyboard = [
            [InlineKeyboardButton("📄 Reporte MOD", callback_data="reporte_contra_mod_in")],
            [InlineKeyboardButton("📄 Reporte 2", callback_data="reporte_contra_mod_in")],
            [InlineKeyboardButton("📄 Reporte 3", callback_data="reporte_contra_mod_in")],
            [InlineKeyboardButton("📄 Reporte 4", callback_data="reporte_contra_mod_in")],
            [InlineKeyboardButton("📄 Reporte 5", callback_data="reporte_contra_mod_in")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(text="Elige un reporte:", reply_markup=reply_markup)

    elif query.data == "reporte_contra_mod_in":
        nomReporte = query.data
        await query.edit_message_text(text="Cargando Reporte. Espera porfavor")
        
        try:
            qa_chain = reporteLoader.operaUnifierUDR(nomReporte)
            user_sessions[user_id] = {
                "mode": "ready",
                "qa_chain": qa_chain,
                "type": "unifier"
            }
            await query.message.reply_text("Reporte cargado. Hazme una pregunta:")
        except Exception as e:
            await query.edit_message_text(f"Error: {str(e)}")
            user_sessions[user_id] = {"mode": "menu"}

@restricted
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja la subida de PDFs"""
    user_id = update.message.from_user.id
    
    if user_id not in user_sessions or user_sessions[user_id].get("mode") != "waiting_pdf":
        await update.message.reply_text("Primero usa /start y elige 'Subir PDF'")
        return
    
    document = update.message.document
    if document.mime_type != 'application/pdf':
        await update.message.reply_text("Por favor, envía un archivo PDF")
        return
    
    await update.message.reply_text("PDF recibido. Procesando...")
    file = await context.bot.get_file(document.file_id)
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
        await file.download_to_drive(temp_file.name)
        temp_path = temp_file.name
    
    try:
        qa_chain = reporteLoader.operaPDF(temp_path)
        user_sessions[user_id] = {
            "mode": "ready",
            "qa_chain": qa_chain,
            "type": "pdf",
            "file_path": temp_path
        }
        await update.message.reply_text("PDF procesado. Ahora puedes hacerme preguntas sobre él:")
    except Exception as e:
        await update.message.reply_text(f"Error procesando PDF: {str(e)}")
        if os.path.exists(temp_path):
            os.remove(temp_path)

@restricted
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja la subida de imágenes JPG"""
    user_id = update.message.from_user.id
    
    if user_id not in user_sessions or user_sessions[user_id].get("mode") != "waiting_img":
        await update.message.reply_text("Para procesar una imagen, usa /start y elige 'Subir Imagen JPG'")
        return
    
    photo = update.message.photo[-1]
    
    await update.message.reply_text("Imagen recibida. Procesando...")
    file = await context.bot.get_file(photo.file_id)
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
        await file.download_to_drive(temp_file.name)
        temp_path = temp_file.name
        
    try:
        qa_chain = reporteLoader.operaIMG(temp_path)
        
        if qa_chain is None:
            await update.message.reply_text("Hubo un error al procesar la imagen. Por favor, intenta con otra.")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            user_sessions[user_id] = {"mode": "menu"}
            return

        user_sessions[user_id] = {
            "mode": "ready",
            "qa_chain": qa_chain,
            "type": "img",
            "file_path": temp_path
        }
        await update.message.reply_text("Imagen procesada. Ahora puedes hacerme preguntas sobre ella:")
    except Exception as e:
        await update.message.reply_text(f"Error procesando la imagen: {str(e)}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        user_sessions[user_id] = {"mode": "menu"}

@restricted
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja los mensajes de texto (preguntas)"""
    user_id = update.message.from_user.id
    message_text = update.message.text
    
    if user_id not in user_sessions or user_sessions[user_id].get("mode") != "ready":
        await update.message.reply_text("Usa /start para comenzar y subir un archivo.")
        return
    
    try:
        qa_chain = user_sessions[user_id]["qa_chain"]
        result = qa_chain({"question": message_text, "chat_history": []})
        await update.message.reply_text(f"Respuesta:\n{result['answer']}")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

@restricted
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Limpia la sesión del usuario"""
    user_id = update.message.from_user.id
    if user_id in user_sessions:
        if "file_path" in user_sessions[user_id] and user_sessions[user_id]["file_path"]:
            try:
                os.remove(user_sessions[user_id]["file_path"])
            except:
                pass
        del user_sessions[user_id]
    
    await update.message.reply_text("Sesión limpiada. Usa /start para comenzar de nuevo.")

def main():
    print("Iniciando bot de Telegram...")
    if not AUTHORIZED_USERS:
        print("ADVERTENCIA: La variable de entorno AUTHORIZED_USERS no está definida. El bot será público.")
    else:
        print(f"Bot restringido a los siguientes usuarios: {AUTHORIZED_USERS}")

    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo)) 
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot listo. Presiona Ctrl+C para detener.")
    app.run_polling()

if __name__ == "__main__":
    main()