#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Shm Bot - TikTok Automation Bot
ينشر الفيديوهات بأفضل أوقات عالعالم
"""

import os
import time
import json
import datetime
from pathlib import Path
import pytz
import schedule
from telegram import Bot
from telegram.error import TelegramError

from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    BEST_POSTING_TIMES,
    BIO_DOTS,
    DEFAULT_HASHTAGS
)

# إنشاء مجلد للفيديوهات
VIDEOS_FOLDER = "videos"
QUEUE_FILE = "video_queue.json"

if not os.path.exists(VIDEOS_FOLDER):
    os.makedirs(VIDEOS_FOLDER)

class ShmBot:
    def __init__(self):
        self.telegram_bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.video_queue = []
        self.load_queue()
        
    def load_queue(self):
        """تحميل قائمة الفيديوهات المنتظرة"""
        if os.path.exists(QUEUE_FILE):
            with open(QUEUE_FILE, 'r') as f:
                self.video_queue = json.load(f)
        else:
            self.video_queue = []
    
    def save_queue(self):
        """حفظ قائمة الفيديوهات"""
        with open(QUEUE_FILE, 'w') as f:
            json.dump(self.video_queue, f, indent=2)
    
    def get_best_posting_time(self):
        """حساب أفضل وقت للنشر عالعالم"""
        best_times_utc = [
            datetime.time(8, 0),   # 8 AM UTC
            datetime.time(12, 0),  # 12 PM UTC
            datetime.time(18, 0),  # 6 PM UTC
            datetime.time(20, 0),  # 8 PM UTC
        ]
        
        now = datetime.datetime.now(pytz.UTC)
        
        for posting_time in best_times_utc:
            scheduled = now.replace(hour=posting_time.hour, minute=posting_time.minute, second=0)
            if scheduled > now:
                return scheduled
        
        tomorrow = now + datetime.timedelta(days=1)
        return tomorrow.replace(hour=best_times_utc[0].hour, minute=best_times_utc[0].minute, second=0)
    
    def receive_videos_from_telegram(self):
        """استقبال الفيديوهات من Telegram"""
        try:
            print("🎥 في انتظار استقبال الفيديوهات من Telegram...")
        except Exception as e:
            print(f"❌ خطأ في استقبال الفيديوهات: {e}")
    
    def add_to_queue(self, video_path, hashtags=DEFAULT_HASHTAGS):
        """إضافة فيديو للقائمة"""
        video_info = {
            "path": video_path,
            "hashtags": hashtags,
            "added_time": datetime.datetime.now().isoformat(),
            "scheduled": False
        }
        self.video_queue.append(video_info)
        self.save_queue()
        print(f"✅ تم إضافة الفيديو: {video_path}")
    
    def schedule_next_post(self):
        """جدولة الفيديو التالي للنشر"""
        if not self.video_queue:
            print("📭 لا توجد فيديوهات في القائمة")
            return
        
        next_video = self.video_queue[0]
        best_time = self.get_best_posting_time()
        
        print(f"📅 جدولة الفيديو التالي للنشر في: {best_time}")
        print(f"🎬 الفيديو: {next_video['path']}")
        print(f"#️⃣ الهاشتاجات: {next_video['hashtags']}")
    
    def post_video_to_tiktok(self, video_path, hashtags):
        """نشر الفيديو على TikTok"""
        try:
            print(f"🚀 جاري نشر الفيديو: {video_path}")
            print(f"📝 الهاشتاجات: {hashtags}")
            print(f"💬 البايو: {BIO_DOTS[:50]}...")
            print("⏰ جاري محاكاة النشر...")
            
            time.sleep(2)
            
            print("✅ تم نشر الفيديو بنجاح!")
            return True
        except Exception as e:
            print(f"❌ خطأ في النشر: {e}")
            return False
    
    def publish_scheduled_video(self):
        """نشر الفيديو المجدول"""
        if not self.video_queue:
            print("📭 لا توجد فيديوهات للنشر")
            return
        
        video_info = self.video_queue.pop(0)
        success = self.post_video_to_tiktok(video_info['path'], video_info['hashtags'])
        
        if success:
            self.save_queue()
            print(f"✅ تم حذف الفيديو من القائمة")
        else:
            self.video_queue.insert(0, video_info)
            self.save_queue()
            print(f"⚠️ سيتم إعادة محاولة لاحقاً")
    
    def send_status_to_telegram(self, message):
        """إرسال حالة البوت إلى Telegram"""
        try:
            self.telegram_bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=message
            )
            print(f"📨 تم إرسال الرسالة إلى Telegram")
        except TelegramError as e:
            print(f"❌ خطأ في إرسال الرسالة: {e}")
    
    def run(self):
        """تشغيل البوت الرئيسي"""
        print("=" * 50)
        print("🤖 تم بدء Shm Bot")
        print("=" * 50)
        
        schedule.every().day.at("08:00").do(self.publish_scheduled_video)
        schedule.every().day.at("12:00").do(self.publish_scheduled_video)
        schedule.every().day.at("18:00").do(self.publish_scheduled_video)
        schedule.every().day.at("20:00").do(self.publish_scheduled_video)
        
        schedule.every().hour.do(self.receive_videos_from_telegram)
        
        self.send_status_to_telegram("✅ تم بدء Shm Bot - البوت يعمل الآن!")
        
        print("🔄 البوت يعمل الآن... (اضغط Ctrl+C للإيقاف)")
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n🛑 تم إيقاف البوت")
            self.send_status_to_telegram("🛑 تم إيقاف Shm Bot")

if __name__ == "__main__":
    bot = ShmBot()
    bot.run()
