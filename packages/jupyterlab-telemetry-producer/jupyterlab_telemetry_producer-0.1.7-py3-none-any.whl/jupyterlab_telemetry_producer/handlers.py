from ._version import __version__
from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.extension.handler import ExtensionHandlerMixin
import os, json, tornado

class RouteHandler(ExtensionHandlerMixin, JupyterHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server
    @tornado.web.authenticated
    def get(self, resource):
        try:
            self.set_header('Content-Type', 'application/json') 
            if resource == 'version':
                self.finish(json.dumps(__version__))
            elif resource == 'environ':
                self.finish(json.dumps({k:v for k, v in os.environ.items()}))
            elif resource == 'config':
                self.finish(json.dumps(self.config))
            else:
                self.set_status(404)
        except Exception as e:
            self.log.error(str(e))
            self.set_status(500)
            self.finish(json.dumps(str(e)))