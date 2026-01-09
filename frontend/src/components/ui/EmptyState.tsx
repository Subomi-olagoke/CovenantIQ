import { FileText } from 'lucide-react';
import { Button } from '../ui/Button';

interface EmptyStateProps {
    icon?: React.ReactNode;
    title: string;
    description: string;
    actionLabel?: string;
    onAction?: () => void;
}

export const EmptyState = ({
    icon,
    title,
    description,
    actionLabel,
    onAction
}: EmptyStateProps) => {
    return (
        <div className="flex flex-col items-center justify-center py-16 px-4">
            <div className="text-gray-300 mb-4">
                {icon || <FileText className="w-16 h-16" />}
            </div>
            <h3 className="text-lg font-semibold text-black mb-2">{title}</h3>
            <p className="text-sm text-gray-600 mb-6 text-center max-w-md">{description}</p>
            {actionLabel && onAction && (
                <Button onClick={onAction}>
                    {actionLabel}
                </Button>
            )}
        </div>
    );
};
