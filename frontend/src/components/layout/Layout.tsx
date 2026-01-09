import { useState, useEffect, type ReactNode } from 'react';
import Sidebar from './Sidebar';
import { SearchModal } from '../ui/SearchModal';

interface LayoutProps {
    children: ReactNode;
    title?: string;
    actions?: ReactNode;
    maxWidth?: 'normal' | 'wide' | 'full';
}

export default function Layout({ children, title, actions, maxWidth = 'normal' }: LayoutProps) {
    const [isSearchOpen, setIsSearchOpen] = useState(false);

    const maxWidthClass = {
        normal: 'max-w-7xl',
        wide: 'max-w-[90rem]',
        full: 'max-w-none'
    }[maxWidth];

    // Keyboard shortcut for search (Cmd+K or Ctrl+K)
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                setIsSearchOpen(true);
            }
            if (e.key === 'Escape' && isSearchOpen) {
                setIsSearchOpen(false);
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [isSearchOpen]);

    return (
        <div className="min-h-screen bg-gray-50 flex">
            {/* Sidebar */}
            <Sidebar />

            {/* Main Content */}
            <div className="flex-1 ml-14">
                {/* Mobile Warning */}
                <div className="lg:hidden fixed inset-0 bg-black text-white flex items-center justify-center p-6 z-50">
                    <div className="text-center">
                        <h2 className="text-xl font-bold mb-2">Desktop Only</h2>
                        <p className="text-gray-400">This application is optimized for desktop screens.</p>
                    </div>
                </div>

                {/* Desktop Content */}
                <div className="hidden lg:block">
                    {/* Header */}
                    <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
                        <div className={`mx-auto px-8 ${maxWidthClass}`}>
                            <div className="h-16 flex items-center justify-between">
                                {/* Title Section */}
                                <div className="flex items-center gap-6 flex-1">
                                    {title && <h1 className="text-xl font-semibold text-black">{title}</h1>}
                                </div>

                                {/* Search Trigger */}
                                <div className="flex-1 max-w-md">
                                    <button
                                        onClick={() => setIsSearchOpen(true)}
                                        className="w-full px-4 py-2 text-sm text-left text-gray-500 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 hover:border-gray-300 transition-all flex items-center justify-between group"
                                    >
                                        <span>Search...</span>
                                        <kbd className="px-2 py-1 text-xs text-gray-400 bg-white border border-gray-200 rounded group-hover:border-gray-300">
                                            ⌘K
                                        </kbd>
                                    </button>
                                </div>
                            </div>

                            {/* Actions Row */}
                            {actions && (
                                <div className="pb-4">
                                    {actions}
                                </div>
                            )}
                        </div>
                    </header>

                    {/* Page Content */}
                    <main className={`mx-auto px-8 py-8 ${maxWidthClass}`}>
                        {children}
                    </main>
                </div>
            </div>

            {/* Search Modal */}
            <SearchModal isOpen={isSearchOpen} onClose={() => setIsSearchOpen(false)} />
        </div>
    );
}
