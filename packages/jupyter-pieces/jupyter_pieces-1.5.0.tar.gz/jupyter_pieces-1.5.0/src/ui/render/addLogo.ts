import { theme } from '../../index';
//Helper function to add the Pieces logo to any given container
export function addLogo(container: HTMLElement) {
  let piecesLogo = document.createElement('div');
  if (theme === 'false') {
    piecesLogo.classList.add('pfd-white');
  } else {
    piecesLogo.classList.add('pfd-black');
  }
  piecesLogo.classList.add('logo-heading', 'load-error-content');
  container.appendChild(piecesLogo);
}
