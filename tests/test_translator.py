import unittest

try:
    from games.libraries import morse, translator
except Exception:
    from libraries import morse, translator


class TestMorse(unittest.TestCase):
    def test_encode_decode(self):
        s = 'SOS 123'
        encoded = morse.encode(s)
        self.assertIn('...', encoded)
        decoded = morse.decode(encoded.replace('/', ' / '))
        # digits and letters should round-trip or produce '?' for unknowns
        self.assertTrue('SOS' in decoded or 'S' in decoded)


class TestTranslator(unittest.TestCase):
    def test_morse_translate(self):
        out = translator.translate_to_script('morse', 'abc')
        self.assertIsInstance(out, str)

    def test_aksara_placeholder(self):
        # existing placeholder modules should be discoverable
        for name in ('minang', 'malay', 'batak', 'bugis'):
            out = translator.translate_to_script(name, 'rumah')
            self.assertIsInstance(out, str)


if __name__ == '__main__':
    unittest.main()
