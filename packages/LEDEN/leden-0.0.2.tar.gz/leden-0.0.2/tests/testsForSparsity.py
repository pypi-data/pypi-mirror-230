import unittest
import numpy as np
import sys
import os

# Add the src directory to the PYTHONPATH so the packages can be found.
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from packages.sparsity import Sparsity


class TestSparsityCalculator(unittest.TestCase):

    def test_default_init(self):
        calc = Sparsity()
        self.assertEqual(calc._weight_threshold, 0.01)
        self.assertEqual(calc._normalize, True)

    def test_normalize_exp(self):
        calc = Sparsity()
        result = calc._normalize_exp(np.array([2, 2, 2, 2]))
        expected = np.array([0.25, 0.25, 0.25, 0.25])
        np.testing.assert_array_almost_equal(result, expected)

    def test_normalize_exp_zero_sum(self):
        calc = Sparsity()
        with self.assertRaises(ZeroDivisionError):
            calc._normalize_exp(np.array([0, 0, 0, 0]))

    def test_compute_sparsity(self):
        calc = Sparsity()
        sparsity = calc.compute([2, 0.005, -0.2, 0.5])
        self.assertEqual(sparsity, 3)  # Because only one value is below the threshold (0.005).

    def test_compute_sparsity_normalized(self):
        calc = Sparsity(normalize=True)
        sparsity = calc.compute([2, 0.005, -0.2, 0.5])
        self.assertEqual(sparsity, 3)  # After normalization, three values exceed 0.01.


    def test_compute_sparsity_non_list_input(self):
        calc = Sparsity()
        with self.assertRaises(TypeError):
            calc.compute("Not a list or numpy array")

    def test_compute_sparsity_non_normalize(self):
        calc = Sparsity(normalize=False)
        sparsity = calc.compute([0.02, 0.005, 0.02, 0.015])
        self.assertEqual(sparsity, 3)  # Three values are above the threshold.

if __name__ == '__main__':
    unittest.main()
