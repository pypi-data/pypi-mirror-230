import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { MainAreaWidget, ICommandPalette } from '@jupyterlab/apputils';
import { ILauncher } from '@jupyterlab/launcher';
import icon from '@datalayer/icons-react/data2/RecyclingIconLabIcon';
import { requestAPI } from './handler';
import { EnvironmentsWidget } from './widget';
import { connect } from './ws';

import '../style/index.css';

/**
 * The command IDs used by the jupyter-environments plugin.
 */
namespace CommandIDs {
  export const create = 'create-jupyter-environments-widget';
}

/**
 * Initialization data for the @datalayer/jupyter-environments extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: '@datalayer/jupyter-environments:plugin',
  autoStart: true,
  requires: [ICommandPalette],
  optional: [ISettingRegistry, ILauncher],
  activate: (
    app: JupyterFrontEnd,
    palette: ICommandPalette,
    settingRegistry: ISettingRegistry | null,
    launcher: ILauncher | null
  ) => {
    const { commands } = app;
    const command = CommandIDs.create;
    commands.addCommand(command, {
      caption: 'Show Environments',
      label: 'Environments',
      icon,
      execute: () => {
        const content = new EnvironmentsWidget();
        const widget = new MainAreaWidget<EnvironmentsWidget>({ content });
        widget.title.label = 'Environments';
        widget.title.icon = icon;
        app.shell.add(widget, 'main');
      }
    });
    const category = 'Datalayer';
    palette.addItem({ command, category });
    if (launcher) {
      launcher.add({
        command,
        category,
        rank: 5,
      });
    }
    console.log('JupyterLab plugin @datalayer/jupyter-environments is activated!');
    if (settingRegistry) {
      settingRegistry
        .load(plugin.id)
        .then(settings => {
          console.log('@datalayer/jupyter-environments settings loaded:', settings.composite);
        })
        .catch(reason => {
          console.error('Failed to load settings for @datalayer/jupyter-environments.', reason);
        });
    }
    connect('ws://localhost:8888/api/jupyter/jupyter_environments/echo', true);
    requestAPI<any>('config')
      .then(data => {
        console.log(data);
      })
      .catch(reason => {
        console.error(
          `Error while accessing the jupyter server jupyter_environments extension.\n${reason}`
        );
      });
  }
};

export default plugin;
