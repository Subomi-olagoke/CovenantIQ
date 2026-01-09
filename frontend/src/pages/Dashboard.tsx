import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import api from '../lib/api';
import type { PortfolioSummary, Alert, RiskHeatmapItem, PortfolioValueResponse, PortfolioTrendsResponse, CovenantTrendsResponse } from '../types';
import { getSeverityColor } from '../lib/dashboard-utils';
import Layout from '../components/layout/Layout';
import { MetricCard, Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Plus, TrendingUp, TrendingDown, FileText } from 'lucide-react';
import { formatCurrency } from '../lib/utils';
import { LoanUploadModal } from '../components/loans/LoanUploadModal';
import CountUp from 'react-countup';

export default function Dashboard() {
    const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
    const [selectedPeriod, setSelectedPeriod] = useState('week');

    // Fetch portfolio summary
    const { data: summary } = useQuery<PortfolioSummary>({
        queryKey: ['portfolio-summary'],
        queryFn: async () => {
            const res = await api.get('/api/analytics/portfolio-summary');
            return res.data;
        },
    });

    // Fetch heatmap data
    const { data: heatmap, isLoading: loadingHeatmap } = useQuery<RiskHeatmapItem[]>({
        queryKey: ['risk-heatmap'],
        queryFn: async () => {
            const res = await api.get('/api/analytics/risk-heatmap');
            return res.data;
        },
    });

    // Fetch critical alerts
    const { data: alerts, isLoading: loadingAlerts } = useQuery<Alert[]>({
        queryKey: ['critical-alerts'],
        queryFn: async () => {
            const res = await api.get('/api/analytics/critical-alerts');
            return res.data;
        },
    });

    // Fetch portfolio value
    const { data: portfolioValue } = useQuery<PortfolioValueResponse>({
        queryKey: ['portfolio-value'],
        queryFn: async () => {
            const res = await api.get('/api/analytics/portfolio-value');
            return res.data;
        },
    });

    // Fetch portfolio trends
    const { data: portfolioTrends } = useQuery<PortfolioTrendsResponse>({
        queryKey: ['portfolio-trends'],
        queryFn: async () => {
            const res = await api.get('/api/analytics/portfolio-trends');
            return res.data;
        },
    });

    // Fetch covenant trends
    const { data: covenantTrends } = useQuery<CovenantTrendsResponse>({
        queryKey: ['covenant-trends'],
        queryFn: async () => {
            const res = await api.get('/api/analytics/covenant-trends');
            return res.data;
        },
    });

    const portfolioHealth = summary ? (summary.compliant_covenants / summary.total_covenants) * 100 : 0;

    return (
        <Layout
            title="Dashboard"
            actions={
                <div className="flex items-center gap-3">
                    <select
                        value={selectedPeriod}
                        onChange={(e) => setSelectedPeriod(e.target.value)}
                        className="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-black"
                    >
                        <option value="week">Jan 1 '26 - Jan 8 '26</option>
                        <option value="month">Dec '25</option>
                        <option value="year">2025</option>
                        <option value="all">All Time</option>
                    </select>
                    <Button
                        variant="primary"
                        size="sm"
                        onClick={() => setIsUploadModalOpen(true)}
                    >
                        <Plus className="w-4 h-4" />
                        Add Loan
                    </Button>
                </div>
            }
        >
            {/* Main Metric */}
            <div className="mb-8">
                <div className="flex items-baseline gap-3 mb-2">
                    <h2 className="text-4xl font-bold text-black">
                        $<CountUp
                            end={portfolioValue?.current_value || 0}
                            duration={1.5}
                            separator=","
                            decimals={0}
                        />
                    </h2>
                    <span className="text-sm text-gray-500">
                        vs {formatCurrency(portfolioValue?.previous_value || 0)} last period
                    </span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                    <span className="flex items-center gap-1 px-2 py-0.5 bg-gray-100 rounded-full">
                        <span className="w-2 h-2 bg-black rounded-full"></span>
                        Current Period
                    </span>
                    <span className="flex items-center gap-1 px-2 py-0.5 bg-gray-100 rounded-full">
                        <span className="w-2 h-2 bg-gray-400 rounded-full"></span>
                        Last Period
                    </span>
                </div>
            </div>

            {/* Chart */}
            <Card className="mb-6 p-0 overflow-hidden">
                <div className="p-6 pb-0">
                    <div className="h-64 relative">
                        {portfolioTrends ? (
                            <>
                                {/* Y-axis labels - dynamically calculate based on max value */}
                                <div className="absolute left-0 top-0 bottom-8 flex flex-col justify-between text-xs text-gray-400">
                                    {(() => {
                                        const maxVal = Math.max(...portfolioTrends.current_period, ...portfolioTrends.previous_period);
                                        const step = Math.ceil(maxVal / 4);
                                        return [4, 3, 2, 1, 0].map(i => (
                                            <span key={i}>{(step * i).toLocaleString()}</span>
                                        ));
                                    })()}
                                </div>

                                {/* Chart area */}
                                <div className="ml-12 h-full relative">
                                    <svg className="w-full h-full" viewBox="0 0 800 240" preserveAspectRatio="none">
                                        {/* Grid lines */}
                                        <line x1="0" y1="0" x2="800" y2="0" stroke="#E5E5E5" strokeWidth="1" />
                                        <line x1="0" y1="60" x2="800" y2="60" stroke="#E5E5E5" strokeWidth="1" />
                                        <line x1="0" y1="120" x2="800" y2="120" stroke="#E5E5E5" strokeWidth="1" />
                                        <line x1="0" y1="180" x2="800" y2="180" stroke="#E5E5E5" strokeWidth="1" />

                                        {/* Last period line (gray) */}
                                        {(() => {
                                            const maxVal = Math.max(...portfolioTrends.current_period, ...portfolioTrends.previous_period);
                                            return (
                                                <polyline
                                                    points={portfolioTrends.previous_period.map((val, i) =>
                                                        `${(i / (portfolioTrends.previous_period.length - 1)) * 800},${240 - (val / maxVal) * 240}`
                                                    ).join(' ')}
                                                    fill="none"
                                                    stroke="#D4D4D4"
                                                    strokeWidth="2"
                                                />
                                            );
                                        })()}

                                        {/* Current period line (black) */}
                                        {(() => {
                                            const maxVal = Math.max(...portfolioTrends.current_period, ...portfolioTrends.previous_period);
                                            return (
                                                <polyline
                                                    points={portfolioTrends.current_period.map((val, i) =>
                                                        `${(i / (portfolioTrends.current_period.length - 1)) * 800},${240 - (val / maxVal) * 240}`
                                                    ).join(' ')}
                                                    fill="none"
                                                    stroke="#000000"
                                                    strokeWidth="2.5"
                                                />
                                            );
                                        })()}
                                    </svg>
                                </div>

                                {/* X-axis labels */}
                                <div className="flex justify-between text-xs text-gray-400 mt-2 ml-12">
                                    {portfolioTrends.months.map((month, i) => (
                                        <span key={i}>{month}</span>
                                    ))}
                                </div>
                            </>
                        ) : (
                            <div className="h-full flex items-center justify-center text-gray-400 text-sm">
                                Loading chart data...
                            </div>
                        )}
                    </div>
                </div>
            </Card>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <MetricCard
                    title="Total Covenants"
                    value={summary?.total_covenants || 0}
                    subtitle="Across all agreements"
                    icon={<FileText className="w-4 h-4" />}
                />
                <MetricCard
                    title="Compliant"
                    value={summary?.compliant_covenants || 0}
                    subtitle={`${Math.round(portfolioHealth)}% of portfolio`}
                    trend={covenantTrends ? {
                        value: `${covenantTrends.compliant_change > 0 ? '+' : ''}${covenantTrends.compliant_change.toFixed(1)}%`,
                        isPositive: covenantTrends.compliant_change >= 0
                    } : undefined}
                    icon={<TrendingUp className="w-4 h-4" />}
                />
                <MetricCard
                    title="At Risk"
                    value={(summary?.warning_covenants || 0) + (summary?.breach_covenants || 0)}
                    subtitle="Require attention"
                    trend={covenantTrends ? {
                        value: `${covenantTrends.breach_change > 0 ? '+' : ''}${covenantTrends.breach_change.toFixed(1)}%`,
                        isPositive: covenantTrends.breach_change <= 0
                    } : undefined}
                    icon={<TrendingDown className="w-4 h-4" />}
                />
            </div>

            {/* Bottom Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Portfolio Breakdown */}
                <Card className="lg:col-span-2">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="text-sm font-semibold text-black">Portfolio Risk Distribution</h3>
                        <button className="text-xs text-gray-500 hover:text-black transition-colors">View All</button>
                    </div>


                    {loadingHeatmap ? (
                        <div className="h-48 flex items-center justify-center text-gray-400 text-sm">Loading...</div>
                    ) : (
                        <div className="grid grid-cols-8 sm:grid-cols-10 md:grid-cols-12 gap-2">
                            {heatmap?.slice(0, 48).map((item) => (
                                <Link
                                    key={item.loan_id}
                                    to={`/loans/${item.loan_id}`}
                                    className="group relative aspect-square"
                                    title={item.borrower_name || 'Unknown'}
                                >
                                    <div className={`
                                        w-full h-full rounded-md border flex items-center justify-center transition-all text-[10px] font-medium
                                        ${item.status === 'breach' ? 'bg-status-danger-bg border-status-danger-border text-status-danger' :
                                            item.status === 'warning' ? 'bg-status-warning-bg border-status-warning-border text-status-warning' :
                                                'bg-status-success-bg border-status-success-border text-status-success'}
                                        hover:scale-105 hover:shadow-sm hover:z-10
                                    `}>
                                        {item.borrower_name?.substring(0, 2).toUpperCase() || 'NA'}
                                    </div>
                                </Link>
                            ))}
                        </div>
                    )}
                </Card>

                {/* Recent Alerts */}
                <Card>
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="text-sm font-semibold text-black">Recent Alerts</h3>
                        <Link to="/alerts" className="text-xs text-gray-500 hover:text-black transition-colors">
                            View All
                        </Link>
                    </div>
                    <div className="space-y-3">
                        {loadingAlerts ? (
                            <div className="text-sm text-gray-400">Loading...</div>
                        ) : alerts?.length === 0 ? (
                            <div className="text-center text-gray-400 text-sm py-8">No alerts</div>
                        ) : (
                            alerts?.slice(0, 6).map((alert) => (
                                <div
                                    key={alert.id}
                                    className="pb-3 border-b border-gray-100 last:border-0 last:pb-0"
                                >
                                    <div className="flex items-start gap-2">
                                        <div className={`mt-1 w-1.5 h-1.5 rounded-full shrink-0 ${getSeverityColor(alert.severity).replace('text-', 'bg-')}`} />
                                        <div className="flex-1 min-w-0">
                                            <h4 className="text-xs font-medium text-black truncate mb-0.5">
                                                {alert.title}
                                            </h4>
                                            <p className="text-xs text-gray-500 line-clamp-2">
                                                {alert.message}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </Card>
            </div>

            {/* Upload Modal */}
            <LoanUploadModal
                isOpen={isUploadModalOpen}
                onClose={() => setIsUploadModalOpen(false)}
                onSuccess={() => {
                    window.location.reload();
                }}
            />
        </Layout>
    );
}
