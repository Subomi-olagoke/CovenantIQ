import { type ButtonHTMLAttributes, forwardRef } from 'react';
import { Loader2 } from 'lucide-react';
import { cn } from '../../lib/utils';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'ghost' | 'icon';
    size?: 'sm' | 'default' | 'lg';
    loading?: boolean;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(({
    className,
    variant = 'primary',
    size = 'default',
    loading = false,
    children,
    disabled,
    ...props
}, ref) => {

    const baseStyles = 'inline-flex items-center justify-center font-medium rounded-lg transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-black focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none';

    const variants = {
        primary: 'bg-black text-white hover:bg-gray-800',
        secondary: 'bg-white text-black border-2 border-black hover:bg-gray-50',
        ghost: 'bg-transparent text-gray-600 hover:bg-gray-100 hover:text-black',
        icon: 'bg-transparent text-gray-600 hover:bg-gray-100 hover:text-black p-0',
    };

    const sizes = {
        sm: 'h-8 px-3 text-xs',
        default: 'h-10 px-4 text-sm',
        lg: 'h-11 px-6 text-sm',
    };

    const iconSize = variant === 'icon' ? 'h-9 w-9' : '';

    return (
        <button
            ref={ref}
            className={cn(
                baseStyles,
                variants[variant],
                variant !== 'icon' && sizes[size],
                iconSize,
                className
            )}
            disabled={disabled || loading}
            {...props}
        >
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {children}
        </button>
    );
});

Button.displayName = 'Button';

export { Button };
