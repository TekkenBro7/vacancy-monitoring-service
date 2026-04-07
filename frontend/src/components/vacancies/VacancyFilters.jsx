import { useState, useEffect, useRef } from 'react';
import {
  Search,
  X,
  MapPin,
  Building2,
  Globe,
  Banknote,
  Briefcase,
  Clock,
  GraduationCap,
  Sparkles,
  RotateCcw,
  SlidersHorizontal,
  History,
  Trash2,
  Loader2,
  LogIn,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { MultiSelect, SalaryRangeFilter, ToggleFilter, ActiveFilterTags } from './filters';
import { SearchQueriesService } from '@/api/services/SearchQueries';
import { useAuth } from '@/utils/AuthContext';

export default function VacancyFilters({ filters, availableFilters, onFiltersChange, loading }) {
  const { user } = useAuth();
  const [isExpanded, setIsExpanded] = useState(false);
  const [localSearch, setLocalSearch] = useState(filters.search || '');
  const [searchHistory, setSearchHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const searchInputRef = useRef(null);
  const historyRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        historyRef.current &&
        !historyRef.current.contains(event.target) &&
        searchInputRef.current &&
        !searchInputRef.current.contains(event.target)
      ) {
        setShowHistory(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSearchFocus = async () => {
    setShowHistory(true);
    if (!historyLoaded && user?.id) {
      setHistoryLoading(true);
      try {
        const history = await SearchQueriesService.getUserQueries(user.id);
        setSearchHistory(history);
        setHistoryLoaded(true);
      } catch (error) {
        console.error('Failed to load search history:', error);
      } finally {
        setHistoryLoading(false);
      }
    }
  };

  const handleSelectHistory = (queryText) => {
    setLocalSearch(queryText);
    setShowHistory(false);
    onFiltersChange({ ...filters, search: queryText });
  };

  const handleDeleteHistory = async (e, queryId) => {
    e.stopPropagation();
    try {
      await SearchQueriesService.deleteQuery(queryId);
      setSearchHistory((prev) => prev.filter((q) => q.id !== queryId));
    } catch (error) {
      console.error('Failed to delete search query:', error);
    }
  };

  const saveSearchQuery = async (queryText) => {
    if (!user?.id || !queryText.trim()) return;
    const exists = searchHistory.some(
      (q) => q.query_text.toLowerCase() === queryText.toLowerCase()
    );
    if (!exists) {
      try {
        const newQuery = await SearchQueriesService.createQuery(user.id, queryText.trim());
        setSearchHistory((prev) => [newQuery, ...prev]);
      } catch (error) {
        if (error.response?.status !== 409) {
          console.error('Failed to save search query:', error);
        }
      }
    }
  };

  const handleSearchSubmit = async (e) => {
    e.preventDefault();
    setShowHistory(false);
    if (localSearch.trim()) {
      await saveSearchQuery(localSearch);
    }
    onFiltersChange({ ...filters, search: localSearch });
  };

  const handleClearSearch = () => {
    setLocalSearch('');
    onFiltersChange({ ...filters, search: '' });
  };

  const activeFiltersCount = [
    filters.source_ids?.length > 0,
    filters.company_ids?.length > 0,
    filters.city_ids?.length > 0,
    filters.skill_ids?.length > 0,
    filters.experience?.length > 0,
    filters.employment?.length > 0,
    filters.schedule?.length > 0,
    filters.salary_from || filters.salary_to,
    filters.is_remote,
    filters.with_salary_only,
    filters.internship,
  ].filter(Boolean).length;

  const resetFilters = () => {
    setLocalSearch('');
    onFiltersChange({
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
    });
  };

  const filteredHistory = searchHistory.filter((q) =>
    q.query_text.toLowerCase().includes(localSearch.toLowerCase())
  );

  return (
    <div
      className="rounded-2xl border p-6 mb-8"
      style={{
        backgroundColor: 'rgb(var(--bg-header-muted))',
        borderColor: 'rgb(var(--border))',
      }}
    >
      <div className="relative mb-6">
        <form onSubmit={handleSearchSubmit} className="relative">
          <Search
            className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5"
            style={{ color: 'rgb(var(--accent))' }}
          />
          <Input
            ref={searchInputRef}
            type="text"
            placeholder="Поиск по названию, описанию, навыкам..."
            value={localSearch}
            onChange={(e) => setLocalSearch(e.target.value)}
            onFocus={handleSearchFocus}
            className="pl-12 pr-32 h-14 rounded-xl border-2 text-base"
            style={{
              backgroundColor: 'var(--dropdown-bg)',
              borderColor: showHistory ? 'rgb(var(--accent))' : 'rgb(var(--border))',
              color: 'rgb(var(--text-primary))',
            }}
          />
          {localSearch && (
            <button
              type="button"
              onClick={handleClearSearch}
              className="absolute right-26 top-1/2 -translate-y-1/2 p-1 rounded-full transition-colors"
              style={{ color: 'rgb(var(--text-muted))' }}
            >
              <X className="h-4 w-4" />
            </button>
          )}
          <Button
            type="submit"
            disabled={loading}
            className="absolute right-2 top-1/2 -translate-y-1/2 h-10 px-6 rounded-lg"
            style={{
              backgroundColor: 'rgb(var(--accent))',
              color: 'white',
            }}
          >
            Найти
          </Button>
        </form>

        {showHistory && (
          <div
            ref={historyRef}
            className="absolute top-full left-0 right-0 mt-2 rounded-xl border shadow-lg overflow-hidden z-50"
            style={{
              backgroundColor: 'var(--dropdown-bg)',
              borderColor: 'rgb(var(--border))',
            }}
          >
            <div
              className="flex items-center justify-between px-4 py-3 border-b"
              style={{
                borderColor: 'rgb(var(--border))',
                backgroundColor: 'var(--dropdown-header)',
              }}
            >
              <div className="flex items-center gap-2">
                <History className="h-4 w-4" style={{ color: 'rgb(var(--text-muted))' }} />
                <span className="text-sm font-medium" style={{ color: 'rgb(var(--text-primary))' }}>
                  История поиска
                </span>
              </div>
              {historyLoading && (
                <Loader2 className="h-4 w-4 animate-spin" style={{ color: 'rgb(var(--accent))' }} />
              )}
            </div>

            <div
              className="max-h-64 overflow-y-auto"
              style={{ backgroundColor: 'var(--dropdown-bg)' }}
            >
              {!user ? (
                <div
                  className="flex flex-col items-center justify-center py-8 px-4 text-center"
                  style={{ backgroundColor: 'var(--dropdown-bg)' }}
                >
                  <LogIn className="h-10 w-10 mb-3" style={{ color: 'rgb(var(--text-muted))' }} />
                  <span
                    className="text-sm font-medium mb-1"
                    style={{ color: 'rgb(var(--text-primary))' }}
                  >
                    Войдите в аккаунт
                  </span>
                  <span className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                    Чтобы сохранять историю поиска и получить доступ к персональным рекомендациям
                  </span>
                </div>
              ) : historyLoading && searchHistory.length === 0 ? (
                <div
                  className="flex items-center justify-center py-8"
                  style={{ backgroundColor: 'var(--dropdown-bg)' }}
                >
                  <Loader2
                    className="h-6 w-6 animate-spin"
                    style={{ color: 'rgb(var(--accent))' }}
                  />
                </div>
              ) : filteredHistory.length > 0 ? (
                filteredHistory.map((query) => (
                  <div
                    key={query.id}
                    onClick={() => handleSelectHistory(query.query_text)}
                    className="flex items-center justify-between px-4 py-3 cursor-pointer transition-colors group"
                    style={{ backgroundColor: 'var(--dropdown-bg)' }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = 'var(--dropdown-hover)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = 'var(--dropdown-bg)';
                    }}
                  >
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <Search
                        className="h-4 w-4 flex-shrink-0"
                        style={{ color: 'rgb(var(--text-muted))' }}
                      />
                      <span className="truncate" style={{ color: 'rgb(var(--text-primary))' }}>
                        {query.query_text}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                        {formatDate(query.created_at)}
                      </span>
                      <button
                        onClick={(e) => handleDeleteHistory(e, query.id)}
                        className="p-1 rounded opacity-0 group-hover:opacity-100 transition-opacity"
                        style={{ color: 'rgb(var(--text-muted))' }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.color = '#ef4444';
                          e.currentTarget.style.backgroundColor = 'rgba(239, 68, 68, 0.1)';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.color = 'rgb(var(--text-muted))';
                          e.currentTarget.style.backgroundColor = 'transparent';
                        }}
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <div
                  className="flex flex-col items-center justify-center py-8 text-center"
                  style={{ color: 'rgb(var(--text-muted))', backgroundColor: 'var(--dropdown-bg)' }}
                >
                  <History className="h-8 w-8 mb-2 opacity-50" />
                  <span className="text-sm">
                    {localSearch ? 'Ничего не найдено' : 'История поиска пуста'}
                  </span>
                </div>
              )}
            </div>

            {user && filteredHistory.length > 0 && (
              <div
                className="px-4 py-2 border-t text-xs"
                style={{
                  borderColor: 'rgb(var(--border))',
                  color: 'rgb(var(--text-muted))',
                  backgroundColor: 'var(--dropdown-header)',
                }}
              >
                💡 Нажмите на запрос, чтобы сразу выполнить поиск
              </div>
            )}
          </div>
        )}
      </div>

      <div className="flex flex-wrap gap-3 mb-4">
        <ToggleFilter
          label="Удалённая работа"
          icon={Globe}
          value={filters.is_remote}
          count={availableFilters?.remote_count || 0}
          onChange={(v) => onFiltersChange({ ...filters, is_remote: v ? true : null })}
        />
        <ToggleFilter
          label="С зарплатой"
          icon={Banknote}
          value={filters.with_salary_only}
          count={availableFilters?.with_salary_count || 0}
          onChange={(v) => onFiltersChange({ ...filters, with_salary_only: v })}
        />
        <ToggleFilter
          label="Стажировки"
          icon={GraduationCap}
          value={filters.internship}
          count={availableFilters?.internship_count || 0}
          onChange={(v) => onFiltersChange({ ...filters, internship: v ? true : null })}
        />
        <Button
          variant="outline"
          onClick={() => setIsExpanded(!isExpanded)}
          className="ml-auto"
          style={{
            borderColor: activeFiltersCount > 0 ? 'rgb(var(--accent))' : 'rgb(var(--border))',
            color: 'rgb(var(--text-primary))',
          }}
        >
          <SlidersHorizontal className="h-4 w-4 mr-2" />
          Все фильтры
          {activeFiltersCount > 0 && (
            <Badge
              className="ml-2"
              style={{ backgroundColor: 'rgb(var(--accent))', color: 'white' }}
            >
              {activeFiltersCount}
            </Badge>
          )}
        </Button>
        {activeFiltersCount > 0 && (
          <Button
            variant="ghost"
            onClick={resetFilters}
            style={{ color: 'rgb(var(--text-muted))' }}
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            Сбросить
          </Button>
        )}
      </div>

      {isExpanded && (
        <div
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pt-4 border-t"
          style={{ borderColor: 'rgb(var(--border))' }}
        >
          <MultiSelect
            label="Источник"
            icon={Globe}
            options={availableFilters?.sources || []}
            selected={filters.source_ids || []}
            onChange={(v) => onFiltersChange({ ...filters, source_ids: v })}
            placeholder="источников"
            maxHeight={250}
          />
          <MultiSelect
            label="Компания"
            icon={Building2}
            options={availableFilters?.companies || []}
            selected={filters.company_ids || []}
            onChange={(v) => onFiltersChange({ ...filters, company_ids: v })}
            placeholder="компаний"
            maxHeight={300}
            filterType="companies"
            currentFilters={filters}
          />
          <MultiSelect
            label="Город"
            icon={MapPin}
            options={availableFilters?.cities || []}
            selected={filters.city_ids || []}
            onChange={(v) => onFiltersChange({ ...filters, city_ids: v })}
            placeholder="городов"
            maxHeight={300}
            filterType="cities"
            currentFilters={filters}
          />
          <SalaryRangeFilter
            salaryFrom={filters.salary_from}
            salaryTo={filters.salary_to}
            currency={filters.currency_id}
            currencies={availableFilters?.currencies || []}
            onChange={(v) =>
              onFiltersChange({
                ...filters,
                salary_from: v.from !== undefined ? v.from : filters.salary_from,
                salary_to: v.to !== undefined ? v.to : filters.salary_to,
                currency_id: v.currency !== undefined ? v.currency : filters.currency_id,
              })
            }
          />
          <MultiSelect
            label="Опыт"
            icon={Briefcase}
            options={availableFilters?.experience || []}
            selected={filters.experience || []}
            onChange={(v) => onFiltersChange({ ...filters, experience: v })}
            placeholder="опыта"
            maxHeight={200}
          />
          <MultiSelect
            label="Занятость"
            icon={Clock}
            options={availableFilters?.employment || []}
            selected={filters.employment || []}
            onChange={(v) => onFiltersChange({ ...filters, employment: v })}
            placeholder="занятости"
            maxHeight={200}
          />
          <MultiSelect
            label="График"
            icon={Clock}
            options={availableFilters?.schedule || []}
            selected={filters.schedule || []}
            onChange={(v) => onFiltersChange({ ...filters, schedule: v })}
            placeholder="графиков"
            maxHeight={200}
          />
          <MultiSelect
            label="Навыки"
            icon={Sparkles}
            options={availableFilters?.skills || []}
            selected={filters.skill_ids || []}
            onChange={(v) => onFiltersChange({ ...filters, skill_ids: v })}
            placeholder="навыков"
            maxHeight={350}
            filterType="skills"
            currentFilters={filters}
          />
        </div>
      )}

      {activeFiltersCount > 0 && (
        <ActiveFilterTags
          filters={filters}
          availableFilters={availableFilters}
          onFiltersChange={onFiltersChange}
        />
      )}
    </div>
  );
}

function formatDate(dateString) {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);
  if (diffMins < 1) return 'только что';
  if (diffMins < 60) return `${diffMins} мин назад`;
  if (diffHours < 24) return `${diffHours} ч назад`;
  if (diffDays < 7) return `${diffDays} дн назад`;
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
  });
}
