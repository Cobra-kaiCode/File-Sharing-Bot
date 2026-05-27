#(©)BotWorld4U
#BotWorld4U on Tg #Dont remove this line

import base64
import re
import asyncio
import time
import html
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from config import *
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait
from database.database import *
try:
    from shortzy import Shortzy
except Exception:
    Shortzy = None



#used for cheking if a user is admin ~Owner also treated as admin level
async def check_admin(filter, client, update):
    try:
        user_id = update.from_user.id       
        return any([user_id == OWNER_ID, await db.admin_exist(user_id)])
    except Exception as e:
        print(f"! Exception in check_admin: {e}")
        return False

async def is_subscribed(client, user_id):
    channel_ids = await db.show_channels()

    if not channel_ids:
        return True

    if user_id == OWNER_ID:
        return True

    for cid in channel_ids:
        if not await is_sub(client, user_id, cid):
            # Retry once if join request might be processing
            mode = await db.get_channel_mode(cid)
            if mode == "on":
                await asyncio.sleep(2)  # give time for @on_chat_join_request to process
                if await is_sub(client, user_id, cid):
                    continue
            return False

    return True


async def is_sub(client, user_id, channel_id):
    try:
        member = await client.get_chat_member(channel_id, user_id)
        status = member.status
        #print(f"[SUB] User {user_id} in {channel_id} with status {status}")
        return status in {
            ChatMemberStatus.OWNER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.MEMBER
        }

    except UserNotParticipant:
        mode = await db.get_channel_mode(channel_id)
        if mode == "on":
            exists = await db.req_user_exist(channel_id, user_id)
            #print(f"[REQ] User {user_id} join request for {channel_id}: {exists}")
            return exists
        #print(f"[NOT SUB] User {user_id} not in {channel_id} and mode != on")
        return False

    except Exception as e:
        print(f"[!] Error in is_sub(): {e}")
        return False


async def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    base64_string = (base64_bytes.decode("ascii")).strip("=")
    return base64_string

async def decode(base64_string):
    base64_string = base64_string.strip("=") # links generated before this commit will be having = sign, hence striping them to handle padding errors.
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes) 
    string = string_bytes.decode("ascii")
    return string

async def decode_start_payload(payload: str):
    """
    Strict /start token checker.

    Old links supported:
      get-<message_id * abs(first_db_channel_id)>
      get-<start_product>-<end_product>

    New multi DB-channel links supported:
      getv2-<abs_db_channel_id>-<message_id>
      getv2-<abs_db_channel_id>-<start_message_id>-<end_message_id>

    It blocks edited links with extra prefix/suffix like yu3elk...7.
    """
    if not payload:
        return None

    payload = payload.strip().rstrip("=")

    if not re.fullmatch(r"[A-Za-z0-9_-]+", payload):
        return None

    if len(payload) % 4 == 1:
        return None

    try:
        padded = payload + "=" * (-len(payload) % 4)
        decoded_bytes = base64.b64decode(
            padded.encode("ascii"),
            altchars=b"-_",
            validate=True
        )
        decoded_text = decoded_bytes.decode("ascii")
    except Exception:
        return None

    allowed = (
        r"get-\d+(?:-\d+)?"                         # old one-channel format
        r"|getv2-\d+-\d+(?:-\d+)?"                  # new multi-channel format
    )
    if not re.fullmatch(allowed, decoded_text):
        return None

    original_payload = await encode(decoded_text)
    if original_payload != payload:
        return None

    return decoded_text


def get_db_channel_by_abs(client, abs_channel_id: int):
    """Return a DB channel object by absolute channel id."""
    try:
        abs_channel_id = abs(int(abs_channel_id))
    except Exception:
        return None
    channels_by_abs = getattr(client, "db_channels_by_abs", {}) or {}
    return channels_by_abs.get(abs_channel_id)


async def choose_db_channel(client):
    """Round-robin DB channel selector for new uploads."""
    channels = list(getattr(client, "db_channel_list", []) or [])
    if not channels:
        return getattr(client, "db_channel", None)
    if len(channels) == 1:
        return channels[0]

    index = await db.get_setting("db_round_robin_index", 0)
    try:
        index = int(index)
    except Exception:
        index = 0
    channel = channels[index % len(channels)]
    await db.set_setting("db_round_robin_index", (index + 1) % len(channels))
    return channel


async def reload_db_channels(client):
    """Refresh client DB channel cache from root config.py channels + runtime extra channels."""
    extra_ids = await db.get_setting("extra_db_channel_ids", [])
    if not isinstance(extra_ids, list):
        extra_ids = []

    channel_ids = []
    for cid in list(DB_CHANNEL_IDS) + list(extra_ids):
        try:
            cid = int(cid)
        except Exception:
            continue
        if cid != 0 and cid not in channel_ids:
            channel_ids.append(cid)

    channels = []
    channels_by_id = {}
    channels_by_abs = {}
    failed = []
    primary_channel = None
    for cid in channel_ids:
        try:
            chat = await client.get_chat(cid)
            test = await client.send_message(chat_id=chat.id, text="Test Message")
            await test.delete()
            channels.append(chat)
            channels_by_id[int(chat.id)] = chat
            channels_by_abs[abs(int(chat.id))] = chat
            if PRIMARY_DB_CHANNEL_ID and int(chat.id) == int(PRIMARY_DB_CHANNEL_ID):
                primary_channel = chat
        except Exception as e:
            failed.append((cid, str(e)))

    if channels:
        if primary_channel:
            channels = [primary_channel] + [c for c in channels if int(c.id) != int(primary_channel.id)]
        client.db_channel_list = channels
        client.db_channels = channels_by_id
        client.db_channels_by_abs = channels_by_abs
        client.primary_db_channel = primary_channel
        client.db_channel = primary_channel or channels[0]
        client.db_ready = True
    else:
        client.db_channel_list = []
        client.db_channels = {}
        client.db_channels_by_abs = {}
        client.primary_db_channel = None
        client.db_channel = None
        client.db_ready = False
    return channels, failed


async def get_messages(client, message_ids, db_channel=None):
    messages = []
    message_ids = list(message_ids)
    total_messages = 0
    channel = db_channel or getattr(client, "db_channel", None)
    if not channel:
        return messages
    while total_messages != len(message_ids):
        temb_ids = message_ids[total_messages:total_messages+200]
        try:
            msgs = await client.get_messages(
                chat_id=channel.id,
                message_ids=temb_ids
            )
        except FloodWait as e:
            await asyncio.sleep(e.x)
            msgs = await client.get_messages(
                chat_id=channel.id,
                message_ids=temb_ids
            )
        except Exception as e:
            print(f"[!] Error in get_messages(): {e}")
            msgs = []
        total_messages += len(temb_ids)
        if isinstance(msgs, list):
            messages.extend([m for m in msgs if m])
        elif msgs:
            messages.append(msgs)
    return messages

async def get_message_ref(client, message):
    """Return (db_channel, message_id) if message/link belongs to any DB channel."""
    db_channels = list(getattr(client, "db_channel_list", []) or [getattr(client, "db_channel", None)])
    db_channels = [c for c in db_channels if c]
    db_by_id = {int(c.id): c for c in db_channels}
    db_by_abs = {str(abs(int(c.id))): c for c in db_channels}
    db_by_private_link_id = {}
    for c in db_channels:
        abs_id = str(abs(int(c.id)))
        # Telegram private channel links use https://t.me/c/<id_without_-100>/<msg_id>
        # Example: -1002170811388 -> /c/2170811388/123
        db_by_private_link_id[abs_id[3:] if abs_id.startswith("100") else abs_id] = c
    db_by_username = {str(getattr(c, "username", "")).lower(): c for c in db_channels if getattr(c, "username", None)}

    if message.forward_from_chat:
        channel = db_by_id.get(int(message.forward_from_chat.id))
        if channel:
            return channel, message.forward_from_message_id
        return None, 0
    elif message.forward_sender_name:
        return None, 0
    elif message.text:
        pattern = r"https://t.me/(?:c/)?([^/]+)/([0-9]+)"
        matches = re.match(pattern, message.text.strip())
        if not matches:
            return None, 0
        channel_key = matches.group(1)
        msg_id = int(matches.group(2))
        channel = None
        if channel_key.isdigit():
            channel = db_by_private_link_id.get(channel_key) or db_by_abs.get(channel_key)
        else:
            channel = db_by_username.get(channel_key.lower().lstrip("@"))
        if channel:
            return channel, msg_id
    return None, 0

async def get_message_id(client, message):
    """Backward compatible helper: returns only the message ID."""
    _channel, msg_id = await get_message_ref(client, message)
    return msg_id


def get_readable_time(seconds: int) -> str:
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    hmm = len(time_list)
    for x in range(hmm):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        up_time += f"{time_list.pop()}, "
    time_list.reverse()
    up_time += ":".join(time_list)
    return up_time


def get_exp_time(seconds):
    periods = [('days', 86400), ('hours', 3600), ('mins', 60), ('secs', 1)]
    result = ''
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f'{int(period_value)} {period_name}'
    return result


def safe_format_user(template: str, user):
    values = {
        "first": getattr(user, "first_name", None) or "",
        "last": getattr(user, "last_name", None) or "",
        "username": None if not getattr(user, "username", None) else "@" + user.username,
        "mention": getattr(user, "mention", ""),
        "id": getattr(user, "id", "")
    }
    try:
        return template.format(**values)
    except Exception as e:
        print(f"[!] Message template format error: {e}")
        return template


def str_to_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y", "on"}

async def get_runtime_setting(key: str, default=None):
    return await db.get_setting(key, default)


def _human_size(size):
    try:
        size = int(size or 0)
    except Exception:
        size = 0
    if size <= 0:
        return "Unknown"
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.2f} {unit}" if unit != "B" else f"{int(value)} {unit}"
        value /= 1024


def get_file_info_from_message(message):
    """Return filename, filesize and filetype safely for caption templates."""
    media_map = [
        ("document", getattr(message, "document", None)),
        ("video", getattr(message, "video", None)),
        ("audio", getattr(message, "audio", None)),
        ("animation", getattr(message, "animation", None)),
        ("photo", getattr(message, "photo", None)),
        ("voice", getattr(message, "voice", None)),
        ("video_note", getattr(message, "video_note", None)),
        ("sticker", getattr(message, "sticker", None)),
    ]
    for filetype, media in media_map:
        if not media:
            continue
        filename = getattr(media, "file_name", None)
        if not filename:
            if filetype == "photo":
                filename = "Photo.jpg"
            elif filetype == "video":
                filename = "Video.mp4"
            elif filetype == "audio":
                filename = "Audio.mp3"
            elif filetype == "animation":
                filename = "Animation.mp4"
            elif filetype == "voice":
                filename = "Voice.ogg"
            elif filetype == "video_note":
                filename = "VideoNote.mp4"
            elif filetype == "sticker":
                filename = "Sticker.webp"
            else:
                filename = "File"
        filesize = getattr(media, "file_size", None)
        return filename, filesize, filetype
    return "Message", None, "message"


def message_supports_caption(message) -> bool:
    return any(getattr(message, attr, None) for attr in ("document", "video", "audio", "animation", "photo"))


def format_file_caption(template: str, message):
    """Build custom caption. Supports {filename}, {filesize}, {filetype}, {caption}, {previouscaption}."""
    if not template:
        return None
    filename, filesize, filetype = get_file_info_from_message(message)
    previous_caption = "" if not getattr(message, "caption", None) else message.caption.html
    values = {
        "filename": html.escape(str(filename)),
        "filesize": html.escape(_human_size(filesize)),
        "filetype": html.escape(str(filetype)),
        "caption": previous_caption,
        "previouscaption": previous_caption,
        "channel": "@BotWorld4U",
        "credit": "@BotWorld4U",
    }
    try:
        return template.format(**values)
    except Exception as e:
        print(f"[!] Caption template format error: {e}")
        return template


async def get_shortlink(url, api, link):
    """Create short link safely. If shortener config is missing/fails, return original link."""
    url = (url or "").strip().replace("https://", "").replace("http://", "").strip("/")
    api = (api or "").strip()
    if not url or not api or Shortzy is None:
        return link
    try:
        shortzy = Shortzy(api_key=api, base_site=url)
        return await shortzy.convert(link)
    except Exception as e:
        print(f"[!] Shortener failed, using original link: {e}")
        return link

subscribed = filters.create(is_subscribed)
admin = filters.create(check_admin)

#BotWorld4U on Tg :