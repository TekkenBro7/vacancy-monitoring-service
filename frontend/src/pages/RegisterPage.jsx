import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  User,
  Mail,
  Lock,
  Eye,
  EyeOff,
  Briefcase,
  Sparkles,
  ArrowRight,
  CheckCircle,
  Shield,
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
import { UserService } from '@/api/services/UserService';
import useNotification from '@/hooks/useNotification';

export default function RegisterPage() {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formError, setFormError] = useState('');
  const notification = useNotification();

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
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
      setFormError('Введите имя пользователя');
      return false;
    }
    if (!formData.email.trim()) {
      setFormError('Введите email');
      return false;
    }
    if (!/\S+@\S+\.\S+/.test(formData.email)) {
      setFormError('Введите корректный email');
      return false;
    }
    if (!formData.password) {
      setFormError('Введите пароль');
      return false;
    }
    if (formData.password.length < 6) {
      setFormError('Пароль должен быть не менее 6 символов');
      return false;
    }
    if (formData.password !== formData.confirmPassword) {
      setFormError('Пароли не совпадают');
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
      await UserService.create({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        role_id: 5,
      });

      notification.success('Регистрация успешна', 'Сейчас вы будете перенаправлены');

      navigate('/login');
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Ошибка регистрации. Проверьте данные.';

      setFormError(errorMessage);

      notification.error('Ошибка регистрации', err.response?.data?.detail || 'Проверьте данные');
    } finally {
      setLoading(false);
    }
  };

  const passwordStrength = (password) => {
    if (!password) return { strength: 0, color: 'bg-gray-700' };

    let score = 0;
    if (password.length >= 6) score += 1;
    if (/[A-Z]/.test(password)) score += 1;
    if (/[0-9]/.test(password)) score += 1;
    if (/[^A-Za-z0-9]/.test(password)) score += 1;

    if (score === 0) return { strength: 0, color: 'bg-red-500' };
    if (score === 1) return { strength: 25, color: 'bg-red-500' };
    if (score === 2) return { strength: 50, color: 'bg-amber-500' };
    if (score === 3) return { strength: 75, color: 'bg-blue-500' };
    return { strength: 100, color: 'bg-emerald-500' };
  };

  const strength = passwordStrength(formData.password);

  const features = [
    'Доступ ко всем вакансиям',
    'Персональные рекомендации',
    'Сравнение предложений',
    'Уведомления о новых вакансиях',
    'Аналитика рынка',
    'Бесплатно навсегда',
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

      <div className="container mx-auto px-6 py-12 relative z-10">
        <div className="max-w-6xl mx-auto">
          <div className="flex justify-between items-center mb-12">
            <Logo size="small" showText={true} />

            <div style={{ color: 'rgb(var(--text-muted))' }}>
              Уже есть аккаунт?{' '}
              <Link
                to="/login"
                style={{ color: 'rgb(var(--accent))' }}
                className="hover:opacity-80 font-medium transition-opacity"
              >
                Войти
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
                    Создайте аккаунт
                  </span>
                  <br />
                  <span style={{ color: 'rgb(var(--text-primary))' }}>
                    и начните карьерный рост
                  </span>
                </h1>
                <p style={{ color: 'rgb(var(--text-muted))' }}>
                  Присоединяйтесь к сообществу профессионалов
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
                  <CardTitle style={{ color: 'rgb(var(--text-primary))' }}>Регистрация</CardTitle>
                  <CardDescription style={{ color: 'rgb(var(--text-muted))' }}>
                    Заполните форму для создания аккаунта
                  </CardDescription>
                </CardHeader>

                <form onSubmit={handleSubmit}>
                  <CardContent className="space-y-6">
                    {formError && (
                      <Alert
                        className="border"
                        style={{
                          backgroundColor: 'rgb(239 68 68 / 0.2)',
                          borderColor: 'rgb(239 68 68 / 0.3)',
                        }}
                      >
                        <AlertDescription style={{ color: 'rgb(254 202 202)' }}>
                          {formError}
                        </AlertDescription>
                      </Alert>
                    )}

                    <div className="space-y-2">
                      <label
                        className="text-sm font-medium"
                        style={{ color: 'rgb(var(--text-primary))' }}
                      >
                        Имя пользователя
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
                          placeholder="Введите имя пользователя"
                          className="pl-10 h-11 backdrop-blur-sm focus:outline-none"
                          style={{
                            backgroundColor: 'rgb(var(--bg-header-muted))',
                            borderColor: 'rgb(var(--border))',
                            color: 'rgb(var(--text-primary))',
                          }}
                          disabled={loading}
                          autoComplete="username"
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <label
                        className="text-sm font-medium"
                        style={{ color: 'rgb(var(--text-primary))' }}
                      >
                        Email
                      </label>
                      <div className="relative">
                        <Mail
                          className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4"
                          style={{ color: 'rgb(var(--accent))' }}
                        />
                        <Input
                          name="email"
                          type="email"
                          value={formData.email}
                          onChange={handleChange}
                          placeholder="Введите email"
                          className="pl-10 h-11 backdrop-blur-sm focus:outline-none"
                          style={{
                            backgroundColor: 'rgb(var(--bg-header-muted))',
                            borderColor: 'rgb(var(--border))',
                            color: 'rgb(var(--text-primary))',
                          }}
                          disabled={loading}
                          autoComplete="email"
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <label
                        className="text-sm font-medium"
                        style={{ color: 'rgb(var(--text-primary))' }}
                      >
                        Пароль
                      </label>
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
                          autoComplete="new-password"
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

                      {formData.password && (
                        <div className="space-y-1">
                          <div
                            className="flex justify-between text-xs"
                            style={{ color: 'rgb(var(--text-muted))' }}
                          >
                            <span>Сложность пароля</span>
                            <span>{strength.strength}%</span>
                          </div>
                          <div
                            className="h-2 w-full rounded-full overflow-hidden"
                            style={{ backgroundColor: 'rgb(var(--border)/0.5)' }}
                          >
                            <div
                              className={`h-full ${strength.color} transition-all duration-300`}
                              style={{ width: `${strength.strength}%` }}
                            />
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="space-y-2">
                      <label
                        className="text-sm font-medium"
                        style={{ color: 'rgb(var(--text-primary))' }}
                      >
                        Подтвердите пароль
                      </label>
                      <div className="relative">
                        <Lock
                          className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4"
                          style={{ color: 'rgb(var(--accent))' }}
                        />
                        <Input
                          name="confirmPassword"
                          type="password"
                          value={formData.confirmPassword}
                          onChange={handleChange}
                          placeholder="Повторите пароль"
                          className="pl-10 h-11 backdrop-blur-sm focus:outline-none"
                          style={{
                            backgroundColor: 'rgb(var(--bg-header-muted))',
                            borderColor: 'rgb(var(--border))',
                            color: 'rgb(var(--text-primary))',
                          }}
                          disabled={loading}
                          autoComplete="new-password"
                        />
                      </div>
                    </div>

                    <div className="flex items-start space-x-3">
                      <input
                        type="checkbox"
                        id="terms"
                        required
                        className="mt-1 h-4 w-4 rounded focus:ring-2 focus:outline-none"
                        style={{
                          borderColor: 'rgb(var(--border))',
                          backgroundColor: 'rgb(var(--bg-header-muted))',
                          color: 'rgb(var(--accent))',
                        }}
                        disabled={loading}
                      />
                      <label
                        htmlFor="terms"
                        style={{ color: 'rgb(var(--text-muted))' }}
                        className="text-sm"
                      >
                        Я соглашаюсь с{' '}
                        <Link
                          to="/terms"
                          style={{ color: 'rgb(var(--accent))' }}
                          className="hover:opacity-80 transition-opacity"
                        >
                          условиями использования
                        </Link>{' '}
                        и{' '}
                        <Link
                          to="/privacy"
                          style={{ color: 'rgb(var(--accent))' }}
                          className="hover:opacity-80 transition-opacity"
                        >
                          политикой конфиденциальности
                        </Link>
                      </label>
                    </div>
                  </CardContent>

                  <CardFooter className="flex-col space-y-4">
                    <Button
                      type="submit"
                      className="w-full h-12 rounded-xl text-white text-lg font-semibold shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                      style={{
                        background:
                          'linear-gradient(to right, rgb(var(--button-from)), rgb(var(--button-to)))',
                      }}
                      disabled={loading}
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
                          Регистрация...
                        </span>
                      ) : (
                        <span className="flex items-center gap-2">
                          Создать аккаунт
                          <ArrowRight className="h-5 w-5" />
                        </span>
                      )}
                    </Button>

                    <div
                      style={{ color: 'rgb(var(--text-muted))' }}
                      className="text-center text-sm"
                    >
                      Регистрация займет меньше минуты
                    </div>
                  </CardFooter>
                </form>
              </Card>
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
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
                    <span style={{ color: 'rgb(var(--text-primary))' }}>Преимущества JobHub</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    {features.map((feature, index) => (
                      <li key={index} className="flex items-center gap-3">
                        <CheckCircle
                          className="h-4 w-4 flex-shrink-0"
                          style={{ color: 'rgb(var(--accent))' }}
                        />
                        <span style={{ color: 'rgb(var(--text-primary))' }}>{feature}</span>
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
                    Ваша карьера начинается здесь
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center gap-3">
                      <div
                        className="p-2 rounded-lg"
                        style={{
                          backgroundColor: 'rgb(var(--accent))/20',
                        }}
                      >
                        <Briefcase className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
                      </div>
                      <div>
                        <div
                          className="font-semibold"
                          style={{ color: 'rgb(var(--text-primary))' }}
                        >
                          12K+ вакансий
                        </div>
                        <div style={{ color: 'rgb(var(--text-muted))' }} className="text-sm">
                          От ведущих компаний
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
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
                          Умный поиск
                        </div>
                        <div style={{ color: 'rgb(var(--text-muted))' }} className="text-sm">
                          Персонализированные рекомендации
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <div
                        className="p-2 rounded-lg"
                        style={{
                          backgroundColor: 'rgb(var(--accent))/20',
                        }}
                      >
                        <User className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
                      </div>
                      <div>
                        <div
                          className="font-semibold"
                          style={{ color: 'rgb(var(--text-primary))' }}
                        >
                          50K+ пользователей
                        </div>
                        <div style={{ color: 'rgb(var(--text-muted))' }} className="text-sm">
                          Уже нашли работу
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <div style={{ color: 'rgb(var(--text-muted))' }} className="text-center text-sm">
                Регистрируясь, вы получаете доступ ко всем функциям платформы совершенно бесплатно
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
