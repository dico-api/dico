import dico

client = dico.Client("YOUR_BOT_TOKEN")

client.on_ready = lambda ready: print(f"Bot ready, with {len(ready.guilds)} guilds.")


@client.on_message_create
async def on_message_create(message: dico.Message):
    if message.content.startswith("!embed"):
        embed = dico.Embed(
            title="Hello, Embed!",
            description="Here is the example embed.",
            timestamp=message.timestamp,
        )
        embed.set_author(name="Author Name")
        embed.add_field(name="Field 1", value="Value 1")
        embed.set_footer(text="Footer Text")
        await message.reply(embed=embed)


client.run()
