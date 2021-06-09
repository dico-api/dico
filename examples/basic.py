import dico

client = dico.Client("YOUR_BOT_TOKEN")

client.on_ready = lambda ready: print(f"Bot ready, with {len(ready.guilds)} guilds.")


@client.on_message_create
async def on_message_create(message: dico.Message):
    if message.content.startswith("!ping"):
        await message.reply(f"Pong! {round(client.ws.ping*1000)}ms")

client.run()
