import createAsset from '../../actions/create_asset';
import PiecesCacheSingleton from '../../cache/pieces_cache';
import Notifications from '../../connection/notification_handler';
import versionCheck, { versionChecker } from '../../connection/version_check';
import Constants from '../../const';
import { returnedSnippet } from '../../models/typedefs';
import {
  defaultSortingView,
  searchBoxElement,
  sortSnippetsDropdownElement,
} from '../render/renderSearchBox';
import { SortSnippetsBy } from '../../models/SortSnippetsBy';
import { showLoadErrorState } from '../render/showLoadErrorState';
import { showLoadingState } from '../render/showLoadingState';
import { showNoSnippetState } from '../render/showNoSnippetState';
import { renderLanguageView } from './renderLanguageView';
import { renderListView } from './renderListView';
import Discovery from '../../actions/discover_snippets';
import { snippetDiscovery } from '../../models/snippetDiscovery';
import { saveAllIcon } from '../LabIcons';
import SearchFiltersModal from '../modals/SearchFiltersModal';
import Modal from '../modals/Modal';

export default class DisplayController {
  public static filterModalBtn: HTMLElement;
  public static containerDiv = document.createElement('div'); // Holding Div
  private static dropdownRow: HTMLDivElement;
  public static sortDropdown = sortSnippetsDropdownElement();
  public static isLoading = true;
  public static isFetchFailed = false;
  public static discoveryCheckboxArray: snippetDiscovery[] = [];
  private static searchFilterModal: Modal;

  static appendDiscovery = (value: snippetDiscovery) => {
    this.discoveryCheckboxArray.push(value);
  };
  static clearDiscovery = () => {
    this.discoveryCheckboxArray = [];
  };

  static setIsLoading = (val: boolean) => {
    this.isLoading = val;
  };

  static setIsFetchFailed = (val: boolean) => {
    this.isFetchFailed = val;
  };

  static createSnippetListView = async ({
    containerVar,
  }: {
    containerVar: Element;
    snippets: returnedSnippet[];
    viewType: SortSnippetsBy;
    searched?: boolean;
  }) => {
    //Add the search box
    containerVar.id = 'piecesContainer';
    containerVar.classList.add('pieces-container');

    const searchBoxDiv = document.createElement('div');
    searchBoxDiv.classList.add('search-box-div');
    searchBoxDiv.appendChild(searchBoxElement());

    this.dropdownRow = document.createElement('div');
    this.dropdownRow.classList.add('row', 'search-row', 'search-row-dropdown');

    this.dropdownRow.appendChild(this.sortDropdown);

    searchBoxDiv.appendChild(this.dropdownRow);

    // Discover View Additions

    containerVar.appendChild(searchBoxDiv);

    this.drawSnippets({});
    containerVar.appendChild(this.containerDiv);
    this.containerDiv.classList.add('container-div');
    this.containerDiv.id = 'pieces-snippet-container';
  };

  // Make sure you call create view before calling this
  //   - this is also called by createview
  // Call this to redraw the view
  static drawSnippets = async ({
    snippets,
    search,
  }: {
    snippets?: returnedSnippet[];
    search?: boolean;
  }) => {
    const cache: PiecesCacheSingleton = PiecesCacheSingleton.getInstance();
    this.containerDiv.innerHTML = '';
    this.containerDiv.classList.remove('load-error-state');
    console.log('Pieces For Developers: Redrawing');

    //Set up the loading state
    if (this.isLoading) {
      showLoadingState(this.containerDiv);
      return;
    }

    if (this.isFetchFailed || !(await versionCheck({}))) {
      showLoadErrorState(this.containerDiv);
      return;
    }

    if (cache.assets.length === 0) {
      showNoSnippetState(this.containerDiv);
      return;
    }

    let piecesSnippets = snippets !== undefined ? snippets : cache.assets;

    let discoverElements: HTMLDivElement = this.createDiscoverElements({});
    document.getElementById('pieces-filter-button')?.remove();
    if (defaultSortingView !== SortSnippetsBy.Discover) {
      const filterBtn = document.createElement('button');
      this.filterModalBtn = filterBtn;
      filterBtn.classList.add('jp-btn');
      filterBtn.id = 'pieces-filter-button';
      this.dropdownRow.appendChild(filterBtn);
      filterBtn.innerHTML = Constants.FILTER_ICON;
      const disableFilters = versionChecker({ minVersion: '6.1.0' });
      filterBtn.onclick = () => {
        disableFilters
          .then((val) => {
            if (val) {
              if (!this.searchFilterModal) {
                this.searchFilterModal = new SearchFiltersModal();
              }
              this.searchFilterModal.open();
            } else {
              Notifications.getInstance().error({
                message:
                  'Please update to Pieces OS 6.1.0 or higher to use the snippet filtering feature.',
              });
            }
          })
          .catch();
      };
    }
    if (defaultSortingView === SortSnippetsBy.Recent) {
      renderListView({
        container: this.containerDiv,
        snippets: search
          ? piecesSnippets
          : piecesSnippets.sort(
              (a, b) => b.created.getTime() - a.created.getTime()
            ),
      });
      const dropdownDiv = document.getElementById('discovery-nav-div');
      dropdownDiv?.remove();
    } else if (defaultSortingView === SortSnippetsBy.Language) {
      renderLanguageView({
        container: this.containerDiv,
        snippets: search
          ? piecesSnippets
          : piecesSnippets.sort((a, b) => a.language.localeCompare(b.language)),
      });
      const dropdownDiv = document.getElementById('discovery-nav-div');
      dropdownDiv?.remove();
    } else if (defaultSortingView === SortSnippetsBy.Discover) {
      const dropdownDiv = document.getElementById('discovery-nav-div');
      dropdownDiv?.remove();
      this.dropdownRow.appendChild(discoverElements);
      if (search && snippets) {
        renderListView({
          container: this.containerDiv,
          snippets: snippets,
        });
      } else if (cache.discoveredSnippets.length === 0) {
        showLoadingState(this.containerDiv);
        await Discovery.discoverAllSnippets();
      } else {
        renderListView({
          container: this.containerDiv,
          snippets: cache.discoveredSnippets,
        });
      }
    }
  };

  static createDiscoverElements = ({}: {}) => {
    const cache: PiecesCacheSingleton = PiecesCacheSingleton.getInstance();
    const saveAllDiv = document.createElement('div');
    saveAllDiv.classList.add('discovery-div');
    saveAllDiv.id = 'discovery-nav-div';

    const selectAllDiv = document.createElement('div');
    saveAllDiv.appendChild(selectAllDiv);
    selectAllDiv.classList.add('discovery-div-inner');

    const selectAllCheckbox = document.createElement('input');
    selectAllCheckbox.id = 'select-all-checkbox';
    selectAllCheckbox.classList.add('discovery-checkbox-appearance');
    selectAllDiv.appendChild(selectAllCheckbox);
    selectAllCheckbox.type = 'checkbox';

    selectAllCheckbox.addEventListener('click', () => {
      if (selectAllCheckbox.checked) {
        for (let i = 0; i < this.discoveryCheckboxArray.length; i++) {
          this.discoveryCheckboxArray[i].snippetCheckbox.checked = true;
        }
      } else {
        for (let i = 0; i < this.discoveryCheckboxArray.length; i++) {
          this.discoveryCheckboxArray[i].snippetCheckbox.checked = false;
        }
      }
    });

    const selectAllLabel = document.createElement('label');
    selectAllLabel.htmlFor = 'select-all-checkbox';
    selectAllDiv.appendChild(selectAllLabel);
    selectAllLabel.innerText = 'Select all';
    selectAllLabel.classList.add('discovery-title');

    const discBreak = document.createElement('div');
    discBreak.classList.add('discovery-break');
    saveAllDiv.appendChild(discBreak);

    const saveButton = document.createElement('button');
    saveAllDiv.appendChild(saveButton);
    saveAllIcon.element({
      container: saveButton,
    });
    saveButton.classList.add('jp-btn', 'discovery-save-btn');
    saveButton.title =
      cache.discoveredSnippets.length < 1
        ? "There aren't any selected snippets to save"
        : 'Save all selected snippets to Pieces';
    saveButton.addEventListener('click', async () => {
      const loading = document.createElement('div');
      loading.classList.add('bouncing-loader');
      loading.appendChild(document.createElement('div'));
      loading.appendChild(document.createElement('div'));
      loading.appendChild(document.createElement('div'));
      saveAllDiv.replaceChild(loading, saveButton);
      if (
        this.discoveryCheckboxArray.filter((check) => {
          return check.snippetCheckbox.checked;
        }).length === 0
      ) {
        const notifications: Notifications = Notifications.getInstance();
        notifications.information({
          message: Constants.NO_SELECTION_SAVE,
        });
      }
      for (let i = 0; i < this.discoveryCheckboxArray.length; i++) {
        const element = this.discoveryCheckboxArray[i];

        if (element.snippetCheckbox.checked) {
          await createAsset({
            selection: element.snippetObject.raw,
            name: element.snippetObject.title,
            annotations: element.snippetObject.annotations,
            lang: element.snippetObject.language,
          });

          const discoverIndx = cache.discoveredSnippets.findIndex((value) => {
            return value.id === element.snippetObject.id;
          });
          cache.discoveredSnippets.splice(discoverIndx, 1);

          const removalEl = document.getElementById(
            'snippet-el-' + element.snippetObject.id
          );
          removalEl?.remove();
          this.discoveryCheckboxArray.splice(
            this.discoveryCheckboxArray.indexOf(element),
            1
          );
        }
      }
      if (cache.discoveredSnippets.length === 0) {
        this.drawSnippets({});
      }
      saveAllDiv.replaceChild(saveButton, loading);
    });
    return saveAllDiv;
  };
}
