import {
  QGPTQuestionAnswer,
  QGPTStreamInput,
  QGPTStreamOutputFromJSON,
  RelevantQGPTSeed,
  RelevantQGPTSeeds,
  SeedTypeEnum,
} from '../PiecesSDK/core';
import { marked } from 'marked';
import ConnectorSingleton, { portNumber } from './connector_singleton';
import QGPT from '../actions/qgpt';
import QGPTView from '../ui/views/create_gpt_view';

interface MessageOutput {
  answer: string;
  relevant: RelevantQGPTSeeds;
}

/**
 * Stream controller class for interacting with the QGPT websocket
 */
export default class CopilotStreamController {
  private static instance: CopilotStreamController;

  private hasScrolled = false; // whether or not the user has used their mousewheel

  private ws: WebSocket | null = null; // the qgpt websocket

  private answerEl: HTMLElement | null = null; // the current answer element to be updated from socket events

  // this will resolve the current promise that is created by this.handleMessage
  private messageResolver: null | ((arg0: MessageOutput) => void) = null;

  // this will reject the current promise that is created by this.handleMessage
  private messageRejector: null | ((arg0: any) => void) = null;

  //@TODO implement socket unloading
  private constructor() {
    this.connect();
  }

  /**
   * cleanup function
   */
  public closeSocket() {
    this.ws?.close();
  }

  /**
   * This is the entry point for all chat messages into this socket.
   * @param param0 The inputted user query, any relevant snippets, and the answer element to be updated
   * @returns a promise which is resolved when we get a 'COMPLETED' status from the socket, or rejected on a socket error.
   */
  public async askQGPT({
    query,
    relevant,
    answerEl,
  }: {
    query: string;
    relevant?: string;
    answerEl: HTMLElement;
  }): Promise<{ answer: string; relevant: RelevantQGPTSeeds }> {
    if (!this.ws) this.connect(); // need to connect the socket if it's not established.
    let input: QGPTStreamInput;
    const config = ConnectorSingleton.getInstance();
    const application = config.context.application;

    // we have a relevant snippet inputted, this is the 'ask copilot about...' flow
    if (relevant) {
      input = {
        question: {
          query,
          relevant: {
            iterable: [
              {
                seed: {
                  type: SeedTypeEnum.Asset,
                  asset: {
                    application,
                    format: {
                      fragment: {
                        string: {
                          raw: relevant,
                        },
                      },
                    },
                  },
                },
              },
            ],
          },
        },
      };
    } else {
      input = {
        relevance: {
          query,
          seeds: {
            iterable: [],
          },
          options: {
            question: true,
            database: true,
          },
        },
      };
      await QGPT.appendRelevantSeeds(input.relevance!.seeds!.iterable!);
    }

    return this.handleMessages({ input, answerEl });
  }

  /**
   * Connects the websocket, handles all message callbacks, error handling, and rendering.
   */
  private connect() {
    this.ws = new WebSocket(`ws://localhost:${portNumber}/qgpt/stream`);

    let totalMessage = '';
    let relevantSnippets: RelevantQGPTSeed[] = [];

    this.ws.onmessage = (msg) => {
      const json = JSON.parse(msg.data);
      const result = QGPTStreamOutputFromJSON(json);
      let answer: QGPTQuestionAnswer | undefined;
      let relevant: RelevantQGPTSeeds | undefined;

      // we got something from /relevance
      if (result.relevance) {
        relevant = result.relevance.relevant;
      } else {
        relevant = { iterable: [] };
      }

      // there is relevant snippets from the socket
      if (relevant) {
        for (const el of relevant.iterable) {
          relevantSnippets.push(el);
        }
      }

      // we got something from /question
      if (result.question) {
        answer = result.question.answers.iterable[0];
      } else {
        // the message is complete, or we do nothing
        if (result.status === 'COMPLETED') {
          // add the buttons to the answer element's code blocks.
          QGPTView.buildCodeButtons(
            Array.from(this.answerEl?.querySelectorAll('pre > code') ?? [])
          );
          if (!totalMessage) {
            this.answerEl!.innerHTML =
              "I'm sorry, it seems I don't have any relevant context to that question. Please try again 😃";
          }
          // resolve the 'handleMessage' promise
          this.messageResolver!({
            answer: totalMessage,
            relevant: { iterable: relevantSnippets },
          });
          // cleanup
          totalMessage = '';
          relevantSnippets = [];
        }
        return;
      }
      // add to the total message
      if (answer?.text) {
        totalMessage += answer.text;
      }
      // render the new total message
      this.handleRender(totalMessage, this.answerEl!);
      // if the container is scrollable, scroll it to the bottom if user has not used mouse wheel
      if (
        this.answerEl!.parentElement!.parentElement!.scrollHeight >
        this.answerEl!.parentElement!.parentElement!.clientHeight
      ) {
        this.forceScroll(this.answerEl!);
      }
    };
    // on error, regect the 'handleMessage' promise, and close the socket.
    this.ws.onerror = (error) => {
      console.error(error);
      totalMessage = '';
      relevantSnippets = [];
      if (this.messageRejector) this.messageRejector(error);
      this.ws = null;
    };
  }

  /**
   *
   * @param param0 the input into the websocket, and the answer element to be updated.
   * @returns a promise that is resolved when the chat is complete, or rejected on an error.
   */
  private handleMessages({
    input,
    answerEl,
  }: {
    input: QGPTStreamInput;
    answerEl: HTMLElement;
  }) {
    this.answerEl = answerEl;

    // scroll the container to the bottom
    answerEl!.parentElement!.parentElement!.scrollTop =
      answerEl!.parentElement!.parentElement!.scrollHeight;

    //create loader
    const loader = document.createElement('div');
    loader.classList.add('flex', 'flex-row', 'justify-center');
    loader.appendChild(QGPTView.createLoader());
    answerEl.parentElement!.insertAdjacentElement('afterend', loader);

    // init message promise
    const promise = new Promise<MessageOutput>((res, rej) => {
      this.messageResolver = res;
      this.messageRejector = rej;
    });
    promise.finally(() => {
      loader.remove();
    });
    try {
      this.ws!.send(JSON.stringify(input));
    } catch (err) {
      console.error('err', err);
      this.messageRejector?.(err);
    }

    return promise;
  }

  /**
   * This converts our raw markdown into HTML, then syntax highlights the pre > code blocks, then renders the result.
   * @param totalMessage The total message to rendre
   * @param answerEl the answer element to update
   */
  private handleRender(totalMessage: string, answerEl: HTMLElement) {
    const htmlString = marked.parse(totalMessage, {
      headerIds: false,
      mangle: false,
    });
    const div = document.createElement('div');
    div.classList.add('gpt-text-response', 'gpt-response', 'gpt-col');
    div.innerHTML = htmlString;
    QGPTView.highlightCodeBlocks(
      Array.from(div.querySelectorAll('pre > code'))
    );

    answerEl.innerHTML = div.innerHTML;
  }

  /**
   * If the user has not used their mousewheel, scroll their container to the bottom.
   * @param answerEl The answer element that is being updated
   * @returns void
   */
  private forceScroll(answerEl: HTMLElement) {
    // only keep the bottom until the user uses mouse wheel
    if (this.hasScrolled) {
      return;
    }
    answerEl.parentElement!.parentElement!.onwheel = () => {
      this.hasScrolled = true;
    };

    answerEl.parentElement!.parentElement!.scrollTop =
      answerEl.parentElement!.parentElement!.scrollHeight;
  }

  public static getInstance() {
    return (CopilotStreamController.instance ??= new CopilotStreamController());
  }
}
