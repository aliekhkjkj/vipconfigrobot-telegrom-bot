# -*- coding: utf-8 -*-

# ===============================================
# بخش اول: وارد کردن کتابخانه‌ها
# ===============================================
import logging
import os
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from datetime import datetime
import pytz # برای کار با منطقه زمانی ایران

# ===============================================
# بخش دوم: تنظیمات اولیه و مهم
# ===============================================

# خواندن توکن ربات از متغیرهای محیطی سرور
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# شناسه عددی اکانت ادمین برای دریافت رسیدها
ADMIN_CHAT_ID = 6063054006

# شماره کارت و نام صاحب حساب
CARD_NUMBER = "6219-8619-4829-7832"
ACCOUNT_HOLDER_NAME = "امیرحسین زمانی"

# فعال‌سازی لاگ‌ها برای پیدا کردن راحت‌تر خطاها
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===============================================
# بخش سوم: تعریف دکمه‌های منو
# ===============================================
# منوی اصلی
MAIN_MENU_KEYBOARD = [
    ["🛍️ خرید اشتراک", "🎁 تست رایگان"],
    ["🔑 سرویس‌های من", "💰 تعرفه‌ها"],
    ["💰 کیف پول", "👤 پروفایل کاربری"],
    ["🤝 طرح همکاری"],
    ["👨‍💻 پشتیبانی", "📚 آموزش اتصال"]
]
MAIN_MENU_MARKUP = ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, resize_keyboard=True)

# دکمه بازگشت به منوی اصلی
BACK_TO_MAIN_MENU_KEYBOARD = [
    [InlineKeyboardButton("↪️ بازگشت به منوی اصلی", callback_data="main_menu")]
]
BACK_TO_MAIN_MENU_MARKUP = InlineKeyboardMarkup(BACK_TO_MAIN_MENU_KEYBOARD)


# ===============================================
# بخش چهارم: تعریف توابع اصلی ربات
# ===============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /start را مدیریت می‌کند و پیام خوشامدگویی را با منوی اصلی ارسال می‌کند."""
    user = update.effective_user
    welcome_message = f"درود {user.mention_html()} عزیز!\nبه ربات رسمی VipConfig خوش آمدید 👑\n\nبرای شروع، از منوی زیر استفاده کنید. 👇"
    await update.message.reply_text(welcome_message, reply_markup=MAIN_MENU_MARKUP, parse_mode='HTML')

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تمام پیام‌های متنی که از دکمه‌های منوی اصلی می‌آیند را مدیریت می‌کند."""
    text = update.message.text
    # توابع مختلف بر اساس متن دکمه فراخوانی می شوند
    if text == "🛍️ خرید اشتراک":
        await purchase_flow_start(update, context)
    elif text == "👤 پروفایل کاربری":
        await show_profile(update, context)
    elif text == "📚 آموزش اتصال":
        await show_connection_guide(update, context)
    elif text == "💰 کیف پول":
        await wallet_menu(update, context)
    elif text == "👨‍💻 پشتیبانی":
        await support_info(update, context)
    # ... سایر دکمه ها
    else:
        await update.message.reply_text(f"شما دکمه «{text}» را انتخاب کردید. این بخش در حال توسعه است.")


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اطلاعات پروفایل کاربر را نمایش می دهد."""
    user = update.effective_user
    # تنظیم منطقه زمانی تهران
    tehran_tz = pytz.timezone("Asia/Tehran")
    now = datetime.now(tehran_tz)
    
    # دریافت اطلاعات کاربر (در آینده این اطلاعات از دیتابیس خوانده می شود)
    user_balance = 0
    active_services = 0
    referrals = 0

    profile_text = (
        f"**👨🏻‍💻 وضعیت حساب کاربری شما:**\n\n"
        f"👤 نام: `{user.full_name}`\n"
        f"🕴🏻 شناسه کاربری: `{user.id}`\n"
        f"💰 موجودی: `{user_balance:,}` تومان\n"
        f"🛍️ تعداد سرویس های فعال: `{active_services}`\n"
        f"🤝 تعداد زیر مجموعه ها: `{referrals}` نفر\n\n"
        f"📆 `{now.year}/{now.month:02d}/{now.day:02d}` → ⏰ `{now.hour:02d}:{now.minute:02d}:{now.second:02d}`"
    )
    await update.message.reply_text(profile_text, parse_mode='Markdown')

async def show_connection_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی راهنمای اتصال را نمایش می دهد."""
    keyboard = [
        [InlineKeyboardButton("🤖 اندروید", callback_data="guide_android")],
        [InlineKeyboardButton("🍏 آیفون (iOS)", callback_data="guide_ios")],
        [InlineKeyboardButton("💻 ویندوز", callback_data="guide_windows")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("لطفاً سیستم‌عامل خود را برای دریافت راهنمای اتصال انتخاب کنید:", reply_markup=reply_markup)

async def support_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اطلاعات پشتیبانی را نمایش می دهد."""
    support_text = (
        "در صورت بروز هرگونه مشکل یا سوال، می‌توانید مستقیماً با تیم پشتیبانی ما در ارتباط باشید.\n\n"
        "ما همیشه آنلاین و آماده پاسخگویی هستیم! 😊\n\n"
        "👇 برای تماس با ما روی لینک زیر کلیک کنید:\n"
        "🆔 @VipConfig_Support"
    )
    await update.message.reply_text(support_text)


# --- توابع مربوط به جریان خرید ---
async def purchase_flow_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع جریان خرید و نمایش لوکیشن ها"""
    keyboard = [
        [InlineKeyboardButton("🇩🇪 آلمان", callback_data="purchase_location_de")],
        [InlineKeyboardButton("🇫🇮 فنلاند (به زودی)", callback_data="location_soon")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("لطفا لوکیشن مورد نظر را انتخاب کنید:", reply_markup=reply_markup)

async def show_plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش پلن های یک لوکیشن خاص"""
    # این تابع در آینده بر اساس لوکیشن انتخابی پلن ها را نمایش می دهد
    # فعلا فقط برای آلمان پیاده سازی شده
    keyboard = [
        [InlineKeyboardButton("۱ کاربره / ۳۰ روزه / نامحدود: ۱۱۰ هزار تومان", callback_data="plan_de_1user")],
        [InlineKeyboardButton("۲ کاربره / ۳۰ روزه / نامحدود: ۱۴۵ هزار تومان", callback_data="plan_de_2user")],
        # ... سایر پلن ها
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text("سرویس مورد نظر برای لوکیشن آلمان را انتخاب کنید:", reply_markup=reply_markup)


# --- توابع مربوط به کیف پول ---
async def wallet_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی کیف پول را نمایش می دهد."""
    user_balance = 0 # در آینده از دیتابیس خوانده می شود
    text = f"💰 موجودی کیف پول شما: `{user_balance:,}` تومان"
    keyboard = [
        [InlineKeyboardButton("💸 افزایش موجودی", callback_data="wallet_add_credit")],
        [InlineKeyboardButton("↪️ بازگشت", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")


# --- تابع اصلی برای مدیریت دکمه های Inline ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تمام کلیک های روی دکمه های شیشه ای (Inline) را مدیریت می کند."""
    query = update.callback_query
    await query.answer() # برای اینکه علامت ساعت روی دکمه از بین برود
    
    # مدیریت بازگشت به منو
    if query.data == 'main_menu':
        # این بخش را می توان برای نمایش مجدد منوی اصلی کامل کرد
        await query.message.edit_text("شما به منوی اصلی بازگشتید.")
    
    # مدیریت راهنمای اتصال
    elif query.data == 'guide_android':
        guide_text = """
        **راهنمای اتصال برای اندروید (V2RayNG)**

        1.  ابتدا برنامه **V2RayNG** را از لینک زیر دانلود و نصب کنید:
            [📥 دانلود مستقیم از گیت‌هاب (پیشنهادی)](https://github.com/2dust/v2rayNG/releases/latest)

        2.  کد کانفیگ (که با `vless://` شروع می‌شود) را که از ربات دریافت کرده‌اید، به طور کامل کپی کنید (با یک بار کلیک روی کد، کپی می‌شود).

        3.  وارد برنامه V2RayNG شوید و روی علامت **+** در گوشه بالا سمت راست بزنید.

        4.  از منوی باز شده، گزینه **"Import config from Clipboard"** را انتخاب کنید.

        5.  کانفیگ شما به لیست اضافه می‌شود. آن را انتخاب کرده و با زدن دکمه **V** بزرگ در پایین صفحه، به آن متصل شوید.
        """
        await query.message.edit_text(guide_text, reply_markup=BACK_TO_MAIN_MENU_MARKUP, parse_mode="Markdown")
    
    # مدیریت جریان خرید
    elif query.data == 'purchase_location_de':
        await show_plans(update, context)

    # ... سایر دکمه ها در اینجا مدیریت خواهند شد ...


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تمام خطاها را لاگ می‌کند."""
    logger.error("Exception while handling an update:", exc_info=context.error)

# ===============================================
# بخش پنجم: تابع اصلی و اجرای ربات
# ===============================================
def main() -> None:
    """این تابع اصلی، ربات را اجرا و در حالت Polling قرار می‌دهد."""
    
    print("Bot starting...")
    
    # ساخت اپلیکیشن ربات با توکن خوانده شده
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # --- افزودن مدیریت‌کننده‌ها (Handlers) ---
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_main_menu))
    application.add_handler(CallbackQueryHandler(button_handler)) # برای دکمه های شیشه ای
    application.add_error_handler(error_handler)

    # اجرای ربات
    print("Bot is running in Polling mode...")
    application.run_polling()


if __name__ == '__main__':
    main()

