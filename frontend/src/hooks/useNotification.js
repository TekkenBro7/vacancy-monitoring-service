import { useCallback } from 'react';
import toast from 'react-hot-toast';

export default function useNotification() {
  return {
    success: useCallback((title, message) => {
      if (message) {
        toast.success(`${title}: ${message}`);
      } else {
        toast.success(title);
      }
    }, []),
    error: useCallback((title, message) => {
      if (message) {
        toast.error(`${title}: ${message}`);
      } else {
        toast.error(title);
      }
    }, []),
    info: useCallback((title, message) => {
      if (message) {
        toast(`${title}: ${message}`, { icon: 'ℹ️' });
      } else {
        toast(title, { icon: 'ℹ️' });
      }
    }, []),
    warning: useCallback((title, message) => {
      if (message) {
        toast(`${title}: ${message}`, { icon: '⚠️' });
      } else {
        toast(title, { icon: '⚠️' });
      }
    }, []),
  };
}
