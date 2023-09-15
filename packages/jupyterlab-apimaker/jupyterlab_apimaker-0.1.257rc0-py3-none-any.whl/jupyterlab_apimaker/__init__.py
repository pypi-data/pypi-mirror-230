import json
from pathlib import Path
from jupyter_server.utils import url_path_join

# from .handlers import (ProcessNotebook, MakeAPI, APICollection)
from .handlers import (ProcessNotebook,
                       MakeAPI,
                       MasterTokensDBHander,
                       FunctionTokensListHandler,
                       TokenOperationsHandler,
                       GetJobStatus)
from .config import JupyterServerParameters

from ._version import __version__

HERE = Path(__file__).parent.resolve()
NAMESPACE = 'jupyterlab_apimaker'

with (HERE / "labextension" / "package.json").open() as fid:
    data = json.load(fid)


def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": data["name"]
    }]


def _jupyter_server_extension_points():
    return [{"module": NAMESPACE}]


def _load_jupyter_server_extension(app):
    app.web_app.settings[NAMESPACE] = JupyterServerParameters(parent=app)
    host_pattern = ".*$"

    base_url = app.web_app.settings["base_url"]
    process_notebook = url_path_join(base_url, NAMESPACE, "/process_notebook")
    make_api = url_path_join(base_url, NAMESPACE, "/make_api")
    api_catalog = url_path_join(base_url, NAMESPACE, "/api_catalog")
    master_token = url_path_join(base_url, NAMESPACE, "/tokens")
    function_tokens = url_path_join(base_url, NAMESPACE, "/tokens_container")
    tokens_operations = url_path_join(base_url, NAMESPACE, "/tokenops")
    job_status = url_path_join(base_url, NAMESPACE, "/get_job_status")
    handlers = [(process_notebook, ProcessNotebook),
                (make_api, MakeAPI),
                (master_token, MasterTokensDBHander),
                (function_tokens, FunctionTokensListHandler),
                (tokens_operations, TokenOperationsHandler),
                (job_status, GetJobStatus)
                ]
    app.web_app.add_handlers(host_pattern, handlers)
    app.log.info("Registered API Baker")


# For backward compatibility with notebook server - useful for Binder/JupyterHub
load_jupyter_server_extension = _load_jupyter_server_extension
