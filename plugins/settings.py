import re
import html
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from bot import Bot
from config import OWNER_ID, START_PIC, FORCE_PIC, START_MSG, FORCE_MSG, PROTECT_CONTENT, CUSTOM_CAPTION, DB_CHANNEL_IDS, PRIMARY_DB_CHANNEL_ID, SHORTENER_ENABLED, SHORTLINK_URL, SHORTLINK_API, SHORTENER_PIC, SHORT_MSG, TUT_VID, VERIFY_MODE, VERIFY_TIME, VERIFY_TOKEN_EXPIRE, BYPASS_MINIMUM_SECONDS, BYPASS_BLOCK_SECONDS, BYPASS_MAX_WARNINGS
from helper_func import admin, str_to_bool, reload_db_channels, format_file_caption, message_supports_caption
from database.database import db


VALID_PLACES = {"start", "force"}
URL_RE = re.compile(r"^https?://", re.IGNORECASE)


def close_markup():
    return InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])


def _extract_text_after_command(message: Message):
    parts = message.text.split(maxsplit=1) if message.text else []
    return parts[1].strip() if len(parts) > 1 else ""


def _get_replied_text(message: Message):
    if message.reply_to_message:
        if message.reply_to_message.text:
            return message.reply_to_message.text.html
        if message.reply_to_message.caption:
            return message.reply_to_message.caption.html
    return None


async def _owner_only(message: Message):
    if message.from_user.id != OWNER_ID:
        await message.reply_text("<b>❌ Only owner can use this command.</b>", reply_markup=close_markup())
        return False
    return True


def _parse_duration_to_seconds(value: str):
    """Parse 30m, 6h, 1d, 7days, or raw seconds."""
    value = (value or "").strip().lower().replace(" ", "")
    if not value:
        return None
    match = re.fullmatch(r"(\d+)(s|sec|secs|second|seconds|m|min|mins|minute|minutes|h|hr|hrs|hour|hours|d|day|days)?", value)
    if not match:
        return None
    num = int(match.group(1))
    unit = match.group(2) or "s"
    if unit in {"s", "sec", "secs", "second", "seconds"}:
        seconds = num
    elif unit in {"m", "min", "mins", "minute", "minutes"}:
        seconds = num * 60
    elif unit in {"h", "hr", "hrs", "hour", "hours"}:
        seconds = num * 3600
    elif unit in {"d", "day", "days"}:
        seconds = num * 86400
    else:
        return None
    return max(seconds, 1)


def _format_duration(seconds: int):
    try:
        seconds = int(seconds)
    except Exception:
        seconds = int(VERIFY_TIME)
    if seconds % 86400 == 0:
        return f"{seconds // 86400} day(s)"
    if seconds % 3600 == 0:
        return f"{seconds // 3600} hour(s)"
    if seconds % 60 == 0:
        return f"{seconds // 60} minute(s)"
    return f"{seconds} second(s)"


async def _verify_mode_status_text():
    enabled = str_to_bool(await db.get_setting("shortener_enabled", SHORTENER_ENABLED))
    mode = str(await db.get_setting("verify_mode", VERIFY_MODE)).strip().lower()
    if mode not in {"everytime", "timebased"}:
        mode = "timebased"
    verify_seconds = int(await db.get_setting("verify_time_seconds", VERIFY_TIME))
    token_expire = int(await db.get_setting("verify_token_expire_seconds", VERIFY_TOKEN_EXPIRE))
    min_wait = int(await db.get_setting("bypass_minimum_seconds", BYPASS_MINIMUM_SECONDS))
    block_time = int(await db.get_setting("bypass_block_seconds", BYPASS_BLOCK_SECONDS))
    max_warn = int(await db.get_setting("bypass_max_warnings", BYPASS_MAX_WARNINGS))
    return (
        "<b>🔐 Verification Mode Settings</b>\n\n"
        f"<b>Shortener:</b> {'ON ✅' if enabled else 'OFF ❌'}\n"
        f"<b>Verify Mode:</b> <code>{mode}</code>\n"
        f"<b>Time-based duration:</b> <code>{_format_duration(verify_seconds)}</code>\n"
        f"<b>One verify link validity:</b> <code>{_format_duration(token_expire)}</code>\n"
        f"<b>Bypass minimum wait:</b> <code>{_format_duration(min_wait)}</code>\n"
        f"<b>Bypass temp block:</b> <code>{_format_duration(block_time)}</code>\n"
        f"<b>Ban after warnings:</b> <code>{max_warn}</code>\n\n"
        "<b>Buttons:</b>\n"
        "ON/OFF controls shortener gate.\n"
        "Everytime means user verifies every file.\n"
        "Time Based means after verify, user can use links for set time.\n\n"
        "Set time with: <code>/set_verify_time 24h</code>"
    )


def _verify_mode_markup():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Shortener ON", callback_data="verify_mode_short_on"),
            InlineKeyboardButton("❌ Shortener OFF", callback_data="verify_mode_short_off"),
        ],
        [
            InlineKeyboardButton("♻️ Every Time", callback_data="verify_mode_everytime"),
            InlineKeyboardButton("⏱ Time Based", callback_data="verify_mode_timebased"),
        ],
        [InlineKeyboardButton("🔄 Refresh", callback_data="verify_mode_refresh")],
        [InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")],
    ])


@Bot.on_message(filters.command("addbutton") & filters.private & admin)
async def add_button_cmd(client: Client, message: Message):
    """
    Usage:
    /addbutton start Button Text | https://example.com
    /addbutton force Button Text | https://example.com
    """
    args = _extract_text_after_command(message)
    if not args:
        return await message.reply_text(
            "<b>Usage:</b>\n"
            "<code>/addbutton start Button Text | https://example.com</code>\n"
            "<code>/addbutton force Button Text | https://example.com</code>",
            reply_markup=close_markup()
        )

    try:
        place, rest = args.split(maxsplit=1)
    except ValueError:
        return await message.reply_text("<b>❌ Wrong format.</b> Use: <code>/addbutton start Text | Link</code>", reply_markup=close_markup())

    place = place.lower().strip()
    if place not in VALID_PLACES:
        return await message.reply_text("<b>❌ Place must be:</b> <code>start</code> or <code>force</code>", reply_markup=close_markup())

    if "|" not in rest:
        return await message.reply_text("<b>❌ Use separator:</b> <code>Button Text | https://link</code>", reply_markup=close_markup())

    text, url = [x.strip() for x in rest.split("|", 1)]
    if not text or not url or not URL_RE.match(url):
        return await message.reply_text("<b>❌ Invalid button text or URL. URL must start with http:// or https://</b>", reply_markup=close_markup())

    buttons = await db.add_button(place, text, url)
    await message.reply_text(
        f"<b>✅ Button added to <code>{place}</code>.</b>\n\n"
        f"<b>#{len(buttons)}</b> {text}\n<code>{url}</code>",
        reply_markup=close_markup(),
        disable_web_page_preview=True
    )


@Bot.on_message(filters.command("delbutton") & filters.private & admin)
async def del_button_cmd(client: Client, message: Message):
    """
    Usage:
    /delbutton start 1
    /delbutton force all
    """
    args = _extract_text_after_command(message).split()
    if len(args) != 2:
        return await message.reply_text(
            "<b>Usage:</b>\n"
            "<code>/delbutton start 1</code>\n"
            "<code>/delbutton force all</code>",
            reply_markup=close_markup()
        )

    place, index = args[0].lower(), args[1].lower()
    if place not in VALID_PLACES:
        return await message.reply_text("<b>❌ Place must be:</b> <code>start</code> or <code>force</code>", reply_markup=close_markup())

    if index == "all":
        await db.clear_buttons(place)
        return await message.reply_text(f"<b>✅ All <code>{place}</code> buttons removed.</b>", reply_markup=close_markup())

    try:
        index_int = int(index)
    except ValueError:
        return await message.reply_text("<b>❌ Index must be number or all.</b>", reply_markup=close_markup())

    ok = await db.del_button(place, index_int)
    if ok:
        await message.reply_text(f"<b>✅ Button #{index_int} removed from <code>{place}</code>.</b>", reply_markup=close_markup())
    else:
        await message.reply_text("<b>❌ Button index not found.</b>", reply_markup=close_markup())


@Bot.on_message(filters.command("buttons") & filters.private & admin)
async def list_buttons_cmd(client: Client, message: Message):
    text = "<b>📌 Custom Buttons</b>\n\n"
    for place in ("start", "force"):
        buttons = await db.get_buttons(place)
        text += f"<b>{place.upper()}:</b>\n"
        if not buttons:
            text += "<i>No custom buttons.</i>\n\n"
            continue
        for i, btn in enumerate(buttons, start=1):
            text += f"<b>{i}.</b> {btn.get('text')}\n<code>{btn.get('url')}</code>\n"
        text += "\n"
    await message.reply_text(text, reply_markup=close_markup(), disable_web_page_preview=True)


@Bot.on_message(filters.command(["restriction", "protect"]) & filters.private & admin)
async def restriction_cmd(client: Client, message: Message):
    """
    Protect/restrict content forwarding from bot.
    Usage: /restriction on or /restriction off
    """
    args = _extract_text_after_command(message).lower()
    if args not in {"on", "off", "status"}:
        current = str_to_bool(await db.get_setting("protect_content", PROTECT_CONTENT))
        return await message.reply_text(
            f"<b>Current Restriction:</b> {'ON ✅' if current else 'OFF ❌'}\n\n"
            "<b>Usage:</b>\n"
            "<code>/restriction on</code> - users cannot forward/save easily\n"
            "<code>/restriction off</code> - normal files",
            reply_markup=close_markup()
        )

    if args == "status":
        current = str_to_bool(await db.get_setting("protect_content", PROTECT_CONTENT))
        return await message.reply_text(f"<b>Restriction is:</b> {'ON ✅' if current else 'OFF ❌'}", reply_markup=close_markup())

    value = args == "on"
    await db.set_setting("protect_content", value)
    await message.reply_text(f"<b>✅ Restriction set to:</b> {'ON' if value else 'OFF'}", reply_markup=close_markup())




@Bot.on_message(filters.command("shortener") & filters.private & admin)
async def shortener_toggle_cmd(client: Client, message: Message):
    if not await _owner_only(message):
        return
    args = _extract_text_after_command(message).lower()
    if args not in {"on", "off", "status"}:
        current = str_to_bool(await db.get_setting("shortener_enabled", SHORTENER_ENABLED))
        return await message.reply_text(
            f"<b>Current Shortener:</b> {'ON ✅' if current else 'OFF ❌'}\n\n"
            "<b>Usage:</b>\n"
            "<code>/shortener on</code>\n"
            "<code>/shortener off</code>\n"
            "<code>/shortener status</code>",
            reply_markup=close_markup()
        )

    if args == "status":
        current = str_to_bool(await db.get_setting("shortener_enabled", SHORTENER_ENABLED))
        return await message.reply_text(f"<b>Shortener is:</b> {'ON ✅' if current else 'OFF ❌'}", reply_markup=close_markup())

    value = args == "on"
    await db.set_setting("shortener_enabled", value)
    await message.reply_text(f"<b>✅ Shortener set to:</b> {'ON' if value else 'OFF'}", reply_markup=close_markup())


@Bot.on_message(filters.command("setshortener") & filters.private & admin)
async def set_shortener_cmd(client: Client, message: Message):
    if not await _owner_only(message):
        return
    args = _extract_text_after_command(message)
    if not args:
        return await message.reply_text(
            "<b>Usage:</b>\n"
            "<code>/setshortener domain.com API_KEY</code>\n\n"
            "Example:\n"
            "<code>/setshortener linkshortify.com 123456</code>",
            reply_markup=close_markup()
        )

    parts = args.split(maxsplit=1)
    if len(parts) != 2:
        return await message.reply_text("<b>❌ Send both domain and API key.</b>", reply_markup=close_markup())

    domain = parts[0].replace("https://", "").replace("http://", "").strip("/")
    api = parts[1].strip()
    await db.set_setting("shortlink_url", domain)
    await db.set_setting("shortlink_api", api)

    await message.reply_text(
        f"<b>✅ Shortener updated.</b>\n\n<b>Domain:</b> <code>{domain}</code>\n<b>API:</b> <code>{api[:5]}***</code>",
        reply_markup=close_markup(),
        disable_web_page_preview=True
    )


@Bot.on_message(filters.command("setshortpic") & filters.private & admin)
async def set_short_pic_cmd(client: Client, message: Message):
    if not await _owner_only(message):
        return
    pic = _extract_text_after_command(message)
    if message.reply_to_message and message.reply_to_message.photo:
        pic = message.reply_to_message.photo.file_id

    if not pic:
        return await message.reply_text(
            "<b>Usage:</b>\n"
            "<code>/setshortpic https://image-link</code>\n"
            "or reply to a photo with <code>/setshortpic</code>",
            reply_markup=close_markup()
        )

    await db.set_setting("shortener_pic", pic)
    await message.reply_text("<b>✅ Shortener photo updated.</b>", reply_markup=close_markup())


@Bot.on_message(filters.command("setshortmsg") & filters.private & admin)
async def set_short_msg_cmd(client: Client, message: Message):
    if not await _owner_only(message):
        return
    text = _get_replied_text(message) or _extract_text_after_command(message)
    if not text:
        return await message.reply_text(
            "<b>Usage:</b>\n"
            "<code>/setshortmsg Your shortener page message</code>\n"
            "or reply to text/caption with <code>/setshortmsg</code>",
            reply_markup=close_markup()
        )

    await db.set_setting("short_msg", text)
    await message.reply_text("<b>✅ Shortener message updated.</b>", reply_markup=close_markup())


@Bot.on_message(filters.command("settutorial") & filters.private & admin)
async def set_tutorial_cmd(client: Client, message: Message):
    if not await _owner_only(message):
        return
    url = _extract_text_after_command(message)
    if not url or not URL_RE.match(url):
        return await message.reply_text("<b>Usage:</b> <code>/settutorial https://t.me/...</code>", reply_markup=close_markup())

    await db.set_setting("tutorial_url", url)
    await message.reply_text("<b>✅ Tutorial URL updated.</b>", reply_markup=close_markup(), disable_web_page_preview=True)


@Bot.on_message(filters.command("shortsettings") & filters.private & admin)
async def short_settings_cmd(client: Client, message: Message):
    enabled = str_to_bool(await db.get_setting("shortener_enabled", SHORTENER_ENABLED))
    domain = await db.get_setting("shortlink_url", SHORTLINK_URL)
    api = await db.get_setting("shortlink_api", SHORTLINK_API)
    pic = await db.get_setting("shortener_pic", SHORTENER_PIC)
    tutorial = await db.get_setting("tutorial_url", TUT_VID)
    msg = await db.get_setting("short_msg", SHORT_MSG)

    text = (
        "<b>🔗 Shortener Settings</b>\n\n"
        f"<b>Status:</b> {'ON ✅' if enabled else 'OFF ❌'}\n"
        f"<b>Verify Mode:</b> <code>{str(await db.get_setting('verify_mode', VERIFY_MODE)).strip().lower()}</code>\n"
        f"<b>Verify Time:</b> <code>{_format_duration(int(await db.get_setting('verify_time_seconds', VERIFY_TIME)))}</code>\n"
        f"<b>One verify link validity:</b> <code>{_format_duration(int(await db.get_setting('verify_token_expire_seconds', VERIFY_TOKEN_EXPIRE)))}</code>\n"
        f"<b>Bypass minimum wait:</b> <code>{_format_duration(int(await db.get_setting('bypass_minimum_seconds', BYPASS_MINIMUM_SECONDS)))}</code>\n"
        f"<b>Bypass block:</b> <code>{_format_duration(int(await db.get_setting('bypass_block_seconds', BYPASS_BLOCK_SECONDS)))}</code>\n"
        f"<b>Ban after warnings:</b> <code>{int(await db.get_setting('bypass_max_warnings', BYPASS_MAX_WARNINGS))}</code>\n"
        f"<b>Domain:</b> <code>{domain or 'not set'}</code>\n"
        f"<b>API:</b> <code>{'set' if api else 'not set'}</code>\n"
        f"<b>Tutorial:</b> <code>{tutorial}</code>\n"
        f"<b>Photo:</b> <code>{pic}</code>\n\n"
        "<b>Message:</b>\n"
        f"<code>{html.escape(str(msg))}</code>"
    )
    await message.reply_text(text, reply_markup=close_markup(), disable_web_page_preview=True)



@Bot.on_message(filters.command(["verify_mode", "verifiy_mode"]) & filters.private)
async def verify_mode_cmd(client: Client, message: Message):
    if not await _owner_only(message):
        return
    await message.reply_text(
        await _verify_mode_status_text(),
        reply_markup=_verify_mode_markup(),
        disable_web_page_preview=True
    )


@Bot.on_message(filters.command(["set_verify_time", "verify_time", "setverifytime"]) & filters.private)
async def set_verify_time_cmd(client: Client, message: Message):
    if not await _owner_only(message):
        return

    arg = _extract_text_after_command(message)
    seconds = _parse_duration_to_seconds(arg)
    if not seconds:
        return await message.reply_text(
            "<b>Usage:</b>\n"
            "<code>/set_verify_time 30m</code>\n"
            "<code>/set_verify_time 6h</code>\n"
            "<code>/set_verify_time 1d</code>\n"
            "<code>/set_verify_time 7days</code>",
            reply_markup=close_markup()
        )

    seconds = max(int(seconds), 60)
    await db.set_setting("verify_time_seconds", int(seconds))
    await message.reply_text(
        f"<b>✅ Time-based verification duration set to:</b> <code>{_format_duration(seconds)}</code>",
        reply_markup=close_markup()
    )


async def _bypass_settings_text():
    token_expire = int(await db.get_setting("verify_token_expire_seconds", VERIFY_TOKEN_EXPIRE))
    min_wait = int(await db.get_setting("bypass_minimum_seconds", BYPASS_MINIMUM_SECONDS))
    block_time = int(await db.get_setting("bypass_block_seconds", BYPASS_BLOCK_SECONDS))
    max_warn = int(await db.get_setting("bypass_max_warnings", BYPASS_MAX_WARNINGS))
    return (
        "<b>🛡 Anti-Bypass Settings</b>\n\n"
        f"<b>Each verify link valid:</b> <code>{_format_duration(token_expire)}</code>\n"
        f"<b>Minimum wait before verify:</b> <code>{_format_duration(min_wait)}</code>\n"
        f"<b>Temp block on bypass:</b> <code>{_format_duration(block_time)}</code>\n"
        f"<b>Ban after warnings:</b> <code>{max_warn}</code>\n\n"
        "<b>Commands:</b>\n"
        "<code>/set_bypass_time 50s</code>\n"
        "<code>/set_bypass_block 10m</code>\n"
        "<code>/set_bypass_warn 3</code>\n"
        "<code>/reset_bypass user_id</code>"
    )


@Bot.on_message(filters.command("bypass_settings") & filters.private)
async def bypass_settings_cmd(client: Client, message: Message):
    if not await _owner_only(message):
        return
    await message.reply_text(await _bypass_settings_text(), reply_markup=close_markup())


@Bot.on_message(filters.command(["set_bypass_time", "setbypasstime"]) & filters.private)
async def set_bypass_time_cmd(client: Client, message: Message):
    if not await _owner_only(message):
        return
    seconds = _parse_duration_to_seconds(_extract_text_after_command(message))
    if not seconds:
        return await message.reply_text(
            "<b>Usage:</b> <code>/set_bypass_time 50s</code>",
            reply_markup=close_markup()
        )
    seconds = max(int(seconds), 5)
    await db.set_setting("bypass_minimum_seconds", seconds)
    await message.reply_text(f"<b>✅ Minimum wait set to:</b> <code>{_format_duration(seconds)}</code>", reply_markup=close_markup())


@Bot.on_message(filters.command(["set_bypass_block", "setbypassblock"]) & filters.private)
async def set_bypass_block_cmd(client: Client, message: Message):
    if not await _owner_only(message):
        return
    seconds = _parse_duration_to_seconds(_extract_text_after_command(message))
    if not seconds:
        return await message.reply_text(
            "<b>Usage:</b> <code>/set_bypass_block 10m</code>",
            reply_markup=close_markup()
        )
    seconds = max(int(seconds), 60)
    await db.set_setting("bypass_block_seconds", seconds)
    await message.reply_text(f"<b>✅ Bypass block time set to:</b> <code>{_format_duration(seconds)}</code>", reply_markup=close_markup())


@Bot.on_message(filters.command(["set_bypass_warn", "setbypasswarn"]) & filters.private)
async def set_bypass_warn_cmd(client: Client, message: Message):
    if not await _owner_only(message):
        return
    try:
        count = int(_extract_text_after_command(message))
    except Exception:
        count = 0
    if count < 1:
        return await message.reply_text(
            "<b>Usage:</b> <code>/set_bypass_warn 3</code>",
            reply_markup=close_markup()
        )
    await db.set_setting("bypass_max_warnings", count)
    await message.reply_text(f"<b>✅ Ban after warning count set to:</b> <code>{count}</code>", reply_markup=close_markup())


@Bot.on_message(filters.command("reset_bypass") & filters.private)
async def reset_bypass_cmd(client: Client, message: Message):
    if not await _owner_only(message):
        return
    try:
        user_id = int(_extract_text_after_command(message))
    except Exception:
        return await message.reply_text(
            "<b>Usage:</b> <code>/reset_bypass user_id</code>",
            reply_markup=close_markup()
        )
    await db.reset_bypass_warnings(user_id)
    await message.reply_text(f"<b>✅ Bypass warnings/block reset for:</b> <code>{user_id}</code>", reply_markup=close_markup())


@Bot.on_callback_query(filters.regex(r"^verify_mode_"))
async def verify_mode_callback(client: Client, query: CallbackQuery):
    if query.from_user.id != OWNER_ID:
        return await query.answer("Owner only", show_alert=True)

    action = query.data.replace("verify_mode_", "", 1)
    if action == "short_on":
        await db.set_setting("shortener_enabled", True)
        await query.answer("Shortener ON")
    elif action == "short_off":
        await db.set_setting("shortener_enabled", False)
        await query.answer("Shortener OFF")
    elif action == "everytime":
        await db.set_setting("verify_mode", "everytime")
        await db.clear_all_verified_sessions()
        await query.answer("Verify mode: Every Time")
    elif action == "timebased":
        await db.set_setting("verify_mode", "timebased")
        await query.answer("Verify mode: Time Based")
    elif action == "refresh":
        await query.answer("Refreshed")
    else:
        return await query.answer("Unknown action", show_alert=True)

    try:
        await query.message.edit_text(
            await _verify_mode_status_text(),
            reply_markup=_verify_mode_markup(),
            disable_web_page_preview=True
        )
    except Exception:
        pass


@Bot.on_message(filters.command("setstartpic") & filters.private)
async def set_start_pic_cmd(client: Client, message: Message):
    if not await _owner_only(message):
        return

    pic = _extract_text_after_command(message)
    if message.reply_to_message and message.reply_to_message.photo:
        pic = message.reply_to_message.photo.file_id

    if not pic:
        return await message.reply_text(
            "<b>Usage:</b>\n"
            "Send <code>/setstartpic https://image-link</code>\n"
            "or reply to a photo with <code>/setstartpic</code>",
            reply_markup=close_markup()
        )

    await db.set_setting("start_pic", pic)
    await message.reply_text("<b>✅ Start photo updated.</b>", reply_markup=close_markup())


@Bot.on_message(filters.command("setforcepic") & filters.private)
async def set_force_pic_cmd(client: Client, message: Message):
    if not await _owner_only(message):
        return

    pic = _extract_text_after_command(message)
    if message.reply_to_message and message.reply_to_message.photo:
        pic = message.reply_to_message.photo.file_id

    if not pic:
        return await message.reply_text(
            "<b>Usage:</b>\n"
            "Send <code>/setforcepic https://image-link</code>\n"
            "or reply to a photo with <code>/setforcepic</code>",
            reply_markup=close_markup()
        )

    await db.set_setting("force_pic", pic)
    await message.reply_text("<b>✅ Force-sub photo updated.</b>", reply_markup=close_markup())


@Bot.on_message(filters.command("setstartmsg") & filters.private)
async def set_start_msg_cmd(client: Client, message: Message):
    if not await _owner_only(message):
        return

    text = _get_replied_text(message) or _extract_text_after_command(message)
    if not text:
        return await message.reply_text(
            "<b>Usage:</b>\n"
            "<code>/setstartmsg Hello {mention}</code>\n\n"
            "You can use: <code>{first}</code>, <code>{last}</code>, <code>{username}</code>, <code>{mention}</code>, <code>{id}</code>\n"
            "Or reply to a text/caption with <code>/setstartmsg</code>",
            reply_markup=close_markup()
        )

    await db.set_setting("start_msg", text)
    await message.reply_text("<b>✅ Start message updated.</b>", reply_markup=close_markup())


@Bot.on_message(filters.command("setforcemsg") & filters.private)
async def set_force_msg_cmd(client: Client, message: Message):
    if not await _owner_only(message):
        return

    text = _get_replied_text(message) or _extract_text_after_command(message)
    if not text:
        return await message.reply_text(
            "<b>Usage:</b>\n"
            "<code>/setforcemsg Hello {mention}, join channels first.</code>\n\n"
            "You can use: <code>{first}</code>, <code>{last}</code>, <code>{username}</code>, <code>{mention}</code>, <code>{id}</code>\n"
            "Or reply to a text/caption with <code>/setforcemsg</code>",
            reply_markup=close_markup()
        )

    await db.set_setting("force_msg", text)
    await message.reply_text("<b>✅ Force-sub message updated.</b>", reply_markup=close_markup())


@Bot.on_message(filters.command("setcaption") & filters.private & admin)
async def set_caption_cmd(client: Client, message: Message):
    text = _get_replied_text(message) or _extract_text_after_command(message)
    if not text:
        return await message.reply_text(
            "<b>Usage:</b>\n"
            "<code>/setcaption &lt;b&gt;📁 File Name:&lt;/b&gt; &lt;code&gt;{filename}&lt;/code&gt;\n\nJoin @BotWorld4U</code>\n\n"
            "Or reply to a text/caption with <code>/setcaption</code>\n\n"
            "Supported: <code>{filename}</code>, <code>{filesize}</code>, <code>{filetype}</code>, <code>{caption}</code>",
            reply_markup=close_markup()
        )

    await db.set_setting("custom_caption", text)
    await message.reply_text(
        "<b>✅ Custom caption updated.</b>\n\n"
        "Use <code>{filename}</code> where file name should show.",
        reply_markup=close_markup()
    )


@Bot.on_message(filters.command("caption") & filters.private & admin)
async def view_caption_cmd(client: Client, message: Message):
    caption = await db.get_setting("custom_caption", CUSTOM_CAPTION)
    if not caption:
        return await message.reply_text("<b>Caption:</b> OFF", reply_markup=close_markup())
    await message.reply_text(
        f"<b>Current caption:</b>\n\n<code>{html.escape(str(caption))}</code>",
        reply_markup=close_markup(),
        disable_web_page_preview=True
    )


@Bot.on_message(filters.command("delcaption") & filters.private & admin)
async def del_caption_cmd(client: Client, message: Message):
    await db.set_setting("custom_caption", "")
    await message.reply_text("<b>✅ Custom caption disabled.</b>", reply_markup=close_markup())


@Bot.on_message(filters.command("testcaption") & filters.private & admin)
async def test_caption_cmd(client: Client, message: Message):
    """Preview custom caption by replying to a file/video/photo/audio/document."""
    caption = await db.get_setting("custom_caption", CUSTOM_CAPTION)
    if not caption:
        return await message.reply_text("<b>Caption:</b> OFF", reply_markup=close_markup())

    if not message.reply_to_message or not message_supports_caption(message.reply_to_message):
        return await message.reply_text(
            "<b>Usage:</b> Reply to any file/video/photo with <code>/testcaption</code>\n\n"
            "It will show how <code>{filename}</code> and other tags will look.",
            reply_markup=close_markup()
        )

    preview = format_file_caption(caption, message.reply_to_message)
    await message.reply_text(
        "<b>🧪 Caption preview:</b>\n\n" + preview,
        reply_markup=close_markup(),
        disable_web_page_preview=True
    )


@Bot.on_message(filters.command("setrefbutton") & filters.private & admin)
async def set_ref_button_cmd(client: Client, message: Message):
    args = _extract_text_after_command(message)
    if not args or "|" not in args:
        return await message.reply_text(
            "<b>Usage:</b>\n"
            "<code>/setrefbutton Start Our Bot | https://t.me/YourBot?start=ref</code>\n\n"
            "This button will show on force-sub page.",
            reply_markup=close_markup()
        )

    text, url = [x.strip() for x in args.split("|", 1)]
    if not text or not url or not URL_RE.match(url):
        return await message.reply_text("<b>❌ Invalid format. URL must start with http:// or https://</b>", reply_markup=close_markup())

    await db.set_setting("ref_button", {"text": text, "url": url})
    await message.reply_text(
        f"<b>✅ Force-sub referral button updated.</b>\n\n{text}\n<code>{url}</code>",
        reply_markup=close_markup(),
        disable_web_page_preview=True
    )


@Bot.on_message(filters.command("setrefbot") & filters.private & admin)
async def set_ref_bot_cmd(client: Client, message: Message):
    bot_username = _extract_text_after_command(message).strip().lstrip("@")
    if not bot_username:
        return await message.reply_text(
            "<b>Usage:</b> <code>/setrefbot YourBotUsername</code>",
            reply_markup=close_markup()
        )
    url = f"https://t.me/{bot_username}?start=ref"
    await db.set_setting("ref_button", {"text": "🤖 Start Our Bot", "url": url})
    await message.reply_text(
        f"<b>✅ Force-sub referral bot button set.</b>\n<code>{url}</code>",
        reply_markup=close_markup(),
        disable_web_page_preview=True
    )


@Bot.on_message(filters.command("delrefbutton") & filters.private & admin)
async def del_ref_button_cmd(client: Client, message: Message):
    await db.del_setting("ref_button")
    await message.reply_text("<b>✅ Force-sub referral button removed.</b>", reply_markup=close_markup())




@Bot.on_message(filters.command(["adddbchannel", "adddb"]) & filters.private)
async def add_db_channel_cmd(client: Client, message: Message):
    """Owner only: add extra DB channel without editing config.py."""
    if not await _owner_only(message):
        return

    args = _extract_text_after_command(message).strip()
    if not args:
        return await message.reply_text(
            "<b>Usage:</b> <code>/adddbchannel -100xxxxxxxxxx</code>\n\n"
            "Make bot admin in that DB channel before using this command.",
            reply_markup=close_markup()
        )

    try:
        channel_id = int(args)
    except ValueError:
        return await message.reply_text("<b>❌ Invalid channel ID.</b>", reply_markup=close_markup())

    try:
        chat = await client.get_chat(channel_id)
        test = await client.send_message(chat_id=chat.id, text="Test Message")
        await test.delete()
    except Exception as e:
        return await message.reply_text(
            "<b>❌ Cannot use this DB channel.</b>\n\n"
            "Make sure bot is admin and can post/delete messages there.\n"
            f"<code>{html.escape(str(e))}</code>",
            reply_markup=close_markup()
        )

    config_ids = {int(x) for x in DB_CHANNEL_IDS}
    extra_ids = await db.get_setting("extra_db_channel_ids", [])
    if not isinstance(extra_ids, list):
        extra_ids = []
    extra_ids = [int(x) for x in extra_ids if str(x).lstrip('-').isdigit()]

    if int(chat.id) in config_ids or int(chat.id) in extra_ids:
        await reload_db_channels(client)
        return await message.reply_text(
            f"<b>ℹ️ DB channel already added.</b>\n<code>{chat.id}</code>",
            reply_markup=close_markup()
        )

    extra_ids.append(int(chat.id))
    await db.set_setting("extra_db_channel_ids", extra_ids)
    channels, failed = await reload_db_channels(client)

    await message.reply_text(
        f"<b>✅ DB channel added.</b>\n"
        f"<b>Channel:</b> <code>{chat.id}</code>\n"
        f"<b>Total active DB channels:</b> <code>{len(channels)}</code>",
        reply_markup=close_markup()
    )


@Bot.on_message(filters.command(["deldbchannel", "deldb"]) & filters.private)
async def del_db_channel_cmd(client: Client, message: Message):
    """Owner only: remove runtime-added DB channel."""
    if not await _owner_only(message):
        return

    args = _extract_text_after_command(message).strip()
    if not args:
        return await message.reply_text(
            "<b>Usage:</b> <code>/deldbchannel -100xxxxxxxxxx</code>\n\n"
            "Note: DB channels added in config.py must be removed from config.py, not from this command.",
            reply_markup=close_markup()
        )

    try:
        channel_id = int(args)
    except ValueError:
        return await message.reply_text("<b>❌ Invalid channel ID.</b>", reply_markup=close_markup())

    if channel_id in [int(x) for x in DB_CHANNEL_IDS]:
        return await message.reply_text(
            "<b>❌ This DB channel is from root config.py.</b>\n"
            "Remove it from <code>PRIMARY_DB_CHANNEL_ID</code>/<code>EXTRA_DB_CHANNEL_IDS</code> in config.py and restart bot.",
            reply_markup=close_markup()
        )

    extra_ids = await db.get_setting("extra_db_channel_ids", [])
    if not isinstance(extra_ids, list):
        extra_ids = []
    clean_extra_ids = []
    for x in extra_ids:
        try:
            x_int = int(x)
        except Exception:
            continue
        if x_int != channel_id:
            clean_extra_ids.append(x_int)
    extra_ids = clean_extra_ids
    await db.set_setting("extra_db_channel_ids", extra_ids)
    channels, failed = await reload_db_channels(client)

    await message.reply_text(
        f"<b>✅ DB channel removed if it existed.</b>\n"
        f"<b>Total active DB channels:</b> <code>{len(channels)}</code>",
        reply_markup=close_markup()
    )


@Bot.on_message(filters.command(["dbchannels", "listdbchannels"]) & filters.private & admin)
async def list_db_channels_cmd(client: Client, message: Message):
    channels = list(getattr(client, "db_channel_list", []) or [])
    if not channels:
        channels, _failed = await reload_db_channels(client)

    extra_ids = await db.get_setting("extra_db_channel_ids", [])
    if not isinstance(extra_ids, list):
        extra_ids = []

    text = "<b>🗄 Database Channels</b>\n\n"
    text += f"<b>Primary DB channel:</b> <code>{PRIMARY_DB_CHANNEL_ID or 'not set'}</code>\n"
    text += f"<b>Config channels total:</b> <code>{len(DB_CHANNEL_IDS)}</code>\n"
    text += f"<b>Extra runtime channels:</b> <code>{len(extra_ids)}</code>\n"
    text += f"<b>Active connected channels:</b> <code>{len(channels)}</code>\n\n"

    if not channels:
        text += "<i>No active DB channel connected.</i>"
    else:
        for i, chat in enumerate(channels, start=1):
            title = html.escape(getattr(chat, "title", "DB Channel") or "DB Channel")
            username = getattr(chat, "username", None)
            username_text = f"@{username}" if username else "private"
            tag = " ✅ PRIMARY" if int(chat.id) == int(getattr(client, "db_channel", chat).id) else ""
            text += f"<b>{i}.</b> {title}{tag}\n<code>{chat.id}</code> | {username_text}\n"

    await message.reply_text(text, reply_markup=close_markup(), disable_web_page_preview=True)


@Bot.on_message(filters.command("customsettings") & filters.private & admin)
async def custom_settings_cmd(client: Client, message: Message):
    protect = str_to_bool(await db.get_setting("protect_content", PROTECT_CONTENT))
    start_pic = await db.get_setting("start_pic", START_PIC)
    force_pic = await db.get_setting("force_pic", FORCE_PIC)
    start_buttons = await db.get_buttons("start")
    force_buttons = await db.get_buttons("force")
    caption = await db.get_setting("custom_caption", CUSTOM_CAPTION)
    ref_button = await db.get_setting("ref_button", None)

    text = (
        "<b>⚙️ Bot Custom Settings</b>\n\n"
        f"<b>Restriction:</b> {'ON ✅' if protect else 'OFF ❌'}\n"
        f"<b>Start buttons:</b> {len(start_buttons)}\n"
        f"<b>Force buttons:</b> {len(force_buttons)}\n"
        f"<b>Caption:</b> {'ON ✅' if caption else 'OFF ❌'}\n"
        f"<b>Referral button:</b> {'ON ✅' if isinstance(ref_button, dict) else 'OFF ❌'}\n"
        f"<b>DB channels:</b> <code>{len(getattr(client, 'db_channel_list', []) or [])}</code>\n"
        f"<b>Primary DB:</b> <code>{getattr(getattr(client, 'db_channel', None), 'id', PRIMARY_DB_CHANNEL_ID)}</code>\n"
        f"<b>Start pic:</b> <code>{start_pic}</code>\n"
        f"<b>Force pic:</b> <code>{force_pic}</code>\n\n"
        "<b>Commands:</b>\n"
        "<code>/addbutton start Text | https://link</code>\n"
        "<code>/addbutton force Text | https://link</code>\n"
        "<code>/buttons</code>\n"
        "<code>/restriction on</code> / <code>/restriction off</code>\n"
        "<code>/setstartpic</code>, <code>/setforcepic</code>\n"
        "<code>/setstartmsg</code>, <code>/setforcemsg</code>\n"
        "<code>/setcaption</code>, <code>/caption</code>, <code>/delcaption</code>\n"
        "<code>/setrefbutton Text | https://link</code>, <code>/delrefbutton</code>\n"
        "<code>/dbchannels</code>, <code>/adddbchannel -100...</code>, <code>/deldbchannel -100...</code>"
    )
    await message.reply_text(text, reply_markup=close_markup(), disable_web_page_preview=True)


@Bot.on_message(filters.command("resetcustom") & filters.private)
async def reset_custom_cmd(client: Client, message: Message):
    if not await _owner_only(message):
        return

    for key in ("start_pic", "force_pic", "start_msg", "force_msg", "protect_content", "start_buttons", "force_buttons", "custom_caption", "ref_button"):
        await db.del_setting(key)
    await message.reply_text("<b>✅ Custom bot settings reset to config/default values.</b>", reply_markup=close_markup())
