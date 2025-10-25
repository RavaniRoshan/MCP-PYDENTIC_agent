// src/utils/dateUtils.ts

// Helper function to convert API date strings to Date objects
export const parseAPIDate = (dateString: string | Date | undefined): Date => {
  if (!dateString) return new Date();
  if (dateString instanceof Date) return dateString;
  return new Date(dateString);
};

// Helper function to format dates for display
export const formatDate = (date: Date): string => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
};

// Helper function to format time only
export const formatTime = (date: Date): string => {
  return new Intl.DateTimeFormat('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
};