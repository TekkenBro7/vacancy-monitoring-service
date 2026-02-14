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
  Briefcase,
  Building,
  Zap,
  CheckCircle,
  Mail,
  Key,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import Logo from '@/components/ui_my/Logo';
import AuthService from '@/api/services/AuthService';
import useNotification from '@/hooks/useNotification';
import { useAuth } from '@/utils/AuthContext';

export default function LoginPage() {
  const navigate = useNavigate();
  const notification = useNotification();
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formError, setFormError] = useState('');
  const { checkAuth } = useAuth();

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

      notification.success('Вход выполнен успешно!', 'Добро пожаловать в систему');

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
      } else {
        errorMessage = 'Ошибка при отправке запроса';
      }

      setFormError(errorMessage);

      notification.error('Ошибка входа', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = () => {
    window.location.href = `${import.meta.env.VITE_API_BASE_URL}/auth/google/login`;
  };

  const features = [
    {
      icon: Briefcase,
      text: 'Доступ к тысячам вакансий',
      color: 'bg-gradient-to-r from-blue-400 to-cyan-400 dark:from-blue-500 dark:to-cyan-500',
    },
    {
      icon: Zap,
      text: 'Мгновенные уведомления',
      color: 'bg-gradient-to-r from-purple-400 to-pink-400 dark:from-purple-500 dark:to-pink-500',
    },
    {
      icon: Building,
      text: 'Прямые контакты с компаниями',
      color: 'bg-gradient-to-r from-emerald-400 to-teal-400 dark:from-emerald-500 dark:to-teal-500',
    },
    {
      icon: Sparkles,
      text: 'Персональные рекомендации',
      color: 'bg-gradient-to-r from-amber-400 to-orange-400 dark:from-amber-500 dark:to-orange-500',
    },
  ];

  const quickStats = [
    { value: '12K+', label: 'активных вакансий' },
    { value: '850+', label: 'компаний-партнеров' },
    { value: '50K+', label: 'пользователей' },
    { value: '99%', label: 'удовлетворенности' },
  ];

  return (
    <div className="min-h-screen transition-colors duration-300">
      <div
        className="absolute top-0 left-0 right-0 h-px"
        style={{
          background: 'linear-gradient(to right, transparent, rgb(var(--accent))/30, transparent)',
        }}
      />

      <div className="absolute top-10 right-10 w-64 h-64 bg-[rgb(var(--accent))]/10 rounded-full blur-3xl" />
      <div className="absolute bottom-10 left-10 w-56 h-56 bg-purple-500/10 rounded-full blur-3xl" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-[rgb(var(--accent))]/5 rounded-full blur-3xl" />

      <div className="container mx-auto px-6 py-12 relative z-10">
        <div className="max-w-6xl mx-auto">
          <div className="flex justify-between items-center mb-12">
            <Logo size="small" showText={true} />

            <div className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
              Нет аккаунта?{' '}
              <Link
                to="/register"
                style={{ color: 'rgb(var(--accent))' }}
                className="hover:opacity-80 font-medium transition-opacity"
              >
                Зарегистрироваться
              </Link>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
            <div>
              <div className="mb-8">
                <h1 className="text-4xl font-bold mb-4">
                  <span
                    className="bg-clip-text text-transparent"
                    style={{
                      backgroundImage:
                        'linear-gradient(to right, rgb(var(--accent)), rgb(var(--accent)/0.8))',
                    }}
                  >
                    Войдите в аккаунт
                  </span>
                  <br />
                  <span style={{ color: 'rgb(var(--text-primary))' }}>чтобы продолжить</span>
                </h1>
                <p style={{ color: 'rgb(var(--text-muted))' }}>
                  Войдите, чтобы получить доступ к персонализированным рекомендациям и вакансиям
                </p>
              </div>

              <Card
                className="backdrop-blur-sm"
                style={{
                  backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
                  borderColor: 'rgb(var(--border))',
                }}
              >
                <CardHeader>
                  <CardTitle className="flex items-center gap-3">
                    <Key className="h-6 w-6" style={{ color: 'rgb(var(--accent))' }} />
                    <span style={{ color: 'rgb(var(--text-primary))' }}>Авторизация</span>
                  </CardTitle>
                  <CardDescription style={{ color: 'rgb(var(--text-muted))' }}>
                    Введите данные для входа в систему
                  </CardDescription>
                </CardHeader>

                <form onSubmit={handleSubmit}>
                  <CardContent className="space-y-6">
                    {formError && (
                      <Alert
                        className="border"
                        style={{
                          backgroundColor: 'rgb(var(--error-bg))',
                          borderColor: 'rgb(var(--error-border))',
                        }}
                      >
                        <AlertDescription style={{ color: 'rgb(var(--error-text))' }}>
                          {formError}
                        </AlertDescription>
                      </Alert>
                    )}

                    <div className="space-y-2">
                      <label
                        className="text-sm font-medium"
                        style={{ color: 'rgb(var(--text-primary))' }}
                      >
                        Имя пользователя или Email
                      </label>
                      <div className="relative">
                        <User
                          className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4"
                          style={{ color: 'rgb(var(--accent))' }}
                        />
                        <Input
                          name="username"
                          value={formData.username}
                          onChange={handleChange}
                          placeholder="Введите имя пользователя или email"
                          className="pl-10 h-11 backdrop-blur-sm focus:outline-none"
                          style={{
                            backgroundColor: 'rgb(var(--bg-header-muted))',
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
                          className="text-sm font-medium"
                          style={{ color: 'rgb(var(--text-primary))' }}
                        >
                          Пароль
                        </label>
                        <Link
                          to="/forgot-password"
                          style={{ color: 'rgb(var(--accent))' }}
                          className="text-xs hover:opacity-80 transition-opacity"
                        >
                          Забыли пароль?
                        </Link>
                      </div>
                      <div className="relative">
                        <Lock
                          className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4"
                          style={{ color: 'rgb(var(--accent))' }}
                        />
                        <Input
                          name="password"
                          type={showPassword ? 'text' : 'password'}
                          value={formData.password}
                          onChange={handleChange}
                          placeholder="Введите пароль"
                          className="pl-10 pr-10 h-11 backdrop-blur-sm focus:outline-none"
                          style={{
                            backgroundColor: 'rgb(var(--bg-header-muted))',
                            borderColor: 'rgb(var(--border))',
                            color: 'rgb(var(--text-primary))',
                          }}
                          disabled={loading}
                          autoComplete="current-password"
                        />
                        <button
                          type="button"
                          onClick={() => setShowPassword(!showPassword)}
                          className="absolute right-3 top-1/2 -translate-y-1/2"
                          style={{ color: 'rgb(var(--text-muted))' }}
                          disabled={loading}
                        >
                          {showPassword ? (
                            <EyeOff className="h-4 w-4" />
                          ) : (
                            <Eye className="h-4 w-4" />
                          )}
                        </button>
                      </div>
                    </div>
                  </CardContent>

                  <CardFooter className="flex-col space-y-6">
                    <Button
                      type="submit"
                      disabled={loading}
                      className="
                        w-full h-12 rounded-xl text-white text-lg font-semibold
                        shadow-lg transition-all duration-300
                        hover:shadow-xl hover:scale-[1.02]
                        active:scale-[0.98]
                        disabled:opacity-50 disabled:cursor-not-allowed
                      "
                      style={{
                        background:
                          'linear-gradient(135deg, rgb(var(--button-from)), rgb(var(--button-to)))',
                      }}
                    >
                      {loading ? (
                        <span className="flex items-center gap-2">
                          <div
                            className="h-4 w-4 border-2 rounded-full animate-spin"
                            style={{
                              borderColor: 'transparent',
                              borderTopColor: 'white',
                            }}
                          />
                          Вход...
                        </span>
                      ) : (
                        <span className="flex items-center gap-2">
                          Войти в систему
                          <ArrowRight className="h-5 w-5" />
                        </span>
                      )}
                    </Button>

                    <div className="text-center">
                      <p className="text-sm mb-2" style={{ color: 'rgb(var(--text-muted))' }}>
                        Или войдите с помощью
                      </p>
                      <div className="flex gap-3 justify-center">
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          disabled={loading}
                          onClick={handleGoogleLogin}
                          className="
                            relative overflow-hidden
                            backdrop-blur-sm

                            transition-all duration-300
                            hover:scale-105 active:scale-95
                            hover:shadow-lg

                            before:absolute before:inset-0
                            before:opacity-0
                            before:transition-opacity

                            hover:before:opacity-100
                          "
                          style={{
                            borderColor: 'rgb(var(--border))',
                            color: 'rgb(var(--text-primary))',
                            backgroundColor: 'rgb(var(--bg-header-muted))',
                          }}
                        >
                          <span
                            className="absolute inset-0 pointer-events-none"
                            style={{
                              background:
                                'linear-gradient(135deg, rgb(var(--accent))/12, transparent)',
                              opacity: 0.8,
                            }}
                          />

                          <Mail
                            className="h-4 w-4 mr-2 transition-colors"
                            style={{ color: 'rgb(var(--accent))' }}
                          />
                          <span className="relative z-10">Google</span>
                        </Button>
                      </div>
                    </div>

                    <div
                      className="text-center text-sm"
                      style={{ color: 'rgb(var(--text-muted))' }}
                    >
                      Вход займет несколько секунд
                    </div>
                  </CardFooter>
                </form>
              </Card>

              <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4">
                {quickStats.map((stat) => (
                  <div
                    key={stat.label}
                    className="p-4 rounded-xl backdrop-blur-sm border transition-all hover:border-[rgb(var(--border))]"
                    style={{
                      backgroundColor: 'rgb(var(--bg-header-muted))',
                      borderColor: 'rgb(var(--border))',
                    }}
                  >
                    <div
                      className="text-xl font-bold bg-clip-text text-transparent"
                      style={{
                        backgroundImage:
                          'linear-gradient(to right, rgb(var(--accent)), rgb(var(--accent)/0.8))',
                      }}
                    >
                      {stat.value}
                    </div>
                    <div className="text-xs mt-1" style={{ color: 'rgb(var(--text-muted))' }}>
                      {stat.label}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="space-y-8">
              <Card
                className="backdrop-blur-sm"
                style={{
                  backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
                  borderColor: 'rgb(var(--border))',
                }}
              >
                <CardHeader>
                  <CardTitle className="flex items-center gap-3">
                    <Shield className="h-6 w-6" style={{ color: 'rgb(var(--accent))' }} />
                    <span style={{ color: 'rgb(var(--text-primary))' }}>Почему стоит войти?</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-4">
                    {features.map((feature, index) => (
                      <li key={index} className="flex items-start gap-3">
                        <div className={`p-2 rounded-lg ${feature.color} flex-shrink-0`}>
                          <feature.icon className="h-4 w-4 text-white" />
                        </div>
                        <div>
                          <div
                            className="font-medium"
                            style={{ color: 'rgb(var(--text-primary))' }}
                          >
                            {feature.text}
                          </div>
                          <div className="text-sm mt-1" style={{ color: 'rgb(var(--text-muted))' }}>
                            Получите полный доступ ко всем функциям платформы
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              <Card
                className="backdrop-blur-sm border"
                style={{
                  backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
                  borderColor: 'rgb(var(--border))',
                }}
              >
                <CardHeader>
                  <CardTitle style={{ color: 'rgb(var(--text-primary))' }}>
                    Безопасность и конфиденциальность
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-start gap-3">
                      <div
                        className="p-2 rounded-lg"
                        style={{
                          backgroundColor: 'rgb(var(--accent))/20',
                        }}
                      >
                        <Shield className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
                      </div>
                      <div>
                        <div
                          className="font-semibold"
                          style={{ color: 'rgb(var(--text-primary))' }}
                        >
                          Защита данных
                        </div>
                        <div className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                          Все данные передаются по защищенному соединению
                        </div>
                      </div>
                    </div>

                    <div className="flex items-start gap-3">
                      <div
                        className="p-2 rounded-lg"
                        style={{
                          backgroundColor: 'rgb(var(--accent))/20',
                        }}
                      >
                        <CheckCircle className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
                      </div>
                      <div>
                        <div
                          className="font-semibold"
                          style={{ color: 'rgb(var(--text-primary))' }}
                        >
                          Подтвержденные компании
                        </div>
                        <div className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                          Только проверенные работодатели и вакансии
                        </div>
                      </div>
                    </div>

                    <div className="flex items-start gap-3">
                      <div
                        className="p-2 rounded-lg"
                        style={{
                          backgroundColor: 'rgb(var(--accent))/20',
                        }}
                      >
                        <Sparkles className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
                      </div>
                      <div>
                        <div
                          className="font-semibold"
                          style={{ color: 'rgb(var(--text-primary))' }}
                        >
                          Интеллектуальная система
                        </div>
                        <div className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                          Умный подбор вакансий по вашим навыкам и опыту
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
                <CardFooter>
                  <p className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                    Мы никогда не передаем ваши данные третьим лицам
                  </p>
                </CardFooter>
              </Card>

              <div
                className="p-6 rounded-xl backdrop-blur-sm border"
                style={{
                  backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
                  borderColor: 'rgb(var(--border))',
                }}
              >
                <div className="text-center">
                  <div
                    className="inline-flex items-center gap-2 mb-3 px-4 py-2 rounded-full backdrop-blur-sm border"
                    style={{
                      backgroundColor: 'rgb(var(--bg-header-muted))',
                      borderColor: 'rgb(var(--border))',
                    }}
                  >
                    <Sparkles className="h-4 w-4" style={{ color: 'rgb(var(--accent))' }} />
                    <span className="text-sm" style={{ color: 'rgb(var(--accent))' }}>
                      Нужна помощь?
                    </span>
                  </div>
                  <p className="mb-4" style={{ color: 'rgb(var(--text-primary))' }}>
                    Наша команда поддержки готова помочь 24/7
                  </p>
                  <Button
                    variant="outline"
                    asChild
                    className="
                      w-full
                      transition-all duration-300
                      hover:scale-[1.01] hover:shadow-md  
                    "
                    style={{
                      borderColor: 'rgb(var(--border))',
                      color: 'rgb(var(--text-primary))',
                      backgroundColor: 'rgb(var(--bg-header-muted))',
                      backdropFilter: 'none',
                    }}
                  >
                    <Link to="/support">
                      <Mail className="h-4 w-4 mr-2" />
                      Связаться с поддержкой
                    </Link>
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
