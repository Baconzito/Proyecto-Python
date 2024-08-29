import os
from pydub import AudioSegment
import asyncio
import openpyxl
from openpyxl import Workbook
from datetime import datetime

"""
    Configuraciones de Bot Sonidify
"""
Dir_Sonidos = "Sonidos"
Dir_Temp = "Sonidos/temp"
Dir_FFMPEG = "/usr/bin/ffmpeg"
token = os.getenv("BOT_TOKEN")

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
    

# Función para guardar la información en un archivo Excel
async def guardar_en_excel(nombre_sonido, guild_id):
    archivo_excel = "historial_bot.xlsx"

    # Verificar si el archivo ya existe
    if os.path.exists(archivo_excel):
        workbook = openpyxl.load_workbook(archivo_excel)
        hoja = workbook.active
    else:
        workbook = Workbook()
        hoja = workbook.active
        hoja.append(["Nombre del Sonido", "Fecha", "ID de Servidor"])

    # Agregar los datos
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hoja.append([nombre_sonido, fecha_actual, guild_id])

    # Guardar el archivo
    workbook.save(archivo_excel)