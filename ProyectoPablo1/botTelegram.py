from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler
from dotenv import load_dotenv,find_dotenv
import tempfile
import os
import asyncio


load_dotenv()

TOKEN = os.getenv("TELEGRAM_KEY")

# Estados
MAIN_MENU, UPLOAD_PDF, ASK_QUESTION = range(3)
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📄 Cargar PDF", callback_data="upload_pdf")],
        [InlineKeyboardButton("🔗 Cargar Reporte Unifier", callback_data="upload_unifier")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text("🤖 ¡Bienvenido! ¿Qué deseas hacer?", reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text("🤖 ¡Bienvenido! ¿Qué deseas hacer?", reply_markup=reply_markup)
    
    return MAIN_MENU

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if query.data == "upload_pdf":
        await query.edit_message_text("📄 Por favor, envía el archivo PDF:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("↩️ Cancelar", callback_data="cancel")]]))
        user_data[user_id] = {"mode": "pdf"}
        return UPLOAD_PDF
        
    elif query.data == "upload_unifier":
        # Simular carga desde Unifier
        await query.edit_message_text("⏳ Cargando desde Unifier...")
        await asyncio.sleep(2)
        
        user_data[user_id] = {
            "mode": "unifier",
            "report_data": {
                "name": "Reporte Financiero Q4 2024",
                "project": "Proyecto Alpha",
                "data_points": 150
            }
        }
        
        await query.edit_message_text(
            f"✅ Reporte de Unifier cargado:\n📊 {user_data[user_id]['report_data']['name']}\n"
            "💬 ¿Qué pregunta tienes sobre este reporte?"
        )
        return ASK_QUESTION
        
    elif query.data == "cancel":
        return await start(update, context)

async def handle_pdf_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    if update.message.document and update.message.document.mime_type == 'application/pdf':
        document = update.message.document
        file = await context.bot.get_file(document.file_id)
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            await file.download_to_drive(temp_file.name)
            file_size = os.path.getsize(temp_file.name)
            
        user_data[user_id]["pdf_info"] = {
            "file_name": document.file_name,
            "file_size": file_size,
            "file_path": temp_file.name
        }
        
        await update.message.reply_text(
            f"✅ PDF recibido: {document.file_name}\n💬 ¿Qué pregunta tienes?"
        )
        return ASK_QUESTION
    else:
        await update.message.reply_text("❌ Envía un PDF válido")
        return UPLOAD_PDF

async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    question = update.message.text
    user_info = user_data.get(user_id, {})
    
    if user_info.get("mode") == "pdf":
        response = f"📄 Sobre el PDF: {user_info['pdf_info']['file_name']}\n❓ Pregunta: {question}\n🤖 Analizando contenido..."
    else:
        response = f"📊 Sobre Unifier: {user_info['report_data']['name']}\n❓ Pregunta: {question}\n🤖 Analizando datos..."
    
    keyboard = [
        [InlineKeyboardButton("📄 Nuevo PDF", callback_data="upload_pdf")],
        [InlineKeyboardButton("🔗 Nuevo Reporte", callback_data="upload_unifier")]
    ]
    
    await update.message.reply_text(response, reply_markup=InlineKeyboardMarkup(keyboard))
    return MAIN_MENU

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operación cancelada")
    return await start(update, context)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Error: {context.error}")
    if update and update.message:
        await update.message.reply_text("❌ Error procesando la solicitud")

def main():
    try:
        print("🤖 Iniciando bot...")
        print(f"🔑 Token: {TOKEN[:10]}...")  # Muestra solo parte del token por seguridad
        
        app = Application.builder().token(TOKEN).build()
        
        # Configurar conversation handler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                MAIN_MENU: [CallbackQueryHandler(handle_main_menu)],
                UPLOAD_PDF: [
                    MessageHandler(filters.Document.ALL, handle_pdf_upload),
                    CallbackQueryHandler(handle_main_menu, pattern="^cancel$")
                ],
                ASK_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question)]
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )
        
        app.add_handler(conv_handler)
        app.add_error_handler(error_handler)
        
        print("✅ Bot iniciado correctamente")
        print("📱 Envía /start a tu bot en Telegram")
        app.run_polling()
        
    except Exception as e:
        print(f"❌ Error al iniciar bot: {e}")
        print("🔍 Verifica:")
        print("1. El token es correcto")
        print("2. Tienes conexión a internet")
        print("3. El paquete python-telegram-bot está instalado")

if __name__ == "__main__":
    main()