<div align="center">

# Schedule Assistant Bot

[![Python](https://img.shields.io/badge/Python_3.12-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![Telegram](https://img.shields.io/badge/Telegram_Bot-26a5e4?style=for-the-badge&logo=telegram&logoColor=white)](https://core.telegram.org/bots)
[![SQLite](https://img.shields.io/badge/SQLite-003b57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org)

_Telegram bot for 200+ university students — class schedules, daily quotes, and sticker search._

</div>

---

## About

A Telegram bot built by two students at Odessa Polytechnic University. Students use it to check their daily class schedule, get automated reminders, browse quotes by theme, and search stickers. Admins can broadcast announcements to all subscribers.

Supports Russian and Ukrainian interfaces.

## Features

- View today's/tomorrow's schedule with teacher names and classroom links
- Subscribe to daily schedule notifications
- Daily quotes by theme (motivation, success, etc.)
- Sticker search by keyword
- Customizable language, group, and quote preferences
- Admin broadcast to all subscribers

## Setup

**Requirements:** Python 3.12, Poetry

```bash
git clone https://github.com/KoolHackerz/schedule-assistant-bot.git
cd schedule-assistant-bot
poetry install
```

Create a `.env` file:
```
TOKEN=your_telegram_bot_token
ADMINS=comma_separated_admin_ids
```

Edit `rus_schedule.json` or `ukr_schedule.json` to match your class schedule, then:

```bash
cd src/bot
poetry run python main.py
```

### Sticker database (optional)

Create a `stickers.db` SQLite file with columns: `id`, `sticker_id`, `keyword`. You can use OCR to bulk-populate keywords.

## Logging

Uses `loguru` — logs stored in `logs/`, 10MB max file size with auto-compression.

## Authors

- [Nikita Zhmak (YoshkinKit)](https://github.com/YoshkinKit)
- [Ilya Veles (whoisridze)](https://github.com/whoisridze)
