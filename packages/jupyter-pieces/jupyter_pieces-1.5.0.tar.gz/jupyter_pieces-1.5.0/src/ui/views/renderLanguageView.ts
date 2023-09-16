import { returnedSnippet } from '../../models/typedefs';
import { getIcon } from './../utils/langExtToIcon';
import { getRangeOfChanges } from '../utils/getRangeOfChanges';
import { renderListView } from './renderListView';
import langExtToReadable from '../utils/langExtToReadable';
import PiecesCacheSingleton from '../../cache/pieces_cache';
import { searchLangSpecificEnum } from '../utils/searcLangSpecificEnum';

export function renderLanguageView({
  container,
  snippets,
}: {
  container: HTMLDivElement;
  snippets: returnedSnippet[];
}): void {
  const cache = PiecesCacheSingleton.getInstance();
  const languageContainer = document.createElement('div');
  languageContainer.classList.add('language-container');
  languageContainer.id = 'language-snippet-container';

  const ranges = getRangeOfChanges(snippets);

  ranges.forEach(([start, end]) => {
    const snippetsInRange = snippets.slice(start, end + 1);

    const langView = document.createElement('div');
    langView.classList.add('language-view', 'col');
    langView.id = `code-view-${langExtToReadable(
      snippetsInRange[0].language
    )})`;
    languageContainer.appendChild(langView);

    const titleDiv = document.createElement('div');
    titleDiv.classList.add('language-title-div', 'row');

    const langCol = document.createElement('div');
    langCol.classList.add('language-title', 'col-sm-fixed');

    const langImg = document.createElement('div'); // TODO make this an img with icon
    langImg.classList.add('language-title', 'language-title-img');
    langImg.classList.add(getIcon(snippetsInRange[0].language));
    langCol.appendChild(langImg);

    const langTitleCol = document.createElement('div');
    langTitleCol.classList.add('col');
    const langTitle = document.createElement('h1');
    langTitle.innerText = langExtToReadable(snippetsInRange[0].language);
    langTitleCol.appendChild(langTitle);
    langTitle.classList.add('language-title-div');

    // Create the button element
    const buttonInput = document.createElement('input');
    buttonInput.type = 'checkbox';
    buttonInput.title = `Expand '${langExtToReadable(
      snippetsInRange[0].language
    )}' language view`;
    buttonInput.classList.add('language-button-input');

    buttonInput.id = `input-${
      searchLangSpecificEnum[snippetsInRange[0].language]
    }`;

    titleDiv.appendChild(langCol);
    titleDiv.appendChild(langTitleCol);
    titleDiv.appendChild(buttonInput);
    langView.appendChild(titleDiv);

    const buttonContentOpen = document.createElement('span');
    buttonContentOpen.innerText = '▼';

    const buttonContentClosed = document.createElement('span');
    buttonContentClosed.innerText = '▶';

    if (buttonInput.checked) {
      titleDiv.appendChild(buttonContentOpen);
    } else {
      titleDiv.appendChild(buttonContentClosed);
    }

    let snippetDiv = document.createElement('div');
    // snippetDiv.classList.add('col');

    // @ts-ignore
    let clickTimer = null;
    buttonInput.addEventListener('change', function () {
      // @ts-ignore
      if (buttonInput.checked) {
        // Checkbox is checked, do something
        snippetsInRange.forEach((snippet) => {
          snippet = cache.mappedAssets[snippet.id];
        });
        renderListView({
          container: snippetDiv,
          snippets: snippetsInRange.sort(
            (a, b) => b.created.getTime() - a.created.getTime()
          ),
        });
        langView.appendChild(snippetDiv);
        titleDiv.replaceChild(buttonContentOpen, buttonContentClosed);
      } else {
        // Checkbox is unchecked, do something
        langView.removeChild(snippetDiv);
        snippetDiv = document.createElement('div');
        titleDiv.replaceChild(buttonContentClosed, buttonContentOpen);
      }
    });
  });
  container.appendChild(languageContainer);
}
