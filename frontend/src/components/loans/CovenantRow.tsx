import { useState } from 'react';
import { ChevronDown, TrendingUp, AlertTriangle } from 'lucide-react';
// import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { CovenantTrendChart } from '../charts/CovenantTrendChart';
import type { Covenant } from '../../types';

interface CovenantRowProps {
    covenant: Covenant;
}

export function CovenantRow({ covenant }: CovenantRowProps) {
    const [expanded, setExpanded] = useState(false);

    // Mock trend data for visualization (replace with real data if available in future)
    const mockData = [
        { date: 'Q1 2023', value: covenant.threshold_value ? covenant.threshold_value * 0.8 : 10 },
        { date: 'Q2 2023', value: covenant.threshold_value ? covenant.threshold_value * 0.85 : 12 },
        { date: 'Q3 2023', value: covenant.threshold_value ? covenant.threshold_value * 0.9 : 11 },
        { date: 'Q4 2023', value: covenant.latest_value || (covenant.threshold_value ? covenant.threshold_value * 0.9 : 13) },
    ];

    return (
        <div
            className={`border rounded-lg p-5 mb-4 transition-all duration-200 cursor-pointer ${expanded ? 'border-black shadow-sm ring-1 ring-black/5' : 'border-gray-200 hover:border-gray-300'}`}
            onClick={() => setExpanded(!expanded)}
        >
            {/* Header Row */}
            <div className="grid grid-cols-12 gap-6 items-center">
                <div className="col-span-5">
                    <h3 className="text-base font-semibold text-black">{covenant.covenant_name}</h3>
                    <p className="text-xs text-gray-500 uppercase tracking-wider mt-1">{covenant.covenant_type}</p>
                </div>

                <div className="col-span-2">
                    <div className="flex flex-col">
                        <span className="text-xl font-bold text-black font-tabular">
                            {covenant.latest_value?.toFixed(2) || '-'}x
                        </span>
                        {covenant.latest_value && (
                            <span className="text-xs font-semibold text-status-success flex items-center gap-1">
                                <TrendingUp className="w-3 h-3" /> +0.2x
                            </span>
                        )}
                    </div>
                </div>

                <div className="col-span-2 text-sm text-gray-600">
                    <span className="block text-xs text-gray-400 uppercase">Threshold</span>
                    <span className="font-medium">{covenant.threshold_operator} {covenant.threshold_value}x</span>
                </div>

                <div className="col-span-2">
                    <Badge variant={
                        covenant.latest_status === 'compliant' ? 'success' :
                            covenant.latest_status === 'warning' ? 'warning' :
                                covenant.latest_status === 'breach' ? 'danger' : 'neutral'
                    }>
                        {covenant.latest_status?.toUpperCase() || 'UNKNOWN'}
                    </Badge>
                </div>

                <div className="col-span-1 flex justify-end">
                    <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${expanded ? 'rotate-180' : ''}`} />
                </div>
            </div>

            {/* Expanded Content */}
            {expanded && (
                <div className="mt-6 pt-6 border-t border-gray-100 grid grid-cols-3 gap-8 cursor-default" onClick={e => e.stopPropagation()}>
                    <div className="col-span-2 h-[300px]">
                        <h4 className="text-sm font-semibold text-black mb-4">Historical Performance</h4>
                        <CovenantTrendChart data={mockData} thresholdValue={covenant.threshold_value} />
                    </div>
                    <div className="space-y-6">
                        <div>
                            <h4 className="text-sm font-semibold text-black mb-2">Description</h4>
                            <p className="text-sm text-gray-600 leading-relaxed">
                                {covenant.description || "No description provided."}
                            </p>
                        </div>

                        {/* Prediction Warning (Mock) */}
                        <div className="bg-status-warning-bg border border-status-warning-border rounded-md p-3 flex gap-3">
                            <AlertTriangle className="w-5 h-5 text-status-warning shrink-0" />
                            <div>
                                <h5 className="text-sm font-semibold text-black mb-1">Breach Predicted</h5>
                                <p className="text-xs text-gray-700">AI forecasts potential breach in Q3 2024 based on current EBIT trends.</p>
                                <p className="text-xs text-gray-600 mt-1 font-medium">Confidence: 85%</p>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
