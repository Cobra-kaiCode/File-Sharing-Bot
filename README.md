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

# 📜 Commands

## 👤 User Commands

* `/start` — Start the bot
* `/help` — Show help menu
* `/about` — About the bot

## 👑 Admin Commands

* `/broadcast` — Send broadcast message
* `/ban` — Ban user
* `/unban` — Unban user
* `/maintenance` — Enable/disable maintenance
* `/stats` — Bot statistics

---

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
