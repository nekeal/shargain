import { useTranslation } from 'react-i18next';

export default function LanguageSwitcher() {
  const { i18n } = useTranslation();

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  return (
    <div className="relative">
      <select
        value={i18n.language}
        onChange={(e) => changeLanguage(e.target.value)}
        className="block appearance-none w-full bg-white border border-gray-300 hover:border-gray-400 px-4 py-2 pr-8 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-violet-500 dark:bg-gray-800 dark:border-gray-600 dark:hover:border-gray-500 dark:text-white"
      >
        <option value="en">English</option>
        <option value="pl">Polski</option>
      </select>
      <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700 dark:text-gray-300">
        <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
          <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
        </svg>
      </div>
    </div>
  );
}
