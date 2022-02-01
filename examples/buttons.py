import dico

client = dico.Client("YOUR_BOT_TOKEN")

client.on_ready = lambda ready: print(f"Bot ready, with {len(ready.guilds)} guilds.")


@client.on_message_create
async def on_message_create(message: dico.Message):
    if message.content.startswith("!button"):
        button = dico.Button(
            style=dico.ButtonStyles.PRIMARY, label="Hello!", custom_id="hello"
        )
        button2 = dico.Button(
            style=dico.ButtonStyles.DANGER, label="Bye!", custom_id="bye"
        )
        row = dico.ActionRow(button, button2)
        await message.reply("Button!", component=row)


@client.on_interaction_create
async def on_button_response(interaction: dico.Interaction):
    if (
        not interaction.type.message_component
        or not interaction.data.component_type.button
    ):
        return
    resp = dico.InteractionResponse(
        callback_type=dico.InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
        data=dico.InteractionApplicationCommandCallbackData(
            content=f"Yes, it's {interaction.data.custom_id}.",
            flags=dico.InteractionApplicationCommandCallbackDataFlags.EPHEMERAL,
        ),
    )
    await interaction.create_response(resp)


client.run()
