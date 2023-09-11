def clean_file_extension(extension: str) -> str:
    """Cleans an extension file, removing all characters before the '.' and making them lowercase
    Example: '*.PY' -> '.py'

    It adds the '.' in case it's not present
    """

    dot_index = extension.find(".")

    if dot_index == -1:
        clean_extension = "." + extension
    else:
        clean_extension = extension[dot_index:]

    return clean_extension.lower()
