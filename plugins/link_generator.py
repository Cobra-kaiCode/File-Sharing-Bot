# Manual link generator for FileStore

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from pyrogram.enums import ParseMode
from asyncio import TimeoutError
import asyncio

from bot import Bot
from config import DISABLE_CHANNEL_BUTTON, CUSTOM_CAPTION
from helper_func import (
    encode,
    get_message_ref,
    choose_db_channel,
    admin,
    message_supports_caption,
    format_file_caption,
)
from database.database import db


def _share_markup(link: str):
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f"https://telegram.me/share/url?url={link}")]])


async def _make_link(client: Client, msg_id: int, db_channel=None):
    """Create strict v2 link that remembers which DB channel stores the file."""
    channel = db_channel or getattr(client, "db_channel", None)
    if not channel:
        raise RuntimeError("No DB channel connected. Fix PRIMARY_DB_CHANNEL_ID / EXTRA_DB_CHANNEL_IDS and make bot admin in DB channel.")
    base64_string = await encode(f"getv2-{abs(int(channel.id))}-{int(msg_id)}")
    return f"https://t.me/{client.username}?start={base64_string}"


async def _make_batch_link(client: Client, db_channel, start_msg_id: int, end_msg_id: int):
    if not db_channel:
        raise RuntimeError("No DB channel connected. Fix PRIMARY_DB_CHANNEL_ID / EXTRA_DB_CHANNEL_IDS and make bot admin in DB channel.")
    base64_string = await encode(f"getv2-{abs(int(db_channel.id))}-{int(start_msg_id)}-{int(end_msg_id)}")
    return f"https://t.me/{client.username}?start={base64_string}"


def _get_channel_by_command_index(client: Client, message: Message):
    """Optional DB channel selection: /genlink 2 or /custom_batch 2."""
    try:
        parts = (message.text or "").split(maxsplit=1)
        if len(parts) < 2:
            return None, None
        index = int(parts[1].strip())
    except Exception:
        return None, None

    channels = list(getattr(client, "db_channel_list", []) or [])
    if 1 <= index <= len(channels):
        return channels[index - 1], None
    return None, f"❌ Invalid DB channel number. Use /dbchannels to check available channels."


async def _copy_to_db_with_caption(source_msg: Message, db_channel_id: int):
    """Copy a user message/file to DB channel and apply the current custom caption there too.

    Earlier versions only applied the custom caption when users opened the /start link.
    This made DB-channel files still show the old/original caption.
    Now DB channel and user-delivered file both use the same custom caption.
    """
    copy_kwargs = {
        "chat_id": db_channel_id,
        "disable_notification": True,
    }

    custom_caption = await db.get_setting("custom_caption", CUSTOM_CAPTION)
    if custom_caption and message_supports_caption(source_msg):
        copy_kwargs.update({
            "caption": format_file_caption(custom_caption, source_msg),
            "parse_mode": ParseMode.HTML,
        })

    return await source_msg.copy(**copy_kwargs)


@Bot.on_message(filters.private & admin & filters.command('batch'))
async def batch(client: Client, message: Message):
    if not getattr(client, "db_channel_list", None):
        return await message.reply_text(
            "<b>❌ No DB channel connected.</b>\n\n"
            "Fix <code>PRIMARY_DB_CHANNEL_ID</code> in <code>config.py</code>, "
            "make bot admin in DB channel, then redeploy/restart."
        )

    while True:
        try:
            first_message = await client.ask(
                text="Forward the First Message from DB Channel (with Quotes)..\n\nor Send the DB Channel Post Link",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except Exception:
            return
        f_channel, f_msg_id = await get_message_ref(client, first_message)
        if f_channel and f_msg_id:
            break
        await first_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channels or this Link is not taken from DB Channels", quote=True)

    while True:
        try:
            second_message = await client.ask(
                text="Forward the Last Message from the SAME DB Channel (with Quotes)..\nor Send the DB Channel Post link",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except Exception:
            return
        s_channel, s_msg_id = await get_message_ref(client, second_message)
        if s_channel and s_msg_id:
            if int(s_channel.id) != int(f_channel.id):
                await second_message.reply("❌ Error\n\nFirst and last message must be from the SAME DB channel.", quote=True)
                continue
            break
        await second_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channels or this Link is not taken from DB Channels", quote=True)

    link = await _make_batch_link(client, f_channel, f_msg_id, s_msg_id)
    await second_message.reply_text(f"<b>Here is your batch link</b>\n\n{link}", quote=True, reply_markup=_share_markup(link))


@Bot.on_message(filters.private & admin & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    """
    Manual mode:
    - Reply /genlink to any file/message sent in bot PM -> bot stores it in a DB channel and creates link.
    - DB channel is selected by round-robin when multiple DB channels are configured.
    - If not replied, DB-channel forward/link flow is still available.
    """
    if message.reply_to_message:
        if not getattr(client, "db_channel_list", None):
            return await message.reply_text(
                "<b>❌ No DB channel connected.</b>\n\n"
                "Fix <code>PRIMARY_DB_CHANNEL_ID</code> in <code>config.py</code>, "
                "make bot admin in that channel with post/delete permission, then redeploy/restart.",
                quote=True
            )
        selected_channel, index_error = _get_channel_by_command_index(client, message)
        if index_error:
            return await message.reply_text(f"<b>{index_error}</b>", quote=True)
        db_channel = selected_channel or await choose_db_channel(client)
        wait = await message.reply_text(f"<b>Saving to DB channel...</b>\n<code>{db_channel.id}</code>", quote=True)
        try:
            post_message = await _copy_to_db_with_caption(message.reply_to_message, db_channel.id)
        except FloodWait as e:
            await asyncio.sleep(e.x)
            post_message = await _copy_to_db_with_caption(message.reply_to_message, db_channel.id)
        except Exception as e:
            return await wait.edit_text(f"<b>❌ Failed to save message.</b>\n<code>{e}</code>")

        link = await _make_link(client, post_message.id, db_channel)
        reply_markup = _share_markup(link)
        await wait.edit_text(
            f"<b>Here is your link</b>\n\n{link}\n\n<b>DB Channel:</b> <code>{db_channel.id}</code>",
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )

        if not DISABLE_CHANNEL_BUTTON:
            try:
                await post_message.edit_reply_markup(reply_markup)
            except Exception:
                pass
        return

    # Fallback flow for already-saved DB channel posts
    while True:
        try:
            channel_message = await client.ask(
                text=(
                    "Reply /genlink to any file/message to create a new link.\n\n"
                    "Or forward Message from any DB Channel (with Quotes)..\n"
                    "or send the DB Channel Post link"
                ),
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except Exception:
            return
        db_channel, msg_id = await get_message_ref(client, channel_message)
        if db_channel and msg_id:
            break
        await channel_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channels or this Link is not taken from DB Channels", quote=True)

    link = await _make_link(client, msg_id, db_channel)
    await channel_message.reply_text(
        f"<b>Here is your link</b>\n\n{link}\n\n<b>DB Channel:</b> <code>{db_channel.id}</code>",
        quote=True,
        reply_markup=_share_markup(link)
    )


@Bot.on_message(filters.private & admin & filters.command("custom_batch"))
async def custom_batch(client: Client, message: Message):
    if not getattr(client, "db_channel_list", None):
        return await message.reply_text(
            "<b>❌ No DB channel connected.</b>\n\n"
            "Fix <code>PRIMARY_DB_CHANNEL_ID</code> in <code>config.py</code>, "
            "make bot admin in DB channel, then redeploy/restart."
        )

    collected = []
    selected_channel, index_error = _get_channel_by_command_index(client, message)
    if index_error:
        return await message.reply_text(f"<b>{index_error}</b>")
    db_channel = selected_channel or await choose_db_channel(client)
    STOP_KEYBOARD = ReplyKeyboardMarkup([["STOP"]], resize_keyboard=True)

    await message.reply(
        f"Send all messages you want to include in batch.\n\n"
        f"They will be saved in DB channel: <code>{db_channel.id}</code>\n\n"
        "Press STOP when you're done.",
        reply_markup=STOP_KEYBOARD
    )

    while True:
        try:
            user_msg = await client.ask(
                chat_id=message.chat.id,
                text="Waiting for files/messages...\nPress STOP to finish.",
                timeout=60
            )
        except TimeoutError:
            break

        if user_msg.text and user_msg.text.strip().upper() == "STOP":
            break

        try:
            sent = await _copy_to_db_with_caption(user_msg, db_channel.id)
            collected.append(sent.id)
        except Exception as e:
            await message.reply(f"❌ Failed to store a message:\n<code>{e}</code>")
            continue

    await message.reply("✅ Batch collection complete.", reply_markup=ReplyKeyboardRemove())

    if not collected:
        await message.reply("❌ No messages were added to batch.")
        return

    link = await _make_batch_link(client, db_channel, collected[0], collected[-1])
    await message.reply(
        f"<b>Here is your custom batch link:</b>\n\n{link}\n\n<b>DB Channel:</b> <code>{db_channel.id}</code>",
        reply_markup=_share_markup(link)
    )
