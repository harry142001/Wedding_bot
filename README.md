# 💍 WeddingConnect Telegram Bot

Your middleware commission model:
**Couple → requests vendor → you get notified → you connect them → you earn commission**

## Quick start (5 steps)

### 1. Get a bot token
- Message @BotFather on Telegram
- Send `/newbot`, follow prompts
- Copy the token it gives you

### 2. Get your Telegram user ID
- Message @userinfobot on Telegram
- It replies with your numeric user ID (e.g. 123456789)

### 3. Set up environment
```bash
cp .env.example .env
# Edit .env with your BOT_TOKEN and ADMIN_ID
```

### 4. Install and run
```bash
pip install -r requirements.txt
python bot.py
```

### 5. Test it
- Search for your bot on Telegram
- Send /start — you should see the welcome message
- Browse vendors, request one — check that you get notified

---

## How the money flows

1. Couple finds a vendor through your bot
2. They tap **Request Contact**
3. **You get a Telegram notification** with:
   - Couple's name + Telegram handle
   - Vendor details
   - Your estimated commission (e.g. CAD $250)
4. You message the couple, make the intro
5. Vendor pays you commission when they book

## Admin commands (only you)

| Command | What it does |
|---|---|
| `/admin` | Dashboard: stats + total earned |
| `/requests` | See all leads + their status |
| `/addvendor Name \| Category \| City \| Price \| Email \| Commission%` | Add a new vendor |
| `/status req_0001 booked 2500` | Update lead status + log commission |

## Adding vendors

**Quick way:** `/addvendor Bloom & Co | Florist | Montreal | 900 | bloom@email.com | 12`

**Full way:** Edit `data/vendors.json` directly — add description, Instagram, featured flag, languages.

## Deploying (so it runs 24/7)

### Free option: Railway.app
1. Push code to GitHub (private repo)
2. Go to railway.app → New Project → Deploy from GitHub
3. Add environment variables (BOT_TOKEN, ADMIN_ID)
4. Deploy — runs forever free tier

### Free option: Render.com
Same process. Free tier spins down after inactivity — use Railway instead.

## File structure

```
wedding_bot/
├── bot.py              # Entry point
├── config.py           # Environment config
├── requirements.txt
├── .env.example
├── data/
│   └── vendors.json    # Your vendor database + leads
└── handlers/
    ├── db.py           # Read/write JSON database
    ├── start.py        # /start and /help
    ├── vendors.py      # Browse vendors, request contact
    └── admin.py        # Admin-only commands
```

## Scaling up later

- Replace `data/vendors.json` with Supabase (free PostgreSQL)
- Add `/mywedding` to let couples save their wedding date
- Add guest list management
- Build a web dashboard for vendors to manage their own listings
- Add Stripe for couples to pay deposits directly

## Commission rate guide

| Category | Typical range |
|---|---|
| Photography | 8–12% |
| Venue | 5–10% |
| Florist | 10–15% |
| DJ / Music | 10–12% |
| Catering | 5–8% |
| Hair & Makeup | 10–15% |

Start at 10% flat while you're getting started. Negotiate with each vendor individually.
