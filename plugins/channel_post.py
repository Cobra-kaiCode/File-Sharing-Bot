# Auto link generation is intentionally disabled.
# Admin/owner must reply /genlink to a file/message in bot PM to create a link.

from pyrogram import filters, Client
from pyrogram.types import Message
from bot import Bot
from helper_func import admin


@Bot.on_message(filters.private & admin & filters.command("manualmode_help"))
async def manualmode_help(client: Client, message: Message):
    await message.reply_text(
        "<b>Manual link mode is ON.</b>\n\n"
        "Send any file/message in bot PM, then reply <code>/genlink</code> to that message.\n"
        "Normal messages/files will not create links automatically."
    )
