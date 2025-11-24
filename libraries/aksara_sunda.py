# Konsonan dasar (vokal 'a' otomatis melekat)
consonants = {
  "k": "ᮊ", "g": "ᮌ", "ng": "ᮍ",
  "c": "ᮎ", "j": "ᮏ", "ny": "ᮑ",
  "t": "ᮒ", "d": "ᮓ", "n": "ᮔ",
  "p": "ᮕ", "b": "ᮘ", "m": "ᮙ",
  "y": "ᮚ", "r": "ᮛ", "l": "ᮜ",
  "w": "ᮝ", "s": "ᮞ", "h": "ᮠ",
  "v": "ᮗ", "z": "ᮐ", "x": "ᮟ",
  "f": "ᮖ"
}

# Vokal mandiri (awal kata / tanpa konsonan)
independent_vowels = {
  "a": "ᮃ", "i": "ᮄ", "u": "ᮅ",
  "é": "ᮆ", "e": "ᮇ", "o": "ᮈ"
}

# Sandhangan vokal (melekat pada konsonan)
vowel_signs = {
  "i": "ᮤ", "u": "ᮥ", "é": "ᮦ",
  "o": "ᮧ", "e": "ᮨ"
}

# Pamaéh (virama)
virama = "᮪"

# Pre-compute consonant keys sorted by length (longest first) to match digraphs like "ng","ny"
_CONS_KEYS = sorted(consonants.keys(), key=lambda k: -len(k))
_VOWELS = set(list(independent_vowels.keys()))

def to_aksara_sunda(text):
  if text is None:
    return {'status': 400, 'message': 'No text provided', 'data': {}}

  result = ""
  # split by spaces but preserve multiple spaces by iterating words and adding single space back
  words = text.lower().split(" ")
  for w_idx, word in enumerate(words):
    if word == "":
      result += " "
      continue

    i = 0
    while i < len(word):
      ch = word[i]

      # preserve non-alpha characters
      if not ch.isalpha():
        result += ch
        i += 1
        continue

      # Try to match consonant (prefer digraphs)
      match_key = None
      for k in _CONS_KEYS:
        if word.startswith(k, i):
          match_key = k
          break

      if match_key:
        cons_sym = consonants[match_key]
        i += len(match_key)

        # peek next char
        next_char = word[i] if i < len(word) else ""

        # if next is vowel
        if next_char in _VOWELS:
          if next_char == 'a':
            # inherent 'a' - no vowel sign, keep consonant as-is
            result += cons_sym
          else:
            # attach vowel sign
            sign = vowel_signs.get(next_char, "")
            result += cons_sym + sign
          i += 1  # consume vowel
          continue

        # next is consonant or end or non-letter -> add virama to suppress inherent 'a'
        result += cons_sym + virama
        continue

      # Not a consonant digraph/key -> maybe independent vowel
      if ch in independent_vowels:
        result += independent_vowels[ch]
        i += 1
        continue

      # fallback: copy character
      result += ch
      i += 1

    # add space between words (preserve original single space)
    if w_idx < len(words) - 1:
      result += " "

  return {
    "status": 200,
    "message": "",
    "data": {
      "result": result.strip()
    }
  }