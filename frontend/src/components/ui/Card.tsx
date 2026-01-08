import { type HTMLAttributes, forwardRef } from 'react';
import { cn } from '../../lib/utils';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
    hover?: boolean;
}

const Card = forwardRef<HTMLDivElement, CardProps>(({ className, hover = false, ...props }, ref) => {
    return (
        <div
            ref={ref}
            className={cn(
                "bg-white border border-gray-200 rounded-xl p-6 transition-shadow",
                hover && "cursor-pointer hover:shadow-md",
                className
            )}
            {...props}
        />
    );
});
Card.displayName = "Card";

const MetricCard = ({
    title,
    value,
    subtitle,
    icon,
    trend,
    className
}: {
    title: string;
    value: string | number;
    subtitle: string;
    icon?: React.ReactNode;
    trend?: { value: string; isPositive: boolean };
    className?: string;
}) => {
    return (
        <Card className={cn("min-h-[120px] flex flex-col", className)}>
            <div className="flex justify-between items-start mb-3">
                <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">{title}</span>
                {icon && <span className="text-gray-400">{icon}</span>}
            </div>
            <div className="text-3xl font-bold text-black mb-1">
                {value}
            </div>
            <div className="mt-auto flex items-center justify-between text-sm">
                <span className="text-gray-500">{subtitle}</span>
                {trend && (
                    <span className={cn(
                        "text-xs font-medium",
                        trend.isPositive ? "text-status-success" : "text-status-danger"
                    )}>
                        {trend.value}
                    </span>
                )}
            </div>
        </Card>
    );
};

export { Card, MetricCard };
