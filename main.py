import asyncio

import cleaner_text
from audio_generation import AudioGeneration
from chunk_splitter import ChunkSplitter
from paper import Paper


def main() -> None:
    paper = Paper("https://habr.com/p/599339/")
    paper.fetch_text()
    text_paper = cleaner_text.Cleaner_text.clean_text(paper.text)
    asyncio.run(AudioGeneration.generate_audio(ChunkSplitter.split_text(text_paper)))
    AudioGeneration.merge_audio_ffmpeg()


if __name__ == "__main__":
    main()
