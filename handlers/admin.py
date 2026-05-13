"""
Admin commands — only accessible by your Telegram user ID.
/admin    — dashboard with stats
/requests — see all leads and commission pipeline
/addvendor — guided flow to add a new vendor
"""

from telegram import Update
from telegram.ext import ContextTypes
from handlers.db import get_stats, get_all_requests, add_vendor, update_request_status
from config import ADMIN_IDS

def is_admin(user_id):
    return user_id in ADMIN_IDS

async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Not authorized.")
        return

    stats = get_stats()
    text = (
        f"🛠️ *Admin Dashboard*\n\n"
        f"📊 *Stats*\n"
        f"Active vendors: {stats['active_vendors']}\n"
        f"Total requests: {stats['total_requests']}\n"
        f"Booked: {stats['total_booked']}\n"
        f"Paid/closed: {stats['total_paid']}\n\n"
        f"💰 *Commission earned:* CAD ${stats['total_earned']:,.2f}\n\n"
        f"*Commands:*\n"
        f"/requests — view all leads\n"
        f"/addvendor — add a new vendor\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def admin_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show recent leads with their status."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Not authorized.")
        return

    requests = get_all_requests()
    if not requests:
        await update.message.reply_text("No requests yet. Share the bot to get leads!")
        return

    # Show last 10, newest first
    recent = list(reversed(requests))[:10]
    lines = [f"📋 *Last {len(recent)} requests*\n"]
    for r in recent:
        status_emoji = {"new": "🆕", "contacted": "📞", "booked": "✅", "paid": "💰"}.get(r["status"], "❓")
        commission_str = f" — CAD ${r['commission_earned']:,.0f} earned" if r["status"] == "paid" else ""
        lines.append(
            f"{status_emoji} `{r['id']}` | {r['couple_name']}\n"
            f"   → {r['vendor_name']} ({r['vendor_category']}){commission_str}\n"
            f"   {r['timestamp'][:10]}\n"
        )

    lines.append(
        "\n_To update a status, use:_\n"
        "`/status req_0001 booked 2500`\n"
        "(request_id, new_status, commission_earned)"
    )
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

async def admin_add_vendor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Quick add vendor via command args.
    Usage: /addvendor Name | Category | City | PriceFrom | Email | Commission%
    Example: /addvendor Bloom & Co | Florist | Montreal | 900 | bloom@email.com | 12
    """
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Not authorized.")
        return

    args_text = " ".join(context.args)
    if not args_text or "|" not in args_text:
        await update.message.reply_text(
            "Usage:\n`/addvendor Name | Category | City | PriceFrom | Email | Commission%`\n\n"
            "Example:\n`/addvendor Bloom & Co | Florist | Montreal | 900 | bloom@email.com | 12`",
            parse_mode="Markdown"
        )
        return

    parts = [p.strip() for p in args_text.split("|")]
    if len(parts) < 6:
        await update.message.reply_text("Need 6 fields separated by |. See usage above.")
        return

    try:
        vendor = {
            "name": parts[0],
            "category": parts[1],
            "city": parts[2],
            "price_from": int(parts[3]),
            "price_currency": "CAD",
            "description": f"{parts[1]} service based in {parts[2]}.",
            "languages": ["English", "French"],
            "instagram": "",
            "contact_email": parts[4],
            "contact_phone": "",
            "commission_pct": int(parts[5]),
            "featured": False,
        }
        new_id = add_vendor(vendor)
        await update.message.reply_text(
            f"✅ Vendor added!\n\n"
            f"*{vendor['name']}* — {vendor['category']}, {vendor['city']}\n"
            f"ID: `{new_id}` | Commission: {vendor['commission_pct']}%\n\n"
            f"Edit `data/vendors.json` to add description, Instagram, etc.",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# Handler for /status command to update lead pipeline
async def admin_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /status req_0001 booked 2500
    Updates a request status and optionally logs commission earned.
    """
    if not is_admin(update.effective_user.id):
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: `/status req_0001 booked [commission_amount]`", parse_mode="Markdown")
        return

    req_id = args[0]
    status = args[1]
    commission = float(args[2]) if len(args) >= 3 else None

    update_request_status(req_id, status, commission)
    msg = f"✅ `{req_id}` updated to *{status}*"
    if commission:
        msg += f"\n💰 Commission logged: CAD ${commission:,.2f}"
    await update.message.reply_text(msg, parse_mode="Markdown")
