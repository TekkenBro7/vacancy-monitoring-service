import { useState, useEffect, useCallback } from 'react';
import { Briefcase, ArrowUpDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import VacancyService from '@/api/services/VacancyService';
import BookmarkService from '@/api/services/BookmarkService';
import VacancyFilters from '@/components/vacancies/VacancyFilters';
import VacancyList from '@/components/vacancies/VacancyList';
import Pagination from '@/components/vacancies/Pagination';
import { useAuth } from '@/utils/AuthContext';
import useNotification from '@/hooks/useNotification';

const PAGE_SIZE = 20;

const DEFAULT_FILTERS = {
  search: '',
  source_ids: [],
  company_ids: [],
  city_ids: [],
  skill_ids: [],
  experience: [],
  employment: [],
  schedule: [],
  salary_from: null,
  salary_to: null,
  currency_id: null,
  is_remote: null,
  with_salary_only: false,
  internship: null,
  sort_by: 'published_at',
  sort_order: 'desc',
};

export default function VacanciesPage() {
  const notification = useNotification();
  const { isAuthenticated } = useAuth();

  const [vacancies, setVacancies] = useState([]);
  const [pagination, setPagination] = useState(null);
  const [availableFilters, setAvailableFilters] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [bookmarkedIds, setBookmarkedIds] = useState(new Set());

  const loadBookmarkIds = useCallback(async () => {
    if (!isAuthenticated) {
      setBookmarkedIds(new Set());
      return;
    }

    try {
      const ids = await BookmarkService.getMyBookmarkIds();
      setBookmarkedIds(new Set(ids));
    } catch (error) {
      console.error('Error loading bookmark ids:', error);
    }
  }, [isAuthenticated]);

  const loadVacancies = useCallback(async () => {
    try {
      setLoading(true);

      const params = {
        page: currentPage,
        page_size: PAGE_SIZE,
        include_filters: true,
        sort_by: filters.sort_by,
        sort_order: filters.sort_order,
      };

      if (filters.search) params.search = filters.search;
      if (filters.source_ids?.length) params.source_ids = filters.source_ids;
      if (filters.company_ids?.length) params.company_ids = filters.company_ids;
      if (filters.city_ids?.length) params.city_ids = filters.city_ids;
      if (filters.skill_ids?.length) params.skill_ids = filters.skill_ids;
      if (filters.experience?.length) params.experience = filters.experience;
      if (filters.employment?.length) params.employment = filters.employment;
      if (filters.schedule?.length) params.schedule = filters.schedule;
      if (filters.salary_from) params.salary_from = filters.salary_from;
      if (filters.salary_to) params.salary_to = filters.salary_to;
      if (filters.currency_id) params.currency_id = filters.currency_id;
      if (filters.is_remote !== null) params.is_remote = filters.is_remote;
      if (filters.with_salary_only) params.with_salary_only = true;
      if (filters.internship !== null) params.internship = filters.internship;

      const data = await VacancyService.searchVacancies(params);

      setVacancies(data.items || []);
      setPagination(data.pagination);
      if (data.filters) {
        setAvailableFilters(data.filters);
      }
    } catch (error) {
      notification.error('Ошибка', 'Не удалось загрузить вакансии');
      console.error('Error loading vacancies:', error);
    } finally {
      setLoading(false);
    }
  }, [currentPage, filters, notification]);

  useEffect(() => {
    loadBookmarkIds();
  }, [loadBookmarkIds]);

  useEffect(() => {
    loadVacancies();
  }, [loadVacancies]);

  const handleBookmarkChange = (vacancyId, isBookmarked) => {
    setBookmarkedIds((prev) => {
      const newSet = new Set(prev);
      if (isBookmarked) {
        newSet.add(vacancyId);
      } else {
        newSet.delete(vacancyId);
      }
      return newSet;
    });
  };

  const handleFiltersChange = (newFilters) => {
    setFilters(newFilters);
    setCurrentPage(1);
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSortChange = (sortBy) => {
    const newOrder = filters.sort_by === sortBy && filters.sort_order === 'desc' ? 'asc' : 'desc';
    handleFiltersChange({ ...filters, sort_by: sortBy, sort_order: newOrder });
  };

  const sortOptions = [
    { value: 'published_at', label: 'Дата публикации' },
    { value: 'salary_from', label: 'Зарплата' },
    { value: 'title', label: 'Название' },
  ];

  return (
    <div className="min-h-screen py-8">
      <div className="container mx-auto px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold mb-3" style={{ color: 'rgb(var(--text-primary))' }}>
              Поиск вакансий
            </h1>
            <p className="text-lg" style={{ color: 'rgb(var(--text-muted))' }}>
              {pagination
                ? `Найдено ${pagination.total_items.toLocaleString()} вакансий`
                : 'Загрузка...'}
            </p>
          </div>

          <VacancyFilters
            filters={filters}
            availableFilters={availableFilters}
            onFiltersChange={handleFiltersChange}
            loading={loading}
          />

          <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
            <div className="flex items-center gap-2">
              <Briefcase className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
              <span className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                Показано:{' '}
                <span className="font-semibold" style={{ color: 'rgb(var(--text-primary))' }}>
                  {vacancies.length} из {pagination?.total_items || 0}
                </span>
              </span>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                Сортировка:
              </span>
              <div className="flex gap-1">
                {sortOptions.map((option) => (
                  <Button
                    key={option.value}
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSortChange(option.value)}
                    className="flex items-center gap-1"
                    style={{
                      backgroundColor:
                        filters.sort_by === option.value ? 'rgb(var(--accent)/0.1)' : 'transparent',
                      color:
                        filters.sort_by === option.value
                          ? 'rgb(var(--accent))'
                          : 'rgb(var(--text-muted))',
                    }}
                  >
                    {option.label}
                    {filters.sort_by === option.value && (
                      <ArrowUpDown
                        className={`h-3 w-3 transition-transform ${
                          filters.sort_order === 'asc' ? 'rotate-180' : ''
                        }`}
                      />
                    )}
                  </Button>
                ))}
              </div>
            </div>
          </div>

          <VacancyList
            vacancies={vacancies}
            loading={loading}
            bookmarkedIds={bookmarkedIds}
            onBookmarkChange={handleBookmarkChange}
          />

          {pagination && !loading && pagination.total_pages > 1 && (
            <Pagination pagination={pagination} onPageChange={handlePageChange} />
          )}
        </div>
      </div>
    </div>
  );
}
