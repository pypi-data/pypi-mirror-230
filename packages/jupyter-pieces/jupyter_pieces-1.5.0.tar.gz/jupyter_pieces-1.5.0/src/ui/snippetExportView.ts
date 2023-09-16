import { defaultApp, theme } from '..';
import { Widget } from '@lumino/widgets';
import { MainAreaWidget } from '@jupyterlab/apputils';
import ConnectorSingleton from '../connection/connector_singleton';
import {
  AssetSpecificAssetExportExportTypeEnum,
  AssetSpecificAssetExportRequest,
} from '../PiecesSDK/core';
import { marked } from 'marked';
import { LabIcon } from '@jupyterlab/ui-components';
import { returnedSnippet } from '../models/typedefs';
import { highlightSnippet } from './utils/loadPrism';
import { SegmentAnalytics } from '../analytics/SegmentAnalytics';
import { AnalyticsEnum } from '../analytics/AnalyticsEnum';

export default async function showExportedSnippet({
  snippetData,
}: {
  snippetData: returnedSnippet;
}): Promise<void> {
  SegmentAnalytics.track({
    event: AnalyticsEnum.JUPYTER_SHOW_EXPANDED_VIEW,
  });

  const config = ConnectorSingleton.getInstance();

  const exportWidget = async () => {
    const content = new Widget();

    const params: AssetSpecificAssetExportRequest = {
      asset: snippetData.id,
      exportType: AssetSpecificAssetExportExportTypeEnum.Md,
    };
    const exportedAsset = await config.assetApi.assetSpecificAssetExport(
      params
    );

    content.node.innerHTML = marked(
      exportedAsset.raw.string?.raw ?? '#### Unable to export asset'
    );

    content.node.classList.add('snippet-expand-view');
    const widget = new MainAreaWidget({ content });
    widget.id = `export-${snippetData.id}`;
    widget.title.label = snippetData.title; // TODO Make Dynamic
    widget.title.closable = true;
    widget.title.icon = LabIcon.resolve({
      icon: `jupyter-pieces:${'logo'}`,
    }); // TODO Make Dynamic
    return widget;
  };

  let widget = await exportWidget();

  if (!widget.isAttached) {
    defaultApp.shell.add(widget, 'main');
  }

  defaultApp.shell.activateById(widget.id);

  const snippetContent = document.getElementsByTagName('code');

  for (let i = 0; i < snippetContent.length; i++) {
    const currentElement = snippetContent[i];
    if (currentElement.className.includes('language-')) {
      currentElement.innerHTML = highlightSnippet({
        snippetContent: snippetData.raw,
        snippetLanguage: snippetData.language,
      });
      if (theme === 'false') {
        currentElement.parentElement?.classList.add('snippet-expand-pre-dark');
      } else {
        currentElement.parentElement?.classList.add('snippet-expand-pre-light');
      }
    }
  }
}
