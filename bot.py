from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
)
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Google Sheets-ga ulanish
JSON_FILE = "your-credentials.json"  # JSON fayl nomini to‘g‘rilang
SHEET_NAME = "BUYUR USERS"  # Google Sheets dagi varog‘ingiz nomi

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1  # Birinchi varoqni tanlash

# Holatlar (states)
NAME, PHONE = range(2)

# /start buyrug‘i
async def start(update: Update, context: CallbackContext) -> int:
    user_id = str(update.message.from_user.id)

    # Google Sheets-dagi barcha foydalanuvchilarni olish
    users_data = sheet.get_all_values()

    # Agar foydalanuvchi allaqachon ro‘yxatdan o‘tgan bo‘lsa
    if any(row[0] == user_id for row in users_data):
        await update.message.reply_text(
            "Siz allaqachon ro'yxatdan o'tgansiz!",
            reply_markup=ReplyKeyboardMarkup([["Buyurtma berish"]], resize_keyboard=True)
        )
        return ConversationHandler.END  # Ro‘yxatga olish tugaydi

    await update.message.reply_text(
        "Assalomu alaykum! Iltimos, ro‘yxatdan o‘tish uchun ismingizni yuboring."
    )
    return NAME  # Keyingi state: NAME

# Ismni qabul qilish
async def get_name(update: Update, context: CallbackContext) -> int:
    user_name = update.message.text
    context.user_data['name'] = user_name
    await update.message.reply_text(
        f"Rahmat, {user_name}! Endi siz bilan bog'lanish uchun telefon raqamingizni yuboring (masalan, +998901234567)."
    )
    return PHONE  # Keyingi state: PHONE

# Telefon raqamini qabul qilish va Google Sheets-ga yozish
async def get_phone(update: Update, context: CallbackContext) -> int:
    phone_number = update.message.text

    # Telefon raqamini tekshirish
    if not re.match(r"^\+998\d{9}$", phone_number):
        await update.message.reply_text(
            "Noto'g'ri telefon raqami formati. Iltimos, +998YYXXXXXXX formatida kiriting."
        )
        return PHONE  # Qaytadan telefon raqamini so‘rash

    user_id = str(update.message.from_user.id)
    telegram_id = str(update.message.chat.id)
    user_name = context.user_data['name']
    today_date = datetime.today().strftime("%Y-%m-%d")  # Bugungi sana

    # Google Sheets-dagi barcha foydalanuvchilarni olish
    users_data = sheet.get_all_values()

    # User ID ni aniqlash (0000, 0001, 0002 shaklda)
    next_user_id = f"{len(users_data):04d}"  # 0000 dan boshlab ketadigan ID yaratish

    # Agar foydalanuvchi allaqachon ro‘yxatdan o‘tgan bo‘lsa, xabar berish
    if any(row[0] == user_id for row in users_data):
        await update.message.reply_text(
            f"Rahmat {user_name}! Siz allaqachon ro'yxatdan o'tgansiz!",
            reply_markup=ReplyKeyboardMarkup([["Buyurtma berish"]], resize_keyboard=True)
        )
    else:
        # Google Sheets-ga yangi foydalanuvchini qo‘shish
        sheet.append_row([telegram_id, next_user_id, user_name, phone_number, today_date])
        await update.message.reply_text(
            f"Tabriklaymiz {user_name}! Siz muvaffaqiyatli ro‘yxatdan o‘tdingiz.",
            reply_markup=ReplyKeyboardMarkup([["Buyurtma berish"]], resize_keyboard=True)
        )

    return ConversationHandler.END

# "Buyurtma berish" tugmasi uchun funksiya
async def buyurtma_berish(update: Update, context: CallbackContext):
    url = "https://arm-buyur.netlify.app/"  # Buyurtma berish sahifangiz
    keyboard = [[InlineKeyboardButton("Buyurtma berish", url=url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Buyurtma berish uchun quyidagi tugmani bosing:",
        reply_markup=reply_markup
    )

# Bekor qilish funksiyasi
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Ro'yxatdan o'tish bekor qilindi.")
    return ConversationHandler.END

# Botni ishga tushirish
def main():
    TOKEN = "7924658985:AAERvkX_k-6Gxlbp0m2s1gcb6ujBzgxonVI"  # Bot tokeningizni yozing
    app = Application.builder().token(TOKEN).build()

    # ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Handlerlarni qo‘shish
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.Regex("^Buyurtma berish$"), buyurtma_berish))  

    app.run_polling()

if __name__ == "__main__":
    main()
