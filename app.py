# bot.py (نسخه ساده شده بدون پایگاه داده)

# ===============================================
# بخش ۱: وارد کردن کتابخانه‌ها
# ===============================================
import logging
import os
from datetime import datetime
import pytz
import html
import json
import traceback

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
)

# ===============================================
# بخش ۲: تنظیمات اولیه و ثابت‌ها
# ===============================================
# خواندن توکن ربات از متغیرهای محیطی
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# شناسه عددی ادمین
ADMIN_CHAT_ID = 7968166905

# اطلاعات حساب بانکی
CARD_NUMBER = "6219-8619-4829-7832"
ACCOUNT_HOLDER_NAME = "امیرحسین زمانی"

# تعریف پلن‌ها
PLANS = {
    "plan_de_1user": {"name": "سرویس آلمان / ۱ کاربره / ۳۰ روزه / نامحدود", "price": 110000},
    "plan_de_2user": {"name": "سرویس آلمان / ۲ کاربره / ۳۰ روزه / نامحدود", "price": 145000},
    "plan_de_3user": {"name": "سرویس آلمان / ۳ کاربره / ۳۰ روزه / نامحدود", "price": 185000},
    "plan_de_5user": {"name": "سرویس آلمان / ۵ کاربره / ۳۰ روزه / نامحدود", "price": 245000},
}

# فعال‌سازی لاگ‌ها
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# تعریف مراحل گفتگو
STATE_SELECT_PLAN, STATE_AWAIT_RECEIPT = range(2)

# ===============================================
# بخش ۳: تعریف دکمه‌ها و منوها
# ===============================================
MAIN_MENU_KEYBOARD = [
    ["🛍️ خرید اشتراک", "🎁 تست رایگان"],
    ["🔑 سرویس‌های من", "💰 تعرفه‌ها"],
    ["💰 کیف پول", "👤 پروفایل کاربری"],
    ["🤝 طرح همکاری"],
    ["👨‍💻 پشتیبانی", "📚 آموزش اتصال"]
]
MAIN_MENU_MARKUP = ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, resize_keyboard=True)

# ===============================================
# بخش ۴: توابع اصلی و دستورات
# ===============================================
def get_iran_time():
    """زمان و تاریخ فعلی ایران را برمی‌گرداند."""
    return datetime.now(pytz.timezone("Asia/Tehran"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """پیام خوشامدگویی و نمایش منوی اصلی."""
    user = update.effective_user
    welcome_message = f"درود {user.mention_html()} عزیز!\nبه ربات رسمی VipConfig خوش آمدید 👑\n\nبرای شروع، از منوی زیر استفاده کنید. 👇"
    await update.message.reply_text(welcome_message, reply_markup=MAIN_MENU_MARKUP, parse_mode='HTML')
    return ConversationHandler.END

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پیام‌های متنی منوی اصلی را مدیریت می‌کند."""
    text = update.message.text.strip()
    # در نسخه بدون دیتابیس، بسیاری از قابلیت ها موقتا غیرفعال هستند
    if text == "🛍️ خرید اشتراک":
        return await purchase_start(update, context)
    elif text == "👤 پروفایل کاربری":
        return await show_profile(update, context)
    elif text == "📚 آموزش اتصال":
        return await show_connection_guide_menu(update, context)
    elif text == "💰 کیف پول" or text == "🔑 سرویس‌های من":
         await update.message.reply_text("این قابلیت نیازمند پایگاه داده است و در نسخه‌های بعدی فعال خواهد شد.")
         return ConversationHandler.END
    else:
        await update.message.reply_text(f"بخش «{text}» در حال توسعه است. از شکیبایی شما سپاسگزاریم.")
        return ConversationHandler.END


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اطلاعات ساده پروفایل کاربر را نمایش می‌دهد."""
    user = update.effective_user
    now = get_iran_time()
    profile_text = (
        f"**👤 پروفایل شما:**\n\n"
        f"🔸 نام: `{user.full_name}`\n"
        f"🔸 شناسه کاربری: `{user.id}`\n\n"
        f"📆 `{now.year}/{now.month:02d}/{now.day:02d}` → ⏰ `{now.hour:02d}:{now.minute:02d}:{now.second:02d}`"
    )
    await update.message.reply_text(profile_text, parse_mode='Markdown')

# --- توابع راهنمای اتصال (بدون تغییر) ---
async def show_connection_guide_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🤖 اندروید", callback_data="guide_android"), InlineKeyboardButton("🍏 آیفون (iOS)", callback_data="guide_ios"), InlineKeyboardButton("💻 ویندوز", callback_data="guide_windows")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text("لطفاً سیستم‌عامل خود را برای دریافت راهنمای اتصال انتخاب کنید:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text("لطفاً سیستم‌عامل خود را برای دریافت راهنمای اتصال انتخاب کنید:", reply_markup=reply_markup)

async def show_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """متن راهنمای اتصال را بر اساس انتخاب کاربر نمایش می دهد."""
    query = update.callback_query
    await query.answer()
    guide_type = query.data.split('_')[1]
    guides = {
        "android": """**راهنمای اتصال برای اندروید (V2RayNG)**\n\n1. ابتدا برنامه **V2RayNG** را از [این لینک](https://github.com/2dust/v2rayNG/releases/latest) دانلود و نصب کنید.\n\n2. کد کانفیگ را که از ربات دریافت کرده‌اید، کپی کنید.\n\n3. وارد برنامه V2RayNG شده و روی **+** در بالا بزنید و **Import config from Clipboard** را انتخاب کنید.""",
        "ios": """**راهنمای اتصال برای آیفون (FoXray/V2Box)**\n\n1. یکی از برنامه‌های [**FoXray**](https://apps.apple.com/us/app/foxray/id6448898396) یا [**V2Box**](https://apps.apple.com/us/app/v2box-v2ray-client/id6446814690) را از اپ استور نصب کنید.\n\n2. کد کانفیگ را کپی کرده و برنامه را باز کنید. برنامه معمولا به صورت خودکار کانفیگ را شناسایی و اضافه می‌کند. اگر نشد، روی **+** زده و **Import from Clipboard** را انتخاب کنید.""",
        "windows": """**راهنمای اتصال برای ویندوز (v2rayN)**\n\n1. برنامه **v2rayN-Core** را از [این لینک](https://github.com/2dust/v2rayN/releases/latest) دانلود و اجرا کنید (`v2rayN.exe`).\n\n2. کد کانفیگ را کپی کرده و در برنامه کلیدهای **Ctrl + V** را بزنید.\n\n3. روی سرور کلیک راست کرده و آن را **Set as active server** کنید. سپس از آیکون برنامه کنار ساعت ویندوز، پراکسی را روی **Set system proxy** قرار دهید."""
    }
    back_button = InlineKeyboardMarkup([[InlineKeyboardButton("↪️ بازگشت به منوی راهنما", callback_data="back_to_guides")]])
    await query.edit_message_text(guides.get(guide_type, "راهنما یافت نشد."), parse_mode='Markdown', reply_markup=back_button, disable_web_page_preview=True)

async def back_to_guides(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """کاربر را به منوی انتخاب راهنما برمی گرداند."""
    query = update.callback_query
    await query.answer()
    await show_connection_guide_menu(update, context)

# ===============================================
# بخش ۵: جریان گفتگو برای خرید
# ===============================================
async def purchase_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """مرحله اول خرید: انتخاب لوکیشن"""
    keyboard = [[InlineKeyboardButton("🇩🇪 آلمان (سرور پرسرعت)", callback_data="loc_de")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text("لطفا لوکیشن سرویس مورد نظر خود را انتخاب کنید:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text("لطفا لوکیشن سرویس مورد نظر خود را انتخاب کنید:", reply_markup=reply_markup)
    return STATE_SELECT_PLAN

async def select_plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """مرحله دوم خرید: انتخاب پلن"""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton(f"{v['name']}: {v['price']:,} تومان", callback_data=k)]
        for k, v in PLANS.items()
    ]
    keyboard.append([InlineKeyboardButton("↪️ بازگشت", callback_data="back_to_locations")])
    await query.edit_message_text("یک پلن را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard))
    return STATE_AWAIT_RECEIPT # مستقیم به مرحله انتظار برای رسید می رویم

async def show_payment_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """مرحله سوم: نمایش اطلاعات پرداخت"""
    query = update.callback_query
    await query.answer()
    plan_id = query.data
    plan_info = PLANS.get(plan_id)

    if not plan_info:
        await query.edit_message_text("خطا: پلن نامعتبر است. لطفاً مجدداً تلاش کنید.")
        return ConversationHandler.END

    # ذخیره اطلاعات پلن انتخابی برای استفاده در مرحله بعد
    context.user_data['purchase_info'] = plan_info
    
    amount = plan_info.get('price')
    payment_text = (
        f"برای تکمیل خرید سرویس **{plan_info['name']}**، مبلغ **{amount:,.0f} تومان** را به شماره کارت زیر واریز نمایید:\n\n"
        f"💳 شماره کارت:\n`{CARD_NUMBER}`\n({ACCOUNT_HOLDER_NAME})\n\n"
        f"‼️ پس از واریز، **عکس واضح رسید** را در همین صفحه ارسال نمایید."
    )
    await query.edit_message_text(payment_text, parse_mode="Markdown")
    return STATE_AWAIT_RECEIPT

async def handle_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """رسید ارسال شده را پردازش و برای ادمین ارسال می‌کند."""
    user = update.message.from_user
    purchase_info = context.user_data.get('purchase_info', {})

    if not purchase_info:
         await update.message.reply_text("خطا! به نظر میرسد فرآیند خرید شما منقضی شده است. لطفا از منوی اصلی دوباره شروع کنید.", reply_markup=MAIN_MENU_MARKUP)
         return ConversationHandler.END

    subject = f"خرید سرویس: `{purchase_info.get('name', 'N/A')}`"
    amount_val = purchase_info.get('price', 0)

    admin_caption = (
        f"** رسید جدید **\n\n"
        f"👤 کاربر: {user.mention_html()}\n"
        f"🆔 شناسه: `{user.id}`\n"
        f"⚜️ موضوع: {subject}\n"
        f"💰 مبلغ: `{amount_val:,}` تومان\n\n"
        f"لطفاً پس از بررسی، کانفیگ را به صورت دستی برای کاربر ارسال نمایید."
    )

    # ارسال عکس به همراه کپشن برای ادمین
    await context.bot.send_photo(
        chat_id=ADMIN_CHAT_ID, photo=update.message.photo[-1].file_id,
        caption=admin_caption, parse_mode="HTML"
    )
    await update.message.reply_text("✅ رسید شما برای ادمین ارسال شد. لطفاً منتظر پاسخ و دریافت سرویس خود بمانید.", reply_markup=MAIN_MENU_MARKUP)

    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """لغو گفتگوی فعلی."""
    await update.message.reply_text("عملیات لغو شد و به منوی اصلی بازگشتید.", reply_markup=MAIN_MENU_MARKUP)
    context.user_data.clear()
    return ConversationHandler.END

# ===============================================
# بخش ۶: تابع اصلی و اجرای ربات
# ===============================================
def main() -> None:
    """ربات را ساخته و اجرا می‌کند."""
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Conversation handler برای خرید
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^🛍️ خرید اشتراک$'), purchase_start)],
        states={
            STATE_SELECT_PLAN: [
                CallbackQueryHandler(select_plan, pattern='^loc_de$'),
            ],
            STATE_AWAIT_RECEIPT: [
                CallbackQueryHandler(show_payment_info, pattern='^plan_de_'),
                MessageHandler(filters.PHOTO, handle_receipt),
                CallbackQueryHandler(purchase_start, pattern="^back_to_locations$")
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel), CommandHandler('start', start)],
        conversation_timeout=600, # 10 دقیقه
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('cancel', cancel))

    # هندلرهای راهنما
    application.add_handler(CallbackQueryHandler(show_guide, pattern='^guide_'))
    application.add_handler(CallbackQueryHandler(back_to_guides, pattern='^back_to_guides$'))

    # هندلر منوی اصلی (باید بعد از conv_handler باشد)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu))

    print("ربات در حال اجراست...")
    application.run_polling()

if __name__ == '__main__':
    main()
