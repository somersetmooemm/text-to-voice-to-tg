import asyncio
import edge_tts
import os

text = """
final в Java — это модификатор, который запрещает изменение.

Если final применяется к переменной, её значение можно присвоить только один раз.
Если к методу — его нельзя переопределить в дочерних классах.
Если к классу — от него нельзя наследоваться.

Для ссылочных типов final означает, что нельзя изменить саму ссылку,
но можно изменять содержимое объекта.

Таким образом, final используется для фиксации поведения и защиты от изменений.
"""

async def main():
    communicate = edge_tts.Communicate(
        text=text,
        voice="ru-RU-DmitryNeural",
        rate="+0%",     # скорость
        volume="+0%"    # громкость
    )
    await communicate.save("speech.mp3")

asyncio.run(main())

os.startfile("speech.mp3")