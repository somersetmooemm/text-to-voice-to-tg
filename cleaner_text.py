import re


class Cleaner_text:
    ABBREVIATIONS = {
        "т.е.": "то есть",
        "т.к.": "так как",
        "и т.д.": "и так далее",
        "и т.п.": "и тому подобное",
        "др.": "другие",
        "руб.": "рублей",
        "млн.": "миллионов",
        "млрд.": "миллиардов",
        "гг.": "годах",
        "г.": "года",
        "пр.": "прочее",
    }

    @staticmethod
    def clean_text(text: str) -> str:
        print("Очищаем текст...")
        # Убираем URL
        text = re.sub(r"https?://\S+", "", text)
        # Убираем markdown-разметку
        text = re.sub(r"[*_`#~>]", "", text)
        # Схлопываем множественные пустые строки
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Убираем строки только из цифр и спецсимволов (мусор после парсинга)
        text = re.sub(r"(?m)^[\d\W]+$", "", text)
        # Раскрываем сокращения

        for abbr, full in Cleaner_text.ABBREVIATIONS.items():
            text = text.replace(abbr, full)
            # Убираем лишние пробелы
            text = re.sub(r" {2,}", " ", text)
        return text.strip()
