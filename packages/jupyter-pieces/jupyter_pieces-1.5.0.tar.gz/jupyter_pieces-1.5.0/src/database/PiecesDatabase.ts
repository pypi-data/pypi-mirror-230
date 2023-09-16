import { PLUGIN_ID, defaultApp, defaultState } from '..';
import PiecesCacheSingleton from '../cache/pieces_cache';
import ConnectorSingleton from '../connection/connector_singleton';
import PiecesDB from '../models/database_model';
import { ReadonlyJSONObject } from '@lumino/coreutils';
import DisplayController from '../ui/views/DisplayController';

export default class PiecesDatabase {
  private static writeId: NodeJS.Timeout;
  public static writeDB = () => {
    clearTimeout(PiecesDatabase.writeId);
    const cache = PiecesCacheSingleton.getInstance();
    PiecesDatabase.writeId = setTimeout(async () => {
      defaultApp.restored.then(() => {
        defaultState.save(PLUGIN_ID, {
          assets: cache.assets,
        } as PiecesDB as unknown as ReadonlyJSONObject);
      });
    }, 15_000);
  };

  public static clearStaleIds = async () => {
    const config = ConnectorSingleton.getInstance();
    const cache = PiecesCacheSingleton.getInstance();
    const idSnapshot = await config.assetsApi.assetsIdentifiersSnapshot({pseudo: false});
    const idMap = new Map();
    idSnapshot.iterable?.forEach((identifier) => {
      idMap.set(identifier.id, true);
    });
    // if cache id is not in idsnapshot delete
    const staleIds = Object.keys(cache.mappedAssets).filter((id) => {
      return !idMap.has(id);
    });

    staleIds.forEach((id) => {
      const snippetEl = document.getElementById(`snippet-el-${id}`);
      snippetEl?.remove();
      delete cache.mappedAssets[id];
    });
    cache.assets = Object.values(cache.mappedAssets);
    PiecesDatabase.writeDB();
    if (!cache.assets.length) {
      DisplayController.drawSnippets({});
    }
  };
}
