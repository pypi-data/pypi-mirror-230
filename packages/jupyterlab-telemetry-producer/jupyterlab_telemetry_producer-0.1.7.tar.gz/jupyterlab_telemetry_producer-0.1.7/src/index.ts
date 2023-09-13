import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';
import { ITelemetryRouter } from 'jupyterlab-telemetry-router';
import { requestAPI } from './handler';
import { producerCollection } from './events';

const PLUGIN_ID = 'jupyterlab-telemetry-producer:plugin';

const plugin: JupyterFrontEndPlugin<void> = {
  id: PLUGIN_ID,
  autoStart: true,
  requires: [ITelemetryRouter, INotebookTracker],
  activate: async (
    app: JupyterFrontEnd,
    telemetryRouter: ITelemetryRouter,
    notebookTracker: INotebookTracker
  ) => {
    const version = await requestAPI<string>('version');
    console.log(`${PLUGIN_ID}: ${version}`);

    const config = await requestAPI<any>('config');

    notebookTracker.widgetAdded.connect(
      async (_, notebookPanel: NotebookPanel) => {
        await notebookPanel.sessionContext.ready; // wait until session id is created
        await telemetryRouter.loadNotebookPanel(notebookPanel);

        producerCollection.forEach(producer => {
          if (config.activeEvents.includes(producer.id)) {
            new producer().listen(
              notebookPanel,
              telemetryRouter,
              config.logNotebookContentEvents.includes(producer.id)
            );
          }
        });
      }
    );
  }
};

export default plugin;
