import type { ReactNode } from 'react';
import Sidebar from './Sidebar';
import { Search, User } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

interface LayoutProps {
    children: ReactNode;
    title?: string;
    maxWidth?: 'default' | 'wide';
    actions?: ReactNode;
}

export default function Layout({ children, title, maxWidth = 'default', actions }: LayoutProps) {
    const { user } = useAuth();

    return (
        <>
            {/* Mobile Warning */}
            <div className="md:hidden min-h-screen flex items-center justify-center bg-white p-8">
                <div className="text-center">
                    <h1 className="text-2xl font-bold text-black mb-4">Desktop Only</h1>
                    <p className="text-gray-600">CovenantIQ requires a minimum viewport width of 1280px. Please use a desktop device.</p>
                </div>
            </div>

            {/* Desktop Layout */}
            <div className="hidden md:flex min-h-screen bg-gray-50">
                <Sidebar />

                <main className="flex-1 ml-14">
                    {/* Header */}
                    <header className="bg-white border-b border-gray-200 px-8 py-4">
                        <div className={maxWidth === 'wide' ? 'max-w-[1600px] mx-auto' : 'max-w-7xl mx-auto'}>
                            <div className="flex items-center justify-between gap-4">
                                {/* Search Bar */}
                                <div className="flex-1 max-w-md">
                                    <div className="relative">
                                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                                        <input
                                            type="text"
                                            placeholder="Find anything..."
                                            className="w-full pl-10 pr-4 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                                        />
                                        <kbd className="absolute right-3 top-1/2 -translate-y-1/2 px-1.5 py-0.5 text-xs text-gray-400 bg-gray-100 rounded">
                                            ⌘K
                                        </kbd>
                                    </div>
                                </div>

                                {/* Right Actions */}
                                <div className="flex items-center gap-3">
                                    <div className="w-8 h-8 rounded-full bg-gray-900 text-white flex items-center justify-center text-sm font-medium">
                                        {user?.full_name?.charAt(0) || <User className="w-4 h-4" />}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </header>

                    {/* Page Content */}
                    <div className={maxWidth === 'wide' ? 'max-w-[1600px] mx-auto' : 'max-w-7xl mx-auto'}>
                        <div className="px-8 py-6">
                            {/* Page Title & Actions */}
                            {(title || actions) && (
                                <div className="flex items-center justify-between mb-6">
                                    {title && <h1 className="text-2xl font-semibold text-black">{title}</h1>}
                                    {actions && <div className="flex items-center gap-3">{actions}</div>}
                                </div>
                            )}

                            {children}
                        </div>
                    </div>
                </main>
            </div>
        </>
    );
}
