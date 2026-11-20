# Telegram Gemini Chatbot — n8n version

This folder has the same chatbot as the Python version in the main folder,
but built in **n8n** instead of code. No Python, no server script to keep
running by hand — n8n runs the flow for you.

When someone messages your bot on Telegram, the flow is simple:

**Telegram Trigger → Google Gemini (AI Studio) → Extract Gemini Reply → Telegram Send Message**

The user's message goes to Gemini, Gemini's answer comes back, and the
bot replies in the same chat.

File in this folder:

- `telegram-gemini-chatbot.workflow.json` — the workflow. This is the file
  you import into n8n.

## How it looks in n8n

Open the preview image in the main folder — `n8n-workflow-preview.png` —
to see the flow laid out on the n8n canvas before you import it.

## Import it, step by step

1. Open your n8n (your own instance, or n8n Cloud).
2. Top right, click the **…** menu, choose **Import from File** —
   in some versions it is under **Workflows → Import**.
3. Pick `telegram-gemini-chatbot.workflow.json`.
4. The workflow opens on the canvas with four nodes, already connected
   in order. It is imported inactive — nothing runs until you finish
   the two credentials below and switch it on.

## Create the two credentials

The workflow needs two keys. The imported file has placeholders for both,
on purpose — your real keys should never live inside a shared file.

### 1. Telegram credential (your BotFather token)

1. In n8n, open **Credentials → New**, search for **Telegram API**.
2. In the **Access Token** field, paste the token BotFather gave you
   when you created the bot (Telegram → @BotFather → `/newbot`).
3. Save it, give it a name like `Telegram account`.
4. Open the workflow, click the **Telegram Trigger** node, and select
   this credential. Do the same on the **Telegram Send Message** node —
   both nodes should use the same Telegram credential.

### 2. Gemini credential (your Google AI Studio key)

The Gemini node is an HTTP Request node that calls the Gemini API
directly, so the key goes in as a header credential:

1. In n8n, open **Credentials → New**, search for **Header Auth**.
2. Set **Name** to `X-goog-api-key`.
3. Set **Value** to your Gemini API key from Google AI Studio
   (aistudio.google.com/apikey → **Create API key** — it starts with
   `AIza`). The key is free; the free tier is plenty for testing.
4. Save it, give it a name like `Google Gemini API Key`.
5. Open the workflow, click the **Google Gemini (AI Studio)** node,
   and under **Credential for Header Auth**, select this credential.

## Activate it

1. With both credentials selected, click the **Active** toggle at the
   top right of the workflow (top right switch, it turns green/blue).
2. Open Telegram, find your bot, press **Start**, and send it any
   message — a question, "explain photosynthesis like I'm 12", anything.
3. The bot should reply with Gemini's answer in a few seconds.
4. To check a run, open the workflow's **Executions** tab in n8n — every
   message shows up there, node by node, so you can see exactly what
   Gemini returned.

To stop the bot, switch **Active** off again. Telegram will keep the
messages, the bot just will not answer them.

## What this version does — and does not do yet

- **Does:** answers any text message with Gemini
  (`gemini-2.5-flash`, changeable in the Gemini node's URL), replies in
  the same chat it was asked in.
- **Does not yet:** remember the conversation. This v1 is stateless —
  each message is answered on its own, so "and why does that happen?"
  will not know what "that" was. The Python version in the main folder
  already has short-term memory. Adding memory here is the natural
  next step (store the last few messages per chat, for example in an
  n8n Data Table or Redis, and send them with each request).
- **Also not handled yet:** photos, voice notes and stickers are ignored
  (text messages only), and very long Gemini answers may hit Telegram's
  4096-character message limit.

## Small troubles

- **Workflow is on but the bot never replies** — check the Telegram
  credential is selected on *both* Telegram nodes, and that you pressed
  **Start** in the chat with the bot the token belongs to.
- **401 / API key error on the Gemini node** — the Header Auth credential
  name must be exactly `X-goog-api-key`, and the value must be the AI
  Studio key, not the BotFather token. The two keys are easy to swap by
  mistake.
- **429 / quota error** — the Gemini free tier's daily limit is reached.
  It resets the next day.
- **Nothing in Executions** — the workflow is not Active, or the trigger
  webhook did not register. Switch it off and on once; n8n re-registers
  the Telegram webhook when the workflow activates.
