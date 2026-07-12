import en from "./locales/en.js";
import ja from "./locales/ja.js";

const STORAGE_KEY = "jr100dev.pcg-workbench.language";
const DEFAULT_LANGUAGE = "ja";
const RESOURCES = Object.freeze({ en, ja });

let currentLanguage = resolveStoredLanguage(globalThis.localStorage);

export function resolveStoredLanguage(storage) {
  try {
    const stored = storage?.getItem(STORAGE_KEY);
    return Object.hasOwn(RESOURCES, stored) ? stored : DEFAULT_LANGUAGE;
  } catch {
    return DEFAULT_LANGUAGE;
  }
}

export function getLanguage() {
  return currentLanguage;
}

export function setLanguage(language) {
  if (!Object.hasOwn(RESOURCES, language)) {
    throw new RangeError("Unsupported UI language");
  }
  currentLanguage = language;
  try {
    globalThis.localStorage?.setItem(STORAGE_KEY, language);
  } catch {
    // The UI still switches when storage is unavailable.
  }
}

export function t(key, variables = {}) {
  const template = RESOURCES[currentLanguage][key] ?? RESOURCES.en[key] ?? key;
  return Object.entries(variables).reduce(
    (text, [name, value]) => text.replaceAll(`{{${name}}}`, String(value)),
    template,
  );
}

export function translateDocument(root = document) {
  document.documentElement.lang = currentLanguage;
  document.title = t("document.title");
  root.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = t(element.dataset.i18n);
  });
  root.querySelectorAll("[data-i18n-title]").forEach((element) => {
    element.title = t(element.dataset.i18nTitle);
  });
  root.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
    element.placeholder = t(element.dataset.i18nPlaceholder);
  });
  root.querySelectorAll("[data-i18n-aria]").forEach((element) => {
    element.setAttribute("aria-label", t(element.dataset.i18nAria));
  });
}
