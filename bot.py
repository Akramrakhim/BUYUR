from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Foydalanuvchilar ma'lumotlarini saqlash uchun lug'at
users = {}

# /start buyrug'i
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Assalomu alaykum! Ro'yxatdan o'tish uchun ismingizni yuboring.")
    return "NAME"

# Ismni qabul qilish
def get_name(update: Update, context: CallbackContext):
    user_name = update.message.text
    context.user_data['name'] = user_name
    update.message.reply_text(f"Rahmat, {user_name}! Endi telefon raqamingizni yuboring (masalan, +998901234567).")
    return "PHONE"

# Telefon raqamini qabul qilish
def get_phone(update: Update, context: CallbackContext):
    phone_number = update.message.text
    user_id = update.message.from_user.id
    users[user_id] = {'name': context.user_data['name'], 'phone': phone_number}
    update.message.reply_text("Rahmat! Siz muvaffaqiyatli ro'yxatdan o'tdingiz.")
    return -1

# Botni ishga tushirish
def main():
    # Bot tokenini shu yerga yozing
    updater = Updater("7924658985:AAERvkX_k-6Gxlbp0m2s1gcb6ujBzgxonVI", use_context=True)
    dp = updater.dispatcher

    # Handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, get_name))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, get_phone))

    # Botni ishga tushirish
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()