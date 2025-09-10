# A dictionary mapping Latin characters to Aksara Sunda Unicode characters.
# This is a simplified mapping for demonstration.
aksara_map = {
  'a': 'ᮃ', 'i': 'ᮄ', 'u': 'ᮅ', 'e': ' 0', 'o': 'ᮇ',
  'ka': 'ᮊ', 'ga': 'ᮌ', 'cha': 'ᮎ', 'ja': 'ᮏ',
  'pa': 'ᮕ', 'ba': 'ᮘ', 'ma': 'ᮙ',
  'ta': 'ᮒ', 'da': 'ᮓ', 'na': 'ᮔ',
  'sa': 'ᮞ', 'wa': 'ᮯ', 'la': 'ᮜ',
  'ya': 'ᮚ', 'ra': 'ᮛ',
  # Panyang: r-final
  'r': 'ᮁ',
  # Panéléng: é
  'é': 'ᮦ',
  # Pamepet: e
  'e': 'ᮧ',
  # Panolong: o
  'o': 'ᮩ',
  # Panyakra: ra
  'ra': 'ᮢ',
  # Panyiku: ya
  'ya': '᮳',
  # Pamaeh: silent vowel
  'ᮊ': 'ᮊ᮪' # Example: to handle final consonants, like 'k'
}

def to_aksara_sunda(text):
  result = ''
  i = 0
  while i < len(text):
    # Check for two-character mappings first (like 'ka', 'ga', etc.)
    if i + 1 < len(text) and text[i:i+2] in aksara_map:
      result += aksara_map[text[i:i+2]]
      i += 2
    elif text[i] in aksara_map:
      result += aksara_map[text[i]]
      i += 1
    else:
      result += text[i]  # If no mapping, keep the original character
      i += 1
  return {
    'status': 200,
    'message': '',
    'data': {
      'result': result
    }
  }