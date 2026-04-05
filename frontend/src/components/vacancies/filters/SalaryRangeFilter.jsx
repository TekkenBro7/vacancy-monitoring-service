import { useState, useEffect, useRef } from 'react';
import { Banknote, ChevronDown, ChevronUp } from 'lucide-react';
import { Input } from '@/components/ui/input';

export default function SalaryRangeFilter({
  salaryFrom,
  salaryTo,
  currency,
  currencies,
  onChange,
}) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen]);

  const presetRanges = [
    { label: 'Любая', from: null, to: null },
    { label: 'до 50 000', from: null, to: 50000 },
    { label: '50 — 100 тыс.', from: 50000, to: 100000 },
    { label: '100 — 150 тыс.', from: 100000, to: 150000 },
    { label: '150 — 200 тыс.', from: 150000, to: 200000 },
    { label: 'от 200 000', from: 200000, to: null },
  ];

  const hasValue = salaryFrom || salaryTo;

  return (
    <div className="relative" ref={containerRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-3 rounded-xl border-2 transition-all duration-200"
        style={{
          backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
          borderColor: hasValue ? 'rgb(var(--accent))' : 'rgb(var(--border))',
        }}
      >
        <div className="flex items-center gap-2">
          <Banknote className="h-4 w-4" style={{ color: 'rgb(var(--accent))' }} />
          <span style={{ color: 'rgb(var(--text-primary))' }}>
            {hasValue ? (
              <>
                {salaryFrom ? `от ${salaryFrom.toLocaleString()}` : ''}
                {salaryFrom && salaryTo ? ' — ' : ''}
                {salaryTo ? `до ${salaryTo.toLocaleString()}` : ''}
              </>
            ) : (
              'Зарплата'
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
            minWidth: '300px',
          }}
        >
          <div className="p-4 max-h-80 overflow-y-auto">
            <p className="text-xs mb-2" style={{ color: 'rgb(var(--text-muted))' }}>
              Быстрый выбор:
            </p>
            <div className="flex flex-wrap gap-2 mb-4">
              {presetRanges.map((range, idx) => {
                const isActive = salaryFrom === range.from && salaryTo === range.to;
                return (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => onChange({ from: range.from, to: range.to })}
                    className="px-3 py-1.5 rounded-full text-sm transition-all"
                    style={{
                      backgroundColor: isActive
                        ? 'rgb(var(--accent))'
                        : 'rgb(var(--bg-header-muted))',
                      color: isActive ? 'white' : 'rgb(var(--text-primary))',
                    }}
                  >
                    {range.label}
                  </button>
                );
              })}
            </div>

            <p className="text-xs mb-2" style={{ color: 'rgb(var(--text-muted))' }}>
              Или укажите свой диапазон:
            </p>
            <div className="flex gap-2 items-center">
              <Input
                type="number"
                placeholder="От"
                value={salaryFrom || ''}
                onChange={(e) =>
                  onChange({
                    from: e.target.value ? parseInt(e.target.value) : null,
                    to: salaryTo,
                  })
                }
                onClick={(e) => e.stopPropagation()}
                className="h-10"
                style={{
                  backgroundColor: 'rgb(var(--bg-header-muted))',
                  borderColor: 'rgb(var(--border))',
                  color: 'rgb(var(--text-primary))',
                }}
              />
              <span style={{ color: 'rgb(var(--text-muted))' }}>—</span>
              <Input
                type="number"
                placeholder="До"
                value={salaryTo || ''}
                onChange={(e) =>
                  onChange({
                    from: salaryFrom,
                    to: e.target.value ? parseInt(e.target.value) : null,
                  })
                }
                onClick={(e) => e.stopPropagation()}
                className="h-10"
                style={{
                  backgroundColor: 'rgb(var(--bg-header-muted))',
                  borderColor: 'rgb(var(--border))',
                  color: 'rgb(var(--text-primary))',
                }}
              />
            </div>

            {currencies && currencies.length > 0 && (
              <div className="mt-4 pt-3 border-t" style={{ borderColor: 'rgb(var(--border))' }}>
                <p className="text-xs mb-2" style={{ color: 'rgb(var(--text-muted))' }}>
                  Валюта:
                </p>
                <div className="flex flex-wrap gap-2">
                  {currencies.map((curr) => (
                    <button
                      key={curr.id}
                      type="button"
                      onClick={() => onChange({ currency: currency === curr.id ? null : curr.id })}
                      className="px-3 py-1 rounded-full text-sm transition-all"
                      style={{
                        backgroundColor:
                          currency === curr.id
                            ? 'rgb(var(--accent))'
                            : 'rgb(var(--bg-header-muted))',
                        color: currency === curr.id ? 'white' : 'rgb(var(--text-primary))',
                      }}
                    >
                      {curr.name}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {hasValue && (
            <div className="px-4 py-2 border-t" style={{ borderColor: 'rgb(var(--border))' }}>
              <button
                type="button"
                onClick={() => onChange({ from: null, to: null, currency: null })}
                className="text-sm w-full text-center"
                style={{ color: 'rgb(var(--accent))' }}
              >
                Сбросить фильтр зарплаты
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
