import { useQuery } from '@tanstack/react-query';
import api from '../lib/api';
import { PortfolioSummary, RiskHeatmapItem, Alert } from '../types';
import { Link } from 'react-router-dom';
import { formatRelativeTime, getStatusColor, getSeverityColor } from '../lib/utils';
import { Bell, TrendingUp, AlertTriangle, CheckCircle2 } from 'lucide-react';

export default function Dashboard() {
    // Fetch portfolio summary
    const { data: summary } = useQuery<PortfolioSummary>({
        queryKey: ['portfolio-summary'],
        queryFn: async () => {
            const res = await api.get('/api/analytics/portfolio-summary');
            return res.data;
        },
    });

    // Fetch risk heatmap
    const { data: heatmap } = useQuery<RiskHeatmapItem[]>({
        queryKey: ['risk-heatmap'],
        queryFn: async () => {
            const res = await api.get('/api/analytics/risk-heatmap');
            return res.data;
        },
    });

    // Fetch critical alerts
    const { data: alerts } = useQuery<Alert[]>({
        queryKey: ['critical-alerts'],
        queryFn: async () => {
            const res = await api.get('/api/analytics/critical-alerts');
            return res.data;
        },
    });

    const portfolioHealth = summary ?
        Math.round((summary.compliant_covenants / Math.max(summary.total_covenants, 1)) * 100) : 0;

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white border-b border-gray-200">
                <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
                    <h1 className="text-2xl font-bold text-black">Covenant Compass</h1>
                    <div className="flex items-center gap-4">
                        <Link to="/alerts" className="relative">
                            <Bell className="w-6 h-6 text-gray-600 hover:text-black" />
                            {summary && summary.unread_alerts > 0 && (
                                <span className="absolute -top-2 -right-2 bg-status-danger text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-semibold">
                                    {summary.unread_alerts}
                                </span>
                            )}
                        </Link>
                    </div>
                </div>
            </header>

            <div className="max-w-7xl mx-auto px-6 py-8">
                {/* Hero Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <MetricCard
                        title="Total Loans"
                        value={summary?.total_loans || 0}
                        subtitle="Active Loans"
                        icon={<TrendingUp className="w-6 h-6" />}
                    />
                    <MetricCard
                        title={`Health: ${portfolioHealth}%`}
                        value={summary?.compliant_covenants || 0}
                        subtitle="Compliant Covenants"
                        icon={<CheckCircle2 className="w-6 h-6 text-status-success" />}
                    />
                    <MetricCard
                        title="Active Alerts"
                        value={summary?.unread_alerts || 0}
                        subtitle="Require Attention"
                        icon={<AlertTriangle className="w-6 h-6 text-status-danger" />}
                        highlight={summary && summary.unread_alerts > 0}
                    />
                    <MetricCard
                        title="At Risk"
                        value={(summary?.warning_covenants || 0) + (summary?.breach_covenants || 0)}
                        subtitle="Approaching Breach"
                        icon={<AlertTriangle className="w-6 h-6 text-status-warning" />}
                    />
                </div>

                {/* Second Row */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                    {/* Risk Heatmap */}
                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                        <h2 className="text-lg font-semibold text-black mb-4">Risk Heatmap</h2>
                        <div className="grid grid-cols-4 gap-3">
                            {heatmap?.slice(0, 12).map((item) => (
                                <Link
                                    key={item.loan_id}
                                    to={`/loans/${item.loan_id}`}
                                    className={`aspect-square border rounded-lg p-2 flex flex-col items-center justify-center text-center hover:shadow-md transition-shadow ${item.status === 'breach' ? 'bg-status-danger/10 border-status-danger' :
                                            item.status === 'warning' ? 'bg-status-warning/10 border-status-warning' :
                                                'bg-status-success/10 border-status-success'
                                        }`}
                                >
                                    <div className="text-xs font-semibold text-black mb-1">
                                        {item.borrower_name?.split(' ').map(w => w[0]).join('') || 'NA'}
                                    </div>
                                    <div className="text-xs text-gray-600">{item.covenant_count}</div>
                                </Link>
                            ))}
                        </div>
                    </div>

                    {/* Alerts Widget */}
                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-lg font-semibold text-black">Recent Alerts</h2>
                            <Link to="/alerts" className="text-sm text-black hover:underline">
                                View all
                            </Link>
                        </div>
                        <div className="space-y-3 max-h-80 overflow-y-auto">
                            {alerts?.map((alert) => (
                                <div key={alert.id} className="flex gap-3 p-3 rounded-lg hover:bg-gray-50">
                                    <div className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${getSeverityColor(alert.severity)}`} />
                                    <div className="flex-1 min-w-0">
                                        <p className="text-sm font-medium text-black truncate">{alert.title}</p>
                                        <p className="text-xs text-gray-600 mt-0.5">{alert.message}</p>
                                        <p className="text-xs text-gray-400 mt-1">{formatRelativeTime(alert.created_at)}</p>
                                    </div>
                                </div>
                            ))}
                            {(!alerts || alerts.length === 0) && (
                                <p className="text-sm text-gray-500 text-center py-8">No alerts</p>
                            )}
                        </div>
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="flex gap-4">
                    <Link
                        to="/loans"
                        className="bg-black text-white px-6 py-3 rounded-lg font-semibold hover:bg-gray-800 transition-colors"
                    >
                        View All Loans
                    </Link>
                </div>
            </div>
        </div>
    );
}

// Helper Components
function MetricCard({ title, value, subtitle, icon, highlight }: {
    title: string;
    value: number;
    subtitle: string;
    icon: React.ReactNode;
    highlight?: boolean;
}) {
    return (
        <div className={`bg-white border rounded-lg p-6 ${highlight ? 'border-status-danger' : 'border-gray-200'}`}>
            <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-600">{title}</span>
                {icon}
            </div>
            <div className="text-4xl font-extrabold text-black font-tabular mb-1">{value}</div>
            <div className="text-sm text-gray-500">{subtitle}</div>
        </div>
    );
}
