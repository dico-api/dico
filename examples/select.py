import dico

client = dico.Client("YOUR_BOT_TOKEN")

client.on_ready = lambda ready: print(f"Bot ready, with {len(ready.guilds)} guilds.")


@client.on_message_create
async def on_message_create(message: dico.Message):
    if message.content.startswith("!select"):
        options = [
            dico.SelectOption(label="Label 1", value="l1"),
            dico.SelectOption(label="Label 2", value="l2"),
            dico.SelectOption(label="Label 3", value="l3")
        ]
        select = dico.SelectMenu(custom_id=f"select{message.guild_id}{message.id}{message.author.id}",
                                 options=options)
        row = dico.ActionRow(select)
        await message.reply("Select!", component=row)


@client.on_interaction_create
async def on_select_response(interaction: dico.Interaction):
    if not interaction.type.message_component or not interaction.data.component_type.select_menu:
        return
    resp = dico.InteractionResponse(callback_type=dico.InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
                                    data=dico.InteractionApplicationCommandCallbackData(content=f"You selected {interaction.data.values[0]}.",
                                                                                        flags=dico.InteractionApplicationCommandCallbackDataFlags.EPHEMERAL))
    await interaction.create_response(resp)

client.run()
