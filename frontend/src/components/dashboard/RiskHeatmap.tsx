import { useNavigate } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import type { RiskHeatmapItem } from '../../types';

interface RiskHeatmapProps {
    loans: RiskHeatmapItem[];
    isLoading: boolean;
}

const RiskHeatmap = ({ loans, isLoading }: RiskHeatmapProps) => {
    const navigate = useNavigate();

    const getStatusColor = (loan: RiskHeatmapItem) => {
        if (loan.status === 'breach') return 'bg-red-50 border-red-300 hover:border-red-500';
        if (loan.status === 'warning') return 'bg-amber-50 border-amber-300 hover:border-amber-500';
        return 'bg-green-50 border-green-300 hover:border-green-500';
    };

    const getInitials = (name: string | null) => {
        if (!name) return '??';
        return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
            </div>
        );
    }

    if (loans.length === 0) {
        return (
            <div className="text-center py-12 text-gray-500">
                <p className="text-sm font-medium">No loans to display</p>
                <p className="text-xs mt-1 text-gray-400">Upload your first loan to get started</p>
            </div>
        );
    }

    return (
        <div className="grid grid-cols-4 gap-3">
            {loans.slice(0, 48).map(loan => (
                <div
                    key={loan.loan_id}
                    onClick={() => navigate(`/loans/${loan.loan_id}`)}
                    className={`
            relative aspect-square p-3 rounded-lg border-2 cursor-pointer 
            transition-all duration-150 hover:scale-105 hover:shadow-md
            ${getStatusColor(loan)}
          `}
                    title={`${loan.borrower_name} - ${loan.covenant_count} covenants`}
                >
                    <div className="font-bold text-lg text-black">
                        {getInitials(loan.borrower_name)}
                    </div>
                    <div className="text-xs text-gray-600 mt-2">
                        {loan.covenant_count} covenant{loan.covenant_count !== 1 ? 's' : ''}
                    </div>
                </div>
            ))}
        </div>
    );
};

export default RiskHeatmap;
