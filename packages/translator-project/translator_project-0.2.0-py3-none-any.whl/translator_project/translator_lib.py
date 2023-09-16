from deep_translator import GoogleTranslator


def translate(source_lang: str, target_lang: str, text: str) -> str:
    """
    Translates given text using Google Translator.

    Pass the languages by the name or by abbreviation, eg. 'english' or 'en'.
    Pass 'auto' for automatic detection of source language.
    """
    try:
        if len(text) < 5000:
            translation = GoogleTranslator(
                source=source_lang, target=target_lang
            ).translate(text=text)
        else:
            translation = ""
            for chunk in [text[x : x + 4999] for x in range(0, len(text), 4999)]:
                translation += (
                    GoogleTranslator(source=source_lang, target=target_lang).translate(
                        text=chunk
                    )
                    + " "
                )
    except Exception as e:
        translation = "Error during translation"

    return translation
