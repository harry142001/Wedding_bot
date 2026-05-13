from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.db import (
    get_categories, get_vendors_by_category, get_all_vendors,
    get_vendor_by_id, save_request
)
from config import ADMIN_IDS

CAT_EMOJI = {
    "Photography": "📸",
    "Florist": "💐",
    "DJ & Music": "🎵",
    "Venue": "🏛",
    "Wedding Cake": "🎂",
    "Catering": "🍽",
    "Hair & Makeup": "💄",
    "Officiant": "📜",
    "Transportation": "🚗",
    "Videography": "🎥",
}

def cat_emoji(category):
    return CAT_EMOJI.get(category, "✨")

async def vendors_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    categories = get_categories()
    keyboard = []
    row = []
    for i, cat in enumerate(categories):
        row.append(InlineKeyboardButton(
            f"{cat_emoji(cat)} {cat}",
            callback_data=f"cat_{cat}"
        ))
        if len(row) == 2 or i == len(categories) - 1:
            keyboard.append(row)
            row = []
    keyboard.append([InlineKeyboardButton("Featured Vendors", callback_data="cat_featured")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "Browse Wedding Vendors\n\nChoose a category to get started:"
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)

async def vendor_category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cat = query.data.replace("cat_", "")
    if cat == "all":
        return await vendors_handler(update, context)
    if cat == "featured":
        vendors = [v for v in get_all_vendors() if v.get("featured")]
        title = "Featured Vendors"
    else:
        vendors = get_vendors_by_category(cat)
        title = f"{cat_emoji(cat)} {cat} Vendors"
    if not vendors:
        await query.edit_message_text("No vendors in this category yet. Check back soon!")
        return
    keyboard = []
    for v in vendors:
        featured_star = "★ " if v.get("featured") else ""
        label = f"{featured_star}{v['name']} - from {v['price_currency']} ${v['price_from']:,}"
        keyboard.append([InlineKeyboardButton(label, callback_data=f"vendor_{v['id']}")])
    keyboard.append([InlineKeyboardButton("Back to categories", callback_data="cat_all")])
    await query.edit_message_text(
        f"{title}\n\nTap a vendor to see full details:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def vendor_detail_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    vendor_id = query.data.replace("vendor_", "")
    vendor = get_vendor_by_id(vendor_id)
    if not vendor:
        await query.edit_message_text("Vendor not found. Please try again.")
        return
    langs = " / ".join(vendor.get("languages", []))
    featured = "Featured vendor\n" if vendor.get("featured") else ""
    ig = f"Instagram: {vendor['instagram']}\n" if vendor.get("instagram") else ""
    text = (
        f"{vendor['name']}\n"
        f"{cat_emoji(vendor['category'])} {vendor['category']} | {vendor['city']}\n\n"
        f"{featured}"
        f"{vendor['description']}\n\n"
        f"Starting from {vendor['price_currency']} ${vendor['price_from']:,}\n"
        f"Languages: {langs}\n"
        f"{ig}\n"
        f"Interested? Tap below and I will personally connect you within 24 hours."
    )
    keyboard = [
        [InlineKeyboardButton("Request Contact", callback_data=f"request_{vendor_id}")],
        [InlineKeyboardButton("Back", callback_data=f"cat_{vendor['category']}")]
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def vendor_request_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    vendor_id = query.data.replace("request_", "")
    vendor = get_vendor_by_id(vendor_id)
    user = query.from_user
    if not vendor:
        await query.edit_message_text("Something went wrong. Please try /vendors again.")
        return
    req = save_request(
        couple_user_id=user.id,
        couple_username=user.username,
        couple_name=f"{user.first_name} {user.last_name or ''}".strip(),
        vendor_id=vendor_id
    )
    await query.edit_message_text(
        f"Request sent!\n\n"
        f"I have received your interest in {vendor['name']}.\n\n"
        f"I will personally reach out to connect you within 24 hours.\n\n"
        f"Request ID: {req['id']}"
    )
    commission_estimate = vendor["price_from"] * (vendor.get("commission_pct", 10) / 100)
    admin_msg = (
        f"New vendor request!\n\n"
        f"Couple: {req['couple_name']} (@{req['couple_username']})\n"
        f"Telegram ID: {user.id}\n\n"
        f"Vendor: {vendor['name']}\n"
        f"Category: {vendor['category']}\n"
        f"Price from: {vendor['price_currency']} ${vendor['price_from']:,}\n\n"
        f"Your commission estimate: {vendor['price_currency']} ${commission_estimate:,.0f} ({vendor.get('commission_pct', 10)}%)\n\n"
        f"Request ID: {req['id']}\n"
        f"Next step: Message the couple and intro them to the vendor!"
    )
    bot = context.bot
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_msg)
        except Exception:
            pass