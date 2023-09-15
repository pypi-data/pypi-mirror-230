def trim_zeros_single_float(str_float):
    """
    Trims trailing zeros after a decimal point,
    leaving just one if necessary.
    """
    str_float = str_float.rstrip("0")
    if str_float.endswith("."):
        str_float += "0"

    return str_float
