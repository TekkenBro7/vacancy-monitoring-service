import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  User,
  Lock,
  Eye,
  EyeOff,
  ArrowRight,
  Shield,
  Sparkles,
  Zap,
  Building,
  TrendingUp,
  CheckCircle,
  Loader2,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import Logo from '@/components/ui_my/Logo';
import AuthService from '@/api/services/AuthService';
import useNotification from '@/hooks/useNotification';
import { useAuth } from '@/utils/AuthContext';

export default function LoginPage() {
  const navigate = useNavigate();
  const notification = useNotification();
  const { checkAuth } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formError, setFormError] = useState('');

  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    setFormError('');
  };

  const validateForm = () => {
    if (!formData.username.trim()) {
      setFormError('Введите имя пользователя или email');
      return false;
    }
    if (!formData.password) {
      setFormError('Введите пароль');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setLoading(true);
    setFormError('');

    try {
      await AuthService.login({
        username: formData.username,
        password: formData.password,
      });
      await checkAuth();
      notification.success('Вход выполнен успешно', 'Добро пожаловать в систему');
      navigate('/');
    } catch (err) {
      let errorMessage = 'Ошибка входа. Проверьте данные.';
      if (err.response) {
        if (err.response.status === 401) {
          errorMessage = 'Неверное имя пользователя или пароль';
        } else if (err.response.status === 400) {
          errorMessage = err.response.data?.detail || 'Некорректные данные';
        } else if (err.response.status === 404) {
          errorMessage = 'Сервер не найден. Проверьте подключение.';
        } else if (err.response.status >= 500) {
          errorMessage = 'Ошибка сервера. Попробуйте позже.';
        }
      } else if (err.request) {
        errorMessage = 'Нет ответа от сервера. Проверьте подключение.';
      }
      setFormError(errorMessage);
      notification.error('Ошибка входа', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = () => {
    window.location.href = `${import.meta.env.VITE_API_BASE_URL}/auth/google/login/`;
  };

  const features = [
    { icon: Zap, text: 'Поиск по 10K+ вакансий', color: 'from-amber-500 to-orange-500' },
    {
      icon: Sparkles,
      text: 'AI-рекомендации',
      color: 'from-violet-500 to-purple-500',
    },
    { icon: TrendingUp, text: 'Аналитика рынка труда', color: 'from-emerald-500 to-teal-500' },
    { icon: Building, text: '500+ компаний-партнеров', color: 'from-blue-500 to-cyan-500' },
  ];

  return (
    <div className="min-h-[calc(100vh-5rem)] py-8 animate-fade-in">
      <div className="container mx-auto px-6">
        <div className="max-w-5xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-8 lg:gap-12 items-start">
            <div className="order-2 lg:order-1 animate-fade-in-up">
              <div
                className="rounded-2xl backdrop-blur-sm border shadow-xl overflow-hidden"
                style={{
                  backgroundColor: 'rgb(var(--bg-header-muted)/0.4)',
                  borderColor: 'rgb(var(--border)/0.5)',
                }}
              >
                <div
                  className="h-1"
                  style={{
                    background:
                      'linear-gradient(90deg, rgb(var(--accent)), rgb(168, 85, 247), rgb(var(--accent)))',
                  }}
                />

                <div
                  className="relative p-8 border-b overflow-hidden"
                  style={{
                    borderColor: 'rgb(var(--border))',
                    background: 'linear-gradient(135deg, rgb(var(--accent))/5, transparent)',
                  }}
                >
                  <div
                    className="absolute top-0 right-0 w-48 h-48 rounded-full blur-3xl opacity-20 pointer-events-none"
                    style={{
                      background: 'radial-gradient(circle, rgb(var(--accent)) 0%, transparent 70%)',
                    }}
                  />

                  <div className="relative text-center">
                    <div className="inline-block mb-4">
                      <Logo size="default" showText={true} />
                    </div>
                    <h1
                      className="text-2xl md:text-3xl font-bold mb-2"
                      style={{ color: 'rgb(var(--text-primary))' }}
                    >
                      Добро пожаловать
                    </h1>
                    <p style={{ color: 'rgb(var(--text-muted))' }}>
                      Войдите, чтобы продолжить работу
                    </p>
                  </div>
                </div>

                <form onSubmit={handleSubmit} className="p-8 space-y-6">
                  {formError && (
                    <Alert
                      className="border animate-fade-in"
                      style={{
                        background:
                          'linear-gradient(135deg, rgb(239, 68, 68)/10, rgb(239, 68, 68)/5)',
                        borderColor: 'rgb(239, 68, 68)/0.3',
                      }}
                    >
                      <AlertDescription style={{ color: 'rgb(239, 68, 68)' }}>
                        {formError}
                      </AlertDescription>
                    </Alert>
                  )}

                  <div className="space-y-2">
                    <label
                      className="text-sm font-medium flex items-center gap-2"
                      style={{ color: 'rgb(var(--text-primary))' }}
                    >
                      <User className="h-4 w-4" style={{ color: 'rgb(var(--accent))' }} />
                      Имя пользователя
                    </label>
                    <div className="relative group">
                      <Input
                        name="username"
                        value={formData.username}
                        onChange={handleChange}
                        placeholder="Введите имя пользователя"
                        className="h-12 rounded-xl text-base transition-all duration-300 border-2 focus:border-[rgb(var(--accent))] focus:ring-0 focus:shadow-lg focus:shadow-[rgb(var(--accent))]/10"
                        style={{
                          backgroundColor: 'rgb(var(--bg-header-muted)/0.5)',
                          borderColor: 'rgb(var(--border))',
                          color: 'rgb(var(--text-primary))',
                        }}
                        disabled={loading}
                        autoComplete="username"
                        autoFocus
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <label
                        className="text-sm font-medium flex items-center gap-2"
                        style={{ color: 'rgb(var(--text-primary))' }}
                      >
                        <Lock className="h-4 w-4" style={{ color: 'rgb(var(--accent))' }} />
                        Пароль
                      </label>
                      <Link
                        to="/forgot-password"
                        className="text-sm font-medium transition-all hover:opacity-80"
                        style={{ color: 'rgb(var(--accent))' }}
                      >
                        Забыли пароль?
                      </Link>
                    </div>
                    <div className="relative group">
                      <Input
                        name="password"
                        type={showPassword ? 'text' : 'password'}
                        value={formData.password}
                        onChange={handleChange}
                        placeholder="Введите пароль"
                        className="h-12 pr-12 rounded-xl text-base transition-all duration-300 border-2 focus:border-[rgb(var(--accent))] focus:ring-0 focus:shadow-lg focus:shadow-[rgb(var(--accent))]/10"
                        style={{
                          backgroundColor: 'rgb(var(--bg-header-muted)/0.5)',
                          borderColor: 'rgb(var(--border))',
                          color: 'rgb(var(--text-primary))',
                        }}
                        disabled={loading}
                        autoComplete="current-password"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-4 top-1/2 -translate-y-1/2 p-1 rounded-lg transition-all hover:bg-[rgb(var(--accent))]/10"
                        style={{ color: 'rgb(var(--text-muted))' }}
                        disabled={loading}
                      >
                        {showPassword ? (
                          <EyeOff className="h-5 w-5" />
                        ) : (
                          <Eye className="h-5 w-5" />
                        )}
                      </button>
                    </div>
                  </div>

                  <Button
                    type="submit"
                    disabled={loading}
                    className="w-full h-12 rounded-xl text-white text-base font-semibold transition-all duration-300 hover:scale-[1.02] hover:shadow-xl hover:shadow-[rgb(var(--accent))]/20 active:scale-[0.98] disabled:opacity-50"
                    style={{
                      background:
                        'linear-gradient(135deg, rgb(var(--button-from)), rgb(var(--button-to)))',
                    }}
                  >
                    {loading ? (
                      <span className="flex items-center gap-2">
                        <Loader2 className="h-5 w-5 animate-spin" />
                        Входим...
                      </span>
                    ) : (
                      <span className="flex items-center gap-2">
                        Войти в систему
                        <ArrowRight className="h-5 w-5" />
                      </span>
                    )}
                  </Button>

                  <div className="relative">
                    <div className="absolute inset-0 flex items-center" style={{ top: '50%' }}>
                      <div
                        className="w-full border-t"
                        style={{ borderColor: 'rgb(var(--border))' }}
                      />
                    </div>
                    <div className="relative flex justify-center">
                      <span
                        className="px-4 text-sm"
                        style={{
                          backgroundColor: 'rgb(var(--bg-header-muted)/0.4)',
                          color: 'rgb(var(--text-muted))',
                        }}
                      >
                        или
                      </span>
                    </div>
                  </div>

                  <Button
                    type="button"
                    variant="outline"
                    disabled={loading}
                    onClick={handleGoogleLogin}
                    className="w-full h-12 rounded-xl font-medium text-base transition-all duration-300 hover:scale-[1.02] hover:shadow-lg border-2"
                    style={{
                      borderColor: 'rgb(var(--border))',
                      color: 'rgb(var(--text-primary))',
                      backgroundColor: 'rgb(var(--bg-header-muted)/0.5)',
                    }}
                  >
                    <svg className="h-5 w-5 mr-3" viewBox="0 0 24 24">
                      <path
                        fill="#4285F4"
                        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                      />
                      <path
                        fill="#34A853"
                        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                      />
                      <path
                        fill="#FBBC05"
                        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                      />
                      <path
                        fill="#EA4335"
                        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                      />
                    </svg>
                    Войти через Google
                  </Button>

                  <div className="text-center pt-2">
                    <p style={{ color: 'rgb(var(--text-muted))' }}>
                      Еще нет аккаунта?{' '}
                      <Link
                        to="/register"
                        className="font-semibold transition-all hover:opacity-80"
                        style={{ color: 'rgb(var(--accent))' }}
                      >
                        Зарегистрироваться
                      </Link>
                    </p>
                  </div>
                </form>

                <div
                  className="px-8 py-4 border-t flex items-center justify-center gap-2"
                  style={{
                    borderColor: 'rgb(var(--border))',
                    backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
                  }}
                >
                  <Shield className="h-4 w-4" style={{ color: 'rgb(34, 197, 94)' }} />
                  <span className="text-sm" style={{ color: 'rgb(var(--text-muted))' }} />
                </div>
              </div>
            </div>

            <div className="order-1 lg:order-2 space-y-6 animate-fade-in-down">
              <div>
                <Badge
                  className="mb-4 border"
                  style={{
                    background:
                      'linear-gradient(135deg, rgb(var(--accent))/15, rgb(var(--accent))/5)',
                    borderColor: 'rgb(var(--accent))/0.3',
                    color: 'rgb(var(--accent))',
                  }}
                >
                  <Sparkles className="h-3 w-3 mr-1" />
                  Платформа №1 для IT-специалистов
                </Badge>
                <h2
                  className="text-3xl lg:text-4xl font-bold mb-4"
                  style={{ color: 'rgb(var(--text-primary))' }}
                >
                  Найдите работу{' '}
                  <span
                    className="bg-clip-text text-transparent"
                    style={{
                      backgroundImage:
                        'linear-gradient(135deg, rgb(var(--accent)), rgb(168, 85, 247))',
                    }}
                  >
                    мечты
                  </span>
                </h2>
                <p className="text-lg" style={{ color: 'rgb(var(--text-muted))' }}>
                  Получите доступ к сохраненным вакансиям и аналитике рынка
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {features.map((feature, index) => (
                  <div
                    key={index}
                    className="group p-4 rounded-xl transition-all duration-300 hover:scale-[1.02] hover:shadow-lg animate-fade-in"
                    style={{
                      animationDelay: `${index * 100}ms`,
                      backgroundColor: 'rgb(var(--bg-header-muted)/0.4)',
                      border: '1px solid rgb(var(--border)/0.5)',
                    }}
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`p-2.5 rounded-xl bg-gradient-to-br ${feature.color} shadow-lg transition-transform group-hover:scale-110`}
                      >
                        <feature.icon className="h-5 w-5 text-white" />
                      </div>
                      <span
                        className="font-medium text-sm"
                        style={{ color: 'rgb(var(--text-primary))' }}
                      >
                        {feature.text}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              <div
                className="p-6 rounded-2xl border"
                style={{
                  backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
                  borderColor: 'rgb(var(--border)/0.5)',
                }}
              >
                <div className="grid grid-cols-3 gap-4 text-center">
                  {[
                    { value: '10K+', label: 'Вакансий' },
                    { value: '500+', label: 'Компаний' },
                    { value: '50K+', label: 'Пользователей' },
                  ].map((stat, i) => (
                    <div key={i}>
                      <div
                        className="text-2xl font-bold bg-clip-text text-transparent"
                        style={{
                          backgroundImage:
                            'linear-gradient(135deg, rgb(var(--accent)), rgb(168, 85, 247))',
                        }}
                      >
                        {stat.value}
                      </div>
                      <div className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                        {stat.label}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div
                className="p-5 rounded-xl border"
                style={{
                  background: 'linear-gradient(135deg, rgb(var(--accent))/5, transparent)',
                  borderColor: 'rgb(var(--accent))/0.2',
                }}
              >
                <div className="flex items-center gap-3 mb-3">
                  <div
                    className="p-2 rounded-lg"
                    style={{ backgroundColor: 'rgb(var(--accent))/0.1' }}
                  >
                    <CheckCircle className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
                  </div>
                  <span className="font-semibold" style={{ color: 'rgb(var(--text-primary))' }}>
                    Почему JobHub?
                  </span>
                </div>
                <ul className="space-y-2">
                  {[
                    'Агрегация из 6+ источников',
                    'Умный AI-подбор вакансий',
                    'Сравнение предложений',
                    'Бесплатный доступ',
                  ].map((item, i) => (
                    <li
                      key={i}
                      className="flex items-center gap-2 text-sm"
                      style={{ color: 'rgb(var(--text-muted))' }}
                    >
                      <div
                        className="w-1.5 h-1.5 rounded-full"
                        style={{ backgroundColor: 'rgb(var(--accent))' }}
                      />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
