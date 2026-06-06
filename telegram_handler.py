#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telegram Handler - استقبال الفيديوهات من Telegram
"""

import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN, VIDEOS_FOLDER
from main import ShmBot

class TelegramHandler:
    def __init__(self):
        self.bot = ShmBot()
        self.app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        self.app.add_handler(MessageHandler(filters.VIDEO, self.handle_video))
        self.app.add_handler(MessageHandler(filters.TEXT, self.handle_text))
    
    async def handle_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الفيديوهات الواردة"""
        try:
            video = update.message.video
            file = await context.bot.get_file(video.file_id)
            
            video_name = f"video_{update.message.date.timestamp()}.mp4"
            video_path = os.path.join(VIDEOS_FOLDER, video_name)
            await file.download_to_drive(video_path)
            
            self.bot.add_to_queue(video_path)
            
            await update.message.reply_text(
                f"✅ تم استقبال الفيديو!\n"
                f"📹 الاسم: {video_name}\n"
                f"⏰ سيتم النشر في أفضل وقت عالعالم"
            )
            
            print(f"🎥 تم استقبال فيديو جديد: {video_name}")
        
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ: {str(e)}")
            print(f"❌ خطأ في معالجة الفيديو: {e}")
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الرسائل النصية"""
        text = update.message.text
        
        if text == "/start":
            await update.message.reply_text(
                "🤖 مرحباً بك في Shm Bot!\n\n"
                "📤 أرسل الفيديوهات وسأنشرها تلقائياً\n"
                "📊 استخدم الأوامر:\n"
                "/status - حالة البوت\n"
                "/queue - قائمة الفيديوهات"
            )
        
        elif text == "/status":
            queue_count = len(self.bot.video_queue)
            await update.message.reply_text(
                f"📊 حالة البوت:\n"
                f"✅ البوت يعمل\n"
                f"📹 الفيديوهات في الانتظار: {queue_count}"
            )
        
        elif text == "/queue":
            if not self.bot.video_queue:
                await update.message.reply_text("📭 لا توجد فيديوهات في القائمة")
            else:
                message = "📋 قائمة الفيديوهات:\n\n"
                for i, video in enumerate(self.bot.video_queue, 1):
                    message += f"{i}. {video['path']}\n"
                await update.message.reply_text(message)
        
        else:
            await update.message.reply_text(
                "❓ أمر غير معروف\n"
                "📤 أرسل فيديو أو اكتب /start"
            )
    
    def run(self):
        """تشغيل معالج Telegram"""
        print("🤖 تشغيل معالج Telegram...")
        self.app.run_polling()

if __name__ == "__main__":
    handler = TelegramHandler()
    handler.run()
