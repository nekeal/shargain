import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import HttpBackend from 'i18next-http-backend';
import LanguageDetector from 'i18next-browser-languagedetector';
import { defaultNS, resources } from '../i18n/resources';

i18n
  // Load translation using http -> see /public/locales (i.e. https://github.com/i18next/react-i18next/tree/master/example/react/public/locales)
  // Learn more: https://github.com/i18next/i18next-http-backend
  .use(HttpBackend)
  // Detect user language
  // Learn more: https://github.com/i18next/i18next-browser-languageDetector
  .use(LanguageDetector)
  // Pass the i18n instance to react-i18next.
  .use(initReactI18next)
  // Initialize i18next
  .init({
    // For all available options, see: https://www.i18next.com/overview/configuration-options
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json',
    },
    fallbackLng: 'en',
    supportedLngs: ['en', 'pl'],
    defaultNS,
    debug: true,
    interpolation: {
      escapeValue: false, // Not needed for react as it escapes by default
    },
    detection: {
      // For all available options, see: https://github.com/i18next/i18next-browser-languageDetector#detector-options
      order: ['localStorage', 'cookie', 'navigator', 'htmlTag', 'path', 'subdomain'],
      caches: ['localStorage', 'cookie'],
      excludeCacheFor: ['cimode'], // Languages to not persist (cookie, localStorage)
    },
    // Provide en resources inline so hydration works instantly
    resources: { en: resources.en, pl: resources.pl },
  });

export default i18n;
