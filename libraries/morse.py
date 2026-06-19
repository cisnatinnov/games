"""Simple Morse code encoder/decoder."""
MORSE_CODE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
    'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.'
}
REVERSE_MORSE = {v: k for k, v in MORSE_CODE.items()}


def encode(text: str) -> str:
    """Encode ASCII text to morse (uppercase letters/digits)."""
    out = []
    for ch in text.upper():
        if ch == ' ':
            out.append('/')
        else:
            out.append(MORSE_CODE.get(ch, '?'))
    return ' '.join(out)


def decode(code: str) -> str:
    """Decode morse string to ASCII. Words separated by '/'."""
    words = []
    for word in code.split(' / '):
        chars = []
        for token in word.split():
            chars.append(REVERSE_MORSE.get(token, '?'))
        words.append(''.join(chars))
    return ' '.join(words)
