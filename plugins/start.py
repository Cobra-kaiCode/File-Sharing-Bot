# Credit: @BotWorld4U
# Support: @BotWorld4U
#
# Copyright (C) 2025 by BotWorld4U@Github, < https://github.com/BotWorld4U >.
#
# This file is part of < https://github.com/BotWorld4U/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/BotWorld4U/FileStore/blob/master/LICENSE >
#
# All rights reserved.
#

import asyncio
import os
import random
import sys
import time
import secrets
from datetime import datetime, timedelta
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode, ChatAction
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, ChatInviteLink, ChatPrivileges, WebAppInfo
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserNotParticipant
from bot import Bot
from config import *
from helper_func import *
from database.database import *
from database.db_premium import *

BAN_SUPPORT = f"{BAN_SUPPORT}"


async def _shortener_is_enabled():
    return str_to_bool(await db.get_setting("shortener_enabled", SHORTENER_ENABLED))


async def _get_verify_mode():
    mode = str(await db.get_setting("verify_mode", VERIFY_MODE)).strip().lower()
    return mode if mode in {"everytime", "timebased"} else "timebased"


async def _get_verify_time_seconds():
    try:
        seconds = int(await db.get_setting("verify_time_seconds", VERIFY_TIME))
    except Exception:
        seconds = int(VERIFY_TIME)
    return max(seconds, 60)


async def _get_verify_token_expire_seconds():
    try:
        seconds = int(await db.get_setting("verify_token_expire_seconds", VERIFY_TOKEN_EXPIRE))
    except Exception:
        seconds = int(VERIFY_TOKEN_EXPIRE)
    return max(seconds, 30)


async def _get_bypass_minimum_seconds():
    try:
        seconds = int(await db.get_setting("bypass_minimum_seconds", BYPASS_MINIMUM_SECONDS))
    except Exception:
        seconds = int(BYPASS_MINIMUM_SECONDS)
    return max(seconds, 5)


async def _get_bypass_block_seconds():
    try:
        seconds = int(await db.get_setting("bypass_block_seconds", BYPASS_BLOCK_SECONDS))
    except Exception:
        seconds = int(BYPASS_BLOCK_SECONDS)
    return max(seconds, 60)


async def _get_bypass_max_warnings():
    try:
        count = int(await db.get_setting("bypass_max_warnings", BYPASS_MAX_WARNINGS))
    except Exception:
        count = int(BYPASS_MAX_WARNINGS)
    return max(count, 1)


def _seconds_left_text(until_ts: int) -> str:
    left = max(0, int(until_ts) - int(time.time()))
    return _format_verify_duration(left or 1)


def _format_verify_duration(seconds: int) -> str:
    seconds = int(seconds)
    if seconds % 86400 == 0:
        return f"{seconds // 86400} day(s)"
    if seconds % 3600 == 0:
        return f"{seconds // 3600} hour(s)"
    if seconds % 60 == 0:
        return f"{seconds // 60} minute(s)"
    return f"{seconds} second(s)"


async def _should_show_shortener(user_id: int):
    if user_id == OWNER_ID:
        return False
    if await db.admin_exist(user_id):
        return False
    try:
        if await is_premium_user(user_id):
            return False
    except Exception:
        pass

    if not await _shortener_is_enabled():
        return False

    mode = await _get_verify_mode()
    if mode == "timebased":
        verified_until = await db.get_verified_until(user_id)
        if verified_until and verified_until > int(time.time()):
            return False

    return True


def _make_gateway_url(token: str) -> str:
    """Return Heroku mini-app gateway URL for a verify token.

    This hides the real shortener link from the Telegram button.
    Users who long-press/copy the button will only get this Heroku URL.
    """
    app_url = str(WEB_APP_URL or "").strip().rstrip("/")
    if not app_url:
        return ""
    return f"{app_url}/v/{token}"


def _make_verify_button(token: str, short_link: str):
    """Build verify button. Prefer Telegram WebApp button with Heroku gateway."""
    gateway_url = _make_gateway_url(token)

    # If WEB_APP_URL is set, never expose real short link in Telegram.
    if gateway_url and HIDE_SHORTLINK_BEHIND_HEROKU:
        if USE_WEBAPP_VERIFY_BUTTON:
            return InlineKeyboardButton(
                text="ᴅᴏᴡɴʟᴏᴀᴅ",
                web_app=WebAppInfo(url=gateway_url)
            )
        return InlineKeyboardButton(text="ᴅᴏᴡɴʟᴏᴀᴅ", url=gateway_url)

    # Fallback only if WEB_APP_URL is not filled in config.py.
    return InlineKeyboardButton(text="ᴅᴏᴡɴʟᴏᴀᴅ", url=short_link)


async def send_shortener_gate(client: Client, message: Message, decoded_payload: str):
    """Send secure shortener gate using one-time DB token.

    Real shortener link is saved in MongoDB and hidden behind Heroku /v/<token>
    mini-app gateway. No command is needed for this behavior.
    """
    token = secrets.token_urlsafe(12).replace("-", "").replace("_", "")[:16]
    expire_seconds = await _get_verify_token_expire_seconds()
    await db.create_verify_token(token, message.from_user.id, decoded_payload, expire_seconds)

    verify_link = f"https://t.me/{client.username}?start=verify_{token}"

    shortlink_url = await db.get_setting("shortlink_url", SHORTLINK_URL)
    shortlink_api = await db.get_setting("shortlink_api", SHORTLINK_API)
    short_link = await get_shortlink(shortlink_url, shortlink_api, verify_link)

    # Store the real short link server-side. Telegram button will use Heroku URL only.
    await db.set_verify_token_short_url(token, short_link)

    tutorial = await db.get_setting("tutorial_url", TUT_VID)
    short_pic = await db.get_setting("shortener_pic", SHORTENER_PIC)
    short_msg = await db.get_setting("short_msg", SHORT_MSG)
    # Do not show verify token expiry / minimum-wait time to users.
    # Anti-bypass protection still works silently in the Heroku gateway.
    short_msg = (
        str(short_msg)
        + "\n\n<i>Click the Download button below and complete verification.</i>"
    )

    buttons = [
        [
            _make_verify_button(token, short_link),
            InlineKeyboardButton(text="ᴛᴜᴛᴏʀɪᴀʟ", url=tutorial)
        ],
        [InlineKeyboardButton(text="ᴘʀᴇᴍɪᴜᴍ", callback_data="premium")]
    ]

    try:
        await message.reply_photo(
            photo=short_pic,
            caption=short_msg,
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    except Exception:
        # Do not print/send real short link in text. Button only.
        await message.reply_text(
            short_msg,
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )



def _format_premium_text(user) -> str:
    """Format premium text safely."""
    return str(PREMIUM_TEXT).format(
        mention=user.mention,
        first=getattr(user, "first_name", "") or "",
        id=getattr(user, "id", "") or "",
        owner_tag=OWNER_TAG,
        upi_id=UPI_ID,
        referral_count=REFERRAL_REWARD_COUNT,
        referral_days=REFERRAL_REWARD_DAYS,
    )


def _premium_markup():
    rows = []
    if PREMIUM_BUTTON_URL:
        rows.append([InlineKeyboardButton(PREMIUM_BUTTON_TEXT, url=PREMIUM_BUTTON_URL)])
    rows.append([InlineKeyboardButton("🔒 Close", callback_data="close")])
    return InlineKeyboardMarkup(rows)


async def send_premium_page(client: Client, message: Message):
    """Send premium buying/referral info."""
    caption = _format_premium_text(message.from_user)
    try:
        await message.reply_photo(
            photo=QR_PIC,
            caption=caption,
            reply_markup=_premium_markup(),
            disable_web_page_preview=True,
        )
    except Exception:
        await message.reply_text(
            caption,
            reply_markup=_premium_markup(),
            disable_web_page_preview=True,
        )


async def _send_referral_reward_notice(client: Client, referrer_id: int, referred_user_id: int, total: int, expiry: str):
    """Notify DB channel and user after successful referral reward."""
    try:
        ref_user = await client.get_users(referrer_id)
    except Exception:
        ref_user = None
    try:
        new_user = await client.get_users(referred_user_id)
    except Exception:
        new_user = None

    ref_name = ref_user.mention if ref_user else f"<code>{referrer_id}</code>"
    new_name = new_user.mention if new_user else f"<code>{referred_user_id}</code>"

    log_text = (
        "<b>🎁 Referral Premium Reward Completed</b>\n\n"
        f"<b>User:</b> {ref_name}\n"
        f"<b>User ID:</b> <code>{referrer_id}</code>\n"
        f"<b>Total valid referrals:</b> <code>{total}</code>\n"
        f"<b>Reward:</b> <code>{REFERRAL_REWARD_DAYS} days premium</code>\n"
        f"<b>Premium expiry:</b> <code>{expiry}</code>\n\n"
        f"<b>Latest valid referral:</b> {new_name}\n"
        f"<b>New user ID:</b> <code>{referred_user_id}</code>\n\n"
        "<b>Credit:</b> @BotWorld4U"
    )

    db_channel = getattr(client, "db_channel", None)
    if db_channel:
        try:
            await client.send_message(db_channel.id, log_text, disable_web_page_preview=True)
        except Exception as e:
            print(f"Failed to send referral reward log to DB channel: {e}")

    try:
        await client.send_message(
            referrer_id,
            f"<b>🎉 Congratulations!</b>\n\n"
            f"You completed <b>{REFERRAL_REWARD_COUNT}</b> valid referrals.\n"
            f"You received <b>{REFERRAL_REWARD_DAYS} days premium</b>.\n"
            f"<b>Expiry:</b> <code>{expiry}</code>",
            disable_web_page_preview=True,
        )
    except Exception:
        pass


async def _finalize_referral_if_ready(client: Client, message: Message):
    """Count referral only after the invited user has joined all required channels."""
    user_id = int(message.from_user.id)
    referrer_id, total, _unused = await db.complete_referral_if_pending(user_id)
    if not referrer_id:
        return

    try:
        await client.send_message(
            referrer_id,
            f"<b>✅ New valid referral counted!</b>\n\n"
            f"<b>Total valid referrals:</b> <code>{total}/{REFERRAL_REWARD_COUNT}</code>\n"
            f"Use /referral to check your link and progress.",
            disable_web_page_preview=True,
        )
    except Exception:
        pass

    if total > 0 and total % REFERRAL_REWARD_COUNT == 0:
        milestone = total // REFERRAL_REWARD_COUNT
        if await db.mark_referral_reward_given(referrer_id, milestone):
            expiry = await add_premium(referrer_id, REFERRAL_REWARD_DAYS, "d")
            await _send_referral_reward_notice(client, referrer_id, user_id, total, expiry)


@Bot.on_message(filters.command(["premium", "buy_premium"]) & filters.private)
async def premium_command(client: Client, message: Message):
    await send_premium_page(client, message)


@Bot.on_message(filters.command(["referral", "refer", "referrals"]) & filters.private)
async def referral_command(client: Client, message: Message):
    user_id = int(message.from_user.id)
    valid_count = await db.get_referral_count(user_id)
    pending_count = await db.get_pending_referral_count(user_id)
    rewards = await db.get_referral_rewards(user_id)
    remaining = REFERRAL_REWARD_COUNT - (valid_count % REFERRAL_REWARD_COUNT)
    if remaining == REFERRAL_REWARD_COUNT and valid_count > 0:
        remaining = REFERRAL_REWARD_COUNT

    link = f"https://t.me/{client.username}?start=ref_{user_id}"
    text = (
        "<b>🎁 Your Referral Link</b>\n\n"
        f"<code>{link}</code>\n\n"
        f"<b>Valid referrals:</b> <code>{valid_count}</code>\n"
        f"<b>Pending referrals:</b> <code>{pending_count}</code>\n"
        f"<b>Reward:</b> <code>{REFERRAL_REWARD_DAYS} days premium for every {REFERRAL_REWARD_COUNT} valid referrals</code>\n"
        f"<b>Remaining for next reward:</b> <code>{remaining}</code>\n"
        f"<b>Rewards received:</b> <code>{len(rewards)}</code>\n\n"
        "<i>Referral counts only when invited user joins all required channels and opens the bot again.</i>"
    )
    await message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔁 Share Referral Link", url=f"https://telegram.me/share/url?url={link}")],
            [InlineKeyboardButton("💎 Premium Plans", callback_data="premium")],
        ]),
        disable_web_page_preview=True,
    )



@Bot.on_message(filters.command('start') & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id

    # Add user if not already present. Referral source is accepted only for new users.
    is_new_user = False
    if not await db.present_user(user_id):
        is_new_user = True
        try:
            await db.add_user(user_id)
        except Exception:
            pass

    # Check if user is banned
    banned_users = await db.get_ban_users()
    if user_id in banned_users:
        return await message.reply_text(
            "<b>⛔️ You are Bᴀɴɴᴇᴅ from using this bot.</b>\n\n"
            "<i>Contact support if you think this is a mistake.</i>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Contact Support", url=BAN_SUPPORT)]]
            )
        )

    # Anti-bypass temporary block. Owner/admin are never blocked by this.
    try:
        is_staff = user_id == OWNER_ID or await db.admin_exist(user_id)
    except Exception:
        is_staff = user_id == OWNER_ID
    if not is_staff:
        bypass_block_until = await db.get_bypass_block_until(user_id)
        if bypass_block_until and bypass_block_until > int(time.time()):
            return await message.reply_text(
                "<b>⛔ You are temporarily blocked.</b>\n\n"
                "<b>Reason:</b> You tried to bypass verification too fast.\n"
                f"<b>Try again after:</b> <code>{_seconds_left_text(bypass_block_until)}</code>\n\n"
                "<i>Please use the latest verify link and wait properly.</i>"
            )

    # Strictly validate /start payload before force-sub.
    # This blocks edited/tampered links like: abc + original_token + 7.
    # Shortener verification uses secure one-time token: verify_<token>.
    payload = None
    decoded_start_data = None
    verified_via_shortener = False

    if message.command and len(message.command) > 1:
        payload = message.command[1].strip()

        if payload.startswith("ref_"):
            try:
                referrer_id = int(payload.split("_", 1)[1].strip())
            except Exception:
                referrer_id = 0
            if referrer_id and referrer_id != user_id and is_new_user:
                try:
                    await db.set_pending_referral(user_id, referrer_id)
                except Exception as e:
                    print(f"Failed to save referral source: {e}")

        elif payload.startswith("verify_"):
            token = payload.split("_", 1)[1].strip()
            token_data = await db.get_verify_token(token)
            if not token_data or int(token_data.get("user_id", 0)) != int(user_id):
                return await message.reply_text(
                    "<b>❌ Invalid or expired verification link.</b>\n\n"
                    "<i>Please open original file link again to get a fresh verify link.</i>"
                )

            token_age = int(time.time()) - int(token_data.get("created_at", 0) or 0)
            min_wait = await _get_bypass_minimum_seconds()
            if token_age < min_wait:
                await db.delete_verify_token(token)
                block_seconds = await _get_bypass_block_seconds()
                max_warnings = await _get_bypass_max_warnings()
                warnings, banned, block_until = await db.register_bypass_attempt(user_id, block_seconds, max_warnings)

                if banned:
                    return await message.reply_text(
                        f"<b>⛔ You are banned.</b>\n\n"
                        f"<b>Reason:</b> Verification bypass detected.\n"
                        f"<b>Warning:</b> <code>{warnings}/{max_warnings}</code>\n\n"
                        "<i>You tried to bypass verification too many times.</i>",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Contact Support", url=BAN_SUPPORT)]])
                    )

                return await message.reply_text(
                    f"<b>⚠️ Bypass Warning {warnings}/{max_warnings}</b>\n\n"
                    "You have tried to bypass verification.\n"
                    f"You are blocked for next <b>{_format_verify_duration(block_seconds)}</b>.\n"
                    f"Try again after: <code>{_seconds_left_text(block_until)}</code>\n\n"
                    f"<i>Wait at least {_format_verify_duration(min_wait)} on the shortener page before clicking verify.</i>"
                )

            decoded_start_data = token_data.get("decoded_payload")
            await db.delete_verify_token(token)
            await db.inc_verify_count(user_id, 1)

            if await _get_verify_mode() == "timebased":
                verify_seconds = await _get_verify_time_seconds()
                await db.set_verified_until(user_id, int(time.time()) + verify_seconds)
                try:
                    await message.reply_text(
                        f"<b>✅ Verification successful.</b>\n\n"
                        f"You can use file links without verification for <b>{_format_verify_duration(verify_seconds)}</b>."
                    )
                except Exception:
                    pass

            verified_via_shortener = True
        else:
            decoded_start_data = await decode_start_payload(payload)
            if not decoded_start_data:
                return await message.reply_text(
                    "<b>❌ Invalid or tampered link.</b>\n\n"
                    "<i>Please use original bot generated link only.</i>"
                )

    # ✅ Check Force Subscription after link validation
    if not await is_subscribed(client, user_id):
        return await not_joined(client, message)

    # Referral becomes valid only after force-sub is completed.
    try:
        await _finalize_referral_if_ready(client, message)
    except Exception as e:
        print(f"Referral finalize failed: {e}")

    # Show shortener gate only after force-sub is completed.
    if decoded_start_data and not verified_via_shortener and await _should_show_shortener(user_id):
        await send_shortener_gate(client, message, decoded_start_data)
        return

    # File auto-delete time in seconds
    FILE_AUTO_DELETE = await db.get_del_timer()

    # Handle file/link flow
    if decoded_start_data:
        string = decoded_start_data
        argument = string.split("-")

        ids = []
        db_channel = getattr(client, "db_channel", None)

        if argument[0] == "getv2":
            # New multi-DB format:
            # getv2-<abs_db_channel_id>-<msg_id>
            # getv2-<abs_db_channel_id>-<start_msg_id>-<end_msg_id>
            try:
                db_channel = get_db_channel_by_abs(client, int(argument[1]))
                if not db_channel:
                    return await message.reply_text("<b>❌ DB channel not found for this link.</b>")

                if len(argument) == 3:
                    ids = [int(argument[2])]
                elif len(argument) == 4:
                    start = int(argument[2])
                    end = int(argument[3])
                    ids = range(start, end + 1) if start <= end else list(range(start, end - 1, -1))
                else:
                    return await message.reply_text("<b>❌ Invalid link format.</b>")
            except Exception as e:
                print(f"Error decoding v2 link IDs: {e}")
                return await message.reply_text("<b>❌ Invalid link data.</b>")

        else:
            # Old one-channel format for backward compatibility.
            # Old links always use the first/default DB channel.
            if not getattr(client, "db_channel", None):
                return await message.reply_text("<b>❌ DB channel is not connected. Please contact bot owner.</b>")
            if len(argument) == 3:
                try:
                    start = int(int(argument[1]) / abs(client.db_channel.id))
                    end = int(int(argument[2]) / abs(client.db_channel.id))
                    ids = range(start, end + 1) if start <= end else list(range(start, end - 1, -1))
                except Exception as e:
                    print(f"Error decoding old IDs: {e}")
                    return await message.reply_text("<b>❌ Invalid link data.</b>")

            elif len(argument) == 2:
                try:
                    ids = [int(int(argument[1]) / abs(client.db_channel.id))]
                except Exception as e:
                    print(f"Error decoding old ID: {e}")
                    return await message.reply_text("<b>❌ Invalid link data.</b>")
            else:
                return await message.reply_text("<b>❌ Invalid link format.</b>")

        temp_msg = await message.reply("<b>Please wait...</b>")
        try:
            messages = await get_messages(client, ids, db_channel=db_channel)
        except Exception as e:
            await message.reply_text("Something went wrong!")
            print(f"Error getting messages: {e}")
            return
        finally:
            await temp_msg.delete()

        if not messages:
            return await message.reply_text("<b>❌ File not found or deleted from DB channel.</b>")

        protect_content = str_to_bool(await db.get_setting("protect_content", PROTECT_CONTENT))

        codeflix_msgs = []
        for msg in messages:
            if not msg:
                continue
            custom_caption = await db.get_setting("custom_caption", CUSTOM_CAPTION)
            reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None
            copy_kwargs = {
                "chat_id": message.from_user.id,
                "reply_markup": reply_markup,
                "protect_content": protect_content,
            }
            if message_supports_caption(msg):
                caption = format_file_caption(custom_caption, msg) if custom_caption else ("" if not msg.caption else msg.caption.html)
                copy_kwargs.update({"caption": caption, "parse_mode": ParseMode.HTML})
            try:
                copied_msg = await msg.copy(**copy_kwargs)
                await asyncio.sleep(0.1)
                codeflix_msgs.append(copied_msg)
            except Exception as e:
                print(f"Failed to send message: {e}")

        if FILE_AUTO_DELETE > 0 and codeflix_msgs:
            notification_msg = await message.reply(
                f"<b>Tʜɪs Fɪʟᴇ ᴡɪʟʟ ʙᴇ Dᴇʟᴇᴛᴇᴅ ɪɴ  {get_exp_time(FILE_AUTO_DELETE)}. Pʟᴇᴀsᴇ sᴀᴠᴇ ᴏʀ ғᴏʀᴡᴀʀᴅ ɪᴛ ᴛᴏ ʏᴏᴜʀ sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs ʙᴇғᴏʀᴇ ɪᴛ ɢᴇᴛs Dᴇʟᴇᴛᴇᴅ.</b>"
            )
            reload_payload = await encode(decoded_start_data)
            reload_url = f"https://t.me/{client.username}?start={reload_payload}"
            asyncio.create_task(
                schedule_auto_delete(client, codeflix_msgs, notification_msg, FILE_AUTO_DELETE, reload_url)
            )
        return

    # Normal /start page
    start_pic = await db.get_setting("start_pic", START_PIC)
    start_msg = await db.get_setting("start_msg", START_MSG)
    start_buttons = await db.get_buttons("start")

    rows = []
    for btn in start_buttons:
        text = btn.get("text")
        url = btn.get("url")
        if text and url:
            rows.append([InlineKeyboardButton(text, url=url)])

    # Default buttons stay available
    rows.append([InlineKeyboardButton("• ᴜᴘᴅᴀᴛᴇs •", url="https://t.me/BotWorld4U")])
    rows.append([
        InlineKeyboardButton("🎁 ʀᴇғᴇʀʀᴀʟ", callback_data="show_referral"),
        InlineKeyboardButton("💎 ᴘʀᴇᴍɪᴜᴍ", callback_data="premium")
    ])
    rows.append([
        InlineKeyboardButton("• ᴀʙᴏᴜᴛ", callback_data="about"),
        InlineKeyboardButton("ʜᴇʟᴘ •", callback_data="help")
    ])

    await message.reply_photo(
        photo=start_pic,
        caption=safe_format_user(start_msg, message.from_user),
        reply_markup=InlineKeyboardMarkup(rows),
        message_effect_id=5104841245755180586
    )
    return



#=====================================================================================##
# Credit: @BotWorld4U
# Support: @BotWorld4U



# Create a global dictionary to store chat data
chat_data_cache = {}

async def not_joined(client: Client, message: Message):
    temp = await message.reply("<b><i>ᴡᴀɪᴛ ᴀ sᴇᴄ..</i></b>")

    user_id = message.from_user.id
    buttons = []
    count = 0

    try:
        all_channels = await db.show_channels()  # Should return list of (chat_id, mode) tuples
        for total, chat_id in enumerate(all_channels, start=1):
            mode = await db.get_channel_mode(chat_id)  # fetch mode 

            await message.reply_chat_action(ChatAction.TYPING)

            if not await is_sub(client, user_id, chat_id):
                try:
                    # Cache chat info
                    if chat_id in chat_data_cache:
                        data = chat_data_cache[chat_id]
                    else:
                        data = await client.get_chat(chat_id)
                        chat_data_cache[chat_id] = data

                    name = data.title

                    # Generate proper invite link based on the mode
                    if mode == "on" and not data.username:
                        invite = await client.create_chat_invite_link(
                            chat_id=chat_id,
                            creates_join_request=True,
                            expire_date=datetime.utcnow() + timedelta(seconds=FSUB_LINK_EXPIRY) if FSUB_LINK_EXPIRY else None
                            )
                        link = invite.invite_link

                    else:
                        if data.username:
                            link = f"https://t.me/{data.username}"
                        else:
                            invite = await client.create_chat_invite_link(
                                chat_id=chat_id,
                                expire_date=datetime.utcnow() + timedelta(seconds=FSUB_LINK_EXPIRY) if FSUB_LINK_EXPIRY else None)
                            link = invite.invite_link

                    buttons.append([InlineKeyboardButton(text=name, url=link)])
                    count += 1
                    await temp.edit(f"<b>{'! ' * count}</b>")

                except Exception as e:
                    print(f"Error with chat {chat_id}: {e}")
                    return await temp.edit(
                        f"<b><i>! Eʀʀᴏʀ, Cᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @BotWorld4U</i></b>\n"
                        f"<blockquote expandable><b>Rᴇᴀsᴏɴ:</b> {e}</blockquote>"
                    )

        # Optional force-sub referral bot/button set by owner/admin
        ref_button = await db.get_setting("ref_button", None)
        if isinstance(ref_button, dict):
            ref_text = ref_button.get("text")
            ref_url = ref_button.get("url")
            if ref_text and ref_url:
                buttons.append([InlineKeyboardButton(text=ref_text, url=ref_url)])

        # Extra custom force-sub buttons set by owner/admin
        force_buttons = await db.get_buttons("force")
        for btn in force_buttons:
            text = btn.get("text")
            url = btn.get("url")
            if text and url:
                buttons.append([InlineKeyboardButton(text=text, url=url)])

        # Retry Button
        try:
            buttons.append([
                InlineKeyboardButton(
                    text='♻️ Tʀʏ Aɢᴀɪɴ',
                    url=f"https://t.me/{client.username}?start={message.command[1]}"
                )
            ])
        except IndexError:
            pass

        force_pic = await db.get_setting("force_pic", FORCE_PIC)
        force_msg = await db.get_setting("force_msg", FORCE_MSG)

        await message.reply_photo(
            photo=force_pic,
            caption=safe_format_user(force_msg, message.from_user),
            reply_markup=InlineKeyboardMarkup(buttons),
        )

    except Exception as e:
        print(f"Final Error: {e}")
        await temp.edit(
            f"<b><i>! Eʀʀᴏʀ, Cᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @BotWorld4U</i></b>\n"
            f"<blockquote expandable><b>Rᴇᴀsᴏɴ:</b> {e}</blockquote>"
        )

@Bot.on_message(filters.command('help') & filters.private)
async def help_command(client: Client, message: Message):
    await message.reply_text(
        text=HELP_TXT.format(first=message.from_user.first_name),
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏꜱᴇ", callback_data='close')]])
    )


@Bot.on_message(filters.command('about') & filters.private)
async def about_command(client: Client, message: Message):
    await message.reply_text(
        text=ABOUT_TXT.format(first=message.from_user.first_name),
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏꜱᴇ", callback_data='close')]])
    )


#=====================================================================================##

@Bot.on_message(filters.command('commands') & filters.private & admin)
async def bcmd(bot: Bot, message: Message):        
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("• ᴄʟᴏsᴇ •", callback_data = "close")]])
    await message.reply(text=CMD_TXT, reply_markup = reply_markup, quote= True)


#=====================================================================================##
# PREMIUM / SHORTENER ADMIN COMMANDS
@Bot.on_message(filters.command('myplan') & filters.private)
async def check_plan(client: Client, message: Message):
    user_id = message.from_user.id  # Get user ID from the message

    # Get the premium status of the user
    status_message = await check_user_plan(user_id)

    # Send the response message to the user
    await message.reply(status_message)

#=====================================================================================##
# Command to add premium user
@Bot.on_message(filters.command('addpremium') & filters.private & admin)
async def add_premium_user_command(client, msg):
    if len(msg.command) != 4:
        await msg.reply_text(
            "Usage: /addpremium <user_id> <time_value> <time_unit>\n\n"
            "Time Units:\n"
            "s - seconds\n"
            "m - minutes\n"
            "h - hours\n"
            "d - days\n"
            "y - years\n\n"
            "Examples:\n"
            "/addpremium 123456789 30 m → 30 minutes\n"
            "/addpremium 123456789 2 h → 2 hours\n"
            "/addpremium 123456789 1 d → 1 day\n"
            "/addpremium 123456789 1 y → 1 year"
        )
        return

    try:
        user_id = int(msg.command[1])
        time_value = int(msg.command[2])
        time_unit = msg.command[3].lower()  # supports: s, m, h, d, y

        # Call add_premium function
        expiration_time = await add_premium(user_id, time_value, time_unit)

        # Notify the admin
        await msg.reply_text(
            f"✅ User `{user_id}` added as a premium user for {time_value} {time_unit}.\n"
            f"Expiration Time: `{expiration_time}`"
        )

        # Notify the user
        await client.send_message(
            chat_id=user_id,
            text=(
                f"🎉 Premium Activated!\n\n"
                f"You have received premium access for `{time_value} {time_unit}`.\n"
                f"Expires on: `{expiration_time}`"
            ),
        )

    except ValueError:
        await msg.reply_text("❌ Invalid input. Please ensure user ID and time value are numbers.")
    except Exception as e:
        await msg.reply_text(f"⚠️ An error occurred: `{str(e)}`")


# Command to remove premium user
@Bot.on_message(filters.command('remove_premium') & filters.private & admin)
async def pre_remove_user(client: Client, msg: Message):
    if len(msg.command) != 2:
        await msg.reply_text("useage: /remove_premium user_id ")
        return
    try:
        user_id = int(msg.command[1])
        await remove_premium(user_id)
        await msg.reply_text(f"User {user_id} has been removed.")
    except ValueError:
        await msg.reply_text("user_id must be an integer or not available in database.")


# Command to list active premium users
@Bot.on_message(filters.command('premium_users') & filters.private & admin)
async def list_premium_users_command(client, message):
    # Define IST timezone
    ist = timezone("Asia/Kolkata")

    # Retrieve all users from the collection
    premium_users_cursor = collection.find({})
    premium_user_list = ['Active Premium Users in database:']
    current_time = datetime.now(ist)  # Get current time in IST

    # Use async for to iterate over the async cursor
    async for user in premium_users_cursor:
        user_id = user["user_id"]
        expiration_timestamp = user["expiration_timestamp"]

        try:
            # Convert expiration_timestamp to a timezone-aware datetime object in IST
            expiration_time = datetime.fromisoformat(expiration_timestamp).astimezone(ist)

            # Calculate remaining time
            remaining_time = expiration_time - current_time

            if remaining_time.total_seconds() <= 0:
                # Remove expired users from the database
                await collection.delete_one({"user_id": user_id})
                continue  # Skip to the next user if this one is expired

            # If not expired, retrieve user info
            user_info = await client.get_users(user_id)
            username = user_info.username if user_info.username else "No Username"
            first_name = user_info.first_name
            mention=user_info.mention

            # Calculate days, hours, minutes, seconds left
            days, hours, minutes, seconds = (
                remaining_time.days,
                remaining_time.seconds // 3600,
                (remaining_time.seconds // 60) % 60,
                remaining_time.seconds % 60,
            )
            expiry_info = f"{days}d {hours}h {minutes}m {seconds}s left"

            # Add user details to the list
            premium_user_list.append(
                f"UserID: <code>{user_id}</code>\n"
                f"User: @{username}\n"
                f"Name: {mention}\n"
                f"Expiry: {expiry_info}"
            )
        except Exception as e:
            premium_user_list.append(
                f"UserID: <code>{user_id}</code>\n"
                f"Error: Unable to fetch user details ({str(e)})"
            )

    if len(premium_user_list) == 1:  # No active users found
        await message.reply_text("I found 0 active premium users in my DB")
    else:
        await message.reply_text("\n\n".join(premium_user_list), parse_mode=None)


#=====================================================================================##

@Bot.on_message(filters.command("count") & filters.private & admin)
async def total_verify_count_cmd(client, message: Message):
    total = await db.get_total_verify_count()
    await message.reply_text(f"Tᴏᴛᴀʟ ᴠᴇʀɪғɪᴇᴅ ᴛᴏᴋᴇɴs ᴛᴏᴅᴀʏ: <b>{total}</b>")

async def schedule_auto_delete(client, codeflix_msgs, notification_msg, file_auto_delete, reload_url):
    await asyncio.sleep(file_auto_delete)
    for snt_msg in codeflix_msgs:
        if snt_msg:
            try:
                await snt_msg.delete()
            except Exception as e:
                print(f"Error deleting message {snt_msg.id}: {e}")

    try:
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("ɢᴇᴛ ғɪʟᴇ ᴀɢᴀɪɴ!", url=reload_url)]]
        ) if reload_url else None

        await notification_msg.edit(
            "<b>ʏᴏᴜʀ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ ɪꜱ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ !!\n\nᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ᴅᴇʟᴇᴛᴇᴅ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ 👇</b>",
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"Error updating notification with 'Get File Again' button: {e}")
