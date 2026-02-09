'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface LoadingSpinnerProps {
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  message?: string;
}

export default function LoadingSpinner({
  className,
  size = 'md',
  message = 'Loading...'
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16'
  };

  return (
    <div className="flex flex-col items-center justify-center gap-4">
      <div className="relative">
        {/* Main spinner */}
        <motion.div
          className={cn(
            'rounded-full border-4 border-transparent',
            'border-t-white border-r-cyan-400 border-b-cyan-400',
            sizeClasses[size],
            className
          )}
          animate={{
            rotate: 360
          }}
          transition={{
            duration: 1,
            repeat: Infinity,
            ease: 'linear',
            repeatType: 'loop'
          }}
        />

        {/* Secondary spinner */}
        <motion.div
          className={cn(
            'absolute top-0 left-0 rounded-full border-4 border-transparent',
            'border-b-blue-400 border-l-blue-400',
            sizeClasses[size],
            className
          )}
          animate={{
            rotate: -360
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: 'linear',
            repeatType: 'loop'
          }}
        />

        {/* Center dot */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
          <motion.div
            className="w-2 h-2 bg-white rounded-full"
            animate={{
              scale: [1, 1.2, 1],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              repeatType: 'loop',
              ease: 'easeInOut'
            }}
          />
        </div>
      </div>

      {message && (
        <motion.p
          className="text-gray-400 text-lg font-medium"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          {message}
        </motion.p>
      )}
    </div>
  );
}