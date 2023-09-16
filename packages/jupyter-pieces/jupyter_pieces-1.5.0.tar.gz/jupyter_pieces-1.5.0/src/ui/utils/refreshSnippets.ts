import { renderLoading } from './renderLoading';
import { loadPieces } from '../../connection/api_wrapper';
import DisplayController from '../views/DisplayController';
import { searchBtn } from '../render/renderSearchBox';

export const refreshSnippets = async () => {
  const loading = renderLoading(document, 'refresh-');

  if (searchBtn.parentElement)
    searchBtn.parentElement!.replaceChild(loading, searchBtn);

  try {
    await loadPieces();
    DisplayController.drawSnippets({});
  } catch (e) {
    console.log(e);
  }
  if (loading.parentElement)
    loading.parentElement!.replaceChild(searchBtn, loading);
};
