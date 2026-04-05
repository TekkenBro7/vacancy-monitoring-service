import { useState, useEffect, useRef } from 'react';
import { Search, X, ChevronDown, ChevronUp, Check } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import VacancyService from '@/api/services/VacancyService';

export default function MultiSelect({
  label,
  icon: Icon,
  options = [],
  selected = [],
  onChange,
  placeholder,
  maxHeight = 280,
  filterType = null,
  currentFilters = {},
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const containerRef = useRef(null);
  const searchTimeoutRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
        setSearchTerm('');
        setSearchResults(null);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  // Закрытие по Escape
  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
        setSearchTerm('');
        setSearchResults(null);
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen]);

  useEffect(() => {
    if (!filterType || !searchTerm.trim()) {
      setSearchResults(null);
      return;
    }

    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    searchTimeoutRef.current = setTimeout(async () => {
      setIsSearching(true);
      try {
        const results = await VacancyService.searchFilterOptions(filterType, searchTerm.trim(), {
          source_ids: currentFilters.source_ids,
        });
        setSearchResults(results);
      } catch (error) {
        console.error('Search error:', error);
        setSearchResults(null);
      } finally {
        setIsSearching(false);
      }
    }, 300);

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [searchTerm, filterType, currentFilters.source_ids]);

  useEffect(() => {
    if (!isOpen) {
      setSearchTerm('');
      setSearchResults(null);
    }
  }, [isOpen]);

  const displayOptions = searchResults !== null ? searchResults : options;

  const filteredOptions = filterType
    ? displayOptions
    : displayOptions.filter((opt) => opt.name.toLowerCase().includes(searchTerm.toLowerCase()));

  const sortedOptions = [...filteredOptions].sort((a, b) => {
    const aSelected = selected.includes(a.id);
    const bSelected = selected.includes(b.id);
    if (aSelected && !bSelected) return -1;
    if (!aSelected && bSelected) return 1;
    return (b.count || 0) - (a.count || 0);
  });

  const toggleOption = (id) => {
    if (selected.includes(id)) {
      onChange(selected.filter((s) => s !== id));
    } else {
      onChange([...selected, id]);
    }
  };

  return (
    <div className="relative" ref={containerRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-3 rounded-xl border-2 transition-all duration-200 hover:border-opacity-70"
        style={{
          backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
          borderColor: selected.length > 0 ? 'rgb(var(--accent))' : 'rgb(var(--border))',
        }}
      >
        <div className="flex items-center gap-2">
          <Icon className="h-4 w-4" style={{ color: 'rgb(var(--accent))' }} />
          <span style={{ color: 'rgb(var(--text-primary))' }}>
            {label}
            {selected.length > 0 && (
              <Badge
                className="ml-2 text-xs"
                style={{
                  backgroundColor: 'rgb(var(--accent))',
                  color: 'white',
                }}
              >
                {selected.length}
              </Badge>
            )}
          </span>
        </div>
        {isOpen ? (
          <ChevronUp className="h-4 w-4" style={{ color: 'rgb(var(--text-muted))' }} />
        ) : (
          <ChevronDown className="h-4 w-4" style={{ color: 'rgb(var(--text-muted))' }} />
        )}
      </button>

      {isOpen && (
        <div
          className="absolute z-50 w-full mt-2 rounded-xl border-2 shadow-2xl overflow-hidden"
          style={{
            backgroundColor: 'rgb(var(--bg-header))',
            borderColor: 'rgb(var(--border))',
            minWidth: '280px',
          }}
        >
          {(options.length > 5 || filterType) && (
            <div className="p-3 border-b" style={{ borderColor: 'rgb(var(--border))' }}>
              <div className="relative">
                <Search
                  className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4"
                  style={{ color: 'rgb(var(--text-muted))' }}
                />
                <Input
                  placeholder={`Поиск ${placeholder}...`}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-9 h-9"
                  style={{
                    backgroundColor: 'rgb(var(--bg-header-muted))',
                    borderColor: 'rgb(var(--border))',
                    color: 'rgb(var(--text-primary))',
                  }}
                  onClick={(e) => e.stopPropagation()}
                  autoFocus
                />
                {(searchTerm || isSearching) && (
                  <div className="absolute right-3 top-1/2 -translate-y-1/2">
                    {isSearching ? (
                      <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSearchTerm('');
                          setSearchResults(null);
                        }}
                        className="p-1"
                      >
                        <X className="h-3 w-3" style={{ color: 'rgb(var(--text-muted))' }} />
                      </button>
                    )}
                  </div>
                )}
              </div>

              <p className="text-xs mt-2" style={{ color: 'rgb(var(--text-muted))' }}>
                {searchTerm
                  ? `Найдено: ${filteredOptions.length}`
                  : filterType
                    ? `Показаны топ-${options.length}. Введите для поиска.`
                    : `Всего: ${options.length}`}
              </p>
            </div>
          )}

          {selected.length > 0 && !searchTerm && (
            <div
              className="px-3 py-2 border-b flex items-center justify-between"
              style={{
                borderColor: 'rgb(var(--border))',
                backgroundColor: 'rgb(var(--accent)/0.05)',
              }}
            >
              <span className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                Выбрано: {selected.length}
              </span>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  onChange([]);
                }}
                className="text-xs hover:underline"
                style={{ color: 'rgb(var(--accent))' }}
              >
                Сбросить все
              </button>
            </div>
          )}

          <div
            className="overflow-y-auto overscroll-contain"
            style={{ maxHeight: `${maxHeight}px` }}
          >
            {sortedOptions.length > 0 ? (
              <div className="p-2 space-y-0.5">
                {sortedOptions.map((option) => {
                  const isSelected = selected.includes(option.id);
                  return (
                    <label
                      key={option.id}
                      className="flex items-center justify-between p-2.5 rounded-lg cursor-pointer transition-all duration-150"
                      style={{
                        backgroundColor: isSelected ? 'rgb(var(--accent)/0.12)' : 'transparent',
                      }}
                      onMouseEnter={(e) => {
                        if (!isSelected) {
                          e.currentTarget.style.backgroundColor = 'rgb(var(--bg-header-muted))';
                        }
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = isSelected
                          ? 'rgb(var(--accent)/0.12)'
                          : 'transparent';
                      }}
                    >
                      <div className="flex items-center gap-3 flex-1 min-w-0">
                        <div
                          className="w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 transition-all"
                          style={{
                            borderColor: isSelected ? 'rgb(var(--accent))' : 'rgb(var(--border))',
                            backgroundColor: isSelected ? 'rgb(var(--accent))' : 'transparent',
                          }}
                        >
                          {isSelected && <Check className="h-3 w-3 text-white" />}
                        </div>
                        <span
                          className="text-sm truncate"
                          style={{
                            color: isSelected ? 'rgb(var(--accent))' : 'rgb(var(--text-primary))',
                            fontWeight: isSelected ? 500 : 400,
                          }}
                          title={option.name}
                        >
                          {option.name}
                        </span>
                      </div>
                      <span
                        className="text-xs px-2 py-0.5 rounded-full flex-shrink-0 ml-2"
                        style={{
                          backgroundColor: isSelected
                            ? 'rgb(var(--accent)/0.2)'
                            : 'rgb(var(--bg-header-muted))',
                          color: isSelected ? 'rgb(var(--accent))' : 'rgb(var(--text-muted))',
                        }}
                      >
                        {(option.count || 0).toLocaleString()}
                      </span>
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => toggleOption(option.id)}
                        className="sr-only"
                      />
                    </label>
                  );
                })}
              </div>
            ) : (
              <div className="p-8 text-center">
                <p className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                  {isSearching ? 'Поиск...' : 'Ничего не найдено'}
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
