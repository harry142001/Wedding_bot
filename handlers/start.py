from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

WELCOME_TEXT = """
💍 *Welcome to WeddingConnect Bot!*

I help you find and connect with the best local wedding vendors — photographers, florists, DJs, venues, and more.

All vendors are personally reviewed. When you request a contact, I'll personally reach out to connect you within 24 hours.

*What I can do:*
🏪 /vendors — Browse vendors by category
❓ /help — How this works

Let's make your wedding unforgettable! ✨
"""

HELP_TEXT = """
*How WeddingConnect works:*

1️⃣ Browse vendors with /vendors
2️⃣ Tap a vendor to see full details
3️⃣ Tap *Request Contact* when you're interested
4️⃣ I personally connect you with the vendor within 24 hours
5️⃣ All bookings are assisted — no hidden fees for you

*Why use us?*
✅ All vendors pre-vetted
✅ Personal introduction (no cold emails)
✅ Help negotiating if needed
✅ Available in English & French

Questions? Message me directly here anytime.
"""

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🏪 Browse Vendors", callback_data="cat_all")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        WELCOME_TEXT,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")
