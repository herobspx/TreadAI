import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, CommandHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
ADMIN_ID       = int(os.environ.get("ADMIN_ID", "6445681743"))

WELCOME_MSG = """🚨 إطلاق فرصة محدودة — تداول آلي
—
تم فتح التسجيل على نظام تداول آلي جديد
مبني على استراتيجيات احترافية في SPX (سباكس)
—
🎯 الهدف:
مضاعفة رأس المال (مرة واحدة فقط)
—
⚙️ النظام يعتمد على:
• دخول ذكي على مناطق سيولة عالية
• إدارة صفقة لحظية
• تقليل المخاطر أثناء الحركة
• خروج دقيق عند تحقيق الهدف
—
💰 مثال:
رأس مال 1000$
الهدف: 2000$
(3750 ريال ➝ 7500 ريال)
—
⛔️ ملاحظات مهمة:
• الفرصة محدودة بعدد معين فقط
• الإغلاق يتم فور اكتمال العدد
• لا يتم فتح التسجيل مرة أخرى بنفس الشروط"""

WAITING_MSG = "✅ نرجو الانتظار وسيتم الرد عليك"

def welcome_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 للاشتراك أو التفاصيل اضغط هنا", callback_data="details")]
    ])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user:
        return

    # إشعار الأدمن
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📩 رسالة جديدة\n👤 {user.full_name}\n🆔 `{user.id}`\n📱 @{user.username or '—'}\n\nالرسالة:\n{update.message.text or '—'}",
        parse_mode="Markdown"
    )

    # الرد التلقائي
    await update.message.reply_text(
        WELCOME_MSG,
        reply_markup=welcome_keyboard()
    )

async def handle_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(WAITING_MSG)

    # إشعار الأدمن
    user = query.from_user
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🔔 طلب تفاصيل\n👤 {user.full_name}\n🆔 `{user.id}`\n📱 @{user.username or '—'}",
        parse_mode="Markdown"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        WELCOME_MSG,
        reply_markup=welcome_keyboard()
    )

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_details, pattern="^details$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Trading bot started!")
    app.run_polling()

if __name__ == "__main__":
    main()
