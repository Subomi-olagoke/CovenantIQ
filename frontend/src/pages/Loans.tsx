import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Plus, Filter, ChevronRight } from 'lucide-react';
import api from '../lib/api';
import type { LoanAgreement } from '../types';
import Layout from '../components/layout/Layout';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { LoanUploadModal } from '../components/loans/LoanUploadModal';
import { formatCurrency } from '../lib/utils';

export default function Loans() {
    const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);

    const { data: loans, isLoading } = useQuery<LoanAgreement[]>({
        queryKey: ['loans'],
        queryFn: async () => {
            const res = await api.get('/api/loans');
            return res.data;
        },
    });

    return (
        <Layout
            title="Loans"
            maxWidth="default"
            actions={
                <div className="flex gap-3">
                    <Button variant="secondary" className="hidden sm:flex">
                        <Filter className="w-4 h-4 mr-2" />
                        Filter
                    </Button>
                    <Button onClick={() => setIsUploadModalOpen(true)}>
                        <Plus className="w-4 h-4 mr-2" />
                        Add Loan
                    </Button>
                </div>
            }
        >
            <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
                {isLoading ? (
                    <div className="p-12 text-center text-gray-400 text-sm">Loading loans...</div>
                ) : !loans || loans.length === 0 ? (
                    <div className="p-12 text-center">
                        <p className="text-gray-500 text-sm">No loans yet. Add your first loan agreement.</p>
                    </div>
                ) : (
                    <div className="divide-y divide-gray-100">
                        {loans.map((loan) => (
                            <Link
                                key={loan.id}
                                to={`/loans/${loan.id}`}
                                className="flex items-center gap-6 p-5 hover:bg-gray-50 transition-colors group"
                            >
                                {/* Avatar */}
                                <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center shrink-0">
                                    <span className="text-sm font-medium text-gray-700">
                                        {loan.borrower_name?.substring(0, 2).toUpperCase() || 'NA'}
                                    </span>
                                </div>

                                {/* Info */}
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-3 mb-1">
                                        <h3 className="text-sm font-semibold text-black truncate">
                                            {loan.borrower_name || 'Unnamed Borrower'}
                                        </h3>
                                        <Badge variant={
                                            loan.status === 'compliant' ? 'success' :
                                                loan.status === 'warning' ? 'warning' : 'danger'
                                        }>
                                            {loan.status?.toUpperCase() || 'UNKNOWN'}
                                        </Badge>
                                    </div>
                                    <div className="flex items-center gap-4 text-xs text-gray-500">
                                        <span>{formatCurrency(loan.loan_amount || 0)}</span>
                                        <span>•</span>
                                        <span>{loan.covenant_count || 0} Covenants</span>
                                    </div>
                                </div>

                                {/* Arrow */}
                                <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-black transition-colors shrink-0" />
                            </Link>
                        ))}
                    </div>
                )}
            </div>

            <LoanUploadModal
                isOpen={isUploadModalOpen}
                onClose={() => setIsUploadModalOpen(false)}
                onSuccess={() => {
                    // Refresh the loans list
                    window.location.reload();
                }}
            />
        </Layout>
    );
}
