import { useState, useEffect } from 'react';
import { Search, Briefcase, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import VacancyService from '@/api/services/VacancyService';
import VacancyList from '@/components/vacancies/VacancyList';
import Pagination from '@/components/vacancies/Pagination';
import useNotification from '@/hooks/useNotification';

const PAGE_SIZE = 10;

export default function VacanciesPage() {
  const notification = useNotification();
  const [vacancies, setVacancies] = useState([]);
  const [pagination, setPagination] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    loadVacancies();
  }, [currentPage]);

  const loadVacancies = async () => {
    try {
      setLoading(true);
      const data = await VacancyService.getVacancies({
        page: currentPage,
        page_size: PAGE_SIZE,
      });
      setVacancies(data.items || []);
      setPagination(data.pagination);
    } catch (error) {
      notification.error('Ошибка', 'Не удалось загрузить вакансии');
      console.error('Error loading vacancies:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const filteredVacancies = vacancies.filter((vacancy) => {
    if (!searchQuery.trim()) return true;

    const query = searchQuery.toLowerCase();
    return (
      vacancy.title?.toLowerCase().includes(query) ||
      vacancy.description?.toLowerCase().includes(query) ||
      vacancy.company?.name?.toLowerCase().includes(query)
    );
  });

  return (
    <div className="min-h-screen py-8">
      <div className="container mx-auto px-6">
        {/* Header */}
        <div className="max-w-6xl mx-auto mb-8">
          <div className="text-center mb-8">
            <h1
              className="text-4xl font-bold mb-3"
              style={{ color: 'rgb(var(--text-primary))' }}
            >
              Все вакансии
            </h1>
            <p className="text-lg" style={{ color: 'rgb(var(--text-muted))' }}>
              {pagination
                ? `Найдено ${pagination.total_items} вакансий`
                : 'Загрузка вакансий...'}
            </p>
          </div>

          {/* Search Bar */}
          <div className="relative max-w-2xl mx-auto">
            <Search
              className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5"
              style={{ color: 'rgb(var(--accent))' }}
            />
            <Input
              type="search"
              placeholder="Поиск по названию, описанию или компании..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-12 pr-12 h-12 rounded-xl border-2 text-base shadow-lg"
              style={{
                backgroundColor: 'rgb(var(--bg-header-muted)/0.5)',
                borderColor: 'rgb(var(--border))',
                color: 'rgb(var(--text-primary))',
              }}
            />
            {searchQuery && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSearchQuery('')}
                className="absolute right-2 top-1/2 -translate-y-1/2 h-8"
                style={{ color: 'rgb(var(--text-muted))' }}
              >
                ✕
              </Button>
            )}
          </div>

          {/* Stats & Filters Bar */}
          <div className="flex flex-wrap items-center justify-between gap-4 mt-6">
            <div className="flex items-center gap-2">
              <Briefcase
                className="h-5 w-5"
                style={{ color: 'rgb(var(--accent))' }}
              />
              <span className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                Показано:{' '}
                <span className="font-semibold" style={{ color: 'rgb(var(--text-primary))' }}>
                  {filteredVacancies.length} из {vacancies.length}
                </span>
              </span>
            </div>
            <Button
              variant="outline"
              size="sm"
              style={{
                borderColor: 'rgb(var(--border))',
                color: 'rgb(var(--text-primary))',
              }}
            >
              <Filter className="h-4 w-4 mr-2" />
              Фильтры
            </Button>
          </div>
        </div>

        {/* Vacancies Grid */}
        <div className="max-w-6xl mx-auto">
          <VacancyList vacancies={filteredVacancies} loading={loading} />

          {/* Pagination */}
          {pagination && !loading && (
            <Pagination pagination={pagination} onPageChange={handlePageChange} />
          )}
        </div>
      </div>
    </div>
  );
}
