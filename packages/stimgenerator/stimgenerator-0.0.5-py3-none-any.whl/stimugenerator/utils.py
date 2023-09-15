def swap_dict(dictionary):
    swapped_dict = {}
    for key, value in dictionary.items():
        swapped_dict.setdefault(value, []).append(key)
    return swapped_dict
