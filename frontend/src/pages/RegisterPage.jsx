import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  User,
  Mail,
  Lock,
  Eye,
  EyeOff,
  Sparkles,
  ArrowRight,
  CheckCircle,
  CheckCircle2,
  Shield,
  Key,
  AlertCircle,
  Zap,
  Building,
  TrendingUp,
  Loader2,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import Logo from '@/components/ui_my/Logo';
import { UserService } from '@/api/services/UserService';
import useNotification from '@/hooks/useNotification';

export default function RegisterPage() {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formError, setFormError] = useState('');
  const notification = useNotification();

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  const [verificationCode, setVerificationCode] = useState('');
  const [verificationErrors, setVerificationErrors] = useState({});
  const [isVerificationModalOpen, setIsVerificationModalOpen] = useState(false);

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
      await UserService.sendVerificationCode(
        formData.email,
        'register',
        formData.password,
        formData.username
      );
      setIsVerificationModalOpen(true);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Ошибка отправки кода';
      setFormError(errorMessage);
      notification.error('Ошибка регистрации', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyCode = async () => {
    if (!verificationCode) {
      setVerificationErrors({ code: 'Введите код' });
      return;
    }

    setLoading(true);
    try {
      await UserService.verifyCode(formData.email, verificationCode, 'register');
      notification.success('Регистрация успешна', 'Сейчас вы будете перенаправлены');
      setIsVerificationModalOpen(false);
      navigate('/login');
    } catch (err) {
      const message = err.response?.data?.detail || 'Неверный код';
      setVerificationErrors({ code: message });
      notification.error('Ошибка', message);
    } finally {
      setLoading(false);
    }
  };

  const handleResendCode = async () => {
    setLoading(true);
    try {
      await UserService.sendVerificationCode(
        formData.email,
        'register',
        formData.password,
        formData.username
      );
      notification.success('Код отправлен', 'Проверьте почту');
    } catch (err) {
      const message = err.response?.data?.detail || 'Не удалось отправить код';
      notification.error('Ошибка', message);
    } finally {
      setLoading(false);
    }
  };

  const handleCloseVerification = () => {
    setIsVerificationModalOpen(false);
    setVerificationCode('');
    setVerificationErrors({});
  };

  const passwordStrength = (password) => {
    if (!password) return { strength: 0, label: '', color: 'bg-gray-500' };

    let score = 0;
    if (password.length >= 6) score += 1;
    if (/[A-Z]/.test(password)) score += 1;
    if (/[0-9]/.test(password)) score += 1;
    if (/[^A-Za-z0-9]/.test(password)) score += 1;

    if (score === 1) return { strength: 25, label: 'Слабый', color: 'bg-red-500' };
    if (score === 2) return { strength: 50, label: 'Средний', color: 'bg-amber-500' };
    if (score === 3) return { strength: 75, label: 'Хороший', color: 'bg-blue-500' };
    if (score === 4) return { strength: 100, label: 'Отличный', color: 'bg-emerald-500' };
    return { strength: 0, label: '', color: 'bg-gray-500' };
  };

  const strength = passwordStrength(formData.password);

  const features = [
    { icon: Zap, text: 'Мгновенный доступ к 10K+ вакансий', color: 'from-amber-500 to-orange-500' },
    {
      icon: Sparkles,
      text: 'AI-сравнение вакансий',
      color: 'from-violet-500 to-purple-500',
    },
    {
      icon: TrendingUp,
      text: 'Аналитика и сравнение вакансий',
      color: 'from-emerald-500 to-teal-500',
    },
    { icon: Building, text: '500+ проверенных компаний', color: 'from-blue-500 to-cyan-500' },
  ];

  const benefits = [
    'Удобный поиск',
    'Сравнение предложений',
    'Агрегация из различных источников',
    'Бесплатно навсегда',
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
                      Создать аккаунт
                    </h1>
                    <p style={{ color: 'rgb(var(--text-muted))' }}>
                      Присоединяйтесь к сообществу профессионалов
                    </p>
                  </div>
                </div>

                <form onSubmit={handleSubmit} className="p-8 space-y-5">
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
                    />
                  </div>

                  <div className="space-y-2">
                    <label
                      className="text-sm font-medium flex items-center gap-2"
                      style={{ color: 'rgb(var(--text-primary))' }}
                    >
                      <Mail className="h-4 w-4" style={{ color: 'rgb(var(--accent))' }} />
                      Email
                    </label>
                    <Input
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleChange}
                      placeholder="Введите email"
                      className="h-12 rounded-xl text-base transition-all duration-300 border-2 focus:border-[rgb(var(--accent))] focus:ring-0 focus:shadow-lg focus:shadow-[rgb(var(--accent))]/10"
                      style={{
                        backgroundColor: 'rgb(var(--bg-header-muted)/0.5)',
                        borderColor: 'rgb(var(--border))',
                        color: 'rgb(var(--text-primary))',
                      }}
                      disabled={loading}
                      autoComplete="email"
                    />
                  </div>

                  <div className="space-y-2">
                    <label
                      className="text-sm font-medium flex items-center gap-2"
                      style={{ color: 'rgb(var(--text-primary))' }}
                    >
                      <Lock className="h-4 w-4" style={{ color: 'rgb(var(--accent))' }} />
                      Пароль
                    </label>
                    <div className="relative">
                      <Input
                        name="password"
                        type={showPassword ? 'text' : 'password'}
                        value={formData.password}
                        onChange={handleChange}
                        placeholder="Минимум 6 символов"
                        className="h-12 pr-12 rounded-xl text-base transition-all duration-300 border-2 focus:border-[rgb(var(--accent))] focus:ring-0 focus:shadow-lg focus:shadow-[rgb(var(--accent))]/10"
                        style={{
                          backgroundColor: 'rgb(var(--bg-header-muted)/0.5)',
                          borderColor: 'rgb(var(--border))',
                          color: 'rgb(var(--text-primary))',
                        }}
                        disabled={loading}
                        autoComplete="new-password"
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

                    {formData.password && (
                      <div className="space-y-1.5 animate-fade-in">
                        <div className="flex justify-between items-center">
                          <span className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                            Надежность пароля
                          </span>
                          <span
                            className="text-xs font-medium"
                            style={{ color: 'rgb(var(--text-primary))' }}
                          >
                            {strength.label}
                          </span>
                        </div>
                        <div
                          className="h-1.5 w-full rounded-full overflow-hidden"
                          style={{ backgroundColor: 'rgb(var(--border)/0.5)' }}
                        >
                          <div
                            className={`h-full ${strength.color} transition-all duration-500`}
                            style={{ width: `${strength.strength}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="space-y-2">
                    <label
                      className="text-sm font-medium flex items-center gap-2"
                      style={{ color: 'rgb(var(--text-primary))' }}
                    >
                      <Lock className="h-4 w-4" style={{ color: 'rgb(var(--accent))' }} />
                      Подтвердите пароль
                    </label>
                    <div className="relative">
                      <Input
                        name="confirmPassword"
                        type={showConfirmPassword ? 'text' : 'password'}
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        placeholder="Повторите пароль"
                        className="h-12 pr-12 rounded-xl text-base transition-all duration-300 border-2 focus:border-[rgb(var(--accent))] focus:ring-0 focus:shadow-lg focus:shadow-[rgb(var(--accent))]/10"
                        style={{
                          backgroundColor: 'rgb(var(--bg-header-muted)/0.5)',
                          borderColor:
                            formData.confirmPassword &&
                            formData.password !== formData.confirmPassword
                              ? 'rgb(239, 68, 68)'
                              : 'rgb(var(--border))',
                          color: 'rgb(var(--text-primary))',
                        }}
                        disabled={loading}
                        autoComplete="new-password"
                      />
                      <button
                        type="button"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        className="absolute right-4 top-1/2 -translate-y-1/2 p-1 rounded-lg transition-all hover:bg-[rgb(var(--accent))]/10"
                        style={{ color: 'rgb(var(--text-muted))' }}
                        disabled={loading}
                      >
                        {showConfirmPassword ? (
                          <EyeOff className="h-5 w-5" />
                        ) : (
                          <Eye className="h-5 w-5" />
                        )}
                      </button>
                    </div>
                    {formData.confirmPassword && formData.password === formData.confirmPassword && (
                      <p
                        className="text-xs flex items-center gap-1 animate-fade-in"
                        style={{ color: 'rgb(34, 197, 94)' }}
                      >
                        <CheckCircle className="h-3 w-3" />
                        Пароли совпадают
                      </p>
                    )}
                  </div>

                  <div className="flex items-start gap-3 pt-2">
                    <input
                      type="checkbox"
                      id="terms"
                      required
                      className="mt-1 h-4 w-4 rounded border-2 transition-all focus:ring-2 focus:ring-offset-0"
                      style={{
                        borderColor: 'rgb(var(--border))',
                        accentColor: 'rgb(var(--accent))',
                      }}
                      disabled={loading}
                    />
                    <label
                      htmlFor="terms"
                      className="text-sm leading-relaxed"
                      style={{ color: 'rgb(var(--text-muted))' }}
                    >
                      Я соглашаюсь с{' '}
                      <Link
                        to="/terms"
                        className="font-medium hover:underline"
                        style={{ color: 'rgb(var(--accent))' }}
                      >
                        условиями использования
                      </Link>{' '}
                      и{' '}
                      <Link
                        to="/privacy"
                        className="font-medium hover:underline"
                        style={{ color: 'rgb(var(--accent))' }}
                      >
                        политикой конфиденциальности
                      </Link>
                    </label>
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
                        Отправка...
                      </span>
                    ) : (
                      <span className="flex items-center gap-2">
                        Создать аккаунт
                        <ArrowRight className="h-5 w-5" />
                      </span>
                    )}
                  </Button>

                  <div className="text-center pt-2">
                    <p style={{ color: 'rgb(var(--text-muted))' }}>
                      Уже есть аккаунт?{' '}
                      <Link
                        to="/login"
                        className="font-semibold transition-all hover:opacity-80"
                        style={{ color: 'rgb(var(--accent))' }}
                      >
                        Войти
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
                  Бесплатная регистрация
                </Badge>
                <h2
                  className="text-3xl lg:text-4xl font-bold mb-4"
                  style={{ color: 'rgb(var(--text-primary))' }}
                >
                  Начните{' '}
                  <span
                    className="bg-clip-text text-transparent"
                    style={{
                      backgroundImage:
                        'linear-gradient(135deg, rgb(var(--accent)), rgb(168, 85, 247))',
                    }}
                  >
                    карьерный рост
                  </span>
                </h2>
                <p className="text-lg" style={{ color: 'rgb(var(--text-muted))' }}>
                  Получите доступ ко всем возможностям платформы за пару минут
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
                <div className="flex items-center gap-3 mb-4">
                  <div
                    className="p-2 rounded-lg"
                    style={{ backgroundColor: 'rgb(var(--accent))/0.1' }}
                  >
                    <CheckCircle className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
                  </div>
                  <span className="font-semibold" style={{ color: 'rgb(var(--text-primary))' }}>
                    Что вы получите
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  {benefits.map((benefit, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <div
                        className="w-1.5 h-1.5 rounded-full flex-shrink-0"
                        style={{ backgroundColor: 'rgb(var(--accent))' }}
                      />
                      <span className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                        {benefit}
                      </span>
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

              <p className="text-sm text-center" style={{ color: 'rgb(var(--text-muted))' }}>
                Регистрация займет меньше минуты
              </p>
            </div>
          </div>
        </div>
      </div>

      <Dialog
        open={isVerificationModalOpen}
        onOpenChange={(open) => {
          if (!open) handleCloseVerification();
        }}
      >
        <DialogContent
          showCloseButton={false}
          className="border overflow-hidden rounded-2xl"
          style={{
            backgroundColor: 'rgb(var(--bg-header))',
            borderColor: 'rgb(var(--border))',
            maxWidth: '420px',
          }}
          onInteractOutside={(e) => e.preventDefault()}
          onEscapeKeyDown={(e) => e.preventDefault()}
        >
          <div
            className="absolute top-0 left-0 right-0 h-1"
            style={{
              background:
                'linear-gradient(90deg, rgb(var(--accent)), rgb(168, 85, 247), rgb(var(--accent)))',
            }}
          />

          <DialogHeader className="pt-6">
            <div className="mx-auto mb-4 h-16 w-16 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-xl">
              <Mail className="h-7 w-7 text-white" />
            </div>
            <DialogTitle
              className="text-center text-xl"
              style={{ color: 'rgb(var(--text-primary))' }}
            >
              Подтверждение email
            </DialogTitle>
            <DialogDescription className="text-center">
              Мы отправили код на вашу почту
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-5 py-4">
            <div className="flex justify-center">
              <div
                className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm border"
                style={{
                  backgroundColor: 'rgb(var(--bg-header-muted)/0.5)',
                  borderColor: 'rgb(var(--border))',
                }}
              >
                <Mail className="h-4 w-4" style={{ color: 'rgb(var(--accent))' }} />
                <span style={{ color: 'rgb(var(--text-primary))' }}>{formData.email}</span>
              </div>
            </div>

            <div className="space-y-2">
              <label
                className="text-sm font-medium flex items-center gap-2"
                style={{ color: 'rgb(var(--text-primary))' }}
              >
                <Key className="h-4 w-4" style={{ color: 'rgb(var(--accent))' }} />
                Код подтверждения
              </label>
              <Input
                type="text"
                value={verificationCode}
                onChange={(e) => {
                  setVerificationCode(e.target.value.replace(/\D/g, '').slice(0, 6));
                  setVerificationErrors({});
                }}
                placeholder="000000"
                maxLength={6}
                className={`h-14 text-center text-2xl tracking-[0.5em] font-mono rounded-xl transition-all border-2 ${
                  verificationErrors.code ? 'border-red-500' : ''
                }`}
                style={{
                  backgroundColor: 'rgb(var(--bg-header-muted)/0.5)',
                  borderColor: verificationErrors.code ? undefined : 'rgb(var(--border))',
                  color: 'rgb(var(--text-primary))',
                }}
              />
              {verificationErrors.code && (
                <p
                  className="text-xs flex items-center gap-1"
                  style={{ color: 'rgb(239, 68, 68)' }}
                >
                  <AlertCircle className="h-3 w-3" />
                  {verificationErrors.code}
                </p>
              )}
            </div>

            <div
              className="flex items-start gap-3 p-4 rounded-xl text-sm"
              style={{
                backgroundColor: 'rgb(var(--accent)/0.05)',
                border: '1px solid rgb(var(--accent)/0.1)',
              }}
            >
              <AlertCircle
                className="h-5 w-5 flex-shrink-0"
                style={{ color: 'rgb(var(--accent))' }}
              />
              <div style={{ color: 'rgb(var(--text-muted))' }}>
                <p>
                  Код действителен{' '}
                  <strong style={{ color: 'rgb(var(--text-primary))' }}>15 минут</strong>
                </p>
                <p className="mt-1">Проверьте папку «Спам», если письмо не пришло</p>
              </div>
            </div>

            <div className="text-center">
              <button
                type="button"
                onClick={handleResendCode}
                disabled={loading}
                className="text-sm font-medium hover:underline disabled:opacity-50 transition-all"
                style={{ color: 'rgb(var(--accent))' }}
              >
                Отправить код повторно
              </button>
            </div>
          </div>

          <DialogFooter className="gap-3 pb-2">
            <Button
              type="button"
              variant="outline"
              onClick={handleCloseVerification}
              disabled={loading}
              className="flex-1 h-11 rounded-xl border-2 transition-all"
              style={{
                borderColor: 'rgb(var(--border))',
                color: 'rgb(var(--text-primary))',
              }}
            >
              Отмена
            </Button>
            <Button
              type="button"
              onClick={handleVerifyCode}
              disabled={loading || verificationCode.length < 6}
              className="flex-1 h-11 rounded-xl text-white transition-all duration-300 hover:scale-[1.02] hover:shadow-xl disabled:opacity-50"
              style={{
                background:
                  'linear-gradient(135deg, rgb(var(--button-from)), rgb(var(--button-to)))',
              }}
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Проверка...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4" />
                  Подтвердить
                </span>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
