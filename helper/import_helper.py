import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).parent.parent


def load_module(name: str, *parts: str):
    if name in sys.modules:
        return sys.modules[name]

    path = ROOT.joinpath(*parts)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
