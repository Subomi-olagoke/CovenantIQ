export const generateSparklineData = (trend: number) => {
    const data = [];
    let current = 50;
    for (let i = 0; i < 20; i++) {
        current += (Math.random() - 0.5) * 10 * (trend > 0 ? 1.2 : 0.8);
        data.push({ value: current });
    }
    return data;
};

export const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
        case 'high':
        case 'breach':
        case 'danger':
            return 'text-status-danger';
        case 'medium':
        case 'warning':
            return 'text-status-warning';
        case 'low':
        case 'safe':
        case 'compliant':
            return 'text-status-success';
        default:
            return 'text-gray-500';
    }
};
