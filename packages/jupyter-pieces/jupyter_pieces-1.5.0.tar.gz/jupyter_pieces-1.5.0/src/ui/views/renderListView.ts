import { returnedSnippet } from '../../models/typedefs';
import { getIcon } from './../utils/langExtToIcon';
import { renderSnippet } from './../render/renderSnippets';
import showExportedSnippet from '../snippetExportView';
import { defaultSortingView } from '../render/renderSearchBox';
import { SortSnippetsBy } from '../../models/SortSnippetsBy';
import DisplayController from './DisplayController';
import AnnotationHandler from '../../utils/annotationHandler';

export function renderListView({
  container,
  snippets,
  discovery,
}: {
  container: HTMLDivElement;
  snippets: returnedSnippet[];
  discovery?: boolean;
}): HTMLDivElement {
  for (const snippet of snippets) {
    const snippetElement = constructSnippet({
      snippetData: snippet,
      discovery: discovery,
    });
    container.appendChild(snippetElement);
  }
  return container;
}

export const constructSnippet = ({
  snippetData,
  isPreview,
  opened,
  discovery,
}: {
  snippetData: returnedSnippet;
  isPreview?: boolean;
  opened?: boolean;
  discovery?: boolean;
}): HTMLDivElement => {
  const annotationHandler = AnnotationHandler.getInstance();
  const snippetElement = document.createElement('div');
  snippetElement.classList.add('piecesSnippet');
  snippetElement.id = `snippet-el-${snippetData.id}`;

  if (defaultSortingView === SortSnippetsBy.Discover) {
    const discoveryDiv = document.createElement('div');
    discoveryDiv.classList.add('discovery-div-parent', 'col-sm-fixed');

    const selectCheckbox = document.createElement('input');
    selectCheckbox.type = 'checkbox';
    selectCheckbox.classList.add(
      'discovery-checkbox',
      'discovery-checkbox-appearance'
    );

    DisplayController.appendDiscovery({
      snippetCheckbox: selectCheckbox,
      snippetObject: snippetData,
    });

    discoveryDiv.appendChild(selectCheckbox);

    snippetElement.appendChild(discoveryDiv);
  }

  const headerElement = document.createElement('div');

  //TITLE
  const titleRow = document.createElement('div');
  titleRow.classList.add('row');
  titleRow.classList.add('snippet-title');

  const title = document.createElement('h4');
  title.innerText = snippetData.title;
  const titleCol = document.createElement('div');
  titleCol.classList.add('col');
  titleCol.classList.add('snippet-title');
  titleCol.appendChild(title);

  const langCol = document.createElement('div');
  langCol.classList.add('col');
  langCol.classList.add('col-sm-fixed');
  langCol.classList.add('snippet-title');
  const lang = document.createElement('div'); // TODO make this an img with icon
  lang.classList.add('snippet-title', 'snippet-title-img');
  lang.classList.add(getIcon(snippetData.language));
  langCol.appendChild(lang);

  if (defaultSortingView === SortSnippetsBy.Discover) {
    const seperator = document.createElement('span');
    seperator.classList.add('discovery-seperator');
    seperator.innerText = ' ';
    titleRow.appendChild(seperator);
  }

  titleRow.appendChild(langCol);
  titleRow.appendChild(titleCol);
  headerElement.appendChild(titleRow);

  //DESCRIPTION
  const descRow = document.createElement('div');
  descRow.classList.add('row');
  const descEl = document.createElement('p');
  descEl.classList.add('snippet-description');

  let annotationText = annotationHandler
    .getFavorited(snippetData.annotations ?? [])
    .map((el) => el.text)
    .join('\n');

  if (annotationText.length === 0)
    annotationText =
      annotationHandler
        .sortAnnotationsByUpdated({
          annotations: snippetData.annotations ?? [],
        })[0]
        ?.text.replace(/\n/g, ' ') ?? '';
  descEl.innerText = annotationText;

  descRow.appendChild(descEl);
  headerElement.appendChild(descRow);

  // VIEW CODE

  // Create a button container element
  const viewCodeDiv = document.createElement('div');
  viewCodeDiv.classList.add('row', 'jp-viewcode-container');

  headerElement.appendChild(viewCodeDiv);

  snippetElement.appendChild(headerElement);

  if (isPreview) {
    const previewSnippet = renderSnippet({
      snippetData: snippetData,
      isPreview: isPreview,
      discovery: discovery,
    });
    snippetElement.appendChild(previewSnippet);
    return snippetElement;
  }

  // Create the button element
  const buttonInput = document.createElement('input');
  buttonInput.type = 'checkbox';
  buttonInput.title = 'View expanded code snippet';
  buttonInput.classList.add('jp-viewcode-input');

  viewCodeDiv.appendChild(buttonInput);

  const buttonContentOpen = document.createElement('span');
  buttonContentOpen.innerText = 'View Code ▼';
  buttonContentOpen.classList.add('jp-viewcode-container');

  const buttonContentClosed = document.createElement('span');
  buttonContentClosed.innerText = 'View Code ▶';
  buttonContentClosed.classList.add('jp-viewcode-container');

  if (buttonInput.checked) {
    viewCodeDiv.appendChild(buttonContentOpen);
  } else {
    viewCodeDiv.appendChild(buttonContentClosed);
  }

  let newSnippet: HTMLDivElement;

  if (opened) {
    buttonInput.checked = true;
    newSnippet = renderSnippet({
      snippetData: snippetData,
      isPreview: isPreview,
      discovery: discovery,
    });
    viewCodeDiv.replaceChild(buttonContentOpen, buttonContentClosed);
    snippetElement.appendChild(newSnippet);
  }

  let clickTimer: NodeJS.Timeout | null = null;

  headerElement.addEventListener('click', async function () {
    if (clickTimer === null) {
      clickTimer = setTimeout(function () {
        buttonInput.checked = !buttonInput.checked;
        if (buttonInput.checked) {
          // Checkbox is checked, do something
          newSnippet = renderSnippet({
            snippetData: snippetData,
            isPreview: isPreview,
            discovery: discovery,
          });

          viewCodeDiv.removeChild(buttonContentClosed);
          viewCodeDiv.appendChild(buttonContentOpen);
          snippetElement.appendChild(newSnippet);
        } else {
          // Checkbox is unchecked, do something
          viewCodeDiv.removeChild(buttonContentOpen);
          viewCodeDiv.appendChild(buttonContentClosed);
          snippetElement.removeChild(newSnippet);
        }
        clickTimer = null;
      }, 150); // Adjust the delay (in milliseconds) to define the maximum duration for a single click
    } else {
      clearTimeout(clickTimer);
      clickTimer = null;
      if (defaultSortingView !== SortSnippetsBy.Discover) {
        showExportedSnippet({
          snippetData: snippetData,
        });
      }
    }
  });

  return snippetElement;
};
