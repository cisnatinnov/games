# Konsonan dasar (vokal 'a' otomatis melekat)
consonants = {
  "k": "ᮊ", "g": "ᮌ", "ng": "ᮍ", 
  "c": "ᮎ", "j": "ᮏ", "ny": "ᮑ",
  "t": "ᮒ", "d": "ᮓ", "n": "ᮔ", 
  "p": "ᮕ", "b": "ᮘ", "m": "ᮙ", 
  "y": "ᮚ", "r": "ᮛ", "l": "ᮜ", 
  "w": "ᮝ", "s": "ᮞ", "h": "ᮠ"
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

# Pamaéh
virama = "᮪"

def to_aksara_sunda(text):
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
      if i < len(word):        
        if word[i] in vowel_signs:
          cons += vowel_signs[word[i]]
        else:
          cons += ""
  
        i += 1
        vowel_added = True
        
      if not vowel_added and (i < len(word) and word[i] not in independent_vowels and word[i] not in consonants):
        cons += virama
      if not vowel_added:
        cons += virama

      result += cons

    result += " "
  return {
    "status": 200,
    "message": "",
    "data": {
      "result": result.strip()
    }
  }