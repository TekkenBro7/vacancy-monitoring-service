import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Moon, Sun, Monitor } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

export default function ThemeToggle() {
  const [theme, setTheme] = useState('light');

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    applyTheme(savedTheme);
  }, []);

  function applyTheme(newTheme) {
    const root = document.documentElement;
    root.classList.remove('light', 'dark');

    if (newTheme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light';
      root.classList.add(systemTheme);
    } else {
      root.classList.add(newTheme);
    }

    localStorage.setItem('theme', newTheme);
    setTheme(newTheme);
  }

  function toggleTheme() {
    const next = theme === 'dark' ? 'light' : 'dark';
    applyTheme(next);
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="h-9 w-9 relative hover:bg-accent"
          aria-label="Переключить тему"
        >
          <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0 text-foreground" />
          <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100 text-foreground" />
          <span className="sr-only">Переключить тему</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-40">
        <DropdownMenuItem
          onClick={() => applyTheme('light')}
          className="flex items-center gap-2 cursor-pointer hover:bg-accent"
        >
          <Sun className="h-4 w-4" />
          <span>Светлая</span>
          {theme === 'light' && <span className="ml-auto h-2 w-2 rounded-full bg-primary"></span>}
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={() => applyTheme('dark')}
          className="flex items-center gap-2 cursor-pointer hover:bg-accent"
        >
          <Moon className="h-4 w-4" />
          <span>Темная</span>
          {theme === 'dark' && <span className="ml-auto h-2 w-2 rounded-full bg-primary"></span>}
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={() => applyTheme('system')}
          className="flex items-center gap-2 cursor-pointer hover:bg-accent"
        >
          <Monitor className="h-4 w-4" />
          <span>Системная</span>
          {theme === 'system' && <span className="ml-auto h-2 w-2 rounded-full bg-primary"></span>}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
