from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
)
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import re

# PostgreSQL-ga ulanish
DB_URL = "postgresql://postgres:oM0NjgIQyas9@localhost:5432/BUYUR"  # Ulanish ma'lumotlarini to'g'rilang
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)

Base = declarative_base()

# Foydalanuvchilar jadvali
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)

Base.metadata.create_all(engine)

# Holatlar (states)
NAME, PHONE = range(2)

# /start buyrug‘i
async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Assalomu alaykum! BUYUR - tezkor yetkazib berish xizmatiga xush kelibsiz! Iltimos ro‘yxatdan o‘tish uchun ismingizni yuboring.")
    return NAME  # Keyingi state: NAME

# Ismni qabul qilish
async def get_name(update: Update, context: CallbackContext) -> int:
    user_name = update.message.text
    context.user_data['name'] = user_name
    await update.message.reply_text(f"Rahmat, {user_name}! Endi telefon raqamingizni yuboring (masalan, +998901234567).")
    return PHONE  # Keyingi state: PHONE

# Telefon raqamini qabul qilish
async def get_phone(update: Update, context: CallbackContext) -> int:
    phone_number = update.message.text
    
    # Telefon raqamini tekshirish
    if not re.match(r"^\+998\d{9}$", phone_number):
        await update.message.reply_text("Noto'g'ri telefon raqami formati. Iltimos, +998YYXXXXXXX formatida kiriting.")
        return PHONE  # Qaytadan telefon raqamini so'rash
    
    user_id = update.message.from_user.id
    user_name = context.user_data['name']
    
    try:
        # Har bir so'rov uchun yangi ulanish ochish
        session = Session()
        
        # Foydalanuvchini bazadan qidirish
        existing_user = session.query(User).filter(User.telegram_id == user_id).first()
        
        if existing_user:
            # Agar foydalanuvchi allaqachon mavjud bo'lsa
            await update.message.reply_text(
                f"Rahmat {user_name}! Siz allaqachon ro'yxatdan o'tgansiz!",
                reply_markup=ReplyKeyboardMarkup([["Buyurtma berish"]], resize_keyboard=True)
            )
        else:
            # Yangi foydalanuvchini qo'shish
            new_user = User(telegram_id=user_id, name=user_name, phone=phone_number)
            session.add(new_user)
            session.commit()
            await update.message.reply_text(
                f"Rahmat {user_name}! Siz muvaffaqiyatli ro‘yxatdan o‘tdingiz.",
                reply_markup=ReplyKeyboardMarkup([["Buyurtma berish"]], resize_keyboard=True)
            )
    except Exception as e:
        await update.message.reply_text(f"Xatolik yuz berdi: {e}. Iltimos, qayta urinib ko'ring.")
    finally:
        session.close()  # Ulanishni yopish
    
    return ConversationHandler.END

# "Buyurtma berish" tugmasi uchun funksiya
async def buyurtma_berish(update: Update, context: CallbackContext):
    # Havola (URL) ni belgilang
    url = "https://arm-buyur.netlify.app/"  # O'z saytingizning havolasini qo'ying
    
    # InlineKeyboardButton yaratish
    keyboard = [[InlineKeyboardButton("Buyurtma berish", url=url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Foydalanuvchiga xabar va tugma yuborish
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
    # Bot tokenini shu yerga yozing
    TOKEN = "7924658985:AAERvkX_k-6Gxlbp0m2s1gcb6ujBzgxonVI"  # O'z tokenizingizni qo'ying
    
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
    app.add_handler(MessageHandler(filters.Regex("^Buyurtma berish$"), buyurtma_berish))  # "Buyurtma berish" tugmasi uchun

    # Botni ishga tushirish
    app.run_polling()

if __name__ == "__main__":
    main()