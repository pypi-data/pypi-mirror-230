from ._version import __version__

import sys
import warnings
from pathlib import Path

from traitlets import Bool, Unicode

from datalayer.application import DatalayerApp, NoStart, base_aliases, base_flags

HERE = Path(__file__).parent


jupyter_environments_aliases = dict(base_aliases)
jupyter_environments_aliases["cloud"] = "JupyterEnvironmentsApp.cloud"

jupyter_environments_flags = dict(base_flags)
jupyter_environments_flags["dev-build"] = (
    {"JupyterEnvironmentsApp": {"dev_build": True}},
    "Build in development mode.",
)
jupyter_environments_flags["no-minimize"] = (
    {"JupyterEnvironmentsApp": {"minimize": False}},
    "Do not minimize a production build.",
)


class ConfigExportApp(DatalayerApp):
    """An application to export the configuration."""

    version = __version__
    description = """
   An application to export the configuration
    """

    def initialize(self, *args, **kwargs):
        """Initialize the app."""
        super().initialize(*args, **kwargs)

    def start(self):
        """Start the app."""
        if len(self.extra_args) > 1:  # pragma: no cover
            warnings.warn("Too many arguments were provided for workspace export.")
            self.exit(1)
        self.log.info("JupyterEnvironmentsConfigApp %s", self.version)


class JupyterEnvironmentsConfigApp(DatalayerApp):
    """A config app."""

    version = __version__
    description = """
    Manage the configuration
    """

    subcommands = {}
    subcommands["export"] = (
        ConfigExportApp,
        ConfigExportApp.description.splitlines()[0],
    )

    def start(self):
        try:
            super().start()
            self.log.error("One of `export` must be specified.")
            self.exit(1)
        except NoStart:
            pass
        self.exit(0)


class JupyterEnvironmentsShellApp(DatalayerApp):
    """A shell app."""

    version = __version__
    description = """
    Run predefined scripts.
    """

    def start(self):
        super().start()
        args = sys.argv
        self.log.info(args)
            


class JupyterEnvironmentsApp(DatalayerApp):
    name = "jupyter_environments"
    description = """
    Import or export a JupyterLab workspace or list all the JupyterLab workspaces

    You can use the "config" sub-commands.
    """
    version = __version__

    aliases = jupyter_environments_aliases
    flags = jupyter_environments_flags

    cloud = Unicode("ovh", config=True, help="The app directory to build in")

    minimize = Bool(
        True,
        config=True,
        help="Whether to minimize a production build (defaults to True).",
    )

    subcommands = {
        "config": (JupyterEnvironmentsConfigApp, JupyterEnvironmentsConfigApp.description.splitlines()[0]),
        "sh": (JupyterEnvironmentsShellApp, JupyterEnvironmentsShellApp.description.splitlines()[0]),
    }

    def initialize(self, argv=None):
        """Subclass because the ExtensionApp.initialize() method does not take arguments"""
        super().initialize()

    def start(self):
        super(JupyterEnvironmentsApp, self).start()
        self.log.info("JupyterEnvironments - Version %s - Cloud %s ", self.version, self.cloud)


# -----------------------------------------------------------------------------
# Main entry point
# -----------------------------------------------------------------------------

main = launch_new_instance = JupyterEnvironmentsApp.launch_instance

if __name__ == "__main__":
    main()
