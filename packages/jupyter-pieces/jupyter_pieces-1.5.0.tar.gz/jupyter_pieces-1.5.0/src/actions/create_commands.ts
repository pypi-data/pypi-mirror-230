import { CodeCell } from '@jupyterlab/cells';
import { ICommandPalette } from '@jupyterlab/apputils';
import createAsset from './create_asset';
import {
  AnnotationTypeEnum,
  DiscoveryDiscoverAssetsRequest,
  FullTextSearchRequest,
  SeededFile,
} from '../PiecesSDK/core';
import { SeededDiscoverableAsset } from '../PiecesSDK/common';
import ConnectorSingleton from '../connection/connector_singleton';
import Constants from '../const';
import { loadPieces } from '../connection/api_wrapper';
import PiecesCacheSingleton from '../cache/pieces_cache';
import Notifications from '../connection/notification_handler';
import ShareableLinksService from '../connection/shareable_link';
import copyToClipboard from '../ui/utils/copyToClipboard';
import { showOnboarding } from '../onboarding/showOnboarding';
import Discovery from './discover_snippets';
import langExtToClassificationSpecificEnum from '../ui/utils/langExtToClassificationSpecificEnum';
import { SeededFragment } from '../PiecesSDK/connector';
import { defaultApp } from '../index';
import { getStored } from '../localStorageManager';
import { SegmentAnalytics } from '../analytics/SegmentAnalytics';
import { AnalyticsEnum } from '../analytics/AnalyticsEnum';
import { draft_asset } from './draft_asset';
import { searchBox } from '../ui/render/renderSearchBox';
import { refreshSnippets } from '../ui/utils/refreshSnippets';
import DisplayController from '../ui/views/DisplayController';
import { returnedSnippet } from '../models/typedefs';
import { calculateLevenshteinDistance } from '../utils/calculateLevenshteinDistance';
import { truncateAfterNewline } from '../utils/truncateAfterNewline';
import { v4 as uuidv4 } from 'uuid';
import AskQGPTModal from '../ui/modals/AskQGPTModal';

export const createCommands = ({ palette }: { palette: ICommandPalette }) => {
  const { commands } = defaultApp;

  // Enrich Selection
  const enrich_selection_command = 'jupyter-pieces:enrich-selection';
  commands.addCommand(enrich_selection_command, {
    label: 'Enrich Selection via Pieces',
    caption: 'Add a description to your selection',
    execute: enrichSelection,
  });
  defaultApp.contextMenu.addItem({
    command: enrich_selection_command,
    selector: '.jp-Cell',
    rank: 101,
  });

  // Snippetize notebook
  const snippetize_command = 'jupyter-pieces:discover-snippets';
  commands.addCommand(snippetize_command, {
    label: 'Discover Snippets',
    caption: 'Save all Snippets in your Notebook to Pieces',
    execute: snippetizeNotebook,
  });
  palette.addItem({
    command: snippetize_command,
    category: 'Pieces for Developers',
  });

  // Onboarding command
  const onboarding_command = 'jupyter-pieces:open-onboarding';
  commands.addCommand(onboarding_command, {
    label: 'Pieces for Developers Onboarding',
    execute: showOnboarding,
  });
  palette.addItem({
    command: onboarding_command,
    category: 'Pieces for Developers',
  });

  // save active cell to pieces command
  const save_active_cell_command = 'jupyter-pieces:save-cell-to-pieces';
  commands.addCommand(save_active_cell_command, {
    label: 'Save Active Cell to Pieces',
    caption: 'Save the Active Cell to Pieces',
    execute: saveActiveCellToPieces,
  });
  defaultApp.contextMenu.addItem({
    command: save_active_cell_command,
    selector: '.jp-Cell',
    rank: 100,
  });

  const share_active_cell_command = 'jupyter-pieces:share-cell-via-pieces';
  commands.addCommand(share_active_cell_command, {
    label: 'Share Active Cell via Pieces',
    caption: 'Share the Active Cell via Pieces',
    execute: shareActiveCellViaPieces,
  });
  defaultApp.contextMenu.addItem({
    command: share_active_cell_command,
    selector: '.jp-Cell',
    rank: 100,
  });

  // save selection to pieces command
  const save_selection_to_pieces_command =
    'jupyter-pieces:save-selection-to-pieces';
  commands.addCommand(save_selection_to_pieces_command, {
    label: 'Save Selection to Pieces',
    caption: 'Save your Selection to Pieces',
    execute: saveSelectionToPieces,
  });
  defaultApp.contextMenu.addItem({
    command: save_selection_to_pieces_command,
    selector: '*',
    rank: 100,
  });

  const share_selection_via_pieces_command =
    'jupyter-pieces:share-selection-via-pieces';
  commands.addCommand(share_selection_via_pieces_command, {
    label: 'Share Selection via Pieces',
    caption: 'Share your Selection via Pieces',
    execute: shareSelectionViaPieces,
  });
  defaultApp.contextMenu.addItem({
    command: share_selection_via_pieces_command,
    selector: '*',
    rank: 100,
  });

  // Ask QGPT about selectin
  const askCopilotCommand = 'jupyter-pieces:ask-copilot-about-selection';
  commands.addCommand(askCopilotCommand, {
    label: 'Ask Pieces about your selection',
    caption: 'Ask Pieces Copilot a question about your selected text',
    execute: () => {
      const selection = document.getSelection();
      if (!selection) {   
        Notifications.getInstance().error({
          message: 'Please select some text to ask our Copilot about!',
        });
        return;
      }
      new AskQGPTModal(selection.toString()).open();
    },
  });
  defaultApp.contextMenu.addItem({
    command: askCopilotCommand,
    selector: '*',
    rank: 101,
  });

  // Right-click menu
  commands.addCommand('text-shortcuts:save-selection-to-pieces', {
    label: 'Save Selection to Pieces',
    execute: saveSelectionToPieces,
  });
  commands.addCommand('text-shortcuts:share-selection-via-pieces', {
    label: 'Share Selection via Pieces',
    execute: shareSelectionViaPieces,
  });
  commands.addCommand('text-shortcuts:save-cell-to-pieces', {
    label: 'Save Active Cell to Pieces',
    execute: saveActiveCellToPieces,
  });
  commands.addCommand('text-shortcuts:share-cell-via-pieces', {
    label: 'Share Active Cell via Pieces',
    execute: shareActiveCellViaPieces,
  });

  // Refresh pieces - right click
  const refresh_snippets_command = 'text-shortcuts:refresh-snippets';
  commands.addCommand(refresh_snippets_command, {
    label: 'Refresh Snippets',
    execute: refreshPieces,
  });

  // Jump to searchbar of Pieces - keyboard command
  const quick_search_command = 'text-shortcuts:quick-search';
  commands.addCommand(quick_search_command, {
    label: 'Quick Search',
    execute: quickSearch,
  });

  // Toggle Pieces view - keyboard command
  const toggle_view_command = 'text-shortcuts:toggle-view';
  commands.addCommand(toggle_view_command, {
    label: 'Toggle View',
    execute: toggleView,
  });

  // Toggle Pieces view - keyboard command
  const snippetize_discover_command = 'text-shortcuts:discover-snippets';
  commands.addCommand(snippetize_discover_command, {
    label: 'Discover Snippets in Your Notebook',
    execute: snippetizeNotebook,
  });
};

const enrichSelection = async () => {
  const notifications: Notifications = Notifications.getInstance();
  const selection = document.getSelection();
  if (!selection || selection.toString().length < 5) {
    notifications.error({ message: Constants.NO_SAVE_SELECTION });
    return;
  }

  const draft_seed = await draft_asset({ text: selection.toString() });

  //@ts-ignore this does not exist in the api given by jupyterlab, however editor does exist if they have a notebook open.
  const editor = defaultApp.shell.currentWidget?.content.activeCell.editor;
  if (!editor || editor === undefined) {
    notifications.error({
      message: 'Unable to detect editor, cannot enrich.',
    });
    return;
  }

  // Define the text you want to insert
  const textToInsert = `'''\n${
    draft_seed.asset?.metadata?.annotations
      ?.map((annotation) => annotation.text)
      .join('\n') ?? ''
  }\n'''\n`;

  editor.replaceSelection(textToInsert + selection);

  // Move the cursor to the end of the inserted text
};

let inSnippetize = false;
const snippetizeNotebook = async () => {
  const notifications: Notifications = Notifications.getInstance();
  const config: ConnectorSingleton = ConnectorSingleton.getInstance();
  if (inSnippetize) {
    notifications.error({
      message: 'We are already snippetizing your notebook! Just wait a bit.',
    });
    return;
  }
  inSnippetize = true;
  notifications.information({
    message: 'We are snippetizing your notebook! Sit tight!',
  });

  try {
    //@ts-ignore
    const cells = defaultApp.shell.currentWidget?.content?.cellsArray;
    if (!cells) {
      notifications.error({ message: Constants.DISCOVERY_FAILURE });
      return;
    }
    const discoverableAssets: DiscoveryDiscoverAssetsRequest = {
      automatic: true,
      seededDiscoverableAssets: {
        application: config.context.application.id,
        iterable: [],
      },
    };

    for (let i = 0; i < cells.length; i++) {
      if (!(cells[i] instanceof CodeCell)) {
        continue;
      }
      const raw = cells[i].model.toJSON().source;
      if (!raw) {
        continue;
      }
      const lang =
        //@ts-ignore
        defaultApp.shell.currentWidget?.sessionContext?.kernelPreference
          ?.language;

      let discoverable: SeededDiscoverableAsset = {};

      let seed: SeededFile | SeededFragment = {
        string: {
          raw: raw,
        },
        metadata: {
          ext: langExtToClassificationSpecificEnum(lang),
        },
      };

      // if code cell is 50 lines or longer then upload it as a file so it gets 'snippetized'
      if (raw.split('\n').length > 50) {
        discoverable.file = seed;
      } else {
        discoverable.fragment = seed;
      }

      discoverableAssets.seededDiscoverableAssets?.iterable.push(discoverable);
    }
    if (!discoverableAssets.seededDiscoverableAssets?.iterable.length) {
      notifications.error({
        message:
          "Something went wrong, we weren't able to find any snippets to discover",
      });
      return;
    }
    const returnedResults = await Discovery.discoverSnippets(
      discoverableAssets
    );
    loadPieces().then(() => {
      DisplayController.drawSnippets({});
    });
    if (getStored('AutoOpen') && returnedResults?.iterable.length !== 0) {
      defaultApp.shell.activateById('piecesView');
    }
  } catch (e) {
    notifications.error({
      message:
        'Failed to snippetize notebook, are you sure Pieces OS is installed, running, and up to date?',
    });
  }

  inSnippetize = false;
};

const refreshPieces = () => {
  SegmentAnalytics.track({
    event: AnalyticsEnum.JUPYTER_REFRESH_HOTKEY,
  });

  refreshSnippets();
};

const quickSearch = () => {
  SegmentAnalytics.track({
    event: AnalyticsEnum.JUPYTER_QUICK_SEARCH_HOTKEY,
  });

  defaultApp.shell.activateById('piecesView');
  searchBox.focus();
};

const toggleView = () => {
  SegmentAnalytics.track({
    event: AnalyticsEnum.JUPYTER_TOGGLE_VIEW_HOTKEY,
  });

  let newSelection =
    (DisplayController.sortDropdown.firstChild as HTMLSelectElement)
      .selectedIndex + 1;
  if (
    newSelection >=
    (DisplayController.sortDropdown.firstChild as HTMLSelectElement).options
      .length
  )
    newSelection = 0; //Wrap back to 0

  (
    DisplayController.sortDropdown.firstChild as HTMLSelectElement
  ).selectedIndex = newSelection;
};

export const saveActiveCellToPieces = async () => {
  const notifications: Notifications = Notifications.getInstance();
  SegmentAnalytics.track({
    event: AnalyticsEnum.JUPYTER_SAVE_ACTIVE_CELL,
  });

  // TODO very sad can't use typescript lsp magic D:
  //@ts-ignore
  const activeCell = defaultApp.shell.currentWidget?.content.activeCell;
  //@ts-ignore
  const cells = defaultApp.shell.currentWidget?.content?.cellsArray;
  //@ts-ignore
  const notebookName = defaultApp.shell.currentPath ?? 'unknown';
  let cellNum;

  if (!activeCell) {
    notifications.error({ message: Constants.NO_ACTIVE_CELL });
    return;
  } else if (!(activeCell instanceof CodeCell)) {
    notifications.error({ message: Constants.NO_CODE_CELL });
    return;
  }

  for (let i = 0; i < cells.length; i++) {
    if (cells[i] === activeCell) {
      cellNum = i;
      break;
    }
  }

  const code = activeCell.model.toJSON().source;
  if (code.length < 5) {
    notifications.error({
      message: 'There is no code saved in this cell!',
    });
    return;
  }
  try {
    const { similarity } = await findSimilarity(code);
    if (similarity < 2) {
      notifications.information({ message: Constants.SAVE_EXISTS });
    } else {
      await createAsset({
        selection: code as string,
        annotations: [
          {
            text: `This snippet came from cell ${
              (cellNum ?? -1) + 1
            } of ${notebookName}`,
            type: AnnotationTypeEnum.Description,
            id: uuidv4(),
            created: {
              value: new Date(),
            },
            updated: {
              value: new Date(),
            },
          },
        ],
      });
      DisplayController.drawSnippets({});
    }
  } catch (e) {
    notifications.error({
      message:
        'Failed to save snippet to pieces, are you sure that Pieces OS is running?',
    });
  }
  if (getStored('AutoOpen')) {
    defaultApp.shell.activateById('piecesView');
  }
};

export const saveSelectionToPieces = async () => {
  const notifications: Notifications = Notifications.getInstance();
  SegmentAnalytics.track({
    event: AnalyticsEnum.JUPYTER_SAVE_SELECTION,
  });

  const selection = document.getSelection();
  //@ts-ignore
  const filename = defaultApp.shell.currentPath ?? 'unknown';
  if (!selection || selection.toString().length < 5) {
    notifications.error({ message: Constants.NO_SAVE_SELECTION });
    return;
  }
  try {
    await createAsset({
      selection: selection.toString(),
      annotations: [
        {
          text: `This snippet was saved via selection from ${filename}`,
          type: AnnotationTypeEnum.Description,
          id: uuidv4(),
          created: {
            value: new Date(),
          },
          updated: {
            value: new Date(),
          },
        },
      ],
    });
  } catch (e) {
    notifications.error({
      message:
        'Failed to save selection to Pieces. Are you sure Pieces OS is running?',
    });
  }
  DisplayController.drawSnippets({});
  if (getStored('AutoOpen')) {
    defaultApp.shell.activateById('piecesView');
  }
};

export const shareSelectionViaPieces = async () => {
  const notifications: Notifications = Notifications.getInstance();
  const linkService: ShareableLinksService =
    ShareableLinksService.getInstance();
  const cache: PiecesCacheSingleton = PiecesCacheSingleton.getInstance();
  SegmentAnalytics.track({
    event: AnalyticsEnum.JUPYTER_SHARE_SELECTION,
  });

  const selection = document.getSelection();
  if (!selection || selection.toString().length < 5) {
    notifications.error({ message: Constants.NO_SAVE_SELECTION });
    return;
  }

  try {
    const { similarity, comparisonID } = await findSimilarity(
      selection.toString()
    );
    if (similarity < 2) {
      if (typeof comparisonID === 'string') {
        const existingLink = cache.mappedAssets[comparisonID].share;
        const link =
          existingLink ??
          (await linkService.generate({
            id: comparisonID,
          }));
        copyToClipboard(link || '');
        if (existingLink) {
          notifications.information({
            message: Constants.LINK_GEN_COPY,
          });
        }
      }
    } else {
      await saveAndShare(selection.toString());
      DisplayController.drawSnippets({});
    }
  } catch (e) {
    notifications.error({
      message:
        'Failed to share selection via pieces, are you sure Pieces OS is running?',
    });
  }
};

export const shareActiveCellViaPieces = async () => {
  const notifications: Notifications = Notifications.getInstance();
  const linkService: ShareableLinksService =
    ShareableLinksService.getInstance();
  // TODO very sad can't use typescript lsp magic D:
  //@ts-ignore
  const activeCell = defaultApp.shell.currentWidget?.content.activeCell;
  //@ts-ignore
  const cells = defaultApp.shell.currentWidget?.content?.cellsArray;
  //@ts-ignore
  const notebookName = defaultApp.shell.currentPath ?? 'unknown';

  if (!activeCell) {
    notifications.error({ message: Constants.NO_ACTIVE_CELL });
    return;
  } else if (!(activeCell instanceof CodeCell)) {
    notifications.error({ message: Constants.NO_CODE_CELL });
    return;
  }

  let cellNum;
  for (let i = 0; i < cells.length; i++) {
    if (cells[i] === activeCell) {
      cellNum = i;
      break;
    }
  }

  const code = activeCell.model.toJSON().source;
  const { similarity, comparisonID } = await findSimilarity(code);

  if (similarity < 2) {
    if (typeof comparisonID === 'string') {
      const link = await linkService.generate({
        id: comparisonID,
      });
      copyToClipboard(link || '');
    }
  } else {
    const id = await createAsset({
      selection: code as string,
      annotations: [
        {
          text: `This snippet came from cell ${
            (cellNum ?? -1) + 1
          } of ${notebookName}`,
          type: AnnotationTypeEnum.Description,
          id: uuidv4(),
          created: {
            value: new Date(),
          },
          updated: {
            value: new Date(),
          },
        },
      ],
    });
    const link = await linkService.generate({
      id: id!,
    });
    copyToClipboard(link || '');
  }
  DisplayController.drawSnippets({});
};

/*
Handler for editor menu -> share snippet
    - creates a snippet
    - generates a link
    - copies to clipboard
*/
async function saveAndShare(selection: string) {
  const linkService: ShareableLinksService =
    ShareableLinksService.getInstance();
  const id = await createAsset({ selection: selection });
  if (typeof id === 'string') {
    const link = await linkService.generate({ id: id });
    copyToClipboard(link || '');
  }
}

export async function findSimilarity(
  codeBlock: string | string[]
): Promise<{ similarity: number; comparisonID: string }> {
  const config: ConnectorSingleton = ConnectorSingleton.getInstance();
  const cache: PiecesCacheSingleton = PiecesCacheSingleton.getInstance();
  let comparisonScore = Infinity;
  let comparisonID = '';
  const rawCode: FullTextSearchRequest = {
    query: truncateAfterNewline(codeBlock),
  };

  const result = config.searchApi.fullTextSearch(rawCode);

  const assetArray: returnedSnippet[] = [];

  await result.then(
    async (res: { iterable: { identifier: string | number }[] }) => {
      res.iterable.forEach((element: { identifier: string | number }) => {
        assetArray.push(cache.mappedAssets[element.identifier]);
      });
      const returnedSnippets = assetArray;

      returnedSnippets.forEach((element) => {
        try {
          // TODO: Make sure that `element.raw` is always going to be a string
          const currentCompScore = calculateLevenshteinDistance(
            codeBlock,
            element.raw as string
          );

          if (currentCompScore < comparisonScore) {
            comparisonScore = currentCompScore; // Update the current low number if the condition is true
            comparisonID = element.id;
          }
        } catch {
          console.log('Error in calculating similarity score');
        }
      });
    }
  );
  return { similarity: comparisonScore, comparisonID: comparisonID };
}
