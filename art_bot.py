import asyncio
import random
import urllib.parse
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile

# --- КОНФИГУРАЦИЯ ---
TOKEN = "8761763990:AAG9Fs3Umzzqt9zMwSZAbqIaGt8ZTMeMu8M"
# ---------------------

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "👁 **Визуализатор реальности запущен.**\n\n"
        "Пиши `/gen` и свой запрос, чтобы получить файл.\n"
        "👉 *Пример: /gen неоновый лев*"
    )

@dp.message(Command("gen"))
async def generate_img(message: types.Message):
    # Извлекаем текст запроса
    prompt = message.text.replace("/gen", "").strip()
    
    if not prompt:
        await message.reply("💀 Напиши запрос после команды!")
        return

    wait_msg = await message.answer("🔮 Материализую пиксели... Жди.")

    # --- ИСПРАВЛЕННЫЙ БЛОК ССЫЛКИ ---
    # Добавляем /prompt/ и следим за слэшами, чтобы ничего не склеилось
    base_url = "https://pollinations.ai"
    safe_prompt = urllib.parse.quote(prompt)
    seed = random.randint(1, 9999999)
    
    # Теперь ссылка будет: https://pollinations.aiяблоко...
    image_url = f"{base_url}{safe_prompt}?seed={seed}&width=1024&height=1024&nologo=true"
    # --------------------------------

    file_path = f"art_{message.from_user.id}.jpg"

    try:
        # Скачиваем файл (ждем до 60 секунд)
        response = requests.get(image_url, timeout=60)
        
        if response.status_code == 200:
            # Сохраняем на диск
            with open(file_path, "wb") as f:
                f.write(response.content)
            
            # Отправляем фото как файл
            photo = FSInputFile(file_path)
            await message.answer_photo(
                photo=photo, 
                caption=f"🔥 **Материя сформирована:** \n_{prompt}_",
                parse_mode="Markdown"
            )
            await wait_msg.delete()
            
            # Удаляем временный файл
            if os.path.exists(file_path):
                os.remove(file_path)
        else:
            await wait_msg.edit_text(f"🛑 Нейросеть занята (Ошибка {response.status_code}). Попробуй позже.")
            
    except Exception as e:
        await wait_msg.edit_text(f"💥 Ошибка: {str(e)}")
        if os.path.exists(file_path):
            os.remove(file_path)

async def main():
    print("🚀 Бот-художник запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
