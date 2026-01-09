import { useEffect, useState } from 'react';
import { Search, X } from 'lucide-react';

interface SearchModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export function SearchModal({ isOpen, onClose }: SearchModalProps) {
    const [query, setQuery] = useState('');

    useEffect(() => {
        if (isOpen) {
            setQuery('');
        }
    }, [isOpen]);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh] px-4">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/50 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Modal */}
            <div className="relative w-full max-w-2xl bg-white rounded-xl shadow-2xl border border-gray-200 overflow-hidden">
                {/* Search Input */}
                <div className="flex items-center gap-3 px-4 py-4 border-b border-gray-200">
                    <Search className="w-5 h-5 text-gray-400 shrink-0" />
                    <input
                        type="text"
                        placeholder="Search loans, borrowers, covenants..."
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        autoFocus
                        className="flex-1 text-base bg-transparent border-none outline-none placeholder:text-gray-400"
                    />
                    <button
                        onClick={onClose}
                        className="p-1.5 hover:bg-gray-100 rounded-md transition-colors"
                    >
                        <X className="w-4 h-4 text-gray-500" />
                    </button>
                </div>

                {/* Results */}
                <div className="max-h-[60vh] overflow-y-auto">
                    {!query ? (
                        <div className="p-8 text-center text-sm text-gray-500">
                            <p>Start typing to search...</p>
                            <div className="mt-6 space-y-2">
                                <p className="text-xs text-gray-400">Quick tips:</p>
                                <div className="flex flex-wrap gap-2 justify-center">
                                    <span className="px-2 py-1 bg-gray-100 rounded text-xs">Borrower names</span>
                                    <span className="px-2 py-1 bg-gray-100 rounded text-xs">Loan titles</span>
                                    <span className="px-2 py-1 bg-gray-100 rounded text-xs">Covenant types</span>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="p-4">
                            <div className="text-sm text-gray-500 text-center py-8">
                                No results for "{query}"
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between px-4 py-3 bg-gray-50 border-t border-gray-200 text-xs text-gray-500">
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-1.5">
                            <kbd className="px-2 py-1 bg-white border border-gray-200 rounded text-xs font-mono">↑↓</kbd>
                            <span>Navigate</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                            <kbd className="px-2 py-1 bg-white border border-gray-200 rounded text-xs font-mono">↵</kbd>
                            <span>Select</span>
                        </div>
                    </div>
                    <div className="flex items-center gap-1.5">
                        <kbd className="px-2 py-1 bg-white border border-gray-200 rounded text-xs font-mono">esc</kbd>
                        <span>Close</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
