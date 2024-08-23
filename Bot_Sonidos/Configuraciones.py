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