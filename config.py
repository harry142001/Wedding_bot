"""
Configuration — copy this to .env and fill in your values.
Never commit .env to git.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Get this from @BotFather on Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Your personal Telegram user ID (get it from @userinfobot)
# Only this ID can use /admin, /addvendor, /requests
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Commission rate you charge vendors (shown to you, not couples)
COMMISSION_RATE = float(os.getenv("COMMISSION_RATE", "0.10"))  # 10%

# Optional: second admin (partner, VA)
ADMIN_IDS = [ADMIN_ID]
