import { type InputHTMLAttributes, forwardRef } from 'react';
import { cn } from '../../lib/utils';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
    label?: string;
    error?: string;
    helper?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(({ className, label, error, helper, ...props }, ref) => {
    return (
        <div className="w-full mb-4">
            {label && (
                <label className="block text-sm font-medium text-black mb-1.5">
                    {label}
                </label>
            )}
            <input
                ref={ref}
                className={cn(
                    "w-full px-3 py-2 text-sm bg-white border border-gray-300 rounded-lg transition-colors placeholder:text-gray-400 focus:outline-none focus:border-black focus:ring-1 focus:ring-black disabled:bg-gray-50 disabled:text-gray-500",
                    error && "border-status-danger focus:border-status-danger focus:ring-status-danger",
                    className
                )}
                {...props}
            />
            {error && <p className="mt-1.5 text-xs text-status-danger font-medium">{error}</p>}
            {helper && !error && <p className="mt-1.5 text-xs text-gray-500">{helper}</p>}
        </div>
    );
});

Input.displayName = 'Input';

export { Input };
