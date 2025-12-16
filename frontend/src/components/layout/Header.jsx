import { useState } from 'react';
import { Search, User, LogOut } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Link } from 'react-router-dom';
import Logo from '@/components/ui_my/Logo';
import { useAuth } from '@/utils/AuthContext';

export default function Header() {
  const [searchQuery, setSearchQuery] = useState('');
  const { isAuthenticated, user, logout, isLoading } = useAuth();

  if (isLoading) return null;

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 backdrop-blur-xl shadow-2xl overflow-hidden">
      <div className="absolute inset-0 opacity-[0.02]">
        <div
          className="h-full w-full"
          style={{
            backgroundImage: `linear-gradient(to right, white 1px, transparent 1px),
                             linear-gradient(to bottom, white 1px, transparent 1px)`,
            backgroundSize: '40px 40px',
          }}
        ></div>
      </div>

      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-blue-500/30 to-transparent"></div>
      <div className="absolute top-10 right-10 w-40 h-40 bg-gradient-to-br from-blue-500/5 to-cyan-500/5 rounded-full blur-2xl"></div>
      <div className="absolute bottom-10 left-10 w-32 h-32 bg-gradient-to-br from-purple-500/5 to-pink-500/5 rounded-full blur-2xl"></div>

      <div className="container mx-auto px-6 relative z-10">
        <div className="flex h-20 items-center justify-between">
          <Logo size="default" showText={true} />

          <div className="hidden xl:flex flex-1 max-w-2xl mx-8">
            <div className="relative w-full">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-blue-400" />
              <Input
                type="search"
                placeholder="Поиск вакансий, должностей, компаний..."
                className="pl-12 pr-24 h-12 rounded-full border-2 border-gray-700 bg-gray-800/50 backdrop-blur-sm text-white placeholder:text-gray-500 shadow-lg shadow-blue-500/10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <Button className="absolute right-2 top-1/2 -translate-y-1/2 h-8 px-4 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-md hover:shadow-lg">
                Найти
              </Button>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {!isAuthenticated ? (
              <>
                <Button
                  variant="ghost"
                  className="h-11 px-4 rounded-xl border border-gray-700 bg-gray-800/40 hover:bg-gray-700/50 backdrop-blur-sm text-blue-300 hover:text-blue-200 font-medium shadow-sm transition-all group"
                  asChild
                >
                  <Link to="/login">
                    <div className="flex items-center gap-3">
                      <div className="h-8 w-8 rounded-full bg-gradient-to-br from-sky-500 to-blue-600 flex items-center justify-center group-hover:scale-110 transition-transform">
                        <User className="h-4 w-4 text-white" />
                      </div>
                      <div className="font-semibold">Войти</div>
                    </div>
                  </Link>
                </Button>

                <Button
                  className="h-11 px-5 rounded-xl border border-blue-500/30 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-medium shadow-lg hover:shadow-xl backdrop-blur-sm transition-all hover:scale-105"
                  asChild
                >
                  <Link to="/register">Регистрация</Link>
                </Button>
              </>
            ) : (
              <div className="flex items-center gap-3 relative">
                <div
                  className="flex items-center gap-3 px-4 py-2 rounded-xl border border-gray-700/50 
                           bg-gradient-to-r from-gray-800/40 to-gray-900/40 backdrop-blur-sm 
                           hover:from-gray-800/60 hover:to-gray-900/60 transition-all duration-300 
                           cursor-pointer group relative overflow-hidden"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 via-purple-500/5 to-pink-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>

                  <div className="relative z-10">
                    <div
                      className="h-10 w-10 rounded-full bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-500 
                                  flex items-center justify-center shadow-lg shadow-emerald-500/20
                                  group-hover:shadow-emerald-500/40 group-hover:scale-105 transition-all"
                    >
                      <span className="text-white font-bold text-sm">
                        {user?.username?.charAt(0).toUpperCase() || 'U'}
                      </span>
                    </div>
                  </div>

                  <div className="relative z-10">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-white text-sm">{user?.username}</span>
                    </div>
                    <div className="text-xs text-emerald-300/80 font-medium bg-emerald-500/10 px-2 py-0.5 rounded-full mt-1 inline-block">
                      {user?.role_name === 'admin' ? '👑 Администратор' : '👤 Пользователь'}
                    </div>
                  </div>
                </div>

                <Button
                  onClick={logout}
                  className="h-11 px-5 rounded-xl border border-rose-500/30 
                           bg-gradient-to-r from-rose-500/10 to-red-500/10 hover:from-rose-500/20 hover:to-red-500/20 
                           text-rose-300 hover:text-rose-200 font-medium shadow-lg hover:shadow-xl 
                           backdrop-blur-sm transition-all hover:scale-105 group"
                >
                  <div className="flex items-center gap-2">
                    <LogOut className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                    <span>Выйти</span>
                  </div>
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
