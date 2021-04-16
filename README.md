# dico
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/0eff61ab0fd741ff8e13a086699d6672)](https://www.codacy.com/gh/eunwoo1104/dico/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=eunwoo1104/dico&amp;utm_campaign=Badge_Grade)
[![Discord](https://img.shields.io/discord/832488748843401217)](https://discord.gg/RVGkZea7VX)

**This project is still in development, therefore I won't accept any PRs or Issues in this point. Also, badge's server invite link will be shown as expired for now for the same reason.**

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
