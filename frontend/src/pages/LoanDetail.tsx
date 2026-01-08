import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ChevronLeft, Pencil, FileText, Download } from 'lucide-react';
import api from '../lib/api';
import type { LoanAgreement, Covenant } from '../types';
import Layout from '../components/layout/Layout';
import { Button } from '../components/ui/Button';
import { CovenantRow } from '../components/loans/CovenantRow';
import { useState } from 'react';

export default function LoanDetail() {
    const { loanId } = useParams();
    const [activeTab, setActiveTab] = useState<'overview' | 'covenants' | 'financials' | 'documents'>('covenants');

    const { data: loan, isLoading } = useQuery<LoanAgreement>({
        queryKey: ['loan', loanId],
        queryFn: async () => {
            const res = await api.get(`/api/loans/${loanId}`);
            return res.data;
        },
    });

    const { data: covenants } = useQuery<Covenant[]>({
        queryKey: ['loan-covenants', loanId],
        queryFn: async () => {
            const res = await api.get(`/api/covenants/loan/${loanId}`);
            return res.data;
        },
        enabled: !!loanId,
    });

    if (isLoading) {
        return <Layout><div className="flex justify-center py-20 text-gray-500">Loading loan details...</div></Layout>;
    }

    if (!loan) {
        return <Layout><div className="flex justify-center py-20 text-gray-500">Loan not found</div></Layout>;
    }

    return (
        <Layout
            title={loan.borrower_name || loan.title}
            actions={
                <Button variant="secondary" size="sm">
                    <Pencil className="w-4 h-4 mr-2" /> Edit Loan
                </Button>
            }
        >
            <div className="mb-8">
                <Link to="/loans" className="inline-flex items-center text-sm text-gray-500 hover:text-black mb-4">
                    <ChevronLeft className="w-4 h-4 mr-1" /> Back to Loans
                </Link>

                <div className="grid grid-cols-3 gap-6 mb-8">
                    <div className="bg-gray-50 rounded-lg p-4 border border-gray-100">
                        <span className="text-xs uppercase tracking-widest text-gray-500 font-medium">Loan Title</span>
                        <div className="text-lg font-bold text-black mt-1">{loan.title}</div>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4 border border-gray-100">
                        <span className="text-xs uppercase tracking-widest text-gray-500 font-medium">Principal Amount</span>
                        <div className="text-lg font-bold text-black mt-1 font-tabular">
                            {loan.currency} {loan.loan_amount?.toLocaleString()}
                        </div>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4 border border-gray-100">
                        <span className="text-xs uppercase tracking-widest text-gray-500 font-medium">Origination Date</span>
                        <div className="text-lg font-bold text-black mt-1">
                            {loan.origination_date ? new Date(loan.origination_date).toLocaleDateString() : 'N/A'}
                        </div>
                    </div>
                </div>

                {/* Tabs */}
                <div className="flex border-b border-gray-200 mb-8">
                    {['Overview', 'Covenants', 'Financials', 'Documents'].map((tab) => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab.toLowerCase() as any)}
                            className={`px-6 py-3 text-sm font-medium transition-colors border-b-2 relative ${activeTab === tab.toLowerCase()
                                ? 'text-black border-black'
                                : 'text-gray-500 border-transparent hover:text-black hover:bg-gray-50'
                                }`}
                        >
                            {tab}
                            {tab === 'Covenants' && covenants && (
                                <span className={`ml-2 px-2 py-0.5 rounded-full text-xs ${activeTab === 'covenants' ? 'bg-black text-white' : 'bg-gray-200 text-gray-700'
                                    }`}>
                                    {covenants.length}
                                </span>
                            )}
                        </button>
                    ))}
                </div>

                {/* Tab Content */}
                <div className="min-h-[400px]">
                    {activeTab === 'covenants' && (
                        <div className="space-y-4">
                            {!covenants || covenants.length === 0 ? (
                                <div className="text-center py-12 text-gray-500 bg-gray-50 rounded-lg border border-dashed border-gray-300">
                                    No covenants found for this loan.
                                </div>
                            ) : (
                                covenants.map(covenant => (
                                    <CovenantRow key={covenant.id} covenant={covenant} />
                                ))
                            )}
                        </div>
                    )}

                    {activeTab === 'documents' && (
                        <div className="bg-white border border-gray-200 rounded-lg p-6">
                            <h3 className="text-lg font-bold text-black mb-4">Loan Documents</h3>
                            <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-black transition-colors cursor-pointer group">
                                <div className="flex items-center gap-4">
                                    <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center text-gray-500 group-hover:text-black transition-colors">
                                        <FileText className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <p className="font-semibold text-black">Original Facility Agreement.pdf</p>
                                        <p className="text-xs text-gray-500">Uploaded on {new Date(loan.created_at).toLocaleDateString()}</p>
                                    </div>
                                </div>
                                <Button variant="ghost" size="sm">
                                    <Download className="w-4 h-4 mr-2" />
                                    Download
                                </Button>
                            </div>
                        </div>
                    )}

                    {(activeTab === 'overview' || activeTab === 'financials') && (
                        <div className="text-center py-20 text-gray-400">
                            {activeTab} content coming soon...
                        </div>
                    )}
                </div>
            </div>
        </Layout>
    );
}
