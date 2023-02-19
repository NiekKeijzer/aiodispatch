import importlib
import uuid
from typing import Any


def generate_uuid() -> str:
    return str(uuid.uuid4())


def load_attribute(import_string: str) -> Any:
    module_name, attr_name = import_string.rsplit(":", 1)
    module = importlib.import_module(module_name)

    try:
        return getattr(module, attr_name)
    except AttributeError as e:
        raise ImportError from e


def dump_attribute(attr: Any) -> str:
    return f"{attr.__module__}:{attr.__name__}"
