import { theme } from '../../index';

export function getIcon(language: string): string {
  switch (language) {
    case 'bat':
      language = theme === 'false' ? 'batchfile-img-w' : 'batchfile-img-b';
      break;
    case 'coffee':
      language =
        theme === 'false' ? 'coffeescript-img-w' : 'coffeescript-img-b';
      break;
    case 'md':
      language = theme === 'false' ? 'markdown-img-w' : 'markdown-img-b';
      break;
    case 'sh':
      language = theme === 'false' ? 'bash-img-w' : 'bash-img-b';
      break;
    case 'yml':
    case 'yaml':
      language = theme === 'false' ? 'yaml-img-w' : 'yaml-img-b';
      break;
    case 'toml':
      language = theme === 'false' ? 'toml-img-w' : 'toml-img-b';
      break;
    default:
      break;
  }
  return IconsEnum[language] || language;
}

const IconsEnum: tIconsEnum = {
  erl: 'erlang-img',
  hs: 'haskell-img',
  lua: 'lua-img',
  matlab: 'matlab-img',
  m: 'objective-c-img',
  c: 'c-img',
  cpp: 'cpp-img',
  cc: 'cpp-img',
  h: 'cpp-img',
  hh: 'cpp-img',
  cs: 'csharp-img',
  css: 'css-img',
  go: 'go-img',
  html: 'html-img',
  htm: 'html-img',
  java: 'java-img',
  js: 'javascript-img',
  ts: 'typescript-img',
  dart: 'dart-img',
  scala: 'scala-img',
  sql: 'sql-img',
  pl: 'perl-img',
  php: 'php-img',
  py: 'python-img',
  pyc: 'python-img',
  ps1: 'powershell-img',
  r: 'r-img',
  swift: 'swift-img',
  rb: 'ruby-img',
  tex: 'tex-img',
  text: 'text-img',
  txt: 'text-img',
  rs: 'rust-img',
  json: 'json-img',
  xml: 'xml-img',
  groovy: 'groovy-img',
  kt: 'kotlin-img',
  clj: 'clojure-img',
  el: 'emacs-lisp-img',
  ex: 'elixir-img',
  sol: 'sol-img',
  sv: 'sv-img',
  asp: 'asp-img',
  cfm: 'cfm-img',
};

type tIconsEnum = {
  [key: string]: string;
};
