import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Moon, Sun } from 'lucide-react';

export default function ThemeToggle() {
  const [theme, setTheme] = useState('dark');

  useEffect(() => {
    const saved = localStorage.getItem('theme') || 'dark';
    applyTheme(saved);
  }, []);

  function applyTheme(value) {
    const root = document.documentElement;

    root.classList.remove('light', 'dark');
    root.classList.add(value);

    localStorage.setItem('theme', value);
    setTheme(value);
  }

  function toggleTheme() {
    applyTheme(theme === 'dark' ? 'light' : 'dark');
  }

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
      {theme === 'dark' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
    </Button>
  );
}
