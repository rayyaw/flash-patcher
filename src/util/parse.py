def strip_line(line:str) -> str:
    """
    Strip leading and trailing characters from a line.
    Having this as a single function allows us to edit this more easily.
    """
    return line.strip("\n\r ")