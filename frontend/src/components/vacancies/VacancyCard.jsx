import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Building,
  MapPin,
  DollarSign,
  Clock,
  ExternalLink,
  Bookmark,
  BookmarkCheck,
  Globe,
  Briefcase,
  Calendar,
  Loader2,
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/utils/AuthContext';
import BookmarkService from '@/api/services/BookmarkService';
import useNotification from '@/hooks/useNotification';

export default function VacancyCard({
  vacancy,
  isBookmarked: initialBookmarked = false,
  onBookmarkChange,
}) {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const notification = useNotification();
  const [isBookmarked, setIsBookmarked] = useState(initialBookmarked);
  const [bookmarkLoading, setBookmarkLoading] = useState(false);

  const formatSalary = (from, to, currency) => {
    const parts = [];
    if (from) parts.push(from.toLocaleString());
    if (to) parts.push(to.toLocaleString());

    if (parts.length === 0) return 'По договорённости';

    const symbol = currency?.symbol || '₽';
    return `${symbol} ${parts.join(' - ')}`;
  };

  const timeAgo = (dateString) => {
    if (!dateString) return 'Не указано';

    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);

    if (diffInSeconds < 60) return 'Только что';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} мин назад`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} ч назад`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)} дн назад`;

    return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' });
  };

  const getLocationText = () => {
    if (!vacancy.location) return 'Локация не указана';
    return vacancy.location.name;
  };

  const getCompanyText = () => {
    if (!vacancy.company) return 'Компания не указана';
    return vacancy.company.name;
  };

  const handleCardClick = (e) => {
    if (e.target.closest('button') || e.target.closest('a')) {
      return;
    }
    navigate(`/vacancies/${vacancy.id}`);
  };

  const handleBookmarkClick = async (e) => {
    e.stopPropagation();

    if (!isAuthenticated) {
      notification.info('Требуется авторизация', 'Войдите, чтобы сохранять вакансии');
      navigate('/login');
      return;
    }

    setBookmarkLoading(true);
    try {
      const result = await BookmarkService.toggleBookmark(vacancy.id);
      setIsBookmarked(result.bookmarked);

      if (result.bookmarked) {
        notification.success('Добавлено в закладки', vacancy.title);
      } else {
        notification.info('Удалено из закладок', vacancy.title);
      }

      if (onBookmarkChange) {
        onBookmarkChange(vacancy.id, result.bookmarked);
      }
    } catch {
      notification.error('Ошибка', 'Не удалось изменить закладку');
    } finally {
      setBookmarkLoading(false);
    }
  };

  return (
    <div
      onClick={handleCardClick}
      className="group relative backdrop-blur-sm border rounded-2xl overflow-hidden transition-all duration-500 hover:shadow-2xl hover:shadow-[rgb(var(--accent))/10] hover:border-[rgb(var(--accent))/30] hover:-translate-y-1 cursor-pointer"
      style={{
        backgroundColor: 'rgb(var(--bg-header-muted)/0.4)',
        borderColor: 'rgb(var(--border)/0.5)',
      }}
    >
      <div
        className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none rounded-2xl"
        style={{
          background:
            'linear-gradient(135deg, rgb(var(--accent))/15, transparent 40%, transparent 60%, rgb(var(--accent))/10)',
        }}
      />

      <div className="relative p-6 md:p-8">
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4 mb-6">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-3 flex-wrap">
              <h3
                className="text-xl md:text-2xl font-bold transition-all duration-300 group-hover:text-[rgb(var(--accent))]"
                style={{ color: 'rgb(var(--text-primary))' }}
              >
                {vacancy.title}
              </h3>
              {vacancy.is_remote && (
                <Badge
                  className="border shrink-0 animate-fade-in"
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
                  className="border shrink-0 animate-fade-in"
                  style={{
                    background: 'linear-gradient(135deg, rgb(34, 197, 94)/25, rgb(34, 197, 94)/10)',
                    borderColor: 'rgb(34, 197, 94)/0.4)',
                    color: 'rgb(34, 197, 94)',
                  }}
                >
                  🎓 Стажировка
                </Badge>
              )}
            </div>

            <div
              className="flex items-center gap-2 flex-wrap"
              style={{ color: 'rgb(var(--text-muted))' }}
            >
              <Building className="h-4 w-4" style={{ color: 'rgb(var(--accent))' }} />
              <span className="font-medium">{getCompanyText()}</span>
              {vacancy.source && (
                <>
                  <span className="text-[rgb(var(--border))]">•</span>
                  <Globe className="h-4 w-4" style={{ color: 'rgb(var(--accent))' }} />
                  <span>{vacancy.source.name}</span>
                </>
              )}
            </div>
          </div>

          <div
            className="md:text-right px-4 py-3 rounded-xl shrink-0"
            style={{
              background: 'linear-gradient(135deg, rgb(var(--accent))/10, rgb(var(--accent))/5)',
              border: '1px solid rgb(var(--accent)/0.2)',
            }}
          >
            <div className="flex items-center md:justify-end gap-2 mb-1">
              <DollarSign className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
              <span
                className="text-lg md:text-xl font-bold"
                style={{ color: 'rgb(var(--accent))' }}
              >
                {formatSalary(vacancy.salary_from, vacancy.salary_to, vacancy.currency)}
              </span>
            </div>
            {vacancy.currency && (
              <div className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                {vacancy.currency.name}
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div
            className="flex items-center gap-3 p-3 rounded-xl transition-all duration-300 hover:scale-105"
            style={{ backgroundColor: 'rgb(var(--bg-header-muted)/0.5)' }}
          >
            <div className="p-2 rounded-lg" style={{ backgroundColor: 'rgb(var(--accent)/0.1)' }}>
              <MapPin className="h-4 w-4" style={{ color: 'rgb(var(--accent))' }} />
            </div>
            <div className="min-w-0">
              <div className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                Город
              </div>
              <div
                className="text-sm font-medium truncate"
                style={{ color: 'rgb(var(--text-primary))' }}
              >
                {getLocationText()}
              </div>
            </div>
          </div>

          {vacancy.experience && (
            <div
              className="flex items-center gap-3 p-3 rounded-xl transition-all duration-300 hover:scale-105"
              style={{ backgroundColor: 'rgb(var(--bg-header-muted)/0.5)' }}
            >
              <div className="p-2 rounded-lg" style={{ backgroundColor: 'rgb(var(--accent)/0.1)' }}>
                <Briefcase className="h-4 w-4" style={{ color: 'rgb(var(--accent))' }} />
              </div>
              <div className="min-w-0">
                <div className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                  Опыт
                </div>
                <div
                  className="text-sm font-medium truncate"
                  style={{ color: 'rgb(var(--text-primary))' }}
                >
                  {vacancy.experience}
                </div>
              </div>
            </div>
          )}

          {vacancy.employment && (
            <div
              className="flex items-center gap-3 p-3 rounded-xl transition-all duration-300 hover:scale-105"
              style={{ backgroundColor: 'rgb(var(--bg-header-muted)/0.5)' }}
            >
              <div className="p-2 rounded-lg" style={{ backgroundColor: 'rgb(var(--accent)/0.1)' }}>
                <Briefcase className="h-4 w-4" style={{ color: 'rgb(var(--accent))' }} />
              </div>
              <div className="min-w-0">
                <div className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                  Занятость
                </div>
                <div
                  className="text-sm font-medium truncate"
                  style={{ color: 'rgb(var(--text-primary))' }}
                >
                  {vacancy.employment}
                </div>
              </div>
            </div>
          )}

          <div
            className="flex items-center gap-3 p-3 rounded-xl transition-all duration-300 hover:scale-105"
            style={{ backgroundColor: 'rgb(var(--bg-header-muted)/0.5)' }}
          >
            <div className="p-2 rounded-lg" style={{ backgroundColor: 'rgb(var(--accent)/0.1)' }}>
              <Clock className="h-4 w-4" style={{ color: 'rgb(var(--accent))' }} />
            </div>
            <div className="min-w-0">
              <div className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                Опубликовано
              </div>
              <div className="text-sm font-medium" style={{ color: 'rgb(var(--text-primary))' }}>
                {timeAgo(vacancy.created_at_source || vacancy.published_at)}
              </div>
            </div>
          </div>
        </div>

        {vacancy.skills && vacancy.skills.length > 0 && (
          <div className="mb-6">
            <div className="text-xs mb-3" style={{ color: 'rgb(var(--text-muted))' }}>
              Ключевые навыки
            </div>
            <div className="flex flex-wrap gap-2">
              {vacancy.skills.slice(0, 8).map((skill) => (
                <Badge
                  key={skill.id}
                  variant="outline"
                  className="text-xs transition-all duration-300 hover:scale-105 hover:shadow-md"
                  style={{
                    borderColor: 'rgb(var(--border))',
                    color: 'rgb(var(--text-primary))',
                    backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
                  }}
                >
                  {skill.name}
                </Badge>
              ))}
              {vacancy.skills.length > 8 && (
                <Badge
                  variant="outline"
                  className="text-xs"
                  style={{
                    borderColor: 'rgb(var(--border))',
                    color: 'rgb(var(--accent))',
                  }}
                >
                  +{vacancy.skills.length - 8}
                </Badge>
              )}
            </div>
          </div>
        )}

        <div className="flex items-center justify-between gap-4 pt-4">
          <div
            className="flex items-center gap-2 text-xs"
            style={{ color: 'rgb(var(--text-muted))' }}
          >
            <Calendar className="h-3 w-3" />
            <span>Обновлено {timeAgo(vacancy.last_seen_at || vacancy.updated_at)}</span>
          </div>

          <div className="flex gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={handleBookmarkClick}
              disabled={bookmarkLoading}
              className="transition-all duration-300 hover:scale-105"
              style={{
                borderColor: isBookmarked ? 'rgb(var(--accent))' : 'rgb(var(--border))',
                color: isBookmarked ? 'rgb(var(--accent))' : 'rgb(var(--text-primary))',
                backgroundColor: isBookmarked ? 'rgb(var(--accent)/0.1)' : 'transparent',
              }}
            >
              {bookmarkLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : isBookmarked ? (
                <>
                  <BookmarkCheck className="h-4 w-4 mr-1" />
                  Сохранено
                </>
              ) : (
                <>
                  <Bookmark className="h-4 w-4 mr-1" />
                  Сохранить
                </>
              )}
            </Button>
            {vacancy.vacancy_url && (
              <Button
                size="sm"
                className="text-white transition-all duration-300 hover:scale-105 hover:shadow-lg hover:shadow-[rgb(var(--accent))/20]"
                style={{
                  background:
                    'linear-gradient(135deg, rgb(var(--button-from)), rgb(var(--button-to)))',
                }}
                asChild
              >
                <a
                  href={vacancy.vacancy_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={(e) => e.stopPropagation()}
                >
                  <ExternalLink className="h-4 w-4 mr-1" />
                  Откликнуться
                </a>
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
