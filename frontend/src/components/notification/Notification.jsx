import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';

const ICONS = {
  success: CheckCircle,
  error: XCircle,
  warning: AlertTriangle,
  info: Info,
};

const COLORS = {
  success: {
    bg: 'bg-gradient-to-r from-emerald-500/15 to-teal-500/15',
    border: 'border-emerald-500/30',
    text: 'text-emerald-100',
    icon: 'text-emerald-400',
    accent: 'from-emerald-400 to-teal-400',
    shadow: 'shadow-lg shadow-emerald-500/20',
  },
  error: {
    bg: 'bg-gradient-to-r from-rose-500/15 to-red-500/15',
    border: 'border-rose-500/30',
    text: 'text-rose-100',
    icon: 'text-rose-400',
    accent: 'from-rose-400 to-red-400',
    shadow: 'shadow-lg shadow-rose-500/20',
  },
  warning: {
    bg: 'bg-gradient-to-r from-amber-500/15 to-orange-500/15',
    border: 'border-amber-500/30',
    text: 'text-amber-100',
    icon: 'text-amber-400',
    accent: 'from-amber-400 to-orange-400',
    shadow: 'shadow-lg shadow-amber-500/20',
  },
  info: {
    bg: 'bg-gradient-to-r from-blue-500/15 to-cyan-500/15',
    border: 'border-blue-500/30',
    text: 'text-blue-100',
    icon: 'text-blue-400',
    accent: 'from-blue-400 to-cyan-400',
    shadow: 'shadow-lg shadow-blue-500/20',
  },
};

export default function Notification({ notification, onClose }) {
  const [isExiting, setIsExiting] = useState(false);
  const [progress, setProgress] = useState(100);
  const progressRef = useRef(null);
  const exitTimerRef = useRef(null);

  const Icon = ICONS[notification.type];
  const colors = COLORS[notification.type];

  const cleanupTimers = () => {
    if (progressRef.current) {
      clearInterval(progressRef.current);
      progressRef.current = null;
    }
    if (exitTimerRef.current) {
      clearTimeout(exitTimerRef.current);
      exitTimerRef.current = null;
    }
  };

  const startExit = () => {
    if (isExiting) return;
    setIsExiting(true);

    setTimeout(() => {
      onClose?.();
    }, 300);
  };

  useEffect(() => {
    if (!notification.duration) return;

    const interval = 50;
    const totalSteps = notification.duration / interval;
    const step = 100 / totalSteps;

    progressRef.current = setInterval(() => {
      setProgress((prev) => {
        const newProgress = prev - step;
        if (newProgress <= 0) {
          cleanupTimers();
          startExit();
          return 0;
        }
        return newProgress;
      });
    }, interval);

    exitTimerRef.current = setTimeout(() => {
      cleanupTimers();
      startExit();
    }, notification.duration);

    return () => {
      cleanupTimers();
    };
  }, [notification.duration]);

  const handleCloseClick = () => {
    cleanupTimers();
    startExit();
  };

  return (
    <div
      className={`
        relative min-w-[320px] max-w-md rounded-xl backdrop-blur-sm
        border ${colors.border} ${colors.bg} ${colors.shadow}
        transition-all duration-300 transform
        ${isExiting ? 'opacity-0 translate-x-20' : 'opacity-100 translate-x-0'}
        overflow-hidden
      `}
    >
      <div className="absolute top-0 left-0 right-0 h-0.5 bg-gray-800/30">
        <div
          className={`h-full bg-gradient-to-r ${colors.accent} transition-all duration-100`}
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="p-4">
        <div className="flex items-start gap-3">
          <div
            className={`relative flex-shrink-0 p-2 rounded-lg bg-gradient-to-br ${colors.accent}/10 border ${colors.border}`}
          >
            <Icon className={`h-5 w-5 ${colors.icon} relative z-10`} />
            <div className={`absolute inset-0 bg-gradient-to-br ${colors.accent}/5 blur-sm`} />
          </div>

          <div className="flex-1 min-w-0">
            <h4 className={`font-semibold ${colors.text} text-base`}>{notification.title}</h4>
            {notification.message && (
              <p className={`text-sm ${colors.text}/90 mt-1 break-words leading-relaxed`}>
                {notification.message}
              </p>
            )}
          </div>

          <button
            onClick={handleCloseClick}
            className={`
              flex-shrink-0 p-2 rounded-lg transition-all
              hover:bg-white/10 active:scale-95
              ${colors.icon}
              cursor-pointer  
            `}
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-bl from-white/3 to-transparent rounded-full -translate-y-1/2 translate-x-1/2" />
      <div className="absolute bottom-0 left-0 w-16 h-16 bg-gradient-to-tr from-white/2 to-transparent rounded-full translate-y-1/2 -translate-x-1/2" />
    </div>
  );
}
