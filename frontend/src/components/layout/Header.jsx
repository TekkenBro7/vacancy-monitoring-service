import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, User, LogOut, Shield } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Link } from 'react-router-dom';
import Logo from '@/components/ui_my/Logo';
import ThemeToggle from '@/components/ui_my/ThemeToggle';
import { useAuth } from '@/utils/AuthContext';

export default function Header() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const { isAuthenticated, user, logout, isLoading } = useAuth();

  if (isLoading) return null;

  return (
    <header
      className="
        sticky top-0 z-50 w-full border-b
        bg-[rgb(var(--bg-header))]
        border-[rgb(var(--border))]
        backdrop-blur-xl
        shadow-xl
        transition-colors
      "
    >
      <div className="absolute inset-0 opacity-[0.04] dark:opacity-[0.02] pointer-events-none">
        <div
          className="h-full w-full"
          style={{
            backgroundImage: `
              linear-gradient(to right, rgb(var(--text-primary)) 1px, transparent 1px),
              linear-gradient(to bottom, rgb(var(--text-primary)) 1px, transparent 1px)
            `,
            backgroundSize: '40px 40px',
          }}
        />
      </div>

      <div className="absolute top-8 right-10 w-40 h-40 bg-[rgb(var(--accent))]/10 rounded-full blur-3xl" />
      <div className="absolute bottom-8 left-10 w-32 h-32 bg-purple-500/10 rounded-full blur-3xl" />

      <div className="container mx-auto px-6 relative z-10">
        <div className="flex h-20 items-center justify-between gap-4">
          <Logo size="default" showText />

          <div className="hidden xl:flex flex-1 max-w-2xl mx-8">
            <div className="relative w-full">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-[rgb(var(--accent))]" />
              <Input
                type="search"
                placeholder="Поиск вакансий, должностей, компаний..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="
                  h-12 pl-12 pr-24 rounded-full
                  bg-[rgb(var(--bg-header-muted))]
                  text-[rgb(var(--text-primary))]
                  placeholder:text-[rgb(var(--text-muted))]
                  border border-[rgb(var(--border))]
                  focus:ring-2 focus:ring-[rgb(var(--accent))]/40
                "
              />
              <Button
                className="
                  absolute right-2 top-1/2 -translate-y-1/2
                  h-8 px-4 rounded-full text-sm font-medium
                  transition-all duration-300
                  hover:scale-105
                  active:scale-95
                  hover:shadow-lg
                "
                style={{
                  background: `
                    linear-gradient(
                      135deg,
                      rgb(var(--button-from)),
                      rgb(var(--button-to))
                    )
                  `,
                  color: 'white',
                }}
              >
                Найти
              </Button>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <ThemeToggle />

            {isAuthenticated && user?.role_name === 'admin' && (
              <Button
                variant="ghost"
                onClick={() => navigate('/admin')}
                className="
                  transition-all duration-300
                  hover:bg-[rgb(var(--accent))]/10
                  hover:shadow-sm
                  hover:scale-[1.03]
                "
              >
                <Shield className="h-4 w-4 mr-2" style={{ color: 'rgb(var(--accent))' }} />
                Админка
              </Button>
            )}

            {!isAuthenticated ? (
              <>
                <Button
                  variant="ghost"
                  asChild
                  className="
                    transition-all duration-300
                    hover:bg-[rgb(var(--accent))]/10
                    hover:shadow-sm
                    hover:scale-[1.03]
                  "
                >
                  <Link to="/login" className="flex items-center gap-2">
                    <User className="h-4 w-4" />
                    Войти
                  </Link>
                </Button>

                <Button
                  asChild
                  className="
                    relative overflow-hidden
                    transition-all duration-300
                    hover:scale-105 active:scale-95
                    hover:shadow-xl

                    before:absolute before:inset-0
                    before:bg-white/10
                    before:opacity-0
                    before:transition-opacity

                    dark:before:bg-white/5

                    hover:before:opacity-100
                  "
                  style={{
                    background: `
                      linear-gradient(
                        135deg,
                        rgb(var(--button-from)),
                        rgb(var(--button-to))
                      )
                    `,
                    color: 'white',
                  }}
                >
                  <Link to="/register">Регистрация</Link>
                </Button>
              </>
            ) : (
              <div className="flex items-center gap-3">
                <div
                  className="
                    flex items-center gap-3 px-4 py-2 rounded-xl
                    bg-[rgb(var(--bg-header-muted))]
                    border border-[rgb(var(--border))]
                    cursor-pointer
                    transition-all duration-300
                    hover:scale-105 active:scale-95
                    hover:shadow-md
                  "
                  onClick={() => navigate('/profile')}
                >
                  <div className="h-9 w-9 rounded-full bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center">
                    <span className="text-white font-bold text-sm">
                      {user?.username?.charAt(0).toUpperCase()}
                    </span>
                  </div>

                  <div>
                    <div className="text-sm font-semibold text-[rgb(var(--text-primary))]">
                      {user?.username}
                    </div>
                    <div className="text-xs text-[rgb(var(--text-muted))]">
                      {user?.role_name === 'admin' ? 'Администратор' : 'Пользователь'}
                    </div>
                  </div>
                </div>

                <Button
                  variant="ghost"
                  onClick={logout}
                  className="
                    transition-all duration-300
                    hover:scale-105 active:scale-95

                    hover:bg-red-500/10
                    dark:hover:bg-red-400/10

                    hover:text-red-600
                    dark:hover:text-red-400
                  "
                >
                  <LogOut className="h-4 w-4" />
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
