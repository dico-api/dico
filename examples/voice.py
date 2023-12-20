import re

import dico

client = dico.Client("YOUR_BOT_TOKEN")
client.on_ready = lambda ready: print(f"Bot ready, with {len(ready.guilds)} guilds.")


@client.on_message_create
async def on_message(message: dico.MessageCreate):
    if message.content.startswith("!connect"):
        voice_state = message.author.voice_state
        if not voice_state or not voice_state.channel_id:
            return await message.reply(
                "Please connect or reconnect to the voice channel first."
            )
        await client.connect_voice(message.guild_id, voice_state.channel_id)

    if message.content.startswith("!disconnect"):
        msg = await message.reply("Please wait, disconnecting...")
        voice_client = client.get_voice_client(message.guild_id)
        if voice_client:
            await voice_client.close()
        await msg.edit("Successfully disconnected from voice channel!")

    if message.content.startswith("!play "):
        voice_state = message.author.voice_state
        if not voice_state or not voice_state.channel_id:
            return await message.reply(
                "Please connect or reconnect to the voice channel first."
            )
        url = message.content[len("!play ") :]
        if not re.match("https?://(?:www\.)?.+", url):
            return await message.reply("Only URL is supported.")
        voice_client = client.get_voice_client(message.guild_id)
        if not voice_client:
            return await message.reply("Please run `!connect` first.")
        audio = dico.Audio(url)
        await voice_client.play(audio)


client.run()
