import { theme } from '../../index';
import { addLogo } from './addLogo';

export function showLoadingState(container: HTMLElement): HTMLElement {
  const loadingDiv = document.createElement('div');
  loadingDiv.classList.add('loading-state');
  addLogo(loadingDiv);
  let loadingStatement = document.createElement('p');
  loadingStatement.innerText =
    "We haven't found any snippets yet! We're still looking...";

  loadingDiv.appendChild(loadingStatement);

  let illustration = document.createElement('div');
  illustration.classList.add('illustration');
  if (theme === 'false') {
    illustration.classList.add('illustration-cat-fish-bowl-white');
  } else {
    illustration.classList.add('illustration-cat-fish-bowl-black');
  }
  loadingDiv.appendChild(illustration);

  container.innerHTML = '';
  container.appendChild(loadingDiv);

  return loadingDiv;
}
