""" from https://github.com/keithito/tacotron

Cleaners are transformations that run over the input text at both training and eval time.

Cleaners can be selected by passing a comma-delimited list of cleaner names as the "cleaners"
hyperparameter. Some cleaners are English-specific. You'll typically want to use:
  1. "english_cleaners" for English text
  2. "transliteration_cleaners" for non-English text that can be transliterated to ASCII using
     the Unidecode library (https://pypi.python.org/pypi/Unidecode)
  3. "basic_cleaners" if you do not want to transliterate (in this case, you should also update
     the symbols in symbols.py to match your data).
"""

import logging
import re

import phonemizer
from unidecode import unidecode
# To avoid excessive logging we set the log level of the phonemizer package to Critical
critical_logger = logging.getLogger("phonemizer")
critical_logger.setLevel(logging.CRITICAL)

# Intializing the phonemizer globally significantly reduces the speed
# now the phonemizer is not initialising at every call
# Might be less flexible, but it is much-much faster

global_phonemizer = phonemizer.backend.EspeakBackend(
    language="en-us",
    preserve_punctuation=True,
    with_stress=True,
    language_switch="remove-flags",
    logger=critical_logger,
)

kyrgyz_phonemizer = phonemizer.backend.EspeakBackend(
    language="ky",
    preserve_punctuation=True,
    with_stress=True,
    language_switch="remove-flags",
    logger=critical_logger,
)
# Regular expression matching whitespace:
_whitespace_re = re.compile(r"\s+")

# List of (regular expression, replacement) pairs for abbreviations:
# ("mrs", "misess"),
        # ("mr", "mister"),
        # ("dr", "doctor"),
        # ("st", "saint"),
        # ("co", "company"),
        # ("jr", "junior"),
        # ("maj", "major"),
        # ("gen", "general"),
        # ("drs", "doctors"),
        # ("rev", "reverend"),
        # ("lt", "lieutenant"),
        # ("hon", "honorable"),
        # ("sgt", "sergeant"),
        # ("capt", "captain"),
        # ("esq", "esquire"),
        # ("ltd", "limited"),
        # ("col", "colonel"),
        # ("ft", "fort"),
_abbreviations = [
    (re.compile(r"\b%s\b" % re.escape(x[0]), re.IGNORECASE), x[1])
    for x in [
        
        ("КТМУ", "Кыргыз-Түрк Манас университет"),
        ("КР", "Кыргыз Республикасы"),
        ("ж.б.", "жана башка"),
        ("ЖИ", "Жасалма интеллект"),
        ("БУУ", "Бириккен Улуттар Уюму"),
        ("КМШ", "Көз карандысыз мамлекеттердин шериктештиги"),
        ("ШКУ", "Шанхай кызматташтык уюму"),
        ("ЕККУ", "Европа коопсуздук жана кызматташуу уюму"),
        ("ЕБ", "Европалык Биримдик"),
        ("ЕАЭБ", "Евразия экономика биримдиги"),
        ("ЕККУ", "Европалык коопсуздук жана кызматташтык уюму"),
        ("СССР", "Советтик Социалисттик Республикалар Союзу"),
        ("ЭЭА", "Эркин экономикалык аймак"),
        ("UNICEF", "Бириккен улуттар уюмунун балдар фондусу"),
        ("USAID", "Америка кошмо штаттарынын эл аралык өнүктүрүү агенттиги"),
        ("ИДП", "Ички дүӊ продукциясы"),
        ("ЖЧК", "Жоопкерчилиги чектелген коом"),
        ("ААК", "Ачык акционердик коому"),
        ("БШК", "Борбордук шайлоо комиссиясы"),
        ("ЖМК", "Жалпыга маалымдоо каражаттары"),
        ("ЖАМК", "Жаза аткаруу мамлекеттик кызматы"),
        ("УКМК", "Улуттук коопсуздук мамлекеттик комитети"),
        ("ТИМ", "Тышкы иштер министрлиги"),
        ("ӨКМ", "Өзгөчө кырдаалдар министрлиги"),
        ("ИИМ", "Ички иштер министрлиги"),
        ("ОИИБ", "Облустук ички иштер башкармалыгы"),
        ("ШИИББ", "Шаардык ички иштер башкы башкармалыгы"),
        ("РИИБ", "Райондук ички иштер башкармалыгы"),
        ("ЧЧК", "Чоң Чүй каналы"),
        ("F", "эф"),
        ("KG", "Кейджи"),
    ]
]



def expand_abbreviations(text):
    for regex, replacement in _abbreviations:
        text = re.sub(regex, replacement, text)
    return text


def lowercase(text):
    return text.lower()


def collapse_whitespace(text):
    return re.sub(_whitespace_re, " ", text)


def convert_to_ascii(text):
    return unidecode(text)


def basic_cleaners(text):
    """Basic pipeline that lowercases and collapses whitespace without transliteration."""
    text = lowercase(text)
    text = collapse_whitespace(text)
    return text


def transliteration_cleaners(text):
    """Pipeline for non-English text that transliterates to ASCII."""
    text = convert_to_ascii(text)
    text = lowercase(text)
    text = collapse_whitespace(text)
    return text


def english_cleaners2(text):
    """Pipeline for English text, including abbreviation expansion. + punctuation + stress"""
    text = convert_to_ascii(text)
    text = lowercase(text)
    text = expand_abbreviations(text)
    phonemes = global_phonemizer.phonemize([text], strip=True, njobs=1)[0]
    phonemes = collapse_whitespace(phonemes)
    return phonemes

def kygryz_cleaners2(text):
    """Pipeline for English text, including abbreviation expansion. + punctuation + stress"""
    #print('Before: ', text)
    #text = convert_to_ascii(text)
    #print('After convert: ', text)
    text = expand_abbreviations(text)
    text = lowercase(text)
    #phonemes = kyrgyz_phonemizer.phonemize([text], strip=True, njobs=1)[0]
    phonemes = collapse_whitespace(text)
    return phonemes

