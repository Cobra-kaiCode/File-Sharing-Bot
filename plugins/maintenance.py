import os
import sys
import time
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import OWNER_ID, LOG_FILE_NAME
from helper_func import admin, reload_db_channels
from database.database import db


def close_markup():
    return InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])


@Bot.on_message(filters.command("ping") & filters.private)
async def ping_cmd(client: Bot, message: Message):
    start = time.time()
    sent = await message.reply_text("<b>Ping...</b>")
    ms = round((time.time() - start) * 1000, 2)
    await sent.edit_text(f"<b>🏓 Pong!</b>\n<code>{ms} ms</code>")


@Bot.on_message(filters.command("checkdb") & filters.private & admin)
async def check_db_cmd(client: Bot, message: Message):
    msg = await message.reply_text("<b>Checking DB channels...</b>")
    channels, failed = await reload_db_channels(client)

    text = "<b>🗄 DB Channel Check</b>\n\n"
    if channels:
        text += "<b>✅ Connected:</b>\n"
        for i, chat in enumerate(channels, start=1):
            tag = " PRIMARY" if getattr(client, "db_channel", None) and int(chat.id) == int(client.db_channel.id) else ""
            text += f"{i}. <code>{chat.id}</code>{tag}\n"
        text += "\n"

    if failed:
        text += "<b>❌ Failed:</b>\n"
        for cid, reason in failed:
            text += f"• <code>{cid}</code>\n<code>{reason}</code>\n"
    elif channels:
        text += "<b>All DB channels are OK.</b>"
    else:
        text += "<b>No active DB channel found.</b>\nFix <code>PRIMARY_DB_CHANNEL_ID</code> in <code>config.py</code>."

    await msg.edit_text(text, reply_markup=close_markup())


@Bot.on_message(filters.command("logs") & filters.private)
async def logs_cmd(client: Bot, message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply_text("<b>❌ Only owner can use this command.</b>", reply_markup=close_markup())

    if not os.path.exists(LOG_FILE_NAME):
        return await message.reply_text("<b>❌ Log file not found.</b>", reply_markup=close_markup())

    await message.reply_document(LOG_FILE_NAME, caption="<b>Bot logs</b>")


@Bot.on_message(filters.command("restart") & filters.private)
async def restart_cmd(client: Bot, message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply_text("<b>❌ Only owner can use this command.</b>", reply_markup=close_markup())

    await message.reply_text("<b>⚠️ Bot restarting...</b>\nAll active tasks will stop.")
    os.execl(sys.executable, sys.executable, *sys.argv)
