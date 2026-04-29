import asyncio
import re
from pathlib import Path

import edge_tts


class ChunkSplitter:
    RETRIES = 3
    MAX_CHUNK_LEN = 3000

    @staticmethod
    def split_text(text: str, max_length: int = MAX_CHUNK_LEN) -> list[str]:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        chunks: list[str] = []
        current = ""

        for sentence in sentences:
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

    @staticmethod
    async def generate_chunk(
            chunk: str,
            index: int,
            voice: str,
            out_dir: Path,
            retries: int = RETRIES,
    ) -> None:

        path = out_dir / f"part_{index:04d}.mp3"

        if path.exists():
            print(f"[~] Чанк {index:04d} — пропускаем")
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

        raise RuntimeError(
            f"Чанк {index:04d} не удалось сгенерировать после {retries} попыток."
        )
