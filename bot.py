"""
Wedding Planner Telegram Bot
Your middleware commission model:
  Couple → sees vendor in bot → clicks "Request Contact" → you get notified → you connect them → you earn
"""

import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, ContextTypes, filters
)
from handlers.start import start_handler, help_handler
from handlers.vendors import (
    vendors_handler, vendor_category_handler,
    vendor_detail_handler, vendor_request_handler
)
from handlers.admin import admin_handler, admin_add_vendor, admin_requests
from config import BOT_TOKEN

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Public commands
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("vendors", vendors_handler))

    # Admin commands (only you can use these)
    app.add_handler(CommandHandler("admin", admin_handler))
    app.add_handler(CommandHandler("addvendor", admin_add_vendor))
    app.add_handler(CommandHandler("requests", admin_requests))

    # Button callbacks
    app.add_handler(CallbackQueryHandler(vendor_category_handler, pattern="^cat_"))
    app.add_handler(CallbackQueryHandler(vendor_detail_handler, pattern="^vendor_"))
    app.add_handler(CallbackQueryHandler(vendor_request_handler, pattern="^request_"))

    logger.info("Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
