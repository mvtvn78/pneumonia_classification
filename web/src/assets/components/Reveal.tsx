import React, { useEffect, useRef, ReactNode } from 'react';
import { motion, useInView, useAnimation } from 'framer-motion';

interface RevealProps {
    children: ReactNode;
    index_Delay?: number;
    dur?: number;
    onlyOpacity?: boolean;
}

const Reveal: React.FC<RevealProps> = ({ children, index_Delay = 0.2, dur = 1, onlyOpacity = false }) => {
    // make ref for element to detect if the element is visible
    const ref = useRef<HTMLDivElement | null>(null);
    const isInview = useInView(ref, { once: true });
    // using useAnimation Hook to manage your animation 
    const mainControls = useAnimation();
    const ops = {
        hidden: { opacity: 0.1, y: 50 },
        intialonlyOpacity: { opacity: 0 },
        visible: { opacity: 1, y: 0 },
    };
    // if element is visible then element will start animation
    useEffect(() => {
        if (isInview) {
            mainControls.start("visible");
        }
    }, [isInview, mainControls]);

    return (
        <div ref={ref}>
            <motion.div
                variants={ops}
                // initial state
                initial={onlyOpacity ? "intialonlyOpacity" : "hidden"}
                // where you put effect to use
                animate={mainControls}
                // using attr transition to make smooth effect
                transition={{ duration: dur, delay: index_Delay }}
            >
                {children}
            </motion.div>
        </div>
    );
};

export default Reveal;

