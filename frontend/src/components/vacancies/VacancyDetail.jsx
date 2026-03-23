import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Building,
  MapPin,
  DollarSign,
  Clock,
  ExternalLink,
  Bookmark,
  Share2,
  Calendar,
  Globe,
  Briefcase,
  TrendingUp,
  Users,
  CheckCircle,
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import VacancyService from '@/api/services/VacancyService';
import useNotification from '@/hooks/useNotification';

export default function VacancyDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const notification = useNotification();
  const [vacancy, setVacancy] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadVacancy();
  }, [id]);

  const loadVacancy = async () => {
    try {
      setLoading(true);
      const data = await VacancyService.getVacancyById(id);
      setVacancy(data);
    } catch (error) {
      notification.error('Ошибка', 'Не удалось загрузить вакансию');
      console.error('Error loading vacancy:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatSalary = (from, to, currency) => {
    if (!from && !to) return 'По договорённости';

    const parts = [];
    if (from) parts.push(from.toLocaleString());
    if (to) parts.push(to.toLocaleString());

    const symbol = currency?.symbol || '₽';
    const result = parts.join(' - ');

    if (from && to) {
      return `${symbol} ${result}`;
    } else if (from) {
      return `от ${symbol} ${result}`;
    } else {
      return `до ${symbol} ${result}`;
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Не указано';
    return new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const timeAgo = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);

    if (diffInSeconds < 60) return 'Только что';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} мин назад`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} ч назад`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)} дн назад`;

    return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' });
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: vacancy?.title,
        text: `Вакансия: ${vacancy?.title}`,
        url: window.location.href,
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      notification.success('Ссылка скопирована', 'URL вакансии в буфере обмена');
    }
  };

  const handleBookmark = () => {
    notification.info('В разработке', 'Функция сохранения будет доступна soon');
  };

  if (loading) {
    return (
      <div className="container mx-auto px-6 py-8">
        <div className="max-w-5xl mx-auto">
          <div className="h-10 w-64 mb-6 animate-pulse rounded" style={{ backgroundColor: 'rgb(var(--bg-header-muted)/0.5)' }} />
          <div className="h-96 rounded-2xl animate-pulse" style={{ backgroundColor: 'rgb(var(--bg-header-muted)/0.3)' }} />
        </div>
      </div>
    );
  }

  if (!vacancy) {
    return (
      <div className="container mx-auto px-6 py-8">
        <div className="max-w-5xl mx-auto text-center py-16">
          <h2 className="text-2xl font-bold mb-4" style={{ color: 'rgb(var(--text-primary))' }}>
            Вакансия не найдена
          </h2>
          <Button onClick={() => navigate('/vacancies')} className="text-white">
            <ArrowLeft className="h-4 w-4 mr-2" />
            К списку вакансий
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-8 animate-fade-in">
      <div className="container mx-auto px-6">
        <div className="max-w-5xl mx-auto">
          {/* Back Button */}
          <div className="flex items-center justify-between mb-6 animate-fade-in-down">
            <Button
              variant="ghost"
              onClick={() => navigate('/vacancies')}
              className="pl-0 hover:bg-transparent"
              style={{ color: 'rgb(var(--text-muted))' }}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Назад к списку
            </Button>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleShare}
                className="transition-all duration-300 hover:scale-105"
                style={{
                  borderColor: 'rgb(var(--border))',
                  color: 'rgb(var(--text-primary))',
                }}
              >
                <Share2 className="h-4 w-4 mr-2" />
                Поделиться
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleBookmark}
                className="transition-all duration-300 hover:scale-105"
                style={{
                  borderColor: 'rgb(var(--border))',
                  color: 'rgb(var(--text-primary))',
                }}
              >
                <Bookmark className="h-4 w-4 mr-2" />
                Сохранить
              </Button>
            </div>
          </div>

          {/* Main Card */}
          <div
            className="rounded-2xl backdrop-blur-sm border shadow-xl overflow-hidden animate-fade-in-up"
            style={{
              backgroundColor: 'rgb(var(--bg-header-muted)/0.4)',
              borderColor: 'rgb(var(--border)/0.5)',
            }}
          >
            {/* Header with Gradient */}
            <div
              className="relative p-8 border-b overflow-hidden"
              style={{
                borderColor: 'rgb(var(--border))',
                background: 'linear-gradient(135deg, rgb(var(--accent))/5, transparent)',
              }}
            >
              {/* Decorative Elements */}
              <div
                className="absolute top-0 right-0 w-64 h-64 rounded-full blur-3xl opacity-20 pointer-events-none"
                style={{ background: 'radial-gradient(circle, rgb(var(--accent)) 0%, transparent 70%)' }}
              />

              <div className="relative">
                <div className="flex items-start justify-between gap-4 mb-6">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-4 flex-wrap">
                      <h1
                        className="text-3xl md:text-4xl font-bold"
                        style={{ color: 'rgb(var(--text-primary))' }}
                      >
                        {vacancy.title}
                      </h1>
                      {vacancy.is_remote && (
                        <Badge
                          className="border"
                          style={{
                            background: 'linear-gradient(135deg, rgb(var(--accent))/25, rgb(var(--accent))/10)',
                            borderColor: 'rgb(var(--accent)/0.4)',
                            color: 'rgb(var(--accent))',
                          }}
                        >
                          🏠 Remote
                        </Badge>
                      )}
                      {vacancy.internship && (
                        <Badge
                          className="border"
                          style={{
                            background: 'linear-gradient(135deg, rgb(34, 197, 94)/25, rgb(34, 197, 94)/10)',
                            borderColor: 'rgb(34, 197, 94)/0.4)',
                            color: 'rgb(34, 197, 94)',
                          }}
                        >
                          🎓 Стажировка
                        </Badge>
                      )}
                      {vacancy.is_active && (
                        <Badge
                          className="border"
                          style={{
                            background: 'linear-gradient(135deg, rgb(34, 197, 94)/25, rgb(34, 197, 94)/10)',
                            borderColor: 'rgb(34, 197, 94)/0.4)',
                            color: 'rgb(34, 197, 94)',
                          }}
                        >
                          <CheckCircle className="h-3 w-3 mr-1" />
                          Активна
                        </Badge>
                      )}
                    </div>

                    <div className="flex items-center gap-3 flex-wrap" style={{ color: 'rgb(var(--text-muted))' }}>
                      <div className="flex items-center gap-2">
                        <Building className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
                        <span className="font-medium">
                          {vacancy.company?.name || 'Компания не указана'}
                        </span>
                      </div>
                      {vacancy.source && (
                        <>
                          <span className="text-[rgb(var(--border))]">•</span>
                          <div className="flex items-center gap-2">
                            <Globe className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
                            <a
                              href={vacancy.source.source_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="hover:underline"
                              style={{ color: 'rgb(var(--accent))' }}
                            >
                              {vacancy.source.name}
                            </a>
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                {/* Key Info Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div
                    className="group p-5 rounded-xl transition-all duration-300 hover:scale-105 hover:shadow-lg"
                    style={{
                      background: 'linear-gradient(135deg, rgb(var(--accent))/10, rgb(var(--accent))/5)',
                      border: '1px solid rgb(var(--accent)/0.2)',
                    }}
                  >
                    <div className="flex items-center gap-3 mb-2">
                      <div
                        className="p-2 rounded-lg"
                        style={{ backgroundColor: 'rgb(var(--accent)/0.1)' }}
                      >
                        <DollarSign className="h-6 w-6" style={{ color: 'rgb(var(--accent))' }} />
                      </div>
                      <span className="text-sm font-medium" style={{ color: 'rgb(var(--text-muted))' }}>
                        Зарплата
                      </span>
                    </div>
                    <div className="text-xl font-bold" style={{ color: 'rgb(var(--accent))' }}>
                      {formatSalary(vacancy.salary_from, vacancy.salary_to, vacancy.currency)}
                    </div>
                    {vacancy.currency && (
                      <div className="text-xs mt-1" style={{ color: 'rgb(var(--text-muted))' }}>
                        {vacancy.currency.name} {vacancy.currency.symbol && `(${vacancy.currency.symbol})`}
                      </div>
                    )}
                  </div>

                  <div
                    className="group p-5 rounded-xl transition-all duration-300 hover:scale-105 hover:shadow-lg"
                    style={{ backgroundColor: 'rgb(var(--bg-header-muted)/0.5)' }}
                  >
                    <div className="flex items-center gap-3 mb-2">
                      <div
                        className="p-2 rounded-lg"
                        style={{ backgroundColor: 'rgb(var(--accent)/0.1)' }}
                      >
                        <MapPin className="h-6 w-6" style={{ color: 'rgb(var(--accent))' }} />
                      </div>
                      <span className="text-sm font-medium" style={{ color: 'rgb(var(--text-muted))' }}>
                        Локация
                      </span>
                    </div>
                    <div className="text-lg font-semibold" style={{ color: 'rgb(var(--text-primary))' }}>
                      {vacancy.location?.name || 'Не указана'}
                    </div>
                    {vacancy.location?.country_id && (
                      <div className="text-xs mt-1" style={{ color: 'rgb(var(--text-muted))' }}>
                        Страна ID: {vacancy.location.country_id}
                      </div>
                    )}
                  </div>

                  <div
                    className="group p-5 rounded-xl transition-all duration-300 hover:scale-105 hover:shadow-lg"
                    style={{ backgroundColor: 'rgb(var(--bg-header-muted)/0.5)' }}
                  >
                    <div className="flex items-center gap-3 mb-2">
                      <div
                        className="p-2 rounded-lg"
                        style={{ backgroundColor: 'rgb(var(--accent)/0.1)' }}
                      >
                        <Calendar className="h-6 w-6" style={{ color: 'rgb(var(--accent))' }} />
                      </div>
                      <span className="text-sm font-medium" style={{ color: 'rgb(var(--text-muted))' }}>
                        Опубликовано
                      </span>
                    </div>
                    <div className="text-lg font-semibold" style={{ color: 'rgb(var(--text-primary))' }}>
                      {timeAgo(vacancy.created_at_source || vacancy.published_at)}
                    </div>
                    <div className="text-xs mt-1" style={{ color: 'rgb(var(--text-muted))' }}>
                      {formatDate(vacancy.created_at_source || vacancy.published_at)}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Main Content */}
            <div className="p-8">
              {/* Details Grid */}
              {(vacancy.experience || vacancy.employment || vacancy.schedule) && (
                <div className="mb-8">
                  <h2
                    className="text-xl font-semibold mb-4 flex items-center gap-2"
                    style={{ color: 'rgb(var(--text-primary))' }}
                  >
                    <Briefcase className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
                    Условия работы
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {vacancy.experience && (
                      <div
                        className="flex items-center gap-3 p-4 rounded-xl"
                        style={{ backgroundColor: 'rgb(var(--bg-header-muted)/0.5)' }}
                      >
                        <div
                          className="p-2 rounded-lg"
                          style={{ backgroundColor: 'rgb(var(--accent)/0.1)' }}
                        >
                          <TrendingUp className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
                        </div>
                        <div>
                          <div className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                            Опыт работы
                          </div>
                          <div className="font-semibold" style={{ color: 'rgb(var(--text-primary))' }}>
                            {vacancy.experience}
                          </div>
                        </div>
                      </div>
                    )}
                    {vacancy.employment && (
                      <div
                        className="flex items-center gap-3 p-4 rounded-xl"
                        style={{ backgroundColor: 'rgb(var(--bg-header-muted)/0.5)' }}
                      >
                        <div
                          className="p-2 rounded-lg"
                          style={{ backgroundColor: 'rgb(var(--accent)/0.1)' }}
                        >
                          <Users className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
                        </div>
                        <div>
                          <div className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                            Занятость
                          </div>
                          <div className="font-semibold" style={{ color: 'rgb(var(--text-primary))' }}>
                            {vacancy.employment}
                          </div>
                        </div>
                      </div>
                    )}
                    {vacancy.schedule && (
                      <div
                        className="flex items-center gap-3 p-4 rounded-xl"
                        style={{ backgroundColor: 'rgb(var(--bg-header-muted)/0.5)' }}
                      >
                        <div
                          className="p-2 rounded-lg"
                          style={{ backgroundColor: 'rgb(var(--accent)/0.1)' }}
                        >
                          <Clock className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
                        </div>
                        <div>
                          <div className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                            График
                          </div>
                          <div className="font-semibold" style={{ color: 'rgb(var(--text-primary))' }}>
                            {vacancy.schedule}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Description */}
              {vacancy.description && (
                <div className="mb-8">
                  <h2
                    className="text-xl font-semibold mb-4"
                    style={{ color: 'rgb(var(--text-primary))' }}
                  >
                    Описание вакансии
                  </h2>
                  <div
                    className="p-6 rounded-xl leading-relaxed"
                    style={{
                      backgroundColor: 'rgb(var(--bg-header-muted)/0.5)',
                      color: 'rgb(var(--text-muted))',
                    }}
                  >
                    <p className="whitespace-pre-wrap">{vacancy.description}</p>
                  </div>
                </div>
              )}

              {/* Skills */}
              {vacancy.skills && vacancy.skills.length > 0 && (
                <div className="mb-8">
                  <h2
                    className="text-xl font-semibold mb-4"
                    style={{ color: 'rgb(var(--text-primary))' }}
                  >
                    Ключевые навыки
                  </h2>
                  <div className="flex flex-wrap gap-2">
                    {vacancy.skills.map((skill, index) => (
                      <Badge
                        key={skill.id}
                        className="text-sm px-4 py-2 transition-all duration-300 hover:scale-105 hover:shadow-md animate-fade-in"
                        style={{
                          animationDelay: `${index * 50}ms`,
                          background: 'linear-gradient(135deg, rgb(var(--accent)/0.15), rgb(var(--accent)/0.05))',
                          border: '1px solid rgb(var(--accent)/0.3)',
                          color: 'rgb(var(--text-primary))',
                        }}
                      >
                        {skill.name}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              <Separator className="my-8" style={{ backgroundColor: 'rgb(var(--border))' }} />

              {/* Additional Info */}
              <div className="mb-8">
                <h2
                  className="text-xl font-semibold mb-4"
                  style={{ color: 'rgb(var(--text-primary))' }}
                >
                  Дополнительная информация
                </h2>
                <div
                  className="p-6 rounded-xl space-y-3"
                  style={{ backgroundColor: 'rgb(var(--bg-header-muted)/0.5)' }}
                >
                  <div className="flex items-center gap-3">
                    <Calendar className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
                    <span className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                      Создано:{' '}
                      <span className="font-medium" style={{ color: 'rgb(var(--text-primary))' }}>
                        {formatDate(vacancy.created_at_source)}
                      </span>
                    </span>
                  </div>
                  {vacancy.last_seen_at && (
                    <div className="flex items-center gap-3">
                      <CheckCircle className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
                      <span className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                        Последняя активность:{' '}
                        <span className="font-medium" style={{ color: 'rgb(var(--text-primary))' }}>
                          {timeAgo(vacancy.last_seen_at)}
                        </span>
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-4">
                {vacancy.vacancy_url ? (
                  <Button
                    size="lg"
                    className="flex-1 text-white h-14 text-lg transition-all duration-300 hover:scale-105 hover:shadow-xl hover:shadow-[rgb(var(--accent))/20]"
                    style={{
                      background: 'linear-gradient(135deg, rgb(var(--button-from)), rgb(var(--button-to)))',
                    }}
                    asChild
                  >
                    <a href={vacancy.vacancy_url} target="_blank" rel="noopener noreferrer">
                      <ExternalLink className="h-5 w-5 mr-2" />
                      Откликнуться на вакансию
                    </a>
                  </Button>
                ) : (
                  <Button
                    size="lg"
                    className="flex-1 text-white h-14 text-lg transition-all duration-300 hover:scale-105 hover:shadow-xl hover:shadow-[rgb(var(--accent))/20]"
                    style={{
                      background: 'linear-gradient(135deg, rgb(var(--button-from)), rgb(var(--button-to)))',
                    }}
                    onClick={() => notification.info('В разработке', 'Функция отклика будет доступна soon')}
                  >
                    Откликнуться
                  </Button>
                )}
                <Button
                  size="lg"
                  variant="outline"
                  className="flex-1 h-14 text-lg transition-all duration-300 hover:scale-105"
                  style={{
                    borderColor: 'rgb(var(--border))',
                    color: 'rgb(var(--text-primary))',
                  }}
                  onClick={() => navigate('/vacancies')}
                >
                  Другие вакансии
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
