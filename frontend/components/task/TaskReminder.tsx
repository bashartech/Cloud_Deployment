'use client';

import { useEffect, useRef } from 'react';
import { Task } from '@/lib/api';
import { toast } from 'sonner';

interface TaskReminderProps {
  tasks: Task[];
}

export default function TaskReminder({ tasks }: TaskReminderProps) {
  const scheduledRemindersRef = useRef<Record<number, number>>({});

  useEffect(() => {
    // Clear any previously scheduled reminders
    Object.values(scheduledRemindersRef.current).forEach(timeoutId => {
      clearTimeout(timeoutId);
    });
    scheduledRemindersRef.current = {};

    // Schedule reminders for tasks that have reminder_at set
    tasks.forEach(task => {
      if (task.reminder_at && !task.completed) {
        try {
          // Parse the reminder time - handle ISO string properly
          const reminderDate = new Date(task.reminder_at);
          const reminderTime = reminderDate.getTime();
          const currentTime = Date.now();
          const timeUntilReminder = reminderTime - currentTime;

          console.log(`Task ${task.id}: reminder set for ${reminderDate}, current time: ${new Date()}, time until: ${timeUntilReminder}ms`);

          // Only schedule if the reminder is in the future (positive time difference)
          if (timeUntilReminder > 0) {
            const timeoutId = window.setTimeout(() => {
              console.log(`Executing reminder for task: ${task.title}`);
              showNotification(task);
              // Remove the timeout ID from our reference after execution
              delete scheduledRemindersRef.current[task.id];
            }, timeUntilReminder);

            // Store the timeout ID so we can clear it later if needed
            scheduledRemindersRef.current[task.id] = timeoutId;
          } else if (timeUntilReminder < 0) {
            // The reminder time has already passed, potentially show notification immediately or skip
            console.log(`Reminder for task ${task.id} was scheduled in the past: ${Math.abs(timeUntilReminder)}ms ago`);
          }
        } catch (error) {
          console.error('Error parsing reminder date for task:', task.id, error);
        }
      }
    });

    // Cleanup function to clear all scheduled reminders when component unmounts
    return () => {
      Object.values(scheduledRemindersRef.current).forEach(timeoutId => {
        clearTimeout(timeoutId);
      });
      scheduledRemindersRef.current = {};
    };
  }, [tasks]);

  const showNotification = (task: Task) => {
    console.log('Attempting to show toast notification for task:', task.title);

    // Use sonner toast notification instead of browser notification
    toast.info(`⏰ Task Reminder: ${task.title}`, {
      description: task.description || 'Time to work on this task!',
      duration: 8000, // Show for 8 seconds
      action: {
        label: 'View Dashboard',
        onClick: () => {
          // Navigate to dashboard or focus the window
          window.location.href = '/dashboard';
        },
      },
    });
  };

  return null; // This component doesn't render anything visible
}