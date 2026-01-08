import { type HTMLAttributes, forwardRef } from 'react';
import { cn } from '../../lib/utils';

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
    variant?: 'success' | 'warning' | 'danger' | 'info' | 'neutral';
    dot?: boolean;
}

const Badge = forwardRef<HTMLSpanElement, BadgeProps>(({ className, variant = 'neutral', dot = false, children, ...props }, ref) => {
    const variants = {
        success: 'bg-status-success-bg text-status-success border-status-success-border',
        warning: 'bg-status-warning-bg text-status-warning border-status-warning-border',
        danger: 'bg-status-danger-bg text-status-danger border-status-danger-border',
        info: 'bg-status-info-bg text-status-info border-status-info-border',
        neutral: 'bg-gray-100 text-gray-700 border-gray-200',
    };

    return (
        <span
            ref={ref}
            className={cn(
                "inline-flex items-center px-3 py-1 text-xs font-semibold rounded-full border border-transparent leading-none",
                variants[variant],
                className
            )}
            {...props}
        >
            {dot && (
                <span className={cn(
                    "mr-1.5 h-2 w-2 rounded-full",
                    variant === 'success' && "bg-status-success",
                    variant === 'warning' && "bg-status-warning",
                    variant === 'danger' && "bg-status-danger",
                    variant === 'info' && "bg-status-info",
                    variant === 'neutral' && "bg-gray-500"
                )} />
            )}
            {children}
        </span>
    );
});

Badge.displayName = "Badge";

export { Badge };
