# Evento al presionar un botón
@client.event
async def on_interaction(interaction):
    global selected_audio
    custom_id = interaction.data['custom_id']
    if custom_id.startswith('play_sound_'):
        selected_audio = custom_id[len('play_sound_'):]
        await interaction.response.send_message(f'Añadido a la cola: {urllib.parse.unquote(selected_audio.replace(".mp3", ""))}', ephemeral=False, delete_after=5)
        guild_id = interaction.guild.id
        directorio = await cnf.obtener_directorio_sonidos(guild_id)
        await cnf.agregar_a_cola(interaction, f'{directorio}/{selected_audio}')

# Manejo de errores de permisos
@limpiar_mensajes.error
async def limpiar_mensajes_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("No tienes permiso para usar este comando.")

# Ejecutar el bot
client.run(cnf.token)