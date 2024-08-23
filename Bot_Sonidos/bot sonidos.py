import discord
from discord.ext import commands
from discord.ui import Button, View
import os
import asyncio
import urllib.parse
import Configuraciones as cnf # type: ignore

intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True
intents.guilds = True
client = commands.Bot(command_prefix='!', intents=intents)

# Variable para almacenar el cliente de voz actual
voice_client = None

# Comando para mostrar un menú con botones de audio
@client.command(name='menu', help='Mostrar un menú con botones de audio')
async def mostrar_menu(ctx):
    print("Menú de sonidos")
    guild_id = ctx.guild.id
    directorio = await cnf.obtener_directorio_sonidos(guild_id)
    audios = await cnf.cargar_lista_de_audios(directorio)
    if not audios:
        await ctx.send("No hay sonidos agregados")
        return

    botones = [Button(label=urllib.parse.unquote(audio.replace('.mp3', '')), custom_id=f'play_sound_{audio}') for audio in audios]
    
    # Dividir los botones en páginas
    for i in range(0, len(botones), cnf.MAX_Botones):
        botones_pagina = botones[i:i + cnf.MAX_Botones]
        vista = View()
        for boton in botones_pagina:
            vista.add_item(boton)
        await ctx.send('Selecciona un audio:', view=vista, delete_after=60)

# Función para reproducir el audio seleccionado
async def reproducir_audio():
    global voice_client
    while True:
        audio_file = await cnf.sound_queue.get()  # Obtener el siguiente archivo de audio en la cola
        if not voice_client or not voice_client.is_connected():
            canal = discord.utils.get(client.get_all_channels(), id=audio_file['channel_id'])
            if canal:
                voice_client = await canal.connect()
        audio_source = discord.FFmpegPCMAudio(executable=cnf.Dir_FFMPEG, source=audio_file['path'])
        voice_client.play(audio_source)

        while voice_client.is_playing():
            await asyncio.sleep(1)

        # Desconectar después de terminar la reproducción
        if not cnf.sound_queue.qsize():
            await voice_client.disconnect()

# Comando para limpiar los mensajes del bot y comandos relacionados
@client.command(name='limpiar', help='Eliminar todos los mensajes del bot y comandos relacionados en el canal actual')
@commands.has_permissions(manage_messages=True)
async def limpiar_mensajes(ctx):
    # Verificar si el bot tiene permisos para gestionar mensajes
    if not ctx.channel.permissions_for(ctx.guild.me).manage_messages:
        await ctx.send("No tengo permiso para gestionar mensajes en este canal.")
        return
    
    # Obtener los mensajes en el canal
    mensajes = [msg async for msg in ctx.channel.history(limit=100)]
    
    # Filtrar los mensajes del bot y comandos relacionados
    mensajes_bot = [msg for msg in mensajes if msg.author == client.user or msg.content.startswith('!')]

    # Eliminar los mensajes del bot y comandos relacionados
    for mensaje in mensajes_bot:
        await mensaje.delete()
    
    # Confirmar la eliminación
    confirmacion = await ctx.send("Se han eliminado todos los mensajes del bot y comandos relacionados.", delete_after=5)

# Comando para agregar un nuevo audio
@client.command(name='agregar', help='Agregar un nuevo audio')
async def agregar_audio(ctx, *, audio_name):
    print("Agregar audio")
    if len(ctx.message.attachments) == 0:
        await ctx.send("Por favor adjunta un archivo de audio.")
        return
    attachment = ctx.message.attachments[0]

    if attachment.size == 0:
        await ctx.send('El archivo adjuntado está vacío.')
        return
    
    guild_id = ctx.guild.id
    directorio = await cnf.obtener_directorio_sonidos(guild_id)
    if(await cnf.ValidarArchivo(attachment)):
        await ctx.send('El archivo adjuntado no es un archivo .mp3 o sobrepasa los 15 segundos')
        return
    
    encoded_name = urllib.parse.quote(audio_name)
    await attachment.save(f'{directorio}/{encoded_name}.mp3')
    await ctx.send(f'Se ha agregado el audio "{audio_name}" correctamente')

# Comando para borrar un audio existente
@client.command(name='borrar', help='Eliminar un audio existente')
async def borrar_audio(ctx, *, audio_name):
    print("Eliminar audio")
    guild_id = ctx.guild.id
    directorio = await cnf.obtener_directorio_sonidos(guild_id)
    try:
        encoded_name = urllib.parse.quote(audio_name)
        os.remove(f'{directorio}/{encoded_name}.mp3')
        await ctx.send(f'Se ha eliminado el audio "{audio_name}" correctamente')
    except FileNotFoundError:
        await ctx.send(f'No se encontró el audio "{audio_name}"')

@client.command(name="info",help="Te da info de como descargar y editar un audio")
async def informacion(ctx):
    descarga = "https://y2meta.app/es36/youtube-to-mp3"
    edicion = "https://mp3cutter.app/es"
    await ctx.send(f"Para descargar los audios en .mp3 usar:\nDescarga: {descarga}\nEdicion: {edicion}")

@client.event
async def on_ready():
    print(f'Conectado como {client.user.name}')
    client.loop.create_task(reproducir_audio())

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