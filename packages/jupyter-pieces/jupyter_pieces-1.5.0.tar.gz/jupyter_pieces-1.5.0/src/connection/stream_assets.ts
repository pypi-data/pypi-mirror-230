import PiecesCacheSingleton from '../cache/pieces_cache';
import { constructSnippet } from '../ui/views/renderListView';
import { loadConnect, processAsset } from './api_wrapper';
import {
  Asset,
  StreamedIdentifiers,
  Assets,
  Annotation,
} from '../PiecesSDK/core';
import DedupeAssetQueue from './DedupeAssetQueue';
import PiecesDatabase from '../database/PiecesDatabase';
import {
  defaultSortingView,
  setDefaultSortingView,
} from '../ui/render/renderSearchBox';
import { SortSnippetsBy } from '../models/SortSnippetsBy';
import DisplayController from '../ui/views/DisplayController';
import QGPTView from '../ui/views/create_gpt_view';
import { SentryTracking } from '../analytics/SentryTracking';
import CheckVersionAndConnection from './checkVersionAndConnection';
import { sleep } from '../utils/sleep';
import ConnectorSingleton from './connector_singleton';
import AnnotationHandler from '../utils/annotationHandler';
import { portNumber } from './connector_singleton';

let identifierWs: WebSocket;
const fetchQueue = new DedupeAssetQueue();
export let streamOpen = false;
let streamClosed = false;
export const waitTimer = 10_000;
export const setStreamOpen = (val: boolean) => {
  streamOpen = val;
};
export const stream = async () => {
  streamIdentifiers();
};

/*
	This establishes a websocket connection with POS
	on each event, we first check if it is a delete
	if it's a delete, remove the asset from UI and cache, then return
	if not, then we fetch the snapshot and formats related to that asset
	we then run checks to see if it is a new asset, or an updated asset,
	and then update ui + cache accordingly.
*/
const streamIdentifiers = async (): Promise<void> => {
  if (streamClosed) return;
  if (streamOpen) {
    return;
  }
  streamOpen = true;
  if (identifierWs?.readyState === identifierWs?.OPEN) {
    identifierWs?.close();
  }

  identifierWs = new WebSocket(
    `ws://localhost:${portNumber}/assets/stream/identifiers`
  );

  identifierWs.onclose = async () => {
    console.log('closed');
    if (!DisplayController.isFetchFailed) {
      DisplayController.setIsFetchFailed(true);
      DisplayController.drawSnippets({});
      QGPTView.redrawGpt();
    }
    await sleep(15_000);
    streamOpen = false;
    CheckVersionAndConnection.run().then(() => {
      streamIdentifiers();
    });
  };

  // update the ui when socket is established
  identifierWs.onopen = () => {
    loadConnect()
      .then(async () => {
        await SentryTracking.update();
      })
      .catch(() => {
        // do nothing
      });
    if (DisplayController.isFetchFailed) {
      DisplayController.setIsFetchFailed(false);
      DisplayController.drawSnippets({});
      QGPTView.redrawGpt();
    }

    PiecesDatabase.clearStaleIds();
  };

  identifierWs.onmessage = async (event) => {
    const cache = PiecesCacheSingleton.getInstance();
    const assets = JSON.parse(event.data) as StreamedIdentifiers;

    for (let i = 0; i < assets.iterable.length; i++) {
      if (assets.iterable[i].deleted) {
        const snippetEl = document.getElementById(
          `snippet-el-${assets.iterable[i].asset!.id}`
        );
        snippetEl?.remove();

        // remove from cache
        delete cache.mappedAssets[assets.iterable[i].asset!.id];
        const indx = cache.assets.findIndex(
          (e) => e.id === assets.iterable[i].asset!.id
        );
        if (indx >= 0) {
          // <-- this check is somewhat redundant but why not be safe
          cache.assets = [
            ...cache.assets.slice(0, indx),
            ...cache.assets.slice(indx + 1),
          ];
          PiecesDatabase.writeDB();
          if (!cache.assets.length) {
            if (defaultSortingView !== SortSnippetsBy.Discover) {
              setDefaultSortingView(SortSnippetsBy.Recent);
            }
            DisplayController.drawSnippets({});
          } else if (defaultSortingView === SortSnippetsBy.Language) {
            langReset();
          }
        }
        continue;
      }

      fetchQueue.push(assets.iterable[i].asset!.id);
    }
  };
};

export const closeStreams = async () => {
  streamClosed = true;
  identifierWs?.close();
};

/*
	Forewarning: somewhat complex
	This receives assets from the fetch queue and updates the dom accordingly
	first make sure to remove the loading / 0 snippet divs
	then update snippet list element(s)
*/
export const renderFetched = async ({ assets }: { assets: Assets }) => {
  const cache = PiecesCacheSingleton.getInstance();
  const loadingDivs = document.querySelectorAll('.loading-div');
  if (defaultSortingView !== SortSnippetsBy.Discover) {
    loadingDivs.forEach((loadingDiv) => {
      loadingDiv.remove();
    });
  }

  const emptyDivs = document.querySelectorAll('.pieces-empty-state');
  emptyDivs.forEach((div) => {
    div.remove();
  });

  const newDivs = document.querySelectorAll('.new-div');
  newDivs.forEach((newDiv) => {
    newDiv.remove();
  });

  if (newDivs.length || loadingDivs.length) {
    const onlyDiv = document.querySelectorAll('.only-snippet');
    onlyDiv.forEach((el) => {
      el.remove();
    });
    // commenting this out because i think it's causing more issues than it solves.
    //await triggerUIRedraw(false, undefined, undefined, false);
  }
  const sortedAssets = cache.assets.sort(
    (a, b) => b.created.getTime() - a.created.getTime()
  );
  const config = ConnectorSingleton.getInstance();
  assets.iterable.forEach(async (element: Asset) => {
    const cachedAsset = cache.mappedAssets[element.id];
    let processed = processAsset({ asset: element });

    const annotationsReqs = Object.keys(element.annotations?.indices ?? {})
      .filter((key) => (element.annotations?.indices ?? {})[key] !== -1)
      .map((annotation) =>
        config.annotationApi.annotationSpecificAnnotationSnapshot({
          annotation,
        })
      );
    const annotations = await Promise.all(annotationsReqs).catch((e) => {
      console.error(e);
      return [] as Annotation[];
    });
    //new asset
    if (!cachedAsset) {
      cache.storeAnnotations(annotations, element.id);
      cache.prependAsset({ asset: element });
      const processed = processAsset({ asset: element });

      // Need to update the Map
      const newMap = cache.snippetMap.get(processed.language);
      // If the language map does not exist, create it
      if (!newMap) {
        cache.snippetMap.set(processed.language, [processed.id]);
      } else {
        newMap.unshift(processed.id);
        cache.snippetMap.set(processed.language, newMap);
      }

      // Map is updated, now update the UI

      if (defaultSortingView === SortSnippetsBy.Recent) {
        const parentEl = document.getElementById(
          'pieces-snippet-container'
        ) as HTMLDivElement;

        const newIndex = sortedAssets.findIndex(
          (asset) => asset.created.getTime() < processed.created.getTime()
        );

        // Create the new element
        const newElement = constructSnippet({ snippetData: processed });

        // Insert the new element at the proper index
        if (newIndex === -1) {
          // If newIndex is -1, it means the new element should be the oldest, so append it.
          parentEl.appendChild(newElement);
        } else {
          // Insert the new element before the element at the newIndex.
          parentEl.insertBefore(newElement, parentEl.children[newIndex - 1]);
        }
      } else if (defaultSortingView === SortSnippetsBy.Language) {
        if (!cache.assets.length) {
          setDefaultSortingView(SortSnippetsBy.Recent);
          DisplayController.drawSnippets({});
        } else if (defaultSortingView === SortSnippetsBy.Language) {
          langReset();
        }
      }
    }

    //updated asset
    else if (
      !AnnotationHandler.getInstance().annotationsAreEqual(
        cachedAsset.annotations,
        annotations
      ) ||
      processed.raw === cachedAsset.raw ||
      processed.title === cachedAsset.title ||
      processed.language === cachedAsset.language ||
      processed.share === cachedAsset.share
    ) {
      cache.storeAnnotations(annotations, element.id);
      processed = processAsset({ asset: element });
      if (processed.language !== cachedAsset.language) {
        // Need to remove the old asset from the map
        const oldMapKeyValues = cache.snippetMap.get(cachedAsset.language);

        oldMapKeyValues?.forEach((value, i) => {
          if (value === processed.id) {
            oldMapKeyValues.splice(i, 1);
            if (oldMapKeyValues.length === 0) {
              cache.snippetMap.delete(cachedAsset.language);
            } else {
              cache.snippetMap.set(cachedAsset.language, oldMapKeyValues);
            }
          }
        });

        const newMapkeyValues = cache.snippetMap.get(processed.language) || [];
        newMapkeyValues.unshift(processed.id);
        cache.snippetMap.set(processed.language, newMapkeyValues);
      }

      // Map is updated, now update the UI

      cache.updateAsset({ asset: element });

      let snippetEl;
      if (defaultSortingView === SortSnippetsBy.Recent) {
        snippetEl = document.getElementById(`snippet-el-${element.id}`);
        const opened = (
          snippetEl?.children[0].lastChild?.firstChild as HTMLInputElement
        )?.checked;
        snippetEl?.replaceWith(
          constructSnippet({
            snippetData: processed,
            isPreview: false,
            opened: opened,
          })
        );
      } else if (defaultSortingView === SortSnippetsBy.Language) {
        if (processed.language === cachedAsset.language) {
          snippetEl = document.getElementById(`snippet-el-${element.id}`);
        } else {
          langReset();
          return;
        }
      }
      if (!snippetEl) return; // we are in a view that does not require rendering.
      const opened = (
        snippetEl?.children[0].lastChild?.firstChild as HTMLInputElement
      )?.checked;
      snippetEl?.replaceWith(
        constructSnippet({
          snippetData: processed,
          isPreview: false,
          opened: opened,
        })
      );
    }
  });
  PiecesDatabase.writeDB();
};

const langReset = async () => {
  const openLangs: string[] = [];
  // Get all open language views
  const langContainers = Array.from(
    document.querySelectorAll('.language-button-input')
  );

  langContainers.forEach((langContainer) => {
    if ((langContainer as HTMLInputElement).checked) {
      openLangs.push(langContainer.id);
    }
  });

  await DisplayController.drawSnippets({});

  openLangs.forEach((langId) => {
    try {
      const snippetContentParent = document.getElementById(
        langId
      ) as HTMLInputElement;
      // there should only be a single parent element found
      snippetContentParent.checked = true;
      const clickEvent = new Event('change');
      snippetContentParent?.dispatchEvent(clickEvent);
    } catch (e) {
      // do nothing
    }
  });
};
