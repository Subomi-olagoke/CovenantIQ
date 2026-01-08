import { useQuery } from '@tanstack/react-query';
import { AlertTriangle, CheckCircle } from 'lucide-react';
import api from '../lib/api';
import type { Alert } from '../types';
import Layout from '../components/layout/Layout';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { formatRelativeTime } from '../lib/utils';
// import { getSeverityColor } from '../lib/dashboard-utils';

export default function Alerts() {
    const { data: alerts, isLoading } = useQuery<Alert[]>({
        queryKey: ['alerts'],
        queryFn: async () => {
            const res = await api.get('/api/analytics/critical-alerts'); // Using same endpoint for now, ideally /api/alerts
            return res.data;
        },
    });

    return (
        <Layout title="Alerts">
            <div className="space-y-6 max-w-4xl mx-auto">
                {isLoading ? (
                    <div className="text-center py-12 text-gray-500">Loading alerts...</div>
                ) : alerts && alerts.length > 0 ? (
                    alerts.map((alert) => (
                        <Card key={alert.id} className="flex gap-4 p-5 hover:border-black transition-colors cursor-pointer">
                            <div className={`mt-1 p-2 rounded-full shrink-0 ${alert.severity === 'high' ? 'bg-status-danger-bg text-status-danger' :
                                alert.severity === 'medium' ? 'bg-status-warning-bg text-status-warning' :
                                    'bg-status-info-bg text-status-info'
                                }`}>
                                <AlertTriangle className="w-5 h-5" />
                            </div>

                            <div className="flex-1 min-w-0">
                                <div className="flex justify-between items-start mb-1">
                                    <h3 className="font-semibold text-black">{alert.title}</h3>
                                    <span className="text-xs text-gray-500 whitespace-nowrap ml-4">
                                        {formatRelativeTime(alert.created_at)}
                                    </span>
                                </div>
                                <p className="text-sm text-gray-600 mb-3 leading-relaxed">
                                    {alert.message}
                                </p>

                                <div className="flex items-center gap-2">
                                    <Badge variant={
                                        alert.severity === 'high' ? 'danger' :
                                            alert.severity === 'medium' ? 'warning' : 'info'
                                    }>
                                        {alert.severity.toUpperCase()}
                                    </Badge>
                                    <span className="text-xs text-gray-400">•</span>
                                    <span className="text-xs text-gray-500">
                                        Possible Breach Date: {alert.predicted_breach_date ? new Date(alert.predicted_breach_date).toLocaleDateString() : 'N/A'}
                                    </span>
                                </div>
                            </div>
                        </Card>
                    ))
                ) : (
                    <div className="text-center py-12">
                        <div className="mx-auto w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mb-3">
                            <CheckCircle className="w-6 h-6 text-status-success" />
                        </div>
                        <h3 className="text-lg font-semibold text-black mb-1">All Clear</h3>
                        <p className="text-gray-500">You have no active alerts.</p>
                    </div>
                )}
            </div>
        </Layout>
    );
}
