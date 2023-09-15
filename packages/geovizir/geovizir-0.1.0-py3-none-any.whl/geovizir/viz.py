def label_bins(bins: list[int, float]) -> list[str]:
    """Return a list of labels for a list of bins.
    
    For each element of the bins, an interval is created with 
    the previous element. The first element is add as '< first_element'
    and the last element as '> last_element'.

    Parameters
    ----------
    bins : list[float, int]
        A list of bins to be labeled.

    Returns
    -------
    list[str]
        A list of labels.

    Examples
    --------
    >>> bins([1,2,3])    
    """
    return [f'< {bins[0]}', *(f'{a}-{b}' for a, b in zip(bins[:-1], bins[1:])), f'> {bins[-1]}']
    