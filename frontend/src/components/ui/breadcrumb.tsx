import { Link, useLocation } from '@tanstack/react-router'
import { ChevronRight } from 'lucide-react'

interface BreadcrumbItem {
  label: string
  href?: string
}

export function Breadcrumb() {
  const location = useLocation()
  
  // Define breadcrumbs based on the current path
  const breadcrumbs: BreadcrumbItem[] = [
    { label: 'Home', href: '/dashboard' }
  ]
  
  // Add additional breadcrumbs based on the current path
  if (location.pathname.startsWith('/notifications')) {
    breadcrumbs.push({ label: 'Notifications' })
  } else if (location.pathname === '/dashboard') {
    breadcrumbs.push({ label: 'Dashboard' })
  }
  
  return (
    <nav className="flex items-center space-x-2 text-sm">
      {breadcrumbs.map((crumb, index) => (
        <div key={index} className="flex items-center">
          {crumb.href ? (
            <Link 
              to={crumb.href} 
              className="text-gray-600 hover:text-violet-600 transition-colors"
            >
              {crumb.label}
            </Link>
          ) : (
            <span className="text-gray-900 font-medium">{crumb.label}</span>
          )}
          {index < breadcrumbs.length - 1 && (
            <ChevronRight className="h-4 w-4 text-gray-400 mx-2" />
          )}
        </div>
      ))}
    </nav>
  )
}
