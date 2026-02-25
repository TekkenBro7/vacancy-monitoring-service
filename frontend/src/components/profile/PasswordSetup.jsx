import { useState } from 'react';
import { Lock, Mail, CheckCircle2, AlertCircle, Key, Shield } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

export default function PasswordSetup({ user, onSave }) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [step, setStep] = useState('form');
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({ password: '', confirmPassword: '' });
  const [errors, setErrors] = useState({});

  const hasPassword = user?.password_hash;
  const userEmail = user?.email || 'ваш email';

  const validateForm = () => {
    const newErrors = {};
    if (!formData.password) {
      newErrors.password = 'Введите пароль';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Пароль должен быть не менее 6 символов';
    }
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Пароли не совпадают';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;
    setLoading(true);
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setLoading(false);
    setStep('email-sent');
  };

  const handleClose = () => {
    setIsModalOpen(false);
    setStep('form');
    setFormData({ password: '', confirmPassword: '' });
    setErrors({});
  };

  const passwordStrength = (password) => {
    if (!password) return { score: 0, label: '', color: 'bg-gray-700' };
    let score = 0;
    if (password.length >= 6) score += 1;
    if (password.length >= 10) score += 1;
    if (password.length >= 14) score += 1;
    if (/[A-Z]/.test(password)) score += 1;
    if (/[0-9]/.test(password)) score += 1;
    if (/[^A-Za-z0-9]/.test(password)) score += 1;
    const labels = [
      '',
      'Очень слабый',
      'Слабый',
      'Средний',
      'Хороший',
      'Очень хороший',
      'Отличный',
    ];
    const colors = [
      '',
      'bg-red-500',
      'bg-red-400',
      'bg-amber-500',
      'bg-yellow-500',
      'bg-lime-500',
      'bg-emerald-500',
    ];
    return { score, label: labels[score], color: colors[score] };
  };

  const strength = passwordStrength(formData.password);

  return (
    <>
      <Card
        className="backdrop-blur-sm border overflow-hidden"
        style={{
          backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
          borderColor: 'rgb(var(--border))',
        }}
      >
        <CardHeader className="pb-3 border-b" style={{ borderColor: 'rgb(var(--border)/0.5)' }}>
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-500/20 to-cyan-500/20 flex items-center justify-center">
              <Shield className="h-4 w-4" style={{ color: 'rgb(var(--accent))' }} />
            </div>
            <div>
              <CardTitle className="text-base" style={{ color: 'rgb(var(--text-primary))' }}>
                Безопасность аккаунта
              </CardTitle>
              <CardDescription className="text-xs">Управление способами входа</CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent className="pt-4 space-y-3">
          <div
            className="group relative flex items-center gap-4 p-4 rounded-xl transition-all duration-200 hover:translate-x-0.5"
            style={{ backgroundColor: 'rgb(var(--bg-header-muted))' }}
          >
            <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 rounded-full bg-gradient-to-b from-blue-500 to-cyan-500 opacity-0 group-hover:opacity-100 transition-opacity" />

            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <Mail className="h-5 w-5 text-white" />
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="font-medium text-sm" style={{ color: 'rgb(var(--text-primary))' }}>
                  Google
                </span>
                <Badge className="h-5 text-[10px] font-medium bg-emerald-500/10 text-emerald-400 border-emerald-500/20">
                  <CheckCircle2 className="h-2.5 w-2.5 mr-0.5" />
                  Активно
                </Badge>
              </div>
              <div className="text-xs truncate" style={{ color: 'rgb(var(--text-muted))' }}>
                {userEmail}
              </div>
            </div>
          </div>

          <div
            className="group relative flex items-center gap-4 p-4 rounded-xl transition-all duration-200 hover:translate-x-0.5"
            style={{ backgroundColor: 'rgb(var(--bg-header-muted))' }}
          >
            <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 rounded-full bg-gradient-to-b from-emerald-500 to-teal-500 opacity-0 group-hover:opacity-100 transition-opacity" />

            <div
              className={`h-10 w-10 rounded-xl flex items-center justify-center shadow-lg ${
                hasPassword
                  ? 'bg-gradient-to-br from-emerald-500 to-teal-500 shadow-emerald-500/20'
                  : 'bg-gradient-to-br from-amber-500 to-orange-500 shadow-amber-500/20'
              }`}
            >
              <Key className="h-5 w-5 text-white" />
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="font-medium text-sm" style={{ color: 'rgb(var(--text-primary))' }}>
                  Пароль
                </span>
                {hasPassword ? (
                  <Badge className="h-5 text-[10px] font-medium bg-emerald-500/10 text-emerald-400 border-emerald-500/20">
                    <CheckCircle2 className="h-2.5 w-2.5 mr-0.5" />
                    Активен
                  </Badge>
                ) : (
                  <Badge className="h-5 text-[10px] font-medium bg-amber-500/10 text-amber-400 border-amber-500/20">
                    Не активен
                  </Badge>
                )}
              </div>
              <div className="text-xs truncate" style={{ color: 'rgb(var(--text-muted))' }}>
                {hasPassword ? 'Пароль установлен' : 'Рекомендуем настроить'}
              </div>
            </div>

            {!hasPassword && (
              <Button
                size="sm"
                onClick={() => setIsModalOpen(true)}
                className="h-8 px-3 text-xs font-medium text-white shadow-lg transition-all duration-300 hover:shadow-xl hover:scale-105"
                style={{
                  background:
                    'linear-gradient(135deg, rgb(var(--button-from)), rgb(var(--button-to)))',
                }}
              >
                Настроить
              </Button>
            )}
          </div>

          {/* Info Banner */}
          {!hasPassword && (
            <div
              className="mt-2 p-3 rounded-xl border backdrop-blur-sm"
              style={{
                background: 'linear-gradient(135deg, rgb(var(--accent)/0.1), transparent)',
                borderColor: 'rgb(var(--accent)/0.2)',
              }}
            >
              <div className="flex gap-2.5">
                <AlertCircle
                  className="h-4 w-4 flex-shrink-0 mt-0.5"
                  style={{ color: 'rgb(var(--accent))' }}
                />
                <div className="space-y-0.5">
                  <p className="text-xs font-medium" style={{ color: 'rgb(var(--text-primary))' }}>
                    Зачем нужен пароль?
                  </p>
                  <p className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                    Пароль позволит вам входить в аккаунт без использования Google, а также повысит
                    безопасность вашего профиля
                  </p>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={isModalOpen} onOpenChange={handleClose}>
        <DialogContent
          className="border overflow-hidden"
          style={{
            backgroundColor: 'rgb(var(--bg-header))',
            borderColor: 'rgb(var(--border))',
            maxWidth: '480px',
          }}
        >
          {step === 'form' ? (
            <>
              <DialogHeader className="relative">
                <div className="relative">
                  <div className="mx-auto mb-4 h-16 w-16 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-xl shadow-blue-500/30">
                    <Lock className="h-7 w-7 text-white" />
                  </div>
                  <DialogTitle
                    className="text-center text-xl"
                    style={{ color: 'rgb(var(--text-primary))' }}
                  >
                    Настройка пароля
                  </DialogTitle>
                  <DialogDescription className="text-center max-w-sm mx-auto">
                    Придумайте надёжный пароль для входа в аккаунт
                  </DialogDescription>
                </div>
              </DialogHeader>

              <div className="space-y-5 py-4">
                {/* Email Info Chip */}
                <div
                  className="inline-flex items-center gap-2 px-4 py-2 mx-auto rounded-full text-sm border backdrop-blur-sm"
                  style={{
                    backgroundColor: 'rgb(var(--bg-header-muted))',
                    borderColor: 'rgb(var(--border))',
                  }}
                >
                  <Mail className="h-3.5 w-3.5" style={{ color: 'rgb(var(--accent))' }} />
                  <span className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                    Код подтверждения на
                  </span>
                  <span
                    className="text-xs font-medium px-2 py-0.5 rounded-full"
                    style={{ backgroundColor: 'rgb(var(--accent)/0.1)' }}
                  >
                    {userEmail}
                  </span>
                </div>

                {/* Password Field */}
                <div className="space-y-2">
                  <label
                    className="text-sm font-medium flex items-center gap-2"
                    style={{ color: 'rgb(var(--text-primary))' }}
                  >
                    <Lock className="h-3.5 w-3.5" style={{ color: 'rgb(var(--accent))' }} />
                    Новый пароль
                  </label>
                  <Input
                    type="password"
                    value={formData.password}
                    onChange={(e) => {
                      setFormData({ ...formData, password: e.target.value });
                      setErrors({ ...errors, password: undefined });
                    }}
                    placeholder="Придумайте надёжный пароль"
                    className={`h-11 transition-all ${errors.password ? 'border-red-500/50 ring-1 ring-red-500/20' : ''}`}
                    style={{
                      backgroundColor: 'rgb(var(--bg-header-muted))',
                      borderColor: errors.password ? undefined : 'rgb(var(--border))',
                      color: 'rgb(var(--text-primary))',
                    }}
                  />

                  {/* Password Strength */}
                  {formData.password && (
                    <div className="space-y-3 pt-2">
                      <div className="flex justify-between text-xs">
                        <span style={{ color: 'rgb(var(--text-muted))' }}>Надёжность пароля</span>
                        <span
                          className="font-medium"
                          style={{
                            color:
                              strength.score >= 3 ? 'rgb(var(--accent))' : 'rgb(var(--text-muted))',
                          }}
                        >
                          {strength.label}
                        </span>
                      </div>
                      <div
                        className="h-2 w-full rounded-full overflow-hidden"
                        style={{ backgroundColor: 'rgb(var(--border)/0.3)' }}
                      >
                        <div
                          className={`h-full ${strength.color} transition-all duration-300 rounded-full`}
                          style={{ width: `${(strength.score / 5) * 100}%` }}
                        />
                      </div>
                      <div className="grid grid-cols-1 gap-2 text-[10px]">
                        {[{ text: 'Минимум 6 символов', test: formData.password.length >= 6 }].map(
                          (item, idx) => (
                            <div
                              key={idx}
                              className="px-2 py-1 rounded-full text-center"
                              style={{
                                backgroundColor: item.test
                                  ? 'rgb(var(--accent)/0.1)'
                                  : 'rgb(var(--border)/0.3)',
                                color: item.test ? 'rgb(var(--accent))' : 'rgb(var(--text-muted))',
                              }}
                            >
                              {item.test ? '✓' : '○'} {item.text}
                            </div>
                          )
                        )}
                      </div>
                    </div>
                  )}

                  {errors.password && (
                    <p
                      className="text-xs flex items-center gap-1 mt-1"
                      style={{ color: 'rgb(var(--error-text))' }}
                    >
                      <AlertCircle className="h-3 w-3" />
                      {errors.password}
                    </p>
                  )}
                </div>

                {/* Confirm Password Field */}
                <div className="space-y-2">
                  <label
                    className="text-sm font-medium flex items-center gap-2"
                    style={{ color: 'rgb(var(--text-primary))' }}
                  >
                    <Lock className="h-3.5 w-3.5" style={{ color: 'rgb(var(--accent))' }} />
                    Подтверждение пароля
                  </label>
                  <Input
                    type="password"
                    value={formData.confirmPassword}
                    onChange={(e) => {
                      setFormData({ ...formData, confirmPassword: e.target.value });
                      setErrors({ ...errors, confirmPassword: undefined });
                    }}
                    placeholder="Повторите введённый пароль"
                    className={`h-11 transition-all ${errors.confirmPassword ? 'border-red-500/50 ring-1 ring-red-500/20' : ''}`}
                    style={{
                      backgroundColor: 'rgb(var(--bg-header-muted))',
                      borderColor: errors.confirmPassword ? undefined : 'rgb(var(--border))',
                      color: 'rgb(var(--text-primary))',
                    }}
                  />
                  {errors.confirmPassword && (
                    <p
                      className="text-xs flex items-center gap-1 mt-1"
                      style={{ color: 'rgb(var(--error-text))' }}
                    >
                      <AlertCircle className="h-3 w-3" />
                      {errors.confirmPassword}
                    </p>
                  )}
                </div>
              </div>

              <DialogFooter className="gap-2">
                <Button
                  variant="outline"
                  onClick={handleClose}
                  disabled={loading}
                  className="flex-1 h-11 border transition-all hover:bg-opacity-80"
                  style={{
                    borderColor: 'rgb(var(--border))',
                    color: 'rgb(var(--text-primary))',
                    backgroundColor: 'transparent',
                  }}
                >
                  Отмена
                </Button>
                <Button
                  onClick={handleSubmit}
                  disabled={loading}
                  className="flex-1 h-11 text-white shadow-lg transition-all duration-300 hover:shadow-xl hover:scale-[1.02] disabled:opacity-50"
                  style={{
                    background:
                      'linear-gradient(135deg, rgb(var(--button-from)), rgb(var(--button-to)))',
                  }}
                >
                  {loading ? (
                    <span className="flex items-center gap-2">
                      <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Отправка...
                    </span>
                  ) : (
                    <span className="flex items-center gap-2">
                      <Mail className="h-4 w-4" />
                      Отправить код
                    </span>
                  )}
                </Button>
              </DialogFooter>
            </>
          ) : (
            <>
              <DialogHeader>
                <div className="mx-auto mb-4 h-20 w-20 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center shadow-xl shadow-emerald-500/30">
                  <Mail className="h-8 w-8 text-white" />
                </div>
                <DialogTitle
                  className="text-center text-xl"
                  style={{ color: 'rgb(var(--text-primary))' }}
                >
                  Письмо отправлено!
                </DialogTitle>
                <DialogDescription className="text-center">
                  Мы отправили код подтверждения на адрес
                </DialogDescription>
                <div
                  className="mt-2 inline-block mx-auto px-4 py-2 rounded-full text-sm font-medium"
                  style={{ backgroundColor: 'rgb(var(--accent)/0.1)' }}
                >
                  {userEmail}
                </div>
              </DialogHeader>

              <div className="space-y-4 py-4">
                <div
                  className="p-4 rounded-xl text-center border"
                  style={{
                    backgroundColor: 'rgb(var(--bg-header-muted))',
                    borderColor: 'rgb(var(--border))',
                  }}
                >
                  <p className="text-sm mb-1" style={{ color: 'rgb(var(--text-primary))' }}>
                    Введите код из письма
                  </p>
                  <p className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                    для подтверждения смены пароля
                  </p>
                </div>

                <div
                  className="flex items-start gap-3 p-3 rounded-lg text-xs"
                  style={{ backgroundColor: 'rgb(var(--accent)/0.05)' }}
                >
                  <AlertCircle
                    className="h-4 w-4 flex-shrink-0 mt-0.5"
                    style={{ color: 'rgb(var(--accent))' }}
                  />
                  <div className="space-y-1" style={{ color: 'rgb(var(--text-muted))' }}>
                    <p className="font-medium" style={{ color: 'rgb(var(--text-primary))' }}>
                      Важно:
                    </p>
                    <p>• Код действителен 15 минут</p>
                    <p>• Никому не сообщайте код подтверждения</p>
                  </div>
                </div>
              </div>

              <DialogFooter className="gap-2">
                <Button
                  variant="outline"
                  onClick={handleClose}
                  className="flex-1 h-11 border transition-all"
                  style={{
                    borderColor: 'rgb(var(--border))',
                    color: 'rgb(var(--text-primary))',
                    backgroundColor: 'transparent',
                  }}
                >
                  Закрыть
                </Button>
                <Button
                  className="flex-1 h-11 text-white shadow-lg transition-all duration-300 hover:shadow-xl hover:scale-[1.02]"
                  style={{
                    background:
                      'linear-gradient(135deg, rgb(var(--button-from)), rgb(var(--button-to)))',
                  }}
                >
                  <Shield className="h-4 w-4 mr-2" />
                  Ввести код
                </Button>
              </DialogFooter>
            </>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}
