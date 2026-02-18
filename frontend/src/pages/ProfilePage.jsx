import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Mail, Phone, DollarSign, Briefcase, Save, X, Edit2, ArrowLeft } from 'lucide-react';
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
import { useAuth } from '@/utils/AuthContext';
import useNotification from '@/hooks/useNotification';
import UserProfileService from '@/api/services/UserProfileService';

export default function ProfilePage() {
  const navigate = useNavigate();
  const { user, isAuthenticated, checkAuth } = useAuth();
  const notification = useNotification();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [formError, setFormError] = useState('');
  const [profile, setProfile] = useState(null);

  const [formData, setFormData] = useState({
    full_name: '',
    phone: '',
    desired_salary: '',
    desired_position: '',
  });

  const fetchProfile = useCallback(async () => {
    setLoading(true);
    try {
      const data = await UserProfileService.getUserProfile(user.id);
      setProfile(data);
      setFormData({
        full_name: data.full_name || '',
        phone: data.phone || '',
        desired_salary: data.desired_salary?.toString() || '',
        desired_position: data.desired_position || '',
      });
    } catch (err) {
      if (err.response?.status === 404) {
        setProfile(null);
      } else {
        notification.error('Ошибка загрузки', 'Не удалось загрузить профиль');
      }
    } finally {
      setLoading(false);
    }
  }, [user?.id, notification]);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    if (user?.id) {
      fetchProfile();
    }
  }, [isAuthenticated, user?.id, fetchProfile, navigate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    setFormError('');
  };

  const validateForm = () => {
    if (formData.desired_salary && isNaN(Number(formData.desired_salary))) {
      setFormError('Зарплата должна быть числом');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) return;

    setSaving(true);
    setFormError('');

    try {
      const updateData = {
        full_name: formData.full_name || null,
        phone: formData.phone || null,
        desired_salary: formData.desired_salary ? Number(formData.desired_salary) : null,
        desired_position: formData.desired_position || null,
      };

      await UserProfileService.updateUserProfile(user.id, updateData);

      await checkAuth();

      notification.success('Профиль обновлен', 'Изменения успешно сохранены');
      setIsEditing(false);
      fetchProfile();
    } catch (err) {
      let errorMessage = 'Ошибка при сохранении профиля';

      if (err.response?.status === 400) {
        errorMessage = err.response.data?.detail || 'Некорректные данные';
      } else if (err.response?.status >= 500) {
        errorMessage = 'Ошибка сервера. Попробуйте позже.';
      }

      setFormError(errorMessage);
      notification.error('Ошибка сохранения', errorMessage);
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    if (profile) {
      setFormData({
        full_name: profile.full_name || '',
        phone: profile.phone || '',
        desired_salary: profile.desired_salary?.toString() || '',
        desired_position: profile.desired_position || '',
      });
    }
    setFormError('');
    setIsEditing(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="h-12 w-12 border-4 border-[rgb(var(--accent))] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p style={{ color: 'rgb(var(--text-muted))' }}>Загрузка профиля...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen transition-colors duration-300 pb-16">
      <div
        className="absolute top-0 left-0 right-0 h-px"
        style={{
          background: 'linear-gradient(to right, transparent, rgb(var(--accent))/30, transparent)',
        }}
      />

      <div className="container mx-auto px-6 py-12 relative z-10">
        <div className="max-w-3xl mx-auto">
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-4">
              <Button
                variant="ghost"
                onClick={() => navigate(-1)}
                className="h-10 w-10 p-0 rounded-full"
                style={{ color: 'rgb(var(--text-muted))' }}
              >
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <h1 className="text-3xl font-bold" style={{ color: 'rgb(var(--text-primary))' }}>
                Мой профиль
              </h1>
            </div>
            <p style={{ color: 'rgb(var(--text-muted))' }}>
              Управляйте информацией о вашем профиле
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
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="flex items-center gap-3">
                    <User className="h-6 w-6" style={{ color: 'rgb(var(--accent))' }} />
                    <span style={{ color: 'rgb(var(--text-primary))' }}>Личная информация</span>
                  </CardTitle>
                  <CardDescription style={{ color: 'rgb(var(--text-muted))' }}>
                    {isEditing ? 'Редактирование профиля' : 'Просмотр информации профиля'}
                  </CardDescription>
                </div>
                {!isEditing && (
                  <Button
                    onClick={() => setIsEditing(true)}
                    className="text-white"
                    style={{
                      background:
                        'linear-gradient(to right, rgb(var(--button-from)), rgb(var(--button-to)))',
                    }}
                  >
                    <Edit2 className="h-4 w-4 mr-2" />
                    Редактировать
                  </Button>
                )}
              </div>
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

                <div className="space-y-4">
                  <div className="space-y-2">
                    <label
                      className="text-sm font-medium flex items-center gap-2"
                      style={{ color: 'rgb(var(--text-primary))' }}
                    >
                      <Mail className="h-4 w-4" style={{ color: 'rgb(var(--accent))' }} />
                      Email
                    </label>
                    <Input
                      value={user?.email || ''}
                      disabled
                      className="h-11 backdrop-blur-sm focus:outline-none opacity-60"
                      style={{
                        backgroundColor: 'rgb(var(--bg-header-muted))',
                        borderColor: 'rgb(var(--border))',
                        color: 'rgb(var(--text-primary))',
                      }}
                    />
                  </div>

                  <div className="space-y-2">
                    <label
                      className="text-sm font-medium flex items-center gap-2"
                      style={{ color: 'rgb(var(--text-primary))' }}
                    >
                      <User className="h-4 w-4" style={{ color: 'rgb(var(--accent))' }} />
                      ФИО
                    </label>
                    <Input
                      name="full_name"
                      value={formData.full_name}
                      onChange={handleChange}
                      placeholder="Иванов Иван Иванович"
                      disabled={!isEditing || saving}
                      className="h-11 backdrop-blur-sm focus:outline-none"
                      style={{
                        backgroundColor: 'rgb(var(--bg-header-muted))',
                        borderColor: 'rgb(var(--border))',
                        color: 'rgb(var(--text-primary))',
                      }}
                    />
                  </div>

                  <div className="space-y-2">
                    <label
                      className="text-sm font-medium flex items-center gap-2"
                      style={{ color: 'rgb(var(--text-primary))' }}
                    >
                      <Briefcase className="h-4 w-4" style={{ color: 'rgb(var(--accent))' }} />
                      Желаемая должность
                    </label>
                    <Input
                      name="desired_position"
                      value={formData.desired_position}
                      onChange={handleChange}
                      placeholder="Frontend разработчик"
                      disabled={!isEditing || saving}
                      className="h-11 backdrop-blur-sm focus:outline-none"
                      style={{
                        backgroundColor: 'rgb(var(--bg-header-muted))',
                        borderColor: 'rgb(var(--border))',
                        color: 'rgb(var(--text-primary))',
                      }}
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label
                        className="text-sm font-medium flex items-center gap-2"
                        style={{ color: 'rgb(var(--text-primary))' }}
                      >
                        <DollarSign className="h-4 w-4" style={{ color: 'rgb(var(--accent))' }} />
                        Желаемая зарплата
                      </label>
                      <Input
                        name="desired_salary"
                        value={formData.desired_salary}
                        onChange={handleChange}
                        placeholder="150000"
                        disabled={!isEditing || saving}
                        className="h-11 backdrop-blur-sm focus:outline-none"
                        style={{
                          backgroundColor: 'rgb(var(--bg-header-muted))',
                          borderColor: 'rgb(var(--border))',
                          color: 'rgb(var(--text-primary))',
                        }}
                      />
                    </div>

                    <div className="space-y-2">
                      <label
                        className="text-sm font-medium flex items-center gap-2"
                        style={{ color: 'rgb(var(--text-primary))' }}
                      >
                        <Phone className="h-4 w-4" style={{ color: 'rgb(var(--accent))' }} />
                        Телефон
                      </label>
                      <Input
                        name="phone"
                        value={formData.phone}
                        onChange={handleChange}
                        placeholder="+7 (999) 123-45-67"
                        disabled={!isEditing || saving}
                        className="h-11 backdrop-blur-sm focus:outline-none"
                        style={{
                          backgroundColor: 'rgb(var(--bg-header-muted))',
                          borderColor: 'rgb(var(--border))',
                          color: 'rgb(var(--text-primary))',
                        }}
                      />
                    </div>
                  </div>
                </div>
              </CardContent>

              {isEditing && (
                <CardFooter className="flex justify-between gap-4">
                  <Button
                    type="button"
                    onClick={handleCancel}
                    disabled={saving}
                    variant="outline"
                    className="flex-1"
                    style={{
                      borderColor: 'rgb(var(--border))',
                      color: 'rgb(var(--text-primary))',
                      backgroundColor: 'rgb(var(--bg-header-muted))',
                    }}
                  >
                    <X className="h-4 w-4 mr-2" />
                    Отмена
                  </Button>
                  <Button
                    type="submit"
                    disabled={saving}
                    className="flex-1 text-white"
                    style={{
                      background:
                        'linear-gradient(to right, rgb(var(--button-from)), rgb(var(--button-to)))',
                    }}
                  >
                    {saving ? (
                      <span className="flex items-center gap-2">
                        <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        Сохранение...
                      </span>
                    ) : (
                      <span className="flex items-center gap-2">
                        <Save className="h-4 w-4" />
                        Сохранить
                      </span>
                    )}
                  </Button>
                </CardFooter>
              )}
            </form>
          </Card>
        </div>
      </div>
    </div>
  );
}
