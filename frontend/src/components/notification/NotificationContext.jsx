import { createContext, useContext, useState, useCallback } from 'react';

const NotificationContext = createContext(null);

export function NotificationProvider({ children }) {
  const [notifications, setNotifications] = useState([]);

  const removeNotification = useCallback((id) => {
    setNotifications((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const showNotification = useCallback(({ type, title, message, duration = 4000 }) => {
    const id = Date.now();
    setNotifications((prev) => [...prev, { id, type, title, message, duration }]);
    return id;
  }, []);

  const api = {
    notifications,
    removeNotification,
    success: (title, message, duration) =>
      showNotification({ type: 'success', title, message, duration }),
    error: (title, message, duration) =>
      showNotification({ type: 'error', title, message, duration }),
    info: (title, message, duration) =>
      showNotification({ type: 'info', title, message, duration }),
    warning: (title, message, duration) =>
      showNotification({ type: 'warning', title, message, duration }),
  };

  return <NotificationContext.Provider value={api}>{children}</NotificationContext.Provider>;
}

export function useNotificationContext() {
  const ctx = useContext(NotificationContext);
  if (!ctx) {
    throw new Error('useNotification must be used inside NotificationProvider');
  }
  return ctx;
}
