def flatten_list(x):
    """If LLM returns nested lists, flatten them."""
    if isinstance(x, list):
        flat = []
        for item in x:
            if isinstance(item, list):
                flat.extend(item)
            else:
                flat.append(item)
        return flat
    return x
