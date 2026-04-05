import { useState } from 'react';
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
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { MultiSelect, SalaryRangeFilter, ToggleFilter, ActiveFilterTags } from './filters';

export default function VacancyFilters({ filters, availableFilters, onFiltersChange, loading }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [localSearch, setLocalSearch] = useState(filters.search || '');

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

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    onFiltersChange({ ...filters, search: localSearch });
  };

  const handleClearSearch = () => {
    setLocalSearch('');
    onFiltersChange({ ...filters, search: '' });
  };

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

  return (
    <div
      className="rounded-2xl border p-6 mb-8"
      style={{
        backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
        borderColor: 'rgb(var(--border))',
      }}
    >
      <form onSubmit={handleSearchSubmit} className="relative mb-6">
        <Search
          className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5"
          style={{ color: 'rgb(var(--accent))' }}
        />
        <Input
          type="text"
          placeholder="Поиск по названию, описанию, навыкам..."
          value={localSearch}
          onChange={(e) => setLocalSearch(e.target.value)}
          className="pl-12 pr-32 h-14 rounded-xl border-2 text-base"
          style={{
            backgroundColor: 'rgb(var(--bg-header-muted))',
            borderColor: 'rgb(var(--border))',
            color: 'rgb(var(--text-primary))',
          }}
        />

        {localSearch && (
          <button
            type="button"
            onClick={handleClearSearch}
            className="absolute right-26 top-1/2 -translate-y-1/2 p-1 rounded-full hover:bg-black/5 transition-colors"
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
