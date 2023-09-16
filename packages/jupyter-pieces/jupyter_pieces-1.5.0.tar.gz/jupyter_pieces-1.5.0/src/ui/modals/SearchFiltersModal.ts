import {
  AssetFilters,
  ClassificationSpecificEnum,
  FilterOperationTypeEnum,
} from '../../PiecesSDK/core';
import langExtToClassificationSpecificEnum from '../utils/langExtToClassificationSpecificEnum';
import ConnectorSingleton from '../../connection/connector_singleton';
import { AssetsSearchWithFiltersRequest } from '../../PiecesSDK/core';
import Notifications from '../../connection/notification_handler';
import PiecesCacheSingleton from '../../cache/pieces_cache';
import DisplayController from '../views/DisplayController';
import { SortSnippetsBy } from '../../models/SortSnippetsBy';
import { searchLangSpecificEnum } from '../utils/searcLangSpecificEnum';
import Modal from './Modal';
import { setDefaultSortingView } from '../render/renderSearchBox';
import Constants from '../../const';

enum FilterTypeEnum {
  Language = 'Language',
  Tags = 'Tags',
  Phrase = 'Phrase',
}

type JLabAssetFilters = {
  [FilterTypeEnum.Language]?: ClassificationSpecificEnum;
  [FilterTypeEnum.Tags]: Array<string>;
  [FilterTypeEnum.Phrase]?: {
    string: string;
    annotations: boolean;
    titles: boolean;
    content: boolean;
  };
  casing: boolean;
};

export default class SearchFiltersModal extends Modal {
  private filtersRan = false;
  private addedFilters: string[] = [];
  private actionCol: HTMLElement;
  private addButton: HTMLElement;
  private filters: JLabAssetFilters = { Tags: [], casing: false };
  private caseDiv: HTMLDivElement;

  constructor() {
    super();

    this.titleEl.setText('Filter Snippets');

    const container = this.contentEl.createDiv();
    container.classList.add('flex', 'flex-col', 'w-full', 'h-full');

    const description = container.createDiv();
    description.classList.add(
      'text-sm',
      'flex',
      'flex-row',
      'w-full',
      'mt-[-8px]',
      'mb-1',
      'text-[var(--jp-layout-color4)]'
    );
    description.setText(
      'Use filters to narrow your search scope & refine results'
    );

    const filtersRow = container.createDiv();
    filtersRow.classList.add('flex', 'flex-row', 'w-full', 'h-full');

    const filtersCol = filtersRow.createDiv();
    filtersCol.classList.add('flex', 'flex-col', 'w-full', 'h-full');

    const actionRow = container.createDiv();
    actionRow.classList.add('flex', 'flex-row', 'w-full', 'mt-2');

    const addCol = actionRow.createDiv();
    addCol.classList.add('flex', 'flex-col', 'min-h-[32px]');
    const addButton = addCol.createEl('button');
    addButton.innerText = 'Add Filter';
    addButton.onclick = () => {
      this.addFilter(addCol, filtersCol, addButton);
      addButton.classList.add('hidden');
    };
    addButton.classList.add('w-fit', 'mr-2', 'jp-btn');
    this.addButton = addButton;

    const caseCol = actionRow.createDiv();
    caseCol.classList.add('flex', 'flex-col', 'hidden', 'w-full');
    const caseRow = caseCol.createDiv();
    caseRow.classList.add(
      'flex',
      'flex-row',
      'w-full',
      'items-center',
      'h-full'
    );
    const caseCheckBox = caseRow.createEl('input');
    caseCheckBox.type = 'checkbox';
    caseCheckBox.onchange = () => {
      this.filters.casing = caseCheckBox.checked;
    };
    const caseLabel = caseRow.createDiv();
    caseLabel.classList.add('w-full');
    caseLabel.setText('Case Sensitive');
    this.caseDiv = caseCol;

    const actionCol = actionRow.createDiv();
    actionCol.classList.add('flex', 'flex-col', 'w-full', 'hidden');
    this.actionCol = actionCol;

    const actionBtnRow = actionCol.createDiv();
    actionBtnRow.classList.add('flex', 'flex-row', 'justify-end', 'w-full');

    const clearBtn = actionBtnRow.createEl('button');
    clearBtn.onclick = () => {
      filtersCol.empty();
      this.addedFilters = [];
      this.filters = { Tags: [], casing: false };
      actionCol.classList.add('hidden');
      this.addButton.classList.remove('hidden');
      this.caseDiv.classList.add('hidden');
      this.handleClear();
    };
    clearBtn.setText('Clear Filters');
    clearBtn.classList.add('mr-2', 'jp-btn');

    const runBtn = actionBtnRow.createEl('button');
    runBtn.classList.add('jp-btn');
    runBtn.onclick = () => {
      this.runFilters();
    };
    runBtn.setText('Run');
  }
  handleClear() {
    document.getElementById('pieces-filters-options')?.remove();
    if (this.filtersRan) {
      DisplayController.drawSnippets({});
      this.filtersRan = false;
    }
  }

  /*
    Creates a delete button
    - @param parent is the element that should be removed when the delete button is clicked
    - @param container is the element the delete button should be appended to
  */
  buildDeleteBtn(
    parent: HTMLElement,
    container: HTMLElement,
    filter: FilterTypeEnum
  ) {
    const delDiv = container.createDiv();
    delDiv.innerHTML = Constants.DELETE_SVG;
    delDiv.classList.add(
      'hover:text-red-600',
      'cursor-pointer',
      'ml-2',
      'mr-2'
    );
    delDiv.onclick = () => {
      parent.remove();
      document.getElementById('pieces-filters-options')?.remove();
      this.addedFilters.remove(filter);
      this.addButton.classList.remove('hidden');
      if (this.addedFilters.length === 0) {
        this.actionCol.classList.add('hidden');
        this.handleClear();
      }
      delete this.filters[filter];
      if (
        !this.addedFilters.includes('Tags') &&
        !this.addedFilters.includes('Phrase')
      ) {
        this.caseDiv.classList.add('hidden');
        this.filters.casing = false;
      }
    };
    return delDiv;
  }

  /*
    Runs the filter request, and renders the results.
  */
  async runFilters() {
    const config = ConnectorSingleton.getInstance();
    const params: AssetsSearchWithFiltersRequest = {
      transferables: false,
      pseudo: false,
      assetsSearchWithFiltersInput: {
        filters: {
          iterable: [],
        },
        casing: this.filters.casing,
      },
    };
    if (this.filters.Language?.length) {
      // add in the language filter if specified
      params.assetsSearchWithFiltersInput?.filters?.iterable.push({
        classification: this.filters.Language,
      });
    }

    if (this.filters.Tags.filter((el) => el.length).length) {
      // add in the tags filter if specified
      params.assetsSearchWithFiltersInput?.filters?.iterable.push({
        tags: this.filters.Tags,
      });
    }

    // phrase filter is added via 'operations' in order to use OR
    if (this.filters.Phrase?.string.length) {
      // add in the phrase filter if specified
      const operations: AssetFilters = {
        iterable: [],
        type: FilterOperationTypeEnum.Or,
      };
      const value = this.filters.Phrase.string;
      if (this.filters.Phrase.annotations) {
        // they checked annotations
        operations.iterable.push({
          phrase: { value, annotation: true },
        });
      }
      if (this.filters.Phrase.content) {
        // they checked content
        operations.iterable.push({
          phrase: { value, content: true },
        });
      }
      if (this.filters.Phrase.titles) {
        // they checked titles
        operations.iterable.push({
          phrase: { value, title: true },
        });
      }
      if (operations.iterable.length) {
        // they checked at least one box
        params.assetsSearchWithFiltersInput?.filters?.iterable.push({
          operations,
        });
      }
    }

    if (!params.assetsSearchWithFiltersInput?.filters?.iterable.length) {
      Notifications.getInstance().error({
        message: 'Filters were empty, skipping.',
      });
      return;
    }

    const assets = await config.assetsApi
      .assetsSearchWithFilters(params)
      .catch(() => {
        Notifications.getInstance().error({
          message:
            'Something went wrong with filtering your snippets. Please make sure that Pieces OS is installed, updated, and running. If the issue persists please contact support@pieces.app',
        });
      });
    if (!assets) return; // the above call errored, nothing was returned
    if (!assets.results.iterable.length) {
      Notifications.getInstance().error({
        message: 'No results found! Try again with a different set of filters.',
      });
      return;
    } else {
      Notifications.getInstance().information({
        message: `${assets.results.iterable.length} results found!`,
      });
    }

    const cache = PiecesCacheSingleton.getInstance();
    const snippets = cache.assets.filter((el) =>
      assets.results.iterable.some((asset) => asset.identifier === el.id)
    );

    // setSearchResultsView(true);

    setDefaultSortingView(SortSnippetsBy.Recent);
    DisplayController.drawSnippets({ snippets, search: false }).then(() => {
      DisplayController.filterModalBtn.classList.add('!text-blue-400');
    });
    this.filtersRan = true;
    this.close();
  }

  /*
    Builder for classification filter element
  */
  buildClassificationEl(container: HTMLElement) {
    const clsRow = container.createDiv();
    clsRow.classList.add('flex', 'flex-row', 'my-2');

    const clsCol = clsRow.createDiv();
    clsCol.classList.add('flex', 'flex-col');

    const labelRow = clsCol.createDiv();
    labelRow.classList.add(
      'flex',
      'flex-row',
      'text-sm',
      'text-[var(--jp-layout-color4)]'
    );
    labelRow.setText('LANGUAGE');

    const filterRow = clsCol.createDiv();
    filterRow.classList.add('flex', 'flex-row', 'items-center');
    const classificationDropdown = filterRow.createEl('select');
    classificationDropdown.classList.add('w-fit', 'text-center', 'jp-dropdown');

    Object.entries(searchLangSpecificEnum).forEach(([key, value]) => {
      const optEl = classificationDropdown.createEl('option');
      optEl.value = key;
      optEl.text = value;
    });
    classificationDropdown.onchange = () => {
      const value = classificationDropdown.value;
      this.filters[FilterTypeEnum.Language] =
        langExtToClassificationSpecificEnum(value);
    };

    this.filters[FilterTypeEnum.Language] = langExtToClassificationSpecificEnum(
      classificationDropdown.value
    );

    this.buildDeleteBtn(clsRow, filterRow, FilterTypeEnum.Language);
  }

  /*
    Builder for phrase filter element
  */
  buildPhraseEl(container: HTMLElement) {
    this.filters[FilterTypeEnum.Phrase] = {
      string: '',
      annotations: true,
      titles: true,
      content: true,
    };
    const phraseRow = container.createDiv();
    phraseRow.classList.add('flex', 'flex-row', 'my-2', 'w-full');

    const phraseCol = phraseRow.createDiv();
    phraseCol.classList.add('flex', 'flex-col', 'w-full');

    const phraseLabel = phraseCol.createDiv();
    phraseLabel.classList.add(
      'flex-row',
      'flex',
      'text-sm',
      'text-[var(--jp-layout-color4)]'
    );
    phraseLabel.setText('PHRASE');

    const inputRow = phraseCol.createDiv();
    inputRow.classList.add(
      'flex',
      'flex-row',
      'my-1',
      'w-full',
      'items-center'
    );

    const inputEl = inputRow.createEl('input');
    inputEl.type = 'text';
    inputEl.placeholder = 'Filter for an exact text match';
    inputEl.classList.add('w-1/2', 'jp-input', 'search-input', '!mt-0');
    inputEl.onchange = () => {
      this.filters[FilterTypeEnum.Phrase]!.string = inputEl.value;
    };

    const optionRow = phraseCol.createDiv();
    optionRow.classList.add(
      'flex',
      'flex-row',
      'w-full',
      'items-center',
      'my-1'
    );

    const annotationCheckBox = optionRow.createEl('input');
    annotationCheckBox.type = 'checkbox';
    annotationCheckBox.checked = true;
    annotationCheckBox.onchange = () => {
      this.filters[FilterTypeEnum.Phrase]!.annotations =
        annotationCheckBox.checked;
    };

    const annotationLabel = optionRow.createDiv();
    annotationLabel.setText('Match Annotations');
    annotationLabel.classList.add('mx-1');

    const seperatorEl = optionRow.createDiv();
    seperatorEl.classList.add(
      'ml-2',
      'mr-3',
      'text-xs',
      'text-[var(--jp-layout-color4)]'
    );
    seperatorEl.setText('OR');

    const titleCheckbox = optionRow.createEl('input');
    titleCheckbox.checked = true;
    titleCheckbox.type = 'checkbox';
    titleCheckbox.onchange = () => {
      this.filters[FilterTypeEnum.Phrase]!.titles = titleCheckbox.checked;
    };

    const titleLabel = optionRow.createDiv();
    titleLabel.setText('Match Titles');
    titleLabel.classList.add('mx-1');

    optionRow.appendChild(seperatorEl.cloneNode(true));

    const contentCheckbox = optionRow.createEl('input');
    contentCheckbox.type = 'checkbox';
    contentCheckbox.checked = true;
    contentCheckbox.onchange = () => {
      this.filters.Phrase!.content = contentCheckbox.checked;
    };

    const contentLabel = optionRow.createDiv();
    contentLabel.setText('Match Content');
    contentLabel.classList.add('mx-1');

    this.buildDeleteBtn(phraseRow, inputRow, FilterTypeEnum.Phrase);
  }

  buildTagEl(container: HTMLElement) {
    const tagRow = container.createDiv();
    tagRow.classList.add('flex', 'flex-row', 'my-2');

    const tagCol = tagRow.createDiv();
    tagCol.classList.add('flex', 'flex-col');

    const tagLabel = tagCol.createDiv();
    tagLabel.classList.add(
      'flex',
      'flex-row',
      'my-1',
      'text-sm',
      'text-[var(--jp-layout-color4)]'
    );
    tagLabel.setText('TAGS');

    const filtersRow = tagCol.createDiv();
    filtersRow.classList.add(
      'flex',
      'flex-row',
      'my-1',
      'items-center',
      'flex-wrap'
    );
    let tagInputCount = 0;
    const buildTagInput = () => {
      const tagIndx = tagInputCount.valueOf();
      tagInputCount++;
      this.filters[FilterTypeEnum.Tags].push('');
      filtersRow.empty();
      for (const tag of this.filters[FilterTypeEnum.Tags]) {
        const tagFilterCol = filtersRow.createDiv();
        tagFilterCol.classList.add('flex', 'flex-col');

        const tagFilterRow = tagFilterCol.createDiv();
        tagFilterRow.classList.add('flex', 'flex-row', 'items-center', 'my-1');

        const tagFilterEl = tagFilterRow.createEl('input');
        tagFilterEl.type = 'text';
        tagFilterEl.onchange = () => {
          this.filters[FilterTypeEnum.Tags][tagIndx] = tagFilterEl.value;
        };
        tagFilterEl.value = tag;
        tagFilterEl.placeholder = 'Add tag...';
        tagFilterEl.classList.add('mr-1', 'jp-input', 'search-input', '!mt-0');

        const deleteBtn = this.buildDeleteBtn(
          tagFilterCol,
          tagFilterRow,
          FilterTypeEnum.Tags
        );
        // overload the onclick for this button
        deleteBtn.onclick = () => {
          document.getElementById('pieces-filters-options')?.remove();
          tagInputCount--;
          this.filters[FilterTypeEnum.Tags]?.remove(tagFilterEl.value);
          tagFilterCol.remove();
          if (tagInputCount <= 0) {
            tagRow.remove();
            this.addButton.classList.remove('hidden');
            this.addedFilters.remove(FilterTypeEnum.Tags);
            if (this.addedFilters.length === 0) {
              this.actionCol.classList.add('hidden');
              this.handleClear();
            }
            if (
              !this.addedFilters.includes('Tags') &&
              !this.addedFilters.includes('Phrase')
            ) {
              this.caseDiv.classList.add('hidden');
              this.filters.casing = false;
            }
          }
        };
      }
      const plusEl = filtersRow.createDiv();
      plusEl.classList.add(
        'mx-1',
        'cursor-pointer',
        'hover:text-[var(--md-blue-400)]'
      );
      plusEl.innerHTML = Constants.PLUS_ICON;
      plusEl.onclick = () => {
        buildTagInput();
      };
    };

    buildTagInput(); // build the first tag input el
  }

  buildFilterEl(type: FilterTypeEnum, container: HTMLDivElement) {
    if (type === FilterTypeEnum.Language) {
      return this.buildClassificationEl(container);
    } else if (type === FilterTypeEnum.Phrase) {
      return this.buildPhraseEl(container);
    } else if (type === FilterTypeEnum.Tags) {
      return this.buildTagEl(container);
    }
    throw new Error('Invalid filter type');
  }

  /*
    Shows the available filter options to the user, 
    and when an option is clicked it will build a filter element
  */
  addFilter(
    container: HTMLDivElement,
    filterCol: HTMLDivElement,
    addButton: HTMLButtonElement
  ) {
    const options = Object.keys(FilterTypeEnum).filter(
      (el) => !this.addedFilters.includes(el)
    );

    const optionDiv = document.createElement('div');
    optionDiv.id = 'pieces-filters-options';
    optionDiv.classList.add(
      'flex',
      'flex-row',
      'items-center',
      'filter-grow-animation',
      'h-full',
      'mr-1'
    );

    for (let i = 0; i < options.length; i++) {
      const option = options[i];
      if (i !== 0) {
        const split = optionDiv.createDiv();
        split.classList.add('mx-1', 'text-[var(--jp-layout-color4)]');
        split.setText('|');
      }
      const curOption = optionDiv.createDiv();
      curOption.classList.add(
        'underline',
        'cursor-pointer',
        'mx-1',
        'hover:text-[var(--md-blue-400)]',
        'text-[var(--jp-layout-color4)]'
      );
      curOption.setText(option);
      curOption.onclick = () => {
        this.addedFilters.push(option);
        this.buildFilterEl(
          FilterTypeEnum[option as keyof typeof FilterTypeEnum],
          filterCol
        );
        optionDiv.remove();
        this.actionCol.classList.remove('hidden');

        // if this is the last filter the user can add, don't show the add button again.
        if (this.addedFilters.length !== Object.keys(FilterTypeEnum).length) {
          addButton.classList.remove('hidden');
        }
        // if they add a filter that can be case sensitive
        if (option === 'Tags' || option === 'Phrase') {
          this.caseDiv.classList.remove('hidden');
        }
      };
    }
    container.appendChild(optionDiv);
  }

  protected onOpen(): void {
    //
  }
  protected onClose(): void {
    //
  }
}
