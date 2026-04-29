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

    # إشعار الأدمن مع زر رد
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("↩️ رد", callback_data=f"reply_{user.id}")
    ]])
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📩 رسالة جديدة\n👤 {user.full_name}\n🆔 `{user.id}`\n📱 @{user.username or '—'}\n\nالرسالة:\n{update.message.text or '—'}",
        parse_mode="Markdown",
        reply_markup=kb
    )

    # الرد التلقائي
    await update.message.reply_text(
        WELCOME_MSG,
        reply_markup=welcome_keyboard()
    )

async def handle_reply_btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لما الأدمن يضغط زر رد"""
    query = update.callback_query
    await query.answer()
    target_id = query.data.replace("reply_", "")
    context.user_data["replying_to"] = target_id
    await query.message.reply_text(f"✏️ اكتب ردك للمستخدم `{target_id}`:", parse_mode="Markdown")

async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """يرسل رد الأدمن للمستخدم"""
    if update.effective_user.id != ADMIN_ID:
        return
    target_id = context.user_data.get("replying_to")
    if not target_id:
        return
    try:
        await context.bot.send_message(chat_id=int(target_id), text=update.message.text)
        await update.message.reply_text("✅ تم إرسال ردك")
        context.user_data.pop("replying_to", None)
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {e}")

async def handle_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(WAITING_MSG)

    # إشعار الأدمن مع زر رد
    user = query.from_user
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("↩️ رد", callback_data=f"reply_{user.id}")
    ]])
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🔔 طلب تفاصيل\n👤 {user.full_name}\n🆔 `{user.id}`\n📱 @{user.username or '—'}",
        parse_mode="Markdown",
        reply_markup=kb
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        WELCOME_MSG,
        reply_markup=welcome_keyboard()
    )

async def reply_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر للأدمن للرد على مستخدم معين: /reply USER_ID الرسالة"""
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("الاستخدام: /reply USER_ID الرسالة")
        return
    try:
        target_id = int(context.args[0])
        msg       = " ".join(context.args[1:])
        await context.bot.send_message(chat_id=target_id, text=msg)
        await update.message.reply_text(f"✅ تم الإرسال لـ {target_id}")
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {e}")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_details,   pattern="^details$"))
    app.add_handler(CallbackQueryHandler(handle_reply_btn, pattern="^reply_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.User(ADMIN_ID), handle_admin_reply))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Trading bot started!")
    app.run_polling()

if __name__ == "__main__":
    main()
