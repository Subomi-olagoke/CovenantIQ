import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, FileText, Bell, Settings, LogOut, TrendingUp } from 'lucide-react';
import { cn } from '../../lib/utils';
import { useAuth } from '../../contexts/AuthContext';

function Sidebar() {
    const location = useLocation();
    const { logout } = useAuth();

    const navItems = [
        { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
        { path: '/loans', icon: FileText, label: 'Loans' },
        { path: '/alerts', icon: Bell, label: 'Alerts' },
        { path: '/settings', icon: Settings, label: 'Settings' },
    ];

    const isActive = (path: string) => {
        if (path === '/') return location.pathname === '/';
        return location.pathname.startsWith(path);
    };

    return (
        <aside className="fixed left-0 top-0 h-screen w-14 bg-white border-r border-gray-200 flex flex-col items-center py-4 z-50">
            {/* Logo */}
            <Link
                to="/"
                className="mb-8 p-2 rounded-lg hover:bg-gray-100 transition-colors group"
                title="CovenantIQ"
            >
                <TrendingUp className="w-6 h-6 text-black" />
            </Link>

            {/* Navigation */}
            <nav className="flex-1 flex flex-col gap-2 w-full px-2">
                {navItems.map((item) => (
                    <Link
                        key={item.path}
                        to={item.path}
                        className={cn(
                            "p-2.5 rounded-lg transition-all relative group",
                            isActive(item.path)
                                ? "bg-gray-100 text-black"
                                : "text-gray-500 hover:bg-gray-50 hover:text-black"
                        )}
                        title={item.label}
                    >
                        <item.icon className="w-5 h-5" />

                        {/* Tooltip */}
                        <div className="absolute left-full ml-2 px-2 py-1 bg-black text-white text-xs rounded whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity">
                            {item.label}
                        </div>
                    </Link>
                ))}
            </nav>

            {/* Logout */}
            <button
                onClick={logout}
                className="p-2.5 rounded-lg text-gray-500 hover:bg-gray-50 hover:text-black transition-all group relative"
                title="Logout"
            >
                <LogOut className="w-5 h-5" />

                {/* Tooltip */}
                <div className="absolute left-full ml-2 px-2 py-1 bg-black text-white text-xs rounded whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity">
                    Logout
                </div>
            </button>
        </aside>
    );
}

export default Sidebar;
