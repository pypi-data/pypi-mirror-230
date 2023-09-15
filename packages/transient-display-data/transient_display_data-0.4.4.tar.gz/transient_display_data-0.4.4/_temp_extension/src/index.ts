import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

/**
 * Initialization data for the transient-display-data extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'transient-display-data:plugin',
  description: 'Extension to display transient_display_data in Jupyter Lab',
  autoStart: true,
  activate: (app: JupyterFrontEnd) => {
    console.log('JupyterLab extension transient-display-data is activated!');
  }
};

export default plugin;
