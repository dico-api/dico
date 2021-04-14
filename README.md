# dico
Yet another Discord API wrapper for Python.

## Features
- Supports both async/request, to support both standalone and backend.
- Cache with expiration time.

## Quick Example
```py
import dico


client = dico.Client("YOUR_TOKEN_HERE", intents=dico.Intents.full())


@client.on_("MESSAGE_CREATE")
async def on_message_create(message_create: dico.MessageCreate):
    message = message_create.message
    if message.content.startswith("!hello"):
        await client.http.create_message(message.channel_id, "Hello, World!", *[None for x in range(5)])


client.run()

```

## Requirements
- Python 3.7+
