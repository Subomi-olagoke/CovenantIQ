import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number | null, currency: string = "EUR"): string {
    if (amount === null) return "N/A";

    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(amount);
}

export function formatDate(dateString: string | null): string {
    if (!dateString) return "N/A";

    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-GB', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
    }).format(date);
}

export function formatRelativeTime(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;

    return formatDate(dateString);
}

export function getStatusColor(status: string): string {
    switch (status) {
        case 'compliant':
            return 'text-status-success bg-status-success/10';
        case 'warning':
            return 'text-status-warning bg-status-warning/10';
        case 'breach':
            return 'text-status-danger bg-status-danger/10';
        default:
            return 'text-gray-600 bg-gray-100';
    }
}

export function getSeverityColor(severity: string): string {
    switch (severity) {
        case 'critical':
            return 'bg-status-danger';
        case 'high':
            return 'bg-status-danger';
        case 'medium':
            return 'bg-status-warning';
        case 'low':
            return 'bg-status-info';
        default:
            return 'bg-gray-400';
    }
}
