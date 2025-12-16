import { Briefcase, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Logo({ size = 'default', showText = true }) {
  const sizes = {
    small: {
      container: 'h-10 w-10 rounded-lg',
      icon: 'h-5 w-5',
      badge: 'h-4 w-4',
      sparkles: 'h-2 w-2',
      text: 'text-xl',
      subtitle: 'text-xs',
    },
    default: {
      container: 'h-14 w-14 rounded-2xl',
      icon: 'h-7 w-7',
      badge: 'h-6 w-6',
      sparkles: 'h-3 w-3',
      text: 'text-3xl',
      subtitle: 'text-xs',
    },
    large: {
      container: 'h-16 w-16 rounded-2xl',
      icon: 'h-8 w-8',
      badge: 'h-7 w-7',
      sparkles: 'h-3.5 w-3.5',
      text: 'text-4xl',
      subtitle: 'text-sm',
    },
  };

  const sizeConfig = sizes[size];

  return (
    <Link to="/" className="flex items-center gap-3 hover:opacity-90 transition-opacity">
      <div
        className={`${sizeConfig.container} bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 
                      flex items-center justify-center shadow-2xl shadow-blue-500/40 relative`}
      >
        <Briefcase className={`${sizeConfig.icon} text-white`} />
        <div
          className={`absolute -top-1 -right-1 ${sizeConfig.badge} bg-gradient-to-br from-amber-400 to-orange-500 
                      rounded-full flex items-center justify-center shadow-lg`}
        >
          <Sparkles className={`${sizeConfig.sparkles} text-white`} />
        </div>
      </div>

      {showText && (
        <div>
          <div
            className={`${sizeConfig.text} font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 
                         bg-clip-text text-transparent`}
          >
            JobHub
          </div>
          <div
            className={`${sizeConfig.subtitle} bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent`}
          >
            Smart Career Platform
          </div>
        </div>
      )}
    </Link>
  );
}
