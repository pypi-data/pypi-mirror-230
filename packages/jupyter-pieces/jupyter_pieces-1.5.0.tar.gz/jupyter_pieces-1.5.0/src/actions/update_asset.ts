import ConnectorSingleton from '../connection/connector_singleton';
import {
  AssetReclassification,
  AssetReclassifyRequest,
  ClassificationGenericEnum,
  Format,
} from '../PiecesSDK/core';
import { ClassificationSpecificEnum } from '../PiecesSDK/connector';
import { Asset } from '../PiecesSDK/common/models/Asset';
import Notifications from '../connection/notification_handler';
import Constants from '../const';
import { SegmentAnalytics } from '../analytics/SegmentAnalytics';
import { AnalyticsEnum } from '../analytics/AnalyticsEnum';

const config = ConnectorSingleton.getInstance();
const notifications = Notifications.getInstance();

export const reclassify = async ({
  asset,
  ext,
}: {
  asset: Asset;
  ext: ClassificationSpecificEnum;
}): Promise<Asset | void> => {
  try {
    const isImage =
      asset.original.reference?.classification.generic ===
      ClassificationGenericEnum.Image;
    let ret = asset;
    if (isImage) {
      const ocrId = asset.original.reference?.analysis?.image?.ocr?.raw.id;

      if (!ocrId) {
        // we don't have an ocrId somehow
        console.log('No OCRId Available');
        return asset;
      }

      const format = asset.formats.iterable?.find(
        (format) => format.id === ocrId
      );

      if (!format) {
        // we don't have a format somehow
        console.log('Failed to find the format on an asset');
        return asset;
      }

      format.file = undefined;
      format.fragment = undefined;

      await config.formatApi.formatReclassify({
        formatReclassification: {
          ext: ext,
          format: format,
        },
      });
      ret = await config.assetApi.assetSnapshot({
        asset: asset.id,
        transferables: true,
      });
    } else {
      const reclassification: AssetReclassification = {
        asset: asset,
        ext: ext,
      };
      const params: AssetReclassifyRequest = {
        assetReclassification: reclassification,
        transferables: false,
      };
      ret = await config.assetApi.assetReclassify(params);
    }

    notifications.information({ message: Constants.RECLASSIFY_SUCCESS });
    return ret;
  } catch (error) {
    console.error(error);
    notifications.error({ message: Constants.RECLASSIFY_FAILURE });
    return;
  }
};

export const update = async ({
  asset,
}: {
  asset: Asset;
}): Promise<Asset | void> => {
  SegmentAnalytics.track({
    event: AnalyticsEnum.JUPYTER_EDIT_SNIPPET,
  });

  try {
    const ret: Asset = await config.assetApi.assetUpdate({ asset: asset });
    notifications.information({ message: Constants.UPDATE_SUCCESS });

    SegmentAnalytics.track({
      event: AnalyticsEnum.JUPYTER_EDIT_SNIPPET_SUCCESS,
    });

    return ret;
  } catch (error) {
    // console.error(error);

    SegmentAnalytics.track({
      event: AnalyticsEnum.JUPYTER_EDIT_SNIPPET_FAILURE,
    });

    notifications.error({ message: Constants.UPDATE_FAILURE });
    return;
  }
};

export const updateFormat = async ({ format }: { format: Format }) => {
  try {
    const ret = await config.formatApi.formatUpdateValue({ format: format });
    notifications.information({ message: Constants.UPDATE_CODE_SUCCESS });
    return ret;
  } catch (error) {
    console.error(error);
    notifications.error({ message: Constants.UPDATE_CODE_FAILURE });
    return;
  }
};
