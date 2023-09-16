import {
  ApplicationNameEnum,
  CapabilitiesEnum,
  Configuration,
  ConfigurationParameters,
  ConnectorApi,
  Context,
  PlatformEnum,
  SeededConnectorConnection,
  SeededConnectorTracking,
  SeededTrackedApplication,
  TrackRequest,
} from '../PiecesSDK/connector';
import {
  AllocationsApi,
  ApplicationApi,
  AssetApi,
  AssetsApi,
  Configuration as CoreConfig,
  FormatApi,
  LinkifyApi,
  SearchApi,
  OSApi,
  UserApi,
  WellKnownApi,
  DiscoveryApi,
  QGPTApi,
  AnnotationApi,
  AnnotationsApi,
} from '../PiecesSDK/core';
import Notifications from './notification_handler';
import Constants from '../const';
import { getStored } from '../localStorageManager';

export const portNumber = getStored('Port')
  ? getStored('Port')
  : process.platform == 'linux'
  ? 5323
  : 1000;

export default class ConnectorSingleton {
  private static instance: ConnectorSingleton;
  private _platform = process.platform;
  private _platformMap: { [key: string]: PlatformEnum } = {
    win32: PlatformEnum.Windows,
    darwin: PlatformEnum.Macos,
    linux: PlatformEnum.Linux,
  };

  private constructor() {}

  public parameters: ConfigurationParameters = {
    basePath: `http://localhost:${portNumber}`,
    fetchApi: fetch,
  };

  public context!: Context;
  public configuration: Configuration = new Configuration(this.parameters);
  public api: ConnectorApi = new ConnectorApi(this.configuration);

  public searchApi = new SearchApi(
    new CoreConfig({ fetchApi: fetch, basePath: this.parameters.basePath })
  );
  public allocationsApi = new AllocationsApi(
    new CoreConfig({ fetchApi: fetch, basePath: this.parameters.basePath })
  );
  public applicationApi = new ApplicationApi(
    new CoreConfig({ fetchApi: fetch, basePath: this.parameters.basePath })
  );
  public linkifyApi = new LinkifyApi(
    new CoreConfig({ fetchApi: fetch, basePath: this.parameters.basePath })
  );
  public assetsApi = new AssetsApi(
    new CoreConfig({ fetchApi: fetch, basePath: this.parameters.basePath })
  );
  public DiscoveryApi = new DiscoveryApi(
    new CoreConfig({ fetchApi: fetch, basePath: this.parameters.basePath })
  );
  public formatApi = new FormatApi(
    new CoreConfig({ fetchApi: fetch, basePath: this.parameters.basePath })
  );
  public userApi = new UserApi(
    new CoreConfig({ fetchApi: fetch, basePath: this.parameters.basePath })
  );
  public osApi = new OSApi(
    new CoreConfig({ fetchApi: fetch, basePath: this.parameters.basePath })
  );
  public assetApi = new AssetApi(
    new CoreConfig({ fetchApi: fetch, basePath: this.parameters.basePath })
  );
  public wellKnownApi = new WellKnownApi(
    new CoreConfig({ fetchApi: fetch, basePath: this.parameters.basePath })
  );
  public QGPTApi = new QGPTApi(
    new CoreConfig({ fetchApi: fetch, basePath: this.parameters.basePath })
  );
  public annotationsApi = new AnnotationsApi(
    new CoreConfig({ fetchApi: fetch, basePath: this.parameters.basePath })
  );
  public annotationApi = new AnnotationApi(
    new CoreConfig({ fetchApi: fetch, basePath: this.parameters.basePath })
  );

  public application: SeededTrackedApplication = {
    name: ApplicationNameEnum.JupyterHub,
    version: Constants.PLUGIN_VERSION,
    platform: this._platformMap[this._platform] || PlatformEnum.Unknown,
    capabilities: getStored('Capabilities')
      ? getStored('Capabilities')
      : CapabilitiesEnum.Blended,
  };

  public seeded: SeededConnectorConnection = {
    application: this.application,
  };

  public static getInstance(): ConnectorSingleton {
    if (!ConnectorSingleton.instance) {
      ConnectorSingleton.instance = new ConnectorSingleton();
    }

    return ConnectorSingleton.instance;
  }

  public static async checkConnection({
    notification = true,
  }: {
    notification?: boolean;
  }): Promise<boolean> {
    try {
      await fetch(`http://localhost:${portNumber}/.well-known/health`);
      return true;
    } catch (e) {
      const notifications = Notifications.getInstance();
      // if notification is set to false we will ignore and just return false.
      if (notification) {
        notifications.information({
          message: Constants.CORE_PLATFORM_MSG,
        });
      }
      return false;
    }
  }

  public async track(event: SeededConnectorTracking): Promise<boolean> {
    const { context, api } = this;

    if (!context) {
      throw new Error('Application context could not be found when calling');
    }

    const seededConnectorTracking: SeededConnectorTracking = { ...event };

    const seed: TrackRequest = {
      application: context.application.id,
      seededConnectorTracking,
    };
    return api
      .track(seed)
      .then((_) => true)
      .catch((error) => {
        // TODO send this to sentry. and extract the actual error from the error.(ie error.message)
        console.log(`Error from api.track Error: ${error}`);
        return false;
      });
  }
}
