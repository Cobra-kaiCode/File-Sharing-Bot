# 🚀 Advanced FileStore Shortner Referral Premium Bot

An advanced Telegram File Sharing & Link Shortener Bot with premium system, referral rewards, force-subscribe support, admin controls, and secure file sharing.

This project is a modified and enhanced version of the original FileStore bot with additional premium features, improved management system, and custom optimizations.

---

# ✨ Features

## 📁 File Sharing System

* Store Telegram files permanently
* Generate secure shareable links
* Fast file retrieval system
* Auto link generation
* Protected content sharing

## 🔗 URL Shortener Support

* Integrated shortener system
* Earn-based link support
* Custom shortener compatibility
* Faster redirection handling

## 👑 Premium Features

* Premium user system
* Premium database support
* Bypass waiting limitations for premium users
* Advanced access management
* Premium expiry support

## 🎁 Referral System

* User referral rewards
* Invite tracking
* Reward-based premium unlocking
* Auto referral counting

## 📢 Force Subscribe System

* Mandatory channel join support
* Multiple channel verification
* Request join handling
* Auto subscription checking

## 🛠️ Admin Controls

* Broadcast system
* Ban / unban users
* Maintenance mode
* Settings manager
* User management tools
* Channel management

## ⚡ Performance Improvements

* Optimized bot handling
* Better database management
* Cleaner plugin structure
* Faster response handling
* Stable deployment support

---

# 📂 Project Structure

```bash
├── database/
│   ├── database.py
│   └── db_premium.py
│
├── plugins/
│   ├── admin.py
│   ├── banuser.py
│   ├── broadcast.py
│   ├── channel_post.py
│   ├── link_generator.py
│   ├── maintenance.py
│   ├── request_fsub.py
│   ├── route.py
│   ├── settings.py
│   └── start.py
│
├── bot.py
├── main.py
├── config.py
├── requirements.txt
└── Procfile
```

---

# ⚙️ Required Variables

Create a `.env` file or add variables in Heroku:

```env
API_ID=
API_HASH=
BOT_TOKEN=
MONGO_URI=
ADMINS=
CHANNEL_ID=
LOG_CHANNEL=
SHORTNER_API=
SHORTNER_WEBSITE=
BOT_USERNAME=
```

Additional premium/referral variables can also be configured depending on your setup.

---

# 🚀 Deployment

## 🔹 Deploy on Heroku

1. Fork this repository
2. Create a new Heroku app
3. Connect GitHub repository
4. Add all required environment variables
5. Deploy the app

---

## 🔹 Deploy Using Docker

```bash
git clone <your-repo-url>
cd <repo-name>
docker build -t filestore-bot .
docker run filestore-bot
```

---

# 📜 Complete Command List

## 👤 User Commands

| Command         | Description                     |
| --------------- | ------------------------------- |
| `/start`        | Start the bot                   |
| `/help`         | Open help menu                  |
| `/about`        | Show bot information            |
| `/commands`     | Show all commands               |
| `/premium`      | Premium system information      |
| `/myplan`       | Check your premium plan         |
| `/referral`     | Referral system details         |
| `/count`        | Count referral or user details  |
| `/batch`        | Generate batch file links       |
| `/genlink`      | Generate single file share link |
| `/custom_batch` | Generate custom batch links     |

---

## 👑 Premium Management Commands

| Command           | Description           |
| ----------------- | --------------------- |
| `/addpremium`     | Add premium user      |
| `/remove_premium` | Remove premium access |
| `/premium_users`  | List premium users    |

---

## 📢 Broadcast Commands

| Command       | Description                |
| ------------- | -------------------------- |
| `/broadcast`  | Broadcast message to users |
| `/pbroadcast` | Pin broadcast message      |
| `/dbroadcast` | Delete broadcast message   |

---

## 🚫 Ban Management Commands

| Command    | Description       |
| ---------- | ----------------- |
| `/ban`     | Ban a user        |
| `/unban`   | Unban a user      |
| `/banlist` | View banned users |

---

## 👨‍💻 Admin Management Commands

| Command      | Description   |
| ------------ | ------------- |
| `/add_admin` | Add new admin |
| `/deladmin`  | Remove admin  |
| `/admins`    | List admins   |

---

## 🔗 Shortener Settings Commands

| Command          | Description             |
| ---------------- | ----------------------- |
| `/shortener`     | Shortener information   |
| `/setshortener`  | Configure shortener     |
| `/setshortpic`   | Set shortener image     |
| `/setshortmsg`   | Set shortener message   |
| `/shortsettings` | View shortener settings |

---

## 🎁 Referral Settings Commands

| Command         | Description            |
| --------------- | ---------------------- |
| `/setrefbutton` | Set referral button    |
| `/setrefbot`    | Configure referral bot |
| `/delrefbutton` | Delete referral button |

---

## 📢 Force Subscribe Commands

| Command      | Description                       |
| ------------ | --------------------------------- |
| `/fsub_mode` | Enable or disable force subscribe |
| `/addchnl`   | Add force subscribe channel       |
| `/delchnl`   | Remove force subscribe channel    |
| `/listchnl`  | List all channels                 |
| `/delreq`    | Delete join requests              |

---

## ⚙️ Verification & Bypass Commands

| Command             | Description                |
| ------------------- | -------------------------- |
| `/verify_mode`      | Enable verification system |
| `/set_verify_time`  | Set verification cooldown  |
| `/bypass_settings`  | Configure bypass system    |
| `/set_bypass_time`  | Set bypass cooldown time   |
| `/set_bypass_block` | Configure bypass block     |
| `/set_bypass_warn`  | Configure warning message  |
| `/reset_bypass`     | Reset bypass settings      |

---

## 🖼️ Customization Commands

| Command           | Description                 |
| ----------------- | --------------------------- |
| `/setstartpic`    | Set start image             |
| `/setforcepic`    | Set force subscribe image   |
| `/setstartmsg`    | Set custom start message    |
| `/setforcemsg`    | Set force subscribe message |
| `/setcaption`     | Set custom caption          |
| `/caption`        | View caption                |
| `/delcaption`     | Delete caption              |
| `/testcaption`    | Test caption format         |
| `/addbutton`      | Add custom button           |
| `/delbutton`      | Delete custom button        |
| `/buttons`        | List custom buttons         |
| `/restriction`    | Restriction settings        |
| `/customsettings` | View custom settings        |
| `/resetcustom`    | Reset custom settings       |

---

## 📂 Database Channel Commands

| Command         | Description             |
| --------------- | ----------------------- |
| `/adddbchannel` | Add database channel    |
| `/deldbchannel` | Remove database channel |
| `/dbchannels`   | List database channels  |

---

## 🛠️ Utility & Maintenance Commands

| Command            | Description                |
| ------------------ | -------------------------- |
| `/stats`           | View bot statistics        |
| `/users`           | View total users           |
| `/dlt_time`        | Configure auto delete time |
| `/check_dlt_time`  | Check delete timer         |
| `/ping`            | Check bot ping             |
| `/checkdb`         | Check database status      |
| `/logs`            | Get bot logs               |
| `/restart`         | Restart the bot            |
| `/manualmode_help` | Manual mode help menu      |

---

# 🔥 Detailed Features

## 🔹 Advanced File Store System

* Permanent Telegram file storage
* Secure media sharing links
* Auto file indexing
* Batch file generation
* Custom batch support
* Link protection system

## 🔹 Premium Subscription System

* Time based premium access
* Premium expiry management
* Premium-only bypass features
* Premium database storage
* Plan checking system

## 🔹 Referral Reward System

* Invite based rewards
* Auto referral counting
* Referral button support
* Referral tracking system
* Referral-based premium unlocking

## 🔹 Verification & Security System

* Verification cooldown setup
* Anti-bypass protection
* Warning system
* Secure access management
* User verification system

## 🔹 Force Subscribe Module

* Multiple force subscribe channels
* Auto join verification
* Request join support
* Force subscribe custom messages
* Force subscribe custom images

## 🔹 Advanced Customization

* Custom start messages
* Custom captions
* Custom buttons
* Custom shortener messages
* Custom images and banners
* Full branding support

## 🔹 Broadcast & User Management

* Global broadcast system
* Pin broadcast support
* Ban/unban system
* Admin management
* User statistics
* User tracking

## 🔹 Deployment Support

* Heroku ready
* Docker support
* MongoDB integration
* Optimized plugin structure
* Stable long-term deployment

# 🧩 Tech Stack

* Python 3
* Pyrogram
* MongoDB
* Telegram Bot API
* Heroku / Docker

---

# 🙌 Credits

## 🌟 Base Repository

Base repo credits go to:

* urlCodeflix-Bots FileStore Repository[https://github.com/Codeflix-Bots/FileStore.git](https://github.com/Codeflix-Bots/FileStore.git)

---

## 🔥 Advanced Modification & Feature Development

Main owner and advanced feature provider:

* Telegram Channel: @BotWorld4U

### 👨‍💻 Developers

* @Truly_Innocent
* @AnimeEmperor

---

# ⚠️ Disclaimer

This project is made for educational and personal usage purposes only.
Use responsibly and follow Telegram Terms of Service.

---

# ⭐ Support

If you like this project:

* Star the repository ⭐
* Share with others 📢
* Support the developers ❤️

---

# 💖 Thank You

Thanks for using this Advanced FileStore Premium Bot.
