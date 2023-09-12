import os
import json
from pathlib import Path

from .handlers import setup_handlers


HERE = Path(__file__).parent.resolve()


def _jupyter_server_extension_points():
    return [{"module": "oceanumlab"}]


def _load_jupyter_server_extension(server_app):
    """Registers the API handler to receive HTTP requests from the frontend extension.
    Parameters
    ----------
    server_app: jupyterlab.labapp.LabApp
        JupyterLab application instance
    """
    url_path = "oceanum"
    setup_handlers(server_app.web_app, url_path)
    server_app.log.info(f"Registered oceanumlab extension at URL path /{url_path}")


# For backward compatibility with the classical notebook
load_jupyter_server_extension = _load_jupyter_server_extension
