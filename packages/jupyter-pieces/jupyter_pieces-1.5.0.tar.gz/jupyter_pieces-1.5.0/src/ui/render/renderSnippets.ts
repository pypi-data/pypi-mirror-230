import { returnedSnippet } from '../../models/typedefs';
import { highlightSnippet } from './../utils/loadPrism';
import copyToClipboard from './../utils/copyToClipboard';
import Notifications from '../../connection/notification_handler';
import Constants from '../../const';
import ShareableLinksService from '../../connection/shareable_link';
import {
  copyIcon,
  deleteIcon,
  editIcon,
  saveIcon,
  shareIcon,
} from '@jupyterlab/ui-components';
import showExportedSnippet from '../snippetExportView';
import EditModal from '../modals/editModal';
import createAsset from '../../actions/create_asset';
import DeleteModal from '../modals/deleteModal';
import DisplayController from '../views/DisplayController';
import { renderLoading } from '../utils/renderLoading';
import { expandIcon, annotationIcon } from '../LabIcons';
import { AnnotationsModal } from '../modals/EditAnnotationsModal';
import PiecesCacheSingleton from '../../cache/pieces_cache';

const share: ShareableLinksService = ShareableLinksService.getInstance();
const notification: Notifications = Notifications.getInstance();

export function renderSnippet({
  snippetData,
  isPreview,
  discovery,
}: {
  snippetData: returnedSnippet;
  isPreview?: boolean;
  discovery?: boolean;
}): HTMLDivElement {
  const snippet = document.createElement('div');
  snippet.id = `snippet-${snippetData.id}`;
  snippet.classList.add('snippet');

  const snippetDiv = document.createElement('div');
  snippetDiv.classList.add('snippet-parent', 'row');

  snippet.appendChild(snippetDiv);

  if (!isPreview && !discovery) {
    const expandBtn = document.createElement('button');
    expandIcon.element({ container: expandBtn });
    expandBtn.title = 'Expand code snippet';
    expandBtn.classList.add('jp-btn-transparent');
    expandBtn.addEventListener('click', () => {
      showExportedSnippet({
        snippetData: snippetData,
      }).catch(() => {
        notification.error({
          message: 'Failed to expand snippet, are you sure POS is running?',
        });
      });
    });
    snippetDiv.appendChild(expandBtn);
  }

  const lineNumDiv = document.createElement('div');
  lineNumDiv.classList.add('snippet-line-div');
  snippetDiv.appendChild(lineNumDiv);

  const rawCodeDiv = document.createElement('div');
  rawCodeDiv.classList.add('snippet-raw');
  snippetDiv.appendChild(rawCodeDiv);
  const preElement = document.createElement('pre');
  preElement.classList.add('snippet-raw-pre');
  if (isPreview || discovery) {
    preElement.style.marginLeft = '18px';
  }
  rawCodeDiv.appendChild(preElement);

  const seperatedRaw = snippetData.raw.split('\n');

  for (let i = 0; i < seperatedRaw.length; i++) {
    const lineNum = document.createElement('code');
    lineNum.classList.add('snippet-line-nums');
    lineNum.innerText = `${i + 1}`;
    lineNumDiv.appendChild(lineNum);
    const br = document.createElement('br');
    lineNumDiv.appendChild(br);
  }

  preElement.innerHTML = highlightSnippet({
    snippetContent: snippetData.raw,
    snippetLanguage: snippetData.language,
  });

  const snippetFooter = document.createElement('div');
  snippetFooter.classList.add('snippet-footer', 'row');

  //BUTTONS
  const btnRow = document.createElement('div');
  btnRow.id = `btn-${snippetData.id}`;
  btnRow.classList.add('snippet-btn-row');
  snippetFooter.appendChild(btnRow);

  const userBtnDiv = document.createElement('div');
  userBtnDiv.classList.add('snippet-btn-row-user');
  btnRow.appendChild(userBtnDiv);

  const verticalBreak = document.createElement('div');
  verticalBreak.classList.add('vert-break');

  if (isPreview || discovery) {
    //Add a save button
    const saveBtn = document.createElement('button');
    saveBtn.classList.add('jp-btn');
    saveBtn.title = 'Save snippet to Pieces';
    saveIcon.element({ container: saveBtn });
    saveBtn.addEventListener('click', async () => {
      const loading = renderLoading(document);
      userBtnDiv.replaceChild(loading, saveBtn);
      try {
        await createAsset({
          selection: snippetData.raw,
          annotations: snippetData.annotations,
        });
      } catch (e) {
        console.log(e);
      }
      DisplayController.drawSnippets({});
      userBtnDiv.replaceChild(saveBtn, loading);
    });

    userBtnDiv.appendChild(saveBtn);
    userBtnDiv.appendChild(verticalBreak.cloneNode(true));
  }

  const copyBtn = document.createElement('button');
  copyBtn.classList.add('jp-btn');
  copyBtn.title = 'Copy snippet to clipboard';
  copyIcon.element({ container: copyBtn });
  copyBtn.addEventListener('click', async () => {
    await copyToClipboard(snippetData.raw);
    notification.information({
      message: Constants.COPY_SUCCESS,
    });
  });

  userBtnDiv.appendChild(copyBtn);
  userBtnDiv.appendChild(verticalBreak.cloneNode(true));

  if (!isPreview && !discovery) {
    const editBtn = document.createElement('button');
    editBtn.classList.add('jp-btn');
    editBtn.title = 'Edit snippet';
    editIcon.element({ container: editBtn });
    editBtn.addEventListener('click', async () => {
      new EditModal(snippetData).open();
    });
    userBtnDiv.appendChild(editBtn);
    userBtnDiv.appendChild(verticalBreak.cloneNode(true));

    const annotationBtn = document.createElement('button');
    annotationBtn.classList.add('jp-btn');
    annotationBtn.title = 'Edit Annotations';
    annotationBtn.onclick = async () => {
      new AnnotationsModal(
        PiecesCacheSingleton.getInstance().mappedAssets[snippetData.id]
      ).open();
    };
    annotationIcon.element({ container: annotationBtn });

    userBtnDiv.appendChild(annotationBtn);
    userBtnDiv.appendChild(verticalBreak.cloneNode(true));

    // buttonDiv.createEl('div').addClass('vertBreak');
  }

  const shareBtn = document.createElement('button');
  shareBtn.classList.add('jp-btn');
  shareBtn.title = `Copy snippet's shareable link`;
  shareIcon.element({ container: shareBtn });
  shareBtn.addEventListener('click', async () => {
    const loading = renderLoading(document);
    userBtnDiv.replaceChild(loading, shareBtn);
    try {
      if (discovery || isPreview) {
        const id = await createAsset({ selection: snippetData.raw });
        if (typeof id === 'string') {
          const link = await share.generate({ id: id });
          await copyToClipboard(link ?? '');
        }
        DisplayController.drawSnippets({});
      } else {
        const link =
          snippetData.share ??
          (await share.generate({
            id: snippetData.id,
          }));
        await copyToClipboard(link ?? '');

        if (snippetData.share) {
          notification.information({
            message: Constants.LINK_GEN_COPY,
          });
        }
      }
    } catch (e) {
      console.log(e);
    }
    userBtnDiv.replaceChild(shareBtn, loading);
  });
  userBtnDiv.appendChild(shareBtn);

  if (!isPreview && !discovery) {
    //Add a delete button
    const deleteBtn = document.createElement('button');
    deleteBtn.classList.add('jp-btn', 'delete-btn');
    deleteBtn.title = 'Delete snippet';
    deleteIcon.element({ container: deleteBtn });
    deleteBtn.addEventListener('click', async () => {
      new DeleteModal(snippetData.id, snippetData.title).open();
    });

    btnRow.appendChild(deleteBtn);
  }

  snippet.appendChild(snippetFooter);
  return snippet;
}
