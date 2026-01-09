import { useEffect, useState } from 'react';
import { Search, X, FileText, AlertTriangle } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import api from '../../lib/api';

interface SearchModalProps {
    isOpen: boolean;
    onClose: () => void;
}

interface LoanResult {
    id: string;
    title: string;
    borrower_name: string;
    type: 'loan';
}

interface CovenantResult {
    id: string;
    name: string;
    loan_title: string;
    type: 'covenant';
}

interface SearchResults {
    loans: LoanResult[];
    covenants: CovenantResult[];
    total: number;
}

export function SearchModal({ isOpen, onClose }: SearchModalProps) {
    const [query, setQuery] = useState('');
    const [isAnimating, setIsAnimating] = useState(false);
    const navigate = useNavigate();

    // Search API
    const { data: results } = useQuery<SearchResults>({
        queryKey: ['search', query],
        queryFn: async () => {
            if (query.length < 2) return { loans: [], covenants: [], total: 0 };
            const res = await api.get(`/api/search?q=${encodeURIComponent(query)}`);
            return res.data;
        },
        enabled: query.length >= 2,
    });

    useEffect(() => {
        if (isOpen) {
            setQuery('');
            setIsAnimating(true);
        } else {
            const timer = setTimeout(() => setIsAnimating(false), 200);
            return () => clearTimeout(timer);
        }
    }, [isOpen]);

    const handleSelectLoan = (loanId: string) => {
        navigate(`/loans/${loanId}`);
        onClose();
    };

    if (!isOpen && !isAnimating) return null;

    const hasResults = results && results.total > 0;
    const showResults = query.length >= 2;

    return (
        <div className={`fixed inset-0 z-50 flex items-start justify-center pt-[15vh] px-4 transition-opacity duration-200 ${isOpen ? 'opacity-100' : 'opacity-0'
            }`}>
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/50 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Modal */}
            <div className={`relative w-full max-w-2xl bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden transition-all duration-200 ${isOpen ? 'scale-100 opacity-100 translate-y-0' : 'scale-95 opacity-0 -translate-y-2'
                }`}>
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
                    {!showResults ? (
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
                    ) : !hasResults ? (
                        <div className="p-8 text-center text-sm text-gray-500">
                            No results for "{query}"
                        </div>
                    ) : (
                        <div className="p-2">
                            {/* Loans */}
                            {results.loans.length > 0 && (
                                <div className="mb-4">
                                    <div className="px-3 py-2 text-xs font-medium text-gray-500">LOANS</div>
                                    {results.loans.map((loan) => (
                                        <button
                                            key={loan.id}
                                            onClick={() => handleSelectLoan(loan.id)}
                                            className="w-full px-3 py-2.5 text-left hover:bg-gray-50 rounded-lg transition-colors flex items-start gap-3"
                                        >
                                            <FileText className="w-4 h-4 text-gray-400 mt-0.5 shrink-0" />
                                            <div className="flex-1 min-w-0">
                                                <div className="text-sm font-medium text-black truncate">{loan.title}</div>
                                                <div className="text-xs text-gray-500 truncate">{loan.borrower_name}</div>
                                            </div>
                                        </button>
                                    ))}
                                </div>
                            )}

                            {/* Covenants */}
                            {results.covenants.length > 0 && (
                                <div>
                                    <div className="px-3 py-2 text-xs font-medium text-gray-500">COVENANTS</div>
                                    {results.covenants.map((covenant) => (
                                        <button
                                            key={covenant.id}
                                            className="w-full px-3 py-2.5 text-left hover:bg-gray-50 rounded-lg transition-colors flex items-start gap-3"
                                        >
                                            <AlertTriangle className="w-4 h-4 text-gray-400 mt-0.5 shrink-0" />
                                            <div className="flex-1 min-w-0">
                                                <div className="text-sm font-medium text-black truncate">{covenant.name}</div>
                                                <div className="text-xs text-gray-500 truncate">in {covenant.loan_title}</div>
                                            </div>
                                        </button>
                                    ))}
                                </div>
                            )}
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
