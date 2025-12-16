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
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900 text-white overflow-hidden">
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-blue-500/30 to-transparent"></div>
      <div className="absolute top-10 right-10 w-64 h-64 bg-gradient-to-br from-blue-500/10 to-cyan-500/10 rounded-full blur-3xl"></div>
      <div className="absolute bottom-10 left-10 w-56 h-56 bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-full blur-3xl"></div>

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
              Уже есть аккаунт?{' '}
              <Link to="/login" className="text-blue-400 hover:text-blue-300 font-medium">
                Войти
              </Link>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
            <div>
              <div className="mb-8">
                <h1 className="text-4xl font-bold mb-4">
                  <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                    Создайте аккаунт
                  </span>
                  <br />
                  <span className="text-white">и начните карьерный рост</span>
                </h1>
                <p className="text-gray-400">Присоединяйтесь к сообществу профессионалов</p>
              </div>

              <Card className="bg-gray-800/30 backdrop-blur-sm border-gray-700/50">
                <CardHeader>
                  <CardTitle>Регистрация</CardTitle>
                  <CardDescription className="text-gray-400">
                    Заполните форму для создания аккаунта
                  </CardDescription>
                </CardHeader>

                <form onSubmit={handleSubmit}>
                  <CardContent className="space-y-6">
                    {formError && (
                      <Alert variant="destructive" className="bg-red-500/20 border-red-500/30">
                        <AlertDescription className="text-red-300">{formError}</AlertDescription>
                      </Alert>
                    )}

                    {/* Имя пользователя */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-300">Имя пользователя</label>
                      <div className="relative">
                        <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-blue-400" />
                        <Input
                          name="username"
                          value={formData.username}
                          onChange={handleChange}
                          placeholder="Введите имя пользователя"
                          className="pl-10 h-11 bg-gray-800/50 border-gray-700 text-white placeholder:text-gray-500"
                          disabled={loading}
                          autoComplete="username"
                        />
                      </div>
                    </div>

                    {/* Email */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-300">Email</label>
                      <div className="relative">
                        <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-blue-400" />
                        <Input
                          name="email"
                          type="email"
                          value={formData.email}
                          onChange={handleChange}
                          placeholder="Введите email"
                          className="pl-10 h-11 bg-gray-800/50 border-gray-700 text-white placeholder:text-gray-500"
                          disabled={loading}
                          autoComplete="email"
                        />
                      </div>
                    </div>

                    {/* Пароль */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-300">Пароль</label>
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
                          autoComplete="new-password"
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

                      {/* Индикатор сложности пароля */}
                      {formData.password && (
                        <div className="space-y-1">
                          <div className="flex justify-between text-xs text-gray-400">
                            <span>Сложность пароля</span>
                            <span>{strength.strength}%</span>
                          </div>
                          <div className="h-2 w-full bg-gray-700 rounded-full overflow-hidden">
                            <div
                              className={`h-full ${strength.color} transition-all duration-300`}
                              style={{ width: `${strength.strength}%` }}
                            ></div>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Подтверждение пароля */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-300">
                        Подтвердите пароль
                      </label>
                      <div className="relative">
                        <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-blue-400" />
                        <Input
                          name="confirmPassword"
                          type="password"
                          value={formData.confirmPassword}
                          onChange={handleChange}
                          placeholder="Повторите пароль"
                          className="pl-10 h-11 bg-gray-800/50 border-gray-700 text-white placeholder:text-gray-500"
                          disabled={loading}
                          autoComplete="new-password"
                        />
                      </div>
                    </div>

                    {/* Условия использования */}
                    <div className="flex items-start space-x-3">
                      <input
                        type="checkbox"
                        id="terms"
                        required
                        className="mt-1 h-4 w-4 rounded border-gray-600 bg-gray-700 text-blue-500 focus:ring-blue-500"
                        disabled={loading}
                      />
                      <label htmlFor="terms" className="text-sm text-gray-400">
                        Я соглашаюсь с{' '}
                        <Link to="/terms" className="text-blue-400 hover:text-blue-300">
                          условиями использования
                        </Link>{' '}
                        и{' '}
                        <Link to="/privacy" className="text-blue-400 hover:text-blue-300">
                          политикой конфиденциальности
                        </Link>
                      </label>
                    </div>
                  </CardContent>

                  <CardFooter className="flex-col space-y-4">
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
                          Регистрация...
                        </span>
                      ) : (
                        <span className="flex items-center gap-2">
                          Создать аккаунт
                          <ArrowRight className="h-5 w-5" />
                        </span>
                      )}
                    </Button>

                    <div className="text-center text-sm text-gray-500">
                      Регистрация займет меньше минуты
                    </div>
                  </CardFooter>
                </form>
              </Card>
            </div>

            {/* Правая часть - информация */}
            <div className="space-y-8">
              <Card className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-sm border-gray-700/50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="h-5 w-5 text-emerald-400" />
                    Преимущества JobHub
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    {features.map((feature, index) => (
                      <li key={index} className="flex items-center gap-3 text-gray-300">
                        <CheckCircle className="h-4 w-4 text-emerald-400 flex-shrink-0" />
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-blue-900/20 to-purple-900/20 backdrop-blur-sm border-blue-500/30">
                <CardHeader>
                  <CardTitle>Ваша карьера начинается здесь</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-blue-500/20">
                        <Briefcase className="h-5 w-5 text-blue-400" />
                      </div>
                      <div>
                        <div className="font-semibold">12K+ вакансий</div>
                        <div className="text-sm text-gray-400">От ведущих компаний</div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-purple-500/20">
                        <Sparkles className="h-5 w-5 text-purple-400" />
                      </div>
                      <div>
                        <div className="font-semibold">Умный поиск</div>
                        <div className="text-sm text-gray-400">
                          Персонализированные рекомендации
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-emerald-500/20">
                        <User className="h-5 w-5 text-emerald-400" />
                      </div>
                      <div>
                        <div className="font-semibold">50K+ пользователей</div>
                        <div className="text-sm text-gray-400">Уже нашли работу</div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <div className="text-center text-sm text-gray-500">
                Регистрируясь, вы получаете доступ ко всем функциям платформы совершенно бесплатно
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
