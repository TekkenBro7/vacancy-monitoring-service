import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';

export default function App() {
  const [dark, setDark] = useState(false);

  useEffect(() => {
    if (dark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [dark]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-4 bg-background text-foreground transition-colors">
      <div className="text-3xl font-bold">Tailwind v4 + shadcn/ui ✅</div>
      <Button>Primary Button</Button>
      <Button onClick={() => setDark(!dark)}>Переключить {dark ? 'Светлую' : 'Темную'} тему</Button>
    </div>
  );
}
