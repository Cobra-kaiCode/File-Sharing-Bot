# BotWorld4U FileStore Shortener Bot

Fill all setup in root `config.py`.

## Main features
- Manual `/genlink` only: send file/message to bot PM, then reply `/genlink`.
- Strict start-link tamper protection.
- Secure shortener verification using one-time DB tokens. Weak `yu3elk...7` bypass is blocked.
- Hidden shortener link system using Heroku Mini-App gateway.
- Telegram verify button uses Heroku app URL, not the real shortener URL.
- Every verify token is user-locked, one-time, and expires quickly.
- Anti-bypass protection: too-fast verify return gives warning/block, 3 tries = ban.
- Time-based verification mode supported.
- Premium user system: premium users can skip shortener.
- Primary DB channel + multiple extra DB channels.
- Custom caption with `{filename}`, `{filesize}`, `{filetype}`, `{caption}`.
- Caption applied while saving into DB channel and while delivering to user.
- Force-sub channels with join-request mode.
- Force-sub referral button.
- Custom start/force messages and photos from bot PM.
- Custom buttons from bot PM.
- Restriction/protect content on/off.
- Auto BotFather command setup on deploy/start.
- Heroku web dyno auto start for bot + verify gateway.
- `/checkdb`, `/ping`, `/logs`, `/restart`.

## Required config

Edit root `config.py`:

```python
TG_BOT_TOKEN = "your token"
APP_ID = 12345
API_HASH = "your api hash"
OWNER_ID = 123456789
DATABASE_URL = "mongodb url"
PRIMARY_DB_CHANNEL_ID = -100xxxxxxxxxx
EXTRA_DB_CHANNEL_IDS = []
FORCE_SUB_CHANNELS = []
SHORTLINK_URL = "linkshortify.com"
SHORTLINK_API = "your api"

# Important for hidden shortlink mini-app gateway:
WEB_APP_URL = "https://your-heroku-app-name.herokuapp.com"
```

Bot must be admin in every DB channel with post/delete permissions.

## Heroku process

This version uses Heroku **web dyno**, because Heroku app URL only works on `web` process.

`Procfile`:

```text
web: python3 main.py
```

The same process runs both:

```text
Telegram bot + Heroku verify gateway
```

Do not run a second worker dyno with the same bot token, otherwise Telegram polling can duplicate/conflict.

## Hidden shortlink flow

```text
User opens file link
→ Bot creates unique verify token
→ Bot creates real shortener link internally
→ Bot stores real shortener link in MongoDB
→ Telegram button shows only https://your-app.herokuapp.com/v/TOKEN
→ Heroku mini-app opens
→ Heroku redirects server-side to real shortener link
→ Shortener finally returns user to /start verify_TOKEN
→ Bot checks user ID, token age, expiry, bypass warnings
→ File is sent if valid
```

So the real shortener URL is not shown in the Telegram message/button.

Credit: @BotWorld4U

## Referral + Premium Reward System

- Users can run `/referral` to get their personal invite link.
- Invite link format: `https://t.me/YourBot?start=ref_USERID`.
- A referral is counted only after the invited user joins all force-sub channels and opens the bot again.
- Default reward: every 10 valid referrals gives 7 days premium.
- When reward is given, bot sends a log message to the primary DB channel with inviter + referred user info.
- `/premium` shows payment details and free referral premium method.

Configure in root `config.py`:

```python
OWNER_TAG = "AnimeEmperor"
UPI_ID = "your-upi-id@upi"
QR_PIC = "https://telegra.ph/file/your_qr.jpg"
SCREENSHOT_URL = "https://t.me/BotWorld4U"
PREMIUM_BUTTON_TEXT = "💎 Buy Premium / Send Screenshot"
PREMIUM_BUTTON_URL = SCREENSHOT_URL
REFERRAL_REWARD_COUNT = 10
REFERRAL_REWARD_DAYS = 7
```
