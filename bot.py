from aiohttp import web
from plugins import web_server
import asyncio
import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
import pytz
from datetime import datetime

from config import *


CREDIT_TEXT = "BY @BotWorld4U"


def get_indian_time():
    """Returns the current time in IST."""
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist)


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN,
        )
        self.LOGGER = LOGGER

    async def _set_botfather_commands(self):
        """Automatically set BotFather command menu on every deploy/start."""
        try:
            from pyrogram.types import BotCommand
            commands = [BotCommand(command=cmd, description=desc) for cmd, desc in BOT_COMMANDS]
            await self.set_bot_commands(commands)
            self.LOGGER(__name__).info("BotFather commands updated successfully.")
        except Exception as e:
            self.LOGGER(__name__).warning(f"Failed to set BotFather commands: {e}")


    async def _sync_config_bootstrap(self):
        """Import root config.py admins, force-sub channels, and UI defaults into MongoDB on startup."""
        try:
            from database.database import db
            await db.ensure_indexes()

            for admin_id in ADMINS:
                try:
                    await db.add_admin(int(admin_id))
                except Exception as e:
                    self.LOGGER(__name__).warning(f"Failed to add config admin {admin_id}: {e}")

            for channel_id in FORCE_SUB_CHANNELS:
                try:
                    await db.add_channel(int(channel_id))
                except Exception as e:
                    self.LOGGER(__name__).warning(f"Failed to add config force-sub channel {channel_id}: {e}")

            # Load optional default UI settings from root config.py only when MongoDB has no value yet.
            default_settings = {
                "start_buttons": START_BUTTONS,
                "force_buttons": FORCE_BUTTONS,
                "ref_button": REFERRAL_BUTTON,
            }
            for key, value in default_settings.items():
                if value:
                    current = await db.get_setting(key, None)
                    if current is None:
                        await db.set_setting(key, value)
        except Exception as e:
            self.LOGGER(__name__).warning(f"Config bootstrap skipped/failed: {e}")

    async def _load_db_channels(self):
        """Connect primary + extra DB channels and keep primary as first channel.

        Important: bad DB channel config should NOT stop the worker.
        If DB channel is wrong, bot still starts, BotFather commands still get added,
        and /dbchannels will show what needs fixing. /genlink will show a clear error.
        """
        try:
            from database.database import db
            runtime_db_channels = await db.get_setting("extra_db_channel_ids", [])
            if not isinstance(runtime_db_channels, list):
                runtime_db_channels = []
        except Exception as e:
            self.LOGGER(__name__).warning(f"Could not read runtime DB channels from MongoDB: {e}")
            runtime_db_channels = []

        channel_ids = []
        for cid in list(DB_CHANNEL_IDS) + list(runtime_db_channels):
            try:
                cid = int(cid)
            except Exception:
                continue
            if cid != 0 and cid not in channel_ids:
                channel_ids.append(cid)

        self.db_channels = {}
        self.db_channels_by_abs = {}
        self.db_channel_list = []
        self.primary_db_channel = None
        self.db_channel = None
        self.db_channel_errors = []
        self.db_ready = False

        for cid in channel_ids:
            try:
                db_channel = await self.get_chat(cid)
                test = await self.send_message(chat_id=db_channel.id, text="Test Message")
                await test.delete()

                self.db_channels[int(db_channel.id)] = db_channel
                self.db_channels_by_abs[abs(int(db_channel.id))] = db_channel
                self.db_channel_list.append(db_channel)

                if PRIMARY_DB_CHANNEL_ID and int(db_channel.id) == int(PRIMARY_DB_CHANNEL_ID):
                    self.primary_db_channel = db_channel

                self.LOGGER(__name__).info(f"DB channel connected: {db_channel.id}")
            except Exception as e:
                error_text = f"{cid}: {e}"
                self.db_channel_errors.append(error_text)
                self.LOGGER(__name__).warning(f"Skipped DB channel {error_text}")
                self.LOGGER(__name__).warning("Make sure bot is admin and can post/delete messages in that channel.")

        if not self.db_channel_list:
            self.LOGGER(__name__).warning(f"No DB channel connected. Configured DB_CHANNEL_IDS: {channel_ids}")
            self.LOGGER(__name__).warning("Bot will stay online, but /genlink will not work until DB channel config is fixed.")
            return

        # Backward-compatible default channel for old links.
        # Prefer configured primary channel; fallback to first connected channel.
        self.db_channel = self.primary_db_channel or self.db_channel_list[0]
        self.db_ready = True

        # Keep primary channel at index 1 in /dbchannels and /genlink 1 when it is connected.
        if self.primary_db_channel:
            ordered = [self.primary_db_channel] + [c for c in self.db_channel_list if int(c.id) != int(self.primary_db_channel.id)]
            self.db_channel_list = ordered

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = get_indian_time()
        self.username = usr_bot_me.username
        self.set_parse_mode(ParseMode.HTML)

        # Set BotFather command menu before DB-channel checks.
        # So even if DB channel is wrong, commands are still added after deploy/start.
        await self._set_botfather_commands()
        await self._sync_config_bootstrap()
        await self._load_db_channels()

        self.LOGGER(__name__).info("Bot running. Credit: @BotWorld4U")
        self.LOGGER(__name__).info(f"Primary DB channel: {getattr(getattr(self, 'db_channel', None), 'id', None)}")
        self.LOGGER(__name__).info(f"Active DB channels: {len(getattr(self, 'db_channel_list', []) or [])}")

        app = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", int(PORT)).start()

        try:
            await self.send_message(
                OWNER_ID,
                text=(
                    "<b><blockquote>✅ Bot restarted / deployed successfully.</blockquote></b>\n\n"
                    f"<b>Username:</b> @{self.username}\n"
                    f"<b>Primary DB:</b> <code>{getattr(getattr(self, 'db_channel', None), 'id', 'not connected')}</code>\n"
                    f"<b>Total DB Channels:</b> <code>{len(getattr(self, 'db_channel_list', []) or [])}</code>\n"
                    f"<b>Web Gateway:</b> <code>{WEB_APP_URL or 'not set'}</code>\n"
                    "<b>Commands:</b> Auto-added in bot PM menu.\n\n"
                    "<b>Credit:</b> @BotWorld4U"
                ),
            )
        except Exception:
            pass

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")

    def run(self):
        """Run the bot."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.start())
        self.LOGGER(__name__).info("Bot is now running. Thanks to @BotWorld4U")
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            self.LOGGER(__name__).info("Shutting down...")
        finally:
            loop.run_until_complete(self.stop())
