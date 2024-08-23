import os
from pydub import AudioSegment
import asyncio

"""
    Configuraciones de Bot Sonidify
"""
Dir_Sonidos = "C:/Users/Javier/Desktop/Bot_Sonidos/Sonidos"
Dir_Temp = "C:/Users/Javier/Desktop/Bot_Sonidos/Sonidos/temp"
Dir_FFMPEG = "C:/Users/Javier/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-7.0.1-essentials_build/bin/ffmpeg.exe"
token = "MTI2Mjg3MDE2NTIzODg0NTYxMw.GL7R0V.-6ynQHzLkJSOYIkUlhLn0-eqG_yXE4Zp5yQ948"


sound_queue = asyncio.Queue() #Cola de reproducicon
is_playing = {} #Sonidos en reproduccion

Max_Tamaño = 15
MAX_Botones = 25

async def obtener_directorio_sonidos(guild_id):
    directorio = f"{Dir_Sonidos}/{guild_id}"
    if not os.path.exists(directorio):
        os.makedirs(directorio)
    return directorio

async def cargar_lista_de_audios(directorio):
    return [archivo for archivo in os.listdir(directorio) if archivo.endswith('.mp3')]

async def ValidarArchivo(Archivo):
    if(not Archivo.filename.endswith('.mp3')):
        return True

    return await ValidarTiempo(Archivo)
    
async def ValidarTiempo(Archivo):
    temp_path = os.path.join(Dir_Temp,Archivo.filename)
    if not os.path.exists(Dir_Temp):
        os.makedirs(Dir_Temp)

    await Archivo.save(temp_path)
    try:
        AudioSegment.converter = Dir_FFMPEG
        audio = AudioSegment.from_file(temp_path)
        duracion = len(audio) / 1000
        return duracion > Max_Tamaño
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

# Función para agregar un audio a la cola
async def agregar_a_cola(interaction, audio_file):
    await sound_queue.put({
        'channel_id': interaction.user.voice.channel.id,
        'path': audio_file
    })