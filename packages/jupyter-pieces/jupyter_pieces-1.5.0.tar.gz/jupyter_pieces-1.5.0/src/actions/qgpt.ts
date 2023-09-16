import ConnectorSingleton from '../connection/connector_singleton';
import {
  QGPTConversationMessage,
  QGPTQuestionAnswer,
  RelevanceRequest,
  RelevantQGPTSeeds,
  Seed,
  SeededFile,
  SeededFragment,
  SeedTypeEnum,
} from '../PiecesSDK/core';
import langExtToClassificationSpecificEnum from '../ui/utils/langExtToClassificationSpecificEnum';
import { defaultApp } from '..';
import { Contents } from '@jupyterlab/services';
import { SegmentAnalytics } from '../analytics/SegmentAnalytics';
import { AnalyticsEnum } from '../analytics/AnalyticsEnum';
import { sha256 } from '../utils/sha256';
import NoteBookFetcher from './NoteBookFetcher';

export default class QGPT {
  private constructor() {}

  private static qGPTSeedToFile: Map<string, string> = new Map<
    string,
    string
  >();
  private static UNIQUE_ID_SUBSTR_LEN = 40;
  private static qGPTSeedCache: Array<Contents.IModel> = [];
  private static notebookFetcher = NoteBookFetcher.getInstance();

  public static getSeedPath(seed: Seed) {
    return this.qGPTSeedToFile.get(
      sha256(
        seed.asset?.format?.fragment?.string?.raw!.substring(
          this.UNIQUE_ID_SUBSTR_LEN
        )!
      )
    );
  }

  static appendRelevantSeeds = async (relevant: Seed[]) => {
    const config = ConnectorSingleton.getInstance();
    const allNotebooks = [
      ...this.qGPTSeedCache,
      ...(await this.notebookFetcher.getNotebooks()),
    ];
    this.qGPTSeedCache = allNotebooks;
    for (let i = 0; i < allNotebooks.length; i++) {
      const cells = allNotebooks[i].content.cells;
      for (let j = 0; j < cells.length; j++) {
        if (!(cells[j].cell_type === 'code')) {
          continue;
        }
        const raw = cells[j].source;
        if (!raw) {
          continue;
        }
        const lang =
          //@ts-ignore 'kernelPreference' is not available from the ts api given by jupyterlab, however it does exist if the user has a notebook open
          // this is okay because we fallback to python if kernelPreference is undefined
          defaultApp.shell.currentWidget?.sessionContext?.kernelPreference
            ?.language ?? 'py';

        let currentSeed: Seed = {
          type: SeedTypeEnum.Asset,
        };

        this.qGPTSeedToFile.set(
          sha256(raw.substring(this.UNIQUE_ID_SUBSTR_LEN)),
          allNotebooks[i].path
        );

        let seed: SeededFile | SeededFragment = {
          string: {
            raw: raw,
          },
          metadata: {
            ext: langExtToClassificationSpecificEnum(lang),
          },
        };

        currentSeed.asset = {
          application: config.context.application,
          format: {
            fragment: seed,
          },
        };

        relevant.push(currentSeed);
      }
    }
  };

  /*
    Loads in the context from all the notebooks
    updates the mapping to relate a seed to a file
    sends request to /relevance question: true
*/
  public static askQGPT = async ({ query }: { query: string }) => {
    SegmentAnalytics.track({
      event: AnalyticsEnum.JUPYTER_AI_ASSISTANT_QUESTION_ASKED,
    });

    const config = ConnectorSingleton.getInstance();

    const relevanceParams: RelevanceRequest = {
      qGPTRelevanceInput: {
        query,
        seeds: {
          iterable: [],
        },
        options: {
          question: true,
        },
      },
    };

    this.appendRelevantSeeds(
      relevanceParams.qGPTRelevanceInput!.seeds!.iterable
    );

    SegmentAnalytics.track({
      event: AnalyticsEnum.JUPYTER_AI_ASSISTANT_QUESTION_SUCCESS,
    });

    return {
      result: await config.QGPTApi.relevance(relevanceParams),
      query: query,
    };
  };

  public static async askQuestion({
    query,
    code,
  }: {
    query: string;
    code: string;
  }) {
    const config = ConnectorSingleton.getInstance();
    const params = {
      query,
      relevant: {
        iterable: [
          {
            seed: {
              type: SeedTypeEnum.Asset,
              asset: {
                application: config.context.application,
                format: {
                  fragment: {
                    string: {
                      raw: code,
                    },
                  },
                },
              },
            },
          },
        ],
      },
    };
    const result = await config.QGPTApi.question({ qGPTQuestionInput: params });
    return { result, query };
  }

  /*
    Generates a question to then pass to gpt
*/
  public static reprompt = async ({
    conversation,
    query,
  }: {
    conversation: QGPTConversationMessage[];
    query: string;
  }) => {
    SegmentAnalytics.track({
      event: AnalyticsEnum.JUPYTER_AI_ASSISTANT_REPROMPT,
    });

    const reversedConv = conversation.reverse();
    const config = ConnectorSingleton.getInstance();
    const repromptRes = await config.QGPTApi.reprompt({
      qGPTRepromptInput: {
        query: query,
        conversation: {
          iterable: reversedConv,
        },
      },
    });
    return this.askQGPT({ query: repromptRes.query });
  };
  /*
    Calls the hints api to generate hints based on the conversation
  */
  public static hints = async ({
    relevant,
    answer,
    query,
  }: {
    relevant: RelevantQGPTSeeds;
    answer?: QGPTQuestionAnswer;
    query?: string;
  }) => {
    const config = ConnectorSingleton.getInstance();

    return config.QGPTApi.hints({
      qGPTHintsInput: {
        relevant,
        answer,
        query,
      },
    });
  };
}
