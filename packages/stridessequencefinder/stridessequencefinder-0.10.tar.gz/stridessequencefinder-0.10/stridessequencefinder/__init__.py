import numexpr
import numpy as np

def rolling_window(a, window):
    """
    Generate a rolling window view of a 1-dimensional NumPy array.

    Parameters:
    a (numpy.ndarray): The input array.
    window (int): The size of the rolling window.

    Returns:
    numpy.ndarray: A view of the input array with shape (N - window + 1, window), where N is the size of the input array.

    Example:
    >>> a = np.array([1, 2, 3, 4, 5])
    >>> windowed = rolling_window(a, 3)
    >>> print(windowed)
    array([[1, 2, 3],
           [2, 3, 4],
           [3, 4, 5]])
    """

    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)


def circular_rolling_window(a, window):
    """
    Generate a circular rolling window view of a 1-dimensional NumPy array.

    Parameters:
    a (numpy.ndarray): The input array.
    window (int): The size of the circular rolling window.

    Returns:
    numpy.ndarray: A view of the input array with shape (N, window), where N is the size of the input array, and the window wraps around at the boundaries.

    Example:
    >>> a = np.array([1, 2, 3, 4, 5])
    >>> circular_windowed = circular_rolling_window(a, 3)
    >>> print(circular_windowed)
    array([[1, 2, 3],
           [2, 3, 4],
           [3, 4, 5],
           [4, 5, 1],
           [5, 1, 2]])
    """

    pseudocircular = np.pad(a, pad_width=(0, window - 1), mode="wrap")
    return rolling_window(pseudocircular, window)


def find_sequence_in_array(sequence, array, numexpr_enabled=True):
    """
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
    """

    a3 = circular_rolling_window(array, len(sequence))
    if numexpr_enabled:
        isseq = numexpr.evaluate(
            "a3==sequence", global_dict={}, local_dict={"a3": a3, "sequence": sequence}
        )
        su1 = numexpr.evaluate(
            "sum(isseq,1)", global_dict={}, local_dict={"isseq": isseq.astype(np.int8)}
        )
        wherelen = numexpr.evaluate(
            "(su1==l)", global_dict={}, local_dict={"su1": su1, "l": len(sequence)}
        )
    else:
        isseq = a3 == sequence
        su1 = np.sum(isseq, axis=1)
        wherelen = su1 == len(sequence)

    resu = np.nonzero(wherelen)
    return resu[0]
