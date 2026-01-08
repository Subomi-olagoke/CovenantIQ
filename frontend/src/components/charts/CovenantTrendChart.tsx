import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

interface CovenantTrendChartProps {
    data: any[];
    thresholdValue: number | null;
}

export function CovenantTrendChart({ data, thresholdValue }: CovenantTrendChartProps) {
    if (!data || data.length === 0) {
        return <div className="h-full flex items-center justify-center text-gray-400">No trend data available</div>;
    }

    return (
        <ResponsiveContainer width="100%" height={300}>
            <LineChart
                data={data}
                margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
            >
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E5E5" vertical={false} />

                <XAxis
                    dataKey="date"
                    tick={{ fontSize: 12, fill: '#737373' }}
                    axisLine={{ stroke: '#E5E5E5' }}
                    tickLine={false}
                    dy={10}
                />

                <YAxis
                    tick={{ fontSize: 12, fill: '#737373' }}
                    axisLine={{ stroke: '#E5E5E5' }}
                    tickLine={false}
                    dx={-10}
                />

                <Tooltip
                    contentStyle={{
                        background: '#FFFFFF',
                        border: '1px solid #E5E5E5',
                        borderRadius: '6px',
                        padding: '8px 12px',
                        fontSize: '12px',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                    }}
                    labelStyle={{ color: '#000000', fontWeight: 600, marginBottom: '4px' }}
                    itemStyle={{ color: '#525252', padding: 0 }}
                />

                {thresholdValue && (
                    <ReferenceLine
                        y={thresholdValue}
                        stroke="#EF4444"
                        strokeDasharray="5 5"
                        strokeWidth={2}
                        label={{
                            value: `Threshold: ${thresholdValue}`,
                            position: 'right',
                            fontSize: 12,
                            fill: '#EF4444'
                        }}
                    />
                )}

                <Line
                    type="monotone"
                    dataKey="value"
                    stroke="#000000"
                    strokeWidth={2}
                    dot={{ fill: '#000000', strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6, strokeWidth: 0 }}
                />
            </LineChart>
        </ResponsiveContainer>
    );
}
