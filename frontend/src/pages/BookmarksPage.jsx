import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bookmark, BookmarkX, Search, ArrowLeft, Loader2, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import VacancyCard from '@/components/vacancies/VacancyCard';
import BookmarkService from '@/api/services/BookmarkService';
import { useAuth } from '@/utils/AuthContext';
import useNotification from '@/hooks/useNotification';

export default function BookmarksPage() {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const notification = useNotification();

  const [bookmarks, setBookmarks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  const loadBookmarks = useCallback(async () => {
    try {
      setLoading(true);
      const data = await BookmarkService.getMyBookmarks();
      setBookmarks(data);
    } catch {
      notification.error('Ошибка', 'Не удалось загрузить закладки');
    } finally {
      setLoading(false);
    }
  }, [notification]);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      navigate('/login');
      return;
    }

    if (isAuthenticated) {
      loadBookmarks();
    }
  }, [isAuthenticated, authLoading, navigate, loadBookmarks]);

  const handleBookmarkChange = (vacancyId, isBookmarked) => {
    if (!isBookmarked) {
      setBookmarks(bookmarks.filter((b) => b.vacancy_id !== vacancyId));
    }
  };

  const filteredBookmarks = bookmarks.filter((bookmark) => {
    if (!searchQuery.trim()) return true;

    const query = searchQuery.toLowerCase();
    const vacancy = bookmark.vacancy;

    return (
      vacancy?.title?.toLowerCase().includes(query) ||
      vacancy?.company?.name?.toLowerCase().includes(query) ||
      vacancy?.location?.name?.toLowerCase().includes(query) ||
      vacancy?.skills?.some((s) => s.name.toLowerCase().includes(query))
    );
  });

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2
            className="h-12 w-12 animate-spin mx-auto mb-4"
            style={{ color: 'rgb(var(--accent))' }}
          />
          <p style={{ color: 'rgb(var(--text-muted))' }}>Загрузка закладок...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-8 animate-fade-in">
      <div className="container mx-auto px-6">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                onClick={() => navigate(-1)}
                className="h-10 w-10 p-0 rounded-full"
                style={{ color: 'rgb(var(--text-muted))' }}
              >
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <div>
                <h1
                  className="text-3xl font-bold flex items-center gap-3"
                  style={{ color: 'rgb(var(--text-primary))' }}
                >
                  <Bookmark className="h-8 w-8" style={{ color: 'rgb(var(--accent))' }} />
                  Мои закладки
                </h1>
                <p style={{ color: 'rgb(var(--text-muted))' }}>
                  {bookmarks.length}{' '}
                  {bookmarks.length === 1
                    ? 'вакансия'
                    : bookmarks.length < 5
                      ? 'вакансии'
                      : 'вакансий'}{' '}
                  сохранено
                </p>
              </div>
            </div>
          </div>

          {/* Search */}
          {bookmarks.length > 0 && (
            <div className="relative mb-8">
              <Search
                className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5"
                style={{ color: 'rgb(var(--accent))' }}
              />
              <Input
                type="search"
                placeholder="Поиск по закладкам..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-12 h-14 rounded-xl border-2 text-base"
                style={{
                  backgroundColor: 'rgb(var(--bg-header-muted))',
                  borderColor: 'rgb(var(--border))',
                  color: 'rgb(var(--text-primary))',
                }}
              />
            </div>
          )}

          {/* Empty State */}
          {bookmarks.length === 0 && (
            <div
              className="text-center py-20 rounded-2xl border"
              style={{
                backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
                borderColor: 'rgb(var(--border))',
              }}
            >
              <div
                className="w-24 h-24 mx-auto mb-6 rounded-full flex items-center justify-center"
                style={{ backgroundColor: 'rgb(var(--accent)/0.1)' }}
              >
                <BookmarkX className="h-12 w-12" style={{ color: 'rgb(var(--accent))' }} />
              </div>
              <h2 className="text-2xl font-bold mb-3" style={{ color: 'rgb(var(--text-primary))' }}>
                Закладок пока нет
              </h2>
              <p className="mb-8 max-w-md mx-auto" style={{ color: 'rgb(var(--text-muted))' }}>
                Сохраняйте интересные вакансии, чтобы вернуться к ним позже. Нажмите на кнопку
                «Сохранить» на карточке вакансии.
              </p>
              <Button
                onClick={() => navigate('/vacancies')}
                className="text-white"
                style={{
                  background:
                    'linear-gradient(135deg, rgb(var(--button-from)), rgb(var(--button-to)))',
                }}
              >
                <Sparkles className="h-4 w-4 mr-2" />
                Найти вакансии
              </Button>
            </div>
          )}

          {bookmarks.length > 0 && filteredBookmarks.length === 0 && (
            <div
              className="text-center py-16 rounded-2xl border"
              style={{
                backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
                borderColor: 'rgb(var(--border))',
              }}
            >
              <Search
                className="h-12 w-12 mx-auto mb-4"
                style={{ color: 'rgb(var(--text-muted))' }}
              />
              <h3
                className="text-xl font-semibold mb-2"
                style={{ color: 'rgb(var(--text-primary))' }}
              >
                Ничего не найдено
              </h3>
              <p style={{ color: 'rgb(var(--text-muted))' }}>
                Попробуйте изменить поисковый запрос
              </p>
            </div>
          )}

          {filteredBookmarks.length > 0 && (
            <div className="space-y-6">
              {filteredBookmarks.map((bookmark) => (
                <VacancyCard
                  key={bookmark.id}
                  vacancy={bookmark.vacancy}
                  isBookmarked={true}
                  onBookmarkChange={handleBookmarkChange}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
