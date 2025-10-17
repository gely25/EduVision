from googletrans import Translator

translator = Translator()

def translate_word(label):
    try:
        result = translator.translate(label, src="en", dest="es")
        return result.text
    except Exception:
        return label
