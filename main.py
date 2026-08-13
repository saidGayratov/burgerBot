import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher

# Tokeningizni to'g'ridan-to'g'ri yozgan bo'lsangiz o'zingiznikini qoldiring, 
# yoki os.getenv("BOT_TOKEN") orqali oling
TOKEN = os.getenv("BOT_TOKEN") 

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Render port talabini qondirish uchun oddiy HTTP sahifa
async def handle(request):
    return web.Response(text="Burger Bot is running and healthy!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Render avtomatik taqdim etadigan PORT o'zgaruvchisini o'qiymiz
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"Web server successfully started on port {port}")

async def main():
    # 1. Avval Render talab qiladigan web serverni (portni) ishga tushiramiz
    await start_web_server()
    
    # 2. Keyin botning polling (xabarlarni qabul qilish) jarayonini boshlaymiz
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
