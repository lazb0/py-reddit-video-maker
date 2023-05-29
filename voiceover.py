from TTS.api import TTS


def create(fileName, postDir, text):
    filePath = f"{postDir}/voiceovers/{fileName}.mp3"
    tts = TTS('tts_models/en/vctk/vits')
    tts.tts_to_file(text, speaker="p234", file_path=filePath)
    return filePath
