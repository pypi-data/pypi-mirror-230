import { Notification } from '@jupyterlab/apputils';
import * as Sentry from '@sentry/browser';

export default class Notifications {
  private static instance: Notifications;

  private constructor() {
    /* */
  }

  public static getInstance(): Notifications {
    if (!Notifications.instance) {
      Notifications.instance = new Notifications();
    }

    return Notifications.instance;
  }

  public information({ message }: { message: string }) {
    Notification.info(message, {
      autoClose: 3000,
    });
  }

  public error({
    message,
    sendToSentry,
  }: {
    message: string;
    sendToSentry?: boolean;
  }) {
    Notification.error(message, {
      autoClose: 3000,
    });

    if (sendToSentry) {
      Sentry.captureException(message);
    }
  }
}
