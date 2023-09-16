import DeletePiece from '../../actions/delete';
import Modal from './Modal';

export default class DeleteModal extends Modal {
  snippetId: string;
  snippetTitle: string;

  constructor(snippetId: string, snippetTitle: string) {
    super();
    this.snippetId = snippetId;
    this.snippetTitle = snippetTitle;
  }

  protected onOpen(): void {
    //TITLE PARENT
    const modalTitleDiv = document.createElement('div');
    modalTitleDiv.classList.add('row');
    this.contentEl.appendChild(modalTitleDiv);

    //TITLE LABEL
    const titleCol = document.createElement('div');
    titleCol.classList.add('col');

    const titleLabelRow = document.createElement('div');
    titleLabelRow.classList.add('row');
    titleCol.appendChild(titleLabelRow);
    const titleLabel = document.createElement('span');
    titleLabel.classList.add('delete-modal-label');
    titleLabel.innerText = `Are you sure you want to delete '${this.snippetTitle}'?`;
    titleLabelRow.appendChild(titleLabel);

    modalTitleDiv.appendChild(titleCol);

    //SAVE BUTTON
    const btnRow = document.createElement('div');
    btnRow.classList.add('row', 'delete-desc-row');
    const saveBtn = document.createElement('button');
    saveBtn.classList.add('jp-btn', 'delete-del-btn');

    saveBtn.addEventListener('click', () => {
      deleteHandler(this.snippetId);
      this.containerEl.remove();
    });

    saveBtn.innerText = 'Delete';
    saveBtn.title = 'Delete piece';
    btnRow.appendChild(saveBtn);
    this.contentEl.appendChild(btnRow);
  }
  protected onClose(): void {}
}

async function deleteHandler(snippetId: string): Promise<void> {
  try {
    await DeletePiece.delete({ id: snippetId });
    const snippetEl = document.getElementById(`snippet-el-${snippetId}`);
    snippetEl?.remove();
  } catch (error) {
    console.log(error);
  }
}
