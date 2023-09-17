from typing import Any, Dict, List

from ._version import __version__
from .serverapplication import JupyterEnvironmentsExtensionApp


def _jupyter_server_extension_points() -> List[Dict[str, Any]]:
    return [{
        "module": "jupyter_environments",
        "app": JupyterEnvironmentsExtensionApp,
    }]


def _jupyter_labextension_paths() -> List[Dict[str, str]]:
    return [{
        "src": "labextension",
        "dest": "@datalayer/jupyter-environments"
    }]
