'''
NAME: Mihir Rao
DATE: 17th August, 2023
'''

import numpy as np

class Sparsity():
    """
    Class for calculating the sparsity of an explanation array based on a weight threshold.
    """

    def __init__(self, 
                 weight_threshold: float = 0.01, 
                 normalize: bool = True) -> None:
        """
        Constructor for SparsityCalculator class.
        
        Parameters:
        - weight_threshold: Threshold for considering a weight as significant.
        - normalize: Flag indicating if the explanation array should be normalized.
        """
        self._weight_threshold = weight_threshold
        self._normalize = normalize

    def _normalize_exp(self, exp: np.array) -> np.array:
        """
        Normalizes the explanation array to sum to 1.
        
        Parameters:
        - exp: Explanation array to normalize.
        
        Returns:
        - Normalized explanation array.
        """
        exp_sum = np.sum(exp)
        if exp_sum == 0:
            raise ZeroDivisionError('Explanation sum is 0. Cannot normalize.')
        return exp / exp_sum
    
    def compute(self, exp: np.array) -> int:
        """
        Computes the sparsity of the explanation.
        Definition: The number of weights in the explanation that are greater than the weight threshold.
        
        Parameters:
        - exp: Explanation array to compute sparsity for.
        
        Returns:
        - Sparsity of the explanation array.
        """
        try:
            exp = np.array(exp)
        except ValueError:
            raise TypeError('Explanation must be convertible to a numpy array.')

        exp = np.abs(exp)
        
        if self._normalize:
            exp = self._normalize_exp(exp)
        
        return np.sum(exp > self._weight_threshold)
