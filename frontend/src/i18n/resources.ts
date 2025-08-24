import translation from "../locales/en/translation.json";
import plTranslation from "../locales/pl/translation.json";

export const defaultNS = 'translation' as const;

export const resources = {
  en: { translation },
  pl: { translation: plTranslation },
} as const;
