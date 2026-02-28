import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Moon, Sun } from 'lucide-react';
import { applyTheme } from '@/lib/theme';

function ThemeToggleInner({ isDark, toggleTheme }) {
  return (
    <Button
      variant="ghost"
      size="icon"
      aria-label="Переключить тему"
      onClick={toggleTheme}
      className="
        h-9 w-9 rounded-full
        text-[rgb(var(--text-primary))]
        hover:bg-[rgb(var(--accent))]/10
        transition-all
      "
    >
      {isDark ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
    </Button>
  );
}

function getInitialDarkMode() {
  if (typeof window === 'undefined') return false;
  const saved = localStorage.getItem('theme');
  return saved === 'dark';
}

export default function ThemeToggle() {
  const [isDark, setIsDark] = useState(getInitialDarkMode);

  const toggleTheme = () => {
    const newTheme = isDark ? 'light' : 'dark';
    applyTheme(newTheme);
    setIsDark(!isDark);
  };

  return <ThemeToggleInner isDark={isDark} toggleTheme={toggleTheme} />;
}
