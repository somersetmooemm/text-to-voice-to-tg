import asyncio
import re
import subprocess
from pathlib import Path

import edge_tts

import cleaner_text
from paper import Paper

# ──────────────────────────────────────────────
# Настройки
# ──────────────────────────────────────────────
URL = "https://habr.com/p/599339/"
VOICE = "ru-RU-DmitryNeural"
BASE_DIR = Path("./result")
MAX_CHUNK_LEN = 3000
MAX_PARALLEL = 5
RETRIES = 3


# ──────────────────────────────────────────────
# 3. Разбивка на чанки по предложениям
# ──────────────────────────────────────────────
def split_text(text: str, max_length: int = MAX_CHUNK_LEN) -> list[str]:
    # Разбиваем по концу предложения (. ! ?)
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks: list[str] = []
    current = ""

    for sentence in sentences:
        # Если одно предложение длиннее лимита — режем жёстко
        if len(sentence) > max_length:
            if current:
                chunks.append(current.strip())
                current = ""
            for i in range(0, len(sentence), max_length):
                chunks.append(sentence[i: i + max_length].strip())
            continue

        if len(current) + len(sentence) + 1 <= max_length:
            current += sentence + " "
        else:
            if current:
                chunks.append(current.strip())
            current = sentence + " "

    if current.strip():
        chunks.append(current.strip())

    return chunks


# ──────────────────────────────────────────────
# 4. Генерация аудио (параллельно + retry + кеш)
# ──────────────────────────────────────────────
async def generate_chunk(
        chunk: str,
        index: int,
        voice: str,
        out_dir: Path,
        retries: int = RETRIES,
) -> None:
    path = out_dir / f"part_{index:04d}.mp3"

    if path.exists():
        print(f"[~] Чанк {index:04d} — пропускаем (уже существует)")
        return

    for attempt in range(1, retries + 1):
        try:
            communicate = edge_tts.Communicate(text=chunk, voice=voice)
            await communicate.save(str(path))
            print(f"[✓] Чанк {index:04d} сохранён")
            return
        except Exception as exc:
            print(f"[!] Чанк {index:04d}, попытка {attempt}/{retries}: {exc}")
            if attempt < retries:
                await asyncio.sleep(1.5 * attempt)

    raise RuntimeError(f"Чанк {index:04d} не удалось сгенерировать после {retries} попыток.")


async def generate_audio(chunks: list[str], voice: str = VOICE, out_dir: Path = BASE_DIR) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    semaphore = asyncio.Semaphore(MAX_PARALLEL)

    async def limited(i: int, chunk: str) -> None:
        async with semaphore:
            await generate_chunk(chunk, i, voice, out_dir)

    await asyncio.gather(*[limited(i, c) for i, c in enumerate(chunks)])


# ──────────────────────────────────────────────
# 5. Склейка через FFmpeg с нормализацией
# ──────────────────────────────────────────────
def merge_audio_ffmpeg(out_dir: Path = BASE_DIR) -> Path:
    parts = sorted(out_dir.glob("part_*.mp3"))
    if not parts:
        raise RuntimeError("Нет файлов для склейки.")

    list_path = out_dir / "list.txt"
    with open(list_path, "w", encoding="utf-8") as f:
        for p in parts:
            f.write(f"file '{p.resolve()}'\n")

    output_path = out_dir / "final.mp3"

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(list_path),
            "-af", "loudnorm,aresample=44100",
            "-ar", "44100",
            "-ab", "192k",
            str(output_path),
        ],
        check=True,
    )

    print(f"[✓] Финальный файл: {output_path}")
    return output_path


# ──────────────────────────────────────────────
# 6. Точка входа
# ──────────────────────────────────────────────
def main() -> None:
    paper = Paper(URL)
    paper.fetch_text()
    text_paper = cleaner_text.Cleaner_text.clean_text(paper.text)

    print("Разбиваем на чанки...")
    chunks = split_text(text_paper)
    print(f"  Всего чанков: {len(chunks)}")

    print("Генерируем аудио...")
    asyncio.run(generate_audio(chunks))

    print("Склеиваем аудио...")
    merge_audio_ffmpeg()


if __name__ == "__main__":
    main()
