import { Widget } from "@lumino/widgets";
import * as React from "react";
import i18next from "./i18n";
import { JDirectory, WorkspaceTree } from "./model";

interface TrainingPanelProps {
  openExercisesNotebook: (path: string, lang: string) => void;
  arboFormation: WorkspaceTree | null;
  getCurrentWidget: () => Widget | null;
}

interface TrainingPanelState {
  filter: string[];
  lang: string;
  doneExercises: string[];
  needHelpExercises: string[];
  tab: string;
  paths: string;
  downloaded: boolean;
}

function getUserLanguage() {
  if (i18next.language) {
    return i18next.language;
  }
  if (navigator.language === 'fr') {
    return 'fr';
  }
  return 'en';
}

export class TrainingPanel extends React.Component<
  TrainingPanelProps,
  TrainingPanelState
> {
  private title = 'Training';
  constructor(props: TrainingPanelProps) {
    super(props);
    this.state = {
      filter: [],
      lang: getUserLanguage(),
      doneExercises: [],
      needHelpExercises: [],
      tab: 'exercises',
      paths: '',
      downloaded: false
    };
  }

  private handleFilterChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    this.setState({
      filter: event.currentTarget.value.toLowerCase().split(' ')
    });
  };

  private handleLanguageChange = (
    event: React.ChangeEvent<HTMLSelectElement>
  ) => {
    i18next.changeLanguage(event.target.value);
    this.setState({ lang: event.target.value });
  };

  private handlePathChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    this.setState({ paths: event.target.value });
  };

  private addToSearchBar = (event: React.MouseEvent<HTMLAnchorElement>) => {
    let currentTag = event.currentTarget.text.trim();
    if (!isNaN(parseInt(currentTag))) {
      currentTag = 'difficulty:' + currentTag;
    }
    const existingTags = this.state.filter;
    if (existingTags.indexOf(currentTag) === -1) {
      existingTags.push(currentTag);
    }
    this.setState({ filter: existingTags });
  };

  private filterOnPaths(dir: JDirectory): boolean {
    if (this.state.paths === '') {
      return true;
    }
    if (dir.metadata && 'paths' in dir.metadata) {
      if (dir.metadata['paths'].includes(this.state.paths)) {
        return true;
      }
    }
    return false;
  }

  private filterOnTags(dir: JDirectory): boolean {
    let isIncluded = true;
    const metadata = dir.metadata;
    let tagsString = '';
    if (metadata) {
      let keywords = metadata['topics'].concat(metadata['slug']);
      if (metadata['slug_fr']) {
        keywords = keywords.concat(metadata['slug_fr']);
      }
      keywords.map((tag: string) => {
        tagsString = tagsString + tag.trim() + i18next.t(tag.trim());
      });
      tagsString = ['difficulty:' + metadata['difficulty'], tagsString]
        .join(' ')
        .toLowerCase();
    }
    // exercises are filtered with AND
    this.state.filter.map((word: string) => {
      isIncluded = tagsString.includes(word) && isIncluded;
    });
    return isIncluded;
  }

  private sortByMetadata(
    dir1: JDirectory,
    dir2: JDirectory,
    metadata: string
  ): number {
    try {
      const difficultyDiff = dir1.metadata[metadata] - dir2.metadata[metadata];
      if (difficultyDiff !== 0) {
        return difficultyDiff;
      }
      const name1 = dir1.name.toLowerCase();
      const name2 = dir2.name.toLowerCase();
      return name1.localeCompare(name2);
    } catch (err) {
      return 0;
    }
  }

  private resetFilters = () => {
    this.setState({ filter: [] });
  };

  private getTrainingPaths(exos: JDirectory[]) {
    const trainingPaths = new Set();
    exos.map((exo: JDirectory) => {
      if (exo.metadata.paths) {
        for (const p of exo.metadata.paths) {
          trainingPaths.add(p);
        }
      }
    });
    return trainingPaths;
  }

  private getButtonTitle(dir: JDirectory) {
    const suffix = '.'.concat(this.state.lang, 'ipynb');
    let buttonTitle = dir.path.replace(suffix, '').replace(/^.*_/, '');
    if (dir.metadata) {
      buttonTitle = dir.metadata['slug'];
      if (`slug_${this.state.lang}` in dir.metadata) {
        buttonTitle = dir.metadata[`slug_${this.state.lang}`];
      }
    }
    if (buttonTitle.includes('__')) {
      buttonTitle = buttonTitle.split('__')[1];
    }
    return buttonTitle;
  }

  private getIsActiveButtonClass(name: string, currentWidget: any) {
    // To activate the button of the current notebook
    let activeButton = '';
    if (currentWidget !== null) {
      if (
        name ===
        currentWidget.context.path.split('/').slice(-2).pop().split('.')[0]
      ) {
        activeButton = 'current-button';
      }
    }
    return activeButton;
  }

  private renderAdvancedOptions(trainingPaths: string[]) {
    return (
      <div>
        <div className="showHide">
          <label
            htmlFor="toggle"
            id="toggle-options"
            className="dropdown-toggle"
          >
            {i18next.t('Advanced options')}
          </label>
          <div className="fieldsetContainer">
            <fieldset>
              <form>
                <div className="form-group">
                  <div className="form-group">
                    <label htmlFor="lang">{i18next.t('Language')}</label>{' '}
                    <select
                      id="lang"
                      className="form-control-sm custom-select"
                      onChange={this.handleLanguageChange}
                      value={this.state.lang}
                    >
                      <option value="en">en</option>
                      <option value="fr">fr</option>
                    </select>
                  </div>
                  <select
                    className="form-control-sm custom-select"
                    id="path"
                    onChange={this.handlePathChange}
                    value={this.state.paths}
                  >
                    <option value="">{i18next.t('Select your path')}</option>
                    {trainingPaths.map((path: string) => {
                      return (
                        <option value={path} key={path}>
                          {i18next.t(path)}
                        </option>
                      );
                    })}
                  </select>
                </div>
              </form>
            </fieldset>
          </div>
        </div>
      </div>
    );
  }

  public renderArbo(
    arbo: JDirectory[],
    openNotebook: any,
    orderby: string,
    getCurrentWidget: () => Widget | null
  ) {
    const handledCategories = new Set();
    return arbo
      .sort((dir1: JDirectory, dir2: JDirectory) =>
        this.sortByMetadata(dir1, dir2, orderby)
      )
      .filter((dir: JDirectory) => this.filterOnTags(dir))
      .filter((dir: JDirectory) => this.filterOnPaths(dir))
      .map((dir: JDirectory, exoIndex: number) => {
        const buttonTitle = this.getButtonTitle(dir);
        const difficultyString = dir.metadata ? dir.metadata.difficulty : '';
        const currentWidget = getCurrentWidget();
        const isActive = this.getIsActiveButtonClass(
          dir.path.split('/').slice(-1)[0],
          currentWidget
        );
        const dirCategory = dir.metadata ? dir.metadata.category : 'More';
        const isNewCategory = !handledCategories.has(dirCategory);
        if (isNewCategory) {
          handledCategories.add(dirCategory);
        }
        let difficultyColor = "#8be757";
        switch (parseInt(difficultyString)) {
          case 2:
            difficultyColor = '#8bb527';
            break;
          case 3:
            difficultyColor = '#f2e501';
            break;
          case 4:
            difficultyColor = '#fdc50c';
            break;
          case 5:
            difficultyColor = '#ffa400';
            break;
          case 6:
            difficultyColor = '#ee8f1c';
            break;
          case 7:
            difficultyColor = '#ee7621';
            break;
          case 8:
            difficultyColor = '#ff6347';
            break;
          case 9:
            difficultyColor = '#b52a2a';
            break;
          case 10:
            difficultyColor = '#8b0000';
            break;
        }
        return (
          <div key={`category-${exoIndex}`}>
            {isNewCategory ? (
              <div className="category">
                <h2>{i18next.t(dirCategory)}</h2>
              </div>
            ) : null}
            <div
              key={`exo-${exoIndex}`}
              className={`list-group-item list-group-item-action ${isActive}`}
            >
              <div>
                <div className="form-check form-check-inline">
                  <a
                    href="#"
                    onClick={() => openNotebook(dir.path, this.state.lang)}
                    className="button-title"
                  >
                    {i18next.t(buttonTitle)}
                  </a>
                </div>
                <div className={"float-right my-2"}>
                  <a
                    href="#"
                    onClick={this.addToSearchBar}
                    className="badge badge-pill badge-secondary button-difficulty"
                    title={`This ${dir.type} is difficulty ${difficultyString}`}
                    style={{
                      marginLeft: '0.5em',
                      backgroundColor: difficultyColor
                    }}
                  >
                    {difficultyString}
                  </a>
                </div>
              </div>
              <div className="button-tags">
                {dir.metadata &&
                  dir.metadata['topics'].map(
                    (tag: string, tagIndex: number) => {
                      return (
                        <a
                          href="#"
                          key={['tag', exoIndex, tagIndex].join('-')}
                          onClick={this.addToSearchBar}
                          className="badge badge-light"
                        >
                          {i18next.t(tag)}
                        </a>
                      );
                    }
                  )}
              </div>
            </div>
          </div>
        );
      });
  }

  public render() {
    const {
      arboFormation,
      openExercisesNotebook,
      getCurrentWidget,
    } = this.props;
    if (!arboFormation) {
      return (
        <div className="jp-TableOfContents" id="jupyterlab-training">
          <header className="formation-header">{this.title}</header>
          <h2>Error</h2>
          <h3>Cannot find workspace</h3>
        </div>
      );
    }
    const trainingPaths = this.getTrainingPaths(arboFormation.exos);

    return (
      <div className="jp-TableOfContents" id="jupyterlab-training">
        <header className="formation-header">{this.title}</header>
        <div className="input-group mb-3" id="filter">
          <input
            className="form-control"
            placeholder="Search"
            onChange={this.handleFilterChange}
            value={this.state.filter.join(' ')}
          />
          <div className="input-group-append">
            <div className="input-group-text">
              <button
                type="button"
                className="btn close"
                aria-label="Remove content"
                onClick={this.resetFilters}
              >
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
          </div>
        </div>
        <input type="checkbox" id="toggle" />
        {this.renderAdvancedOptions([...trainingPaths] as string[])}
        <ul className="nav nav-tabs nav-justified" role="tablist">
          <li className="nav-item">
            <a
              className={
                'nav-link' + (this.state.tab === 'exercises' ? ' active' : '')
              }
              id="exercises-tab"
              onClick={() => this.setState({ tab: 'exercises' })}
            >
              {i18next.t('exercises')}
            </a>
          </li>
          <li className="nav-item">
            <a
              className={
                'nav-link' + (this.state.tab === 'courses' ? ' active' : '')
              }
              id="courses-tab"
              onClick={() => this.setState({ tab: 'courses' })}
            >
              {i18next.t('courses')}
            </a>
          </li>
        </ul>
        <div className="tab-content">
          <div
            className={
              'tab-pane fade' +
              (this.state.tab === 'exercises' ? ' show active' : '')
            }
          >
            <div
              id="exercises"
              className="exercises list-group list-group-flush"
            >
              {this.renderArbo(
                arboFormation.exos,
                openExercisesNotebook,
                'order',
                getCurrentWidget
              )}
            </div>
          </div>
          <div
            className={
              'tab-pane fade' +
              (this.state.tab === 'courses' ? ' show active' : '')
            }
          >
            <div
              id="exercises"
              className="exercises list-group list-group-flush"
            >
              {this.renderArbo(
                arboFormation.courses,
                openExercisesNotebook,
                'order',
                getCurrentWidget
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }
}
