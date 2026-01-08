import { motion, AnimatePresence } from 'motion/react';
import { type ReactNode } from 'react';

interface PageTransitionProps {
    children: ReactNode;
    className?: string;
}

const pageVariants = {
    initial: {
        opacity: 0,
        y: 20,
    },
    animate: {
        opacity: 1,
        y: 0,
    },
    exit: {
        opacity: 0,
        y: -20,
    },
};

const pageTransition = {
    type: "tween" as const,
    ease: "anticipate" as const,
    duration: 0.4,
};

export function PageTransition({ children, className }: PageTransitionProps) {
    return (
        <motion.div
            className={className}
            initial="initial"
            animate="animate"
            exit="exit"
            variants={pageVariants}
            transition={pageTransition}
        >
            {children}
        </motion.div>
    );
}

export function AnimatedPresenceWrapper({ children }: { children: ReactNode }) {
    return (
        <AnimatePresence mode="wait">
            {children}
        </AnimatePresence>
    );
}
