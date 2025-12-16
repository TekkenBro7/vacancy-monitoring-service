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

  const features = [
    { icon: Briefcase, text: 'Доступ к тысячам вакансий', color: 'from-blue-500 to-cyan-500' },
    { icon: Zap, text: 'Мгновенные уведомления', color: 'from-purple-500 to-pink-500' },
    { icon: Building, text: 'Прямые контакты с компаниями', color: 'from-emerald-500 to-teal-500' },
    { icon: Sparkles, text: 'Персональные рекомендации', color: 'from-amber-500 to-orange-500' },
  ];

  const quickStats = [
    { value: '12K+', label: 'активных вакансий' },
    { value: '850+', label: 'компаний-партнеров' },
    { value: '50K+', label: 'пользователей' },
    { value: '99%', label: 'удовлетворенности' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900 text-white overflow-hidden">
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-blue-500/30 to-transparent"></div>
      <div className="absolute top-10 right-10 w-64 h-64 bg-gradient-to-br from-blue-500/10 to-cyan-500/10 rounded-full blur-3xl"></div>
      <div className="absolute bottom-10 left-10 w-56 h-56 bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-full blur-3xl"></div>
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-br from-blue-500/5 to-purple-500/5 rounded-full blur-3xl"></div>

      <div className="absolute inset-0 opacity-5">
        <div
          className="h-full w-full"
          style={{
            backgroundImage: `linear-gradient(to right, white 1px, transparent 1px),
                           linear-gradient(to bottom, white 1px, transparent 1px)`,
            backgroundSize: '40px 40px',
          }}
        ></div>
      </div>

      <div className="container mx-auto px-6 py-12 relative z-10">
        <div className="max-w-6xl mx-auto">
          <div className="flex justify-between items-center mb-12">
            <Logo size="small" showText={true} />

            <div className="text-sm text-gray-400">
              Нет аккаунта?{' '}
              <Link to="/register" className="text-blue-400 hover:text-blue-300 font-medium">
                Зарегистрироваться
              </Link>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
            <div>
              <div className="mb-8">
                <h1 className="text-4xl font-bold mb-4">
                  <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                    Войдите в аккаунт
                  </span>
                  <br />
                  <span className="text-white">чтобы продолжить</span>
                </h1>
                <p className="text-gray-400">
                  Войдите, чтобы получить доступ к персонализированным рекомендациям и вакансиям
                </p>
              </div>

              <Card className="bg-gray-800/30 backdrop-blur-sm border-gray-700/50 shadow-2xl">
                <CardHeader>
                  <CardTitle className="flex items-center gap-3">
                    <Key className="h-6 w-6 text-blue-400" />
                    Авторизация
                  </CardTitle>
                  <CardDescription className="text-gray-400">
                    Введите данные для входа в систему
                  </CardDescription>
                </CardHeader>

                <form onSubmit={handleSubmit}>
                  <CardContent className="space-y-6">
                    {formError && (
                      <Alert variant="destructive" className="bg-red-500/20 border-red-500/30">
                        <AlertDescription className="text-red-300">{formError}</AlertDescription>
                      </Alert>
                    )}

                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-300">
                        Имя пользователя или Email
                      </label>
                      <div className="relative">
                        <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-blue-400" />
                        <Input
                          name="username"
                          value={formData.username}
                          onChange={handleChange}
                          placeholder="Введите имя пользователя или email"
                          className="pl-10 h-11 bg-gray-800/50 border-gray-700 text-white placeholder:text-gray-500"
                          disabled={loading}
                          autoComplete="username"
                          autoFocus
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <label className="text-sm font-medium text-gray-300">Пароль</label>
                        <Link
                          to="/forgot-password"
                          className="text-xs text-blue-400 hover:text-blue-300"
                        >
                          Забыли пароль?
                        </Link>
                      </div>
                      <div className="relative">
                        <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-blue-400" />
                        <Input
                          name="password"
                          type={showPassword ? 'text' : 'password'}
                          value={formData.password}
                          onChange={handleChange}
                          placeholder="Введите пароль"
                          className="pl-10 pr-10 h-11 bg-gray-800/50 border-gray-700 text-white placeholder:text-gray-500"
                          disabled={loading}
                          autoComplete="current-password"
                        />
                        <button
                          type="button"
                          onClick={() => setShowPassword(!showPassword)}
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
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
                      className="w-full h-12 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 
                               hover:from-blue-700 hover:to-purple-700 text-white text-lg font-semibold
                               shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                      disabled={loading}
                    >
                      {loading ? (
                        <span className="flex items-center gap-2">
                          <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
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
                      <p className="text-sm text-gray-500 mb-2">Или войдите с помощью</p>
                      <div className="flex gap-3 justify-center">
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          className="border-gray-700 text-gray-300 hover:text-white"
                          disabled={loading}
                        >
                          <Mail className="h-4 w-4 mr-2" />
                          Google
                        </Button>
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          className="border-gray-700 text-gray-300 hover:text-white"
                          disabled={loading}
                        >
                          <Building className="h-4 w-4 mr-2" />
                          LinkedIn
                        </Button>
                      </div>
                    </div>

                    <div className="text-center text-sm text-gray-500">
                      Вход займет несколько секунд
                    </div>
                  </CardFooter>
                </form>
              </Card>

              <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4">
                {quickStats.map((stat) => (
                  <div
                    key={stat.label}
                    className="p-4 rounded-xl bg-gray-800/30 backdrop-blur-sm border border-gray-700/50 
                             hover:bg-gray-800/50 hover:border-gray-600 transition-all"
                  >
                    <div className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                      {stat.value}
                    </div>
                    <div className="text-xs text-gray-400 mt-1">{stat.label}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="space-y-8">
              <Card className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-sm border-gray-700/50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-3">
                    <Shield className="h-6 w-6 text-emerald-400" />
                    Почему стоит войти?
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-4">
                    {features.map((feature, index) => (
                      <li key={index} className="flex items-start gap-3">
                        <div
                          className={`p-2 rounded-lg bg-gradient-to-br ${feature.color} flex-shrink-0`}
                        >
                          <feature.icon className="h-4 w-4 text-white" />
                        </div>
                        <div>
                          <div className="font-medium text-gray-200">{feature.text}</div>
                          <div className="text-sm text-gray-400 mt-1">
                            Получите полный доступ ко всем функциям платформы
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-blue-900/20 to-purple-900/20 backdrop-blur-sm border-blue-500/30">
                <CardHeader>
                  <CardTitle>Безопасность и конфиденциальность</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-start gap-3">
                      <div className="p-2 rounded-lg bg-emerald-500/20">
                        <Shield className="h-5 w-5 text-emerald-400" />
                      </div>
                      <div>
                        <div className="font-semibold text-gray-200">Защита данных</div>
                        <div className="text-sm text-gray-400">
                          Все данные передаются по защищенному соединению
                        </div>
                      </div>
                    </div>

                    <div className="flex items-start gap-3">
                      <div className="p-2 rounded-lg bg-blue-500/20">
                        <CheckCircle className="h-5 w-5 text-blue-400" />
                      </div>
                      <div>
                        <div className="font-semibold text-gray-200">Подтвержденные компании</div>
                        <div className="text-sm text-gray-400">
                          Только проверенные работодатели и вакансии
                        </div>
                      </div>
                    </div>

                    <div className="flex items-start gap-3">
                      <div className="p-2 rounded-lg bg-purple-500/20">
                        <Sparkles className="h-5 w-5 text-purple-400" />
                      </div>
                      <div>
                        <div className="font-semibold text-gray-200">Интеллектуальная система</div>
                        <div className="text-sm text-gray-400">
                          Умный подбор вакансий по вашим навыкам и опыту
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
                <CardFooter>
                  <p className="text-xs text-gray-500">
                    Мы никогда не передаем ваши данные третьим лицам
                  </p>
                </CardFooter>
              </Card>

              <div className="p-6 rounded-xl bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-sm border border-gray-700/50">
                <div className="text-center">
                  <div className="inline-flex items-center gap-2 mb-3 px-4 py-2 rounded-full bg-gray-800/50 backdrop-blur-sm border border-gray-700">
                    <Sparkles className="h-4 w-4 text-amber-400" />
                    <span className="text-sm text-amber-300">Нужна помощь?</span>
                  </div>
                  <p className="text-gray-300 mb-4">Наша команда поддержки готова помочь 24/7</p>
                  <Button
                    variant="outline"
                    className="border-gray-700 text-gray-300 hover:text-white w-full"
                    asChild
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
