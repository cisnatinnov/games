import os
import unittest
import sys

# Default to mock provider for tests to avoid requiring real SDK keys
os.environ.setdefault('GENAI_PROVIDER', 'mock')

loader = unittest.TestLoader()
tests = loader.discover('tests')
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(tests)
sys.exit(not result.wasSuccessful())
