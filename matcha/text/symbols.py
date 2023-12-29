""" from https://github.com/keithito/tacotron

Defines the set of symbols used in text input to the model.
"""
# _pad = "_"
# _punctuation = ';:,.!?¡¿—…"«»“” '
_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнңоөпрстуүфхцчшщьыъэюя"
_letters_ipa = (
    "ɑɐɒæɓʙβɔɕçɗɖðʤəɘɚɛɜɝɞɟʄɡɠɢʛɦɧħɥʜɨɪʝɭɬɫɮʟɱɯɰŋɳɲɴøɵɸθœɶʘɹɺɾɻʀʁɽʂʃʈʧʉʊʋⱱʌɣɤʍχʎʏʑʐʒʔʡʕʢǀǁǂǃˈˌːˑʼʴʰʱʲʷˠˤ˞↓↑→↗↘'̩'ᵻ"
)

_pad = '_'
_punctuation = ';:,.!?¡¿—…"«»“” '
_special = '-'

# _letters = 'абвгдеёжзийклмнңоөпрстуүфхцчшщьыъэюяe'

# Export all symbols:
symbols = [_pad] + list(_punctuation) + list(_letters) + list(_letters_ipa)
# symbols = [_pad] + list(_special) + list(_punctuation) + list(_letters)

# Special symbol ids
SPACE_ID = symbols.index(" ")
