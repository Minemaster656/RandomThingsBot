import hashlib
import os
import sqlite3
from gtts import gTTS
from pydub import AudioSegment

def md5(string: str) -> str:
    return hashlib.md5(string.encode()).hexdigest()
class TTS_phrase():
    def __init__(self, phrase, filename, path):
        self.phrase = phrase
        self.filename = filename
        self.path = path
class CachedTTS():
    DB_INIT_QUERIES = [
    # uniquie phrase TEXT, unique filename TEXT
    "CREATE TABLE IF NOT EXISTS phrases (phrase TEXT UNIQUE, filename TEXT UNIQUE)",
    ]
    def __init__(self, path_to_audio, sqlite3_db_path):
        #create folder if it doesn't exist
        if not os.path.exists(path_to_audio):
            os.makedirs(path_to_audio)
        self.path_to_audio = path_to_audio
        # create and init db if not exists, else - connect
        if not os.path.exists(sqlite3_db_path):
            try:
                os.makedirs(os.path.dirname(sqlite3_db_path))
            except:
                ...
            open(sqlite3_db_path, 'a').close()
            print("INIT DB")
        self.conn = sqlite3.connect(sqlite3_db_path)
        self.cur = self.conn.cursor()
        for q in self.DB_INIT_QUERIES:
            self.cur.execute(q)
    async def _AbstractTTS(self, phrase: str):
        '''PRIVATE METHOD FOR ABSTRACT TTS'''
        self.cur.execute("SELECT * FROM phrases WHERE phrase=?", (phrase,))
        data = self.cur.fetchone()

        if data:
            # print("Зачем РАБОТАТЬ если можно воспроизвести?")
            return TTS_phrase(phrase, data[1], self.path_to_audio)
        else:
            try:
                filename = md5(phrase)
                # print("GTTS INIT")
                # Используем gTTS для озвучивания фразы
                tts = gTTS(text=phrase, lang='ru')

                # print("MAKING PATH")
                # Генерируем уникальное имя файла для сохранения
                output_file = os.path.join(self.path_to_audio, f"{filename}.mp3")
                # print("SAVING")
                # sound = AudioSegment.from_file(tts)
                # sound.export(f"{filename}.mp3", format="mp3")
                # # Сохраняем озвученную фразу
                tts.save(output_file)
                # print("SAVING TO DB")
                # Сохраняем фразу в базе данных
                self.cur.execute("INSERT INTO phrases (phrase, filename) VALUES (?, ?)", (phrase, filename))
                self.conn.commit()
                return TTS_phrase(phrase, filename, self.path_to_audio)
                # print(f"Фраза озвучена и сохранена в базе данных. Путь к файлу: {output_file}")
            except Exception as e:
                print(e)
                return None


    async def tts(self, phrase: str):

        '''Put phrase to tts, returns TTS_phrase object or none if error'''
        phrase = phrase.lower()
        return await self._AbstractTTS(phrase)



