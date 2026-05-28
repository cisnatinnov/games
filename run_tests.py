import unittest
import sys

loader = unittest.TestLoader()
tests = loader.discover('tests')
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(tests)
sys.exit(not result.wasSuccessful())
