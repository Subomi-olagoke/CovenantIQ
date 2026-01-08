import { motion } from 'motion/react';
import { cn } from '../../lib/utils';

interface SkeletonProps {
    className?: string;
    variant?: 'card' | 'text' | 'circle' | 'rect';
}

export function Skeleton({ className, variant = 'rect' }: SkeletonProps) {
    const variants = {
        card: 'h-40 w-full rounded-xl',
        text: 'h-4 w-full rounded',
        circle: 'h-12 w-12 rounded-full',
        rect: 'h-12 w-full rounded-lg',
    };

    return (
        <motion.div
            className={cn(
                'bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 bg-[length:200%_100%]',
                variants[variant],
                className
            )}
            animate={{
                backgroundPosition: ['200% 0', '-200% 0'],
            }}
            transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'linear',
            }}
        />
    );
}

export function SkeletonCard() {
    return (
        <div className="bg-white border border-gray-200 rounded-xl p-6 space-y-4">
            <Skeleton variant="text" className="w-1/3" />
            <Skeleton variant="text" className="w-full h-8" />
            <Skeleton variant="text" className="w-2/3" />
        </div>
    );
}

export function SkeletonMetricCard() {
    return (
        <div className="bg-white border border-gray-200 rounded-xl p-6 space-y-3">
            <Skeleton variant="text" className="w-1/2 h-3" />
            <Skeleton variant="text" className="w-3/4 h-12" />
            <Skeleton variant="text" className="w-1/3 h-3" />
        </div>
    );
}
