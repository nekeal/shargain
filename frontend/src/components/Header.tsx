import { Link, useLocation } from '@tanstack/react-router'

export default function Header() {
  const location = useLocation()
  
  const navItems = [
    { path: '/dashboard', label: 'Dashboard' },
    { path: '/notifications', label: 'Notifications' }
  ]
  
  return (
    <header className="bg-white shadow-sm">
      <nav className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-8">
            <div className="flex-shrink-0">
              <Link 
                to="/dashboard" 
                className="flex items-center space-x-3"
              >
                <div className="bg-violet-600 text-white rounded-lg w-10 h-10 flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                  </svg>
                </div>
                <span className="text-2xl font-bold bg-gradient-to-r from-violet-600 to-purple-600 bg-clip-text text-transparent">
                  OfferAlert
                </span>
              </Link>
            </div>
            <div className="flex space-x-1">
              {navItems.map((item) => (
                <Link 
                  key={item.path}
                  to={item.path} 
                  className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                    location.pathname === item.path 
                      ? 'bg-violet-100 text-violet-700' 
                      : 'text-gray-700 hover:bg-violet-50 hover:text-violet-600'
                  }`}
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </div>
        </div>
      </nav>
    </header>
  )
}
