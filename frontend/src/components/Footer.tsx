import { Link } from '@tanstack/react-router';

export function Footer() {
  return (
    <footer className="bg-gray-100 text-gray-600 px-6 py-4 mt-auto">
      <div className="container mx-auto flex justify-center items-center text-sm">
        <p>&copy; {new Date().getFullYear()} Shargain. All Rights Reserved.</p>
        <div className="ml-4 pl-4 border-l border-gray-300">
          <Link to="/legal/terms" className="hover:text-violet-600 transition-colors">
            Terms of Service
          </Link>
        </div>
        <div className="ml-4 pl-4 border-l border-gray-300">
          <Link to="/legal/privacy" className="hover:text-violet-600 transition-colors">
            Privacy Policy
          </Link>
        </div>
      </div>
    </footer>
  );
}
