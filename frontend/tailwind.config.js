/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                black: '#000000',
                white: '#FFFFFF',
                gray: {
                    50: '#FAFAFA',
                    100: '#F5F5F5',
                    200: '#E5E5E5',
                    300: '#D4D4D4',
                    400: '#A3A3A3',
                    500: '#737373',
                    600: '#525252',
                    700: '#404040',
                    800: '#262626',
                    900: '#171717',
                },
                status: {
                    success: '#10B981',
                    'success-bg': 'rgba(16, 185, 129, 0.1)',
                    'success-border': 'rgba(16, 185, 129, 0.3)',
                    warning: '#F59E0B',
                    'warning-bg': 'rgba(245, 158, 11, 0.1)',
                    'warning-border': 'rgba(245, 158, 11, 0.3)',
                    danger: '#EF4444',
                    'danger-bg': 'rgba(239, 68, 68, 0.1)',
                    'danger-border': 'rgba(239, 68, 68, 0.3)',
                    info: '#3B82F6',
                    'info-bg': 'rgba(59, 130, 246, 0.1)',
                    'info-border': 'rgba(59, 130, 246, 0.3)',
                },
            },
            fontFamily: {
                sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
            },
            borderRadius: {
                sm: '4px',
                md: '8px',
                lg: '12px',
                xl: '16px',
                '2xl': '24px',
                '3xl': '32px',
                full: '9999px',
            },
            spacing: {
                // 8px base unit system extension if needed beyond default tailwind
                18: '4.5rem',
                28: '7rem',
                128: '32rem',
            },
            boxShadow: {
                sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
                DEFAULT: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)',
                md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
                lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)',
                xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
                '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
                focus: '0 0 0 3px rgba(0, 0, 0, 0.1)',
                glow: '0 0 20px rgba(0, 0, 0, 0.1)',
                'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.1)',
            },
            backdropBlur: {
                xs: '2px',
                sm: '4px',
                md: '8px',
                lg: '12px',
                xl: '16px',
            },
            animation: {
                fadeIn: 'fadeIn 200ms ease-out',
                slideUp: 'slideUp 200ms ease-out',
                slideInRight: 'slideInRight 200ms ease-out',
                shimmer: 'shimmer 1.5s ease-in-out infinite',
                'bounce-subtle': 'bounceSubtle 0.5s ease-out',
                'scale-in': 'scaleIn 200ms ease-out',
                'slide-down': 'slideDown 200ms ease-out',
                'glow': 'glow 2s ease-in-out infinite',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                slideUp: {
                    '0%': { opacity: '0', transform: 'translateY(20px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
                slideDown: {
                    '0%': { opacity: '0', transform: 'translateY(-20px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
                slideInRight: {
                    '0%': { opacity: '0', transform: 'translateX(100%)' },
                    '100%': { opacity: '1', transform: 'translateX(0)' },
                },
                shimmer: {
                    '0%': { backgroundPosition: '-200% 0' },
                    '100%': { backgroundPosition: '200% 0' },
                },
                bounceSubtle: {
                    '0%, 100%': { transform: 'scale(1)' },
                    '50%': { transform: 'scale(1.05)' },
                },
                scaleIn: {
                    '0%': { opacity: '0', transform: 'scale(0.95)' },
                    '100%': { opacity: '1', transform: 'scale(1)' },
                },
                glow: {
                    '0%, 100%': { opacity: '1' },
                    '50%': { opacity: '0.5' },
                },
            },
        },
    },
    plugins: [],
}
