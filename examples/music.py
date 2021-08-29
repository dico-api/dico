"""
This example music bot is powered by lavalink.py
"""

import re
import dico
import lavalink


client = dico.Client("YOUR_BOT_TOKEN")
lava = lavalink.Client(user_id=0)  # Your bot client ID
lava.add_node(host="localhost", port=0, password="PASSWORD", region="ko")
client.on_raw = lava.voice_update_handler
client.on_ready = lambda ready: print(f"Bot ready, with {len(ready.guilds)} guilds.")


def verify_voice_state(voice_state):
    if not voice_state or not voice_state.channel_id:
        return "Please connect or reconnect to the voice channel first."
    return None


color_accept = 0x3dd415
color_deny = 0xe74c3c
color_white = 0xe1e1e1


@client.on_message_create
async def on_message(message: dico.MessageCreate):
    if message.content.startswith("!connect"):
        voice_state = message.author.voice_state
        vv = verify_voice_state(voice_state)
        if vv:
            return await message.reply(embed=dico.Embed(description=vv, color=0xe74c3c))
        lava.player_manager.create(int(message.guild_id), region="ko")
        await client.ws.update_voice_state(str(message.guild_id), str(voice_state.channel_id), False, False)

    if message.content.startswith("!disconnect"):
        msg = await message.reply(embed=dico.Embed(description="Please wait, disconnecting..."))
        await client.ws.update_voice_state(str(message.guild_id), None, False, False)
        await msg.edit(embed=dico.Embed(description="Successfully disconnected from voice channel!", color=color_accept))
        player = lava.player_manager.get(int(message.guild_id))
        if player:
            await lava.player_manager.destroy(message.guild_id)

    if message.content.startswith("!play "):
        voice_state = message.author.voice_state
        vv = verify_voice_state(voice_state)
        if vv:
            return await message.reply(embed=dico.Embed(description=vv, color=color_deny))
        url = message.content[len("!play "):]
        if not re.match("https?://(?:www\.)?.+", url):
            url = f"ytsearch:{url}"
        player = lava.player_manager.get(int(message.guild_id))
        if not player:
            return await message.reply(embed=dico.Embed(description="Please run `!connect` first.", color=color_deny))
        resp = await player.node.get_tracks(url)
        if resp is None or len(resp["tracks"]) == 0:
            return await message.reply(embed=dico.Embed(description="Unable to find any song.", color=color_deny))
        msg = await message.reply(embed=dico.Embed(description="Found the music, please wait..."))
        track = None
        if resp["loadType"] == "PLAYLIST_LOADED":
            return await msg.edit(content="Sorry, playlist is not supported.")
        elif resp["loadType"] == "SEARCH_RESULT":
            return await msg.edit(content="Sorry, searching is not supported.")
        track = track or resp['tracks'][0]
        player.add(requester=message.author.id, track=track)
        if not player.is_playing:
            await player.play()
            await msg.edit(content="", embed=dico.Embed(description=f"Playing [{track['info']['title']}]({track['info']['uri']}).", color=color_accept))
        else:
            await msg.edit(content="", embed=dico.Embed(description=f"Added [{track['info']['title']}]({track['info']['uri']}) to queue.", color=color_accept))

    if message.content.startswith("!skip"):
        voice_state = message.author.voice_state
        vv = verify_voice_state(voice_state)
        if vv:
            return await message.reply(embed=dico.Embed(description=vv, color=color_deny))
        player = lava.player_manager.get(int(message.guild_id))
        msg = await message.reply(embed=dico.Embed(description="Skipping this music..."))
        await player.skip()
        await msg.edit(embed=dico.Embed(description="Done skipping!", color=color_accept))

    if message.content.startswith("!loop") or message.content.startswith("!repeat"):
        voice_state = message.author.voice_state
        vv = verify_voice_state(voice_state)
        if vv:
            return await message.reply(embed=dico.Embed(description=vv, color=color_deny))
        player = lava.player_manager.get(int(message.guild_id))
        player.set_repeat(not player.repeat)
        await message.reply(f"Repeat is {'enabled' if player.repeat else 'disabled'}.")


client.run()
