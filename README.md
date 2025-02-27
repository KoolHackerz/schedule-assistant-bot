# Schedule Assistant Bot

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue.svg" alt="Python 3.12">
  <img src="https://img.shields.io/badge/Platform-Telegram-blue.svg" alt="Platform: Telegram">
</div>

## 🤖 About The Bot

Schedule Assistant Bot is a versatile Telegram bot designed specifically for university students to keep track of their class schedules and receive daily inspirational quotes. Created by students from Odessa Polytechnic University, this bot simplifies schedule management and adds a touch of motivation to students' daily routines.

## ✨ Key Features

- **📅 Interactive Schedule Access**: Instant access to today's or tomorrow's class schedule
- **🌍 Multi-language Support**: Full functionality in both Russian and Ukrainian languages
- **🔔 Automated Notifications**: Daily schedule reminders at customizable times
- **💬 Daily Inspirational Quotes**: Thematic quotes to start the day with motivation
- **🔍 Sticker Search**: Find and share stickers with simple keyword searches
- **⚙️ User Preferences**: Customizable groups, languages, and quote themes
- **👑 Admin Features**: Send broadcast messages to all subscribed users

## 📋 Detailed Features

### For Students
- View complete daily class schedules with teacher information and classroom links
- Subscribe to automated schedule notifications
- Receive curated daily quotes based on chosen themes (motivation, success, etc.)
- Search and send stickers directly through the bot
- Customize language preferences and group assignments

### For Admins
- Send important announcements to all subscribed users through a dedicated admin interface

## 🛠️ Technical Requirements

- Python 3.12
- Poetry for dependency management
- SQLite database (included)

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/whoisridze/schedule-assistant-bot.git
   cd schedule-assistant-bot
   ```

2. **Install dependencies with Poetry:**
   ```bash
   poetry install
   ```

3. **Set up environment variables:**
   Create a `.env` file in the root directory:
   ```
   TOKEN=your_telegram_bot_token
   ADMINS=comma_separated_list_of_admin_user_ids
   ```

4. **Customize the schedule:**
   Edit the `rus_schedule.json` or `ukr_schedule.json` files to match your class schedule.

5. **Set up sticker database (optional):**
   Create a `stickers.db` file with a table containing:
   - `id`: Primary key
   - `sticker_id`: The Telegram sticker ID (can be found using online methods)
   - `keyword`: The search term associated with the sticker
   
   **Tip**: You can use OCR (Optical Character Recognition) to quickly populate keywords for many stickers.

6. **Start the bot:**
   ```bash
   cd src/bot
   poetry run python main.py
   ```

## 📱 Bot Navigation & Functionality

The bot supports both text commands and interactive buttons in its interface.

### Main Functions
- **Schedule Viewing**: Access today's or tomorrow's schedule via menu buttons
- **Sticker Search**: Enter keywords after choosing the sticker search option
- **Settings Management**: Change language, group, and quote preferences through the settings menu
- **Notifications**: Subscribe or unsubscribe to daily schedule updates
- **Quotes**: Receive daily inspirational quotes based on selected themes

**Note**: All major functions are accessible through the menu buttons that appear after starting the bot.

## 📊 Logging and Monitoring

The bot uses `loguru` for comprehensive logging:
- Logs are stored in the `logs/` directory
- 10MB maximum log file size with automatic compression
- Detailed timestamps and error tracking

## 🔧 Customization

- **Schedule Format**: Follow the JSON structure in the example files to create custom schedules
- **Quote Sources**: Edit the quote lists in the database to add new themes or content
- **Language Support**: Add new languages by creating additional translation files

## 👨‍💻 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
