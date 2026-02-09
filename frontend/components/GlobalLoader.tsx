'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';
import LoadingSpinner from './LoadingSpinner';

export default function GlobalLoader() {
  const pathname = usePathname();
  const [isLoading, setIsLoading] = useState(false);
  const [showLoader, setShowLoader] = useState(false);

  // Show loader when navigating to new routes
  useEffect(() => {
    setIsLoading(true);

    // Show loader after a short delay to prevent flickering
    const showTimer = setTimeout(() => {
      setShowLoader(true);
    }, 100);

    // Hide loader after a short time to allow for smooth transition
    const hideTimer = setTimeout(() => {
      setShowLoader(false);
      setIsLoading(false);
    }, 1000);

    return () => {
      clearTimeout(showTimer);
      clearTimeout(hideTimer);
    };
  }, [pathname]);

  return (
    <AnimatePresence>
      {showLoader && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-gradient-to-br from-black via-neutral-900 to-black"
        >
          <div className="flex flex-col items-center justify-center gap-8">
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.2, type: 'spring', stiffness: 100 }}
            >
              <LoadingSpinner size="lg" message="Loading application..." />
            </motion.div>

            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="text-center"
            >
              <motion.h2
                className="text-2xl font-bold bg-gradient-to-r from-white via-blue-200 to-cyan-200 bg-clip-text text-transparent"
                animate={{
                  backgroundPosition: ['0% 50%', '100% 50%', '0% 50%']
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  ease: 'linear'
                }}
              >
                Todo App
              </motion.h2>
              <motion.p
                className="text-gray-400 mt-2"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.7 }}
              >
                Organize, prioritize, and achieve your goals
              </motion.p>
            </motion.div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}