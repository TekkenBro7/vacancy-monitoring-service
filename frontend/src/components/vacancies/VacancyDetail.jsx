import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import DOMPurify from 'dompurify';
import {
  ArrowLeft,
  Building,
  MapPin,
  Clock,
  ExternalLink,
  Bookmark,
  BookmarkCheck,
  Share2,
  Calendar,
  Globe,
  Briefcase,
  TrendingUp,
  Users,
  CheckCircle,
  Sparkles,
  Loader2,
  Edit2,
  Trash2,
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import VacancyService from '@/api/services/VacancyService';
import BookmarkService from '@/api/services/BookmarkService';
import VacancyComments from './VacancyComments';
import { useAuth } from '@/utils/AuthContext';
import useNotification from '@/hooks/useNotification';
import { GitCompare } from 'lucide-react';
import AddToComparisonModal from '@/components/comparisons/AddToComparisonModal';
import VacancyEditModal from './VacancyEditModal';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';

export default function VacancyDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const notification = useNotification();
  const { isAuthenticated, user } = useAuth();
  const isAdmin = user?.role_name === 'admin';

  const [vacancy, setVacancy] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [bookmarkLoading, setBookmarkLoading] = useState(false);

  const [comparisonModalOpen, setComparisonModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const loadVacancy = useCallback(async () => {
    try {
      setLoading(true);
      const data = await VacancyService.getVacancyById(id);
      setVacancy(data);

      if (data.last_enriched_at) {
        const enrichedRecently = new Date(data.last_enriched_at) > new Date(Date.now() - 60000);
        if (enrichedRecently && data.source?.name?.toLowerCase().includes('headhunter')) {
          notification.success('Данные обновлены', 'Описание и навыки дополнены из HeadHunter');
        }
      }
    } catch {
      notification.error('Ошибка', 'Не удалось загрузить вакансию');
    } finally {
      setLoading(false);
    }
  }, [id, notification]);

  const handleDeleteVacancy = async () => {
    setDeleting(true);
    try {
      await VacancyService.deleteVacancy(vacancy.id);
      notification.success('Удалено', 'Вакансия успешно удалена');
      navigate('/vacancies');
    } catch (err) {
      notification.error('Ошибка', err.response?.data?.detail || 'Не удалось удалить вакансию');
    } finally {
      setDeleting(false);
    }
  };

  const checkBookmarkStatus = useCallback(async () => {
    try {
      const result = await BookmarkService.checkBookmark(id);
      setIsBookmarked(result);
    } catch {
      console.error('Error checking bookmark:');
    }
  }, [id]);

  useEffect(() => {
    loadVacancy();
    if (isAuthenticated) {
      checkBookmarkStatus();
    }
  }, [id, isAuthenticated, loadVacancy, checkBookmarkStatus]);

  const handleBookmark = async () => {
    if (!isAuthenticated) {
      notification.info('Требуется авторизация', 'Войдите, чтобы сохранять вакансии');
      navigate('/login');
      return;
    }

    setBookmarkLoading(true);
    try {
      const result = await BookmarkService.toggleBookmark(id);
      setIsBookmarked(result.bookmarked);

      if (result.bookmarked) {
        notification.success('Добавлено в закладки', vacancy?.title);
      } else {
        notification.info('Удалено из закладок', vacancy?.title);
      }
    } catch {
      notification.error('Ошибка', 'Не удалось изменить закладку');
    } finally {
      setBookmarkLoading(false);
    }
  };

  const formatSalary = (from, to, currency) => {
    const symbol = currency?.symbol || 'Ю';

    if (!from && !to) {
      return '$ По договоренности';
    }

    if (from && !to) {
      return `от ${from.toLocaleString()} ${symbol}`;
    }

    if (!from && to) {
      return `до ${to.toLocaleString()} ${symbol}`;
    }

    return `${from.toLocaleString()} - ${to.toLocaleString()} ${symbol}`;
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
    const url = vacancy?.vacancy_url;

    if (navigator.share) {
      navigator.share({
        title: vacancy?.title,
        text: `Вакансия: ${vacancy?.title}\n${url}`,
        url: url,
      });
    } else {
      navigator.clipboard.writeText(url);
      notification.success('Ссылка скопирована', 'URL вакансии в буфере обмена');
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-6 py-8">
        <div className="max-w-5xl mx-auto">
          <div
            className="h-10 w-64 mb-6 animate-pulse rounded"
            style={{ backgroundColor: 'rgb(var(--bg-header-muted)/0.5)' }}
          />
          <div
            className="h-96 rounded-2xl animate-pulse"
            style={{ backgroundColor: 'rgb(var(--bg-header-muted)/0.3)' }}
          />
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
            <ArrowLeft className="h-4 w-4 mr-2" />К списку вакансий
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-8 animate-fade-in">
      <div className="container mx-auto px-6">
        <div className="max-w-5xl mx-auto">
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
                disabled={bookmarkLoading}
                className="transition-all duration-300 hover:scale-105"
                style={{
                  borderColor: isBookmarked ? 'rgb(var(--accent))' : 'rgb(var(--border))',
                  color: isBookmarked ? 'rgb(var(--accent))' : 'rgb(var(--text-primary))',
                  backgroundColor: isBookmarked ? 'rgb(var(--accent)/0.1)' : 'transparent',
                }}
              >
                {bookmarkLoading ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : isBookmarked ? (
                  <BookmarkCheck className="h-4 w-4 mr-2" />
                ) : (
                  <Bookmark className="h-4 w-4 mr-2" />
                )}
                {isBookmarked ? 'Сохранено' : 'Сохранить'}
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  if (!isAuthenticated) {
                    notification.info(
                      'Требуется авторизация',
                      'Войдите, чтобы сравнивать вакансии'
                    );
                    navigate('/login');
                    return;
                  }
                  setComparisonModalOpen(true);
                }}
                className="transition-all duration-300 hover:scale-105"
                style={{
                  borderColor: 'rgb(var(--border))',
                  color: 'rgb(var(--text-primary))',
                }}
              >
                <GitCompare className="h-4 w-4 mr-2" style={{ color: 'rgb(var(--accent))' }} />
                Сравнить
              </Button>
            </div>
            {isAdmin && (
              <>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setEditModalOpen(true)}
                  className="transition-all duration-300 hover:scale-105"
                  style={{
                    borderColor: 'rgb(var(--accent))',
                    color: 'rgb(var(--accent))',
                    backgroundColor: 'rgb(var(--accent)/0.05)',
                  }}
                >
                  <Edit2 className="h-4 w-4 mr-2" />
                  Редактировать
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setDeleteModalOpen(true)}
                  className="transition-all duration-300 hover:scale-105 border-red-500/50 text-red-500 hover:bg-red-500/10"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Удалить
                </Button>
              </>
            )}
          </div>

          <div
            className="rounded-2xl backdrop-blur-sm border shadow-xl overflow-hidden animate-fade-in-up"
            style={{
              backgroundColor: 'rgb(var(--bg-header-muted)/0.4)',
              borderColor: 'rgb(var(--border)/0.5)',
            }}
          >
            <div
              className="relative p-8 border-b overflow-hidden"
              style={{
                borderColor: 'rgb(var(--border))',
                background: 'linear-gradient(135deg, rgb(var(--accent))/5, transparent)',
              }}
            >
              <div
                className="absolute top-0 right-0 w-64 h-64 rounded-full blur-3xl opacity-20 pointer-events-none"
                style={{
                  background: 'radial-gradient(circle, rgb(var(--accent)) 0%, transparent 70%)',
                }}
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
                            background:
                              'linear-gradient(135deg, rgb(var(--accent))/25, rgb(var(--accent))/10)',
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
                            background:
                              'linear-gradient(135deg, rgb(34, 197, 94)/25, rgb(34, 197, 94)/10)',
                            borderColor: 'rgb(34, 197, 94)/0.4)',
                            color: 'rgb(34, 197, 94)',
                          }}
                        >
                          🎓 Стажировка
                        </Badge>
                      )}
                      {vacancy.is_active ? (
                        <Badge
                          className="border"
                          style={{
                            background:
                              'linear-gradient(135deg, rgb(34, 197, 94)/25, rgb(34, 197, 94)/10)',
                            borderColor: 'rgb(34, 197, 94)/0.4)',
                            color: 'rgb(34, 197, 94)',
                          }}
                        >
                          <CheckCircle className="h-3 w-3 mr-1" />
                          Активна
                        </Badge>
                      ) : (
                        <Badge
                          className="border"
                          style={{
                            background:
                              'linear-gradient(135deg, rgb(239, 68, 68)/25, rgb(239, 68, 68)/10)',
                            borderColor: 'rgb(239, 68, 68)/0.4)',
                            color: 'rgb(239, 68, 68)',
                          }}
                        >
                          <Clock className="h-3 w-3 mr-1" />
                          Неактивна
                        </Badge>
                      )}
                    </div>

                    <div
                      className="flex items-center gap-3 flex-wrap"
                      style={{ color: 'rgb(var(--text-muted))' }}
                    >
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

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div
                    className="group p-5 rounded-xl transition-all duration-300 hover:scale-105 hover:shadow-lg"
                    style={{
                      background:
                        'linear-gradient(135deg, rgb(var(--accent))/10, rgb(var(--accent))/5)',
                      border: '1px solid rgb(var(--accent)/0.2)',
                    }}
                  >
                    <div className="flex items-center gap-3 mb-2">
                      <span
                        className="text-sm font-medium"
                        style={{ color: 'rgb(var(--text-muted))' }}
                      >
                        Зарплата
                      </span>
                    </div>
                    <div className="text-xl font-bold" style={{ color: 'rgb(var(--accent))' }}>
                      {formatSalary(vacancy.salary_from, vacancy.salary_to, vacancy.currency)}
                    </div>
                    {vacancy.currency && (
                      <div className="text-xs mt-1" style={{ color: 'rgb(var(--text-muted))' }}>
                        {vacancy.currency.name}{' '}
                        {vacancy.currency.symbol && `(${vacancy.currency.symbol})`}
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
                      <span
                        className="text-sm font-medium"
                        style={{ color: 'rgb(var(--text-muted))' }}
                      >
                        Локация
                      </span>
                    </div>
                    <div
                      className="text-lg font-semibold"
                      style={{ color: 'rgb(var(--text-primary))' }}
                    >
                      {vacancy.location?.name || vacancy.address || 'Не указана'}
                    </div>
                    {vacancy.address &&
                      vacancy.location?.name &&
                      vacancy.address !== vacancy.location.name && (
                        <div className="text-sm mt-1" style={{ color: 'rgb(var(--text-muted))' }}>
                          {vacancy.address}
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
                      <span
                        className="text-sm font-medium"
                        style={{ color: 'rgb(var(--text-muted))' }}
                      >
                        Опубликовано
                      </span>
                    </div>
                    <div
                      className="text-lg font-semibold"
                      style={{ color: 'rgb(var(--text-primary))' }}
                    >
                      {timeAgo(vacancy.published_at || vacancy.created_at_source)}
                    </div>
                    <div className="text-xs mt-1" style={{ color: 'rgb(var(--text-muted))' }}>
                      {formatDate(vacancy.published_at || vacancy.created_at_source)}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="p-8">
              {vacancy.last_enriched_at &&
                vacancy.source?.name?.toLowerCase().includes('headhunter') && (
                  <div
                    className="mb-6 p-4 rounded-xl border flex items-center justify-between"
                    style={{
                      background:
                        'linear-gradient(135deg, rgb(var(--accent)/10), rgb(var(--accent)/5))',
                      borderColor: 'rgb(var(--accent)/0.3)',
                    }}
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className="p-2 rounded-lg"
                        style={{ backgroundColor: 'rgb(var(--accent)/0.1)' }}
                      >
                        <Sparkles className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
                      </div>
                    </div>
                  </div>
                )}

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
                          <div
                            className="font-semibold"
                            style={{ color: 'rgb(var(--text-primary))' }}
                          >
                            {vacancy.experience}
                          </div>
                        </div>
                      </div>
                    )}
                    {vacancy.education && (
                      <div
                        className="flex items-center gap-3 p-4 rounded-xl"
                        style={{ backgroundColor: 'rgb(var(--bg-header-muted)/0.5)' }}
                      >
                        <div
                          className="p-2 rounded-lg"
                          style={{ backgroundColor: 'rgb(var(--accent)/0.1)' }}
                        >
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-5 w-5"
                            style={{ color: 'rgb(var(--accent))' }}
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          >
                            <path d="M22 10v6M2 10l10-5 10 5-10 5z" />
                            <path d="M6 12v5c3 3 9 3 12 0v-5" />
                          </svg>
                        </div>
                        <div>
                          <div className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                            Образование
                          </div>
                          <div
                            className="font-semibold"
                            style={{ color: 'rgb(var(--text-primary))' }}
                          >
                            {vacancy.education}
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
                          <div
                            className="font-semibold"
                            style={{ color: 'rgb(var(--text-primary))' }}
                          >
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
                          <div
                            className="font-semibold"
                            style={{ color: 'rgb(var(--text-primary))' }}
                          >
                            {vacancy.schedule}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {vacancy.description && (
                <div className="mb-8">
                  <h2
                    className="text-xl font-semibold mb-4"
                    style={{ color: 'rgb(var(--text-primary))' }}
                  >
                    Описание вакансии
                  </h2>
                  <div
                    className="prose max-w-none p-6 rounded-xl hh-description"
                    style={{
                      backgroundColor: 'rgb(var(--bg-header-muted)/0.5)',
                      color: 'rgb(var(--text-muted))',
                    }}
                    dangerouslySetInnerHTML={{
                      __html: DOMPurify.sanitize(vacancy.description),
                    }}
                  />
                </div>
              )}

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
                        key={skill.id || index}
                        className="text-sm px-4 py-2 transition-all duration-300 hover:scale-105 hover:shadow-md animate-fade-in"
                        style={{
                          animationDelay: `${index * 50}ms`,
                          background:
                            'linear-gradient(135deg, rgb(var(--accent)/0.15), rgb(var(--accent)/0.05))',
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
                        {formatDate(vacancy.created_at)}
                      </span>
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <Clock className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
                    <span className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                      Обновлено:{' '}
                      <span className="font-medium" style={{ color: 'rgb(var(--text-primary))' }}>
                        {formatDate(vacancy.updated_at)}
                      </span>
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-4">
                {vacancy.vacancy_url ? (
                  <Button
                    size="lg"
                    className="flex-1 text-white h-14 text-lg transition-all duration-300 hover:scale-105 hover:shadow-xl hover:shadow-[rgb(var(--accent))/20]"
                    style={{
                      background:
                        'linear-gradient(135deg, rgb(var(--button-from)), rgb(var(--button-to)))',
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
                      background:
                        'linear-gradient(135deg, rgb(var(--button-from)), rgb(var(--button-to)))',
                    }}
                    onClick={() =>
                      notification.info('В разработке', 'Функция отклика будет доступна скоро')
                    }
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
          <VacancyComments vacancyId={parseInt(id)} />
        </div>
      </div>

      <AddToComparisonModal
        isOpen={comparisonModalOpen}
        onClose={() => setComparisonModalOpen(false)}
        vacancy={vacancy}
        onSuccess={() => {
          notification.success('Готово', 'Вакансия добавлена в сравнение');
        }}
      />

      {isAdmin && vacancy && (
        <VacancyEditModal
          isOpen={editModalOpen}
          onClose={() => setEditModalOpen(false)}
          vacancy={vacancy}
          onSuccess={() => {
            setEditModalOpen(false);
            loadVacancy();
            notification.success('Успешно', 'Вакансия обновлена');
          }}
        />
      )}

      <Dialog open={deleteModalOpen} onOpenChange={setDeleteModalOpen}>
        <DialogContent
          style={{
            backgroundColor: 'rgb(var(--bg-header))',
            borderColor: 'rgb(var(--border))',
          }}
        >
          <DialogHeader>
            <DialogTitle style={{ color: 'rgb(var(--text-primary))' }}>
              Удалить вакансию
            </DialogTitle>
          </DialogHeader>
          <div className="py-4">
            <p style={{ color: 'rgb(var(--text-muted))' }}>
              Вы уверены, что хотите удалить вакансию{' '}
              <span className="font-semibold" style={{ color: 'rgb(var(--text-primary))' }}>
                «{vacancy?.title}»
              </span>
              ? Это действие нельзя отменить.
            </p>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeleteModalOpen(false)}
              disabled={deleting}
              style={{
                borderColor: 'rgb(var(--border))',
                color: 'rgb(var(--text-primary))',
                backgroundColor: 'rgb(var(--bg-header-muted))',
              }}
            >
              Отмена
            </Button>
            <Button
              onClick={handleDeleteVacancy}
              disabled={deleting}
              className="text-white bg-red-500 hover:bg-red-600"
            >
              {deleting ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Удаление...
                </span>
              ) : (
                'Удалить'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
