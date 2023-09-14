def label_bins(bins):
    return [f'< {bins[0]}', *(f'{a}-{b}' for a, b in zip(bins[:-1], bins[1:])), f'> {bins[-1]}']