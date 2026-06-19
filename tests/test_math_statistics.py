import unittest
try:
    from games.libraries.math import statistics
except Exception:
    from libraries.math import statistics

class TestGroupedStatistics(unittest.TestCase):
    def test_mean_group(self):
        # lower_bound=0, class_width=10, freqs for classes: 1,2,3 -> midpoints: 5,15,25
        result = statistics.mean_group(0, 10, [1,2,3])
        expected = ((5*1)+(15*2)+(25*3)) / 6
        self.assertAlmostEqual(result, expected)

    def test_mode_group_interpolated(self):
        # mode class is index 2 (freq 5), neighbors 3 and 2
        f = [1,3,5,2]
        mode = statistics.mode_group(0, 10, f)
        # compute expected via formula: L + ((fm - f1)/(2fm - f1 - f2)) * h
        fm = 5
        f1 = 3
        f2 = 2
        expected = 0 + ((fm - f1) / (2*fm - f1 - f2)) * 10
        self.assertAlmostEqual(mode, expected)

if __name__ == '__main__':
    unittest.main()
