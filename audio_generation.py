import asyncio
import subprocess
from pathlib import Path

from chunk_splitter import ChunkSplitter


class AudioGeneration:
    VOICE = "ru-RU-DmitryNeural"
    BASE_DIR = Path("./result")

    @staticmethod
    async def generate_audio(chunks: list[str], voice: str = VOICE, out_dir: Path = BASE_DIR) -> None:
        out_dir.mkdir(parents=True, exist_ok=True)
        semaphore = asyncio.Semaphore(5)

        async def limited(i: int, chunk: str) -> None:
            async with semaphore:
                await ChunkSplitter.generate_chunk(chunk, i, voice, out_dir)

        await asyncio.gather(*[limited(i, c) for i, c in enumerate(chunks)])

    @staticmethod
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
