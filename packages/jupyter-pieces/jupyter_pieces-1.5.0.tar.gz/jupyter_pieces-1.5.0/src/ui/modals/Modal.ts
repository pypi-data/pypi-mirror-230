export default abstract class Modal {
  protected containerEl: HTMLElement;
  protected contentEl: HTMLElement;
  protected titleEl: HTMLElement;
  private modalParent: HTMLElement;
  private modalBackground: HTMLElement;

  constructor() {
    //ROOT DIV
    const main = document.getElementById('main');

    // MODAL CONTAINER
    const modalContainer = document.createElement('div');
    this.containerEl = modalContainer;
    modalContainer.classList.add('edit-modal-container');

    // MODAL BACKGROUND
    const modalBackground = document.createElement('div');
    modalBackground.classList.add('edit-modal-background');
    this.modalBackground = modalBackground;

    //MODAL PARENT(S)
    const modalParent = document.createElement('div');
    this.modalParent = modalParent;
    modalParent.classList.add('edit-modal');

    //CLOSE BUTTON
    const modalCloseButtonDiv = document.createElement('div');
    modalCloseButtonDiv.classList.add('edit-modal-close-button');
    modalParent.appendChild(modalCloseButtonDiv);

    const closeBtn = document.createElement('span');
    closeBtn.innerHTML = '&times;';
    modalCloseButtonDiv.appendChild(closeBtn);

    // MODAL CONTENT
    const modalContent = document.createElement('div');
    this.contentEl = modalContent;
    modalContent.classList.add('edit-modal-content');
    modalParent.appendChild(modalContent);

    // MODAL HEADER
    const modalHeader = document.createElement('div');
    modalHeader.classList.add('row', 'edit-modal-header');
    modalContent.appendChild(modalHeader);
    this.titleEl = modalHeader;

    //APPEND MODAL TO ROOT
    modalContainer.appendChild(modalBackground);
    modalContainer.appendChild(modalParent);
    main!.appendChild(modalContainer);

    //MODAL CLOSE HANDLERS

    closeBtn.addEventListener('click', () => {
      this.close();
    });
  }

  protected abstract onOpen(): void;

  protected abstract onClose(): void;

  private handleWindowHide = (event: any) => {
    if (
      event.target !== this.modalParent &&
      event.target === this.modalBackground
    ) {
      window.removeEventListener('click', this.handleWindowHide);
      this.containerEl.classList.add('!hidden');
    }
  };

  hide(): void {
    this.containerEl.classList.add('!hidden');
  }

  open(): void {
    window.addEventListener('click', this.handleWindowHide);
    this.containerEl.classList.remove('!hidden');
    this.onOpen();
  }

  close(): void {
    this.onClose();
    window.removeEventListener('click', this.handleWindowHide);
    this.containerEl.classList.add('!hidden');
  }
}
