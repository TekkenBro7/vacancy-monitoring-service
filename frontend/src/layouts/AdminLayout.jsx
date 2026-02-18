import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import {
  LayoutDashboard,
  Users,
  Briefcase,
  Building2,
  Tags,
  Settings,
  Menu,
  X,
  LogOut,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/utils/AuthContext';
import Logo from '@/components/ui_my/Logo';
import ThemeToggle from '@/components/ui_my/ThemeToggle';

const navigation = [
  { name: 'Dashboard', href: '/admin', icon: LayoutDashboard },
  { name: 'Пользователи', href: '/admin/users', icon: Users },
];

export default function AdminLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[rgb(var(--bg))]">
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside
        className={`
          fixed top-0 left-0 z-50 h-full w-64 
          bg-[rgb(var(--bg-header))] border-r border-[rgb(var(--border))]
          transform transition-transform duration-300 ease-in-out
          lg:translate-x-0
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        <div className="flex flex-col h-full">
          <div className="flex items-center justify-between h-15 px-6 border-b border-[rgb(var(--border))]">
            <Logo size="small" showText={true} />
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden"
              style={{ color: 'rgb(var(--text-muted))' }}
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={`
                    flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200
                    ${
                      isActive
                        ? 'bg-[rgb(var(--accent))/10] text-[rgb(var(--accent))]'
                        : 'text-[rgb(var(--text-muted))] hover:bg-[rgb(var(--bg-header-muted))] hover:text-[rgb(var(--text-primary))]'
                    }
                  `}
                >
                  <item.icon className="h-5 w-5" />
                  <span className="font-medium">{item.name}</span>
                </Link>
              );
            })}
          </nav>

          <div className="p-4 border-t border-[rgb(var(--border))]">
            <div
              className="flex items-center gap-3 px-4 py-3 rounded-xl mb-3"
              style={{ backgroundColor: 'rgb(var(--bg-header-muted))' }}
            >
              <div className="h-9 w-9 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                <span className="text-white font-bold text-sm">
                  {user?.username?.charAt(0).toUpperCase()}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-semibold text-[rgb(var(--text-primary))] truncate">
                  {user?.username}
                </div>
                <div className="text-xs text-[rgb(var(--text-muted))]">Администратор</div>
              </div>
            </div>

            <Button
              variant="ghost"
              onClick={() => {
                logout();
                navigate('/');
              }}
              className="w-full justify-start text-[rgb(var(--text-muted))] hover:text-red-500 hover:bg-red-500/10"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Выйти из аккаунта
            </Button>
          </div>
        </div>
      </aside>

      <div className="lg:pl-64">
        <header
          className="
            sticky top-0 z-30 h-15 
            bg-[rgb(var(--bg-header))]/80 backdrop-blur-xl 
            border-b border-[rgb(var(--border))]
          "
        >
          <div className="flex items-center justify-between h-full px-6">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden"
              style={{ color: 'rgb(var(--text-primary))' }}
            >
              <Menu className="h-6 w-6" />
            </button>

            <div className="flex items-center gap-4 ml-auto">
              <ThemeToggle />
              <Link
                to="/"
                className="text-sm text-[rgb(var(--text-muted))] hover:text-[rgb(var(--accent))]"
              >
                ← На главную
              </Link>
            </div>
          </div>
        </header>

        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
