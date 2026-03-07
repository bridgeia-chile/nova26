"""
Telegram Bot Interface - Principal communication interface
"""
import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

class TelegramInterface:
    """Telegram bot interface for nova26."""

    COMMANDS = {
        'start': 'Presentación e info del agente',
        'status': 'Estado actual del agente (recursos, uptime, skills)',
        'memory': 'Ver resumen de memorias almacenadas',
        'forget': 'Olvidar un recuerdo específico',
        'skills': 'Listar habilidades instaladas',
        'teach': 'Enseñar un nuevo procedimiento',
        'backup': 'Crear backup del alma',
        'restore': 'Restaurar desde un archivo de alma',
        'reflect': 'Forzar ciclo de auto-reflexión',
        'delegate': 'Enviar tarea a Claude Code',
        'config': 'Ver/modificar configuración',
        'dashboard': 'Ver el panel de control web',
        'shutdown': 'Apagar el agente limpiamente'
    }

    def __init__(self, brain):
        self.brain = brain
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.owner_id = os.getenv('OWNER_TELEGRAM_ID')
        self.app = None
        self.port = os.getenv("NOVA_API_PORT", 8090)

    async def _verify_owner(self, update: Update) -> bool:
        """Check if message is from the owner."""
        user_id = str(update.effective_user.id)
        if self.owner_id and user_id != self.owner_id:
            await update.message.reply_text("Acceso denegado. No eres mi creador.")
            return False
        return True

    async def dashboard_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self._verify_owner(update): return
        url = f"http://localhost:{self.port}"
        await update.message.reply_text(f"🖥️ **Dashboard de nova26**\nPuedes acceder aquí: {url}\n\nEstilo: Glassmorphism Premium", parse_mode='Markdown')

    async def start_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self._verify_owner(update): return
        welcome_msg = (
            f"🌌 Hola. Soy {self.brain.identity.state.get('name', 'nova26')}.\n"
            "Tu agente autónomo de IA. Usa /help para ver mis comandos.\n"
            f"Accede a mi dashboard en: http://localhost:{self.port}"
        )
        await update.message.reply_text(welcome_msg)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self._verify_owner(update): return
        
        user_text = update.message.text
        if not user_text: return
        
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
        
        try:
            # Send text response
            response = await self.brain.process_input(user_text, interface='telegram')
            await update.message.reply_text(response)
            
            # Check if user asked for audio or if brain generated a voice file (future proofing)
            if any(word in user_text.lower() for word in ['audio', 'voz', 'háblame', 'hablame']):
                await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='record_voice')
                from tools.audio_tools import AudioTools
                audio_tool = AudioTools()
                voice_path = await audio_tool.text_to_speech(response)
                
                if not voice_path.startswith("ERROR"):
                    with open(voice_path, 'rb') as voice:
                        await update.message.reply_voice(voice=voice)
                    if os.path.exists(voice_path):
                        os.remove(voice_path)
                else:
                    logging.warning(f"Failed to generate TTS: {voice_path}")

        except Exception as e:
            logging.error(f"Error processing message: {str(e)}")
            await update.message.reply_text("Ocurrió un error al procesar tu solicitud.")

    async def handle_audio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja mensajes de voz y archivos de audio."""
        if not await self._verify_owner(update): return
        
        # Determinar si es voz o archivo de audio
        audio_file = update.message.voice or update.message.audio
        if not audio_file: return
        
        await update.message.reply_text("📥 Procesando audio...")
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
        
        try:
            # Descargar archivo temporalmente
            new_file = await context.bot.get_file(audio_file.file_id)
            file_ext = "ogg" if update.message.voice else audio_file.file_name.split('.')[-1]
            temp_path = f"tmp_audio_{audio_file.file_id}.{file_ext}"
            await new_file.download_to_drive(temp_path)
            
            # Transcribir
            from tools.audio_tools import AudioTools
            audio_tool = AudioTools()
            transcription = await audio_tool.transcribe(temp_path)
            
            # Limpiar archivo
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            if transcription.startswith("ERROR"):
                await update.message.reply_text(transcription)
                return
                
            # Procesar el texto transcrito como si fuera un mensaje normal
            await update.message.reply_text(f"📝 *Transcripción:* {transcription}", parse_mode='Markdown')
            response = await self.brain.process_input(transcription, interface='telegram')
            await update.message.reply_text(response)
            
        except Exception as e:
            logging.error(f"Error en handle_audio: {e}")
            await update.message.reply_text(f"Error procesando audio: {e}")

    async def start(self):
        """Start the telegram bot background task."""
        if not self.token:
            logging.warning("No TELEGRAM_BOT_TOKEN provided. Telegram interface disabled.")
            return
            
        self.app = ApplicationBuilder().token(self.token).build()
        
        self.app.add_handler(CommandHandler("start", self.start_cmd))
        self.app.add_handler(CommandHandler("dashboard", self.dashboard_cmd))
        self.app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message))
        self.app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, self.handle_audio))
        
        me = await self.app.bot.get_me()
        print(f"[*] nova26 Telegram Bot iniciado para @{me.username}")
        logging.info("Telegram interface initializing...")
        
        # Initialize and start the application
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
        logging.info("Telegram polling started successfully.")
