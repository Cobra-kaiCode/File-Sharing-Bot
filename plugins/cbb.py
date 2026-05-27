#
# Copyright (C) 2025 by BotWorld4U@Github, < https://github.com/BotWorld4U >.
#
# This file is part of < https://github.com/BotWorld4U/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/BotWorld4U/FileStore/blob/master/LICENSE >
#
# All rights reserved.

from pyrogram import Client 
from bot import Bot
from config import *
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.database import *
from helper_func import safe_format_user, str_to_bool


def _format_duration(seconds: int):
    try:
        seconds = int(seconds)
    except Exception:
        seconds = VERIFY_TIME
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
    return (
        "<b>🔐 Verification Mode Settings</b>\n\n"
        f"<b>Shortener:</b> {'ON ✅' if enabled else 'OFF ❌'}\n"
        f"<b>Verify Mode:</b> <code>{mode}</code>\n"
        f"<b>Time-based duration:</b> <code>{_format_duration(verify_seconds)}</code>\n\n"
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


def _format_premium_text(user):
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

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data

    if data.startswith("verify_mode_"):
        if query.from_user.id != OWNER_ID:
            return await query.answer("Owner only", show_alert=True)
        action = data.replace("verify_mode_", "", 1)
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
        return

    if data.startswith(("rfs_", "fsub_")):
        user_id = query.from_user.id
        if user_id != OWNER_ID and not await db.admin_exist(user_id):
            return await query.answer("Admin only", show_alert=True)

    if data == "help":
        await query.message.edit_text(
            text=HELP_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('ʜᴏᴍᴇ', callback_data='start'),
                 InlineKeyboardButton("ᴄʟᴏꜱᴇ", callback_data='close')]
            ])
        )

    elif data == "about":
        await query.message.edit_text(
            text=ABOUT_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('ʜᴏᴍᴇ', callback_data='start'),
                 InlineKeyboardButton('ᴄʟᴏꜱᴇ', callback_data='close')]
            ])
        )

    elif data == "start":
        start_msg = await db.get_setting("start_msg", START_MSG)
        await query.message.edit_text(
            text=safe_format_user(start_msg, query.from_user),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ʜᴇʟᴘ", callback_data='help'),
                 InlineKeyboardButton("ᴀʙᴏᴜᴛ", callback_data='about')]
            ])
        )


    elif data == "show_referral":
        user_id = int(query.from_user.id)
        valid_count = await db.get_referral_count(user_id)
        pending_count = await db.get_pending_referral_count(user_id)
        rewards = await db.get_referral_rewards(user_id)
        remaining = REFERRAL_REWARD_COUNT - (valid_count % REFERRAL_REWARD_COUNT)
        if remaining == 0:
            remaining = REFERRAL_REWARD_COUNT
        link = f"https://t.me/{client.username}?start=ref_{user_id}"
        await query.message.edit_text(
            "<b>🎁 Your Referral Link</b>\n\n"
            f"<code>{link}</code>\n\n"
            f"<b>Valid referrals:</b> <code>{valid_count}</code>\n"
            f"<b>Pending referrals:</b> <code>{pending_count}</code>\n"
            f"<b>Reward:</b> <code>{REFERRAL_REWARD_DAYS} days premium for every {REFERRAL_REWARD_COUNT} valid referrals</code>\n"
            f"<b>Remaining for next reward:</b> <code>{remaining}</code>\n"
            f"<b>Rewards received:</b> <code>{len(rewards)}</code>\n\n"
            "<i>Referral counts only when invited user joins all required channels and opens the bot again.</i>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔁 Share Referral Link", url=f"https://telegram.me/share/url?url={link}")],
                [InlineKeyboardButton("💎 Premium Plans", callback_data="premium")],
                [InlineKeyboardButton("ʜᴏᴍᴇ", callback_data="start"), InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")],
            ]),
            disable_web_page_preview=True,
        )

    elif data == "premium":
        try:
            await query.message.delete()
        except Exception:
            pass
        caption = _format_premium_text(query.from_user)
        try:
            await client.send_photo(
                chat_id=query.message.chat.id,
                photo=QR_PIC,
                caption=caption,
                reply_markup=_premium_markup(),
                disable_web_page_preview=True,
            )
        except Exception:
            await client.send_message(
                chat_id=query.message.chat.id,
                text=caption,
                reply_markup=_premium_markup(),
                disable_web_page_preview=True,
            )

    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass

    elif data.startswith("rfs_ch_"):
        cid = int(data.split("_")[2])
        try:
            chat = await client.get_chat(cid)
            mode = await db.get_channel_mode(cid)
            status = "🟢 ᴏɴ" if mode == "on" else "🔴 ᴏғғ"
            new_mode = "off" if mode == "on" else "on"
            buttons = [
                [InlineKeyboardButton(f"ʀᴇǫ ᴍᴏᴅᴇ {'OFF' if mode == 'on' else 'ON'}", callback_data=f"rfs_toggle_{cid}_{new_mode}")],
                [InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="fsub_back")]
            ]
            await query.message.edit_text(
                f"Channel: {chat.title}\nCurrent Force-Sub Mode: {status}",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except Exception:
            await query.answer("Failed to fetch channel info", show_alert=True)

    elif data.startswith("rfs_toggle_"):
        cid, action = data.split("_")[2:]
        cid = int(cid)
        mode = "on" if action == "on" else "off"

        await db.set_channel_mode(cid, mode)
        await query.answer(f"Force-Sub set to {'ON' if mode == 'on' else 'OFF'}")

        # Refresh the same channel's mode view
        chat = await client.get_chat(cid)
        status = "🟢 ON" if mode == "on" else "🔴 OFF"
        new_mode = "off" if mode == "on" else "on"
        buttons = [
            [InlineKeyboardButton(f"ʀᴇǫ ᴍᴏᴅᴇ {'OFF' if mode == 'on' else 'ON'}", callback_data=f"rfs_toggle_{cid}_{new_mode}")],
            [InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="fsub_back")]
        ]
        await query.message.edit_text(
            f"Channel: {chat.title}\nCurrent Force-Sub Mode: {status}",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif data == "fsub_back":
        channels = await db.show_channels()
        buttons = []
        for cid in channels:
            try:
                chat = await client.get_chat(cid)
                mode = await db.get_channel_mode(cid)
                status = "🟢" if mode == "on" else "🔴"
                buttons.append([InlineKeyboardButton(f"{status} {chat.title}", callback_data=f"rfs_ch_{cid}")])
            except:
                continue

        await query.message.edit_text(
            "sᴇʟᴇᴄᴛ ᴀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴛᴏɢɢʟᴇ ɪᴛs ғᴏʀᴄᴇ-sᴜʙ ᴍᴏᴅᴇ:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
