
import { useTranslation } from 'react-i18next';
import { Link } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';

export function LandingPage() {
  const { t } = useTranslation();

  return (
    <>
      {/* Header with Login button */}
      <div className="absolute top-4 right-4">
        <Button asChild variant="outline" className="border-2 border-violet-300 hover:bg-violet-50 dark:border-violet-700 dark:hover:bg-violet-900/50">
          <Link to="/auth/signin">{t('landing.login')}</Link>
        </Button>
      </div>

      <div className="bg-gradient-to-b from-violet-50 via-purple-50 to-indigo-100 dark:from-violet-950/50 dark:via-purple-950/30 dark:to-background">
        <div className="container mx-auto px-4 text-center py-24">
          <h1 className="text-4xl md:text-6xl font-bold tracking-tighter text-gray-900 dark:text-white">{t('landing.title')}</h1>
          <p className="text-lg md:text-xl text-gray-700 dark:text-gray-300 mt-4 max-w-3xl mx-auto">{t('landing.subtitle')}</p>
          <div className="mt-8">
            <Button asChild size="lg" className="bg-gradient-to-r from-violet-600 to-indigo-700 hover:from-violet-700 hover:to-indigo-800 shadow-lg hover:shadow-xl transition-all duration-300">
              <Link to="/auth/signup">{t('landing.signUp')}</Link>
            </Button>
          </div>
        </div>
      </div>
      <div className="container mx-auto px-4 py-24">
        <h2 className="text-3xl md:text-4xl font-bold tracking-tighter text-center text-gray-900 dark:text-white">{t('landing.howItWorks')}</h2>
        <p className="text-lg md:text-xl text-gray-700 dark:text-gray-300 mt-4 max-w-3xl mx-auto text-center">{t('landing.getStarted')}</p>
        <div className="grid md:grid-cols-3 gap-8 mt-12">
          <div className="text-center bg-white dark:bg-gray-800/50 p-8 rounded-2xl shadow-lg hover:shadow-xl transition-shadow duration-300">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-violet-500 to-purple-500 text-white rounded-full mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-link"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.72" /><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.72-1.72" /></svg>
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white">{t('landing.step1.title')}</h3>
            <p className="text-gray-700 dark:text-gray-300 mt-2">{t('landing.step1.description')}</p>
          </div>
          <div className="text-center bg-white dark:bg-gray-800/50 p-8 rounded-2xl shadow-lg hover:shadow-xl transition-shadow duration-300">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-indigo-500 to-blue-500 text-white rounded-full mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-bell-ring"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" /><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" /><path d="M4 2C2.8 3.7 2 5.7 2 8" /><path d="M22 8c0-2.3-.8-4.3-2-6" /></svg>
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white">{t('landing.step2.title')}</h3>
            <p className="text-gray-700 dark:text-gray-300 mt-2">{t('landing.step2.description')}</p>
          </div>
          <div className="text-center bg-white dark:bg-gray-800/50 p-8 rounded-2xl shadow-lg hover:shadow-xl transition-shadow duration-300">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-full mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-check-circle"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" /></svg>
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white">{t('landing.step3.title')}</h3>
            <p className="text-gray-700 dark:text-gray-300 mt-2">{t('landing.step3.description')}</p>
          </div>
        </div>
      </div>
      <div className="bg-gradient-to-r from-violet-100 to-indigo-100 dark:from-violet-900/30 dark:to-indigo-900/30 py-24">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold tracking-tighter text-center text-gray-900 dark:text-white">{t('landing.pricing.title')}</h2>
          <p className="text-lg md:text-xl text-gray-700 dark:text-gray-300 mt-4 max-w-3xl mx-auto text-center">{t('landing.pricing.subtitle')}</p>
          <div className="max-w-md mx-auto mt-12 bg-white dark:bg-gray-800/50 rounded-2xl shadow-lg p-8 border border-violet-200 dark:border-violet-800">
            <div className="text-center">
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white">{t('landing.pricing.planName')}</h3>
              <div className="mt-4">
                <span className="text-4xl font-bold text-violet-600 dark:text-violet-400">{t('landing.pricing.price')}</span>
                <span className="text-gray-700 dark:text-gray-300"> {t('landing.pricing.period')}</span>
              </div>
              <ul className="mt-6 space-y-3 text-gray-700 dark:text-gray-300">
                <li className="flex items-center justify-center">
                  <svg className="h-5 w-5 text-green-500 mr-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  {t('landing.pricing.feature1')}
                </li>
                <li className="flex items-center justify-center">
                  <svg className="h-5 w-5 text-green-500 mr-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  {t('landing.pricing.feature2')}
                </li>
                <li className="flex items-center justify-center">
                  <svg className="h-5 w-5 text-green-500 mr-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  {t('landing.pricing.feature3')}
                </li>
              </ul>
              <Button asChild className="mt-8 w-full">
                <Link to="/auth/signup">{t('landing.pricing.getStarted')}</Link>
              </Button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
