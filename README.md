# dico
**This project is still in development, therefore I won't accept any PRs or Issues in this point.**

Yet another Discord API wrapper for Python, aimed to follow Discord API format as much as possible but also simple to use.

## Features
soon™

## Quick Example
```py
import dico


client = dico.Client("YOUR_TOKEN_HERE", intents=dico.Intents.full())


@client.on_("MESSAGE_CREATE")
async def on_message_create(message: dico.MessageCreate):
    if message.content.startswith("!hello"):
        # This request part will be improved later.
        await client.http.create_message(message.channel_id, "Hello, World!", *[None for x in range(5)])


client.run()
```

## Requirements
- Python 3.7+
