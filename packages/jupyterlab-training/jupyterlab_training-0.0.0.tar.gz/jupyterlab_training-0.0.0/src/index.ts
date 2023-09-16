import {
  ILabShell,
  ILayoutRestorer,
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { IDocumentManager } from '@jupyterlab/docmanager';
import { INotebookTracker } from '@jupyterlab/notebook';
import { IRenderMimeRegistry } from '@jupyterlab/rendermime';
import { IMainMenu } from '@jupyterlab/mainmenu';
import { LabIcon } from '@jupyterlab/ui-components';
import { ICommandPalette } from '@jupyterlab/apputils';

import '../style/bootstrap/dist/css/bootstrap.css';
import '../style/index.css';
import { FormationTOC } from './menu';
import { addTour } from './tour';
import logilabIcon from '../style/logilab-icon.svg';

/**
 * Initialization data for the jupyterlab-formation Panel extension.
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-training',
  autoStart: true,
  requires: [
    IDocumentManager,
    ILabShell,
    ILayoutRestorer,
    INotebookTracker,
    IRenderMimeRegistry,
    ICommandPalette,
    IMainMenu
  ],
  activate: activate
};

/**
 * Activate the formation extension.
 */
function activate(
  app: JupyterFrontEnd,
  docmanager: IDocumentManager,
  labShell: ILabShell,
  restorer: ILayoutRestorer,
  notebookTracker: INotebookTracker,
  rendermime: IRenderMimeRegistry
): void {
  console.log('JupyterLab extension jupyterlab-training-launcher');
  // Create the formation panel widget.
  const { serviceManager } = app;
  const formationPanel = new FormationTOC({
    docmanager,
    rendermime,
    notebookTracker,
    serviceManager,
    labShell
  });
  // Add the formation panel to the left area.
  const icon = new LabIcon({
    name: 'Training Menu',
    svgstr: logilabIcon
  });
  formationPanel.title.caption = 'Training Menu';
  formationPanel.title.icon = icon;
  formationPanel.id = 'tab-manager';
  app.shell.add(formationPanel, 'left', { rank: 10 });
  // Add the formation widget to the application restorer.
  restorer.add(formationPanel, formationPanel.id);
  // Change the LogilabPanel when the active widget changes.
  notebookTracker.currentChanged.connect(() => {
    formationPanel.currentWidget = notebookTracker.currentWidget;
    formationPanel.update();
  });

  app.restored.then(() => {
    // open formation panel by default
    labShell.activateById(formationPanel.id);
    // add extension tour
    addTour(app, labShell, notebookTracker, docmanager, formationPanel.id);
  });
}

export default extension;
