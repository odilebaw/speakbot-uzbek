# SpeakBot - PythonAnywhere Deployment Guide

## Step A - Upload to PythonAnywhere

1. Go to [PythonAnywhere](https://www.pythonanywhere.com) and log in
2. Go to the **Files** tab
3. Create folder: `/home/[username]/speakbot`
4. Upload all project files:
   - `bot.py`
   - `config.py`
   - `database.py`
   - `gemini_handler.py`
   - `questions.py`
   - `requirements.txt`

## Step B - Install libraries

1. Open **Bash console** from the Consoles tab
2. Run the following command:

```bash
pip3.10 install -r requirements.txt --user
```

3. Wait for all packages to install successfully

## Step C - Set real API keys

1. Go to the **Files** tab
2. Open `config.py`
3. Replace `YOUR_TOKEN_HERE` with your real Telegram bot token (from @BotFather)
4. Replace `YOUR_GEMINI_KEY_HERE` with your real Gemini API key (from Google AI Studio)
5. Replace `YOUR_TELEGRAM_ID_HERE` with your real Telegram ID (from @userinfobot)
6. Save the file

## Step D - Create always-on task

1. Go to the **Tasks** tab on PythonAnywhere
2. Add an always-on task with the following command:

```
python3.10 /home/[username]/speakbot/bot.py
```

3. The bot will start automatically and keep running

## Step E - Test the bot

1. Open Telegram
2. Find your bot (search by the username you set in @BotFather)
3. Send `/start` command
4. Check if the welcome message appears
5. Try sending `/help` to see all available commands
6. Try `/daily` to test the daily challenge feature

## Troubleshooting

- If the bot does not respond, check the task logs in the Tasks tab
- Make sure all API keys are correctly set in `config.py`
- If you get import errors, re-run `pip3.10 install -r requirements.txt --user`
- The database (`speakbot.db`) is created automatically on first run
