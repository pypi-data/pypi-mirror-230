import * as React from 'react';
import * as ReactDOM from 'react-dom';
import { Contents, ServiceManager } from '@jupyterlab/services';
import { IDocumentManager } from '@jupyterlab/docmanager';
import { IRenderMimeRegistry } from '@jupyterlab/rendermime';
import { Widget } from '@lumino/widgets';
import {
  INotebookTracker,
  NotebookActions,
  NotebookPanel
} from '@jupyterlab/notebook';
import { ILabShell } from '@jupyterlab/application';
import { Cell, CodeCell, MarkdownCell } from '@jupyterlab/cells';

import { JFile, WorkspaceTree } from './model';
import { TrainingPanel } from './panel';
import { SpinnerPanel } from './utils';

function createFormationCell(cell: CodeCell, typeCell: string) {
  // first time element is marked
  let cellHeaderDiv = cell.node.getElementsByClassName(
    'toggleFormationCellButton'
  )[0];
  if (cellHeaderDiv) {
    // remove it
    cellHeaderDiv.remove();
  }
  // create a new cell header
  cell.readOnly = true;
  cell.model.setMetadata('editable', false);
  cell.model.setMetadata('deletable', false);
  cell.addClass('formation-cell');
  cellHeaderDiv = document.createElement('div');
  if (cell.inputArea) {
    cell.inputArea.hide();
    if (typeCell !== 'Quiz') {
      cellHeaderDiv.innerHTML += `<button class="toggleFormationCellButton">Show ${typeCell}</button>`;
      const cellHeader = cell.node.getElementsByClassName('jp-CellHeader')[0];
      cellHeader.appendChild(cellHeaderDiv);
      const cellHeaderButton = cell.node.getElementsByClassName(
        'toggleFormationCellButton'
      )[0];
      cellHeaderButton.addEventListener('click', () => {
        if (cell.inputArea?.isHidden) {
          cell.inputArea?.show();
          cellHeaderButton.innerHTML = `Hide ${typeCell}`;
        } else {
          cell.inputArea?.hide();
          cellHeaderButton.innerHTML = `Show ${typeCell}`;
        }
      });
    }
  }
}

function createSpinner() {
  const spinnerDiv = document.createElement('div');
  spinnerDiv.setAttribute('id', 'spinner');
  return spinnerDiv;
}

function parseNotebook(cw: NotebookPanel) {
  cw.content.widgets.forEach((cell: Cell) => {
    // search for cell code tags
    if (cell instanceof CodeCell) {
      cell.ready.then(() => {
        const tags = cell.model.getMetadata('tags') as Array<string>;
        if (tags.includes('test')) {
          createFormationCell(cell, 'Unittests');
          // add spinner
          const spinnerDiv = createSpinner();
          const outputCell =
            cell.node.getElementsByClassName('jp-Cell-outputArea')[0];
          outputCell.appendChild(spinnerDiv);
          // need to wait for the notebook to be totally loaded
          setTimeout(() => {
            CodeCell.execute(cell as CodeCell, cw.sessionContext).then(() =>
              outputCell.removeChild(spinnerDiv)
            );
          }, 700);
        } else if (tags.includes('solution')) {
          createFormationCell(cell, 'Solution');
        } else if (tags.includes('quiz')) {
          createFormationCell(cell, 'Quiz');
          // add spinner
          const spinnerDiv = createSpinner();
          const outputCell =
            cell.node.getElementsByClassName('jp-Cell-outputArea')[0];
          outputCell.appendChild(spinnerDiv);
          // need to wait for the notebook to be totally loaded
          setTimeout(() => {
            CodeCell.execute(cell as CodeCell, cw.sessionContext).then(() =>
              outputCell.removeChild(spinnerDiv)
            );
          }, 700);
        }
      });
    } else {
      // markdown cells
      if (cell instanceof MarkdownCell) {
        cell.ready.then(() => {
          cell.readOnly = true;
          cell.model.setMetadata('editable', false);
          cell.model.setMetadata('deletable', false);
        });
      }
    }
  });
}

function reparseNotebook(cw: NotebookPanel) {
  cw.content.widgets.forEach((cell: Cell) => {
    // search for cell code tags
    if (cell instanceof CodeCell) {
      cell.ready.then(() => {
        const tags = cell.model.getMetadata('tags') as Array<string>;
        if (tags.includes('test')) {
          createFormationCell(cell, 'Unittests');
        } else if (tags.includes('solution')) {
          createFormationCell(cell, 'Solution');
        } else if (tags.includes('quiz')) {
          createFormationCell(cell, 'Quiz');
        }
      });
    }
  });
}

/**
 * A widget for hosting training content
 */
export class FormationTOC extends Widget {
  /**
   * Create a new table of contents.
   */
  constructor(options: FormationTOC.Options) {
    super();
    this._rendermime = options.rendermime;
    this._docmanager = options.docmanager;
    this._serviceManager = options.serviceManager;
    this._notebookTracker = options.notebookTracker;
    this._currentWidget = null;
    this._labShell = options.labShell;
    this._arboFormation = null;

    // show spinner while loading workspace at the first time
    this.renderPanel(<SpinnerPanel />);
  }

  private renderPanel = (panelElement: any) => {
    ReactDOM.render(panelElement, this.node, () => {
      if (this._currentWidget && this._rendermime.latexTypesetter) {
        this._rendermime.latexTypesetter.typeset(this.node);
      }
    });
  };

  set currentWidget(widget: Widget | null) {
    if (widget && this._currentWidget && this._currentWidget === widget) {
      return;
    }
    this._currentWidget = widget;
    // If we are wiping the Panel, update and return.
    this.updateFormationPanel();
  }

  /**
   * Handle an update request.
   */
  protected onUpdateRequest(): void {
    this.updateFormationPanel();
    this.parseOpenedNotebooks();
  }

  public updateMenu(): void {
    setTimeout(() => {
      this.updateFormationPanel();
    }, 200);
  }

  private parseOpenedNotebooks() {
    this._notebookTracker.forEach(this.parseOpenedNotebook);
  }

  private parseOpenedNotebook(cw: NotebookPanel) {
    cw.revealed.then(() => {
      cw.sessionContext.ready.then(() => {
        reparseNotebook(cw);
        // auto save
        setTimeout(() => {
          cw.context.save();
        }, 2000);
      });
    });
  }

  private async getNotebookByLang(dirPath: string, lang: string) {
    // Get the notebook of the current language or the default one (english)
    const { contents } = this._serviceManager;
    const opts: Contents.IFetchOptions = {
      content: true
    };
    const filesModel = await contents.get(dirPath, opts);
    const files = filesModel.content.filter((elt: JFile) =>
      elt.path.endsWith('ipynb')
    );
    for (const nb of files) {
      if (nb.name.includes('.'.concat(lang))) {
        return nb;
      }
    }
    return files[0];
  }

  private async updateFormationPanel() {
    const getCurrentWidget = () => {
      return this._notebookTracker.currentWidget;
    };

    // get exercises notebook path and open it ...
    const openExercisesNotebook = async (dirPath: string, lang: string) => {
      const notebook = await this.getNotebookByLang(dirPath, lang);
      try {
        this._docmanager.services.contents
          .get(notebook.path, { content: false })
          .then(() => {
            const newWidget = this._docmanager.openOrReveal(notebook.path);
            newWidget?.revealed.then(() => {
              this._labShell.activateById('tab-manager');
              // manage notebook
              const cWidget = this._notebookTracker.currentWidget;
              cWidget?.sessionContext.ready.then(() => {
                this._labShell.activateById('tab-manager');
                // cleaning notebook
                NotebookActions.clearAllOutputs(cWidget.content);
                parseNotebook(cWidget);
              });
            });
          });
      } catch (error) {
        alert('this exercice is not available');
      }
    };

    // get content of training directory and make one button by subdirectory name
    if (this._arboFormation === null) {
      try {
        this._arboFormation = await WorkspaceTree.create(this._serviceManager);
      } catch (err) {
        this._arboFormation = null;
        console.error(err);
      }
    }
    const panelWorkspace = (
      <TrainingPanel
        openExercisesNotebook={openExercisesNotebook}
        arboFormation={this._arboFormation}
        getCurrentWidget={getCurrentWidget}
      />
    );
    this.renderPanel(panelWorkspace);
  }

  /**
   * Rerender after showing.
   */
  protected onAfterShow(): void {
    this.update();
  }
  private _rendermime: IRenderMimeRegistry;
  private _docmanager: IDocumentManager;
  private _serviceManager: ServiceManager.IManager;
  private _notebookTracker: INotebookTracker;
  private _currentWidget: Widget | null;
  private _arboFormation: WorkspaceTree | null;
  private _labShell: ILabShell;
}

/**
 * A namespace for FormationTOC statics.
 */
export namespace FormationTOC {
  /**
   * Options for the constructor.
   */
  export interface Options {
    docmanager: IDocumentManager;
    rendermime: IRenderMimeRegistry;
    serviceManager: ServiceManager.IManager;
    notebookTracker: INotebookTracker;
    labShell: ILabShell;
  }
}
