import ConnectorSingleton from '../connection/connector_singleton';
import { launchRuntime } from './launch_runtime';
import Notifications from '../connection/notification_handler';
import PiecesCacheSingleton from '../cache/pieces_cache';
import Constants from '../const';
import { SegmentAnalytics } from '../analytics/SegmentAnalytics';
import { AnalyticsEnum } from '../analytics/AnalyticsEnum';

export default class DeletePiece {
  public static async delete({
    id,
    retry = false,
  }: {
    id: string;
    retry?: boolean;
  }): Promise<void> {
    SegmentAnalytics.track({
      event: AnalyticsEnum.JUPYTER_DELETE,
    });

    const config: ConnectorSingleton = ConnectorSingleton.getInstance();
    const notifications: Notifications = Notifications.getInstance();
    const storage: PiecesCacheSingleton = PiecesCacheSingleton.getInstance();

    try {
      const piece = storage.mappedAssets[id];
      if (!piece) {
        notifications.information({
          message: Constants.SNIPPET_IS_DELETED,
        });
        return;
      }
      await config.assetsApi.assetsDeleteAsset({ asset: id });

      notifications.information({
        message: Constants.SNIPPET_DELETE_SUCCESS,
      });
      SegmentAnalytics.track({
        event: AnalyticsEnum.JUPYTER_DELETE_SUCCESS,
      });
    } catch (error: any) {
      if (error.status === 401 || error.status === 400) {
        if (retry) {
          notifications.error({
            message: Constants.SNIPPET_DELETE_FAILURE,
          });
          SegmentAnalytics.track({
            event: AnalyticsEnum.JUPYTER_DELETE_FAILURE,
          });
        } else {
          try {
            config.context = await config.api.connect({
              seededConnectorConnection: config.seeded,
            });
            return await this.delete({ id, retry: true });
          } catch (e) {
            console.log(`Error from deleting snippet ${e}`);
            SegmentAnalytics.track({
              event: AnalyticsEnum.JUPYTER_DELETE_FAILURE,
            });
          }
        }
      } else {
        if (!retry) {
          if (error.code === 'ECONNREFUSED') {
            // attempt to launch runtime because we could talk to POS.
            await launchRuntime(true);
            config.context = await config.api.connect({
              seededConnectorConnection: config.seeded,
            });
          }
          // then retry our request.
          return await this.delete({ id, retry: true });
        }
        notifications.error({
          message: Constants.SNIPPET_DELETE_FAILURE,
        });
        SegmentAnalytics.track({
          event: AnalyticsEnum.JUPYTER_DELETE_FAILURE,
        });
      }
    }
  }
}
