"""The Jupyter Environments Server application."""

import os

from traitlets import Unicode

from jupyter_server.utils import url_path_join
from jupyter_server.extension.application import ExtensionApp, ExtensionAppJinjaMixin

from ._version import __version__

from .handlers.index.handler import IndexHandler
from .handlers.config.handler import ConfigHandler
from .handlers.echo.handler import WsEchoHandler
from .handlers.relay.handler import WsRelayHandler
from .handlers.proxy.handler import WsProxyHandler
from .handlers.ping.handler import WsPingHandler


DEFAULT_STATIC_FILES_PATH = os.path.join(os.path.dirname(__file__), "./static")

DEFAULT_TEMPLATE_FILES_PATH = os.path.join(os.path.dirname(__file__), "./templates")


class JupyterEnvironmentsExtensionApp(ExtensionAppJinjaMixin, ExtensionApp):
    """The Jupyter Environments Server extension."""

    name = "jupyter_environments"

    extension_url = "/jupyter_environments"

    load_other_extensions = True

    static_paths = [DEFAULT_STATIC_FILES_PATH]
    template_paths = [DEFAULT_TEMPLATE_FILES_PATH]

    config_a = Unicode("", config=True, help="Config A example.")
    config_b = Unicode("", config=True, help="Config B example.")
    config_c = Unicode("", config=True, help="Config C example.")

    def initialize_settings(self):
        self.log.debug("Jupyter Environments Config {}".format(self.config))

    def initialize_templates(self):
        """
        from jinja2 import Environment, PackageLoader, FileSystemLoader, meta
        env = Environment(loader = FileSystemLoader(self.template_paths))
        template_settings = {f'{self.name}_jinja2_env': env}
        self.settings.update(**template_settings)
        env = Environment(loader=PackageLoader('jupyter_environments', 'templates'))
        template_source = env.loader.get_source(env, 'index.html')
        parsed_content = env.parse(template_source)
        variables = meta.find_undeclared_variables(parsed_content)
        ref_templates = meta.find_referenced_templates(parsed_content)
        """
        self.serverapp.jinja_template_vars.update({"jupyter_environments_version" : __version__})

    def initialize_handlers(self):
        self.log.debug("Jupyter Environments Jinja2 Env {}".format(self.settings['jupyter_environments_jinja2_env']))
#        host_pattern = ".*$"
#        base_url = web_app.settings["base_url"]
#        route_pattern = url_path_join(base_url, "jupyter_environments", "get_example")
#        echo_pattern = url_path_join(base_url, "jupyter_environments", "echo")
#        handlers = [
#            (route_pattern, JupyterExecHandler),
#            (echo_pattern, WsEchoHandler),
#        ]
        handlers = [
            ("jupyter_environments", IndexHandler),
            (url_path_join("jupyter_environments", "config"), ConfigHandler),
            (url_path_join("jupyter_environments", "echo"), WsEchoHandler),
            (url_path_join("jupyter_environments", "relay"), WsRelayHandler),
            (url_path_join("jupyter_environments", "proxy"), WsProxyHandler),
            (url_path_join("jupyter_environments", "ping"), WsPingHandler),
        ]
        self.handlers.extend(handlers)


# -----------------------------------------------------------------------------
# Main entry point
# -----------------------------------------------------------------------------

main = launch_new_instance = JupyterEnvironmentsExtensionApp.launch_instance
