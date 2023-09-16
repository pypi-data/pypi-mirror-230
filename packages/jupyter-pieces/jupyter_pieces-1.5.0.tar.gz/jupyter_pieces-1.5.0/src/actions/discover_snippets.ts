import {
  Annotation,
  DiscoveryDiscoverAssetsRequest,
  SeededDiscoverableAsset,
  SeededFile,
  SeededFragment,
} from '../PiecesSDK/core';
import ConnectorSingleton from '../connection/connector_singleton';
import Notifications from '../connection/notification_handler';
import Constants from '../const';
import { SegmentAnalytics } from '../analytics/SegmentAnalytics';
import { AnalyticsEnum } from '../analytics/AnalyticsEnum';
import PiecesCacheSingleton from '../cache/pieces_cache';
import { draft_asset } from './draft_asset';
import langExtToClassificationSpecificEnum from '../ui/utils/langExtToClassificationSpecificEnum';
import { returnedSnippet } from '../models/typedefs';
import { ClassificationSpecificEnum } from '../PiecesSDK/connector';
import { defaultSortingView } from '../ui/render/renderSearchBox';
import { SortSnippetsBy } from '../models/SortSnippetsBy';
import { v4 as uuidv4 } from 'uuid';
import DisplayController from '../ui/views/DisplayController';
import { renderListView } from '../ui/views/renderListView';
import { defaultApp } from '../index';
import { sleep } from '../utils/sleep';
import { Contents } from '@jupyterlab/services';
import NoteBookFetcher from './NoteBookFetcher';
import { CodeBlock } from '../models/CodeBlock';

export default class Discovery {
  static discovery_loaded = false;
  private static notifications = Notifications.getInstance();
  private static config = ConnectorSingleton.getInstance();
  private static notebookFetcher = NoteBookFetcher.getInstance();
  private static allNotebooks: Contents.IModel[] = [];

  static async discoverAllSnippets() {
    const cache = PiecesCacheSingleton.getInstance();
    this.discovery_loaded = false;
    this.allNotebooks = await this.notebookFetcher.getAllNotebooks();
    if (!this.allNotebooks.length) {
      this.notifications.error({ message: Constants.DISCOVERY_FAILURE });
      this.discovery_loaded = true;
      return;
    }
    const snippetDivs = document.querySelectorAll('.piecesSnippet');
    snippetDivs.forEach((snippetDiv) => {
      snippetDiv.remove();
    });
    DisplayController.clearDiscovery();
    cache.discoveredSnippets = [];
    for (let i = 0; i < this.allNotebooks.length; i++) {
      const cells = this.allNotebooks[i].content.cells;
      for (let j = 0; j < cells.length; j++) {
        if (!(cells[j].cell_type === 'code')) {
          continue;
        }
        const raw = cells[j].source;
        if (!raw) {
          continue;
        }
        const lang =
          //@ts-ignore 'kernelPreference' is not available from the ts api given by jupyterlab, however it does exist if the user has a notebook open
          // this is okay because we fallback to python if kernelPreference is undefined
          defaultApp.shell.currentWidget?.sessionContext?.kernelPreference
            ?.language ?? 'py';

        await this.populateDiscoveredSnippet({ code: raw, lang: lang });
      }
    }
    this.notifications.information({
      message: Constants.DISCOVERY_SUCCESS,
    });
    this.discovery_loaded = true;
  }

  static async discoverSnippets(params: DiscoveryDiscoverAssetsRequest) {
    SegmentAnalytics.track({
      event: AnalyticsEnum.JUPYTER_SNIPPET_DISCOVERY,
    });

    try {
      const result = await this.config.DiscoveryApi.discoveryDiscoverAssets(
        params
      );

      if (result.iterable.length === 0) {
        this.notifications.error({
          message: `Something went wrong, we weren't able to find any snippets to discover`,
        });
        return result;
      }

      this.notifications.information({
        message:
          Constants.DISCOVERY_SUCCESS +
          ` ${result.iterable.length} snippets saved to Pieces!`,
      });
      SegmentAnalytics.track({
        event: AnalyticsEnum.JUPYTER_SNIPPET_DISCOVERY_SUCCESS,
      });
      return result;
    } catch (e) {
      this.notifications.error({ message: Constants.DISCOVERY_FAILURE });
      SegmentAnalytics.track({
        event: AnalyticsEnum.JUPYTER_SNIPPET_DISCOVERY_FAILURE,
      });
    }
  }

  private static async populateDiscoveredSnippet(
    codeBlock: CodeBlock
  ): Promise<void> {
    const cache = PiecesCacheSingleton.getInstance();
    const discoverable: SeededDiscoverableAsset = {};

    const seed: SeededFile | SeededFragment = {
      string: {
        raw: codeBlock.code,
      },
      metadata: {
        ext: langExtToClassificationSpecificEnum(codeBlock.lang),
      },
    };

    // if code cell is 50 lines or longer then upload it as a file so it gets 'snippetized'
    if (codeBlock.code.split('\n').length > 50) {
      discoverable.file = seed;
    } else {
      discoverable.fragment = seed;
    }

    if (!discoverable) {
      this.notifications.error({
        message: "Something went wrong, we weren't able to discover a snippet",
      });
      return;
    }

    const params: DiscoveryDiscoverAssetsRequest = {
      automatic: false,
      seededDiscoverableAssets: {
        application: this.config.context.application.id,
        iterable: [discoverable],
      },
    };

    const discovery_result =
      await this.config.DiscoveryApi.discoveryDiscoverAssets(params);

    let _text: string;
    if (
      discovery_result.iterable[0] === undefined ||
      !discovery_result.iterable[0].fragment?.string?.raw
    ) {
      return;
    } else {
      _text = discovery_result.iterable[0].fragment?.string?.raw as string;
    }
    const draft_res = await draft_asset({
      text: _text,
    });

    const snippetObject: returnedSnippet = {
      id: uuidv4(),
      title: draft_res.asset?.metadata?.name ?? 'Unknown Title',
      raw:
        discoverable.fragment?.string?.raw ??
        discoverable.file?.string?.raw ??
        'unable to unpack snippet',
      created: new Date(),
      updated: new Date(),
      language:
        discoverable.file?.metadata?.ext ??
        discoverable.fragment?.metadata?.ext ??
        ClassificationSpecificEnum.Ts,
      annotations:
        draft_res.asset?.metadata?.annotations?.map((el) => {
          const ret = {
            type: el.type,
            text: el.text,
            id: uuidv4(),
            updated: {
              value: new Date(),
            },
            created: {
              value: new Date(),
            },
          } as Annotation;
          if (el.asset) {
            ret.asset = {
              id: el.asset,
            };
          }
          return ret;
        }) ?? [],
      type: draft_res.asset?.format.classification?.specific ?? 'Unknown type',
      time: new Date().toISOString(),
      share: undefined,
    };

    cache.discoveredSnippets.push(snippetObject);

    if (
      defaultSortingView === SortSnippetsBy.Discover &&
      cache.discoveredSnippets.length !== 0
    ) {
      if (cache.discoveredSnippets.length === 1) {
        const loadingDivs = document.querySelectorAll('.loading-state');
        loadingDivs.forEach((loadingDiv) => {
          loadingDiv.remove();
        });
      }
      renderListView({
        container: DisplayController.containerDiv,
        snippets: [snippetObject],
        discovery: true,
      });
    }
    if (cache.discoveredSnippets.length < 5) {
      await sleep(1_000);
    } else {
      await sleep(8_000);
    }
  }
}
