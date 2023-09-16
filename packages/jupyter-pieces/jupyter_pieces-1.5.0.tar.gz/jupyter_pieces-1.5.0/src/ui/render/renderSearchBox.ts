import { AnalyticsEnum } from '../../analytics/AnalyticsEnum';
import { SegmentAnalytics } from '../../analytics/SegmentAnalytics';
import { renderLoading } from '../utils/renderLoading';
import Search from '../../actions/search';
import DisplayController from '../views/DisplayController';
import { versionValid } from '../../connection/version_check';
import Discovery from '../../actions/discover_snippets';
import Notifications from '../../connection/notification_handler';
import { returnedSnippet } from '../../models/typedefs';
import PiecesCacheSingleton from '../../cache/pieces_cache';
import { doSearch } from '../utils/discoverySearch';
import { showLoadingState } from './showLoadingState';
import { SortSnippetsBy } from '../../models/SortSnippetsBy';
import { refreshSnippets } from '../utils/refreshSnippets';
import { cancelIcon, codeSVG, aiSVG } from '../LabIcons';
import Constants from '../../const';

let defaultSearchQuery = '';

const notifications = Notifications.getInstance();
export const searchBox = document.createElement('input');
export const searchBtn = document.createElement('button');
let searchCancelled = false;
export let defaultSortingView = SortSnippetsBy.Recent;

export const setDefaultSortingView = (val: SortSnippetsBy) => {
  defaultSortingView = val;
};

export const handleSearch = async ({
  query,
}: {
  query: string;
}): Promise<void> => {
  const cache = PiecesCacheSingleton.getInstance();
  if (query === '' || defaultSearchQuery === query) {
    return;
  }
  defaultSearchQuery = query;
  searchBox.value = query;
  let result: returnedSnippet[];
  if (defaultSortingView !== SortSnippetsBy.Discover) {
    result = await Search.search({ query: query });
  } else {
    result = doSearch({
      query: query ?? '',
      snippets: cache.discoveredSnippets,
    });
  }
  if (searchCancelled) {
    searchCancelled = false;
    return;
  }
  await DisplayController.drawSnippets({ snippets: result, search: true });
};

export const searchBoxElement = (): HTMLElement => {
  const searchRow = document.createElement('div');
  searchRow.classList.add('row', 'search-row');

  const inputCol = document.createElement('div');
  inputCol.classList.add('col');

  searchBox.classList.add('search-input', 'jp-input');
  searchBox.type = 'text';
  searchBox.placeholder = '🔍  Search for Snippets...';
  searchBox.value = '';
  searchBox.readOnly = !versionValid ? true : false;

  inputCol.appendChild(searchBox);
  searchRow.appendChild(inputCol);

  const searchBtnCol = document.createElement('div');
  searchBtnCol.classList.add('col');

  searchBtn.title = 'Refresh snippets';
  searchBtn.classList.add(/*'pieces-btn-search',*/ 'jp-btn');

  searchBox.value === ''
    ? (searchBtn.innerHTML = Constants.REFRESH_SVG)
    : cancelIcon.element({ container: searchBtn });
  searchBtn.addEventListener('click', async () => {
    if (
      defaultSortingView === SortSnippetsBy.Discover &&
      searchBox.value === ''
    ) {
      notifications.information({
        message: Discovery.discovery_loaded
          ? 'Discovering Pieces...'
          : "We still haven't finished discovering your snippets, please wait.",
      });
      if (Discovery.discovery_loaded) {
        showLoadingState(DisplayController.containerDiv);
        await Discovery.discoverAllSnippets();
      }
    } else if (defaultSortingView === SortSnippetsBy.Discover) {
      searchBox.value = '';
      defaultSearchQuery = '';
      searchBtn.innerHTML = Constants.REFRESH_SVG;
      searchBtn.title = 'Discover snippets';
      DisplayController.drawSnippets({});
    } else {
      if (searchBox.value === '') {
        SegmentAnalytics.track({
          event: AnalyticsEnum.JUPYTER_REFRESH_CLICKED,
        });
        defaultSearchQuery = '';
        refreshSnippets();
      } else {
        searchBox.value = '';
        defaultSearchQuery = '';
        searchBtn.innerHTML = Constants.REFRESH_SVG;
        searchBtn.title = 'Refresh snippets';
        DisplayController.drawSnippets({});
      }
    }
  });

  searchBox.addEventListener('keyup', async (event) => {
    if (event.key === 'Enter' && searchBox.value != '') {
      const loading = renderLoading(document, 'refresh-');
      searchBtnCol.replaceChild(loading, searchBtn);
      try {
        await handleSearch({ query: searchBox.value });
        cancelIcon.element({ container: searchBtn });
        searchBtn.title = 'Clear Search';
      } catch (e) {
        console.log(e);
      }
      searchBtnCol.replaceChild(searchBtn, loading);
    }
  });
  searchBtnCol.appendChild(searchBtn);
  searchRow.appendChild(searchBtnCol);

  return searchRow;
};

export const sortSnippetsDropdownElement = (): HTMLDivElement => {
  const dropdownDiv = document.createElement('div');

  const dropdownElement = document.createElement('select');
  dropdownDiv.appendChild(dropdownElement);
  dropdownElement.classList.add('jp-dropdown');

  const option_recent = document.createElement('option');
  option_recent.value = 'recent';
  option_recent.innerText = '🕓 RECENT';
  dropdownElement.appendChild(option_recent);

  const option_language = document.createElement('option');
  option_language.value = 'language';
  option_language.innerText = '🌐 LANGUAGE';
  dropdownElement.appendChild(option_language);

  const option_discover = document.createElement('option');
  option_discover.value = 'discover';
  option_discover.innerText = '🔍 DISCOVER';
  dropdownElement.appendChild(option_discover);

  dropdownElement.addEventListener('change', async () => {
    if (dropdownElement.value === 'language') {
      setDefaultSortingView(SortSnippetsBy.Language);
    } else if (dropdownElement.value === 'recent') {
      setDefaultSortingView(SortSnippetsBy.Recent);
    } else if (dropdownElement.value === 'discover') {
      setDefaultSortingView(SortSnippetsBy.Discover);
    }

    if (searchBox.value === '') {
      DisplayController.drawSnippets({});
    } else {
      await handleSearch({ query: searchBox.value });
    }
  });

  const option_arrow = document.createElement('span');
  option_arrow.innerText = '▼';
  option_arrow.classList.add('jp-dropdown-arrow');

  dropdownDiv.appendChild(option_arrow);

  return dropdownDiv;
};

export const renderNavBar = ({
  containerVar,
}: {
  containerVar: Element;
}): HTMLDivElement => {
  const backgroundDiv = document.createElement('div');
  backgroundDiv.classList.add('background');
  containerVar.appendChild(backgroundDiv);

  const wrapperDiv = document.createElement('div');
  wrapperDiv.classList.add('wrapper');
  containerVar.appendChild(wrapperDiv);

  const tabsDiv = document.createElement('div');
  wrapperDiv.appendChild(tabsDiv);
  tabsDiv.classList.add('tabs');
  tabsDiv.id = 'piecesTabs';

  const tabInput1 = document.createElement('input');
  tabsDiv.appendChild(tabInput1);
  tabInput1.type = 'radio';
  tabInput1.id = 'radio-1';
  tabInput1.name = 'tabs-1';

  tabInput1.checked = true;

  const tabLabel1 = document.createElement('label');
  tabsDiv.appendChild(tabLabel1);
  tabLabel1.htmlFor = 'radio-1';
  tabLabel1.classList.add('tab');
  tabLabel1.id = 'tab-1';

  codeSVG.element({ container: tabLabel1 });

  const tabInput2 = document.createElement('input');
  tabsDiv.appendChild(tabInput2);
  tabInput2.type = 'radio';
  tabInput2.id = 'radio-2';
  tabInput2.name = 'tabs-2';

  // tabInput2.checked = true;

  const tabLabel2 = document.createElement('label');
  tabsDiv.appendChild(tabLabel2);
  tabLabel2.htmlFor = 'radio-2';
  tabLabel2.classList.add('tab');
  tabLabel2.id = 'tab-2';

  aiSVG.element({ container: tabLabel2 });

  const slider = document.createElement('span');
  tabsDiv.appendChild(slider);
  slider.classList.add('glider');

  return wrapperDiv;
};
