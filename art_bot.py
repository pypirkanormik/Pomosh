import asyncio
import random
import urllib.parse
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile

# --- ТВОЙ ТОКЕН ---
TOKEN = "8761763990:AAG9Fs3Umzzqt9zMwSZAbqIaGt8ZTMeMu8M"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("gen"))
async def generate_img(message: types.Message):
    prompt = message.text.replace("/gen", "").strip()
    if not prompt:
        return await message.reply("💀 Напиши текст запроса!")

    wait_msg = await message.answer("🔮 Материализую пиксели... Подожди.")

    # КОДИРУЕМ ТЕКСТ
    safe_text = urllib.parse.quote(prompt)
    seed = random.randint(1, 9999999)
    
    # ЖЕСТКАЯ ССЫЛКА (слэши прописаны вручную, чтобы не склеилось)
    url = f"https://pollinations.ai{safe_text}?seed={seed}&nologo=true"
    
    # Имя файла для сохранения
    path = f"img_{message.from_user.id}.jpg"

    try:
        # Качаем файл через requests
        r = requests.get(url, timeout=60)
        if r.status_code == 200:
            with open(path, "wb") as f:
                f.write(r.content)
            
            # Отправляем фото
            await message.answer_photo(photo=FSInputFile(path), caption=f"🔥 Готово: {prompt}")
            await wait_msg.delete()
            
            # Удаляем мусор
            if os.path.exists(path):
                os.remove(path)
        else:
            await wait_msg.edit_text(f"🛑 Ошибка сервера: {r.status_code}")
    except Exception as e:
        # Если ты СНОВА видишь ошибку без слэша - значит хостинг НЕ ОБНОВИЛ ФАЙЛ
        await wait_msg.edit_text(f"💥 Ошибка: {str(e)}")
        if os.path.exists(path): os.remove(path)

async def main():
    print("🚀 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
