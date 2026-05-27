#BotWorld4U
#BotWorld4U on Tg

import motor.motor_asyncio
import logging
import time
from config import DB_URI, DB_NAME

logging.basicConfig(level=logging.INFO)


class Rohit:

    def __init__(self, DB_URI, DB_NAME):
        self.dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
        self.database = self.dbclient[DB_NAME]

        self.channel_data = self.database['channels']
        self.admins_data = self.database['admins']
        self.user_data = self.database['users']
        self.banned_user_data = self.database['banned_user']
        self.autho_user_data = self.database['autho_user']
        self.del_timer_data = self.database['del_timer']
        self.fsub_data = self.database['fsub']   
        self.rqst_fsub_data = self.database['request_forcesub']
        self.rqst_fsub_Channel_data = self.database['request_forcesub_channel']
        self.settings_data = self.database['bot_settings']
        self.sex_data = self.database['verify_counts']
        self.verify_tokens_data = self.database['verify_tokens']
        self.referral_data = self.database['referrals']
        self.referral_rewards_data = self.database['referral_rewards']

    async def ensure_indexes(self):
        """Create lightweight indexes for faster admin/force-sub/user lookups."""
        try:
            await self.user_data.create_index('_id')
            await self.admins_data.create_index('_id')
            await self.banned_user_data.create_index('_id')
            await self.fsub_data.create_index('_id')
            await self.rqst_fsub_Channel_data.create_index('_id')
            await self.settings_data.create_index('_id')
            await self.sex_data.create_index('_id')
            await self.sex_data.create_index('bypass_block_until')
            await self.verify_tokens_data.create_index('_id')
            await self.verify_tokens_data.create_index('expires_at')
            await self.referral_data.create_index('_id')
            await self.referral_data.create_index('referrer_id')
            await self.referral_data.create_index('counted')
            await self.referral_rewards_data.create_index('_id')
        except Exception as e:
            logging.warning(f"Index creation skipped/failed: {e}")


    # BOT SETTINGS / CUSTOMIZATION
    async def set_setting(self, key: str, value):
        await self.settings_data.update_one(
            {'_id': key},
            {'$set': {'value': value}},
            upsert=True
        )

    async def get_setting(self, key: str, default=None):
        data = await self.settings_data.find_one({'_id': key})
        if not data:
            return default
        return data.get('value', default)

    async def del_setting(self, key: str):
        await self.settings_data.delete_one({'_id': key})

    async def get_buttons(self, place: str):
        # place must be "start" or "force"
        buttons = await self.get_setting(f'{place}_buttons', [])
        return buttons if isinstance(buttons, list) else []

    async def add_button(self, place: str, text: str, url: str):
        buttons = await self.get_buttons(place)
        buttons.append({'text': text, 'url': url})
        await self.set_setting(f'{place}_buttons', buttons)
        return buttons

    async def del_button(self, place: str, index: int):
        buttons = await self.get_buttons(place)
        if index < 1 or index > len(buttons):
            return False
        buttons.pop(index - 1)
        await self.set_setting(f'{place}_buttons', buttons)
        return True

    async def clear_buttons(self, place: str):
        await self.set_setting(f'{place}_buttons', [])


    # USER DATA
    async def present_user(self, user_id: int):
        found = await self.user_data.find_one({'_id': user_id})
        return bool(found)

    async def add_user(self, user_id: int):
        await self.user_data.insert_one({'_id': user_id})
        return

    async def full_userbase(self):
        user_docs = await self.user_data.find().to_list(length=None)
        user_ids = [doc['_id'] for doc in user_docs]
        return user_ids

    async def del_user(self, user_id: int):
        await self.user_data.delete_one({'_id': user_id})
        return


    # ADMIN DATA
    async def admin_exist(self, admin_id: int):
        found = await self.admins_data.find_one({'_id': admin_id})
        return bool(found)

    async def add_admin(self, admin_id: int):
        if not await self.admin_exist(admin_id):
            await self.admins_data.insert_one({'_id': admin_id})
            return

    async def del_admin(self, admin_id: int):
        if await self.admin_exist(admin_id):
            await self.admins_data.delete_one({'_id': admin_id})
            return

    async def get_all_admins(self):
        users_docs = await self.admins_data.find().to_list(length=None)
        user_ids = [doc['_id'] for doc in users_docs]
        return user_ids


    # BAN USER DATA
    async def ban_user_exist(self, user_id: int):
        found = await self.banned_user_data.find_one({'_id': user_id})
        return bool(found)

    async def add_ban_user(self, user_id: int):
        if not await self.ban_user_exist(user_id):
            await self.banned_user_data.insert_one({'_id': user_id})
            return

    async def del_ban_user(self, user_id: int):
        if await self.ban_user_exist(user_id):
            await self.banned_user_data.delete_one({'_id': user_id})
            return

    async def get_ban_users(self):
        users_docs = await self.banned_user_data.find().to_list(length=None)
        user_ids = [doc['_id'] for doc in users_docs]
        return user_ids



    # AUTO DELETE TIMER SETTINGS
    async def set_del_timer(self, value: int):        
        existing = await self.del_timer_data.find_one({})
        if existing:
            await self.del_timer_data.update_one({}, {'$set': {'value': value}})
        else:
            await self.del_timer_data.insert_one({'value': value})

    async def get_del_timer(self):
        data = await self.del_timer_data.find_one({})
        if data:
            return data.get('value', 600)
        return 0


    # CHANNEL MANAGEMENT
    async def channel_exist(self, channel_id: int):
        found = await self.fsub_data.find_one({'_id': channel_id})
        return bool(found)

    async def add_channel(self, channel_id: int):
        if not await self.channel_exist(channel_id):
            await self.fsub_data.insert_one({'_id': channel_id})
            return

    async def rem_channel(self, channel_id: int):
        if await self.channel_exist(channel_id):
            await self.fsub_data.delete_one({'_id': channel_id})
            return

    async def show_channels(self):
        channel_docs = await self.fsub_data.find().to_list(length=None)
        channel_ids = [doc['_id'] for doc in channel_docs]
        return channel_ids

    
# Get current mode of a channel
    async def get_channel_mode(self, channel_id: int):
        data = await self.fsub_data.find_one({'_id': channel_id})
        return data.get("mode", "off") if data else "off"

    # Set mode of a channel
    async def set_channel_mode(self, channel_id: int, mode: str):
        await self.fsub_data.update_one(
            {'_id': channel_id},
            {'$set': {'mode': mode}},
            upsert=True
        )

    # REQUEST FORCE-SUB MANAGEMENT

    # Add the user to the set of users for a   specific channel
    async def req_user(self, channel_id: int, user_id: int):
        try:
            await self.rqst_fsub_Channel_data.update_one(
                {'_id': int(channel_id)},
                {'$addToSet': {'user_ids': int(user_id)}},
                upsert=True
            )
        except Exception as e:
            print(f"[DB ERROR] Failed to add user to request list: {e}")


    # Method 2: Remove a user from the channel set
    async def del_req_user(self, channel_id: int, user_id: int):
        # Remove the user from the set of users for the channel
        await self.rqst_fsub_Channel_data.update_one(
            {'_id': channel_id}, 
            {'$pull': {'user_ids': user_id}}
        )

    # Check if the user exists in the set of the channel's users
    async def req_user_exist(self, channel_id: int, user_id: int):
        try:
            found = await self.rqst_fsub_Channel_data.find_one({
                '_id': int(channel_id),
                'user_ids': int(user_id)
            })
            return bool(found)
        except Exception as e:
            print(f"[DB ERROR] Failed to check request list: {e}")
            return False  


    # Method to check if a channel exists using show_channels
    async def reqChannel_exist(self, channel_id: int):
    # Get the list of all channel IDs from the database
        channel_ids = await self.show_channels()
        #print(f"All channel IDs in the database: {channel_ids}")

    # Check if the given channel_id is in the list of channel IDs
        if channel_id in channel_ids:
            #print(f"Channel {channel_id} found in the database.")
            return True
        else:
            #print(f"Channel {channel_id} NOT found in the database.")
            return False



    # REFERRAL SYSTEM
    async def set_pending_referral(self, user_id: int, referrer_id: int):
        """Save who invited user_id. Existing referral source is never overwritten."""
        user_id = int(user_id)
        referrer_id = int(referrer_id)
        if user_id == referrer_id or referrer_id <= 0:
            return False
        existing = await self.referral_data.find_one({'_id': user_id})
        if existing:
            return False
        await self.referral_data.insert_one({
            '_id': user_id,
            'referrer_id': referrer_id,
            'created_at': int(time.time()),
            'counted': False
        })
        return True

    async def get_referral_record(self, user_id: int):
        return await self.referral_data.find_one({'_id': int(user_id)})

    async def complete_referral_if_pending(self, user_id: int):
        """Mark referral as valid after invited user completes force-sub.

        Returns: (referrer_id, total_valid_count, reward_milestone) or (None, 0, 0).
        reward_milestone is 1 for 10, 2 for 20, etc. It is returned only once.
        """
        user_id = int(user_id)
        data = await self.referral_data.find_one({'_id': user_id})
        if not data or data.get('counted') is True:
            return None, 0, 0

        referrer_id = int(data.get('referrer_id') or 0)
        if referrer_id <= 0 or referrer_id == user_id:
            return None, 0, 0

        await self.referral_data.update_one(
            {'_id': user_id},
            {'$set': {'counted': True, 'counted_at': int(time.time())}},
            upsert=False
        )

        total = await self.referral_data.count_documents({'referrer_id': referrer_id, 'counted': True})
        return referrer_id, int(total), 0

    async def get_referral_count(self, referrer_id: int):
        return int(await self.referral_data.count_documents({'referrer_id': int(referrer_id), 'counted': True}))

    async def get_pending_referral_count(self, referrer_id: int):
        return int(await self.referral_data.count_documents({'referrer_id': int(referrer_id), 'counted': {'$ne': True}}))

    async def mark_referral_reward_given(self, referrer_id: int, milestone: int):
        """Return True only if this milestone reward was not already given."""
        referrer_id = int(referrer_id)
        milestone = int(milestone)
        data = await self.referral_rewards_data.find_one({'_id': referrer_id}) or {}
        rewards = data.get('milestones', [])
        if milestone in rewards:
            return False
        await self.referral_rewards_data.update_one(
            {'_id': referrer_id},
            {'$addToSet': {'milestones': milestone}, '$set': {'last_reward_at': int(time.time())}},
            upsert=True
        )
        return True

    async def get_referral_rewards(self, referrer_id: int):
        data = await self.referral_rewards_data.find_one({'_id': int(referrer_id)}) or {}
        rewards = data.get('milestones', [])
        return rewards if isinstance(rewards, list) else []


    # SECURE SHORTENER VERIFICATION TOKENS
    async def create_verify_token(self, token: str, user_id: int, decoded_payload: str, ttl_seconds: int = 120, short_url: str = None):
        """Store a one-time verify token for shortener links. Default validity is 2 minutes.

        short_url is stored after creating the shortener URL so the Heroku gateway can
        redirect without exposing the real short link inside the Telegram button.
        """
        now = int(time.time())
        ttl = int(ttl_seconds or 120)
        if ttl < 30:
            ttl = 120
        expires_at = now + ttl
        payload = {
            'user_id': int(user_id),
            'decoded_payload': str(decoded_payload),
            'expires_at': expires_at,
            'created_at': now,
            'used': False
        }
        if short_url:
            payload['short_url'] = str(short_url)
        await self.verify_tokens_data.update_one(
            {'_id': token},
            {'$set': payload},
            upsert=True
        )
        return token

    async def set_verify_token_short_url(self, token: str, short_url: str):
        """Attach the real shortener URL to an existing verify token."""
        await self.verify_tokens_data.update_one(
            {'_id': token},
            {'$set': {'short_url': str(short_url)}},
            upsert=False
        )


    async def get_verify_token(self, token: str):
        data = await self.verify_tokens_data.find_one({'_id': token})
        if not data:
            return None
        if int(data.get('expires_at', 0)) < int(time.time()):
            await self.verify_tokens_data.delete_one({'_id': token})
            return None
        return data

    async def delete_verify_token(self, token: str):
        await self.verify_tokens_data.delete_one({'_id': token})

    async def set_verify_count(self, user_id: int, count: int):
        await self.sex_data.update_one({'_id': int(user_id)}, {'$set': {'verify_count': int(count)}}, upsert=True)

    async def get_verify_count(self, user_id: int):
        data = await self.sex_data.find_one({'_id': int(user_id)})
        return int(data.get('verify_count', 0)) if data else 0

    async def inc_verify_count(self, user_id: int, amount: int = 1):
        await self.sex_data.update_one({'_id': int(user_id)}, {'$inc': {'verify_count': int(amount)}}, upsert=True)

    async def reset_all_verify_counts(self):
        await self.sex_data.update_many({}, {'$set': {'verify_count': 0}})

    async def get_total_verify_count(self):
        pipeline = [{"$group": {"_id": None, "total": {"$sum": "$verify_count"}}}]
        result = await self.sex_data.aggregate(pipeline).to_list(length=1)
        return int(result[0]["total"]) if result else 0

    async def set_verified_until(self, user_id: int, until_ts: int):
        """Set time-based verification session expiry for a user."""
        await self.sex_data.update_one(
            {'_id': int(user_id)},
            {'$set': {'verified_until': int(until_ts)}},
            upsert=True
        )

    async def get_verified_until(self, user_id: int):
        data = await self.sex_data.find_one({'_id': int(user_id)})
        if not data:
            return 0
        try:
            return int(data.get('verified_until', 0) or 0)
        except Exception:
            return 0

    async def clear_verified_session(self, user_id: int):
        await self.sex_data.update_one(
            {'_id': int(user_id)},
            {'$unset': {'verified_until': ""}},
            upsert=True
        )

    async def clear_all_verified_sessions(self):
        await self.sex_data.update_many({}, {'$unset': {'verified_until': ""}})

    async def get_bypass_data(self, user_id: int):
        data = await self.sex_data.find_one({'_id': int(user_id)})
        return data or {}

    async def get_bypass_block_until(self, user_id: int):
        data = await self.get_bypass_data(user_id)
        try:
            return int(data.get('bypass_block_until', 0) or 0)
        except Exception:
            return 0

    async def register_bypass_attempt(self, user_id: int, block_seconds: int = 600, max_warnings: int = 3):
        """Increase bypass warning count and temp-block user. Returns (warnings, banned, block_until)."""
        now = int(time.time())
        block_until = now + int(block_seconds or 600)
        await self.sex_data.update_one(
            {'_id': int(user_id)},
            {'$inc': {'bypass_warnings': 1}, '$set': {'bypass_block_until': block_until, 'last_bypass_at': now}},
            upsert=True
        )
        result = await self.sex_data.find_one({'_id': int(user_id)})
        warnings = int((result or {}).get('bypass_warnings', 1) or 1)
        banned = warnings >= int(max_warnings or 3)
        if banned:
            await self.add_ban_user(int(user_id))
            await self.sex_data.update_one(
                {'_id': int(user_id)},
                {'$set': {'bypass_banned_at': now}, '$unset': {'bypass_block_until': ''}},
                upsert=True
            )
        return warnings, banned, block_until

    async def reset_bypass_warnings(self, user_id: int):
        await self.sex_data.update_one(
            {'_id': int(user_id)},
            {'$unset': {'bypass_warnings': '', 'bypass_block_until': '', 'last_bypass_at': '', 'bypass_banned_at': ''}},
            upsert=True
        )



db = Rohit(DB_URI, DB_NAME)
