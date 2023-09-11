import logging
import re
from functools import partial
from pathlib import Path

import yaml
from yaml.parser import ParserError

logger = logging.getLogger(__name__)


def _loader_scientific_notation():
    """Returns a yaml loader that can parse numbers in scientific notation as numbers
    instead of string. This is because library 'pyyaml' uses YAML 1.1 spec instead of
    YAML 1.2 spec. See:
    https://github.com/yaml/pyyaml/issues/173
    https://stackoverflow.com/a/30462009
    """
    loader = yaml.FullLoader
    loader.add_implicit_resolver(
        "tag:yaml.org,2002:float",
        re.compile(
            """^(?:
     [-+]?(?:[0-9][0-9_]*)\\.[0-9_]*(?:[eE][-+]?[0-9]+)?
    |[-+]?(?:[0-9][0-9_]*)(?:[eE][-+]?[0-9]+)
    |\\.[0-9_]+(?:[eE][-+][0-9]+)?
    |[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\\.[0-9_]*
    |[-+]?\\.(?:inf|Inf|INF)
    |\\.(?:nan|NaN|NAN))$""",
            re.X,
        ),
        list("-+0123456789."),
    )
    return loader


def load_yaml(file: Path, safe_load: bool = False) -> dict:
    """Loads a yaml file and returns it as a dictionary.
    If file is not found, returns an empty dictionary.

    Parameters
    ----------
    file : Path
        file
    safe_load : bool
        use safe load for the yaml

    Returns
    -------
    dict
        dictionary with the the yaml contents
    """

    load = yaml.safe_load if safe_load else partial(yaml.load, Loader=_loader_scientific_notation())

    try:
        with Path.open(file) as f:
            conf = load(f)
            if conf is None:
                return {}
    except ParserError:
        logger.warning("Error loading the file '%s'", file)
        raise
    except FileNotFoundError:
        logger.warning("File '%s' was not found", file)
        raise

    return conf
