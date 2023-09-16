import { JupyterFrontEnd } from '@jupyterlab/application';
import { Widget } from '@lumino/widgets';
import createAsset from './../actions/create_asset';
import Constants from '../const';
import { SegmentAnalytics } from '../analytics/SegmentAnalytics';
import { AnalyticsEnum } from '../analytics/AnalyticsEnum';
import PiecesCacheSingleton from '../cache/pieces_cache';
import { renderNavBar } from './render/renderSearchBox';
import { SortSnippetsBy } from '../models/SortSnippetsBy';
import DisplayController from './views/DisplayController';
import QGPTView from './views/create_gpt_view';
import { PiecesLogo } from './LabIcons';

export class PiecesView {
  private app: any;
  private viewWidget: Widget;
  private cache = PiecesCacheSingleton.getInstance();
  currentTab: Element | undefined = undefined;

  constructor() {
    this.viewWidget = new Widget();
  }

  public async build(app: JupyterFrontEnd): Promise<void> {
    this.app = app;

    await this.createView();
    this.prepareRightClick();
  }

  private saveSelection(): void {
    SegmentAnalytics.track({
      event: AnalyticsEnum.JUPYTER_SAVE_SELECTION,
    });
    createAsset({ selection: this.app.Editor.selection });
  }

  private prepareRightClick(): void {
    const command = 'jupyter-pieces:menuitem';

    this.app.commands.addCommand(command, {
      label: 'Save to Pieces',
      execute: this.saveSelection,
    });

    this.app.contextMenu.addItem({
      command: command,
      selector: '.jp-CodeCell-input .jp-Editor .jp-Notebook *',
      rank: 100,
    });
  }

  // This should only be called once.
  private async createView() {
    // Create and activate your view widget

    this.viewWidget.id = 'piecesView';
    this.viewWidget.title.closable = true;
    this.viewWidget.title.icon = PiecesLogo;

    const containerVar = this.viewWidget.node;
    containerVar.remove(); // Clean Node

    const snippets = this.cache.assets;

    const wrapper = renderNavBar({ containerVar: containerVar });
    const navTab = wrapper.children[0];
    this.currentTab = navTab.children[1];

    const parentDiv = document.createElement('div');
    parentDiv.classList.add('parent-div-container');
    containerVar.appendChild(parentDiv);

    const snippetsTab = document.createElement('div');
    snippetsTab.id = 'snippets-tab';
    parentDiv.appendChild(snippetsTab);

    const gptTab = document.createElement('div');
    gptTab.id = 'gpt-tab';
    parentDiv.appendChild(gptTab);

    navTab.addEventListener('click', (event) => {
      this.changeViews(event, parentDiv, snippetsTab, gptTab, navTab);
    });
    await QGPTView.createGPTView({ containerVar: gptTab });
    DisplayController.createSnippetListView({
      containerVar: snippetsTab,
      snippets: snippets,
      viewType: SortSnippetsBy.Recent,
    });

    if ((navTab.children[0] as HTMLInputElement).checked) {
      gptTab.style.display = 'none';
    } else if ((navTab.children[2] as HTMLInputElement).checked) {
      parentDiv.classList.add('gpt-parent');
      snippetsTab.style.display = 'none';
    }

    this.app.shell.add(this.viewWidget, 'right', { rank: 1 });
  }

  private async changeViews(
    event: Event,
    parentDiv: HTMLDivElement,
    snippetsTab: HTMLDivElement,
    gptTab: HTMLDivElement,
    navTab: Element
  ) {
    let isActive = true;
    if (event.target == this.currentTab) {
      isActive = false;
    }
    if (isActive) {
      if (event.target == navTab.children[1]) {
        (navTab.children[0] as HTMLInputElement).checked = true;
        (navTab.children[2] as HTMLInputElement).checked = false;
        this.currentTab = navTab.children[1];

        // Update global view variable for analytics
        Constants.PIECES_CURRENT_VIEW = AnalyticsEnum.JUPYTER_VIEW_SNIPPET_LIST;
      } else if (event.target == navTab.children[3]) {
        (navTab.children[0] as HTMLInputElement).checked = false;
        (navTab.children[2] as HTMLInputElement).checked = true;
        this.currentTab = navTab.children[3];

        // Update global view variable for analytics
        Constants.PIECES_CURRENT_VIEW = AnalyticsEnum.JUPYTER_VIEW_CHATBOT;
      }

      if ((navTab.children[0] as HTMLInputElement).checked) {
        parentDiv.classList.remove('gpt-parent');
        gptTab.style.display = 'none';
        snippetsTab.style.display = 'block';
      } else if ((navTab.children[2] as HTMLInputElement).checked) {
        parentDiv.classList.add('gpt-parent');
        snippetsTab.style.display = 'none';
        gptTab.style.display = 'flex';
      }
    }
  }
}
