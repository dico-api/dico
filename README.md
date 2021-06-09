# dico
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/0eff61ab0fd741ff8e13a086699d6672)](https://www.codacy.com/gh/eunwoo1104/dico/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=eunwoo1104/dico&amp;utm_campaign=Badge_Grade)
[![Discord](https://img.shields.io/discord/832488748843401217)](https://discord.gg/QH4AXNySpB)

**This project is still in development, therefore I won't accept any PRs or Issues in this point.**

Yet another Discord API wrapper for Python, aimed to follow Discord API format as much as possible but also simple and easy to use.

[Discord Server](https://discord.gg/QH4AXNySpB)

## Features
- Discord v9 API
- Full interaction support
- More soon™

## Installation
Development Version:
```
pip install -U git+https://github.com/eunwoo1104/dico
```
PyPi(**Not Recommended**):
```
pip install -U dico-api
```

## Quick Example
```py
import dico


client = dico.Client("YOUR_BOT_TOKEN_HERE", intents=dico.Intents.full())


@client.on_("MESSAGE_CREATE")
async def on_message_create(message):
    if message.content.startswith("!hello"):
        await message.reply("Hello, World!")


client.run()
```

## Requirements
- Python 3.7+

## TODO
- Implement sync http client
- Documentation
- Implement Audit Log, etc...
