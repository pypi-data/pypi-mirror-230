import logging
from codecs import BOM_UTF8, BOM_UTF16, BOM_UTF16_BE, BOM_UTF16_LE, BOM_UTF32, BOM_UTF32_BE, BOM_UTF32_LE
from pathlib import Path

try:
    import chardet
except ImportError:
    chardet = None

logger = logging.getLogger(__name__)


def detect_encoding(file: str | Path) -> str | None:
    """Detects the encoding of a file by reading the first bytes

    Parameters
    ----------
    file : str | Path
        file to be checked

    Returns
    -------
    encoding : str | None
        encoding of the file (None if file is not found)
    """

    codecs = {
        BOM_UTF8: "utf_8_sig",
        BOM_UTF16: "utf_16",
        BOM_UTF16_BE: "utf_16_be",
        BOM_UTF16_LE: "utf_16_le",
        BOM_UTF32: "utf_32",
        BOM_UTF32_BE: "utf_32_be",
        BOM_UTF32_LE: "utf_32_le",
    }
    file = Path(file) if isinstance(file, str) else file
    try:
        with Path.open(file, "rb") as f:
            # Reads the first 5 bytes
            beginning = f.read(5)

            if beginning[0:2] in codecs:
                encoding = codecs[beginning[0:2]]
            elif beginning[0:3] in codecs:
                encoding = codecs[beginning[0:3]]
            elif beginning[0:4] in codecs:
                encoding = codecs[beginning[0:4]]
            elif beginning[0:5] in codecs:
                encoding = codecs[beginning[0:5]]
            else:
                encoding = "utf-8"
            return encoding
    except FileNotFoundError as err:
        logger.warning(f"Error {err} loading file: {file}")
        return None


def detect_encoding_chardet(file: str | Path) -> str | None:
    """Detects the encoding of the file using the chardet library. This library uses
    heuristics to make an educated guess about the encoding of a file. However, this
    method is not always accurate and may be slow for large files.
    Use in cases where `detect_encoding` fails."""
    file = Path(file) if isinstance(file, str) else file
    try:
        with Path.open(file, "rb") as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result["encoding"]
            return encoding
    except AttributeError:
        logger.warning("Install package 'chardet' for additional encoding detection.")
        return None
    except FileNotFoundError as err:
        logger.warning(f"Error {err} loading file: {file}")
        return None
