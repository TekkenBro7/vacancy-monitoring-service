import Notification from './Notification';
import { useNotificationContext } from './NotificationContext';
import './notification-styles.css';

export default function NotificationContainer() {
  const { notifications, removeNotification } = useNotificationContext();

  if (!notifications.length) return null;

  return (
    <div className="fixed inset-x-0 top-24 z-[100] pointer-events-none">
      <div className="container mx-auto px-4">
        <div className="flex flex-col items-end gap-3">
          {notifications.map((notification) => (
            <div
              key={notification.id}
              className="pointer-events-auto animate-notification-slide-in"
            >
              <Notification
                notification={notification}
                onClose={() => removeNotification(notification.id)}
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
