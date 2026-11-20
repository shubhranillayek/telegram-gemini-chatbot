"""The Gemini side of the bot: one small class that owns the API client,
keeps a short per-user conversation history, and turns a user's message
into a reply.

The API key is read from the environment (loaded from .env by bot.py).
Nothing here knows or cares about Telegram.
"""

import os

from google import genai
from google.genai import types

# How the bot should behave. Edit this to give your own bot a personality,
# a job, or rules ("answer like a patient maths tutor", "reply in Hindi",
# "keep answers under 100 words", and so on).
SYSTEM_PROMPT = (
    "You are a friendly assistant chatting inside Telegram. "
    "Answer clearly and helpfully, in plain language. "
    "Keep answers reasonably short unless the user asks for detail. "
    "Do not use markdown tables. Simple formatting is fine."
)

DEFAULT_MODEL = "gemini-2.5-flash"


class GeminiChat:
    """One user's conversation with Gemini, with a short memory."""

    def __init__(self, api_key=None, model=None, max_turns=10):
        self.client = genai.Client(api_key=api_key or os.environ["GEMINI_API_KEY"])
        self.model = model or os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
        # max_turns counts user+bot exchanges. Older turns are dropped so
        # the history (and the bill / quota use) stays small.
        self.max_turns = max_turns
        self.history = []

    def reset(self):
        """Forget the conversation so far (the /clear command)."""
        self.history = []

    async def reply(self, user_text):
        """Send one message and return Gemini's reply as plain text."""
        contents = self.history + [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_text)],
            )
        ]
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
            ),
        )
        text = (response.text or "").strip()
        if not text:
            raise RuntimeError("Gemini returned an empty reply.")

        # Remember both sides of this exchange.
        self.history.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_text)],
            )
        )
        self.history.append(
            types.Content(
                role="model",
                parts=[types.Part.from_text(text=text)],
            )
        )
        # Keep only the most recent turns.
        self.history = self.history[-2 * self.max_turns :]
        return text
