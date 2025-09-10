# Konsonan dasar (vokal 'a' otomatis melekat)
consonants = {
  "h": "ꦲ", "n": "ꦤ", "c": "ꦕ", "r": "ꦫ",
  "k": "ꦏ", "d": "ꦢ", "t": "ꦠ", "s": "ꦱ",
  "w": "ꦮ", "l": "ꦭ", "p": "ꦥ", "dh": "ꦝ",
  "j": "ꦗ", "y": "ꦪ", "ny": "ꦚ", "m": "ꦩ",
  "g": "ꦒ", "b": "ꦧ", "th": "ꦛ", "ng": "ꦔ"
}

# Vokal mandiri (awal kata / tanpa konsonan)
independent_vowels = {
  "a": "ꦄ", "i": "ꦆ", "u": "ꦈ",
  "e": "ꦌ", "o": "ꦎ"
}

# Sandhangan vokal (melekat pada konsonan)
vowel_signs = {
  "i": "ꦶ", "u": "ꦸ", "e": "ꦺ", "o": "ꦺꦴ"
}

# Pamaéh
virama = "꧀"

def to_aksara_jawa(text):
  result = ""
  words = text.lower().split()
  for word in words:
    i = 0
    while i < len(word):
      # cek konsonan rangkap dulu
      if word[i:i+2] in consonants:
        cons = consonants[word[i:i+2]]
        i += 2
      elif word[i] in consonants:
        cons = consonants[word[i]]
        i += 1
      elif word[i] in independent_vowels:
        result += independent_vowels[word[i]]
        i += 1
        continue
      else:
        result += word[i]
        i += 1
        continue

      # default vokal "a"
      vowel_added = False
      if i < len(word) and word[i] in vowel_signs:
        cons += vowel_signs[word[i]]
        i += 1
        vowel_added = True

      result += cons

    # kalau setelah konsonan tidak ada vokal → tambahkan pamaéh
    if not vowel_added and (i < len(word) and word[i] not in independent_vowels and word[i] not in consonants):
      result += virama

    result += " "
  return {
    "status": 200,
    "message": "",
    "data": {
      "result": result.strip()
    }
  }