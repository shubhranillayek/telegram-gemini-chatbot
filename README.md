# Telegram Gemini Chatbot

A Telegram chatbot that actually talks back — powered by Google's Gemini AI.
You send it a message, it sends your words to Gemini (through the free
Google AI Studio API), and replies like a person would. It remembers the
last few messages of your conversation, so follow-up questions just work.

Built with Python, [python-telegram-bot](https://docs.python-telegram-bot.org/)
and the official [google-genai](https://github.com/googleapis/python-genai) SDK.

**Prefer no-code?** The same chatbot also comes as an **n8n workflow** in
the [`n8n/`](n8n/) folder — import the JSON into n8n, add your two keys,
switch it on. See [`n8n/README.md`](n8n/README.md) for the steps.

![How the chatbot flow looks on the n8n canvas: Telegram Trigger, then the Gemini node, then the reply back to Telegram](n8n-workflow-preview.png)

## What it does

- Answers any text message using Gemini — questions, explanations, drafts,
  ideas, practice conversations, whatever you type
- Remembers the recent conversation per user, so "and why does that happen?"
  makes sense to it
- Keeps every user's conversation separate — two people chatting at once
  never see each other's context
- Shows the "typing…" indicator while Gemini is thinking
- Splits long answers into multiple messages (Telegram caps a message at
  4096 characters)
- Fails politely: if the API hiccups, the user gets a friendly "try again"
  message instead of silence

## Commands

| Command  | What it does                                  |
| -------- | --------------------------------------------- |
| `/start` | Greet the user and explain the bot            |
| `/help`  | List the commands                             |
| `/clear` | Forget the conversation and start fresh       |

Everything else typed in the chat goes to Gemini.

## A short demo

```
You:  /start
Bot:  Hi! I'm a chatbot powered by Google Gemini. Ask me anything —
      explain a topic, draft a message, brainstorm ideas...

You:  Explain photosynthesis like I'm 12.
Bot:  Think of a leaf as a tiny kitchen. Sunlight is the stove,
      water and air are the ingredients, and the plant cooks up
      sugar for food. The leftover smell from the kitchen is
      oxygen — which is what we breathe.

You:  And why do leaves turn yellow in winter?
Bot:  Because that kitchen slows down. With less sunlight the
      plant stops making the green chemical it cooks with, so
      the yellow colours that were there all along show through.
```

Notice the second answer: the bot knew you were still talking about leaves.
That is the conversation memory at work.

## What you need

- Python 3.10 or newer
- A Telegram account (to create the bot with BotFather)
- A free Gemini API key from Google AI Studio
- About 15 minutes

No server and no payment needed to try it. The bot runs on your own
computer while the script is running.

## Setup, step by step

### 1. Get the code and install the packages

Download or clone this project, open a terminal in its folder, and create
a virtual environment (a private box for this project's packages):

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Create the Telegram bot

Open Telegram, talk to [@BotFather](https://t.me/BotFather) (the one with
the blue verified tick), send `/newbot`, and follow the two questions —
a display name, then a username ending in `bot`. BotFather replies with a
**token**: a long string that is your bot's password. Keep it for step 4.

### 3. Get your free Gemini API key

1. Go to [Google AI Studio](https://aistudio.google.com/) and sign in with
   a Google account.
2. Open [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
   (or click **Get API key** in the left menu).
3. Click **Create API key**. If it asks, create or pick a Google Cloud
   project — the default choice is fine.
4. Copy the key it shows you. It starts with `AIza`.

The key is free. The free tier has daily limits that are plenty for
personal use and testing — you do not need to add a card.

### 4. Put both keys in a `.env` file

Copy the example file and fill it in:

```bash
cp .env.example .env             # Windows: copy .env.example .env
```

```ini
TELEGRAM_BOT_TOKEN=123456789:AAE...your-botfather-token...
GEMINI_API_KEY=AIza...your-gemini-key...
GEMINI_MODEL=gemini-2.5-flash
```

The `.env` file is listed in `.gitignore`, so Git will never upload it.
Keys belong here — never inside the code, never in a screenshot.

### 5. Run it

```bash
python bot.py
```

Open your bot in Telegram, press **Start**, and send it a message.
Stop the bot any time with `Ctrl+C`.

## Configuration

| Variable           | Required | Default           | What it is                                   |
| ------------------ | -------- | ----------------- | -------------------------------------------- |
| `TELEGRAM_BOT_TOKEN` | Yes    | —                 | The token BotFather gave you                 |
| `GEMINI_API_KEY`   | Yes      | —                 | Your Google AI Studio key                    |
| `GEMINI_MODEL`     | No       | `gemini-2.5-flash` | Which Gemini model answers. Flash models are fast and suit chat. |

## Project structure

```
telegram-gemini-chatbot/
├── bot.py            # Telegram side: commands, handlers, message flow
├── gemini_chat.py    # Gemini side: API client + per-user memory
├── requirements.txt  # The three packages the project needs
├── .env.example      # Template for your keys (copy it to .env)
├── .gitignore        # Keeps .env and local files out of Git
├── n8n/              # The same chatbot as an n8n workflow (no-code version)
│   ├── telegram-gemini-chatbot.workflow.json
│   └── README.md     # Import + credential steps for n8n
└── LICENSE           # MIT
```

The split is deliberate: `bot.py` knows about Telegram and nothing about
AI, and `gemini_chat.py` knows about Gemini and nothing about Telegram.
Swap either side without touching the other.

## Make it yours

The bot's personality lives in one place: `SYSTEM_PROMPT` at the top of
`gemini_chat.py`. Change that one string and the same code becomes a
patient maths tutor, a Hindi-speaking practice partner, a support bot for
your shop that only answers from your price list — whatever you describe.
The memory length is the `max_turns` value (default 10 exchanges).

## Keeping it online

While `python bot.py` runs, the bot answers; when the script stops, it
sleeps. For a bot that answers at 3 AM too, run it on any always-on
machine — a small VPS is the usual choice. Copy the folder over, repeat
steps 1, 4 and 5 there, and run it under a process manager (systemd on
Linux) so it restarts itself after a reboot or a crash.

## Small troubles

- **`ModuleNotFoundError`** — the virtual environment is off. Run the
  activate command again (your prompt should start with `(.venv)`), then
  `pip install -r requirements.txt`.
- **"TELEGRAM_BOT_TOKEN is not set"** — the `.env` file is missing, named
  wrong (`.env.txt` does not count), or the line is empty.
- **Bot runs but never replies** — check you are messaging the bot the
  token belongs to, and that you pressed **Start** in the chat.
- **Gemini errors about quota** — the free tier's daily limit is reached.
  It resets the next day; heavy testing can also switch `GEMINI_MODEL` to
  a lighter flash model.

## License

MIT — see [LICENSE](LICENSE). Use it, change it, build on it.

## Author

**Shubhranil Layek** — Python developer, Durgapur, India.
Portfolio: [shubhranillayek.github.io](https://shubhranillayek.github.io/)
· GitHub: [github.com/shubhranillayek](https://github.com/shubhranillayek)

I also build Telegram bots to order — FAQ and support bots, alert bots,
and AI chatbots like this one. If you need one for your business, the
portfolio above has my contact details.
