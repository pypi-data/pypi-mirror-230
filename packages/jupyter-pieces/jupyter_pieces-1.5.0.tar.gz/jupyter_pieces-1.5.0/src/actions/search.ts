import ConnectorSingleton from '../connection/connector_singleton';
import PiecesCacheSingleton from '../cache/pieces_cache';
import { returnedSnippet } from '../models/typedefs';
import Constants from '../const';
import { SearchedAssets } from '../PiecesSDK/core';
import { PromiseResolution } from '../utils/PromiseResolution';
import Notifications from '../connection/notification_handler';
import { AnalyticsEnum } from '../analytics/AnalyticsEnum';
import { SegmentAnalytics } from '../analytics/SegmentAnalytics';
import { shuffleAndReinsert } from '../utils/shuffleAndReinsert';

export default class Search {
  private static config: ConnectorSingleton = ConnectorSingleton.getInstance();
  //const notifications: Notifications = Notifications.getInstance()
  private static notifications: Notifications = Notifications.getInstance();

  // TODO for randy to convert this to a singleton, or a class with a static variable for the searching promis resolution.
  private static searching:
    | {
        resolution: {
          resolver: (args: SearchedAssets) => void | SearchedAssets;
          rejector: (args: SearchedAssets) => void | SearchedAssets;
          promise: Promise<SearchedAssets>;
        };
        query: string;
      }
    | undefined;

  public static search = async ({
    query,
  }: {
    query: string;
  }): Promise<returnedSnippet[]> => {
    const storage: PiecesCacheSingleton = PiecesCacheSingleton.getInstance();
    // TODO think about rapid behavior, ie if this gets called many times do we want to reject the current search or wait until it is done?
    SegmentAnalytics.track({
      event: AnalyticsEnum.JUPYTER_SEARCH,
    });

    try {
      // if we havent defined our resolver then define one.
      if (this.searching) {
        // here one is already defined, so we have options here.
        // option 1: we can reject the current search and start a new one.
        // option 2: we can wait untill the current search is done and then start a new one.
        // ans: go with option 1;
        this.searching.resolution.rejector({
          iterable: [],
          suggested: 0,
          exact: 0,
        });
      }

      // reset the searching object, no matter what.
      this.searching = {
        query,
        resolution: PromiseResolution<SearchedAssets>(),
      };

      // declare a global searchingResolver. (PromiseResolution)
      // this is gonna give 3 things.
      // (1) a promise: This will be used to conrol execution of this search.
      // (2) a resolver: this will NEED to get called when the search completes and it is a success
      // (3) a rejector: this will need to get called when (1) there is an error in the search, or (2) if we want to cancel the search.

      // call this sync, this is super important.
      this.config.assetsApi
        .assetsSearchAssets({
          query: query,
          transferables: false,
        })
        .then((response) => {
          if (!this.searching) {
            return response;
          }
          this.searching.resolution.resolver(response);
        })
        .catch((e) => {
          if (!this.searching) {
            return { iterable: [], suggested: 0, exact: 0 };
          }

          this.searching.resolution.rejector({
            iterable: [],
            suggested: 0,
            exact: 0,
          });
        });

      // we are going to indefinetly untill the promise is compkleted in some way shape or form.
      // TODO veify that the parent catch gets fired when we reject the search.
      const results: SearchedAssets | undefined = await this.searching
        ?.resolution.promise;

      // once we are completely done searching, just ensure that we rest our promise resolution.
      this.searching = undefined;

      const assets = storage.assets;
      const returnedResults = [];

      let found_asset;
      for (const asset of results?.iterable ?? []) {
        found_asset = undefined;
        found_asset = assets.find((e) => e.id === asset.identifier);
        if (found_asset) {
          returnedResults.push(found_asset);
        }
      }

      if (returnedResults.length < 5 && returnedResults.length != 0) {
        // Try Neural Code Search
        this.searching = {
          query,
          resolution: PromiseResolution<SearchedAssets>(),
        };

        // Neural Code Search
        this.config.searchApi
          .neuralCodeSearch({
            query: query,
          })
          .then((response) => {
            if (!this.searching) {
              return response;
            }
            this.searching.resolution.resolver(response);
          })
          .catch((e) => {
            if (!this.searching) {
              return { iterable: [], suggested: 0, exact: 0 };
            }

            this.searching.resolution.rejector({
              iterable: [],
              suggested: 0,
              exact: 0,
            });
          });

        // we are going to search indefinetly until the promise is completed in some way shape or form.
        // TODO veify that the parent catch gets fired when we reject the search.
        const results: SearchedAssets = await this.searching.resolution.promise;
        this.searching = undefined;

        for (const asset of results.iterable) {
          found_asset = undefined;
          found_asset = storage.assets.find((e) => e.id === asset.identifier);
          if (found_asset && !returnedResults.includes(found_asset)) {
            returnedResults.push(found_asset);
          }
        }
      }

      const snippets = returnedResults;
      this.notifications.information({
        message: `Search for '${query}' found ${snippets.length} result(s).`,
      });

      SegmentAnalytics.track({
        event: AnalyticsEnum.JUPYTER_SEARCH_SUCCESS,
      });

      return shuffleAndReinsert(snippets); // Lol, for Tsavo
    } catch (error) {
      // once we are completely done searching, just ensure that we rest our promise resolution.(even if it fails.)
      this.searching = undefined;

      const snippets = storage.assets;
      this.notifications.error({ message: Constants.SEARCH_FAILURE });

      SegmentAnalytics.track({
        event: AnalyticsEnum.JUPYTER_SEARCH_FAILURE,
      });

      return snippets;
    }
  };
}
