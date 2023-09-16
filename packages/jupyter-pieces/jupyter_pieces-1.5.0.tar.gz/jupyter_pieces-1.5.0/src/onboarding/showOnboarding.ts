import { MainAreaWidget } from '@jupyterlab/apputils';
import { defaultApp } from '..';
import { Widget } from '@lumino/widgets';
import { marked } from 'marked';
import { onboardingMD } from './pieces-onboarding';
import { LabIcon } from '@jupyterlab/ui-components';
import { SegmentAnalytics } from '../analytics/SegmentAnalytics';
import { AnalyticsEnum } from '../analytics/AnalyticsEnum';

// import Constants from '../const';

export async function openNewTabWithContent(
  title: string,
  htmlContent: HTMLElement
): Promise<void> {
  const content = new Widget();

  content.node.appendChild(htmlContent);

  const widget = new MainAreaWidget({ content });

  // Customize the widget properties if needed
  widget.title.icon = LabIcon.resolve({ icon: 'jupyter-pieces:logo' });
  widget.title.label = title;
  widget.title.closable = true;

  // Add the widget to the main area
  defaultApp.shell.add(widget, 'main');

  // Activate the new tab
  defaultApp.shell.activateById(widget.id);
}

export function showOnboarding() {
  SegmentAnalytics.track({
    event: AnalyticsEnum.JUPYTER_USER_ONBOARDED,
  });

  let onboardingHTML = marked(onboardingMD);

  let container = document.createElement('div');
  container.classList.add('pieces-onboarding');

  let mainArea = document.createElement('div');
  mainArea.classList.add('main');
  mainArea.innerHTML = onboardingHTML;
  container.append(mainArea);

  openNewTabWithContent('Welcome to Pieces', container);
}
