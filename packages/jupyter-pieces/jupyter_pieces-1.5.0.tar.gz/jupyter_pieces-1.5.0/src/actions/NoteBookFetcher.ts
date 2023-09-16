import { Contents, ContentsManager } from '@jupyterlab/services';

export default class NoteBookFetcher {
  private static instance: NoteBookFetcher; // singleton instance
  private contentsManager = new ContentsManager(); // jupyterlab contents manager
  private MAX_FETCH: number = 400; // sets an upper limit on number of fetches
  private MAX_BYTES: number = 10000000; // only let 10 mb of notebooks be fetched
  private notebookContents: Array<Promise<Contents.IModel>> = []; // array of promises to fetch notebook contents
  private contentsFetching: Array<Promise<void>> = []; // array of promises to help fetch notebook contents
  private notebooks: Array<Contents.IModel> = []; // array of all the notebooks
  private lastFetch: Date | undefined; // last time we fetched notebooks
  private totalBytes: number = 0; // total number of bytes fetched
  private totalFetches: number = 0; // total number of fetches
  private fileLastModified: Map<string, string> = new Map<string, string>();

  private constructor() {}

  public static getInstance(): NoteBookFetcher {
    if (!NoteBookFetcher.instance) {
      NoteBookFetcher.instance = new NoteBookFetcher();
    }
    return NoteBookFetcher.instance;
  }

  /*
    This function will either return the cached notebooks inside a time limit or fetch all the notebooks
    - returns a promise array of all the notebooks
  */
  public async getNotebooks() {
    if (new Date().getTime() - (this.lastFetch?.getTime() ?? 0) > 900000) {
      this.lastFetch = new Date();
      return this.getAllNotebooks();
    } else {
      return this.notebooks;
    }
  }

  /*
    This function will recursively get all the notebook files starting at '/' aka the directory jupyterlab was initialized from
    - returns a promise array of all the notebooks
    - ONLY call this manually or on launch
  */
  public async getAllNotebooks(): Promise<Contents.IModel[]> {
    try {
      await this.findNotebooks(this.contentsManager.get('/'));
      await Promise.all(this.contentsFetching);
      this.notebooks = await Promise.all(this.notebookContents);
      this.totalBytes = this.totalFetches = 0;
      return this.notebooks;
    } catch (e) {
      console.log(e);
    }
    this.totalBytes = this.totalFetches = 0;
    return [];
  }

  // helper to get contents of a file, detect if it's a notebook or not, and fetch recursively or not according
  private async findNotebooks(file: Promise<Contents.IModel>) {
    // don't fetch more than 400 files or 10 mb
    if (
      this.totalFetches >= this.MAX_FETCH ||
      this.totalBytes >= this.MAX_BYTES
    )
      return;

    // get the file contents
    const fileContent = await file;

    // dont fetch a file if we already have it cached and it hasn't been modified
    if (
      this.fileLastModified.get(fileContent.path) &&
      this.fileLastModified.get(fileContent.path) === fileContent.last_modified
    ) {
      return;
    }

    this.fileLastModified.set(fileContent.path, fileContent.last_modified);

    // the current file is a notebook
    if (fileContent.type === 'notebook') {
      if (this.totalBytes < this.MAX_BYTES) {
        this.notebookContents.push(
          this.contentsManager.get(fileContent.path, { content: true })
        );
      }
      this.totalFetches++;
      this.totalBytes += fileContent.size ?? 0;
      // current file is a directory
    } else if (fileContent.type === 'directory') {
      for (let i = 0; i < fileContent.content.length; i++) {
        if (
          this.totalFetches >= this.MAX_FETCH ||
          this.totalBytes >= this.MAX_BYTES
        ) {
          return;
        }
        this.totalFetches++;
        this.contentsFetching.push(
          this.findNotebooks(
            this.contentsManager.get(fileContent.content[i].path)
          )
        );
      }
    }
  }
}
