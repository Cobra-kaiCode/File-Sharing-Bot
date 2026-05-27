import os
import logging
from logging.handlers import RotatingFileHandler

# =====================================================
# BotWorld4U FileStore Shortener Bot - ROOT CONFIG FILE
# =====================================================
# Fill all important details in THIS file before deploy.
# Keep your GitHub repo PRIVATE if you put bot token / MongoDB URL here.
# Bot must be admin in every DB channel and force-sub channel.
# Channel IDs must be numeric -100xxxxxxxxxx IDs, not @username.

# =====================================================
# 1) TELEGRAM BOT LOGIN
# =====================================================

# Bot token from @BotFather
TG_BOT_TOKEN = ""

# API ID and API HASH from https://my.telegram.org
APP_ID = 0
API_HASH = ""

# Your Telegram numeric user ID. Owner gets full access.
OWNER_ID = 0
OWNER_USERNAME = "BotWorld4U"  # without @


# =====================================================
# 2) MONGODB DATABASE
# =====================================================

# MongoDB connection URL
DATABASE_URL = ""

# MongoDB database name
DATABASE_NAME = "FileStoreShortner"


# =====================================================
# 3) DATABASE CHANNELS
# =====================================================

# Primary DB channel. Old links and default files use this first.
PRIMARY_DB_CHANNEL_ID = 0

# Extra DB channels. Bot rotates new files across primary + extras.
# Example: EXTRA_DB_CHANNEL_IDS = [-1001111111111, -1002222222222]
EXTRA_DB_CHANNEL_IDS = []


# =====================================================
# 4) FORCE SUBSCRIBE CHANNELS
# =====================================================

# Optional force-sub channels. Bot must be admin in these channels.
# Example: FORCE_SUB_CHANNELS = [-1001111111111, -1002222222222]
FORCE_SUB_CHANNELS = []

# 0 = invite links never expire. 10 = invite link expires after 10 minutes.
FSUB_LINK_EXPIRY = 10


# =====================================================
# 5) ADMINS
# =====================================================

# Admin user IDs. Owner is always admin, no need to add owner here.
# Example: ADMINS = [123456789, 987654321]
ADMINS = []


# =====================================================
# 6) BOT DEFAULT SETTINGS
# =====================================================

# True = restrict forward/save. False = users can forward/save.
PROTECT_CONTENT = False

# Pyrogram workers. 50 is safe for Heroku Eco/Basic.
TG_BOT_WORKERS = 50

# Web server port. Heroku provides PORT automatically; local fallback is 8001.
PORT = "8001"

# Heroku Web/Mini-App gateway URL.
# Fill this with your Heroku app URL after deploy, for example:
# WEB_APP_URL = "https://your-app-name.herokuapp.com"
# If you set HEROKU_APP_NAME env, the bot can auto-build this URL.
WEB_APP_URL = ""

# Always hide real shortener link behind Heroku mini-app gateway.
# No bot command is needed for this. Keep True.
HIDE_SHORTLINK_BEHIND_HEROKU = True

# Use Telegram Web App button for verify button.
# This makes the button open directly instead of showing the real short link in Telegram.
USE_WEBAPP_VERIFY_BUTTON = True

# Support link shown in ban/error messages.
BAN_SUPPORT = "https://t.me/BotWorld4U"

# Hide channel button below delivered files. Usually keep False.
DISABLE_CHANNEL_BUTTON = False


# =====================================================
# 7) SHORTENER / VERIFY SYSTEM
# =====================================================
# Safe shortener mode uses secure one-time tokens.
# It does NOT use weak yu3elk...7 bypass links.

SHORTENER_ENABLED = True

# Shortener domain and API from your shortener account.
# Example: SHORTLINK_URL = "linkshortify.com"
SHORTLINK_URL = ""
SHORTLINK_API = ""

# Tutorial button link shown with shortener page.
TUT_VID = "https://t.me/BotWorld4U"

SHORTENER_PIC = "https://telegra.ph/file/ec17880d61180d3312d6a.jpg"

SHORT_MSG = """<b>⌯ Here is your download link.</b>

<b>Must watch tutorial before clicking Download.</b>

<b>Credit:</b> @BotWorld4U"""

# Secure one-time verify token expiry in seconds.
# This is only for the shortener redirect token itself.
VERIFY_TOKEN_EXPIRE = 120

# Anti-bypass protection.
# Verify link expires in 2 minutes. If user returns too fast, it is counted as bypass.
BYPASS_MINIMUM_SECONDS = 50
BYPASS_BLOCK_SECONDS = 600
BYPASS_MAX_WARNINGS = 3

# Verification mode:
# "everytime"  = user must verify every file link.
# "timebased" = after verify, user can use file links without verify for VERIFY_TIME seconds.
VERIFY_MODE = "timebased"

# Time-based verification duration in seconds.
# Examples: 3600 = 1 hour, 21600 = 6 hours, 86400 = 24 hours, 604800 = 7 days.
VERIFY_TIME = 86400


# =====================================================
# 8) PREMIUM + REFERRAL SYSTEM
# =====================================================

# Premium contact / payment settings. You can edit here or set env vars on Heroku.
OWNER_TAG = os.environ.get("OWNER_TAG", "AnimeEmperor")
UPI_ID = os.environ.get("UPI_ID", "your-upi-id@upi")
QR_PIC = os.environ.get("QR_PIC", "https://telegra.ph/file/3e83c69804826b3cba066-16cffa90cd682570da.jpg")
SCREENSHOT_URL = os.environ.get("SCREENSHOT_URL", "https://t.me/BotWorld4U")
PREMIUM_BUTTON_TEXT = os.environ.get("PREMIUM_BUTTON_TEXT", "💎 Buy Premium / Send Screenshot")
PREMIUM_BUTTON_URL = os.environ.get("PREMIUM_BUTTON_URL", SCREENSHOT_URL)

# Referral reward: when a user gets 10 valid referrals, give 7 days premium.
# A referral is counted only after the invited user joins all force-sub channels.
REFERRAL_REWARD_COUNT = 10
REFERRAL_REWARD_DAYS = 7

PREMIUM_TEXT = """
<b><blockquote>›› ʜᴇʏ, {mention} ×</blockquote></b>

<b><blockquote>❐ 𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗠𝗘𝗧𝗛𝗢𝗗𝗦..!</blockquote></b>

<b>𝖯𝖠𝖸𝖳𝖬 • 𝖴𝖯𝖨 • 𝖯𝖧𝖮𝖭𝖤 𝖯𝖤 • 𝖦𝖯𝖠𝖸 • 𝖰𝖱.</b>

<b>✦ Pʀᴇᴍɪᴜᴍ ᴡɪʟʟ ʙᴇ ᴀᴅᴅᴇᴅ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴏɴᴄᴇ ᴘᴀɪᴅ</b>

<b>❐ NOTΕ : FORWARD & DOWNLOAD ΕNABLΕD ✅</b>

<b>✨ ᴄʜᴏᴏsᴇ ᴀ ᴘʟᴀɴ ʙᴇʟᴏᴡ:</b>

<b><blockquote>🏷 ᴘʀɪᴄɪɴɢ:

↻ ₹200 : 𝟣 ᴍᴏɴᴛʜ
↻ ₹500 : 𝟥 ᴍᴏɴᴛʜꜱ (ᴍᴏꜱᴛ ʙᴏᴜɢʜᴛ)
↻ ₹900 : 𝟨 ᴍᴏɴᴛʜꜱ
↻ ₹1,100 : 𝟫 ᴍᴏɴᴛʜꜱ
↻ ₹1,300 : 𝟣𝟤 ᴍᴏɴᴛʜꜱ
↻ ₹3,500 : ᴠɪᴘ / ʟɪꜰᴇᴛɪᴍᴇ ᴘʟᴀɴ
</blockquote></b>

<b><blockquote>🎁 𝗙𝗥𝗘𝗘 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗠𝗘𝗧𝗛𝗢𝗗

✨ ɪɴᴠɪᴛᴇ 10 ᴠᴀʟɪᴅ ᴜsᴇʀs ᴜsɪɴɢ /referral
✨ ᴀꜰᴛᴇʀ 10 sᴜᴄᴄᴇssꜰᴜʟ ɪɴᴠɪᴛᴇs → ɢᴇᴛ 7 ᴅᴀʏs ᴘʀᴇᴍɪᴜᴍ ғʀᴇᴇ 🎉
✨ ᴜsᴇʀ ᴍᴜsᴛ ᴊᴏɪɴ ᴀʟʟ ʀᴇQᴜɪʀᴇᴅ ᴄʜᴀɴɴᴇʟs ᴛᴏ ᴄᴏᴜɴᴛ
</blockquote></b>

<b><blockquote>➤ UPI ID: <code>{upi_id}</code>
➤ For Buying & Bonus Plan : @{owner_tag}</blockquote></b>
"""

# Old price variables kept for backward compatibility with older callback text.
PRICE1 = "₹200"
PRICE2 = "₹500"
PRICE3 = "₹900"
PRICE4 = "₹1,100"
PRICE5 = "₹1,300"


# =====================================================
# 9) START / FORCE-SUB PHOTO + TEXT
# =====================================================

START_PIC = "https://telegra.ph/file/ec17880d61180d3312d6a.jpg"
FORCE_PIC = "https://telegra.ph/file/e292b12890b8b4b9dcbd1.jpg"

START_MESSAGE = """<b>ʜᴇʟʟᴏ {mention}

<blockquote>ɪ ᴀᴍ ғɪʟᴇ sᴛᴏʀᴇ sʜᴏʀᴛᴇɴᴇʀ ʙᴏᴛ.
sᴇɴᴅ /commands ᴛᴏ sᴇᴇ ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs.</blockquote>

ᴄʀᴇᴅɪᴛ: @BotWorld4U</b>"""

FORCE_SUB_MESSAGE = """ʜᴇʟʟᴏ {mention}

<b><blockquote>ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ᴀɴᴅ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ ᴛʀʏ ᴀɢᴀɪɴ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ꜰɪʟᴇ.</blockquote></b>"""


# =====================================================
# 10) FILE CAPTION
# =====================================================

# Supported placeholders:
# {filename}  {filesize}  {filetype}  {caption}
CUSTOM_CAPTION = """<b>📁 File Name:</b> <code>{filename}</code>

<b>➤ Join:</b> @BotWorld4U"""


# =====================================================
# 11) OPTIONAL DEFAULT BUTTONS
# =====================================================

# You can also change buttons from bot PM using commands.
# Format: [("Button Text", "https://link.com")]
START_BUTTONS = [("📢 Updates", "https://t.me/BotWorld4U")]
FORCE_BUTTONS = []
REFERRAL_BUTTON = None  # Example: ("🤖 Start Our Bot", "https://t.me/YourBot?start=ref")


# =====================================================
# DO NOT EDIT BELOW THIS LINE UNLESS YOU KNOW PYTHON
# =====================================================


def _to_int(value, default: int = 0) -> int:
    try:
        return int(str(value).strip())
    except Exception:
        return default


def _to_bool(value, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on", "enable", "enabled"}


def _parse_ids(value):
    """Parse IDs from list/tuple/set or comma/space separated text."""
    ids = []
    if value is None:
        return ids
    if isinstance(value, (list, tuple, set)):
        parts = list(value)
    else:
        parts = str(value).replace(",", " ").split()

    for part in parts:
        try:
            item = int(str(part).strip())
        except Exception:
            continue
        if item != 0 and item not in ids:
            ids.append(item)
    return ids


def _normalize_buttons(value):
    """Accept [(text, url)] or [{'text': text, 'url': url}] and return DB-ready buttons."""
    buttons = []
    if not isinstance(value, (list, tuple)):
        return buttons
    for item in value:
        text = url = None
        if isinstance(item, dict):
            text = item.get("text")
            url = item.get("url")
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            text, url = item[0], item[1]
        if text and url:
            buttons.append({"text": str(text), "url": str(url)})
    return buttons


def _normalize_button(value):
    """Accept (text, url) or {'text': text, 'url': url}."""
    if isinstance(value, dict) and value.get("text") and value.get("url"):
        return {"text": str(value.get("text")), "url": str(value.get("url"))}
    if isinstance(value, (list, tuple)) and len(value) >= 2 and value[0] and value[1]:
        return {"text": str(value[0]), "url": str(value[1])}
    return None


# Normalize important values so the rest of the bot gets clean data.
TG_BOT_TOKEN = str(TG_BOT_TOKEN).strip()
APP_ID = _to_int(APP_ID, 0)
API_ID = APP_ID
API_HASH = str(API_HASH).strip()
OWNER_ID = _to_int(OWNER_ID, 0)
OWNER = str(OWNER_USERNAME).strip().lstrip("@")

PORT = str(os.environ.get("PORT", PORT)).strip()

WEB_APP_URL = str(os.environ.get("WEB_APP_URL", WEB_APP_URL)).strip().rstrip("/")
if not WEB_APP_URL and os.environ.get("HEROKU_APP_NAME"):
    WEB_APP_URL = f"https://{os.environ.get('HEROKU_APP_NAME')}.herokuapp.com"
HIDE_SHORTLINK_BEHIND_HEROKU = _to_bool(HIDE_SHORTLINK_BEHIND_HEROKU, True)
USE_WEBAPP_VERIFY_BUTTON = _to_bool(USE_WEBAPP_VERIFY_BUTTON, True)

DB_URI = str(DATABASE_URL).strip()
DB_NAME = str(DATABASE_NAME).strip() or "FileStoreShortner"
DATABASE_NAME = DB_NAME
DATABASE_URL = DB_URI

PRIMARY_DB_CHANNEL_ID = _to_int(PRIMARY_DB_CHANNEL_ID, 0)
PRIMARY_CHANNEL_ID = PRIMARY_DB_CHANNEL_ID

DB_CHANNEL_IDS = []
for cid in [PRIMARY_DB_CHANNEL_ID] + _parse_ids(EXTRA_DB_CHANNEL_IDS):
    if cid and cid not in DB_CHANNEL_IDS:
        DB_CHANNEL_IDS.append(cid)

CHANNEL_ID = PRIMARY_DB_CHANNEL_ID or (DB_CHANNEL_IDS[0] if DB_CHANNEL_IDS else 0)
CHANNEL_IDS = DB_CHANNEL_IDS
EXTRA_DB_CHANNEL_IDS = [cid for cid in DB_CHANNEL_IDS if cid != PRIMARY_DB_CHANNEL_ID]

FORCE_SUB_CHANNELS = _parse_ids(FORCE_SUB_CHANNELS)
ADMINS = [uid for uid in _parse_ids(ADMINS) if uid != OWNER_ID]
FSUB_LINK_EXPIRY = _to_int(FSUB_LINK_EXPIRY, 10)
TG_BOT_WORKERS = _to_int(TG_BOT_WORKERS, 50)
PROTECT_CONTENT = _to_bool(PROTECT_CONTENT, False)
DISABLE_CHANNEL_BUTTON = _to_bool(DISABLE_CHANNEL_BUTTON, False)
SHORTENER_ENABLED = _to_bool(SHORTENER_ENABLED, True)
VERIFY_TOKEN_EXPIRE = _to_int(VERIFY_TOKEN_EXPIRE, 120)
if VERIFY_TOKEN_EXPIRE < 30:
    VERIFY_TOKEN_EXPIRE = 120
BYPASS_MINIMUM_SECONDS = _to_int(BYPASS_MINIMUM_SECONDS if 'BYPASS_MINIMUM_SECONDS' in globals() else 50, 50)
BYPASS_BLOCK_SECONDS = _to_int(BYPASS_BLOCK_SECONDS if 'BYPASS_BLOCK_SECONDS' in globals() else 600, 600)
BYPASS_MAX_WARNINGS = _to_int(BYPASS_MAX_WARNINGS if 'BYPASS_MAX_WARNINGS' in globals() else 3, 3)
if BYPASS_MINIMUM_SECONDS < 5:
    BYPASS_MINIMUM_SECONDS = 50
if BYPASS_BLOCK_SECONDS < 60:
    BYPASS_BLOCK_SECONDS = 600
if BYPASS_MAX_WARNINGS < 1:
    BYPASS_MAX_WARNINGS = 3
VERIFY_MODE = str(VERIFY_MODE).strip().lower() if 'VERIFY_MODE' in globals() else "timebased"
if VERIFY_MODE not in {"everytime", "timebased"}:
    VERIFY_MODE = "timebased"
VERIFY_TIME = _to_int(VERIFY_TIME if 'VERIFY_TIME' in globals() else 86400, 86400)
if VERIFY_TIME < 60:
    VERIFY_TIME = 60

REFERRAL_REWARD_COUNT = _to_int(REFERRAL_REWARD_COUNT, 10)
if REFERRAL_REWARD_COUNT < 1:
    REFERRAL_REWARD_COUNT = 10
REFERRAL_REWARD_DAYS = _to_int(REFERRAL_REWARD_DAYS, 7)
if REFERRAL_REWARD_DAYS < 1:
    REFERRAL_REWARD_DAYS = 7

OWNER_TAG = str(OWNER_TAG).strip().lstrip("@")
UPI_ID = str(UPI_ID).strip()
QR_PIC = str(QR_PIC).strip()
SCREENSHOT_URL = str(SCREENSHOT_URL).strip()
PREMIUM_BUTTON_TEXT = str(PREMIUM_BUTTON_TEXT).strip() or "💎 Buy Premium / Send Screenshot"
PREMIUM_BUTTON_URL = str(PREMIUM_BUTTON_URL).strip() or SCREENSHOT_URL
PREMIUM_TEXT = str(PREMIUM_TEXT)

START_MSG = str(START_MESSAGE)
FORCE_MSG = str(FORCE_SUB_MESSAGE)
CUSTOM_CAPTION = str(CUSTOM_CAPTION)
START_BUTTONS = _normalize_buttons(START_BUTTONS)
FORCE_BUTTONS = _normalize_buttons(FORCE_BUTTONS)
REFERRAL_BUTTON = _normalize_button(REFERRAL_BUTTON)

HELP_TXT = """<b><blockquote>ᴛʜɪs ɪs ᴀ ғɪʟᴇ ᴛᴏ ʟɪɴᴋ ʙᴏᴛ ᴡᴏʀᴋ ғᴏʀ @BotWorld4U

❏ ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅs
├/start : sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ
├/about : ᴏᴜʀ Iɴғᴏʀᴍᴀᴛɪᴏɴ
└/help : ʜᴇʟᴘ ʀᴇʟᴀᴛᴇᴅ ʙᴏᴛ

ᴄʟɪᴄᴋ ᴏɴ ʟɪɴᴋ, ᴊᴏɪɴ ʀᴇǫᴜɪʀᴇᴅ ᴄʜᴀɴɴᴇʟs, ᴛʜᴇɴ ᴛʀʏ ᴀɢᴀɪɴ.

ᴄʀᴇᴅɪᴛ: <a href=https://t.me/BotWorld4U>@BotWorld4U</a></blockquote></b>"""

ABOUT_TXT = """<b><blockquote>◈ ᴄʀᴇᴅɪᴛ: <a href=https://t.me/BotWorld4U>@BotWorld4U</a>
◈ sᴜᴘᴘᴏʀᴛ / ᴜᴘᴅᴀᴛᴇs: <a href=https://t.me/BotWorld4U>BotWorld4U</a>
◈ ʙᴏᴛ ᴛʏᴘᴇ: ғɪʟᴇ sᴛᴏʀᴇ + sʜᴏʀᴛᴇɴᴇʀ + ᴘʀᴇᴍɪᴜᴍ ʙᴏᴛ</blockquote></b>"""

CMD_TXT = """<blockquote><b>» ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs:</b></blockquote>

<b>›› /start :</b> sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ
<b>›› /help :</b> ʜᴇʟᴘ
<b>›› /about :</b> ᴀʙᴏᴜᴛ ʙᴏᴛ
<b>›› /commands :</b> ᴄᴏᴍᴍᴀɴᴅ ʟɪsᴛ
<b>›› /genlink :</b> ʀᴇᴘʟʏ ᴛᴏ ғɪʟᴇ/ᴍᴇssᴀɢᴇ ᴛᴏ ᴄʀᴇᴀᴛᴇ ʟɪɴᴋ
<b>›› /batch :</b> ᴍᴀᴋᴇ ʙᴀᴛᴄʜ ғʀᴏᴍ ᴅʙ ᴘᴏsᴛs
<b>›› /custom_batch :</b> ᴄᴏʟʟᴇᴄᴛ ᴍᴜʟᴛɪᴘʟᴇ ғɪʟᴇs ᴀɴᴅ ᴍᴀᴋᴇ ʙᴀᴛᴄʜ
<b>›› /dbchannels :</b> ᴠɪᴇᴡ ᴘʀɪᴍᴀʀʏ/ᴇxᴛʀᴀ ᴅʙ ᴄʜᴀɴɴᴇʟs
<b>›› /checkdb :</b> ᴄʜᴇᴄᴋ ᴅʙ ᴄʜᴀɴɴᴇʟ ᴘᴇʀᴍɪssɪᴏɴ
<b>›› /adddbchannel :</b> ᴏᴡɴᴇʀ ᴀᴅᴅ ᴇxᴛʀᴀ ᴅʙ ᴄʜᴀɴɴᴇʟ
<b>›› /deldbchannel :</b> ᴏᴡɴᴇʀ ʀᴇᴍᴏᴠᴇ ᴇxᴛʀᴀ ᴅʙ ᴄʜᴀɴɴᴇʟ
<b>›› /setcaption :</b> sᴇᴛ ғɪʟᴇ ᴄᴀᴘᴛɪᴏɴ ᴡɪᴛʜ {filename}
<b>›› /caption :</b> ᴠɪᴇᴡ ᴄᴜʀʀᴇɴᴛ ᴄᴀᴘᴛɪᴏɴ
<b>›› /delcaption :</b> ʀᴇᴍᴏᴠᴇ ᴄᴜsᴛᴏᴍ ᴄᴀᴘᴛɪᴏɴ
<b>›› /testcaption :</b> ᴘʀᴇᴠɪᴇᴡ ᴄᴀᴘᴛɪᴏɴ
<b>›› /shortener :</b> sʜᴏʀᴛᴇɴᴇʀ ᴏɴ/ᴏғғ/sᴛᴀᴛᴜs
<b>›› /setshortener :</b> sᴇᴛ sʜᴏʀᴛᴇɴᴇʀ ᴅᴏᴍᴀɪɴ ᴀɴᴅ ᴀᴘɪ
<b>›› /shortsettings :</b> ᴠɪᴇᴡ sʜᴏʀᴛᴇɴᴇʀ sᴇᴛᴛɪɴɢs
<b>›› /verify_mode :</b> ᴏᴡɴᴇʀ sᴇᴛ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴍᴏᴅᴇ
<b>›› /set_verify_time :</b> ᴏᴡɴᴇʀ sᴇᴛ ᴛɪᴍᴇ-ʙᴀsᴇᴅ ᴠᴇʀɪғʏ ᴅᴜʀᴀᴛɪᴏɴ
<b>›› /bypass_settings :</b> ᴏᴡɴᴇʀ ᴠɪᴇᴡ ᴀɴᴛɪ-ʙʏᴘᴀss sᴇᴛᴛɪɴɢs
<b>›› /set_bypass_time :</b> ᴏᴡɴᴇʀ sᴇᴛ ᴍɪɴɪᴍᴜᴍ ᴡᴀɪᴛ ᴛɪᴍᴇ
<b>›› /set_bypass_block :</b> ᴏᴡɴᴇʀ sᴇᴛ ᴛᴇᴍᴘ ʙʟᴏᴄᴋ ᴛɪᴍᴇ
<b>›› /reset_bypass :</b> ᴏᴡɴᴇʀ ʀᴇsᴇᴛ ᴜsᴇʀ ʙʏᴘᴀss ᴡᴀʀɴɪɴɢs
<b>›› /addpremium :</b> ᴀᴅᴅ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀ
<b>›› /remove_premium :</b> ʀᴇᴍᴏᴠᴇ ᴘʀᴇᴍɪᴜᴍ
<b>›› /premium_users :</b> ʟɪsᴛ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs
<b>›› /myplan :</b> ᴄʜᴇᴄᴋ ᴘʀᴇᴍɪᴜᴍ sᴛᴀᴛᴜs
<b>›› /count :</b> ᴄᴏᴜɴᴛ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴs
<b>›› /premium :</b> ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ / ғʀᴇᴇ ᴘʀᴇᴍɪᴜᴍ ᴍᴇᴛʜᴏᴅ
<b>›› /referral :</b> ɢᴇᴛ ʏᴏᴜʀ ʀᴇғᴇʀʀᴀʟ ʟɪɴᴋ ᴀɴᴅ sᴛᴀᴛᴜs
<b>›› /addbutton :</b> ᴀᴅᴅ ᴄᴜsᴛᴏᴍ sᴛᴀʀᴛ/ғᴏʀᴄᴇ ʙᴜᴛᴛᴏɴ
<b>›› /delbutton :</b> ʀᴇᴍᴏᴠᴇ ᴄᴜsᴛᴏᴍ ʙᴜᴛᴛᴏɴ
<b>›› /buttons :</b> ᴠɪᴇᴡ ᴄᴜsᴛᴏᴍ ʙᴜᴛᴛᴏɴs
<b>›› /restriction :</b> ᴛᴜʀɴ ғɪʟᴇ ғᴏʀᴡᴀʀᴅ ʀᴇsᴛʀɪᴄᴛɪᴏɴ ᴏɴ/ᴏғғ
<b>›› /setstartpic :</b> ᴏᴡɴᴇʀ sᴇᴛ sᴛᴀʀᴛ ᴘɪᴄ
<b>›› /setforcepic :</b> ᴏᴡɴᴇʀ sᴇᴛ ғᴏʀᴄᴇ-sᴜʙ ᴘɪᴄ
<b>›› /setstartmsg :</b> ᴏᴡɴᴇʀ sᴇᴛ sᴛᴀʀᴛ ᴛᴇxᴛ
<b>›› /setforcemsg :</b> ᴏᴡɴᴇʀ sᴇᴛ ғᴏʀᴄᴇ-sᴜʙ ᴛᴇxᴛ
<b>›› /setrefbutton :</b> sᴇᴛ ғᴏʀᴄᴇ-sᴜʙ ʀᴇғᴇʀʀᴀʟ ʙᴜᴛᴛᴏɴ
<b>›› /setrefbot :</b> ǫᴜɪᴄᴋ sᴇᴛ ʙᴏᴛ ʀᴇғᴇʀʀᴀʟ ʙᴜᴛᴛᴏɴ
<b>›› /delrefbutton :</b> ʀᴇᴍᴏᴠᴇ ʀᴇғᴇʀʀᴀʟ ʙᴜᴛᴛᴏɴ
<b>›› /addchnl :</b> ᴀᴅᴅ ꜰᴏʀᴄᴇ sᴜʙ ᴄʜᴀɴɴᴇʟ
<b>›› /delchnl :</b> ʀᴇᴍᴏᴠᴇ ꜰᴏʀᴄᴇ sᴜʙ ᴄʜᴀɴɴᴇʟ
<b>›› /listchnl :</b> ᴠɪᴇᴡ ꜰᴏʀᴄᴇ-sᴜʙ ᴄʜᴀɴɴᴇʟs
<b>›› /fsub_mode :</b> ᴛᴏɢɢʟᴇ ꜰᴏʀᴄᴇ sᴜʙ ᴍᴏᴅᴇ
<b>›› /add_admin :</b> ᴀᴅᴅ ᴀɴ ᴀᴅᴍɪɴ
<b>›› /deladmin :</b> ʀᴇᴍᴏᴠᴇ ᴀɴ ᴀᴅᴍɪɴ
<b>›› /admins :</b> ʟɪsᴛ ᴀᴅᴍɪɴs
<b>›› /ban :</b> ʙᴀɴ ᴀ ᴜꜱᴇʀ
<b>›› /unban :</b> ᴜɴʙᴀɴ ᴀ ᴜꜱᴇʀ
<b>›› /banlist :</b> ʟɪsᴛ ʙᴀɴɴᴇᴅ ᴜꜱᴇʀs
<b>›› /broadcast :</b> ʙʀᴏᴀᴅᴄᴀsᴛ ᴍᴇssᴀɢᴇ
<b>›› /pbroadcast :</b> ʙʀᴏᴀᴅᴄᴀsᴛ ᴘʜᴏᴛᴏ
<b>›› /dbroadcast :</b> ʙʀᴏᴀᴅᴄᴀsᴛ ᴀɴᴅ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ
<b>›› /stats :</b> ᴜᴘᴛɪᴍᴇ
<b>›› /users :</b> ᴜsᴇʀ ᴄᴏᴜɴᴛ
<b>›› /dlt_time :</b> sᴇᴛ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇ
<b>›› /check_dlt_time :</b> ᴄʜᴇᴄᴋ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇ
<b>›› /delreq :</b> ᴄʟᴇᴀɴ ʟᴇғᴛᴏᴠᴇʀ ʀᴇǫᴜᴇsᴛ ᴜsᴇʀs
<b>›› /customsettings :</b> ᴠɪᴇᴡ ʙᴏᴛ ᴄᴜsᴛᴏᴍ sᴇᴛᴛɪɴɢs
<b>›› /resetcustom :</b> ᴏᴡɴᴇʀ ʀᴇsᴇᴛ ᴄᴜsᴛᴏᴍ sᴇᴛᴛɪɴɢs
<b>›› /ping :</b> ᴄʜᴇᴄᴋ ʙᴏᴛ ᴀʟɪᴠᴇ
<b>›› /restart :</b> ᴏᴡɴᴇʀ ʀᴇsᴛᴀʀᴛ ʙᴏᴛ
<b>›› /logs :</b> ᴏᴡɴᴇʀ ɢᴇᴛ ʟᴏɢ ғɪʟᴇ

ᴄʀᴇᴅɪᴛ: @BotWorld4U
"""

BOT_STATS_TEXT = "<b>BOT UPTIME</b>\n{uptime}"
USER_REPLY_TEXT = "ʙᴀᴋᴋᴀ ! ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴍʏ ꜱᴇɴᴘᴀɪ!!"
LOG_FILE_NAME = "filesharingbot.txt"

BOT_COMMANDS = [
    ("start", "Start the bot"),
    ("help", "Show help"),
    ("about", "About this bot"),
    ("commands", "Show all commands"),
    ("genlink", "Reply to file/message to create link"),
    ("batch", "Create batch link from DB posts"),
    ("custom_batch", "Collect messages and create batch"),
    ("dbchannels", "View primary and extra DB channels"),
    ("checkdb", "Check DB channel permission"),
    ("setcaption", "Set custom file caption"),
    ("caption", "View current caption"),
    ("testcaption", "Preview caption on a file"),
    ("shortener", "Shortener on/off/status"),
    ("setshortener", "Set shortener domain and API"),
    ("shortsettings", "View shortener settings"),
    ("verify_mode", "Owner: set verification mode"),
    ("set_verify_time", "Owner: set verify duration"),
    ("bypass_settings", "Owner: anti-bypass settings"),
    ("addpremium", "Add premium user"),
    ("remove_premium", "Remove premium user"),
    ("premium_users", "List premium users"),
    ("myplan", "Check premium status"),
    ("premium", "Buy premium / free premium method"),
    ("referral", "Get referral link and status"),
    ("count", "Count verifications"),
    ("restriction", "Protect content on/off"),
    ("addbutton", "Add custom button"),
    ("buttons", "View custom buttons"),
    ("listchnl", "View force-sub channels"),
    ("broadcast", "Broadcast message"),
    ("stats", "Bot stats"),
    ("ping", "Check bot alive"),
]

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler(LOG_FILE_NAME, maxBytes=50000000, backupCount=10),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
