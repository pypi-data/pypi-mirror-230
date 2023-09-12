# finds sequences [3, 4, 5] in NumPy arrays [1, 2, 3, 4, 5, 1, 2, 3, 4, 5] - result: [2 7]

## Tested against Windows 10 / Python 3.10 / Anaconda

## pip install stridessequencefinder



```python

Find occurrences of a sequence in a 1-dimensional NumPy array using a rolling window approach.

Parameters:
sequence (numpy.ndarray): The sequence to search for.
array (numpy.ndarray): The input array to search within.
numexpr_enabled (bool, optional): Whether to use NumExpr for efficient computation (default is True).

Returns:
numpy.ndarray: An array of indices where the sequence is found in the input array.

Example:
>>> arr = np.array([1, 2, 3, 4, 5, 1, 2, 3, 4, 5])
>>> seq = np.array([3, 4, 5])
>>> indices = find_sequence_in_array(seq, arr)
>>> print(indices)
[2 7]

```