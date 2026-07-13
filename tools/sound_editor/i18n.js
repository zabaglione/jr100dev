const LANGUAGE_STORAGE_KEY = "jr100dev.sound-workbench.language";

export const TRANSLATIONS = Object.freeze({
  ja: {
    "app.title": "JR-100 サウンドワークベンチ",
    "app.subtitle": "単音BGMとブロッキング効果音のアセットエディター",
    "language.label": "表示言語",
    "language.ja": "日本語",
    "language.en": "English",
    "status.ready": "準備完了",
    "status.saved": "保存しました",
    "status.previewPlaying": "試聴を再生中です",
    "status.previewStopped": "試聴を停止しました",
    "status.newProject": "新しいプロジェクトを作成しました",
    "status.projectLoaded": "プロジェクトを読み込みました",
    "status.demoBuilt": "確認用PRGを作成しました",
    "status.languageChanged": "表示言語を変更しました",
    "status.buildFailed": "ビルドに失敗しました。プロジェクトの入力値を確認してください。",
    "project.label": "プロジェクト名",
    "project.settings": "プロジェクト設定",
    "project.tickHz": "ゲーム更新Hz",
    "project.gridTicks": "BGMグリッドtick",
    "actions.new": "新規作成",
    "actions.saveJson": "JSONを保存",
    "actions.loadJson": "JSONを読込",
    "actions.downloadAssembly": "sound_assets.incを保存",
    "actions.buildPrg": "確認用PRGを作成",
    "actions.add": "追加",
    "actions.play": "試聴",
    "actions.stop": "停止",
    "actions.delete": "削除",
    "assets.tracks": "BGMトラック",
    "assets.effects": "ブロッキング効果音",
    "assets.sfxConstraint": "効果音は10ms単位で、最大50セルです。",
    "editor.bgm": "BGMピアノロール",
    "editor.sfx": "ブロッキング効果音ピアノロール",
    "editor.name": "名前",
    "editor.identifier": "識別子",
    "editor.cells": "セル数",
    "editor.loopCell": "ループ開始セル",
    "editor.canvas": "ピアノロールエディター",
    "editor.bgmHelp": "左クリックで音を置き、右クリックで休符にします。矢印キーでカーソルを動かし、SpaceまたはEnterで音を置きます。1セルは{ticks}ゲームtickです。",
    "editor.sfxHelp": "左クリックで音を置き、右クリックで休符にします。矢印キーでカーソルを動かし、SpaceまたはEnterで音を置きます。1セルは10msで、全体は500msまでです。",
    "provenance.title": "収録サンプルの来歴",
    "provenance.asset": "資産",
    "provenance.source": "原曲",
    "provenance.composer": "作曲者",
    "provenance.rule": "収録方針",
    "provenance.odeSource": "交響曲第9番・冒頭フレーズ",
    "provenance.odeComposer": "Ludwig van Beethoven（1827年没）",
    "provenance.mozartSource": "K.265主題・冒頭フレーズ",
    "provenance.mozartComposer": "Wolfgang Amadeus Mozart（1791年没）",
    "provenance.ruleText": "独自の単音縮約。楽譜画像、歌詞、録音、近現代編曲は含みません。",
    "asset.newTrack": "新しいBGM",
    "asset.newEffect": "新しい効果音",
    "error.bgmRequired": "プロジェクトにはBGMトラックが1つ以上必要です。",
    "error.invalidProject": "プロジェクトの入力値が不正です。各項目を確認してください。",
    "error.loadFailed": "JSONを読み込めませんでした。ファイルの形式を確認してください。",
  },
  en: {
    "app.title": "JR-100 Sound Workbench",
    "app.subtitle": "Monophonic BGM and blocking SFX asset editor",
    "language.label": "Language",
    "language.ja": "Japanese",
    "language.en": "English",
    "status.ready": "Ready",
    "status.saved": "Saved",
    "status.previewPlaying": "Preview playing",
    "status.previewStopped": "Preview stopped",
    "status.newProject": "New project created",
    "status.projectLoaded": "Project loaded",
    "status.demoBuilt": "Demo PRG built",
    "status.languageChanged": "Language changed",
    "status.buildFailed": "Build failed. Check the project values and try again.",
    "project.label": "Project",
    "project.settings": "Project settings",
    "project.tickHz": "Game tick Hz",
    "project.gridTicks": "BGM grid ticks",
    "actions.new": "New project",
    "actions.saveJson": "Save JSON",
    "actions.loadJson": "Load JSON",
    "actions.downloadAssembly": "Download sound_assets.inc",
    "actions.buildPrg": "Build demo PRG",
    "actions.add": "Add",
    "actions.play": "Play",
    "actions.stop": "Stop",
    "actions.delete": "Delete",
    "assets.tracks": "BGM tracks",
    "assets.effects": "Blocking SFX",
    "assets.sfxConstraint": "SFX uses 10ms cells and is capped at 50 cells.",
    "editor.bgm": "BGM piano roll",
    "editor.sfx": "Blocking SFX piano roll",
    "editor.name": "Name",
    "editor.identifier": "Identifier",
    "editor.cells": "Cells",
    "editor.loopCell": "Loop cell",
    "editor.canvas": "Piano roll editor",
    "editor.bgmHelp": "Left click writes a note. Right click writes a rest. Arrow keys move the cursor; Space or Enter writes a note. Each cell is {ticks} game ticks.",
    "editor.sfxHelp": "Left click writes a note. Right click writes a rest. Arrow keys move the cursor; Space or Enter writes a note. Each cell is 10ms and the complete effect is limited to 500ms.",
    "provenance.title": "Included sample provenance",
    "provenance.asset": "Asset",
    "provenance.source": "Source composition",
    "provenance.composer": "Composer",
    "provenance.rule": "Rule",
    "provenance.odeSource": "Symphony No. 9, opening phrase",
    "provenance.odeComposer": "Ludwig van Beethoven, died 1827",
    "provenance.mozartSource": "K.265 theme, opening phrase",
    "provenance.mozartComposer": "Wolfgang Amadeus Mozart, died 1791",
    "provenance.ruleText": "Original monophonic reduction; no score image, lyrics, recording, or modern arrangement.",
    "asset.newTrack": "New BGM",
    "asset.newEffect": "New SFX",
    "error.bgmRequired": "A project needs one BGM track.",
    "error.invalidProject": "The project has invalid values. Check each field.",
    "error.loadFailed": "Could not load JSON. Check the file format.",
  },
});

let language = resolveLanguage(globalThis.localStorage?.getItem(LANGUAGE_STORAGE_KEY));

function resolveLanguage(value) {
  return Object.hasOwn(TRANSLATIONS, value) ? value : "ja";
}

export function getLanguage() {
  return language;
}

export function setLanguage(value) {
  language = resolveLanguage(value);
  globalThis.localStorage?.setItem(LANGUAGE_STORAGE_KEY, language);
  return language;
}

export function t(key, values = {}) {
  const template = TRANSLATIONS[language][key] ?? TRANSLATIONS.en[key] ?? key;
  return template.replace(/\{(\w+)\}/g, (_, name) => String(values[name] ?? ""));
}

export function translateDocument() {
  document.documentElement.lang = language;
  document.title = t("app.title");
  for (const element of document.querySelectorAll("[data-i18n]")) {
    element.textContent = t(element.dataset.i18n);
  }
  for (const element of document.querySelectorAll("[data-i18n-aria]")) {
    element.setAttribute("aria-label", t(element.dataset.i18nAria));
  }
}
