import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Moon, Sun } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuPortal,
} from '@/components/ui/dropdown-menu';

export default function ThemeToggle() {
  const [theme, setTheme] = useState('dark');

  useEffect(() => {
    const saved = localStorage.getItem('theme') || 'dark';
    setTheme(saved);
    applyTheme(saved);
  }, []);

  function applyTheme(value) {
    const root = document.documentElement;

    root.classList.remove('light', 'dark');
    root.classList.add(value);

    localStorage.setItem('theme', value);
    setTheme(value);
  }

  return (
    <DropdownMenu modal={false}>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          aria-label="Переключить тему"
          className="
            h-9 w-9 rounded-full
            text-[rgb(var(--text-primary))]
            hover:bg-[rgb(var(--accent))]/10
          "
        >
          {theme === 'dark' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
        </Button>
      </DropdownMenuTrigger>

      <DropdownMenuPortal>
        <DropdownMenuContent
          side="bottom"
          align="end"
          sideOffset={8}
          className="
            z-[100]
            min-w-[140px]
            rounded-xl
            border border-[rgb(var(--border))]
            bg-[rgb(var(--bg-header))]
            p-1
            shadow-xl
          "
        >
          <DropdownMenuItem
            onClick={() => applyTheme('light')}
            className="
              flex items-center gap-2 rounded-lg px-3 py-2
              text-[rgb(var(--text-primary))]
              cursor-pointer
              hover:bg-[rgb(var(--accent))]/10
            "
          >
            <Sun className="h-4 w-4" />
            <span>Светлая</span>
            {theme === 'light' && (
              <span className="ml-auto h-2 w-2 rounded-full bg-[rgb(var(--accent))]" />
            )}
          </DropdownMenuItem>

          <DropdownMenuItem
            onClick={() => applyTheme('dark')}
            className="
              flex items-center gap-2 rounded-lg px-3 py-2
              text-[rgb(var(--text-primary))]
              cursor-pointer
              hover:bg-[rgb(var(--accent))]/10
            "
          >
            <Moon className="h-4 w-4" />
            <span>Тёмная</span>
            {theme === 'dark' && (
              <span className="ml-auto h-2 w-2 rounded-full bg-[rgb(var(--accent))]" />
            )}
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenuPortal>
    </DropdownMenu>
  );
}
