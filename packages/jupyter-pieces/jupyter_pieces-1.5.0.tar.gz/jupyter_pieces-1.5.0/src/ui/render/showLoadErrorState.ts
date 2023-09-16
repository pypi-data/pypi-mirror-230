import { addLogo } from './addLogo';
import { theme } from '../../index';
import {
  currentMinVersion,
  versionValid,
} from '../../connection/version_check';
import DisplayController from '../views/DisplayController';

export function showLoadErrorState(container: HTMLElement) {
  container.innerHTML = '';
  container.classList.add('load-error-state');

  const holderDiv = document.createElement('div');
  holderDiv.classList.add('load-error-state-holder');
  container.appendChild(holderDiv);

  addLogo(holderDiv);

  let line1 = document.createElement('p');
  line1.classList.add('load-error-content');
  (line1.innerText =
    'Oops! Something went wrong. ' +
    (!versionValid && !DisplayController.isFetchFailed
      ? `Please update Pieces OS to '${currentMinVersion}' or greater to continue using Pieces!`
      : 'Please make sure Pieces OS is installed, updated, and running.')),
    holderDiv.appendChild(line1);

  let installButton = document.createElement('button');
  installButton.classList.add('jp-btn', 'load-error-content');
  installButton.innerText = DisplayController.isFetchFailed
    ? 'Install Platform Core'
    : 'Update Platform Core';
  installButton.addEventListener('click', function () {
    window.open('https://pieces.app/', '_blank');
  });
  holderDiv.appendChild(installButton);
  installButton.title = DisplayController.isFetchFailed
    ? 'Navigate to the Install Platform Core Dependency page'
    : 'Navigate to the Update Platform Core Dependency page';
  !versionValid && !DisplayController.isFetchFailed
    ? (installButton.style.cssText = 'margin-top: 15px;')
    : null;

  if (versionValid || DisplayController.isFetchFailed) {
    let line2 = document.createElement('p');
    line2.classList.add('load-error-content');
    line2.style.textAlign = 'center';
    line2.innerText = 'Or';
    holderDiv.appendChild(line2);

    let launchButton = document.createElement('button');
    launchButton.classList.add('jp-btn', 'load-error-content');
    launchButton.innerText = 'Launch Pieces OS';
    launchButton.addEventListener('click', function () {
      console.log('Launching Pieces OS...');
      window.open('pieces://launch', '_blank');
    });
    holderDiv.appendChild(launchButton);

    let line3 = document.createElement('p');
    line3.classList.add('load-error-content');
    line3.innerHTML = `Please refresh after launching PiecesOS. If the problem persists, please `;
    let underline = document.createElement('u');
    underline.innerText = 'see our FAQ.';
    let link = document.createElement('a');
    link.href = 'https://docs.pieces.app/faq';
    link.target = '_blank';
    link.appendChild(underline);
    line3.appendChild(link);
    holderDiv.appendChild(line3);
  }

  let illustration = document.createElement('div');
  illustration.classList.add('illustration', 'load-error-content');
  if (theme === 'false') {
    illustration.classList.add('illustration-robot-plugging-in-black');
  } else {
    illustration.classList.add('illustration-robot-plugging-in-white');
  }
  holderDiv.appendChild(illustration);
}
