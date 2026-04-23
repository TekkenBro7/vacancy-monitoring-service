import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import {
  ArrowLeft,
  Sparkles,
  Loader2,
  Building,
  MapPin,
  DollarSign,
  Clock,
  Briefcase,
  ExternalLink,
  Trash2,
  Plus,
  TrendingUp,
  Globe,
  AlertCircle,
  Home,
  GraduationCap,
  Wifi,
  Code,
  Award,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import ComparisonService from '@/api/services/ComparisonService';
import useNotification from '@/hooks/useNotification';

const MIN_VACANCIES = 2;
const VACANCY_COLORS = [
  ['59, 130, 246', '37, 99, 235'],
  ['168, 85, 247', '147, 51, 234'],
  ['34, 197, 94', '22, 163, 74'],
  ['249, 115, 22', '234, 88, 12'],
  ['236, 72, 153', '219, 39, 119'],
];

export default function ComparisonDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const notification = useNotification();

  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);

  const loadComparison = useCallback(async () => {
    try {
      setLoading(true);
      const data = await ComparisonService.getComparisonDetail(id);
      setComparison(data);
    } catch {
      notification.error('Ошибка', 'Не удалось загрузить сравнение');
      navigate('/comparisons');
    } finally {
      setLoading(false);
    }
  }, [id, notification, navigate]);

  useEffect(() => {
    loadComparison();
  }, [loadComparison]);

  const handleAnalyze = async () => {
    if (!comparison || comparison.vacancies.length < MIN_VACANCIES) {
      notification.warning('Недостаточно вакансий', `Нужно минимум ${MIN_VACANCIES} вакансии`);
      return;
    }
    setAnalyzing(true);
    try {
      const result = await ComparisonService.analyzeComparison(id);
      setAnalysis(result.ai_analysis);
      notification.success('Готово', 'AI проанализировал вакансии');
    } catch {
      notification.error('Ошибка', 'Не удалось выполнить анализ');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleRemove = async (vacancyId) => {
    try {
      await ComparisonService.removeVacancy(id, vacancyId);
      notification.success('Удалено', 'Вакансия удалена');
      loadComparison();
      setAnalysis(null);
    } catch {
      notification.error('Ошибка', 'Не удалось удалить');
    }
  };

  const formatSalary = (from, to, currency) => {
    const s = currency || '₽';
    if (!from && !to) return 'Договорная';
    if (from && to) return `${from.toLocaleString()} – ${to.toLocaleString()} ${s}`;
    if (from) return `от ${from.toLocaleString()} ${s}`;
    return `до ${to.toLocaleString()} ${s}`;
  };

  const getColor = (idx) => {
    const c = VACANCY_COLORS[idx % VACANCY_COLORS.length];
    return `linear-gradient(135deg, rgb(${c[0]}), rgb(${c[1]}))`;
  };

  const getColorRgb = (idx) => VACANCY_COLORS[idx % VACANCY_COLORS.length][0];

  const fields = [
    { label: 'Компания', icon: Building, get: (v) => v.company_name || '—' },
    {
      label: 'Зарплата',
      icon: DollarSign,
      get: (v) => formatSalary(v.salary_from, v.salary_to, v.currency_code),
      accent: true,
    },
    { label: 'Город', icon: MapPin, get: (v) => v.city_name || '—' },
    { label: 'Адрес', icon: Home, get: (v) => v.address || '—' },
    {
      label: 'Удалёнка',
      icon: Wifi,
      get: (v) => (v.is_remote === true ? 'Да' : v.is_remote === false ? 'Нет' : '—'),
      color: (v) => (v.is_remote === true ? '#22c55e' : v.is_remote === false ? '#ef4444' : null),
    },
    {
      label: 'Стажировка',
      icon: GraduationCap,
      get: (v) => (v.internship === true ? 'Да' : v.internship === false ? 'Нет' : '—'),
      color: (v) => (v.internship === true ? '#22c55e' : v.internship === false ? '#ef4444' : null),
    },
    { label: 'Опыт', icon: TrendingUp, get: (v) => v.experience || '—' },
    { label: 'Занятость', icon: Briefcase, get: (v) => v.employment || '—' },
    { label: 'График', icon: Clock, get: (v) => v.schedule || '—' },
    { label: 'Источник', icon: Globe, get: (v) => v.source_name || '—' },
  ];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2
            className="h-10 w-10 animate-spin mx-auto mb-4"
            style={{ color: 'rgb(var(--accent))' }}
          />
          <p style={{ color: 'rgb(var(--text-muted))' }}>Загрузка сравнения...</p>
        </div>
      </div>
    );
  }

  if (!comparison) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4">
        <div
          className="w-20 h-20 rounded-full flex items-center justify-center"
          style={{ backgroundColor: 'rgb(var(--accent)/0.1)' }}
        >
          <AlertCircle className="h-10 w-10" style={{ color: 'rgb(var(--accent))' }} />
        </div>
        <p className="text-lg font-medium" style={{ color: 'rgb(var(--text-primary))' }}>
          Сравнение не найдено
        </p>
        <Button onClick={() => navigate('/comparisons')} variant="outline">
          <ArrowLeft className="h-4 w-4 mr-2" />К списку
        </Button>
      </div>
    );
  }

  const vacancies = comparison.vacancies || [];

  return (
    <div className="min-h-screen py-6 lg:py-10">
      <div className="container mx-auto px-4 lg:px-6 max-w-7xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              onClick={() => navigate('/comparisons')}
              className="pl-0 hover:bg-transparent"
              style={{ color: 'rgb(var(--text-muted))' }}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Назад
            </Button>
            <div className="h-8 w-px" style={{ backgroundColor: 'rgb(var(--border))' }} />
            <div>
              <h1
                className="text-xl lg:text-2xl font-bold"
                style={{ color: 'rgb(var(--text-primary))' }}
              >
                {comparison.name}
              </h1>
              <p className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                {vacancies.length} из 5 вакансий
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={() => navigate('/vacancies')}
              style={{ borderColor: 'rgb(var(--border))', color: 'rgb(var(--text-primary))' }}
            >
              <Plus className="h-4 w-4 mr-2" />
              Добавить
            </Button>
            <Button
              onClick={handleAnalyze}
              disabled={analyzing || vacancies.length < MIN_VACANCIES}
              className="text-white shadow-lg"
              style={{
                background:
                  'linear-gradient(135deg, rgb(var(--button-from)), rgb(var(--button-to)))',
              }}
            >
              {analyzing ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Sparkles className="h-4 w-4 mr-2" />
              )}
              {analyzing ? 'Анализ...' : analysis ? 'Обновить' : 'AI Анализ'}
            </Button>
          </div>
        </div>

        {vacancies.length < MIN_VACANCIES && (
          <div
            className="mb-6 p-4 rounded-2xl border flex items-center gap-4"
            style={{
              background:
                'linear-gradient(135deg, rgb(var(--accent)/0.05), rgb(var(--accent)/0.1))',
              borderColor: 'rgb(var(--accent)/0.2)',
            }}
          >
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
              style={{ backgroundColor: 'rgb(var(--accent)/0.15)' }}
            >
              <AlertCircle className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
            </div>
            <div>
              <p className="font-medium" style={{ color: 'rgb(var(--text-primary))' }}>
                Добавьте ещё {MIN_VACANCIES - vacancies.length} вакансию
              </p>
              <p className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                Для AI-анализа нужно минимум {MIN_VACANCIES} вакансии
              </p>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
          <div className="xl:col-span-8 space-y-6">
            {vacancies.length === 0 ? (
              <div
                className="p-16 rounded-3xl border text-center"
                style={{
                  backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
                  borderColor: 'rgb(var(--border))',
                }}
              >
                <div
                  className="w-20 h-20 rounded-2xl mx-auto mb-6 flex items-center justify-center"
                  style={{ backgroundColor: 'rgb(var(--accent)/0.1)' }}
                >
                  <Briefcase className="h-10 w-10" style={{ color: 'rgb(var(--accent))' }} />
                </div>
                <p
                  className="text-lg font-semibold mb-2"
                  style={{ color: 'rgb(var(--text-primary))' }}
                >
                  Пока пусто
                </p>
                <p className="text-sm mb-6" style={{ color: 'rgb(var(--text-muted))' }}>
                  Добавьте вакансии для сравнения
                </p>
                <Button
                  onClick={() => navigate('/vacancies')}
                  className="text-white"
                  style={{
                    background:
                      'linear-gradient(135deg, rgb(var(--button-from)), rgb(var(--button-to)))',
                  }}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Выбрать вакансии
                </Button>
              </div>
            ) : (
              <>
                <div
                  className="grid gap-4"
                  style={{ gridTemplateColumns: `repeat(${vacancies.length}, 1fr)` }}
                >
                  {vacancies.map((v, i) => (
                    <div
                      key={v.id}
                      className="rounded-2xl border p-4 relative overflow-hidden transition-all hover:shadow-lg"
                      style={{
                        backgroundColor: 'rgb(var(--bg-header-muted)/0.4)',
                        borderColor: 'rgb(var(--border))',
                      }}
                    >
                      <div
                        className="absolute top-0 left-0 right-0 h-1"
                        style={{ background: getColor(i) }}
                      />
                      <div className="flex items-start justify-between mb-3">
                        <Badge
                          className="text-xs text-white font-medium"
                          style={{ background: getColor(i) }}
                        >
                          #{i + 1}
                        </Badge>
                        <button
                          onClick={() => handleRemove(v.id)}
                          className="p-1.5 rounded-lg transition-all hover:bg-red-500/10"
                        >
                          <Trash2 className="h-4 w-4" style={{ color: '#ef4444' }} />
                        </button>
                      </div>
                      <h3
                        className="font-semibold text-sm mb-2 line-clamp-2 cursor-pointer hover:underline"
                        style={{ color: 'rgb(var(--text-primary))' }}
                        onClick={() => navigate(`/vacancies/${v.id}`)}
                      >
                        {v.title}
                      </h3>
                      <p className="text-xs mb-3" style={{ color: 'rgb(var(--text-muted))' }}>
                        {v.company_name || 'Компания не указана'}
                      </p>
                      <div className="flex flex-wrap gap-1 mb-3">
                        {v.is_remote && (
                          <Badge
                            className="text-xs"
                            style={{ backgroundColor: 'rgba(34, 197, 94, 0.1)', color: '#22c55e' }}
                          >
                            <Wifi className="h-3 w-3 mr-1" />
                            Remote
                          </Badge>
                        )}
                        {v.internship && (
                          <Badge
                            className="text-xs"
                            style={{ backgroundColor: 'rgba(59, 130, 246, 0.1)', color: '#3b82f6' }}
                          >
                            <GraduationCap className="h-3 w-3 mr-1" />
                            Стажировка
                          </Badge>
                        )}
                      </div>
                      <p
                        className="font-bold text-sm mb-3"
                        style={{ color: `rgb(${getColorRgb(i)})` }}
                      >
                        {formatSalary(v.salary_from, v.salary_to, v.currency_code)}
                      </p>
                      {v.vacancy_url && (
                        <a
                          href={v.vacancy_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-xs font-medium hover:underline"
                          style={{ color: 'rgb(var(--accent))' }}
                        >
                          <ExternalLink className="h-3 w-3" />
                          Открыть
                        </a>
                      )}
                    </div>
                  ))}
                </div>

                <div
                  className="rounded-2xl border overflow-hidden"
                  style={{
                    backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
                    borderColor: 'rgb(var(--border))',
                  }}
                >
                  <div
                    className="p-4 border-b flex items-center gap-2"
                    style={{
                      borderColor: 'rgb(var(--border))',
                      backgroundColor: 'rgb(var(--bg-header-muted)/0.5)',
                    }}
                  >
                    <Award className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
                    <span className="font-semibold" style={{ color: 'rgb(var(--text-primary))' }}>
                      Сравнение характеристик
                    </span>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr style={{ borderBottom: '1px solid rgb(var(--border))' }}>
                          <th
                            className="p-3 text-left text-sm font-medium w-40"
                            style={{
                              color: 'rgb(var(--text-muted))',
                              backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
                            }}
                          >
                            Параметр
                          </th>
                          {vacancies.map((v, i) => (
                            <th
                              key={v.id}
                              className="p-3 text-left text-sm font-medium"
                              style={{ color: `rgb(${getColorRgb(i)})` }}
                            >
                              Вакансия #{i + 1}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {fields.map((f) => (
                          <tr
                            key={f.label}
                            className="border-b last:border-b-0"
                            style={{ borderColor: 'rgb(var(--border)/0.5)' }}
                          >
                            <td
                              className="p-3"
                              style={{ backgroundColor: 'rgb(var(--bg-header-muted)/0.2)' }}
                            >
                              <div className="flex items-center gap-2">
                                <f.icon
                                  className="h-4 w-4"
                                  style={{ color: 'rgb(var(--accent))' }}
                                />
                                <span
                                  className="text-sm font-medium"
                                  style={{ color: 'rgb(var(--text-primary))' }}
                                >
                                  {f.label}
                                </span>
                              </div>
                            </td>
                            {vacancies.map((v) => (
                              <td key={v.id} className="p-3">
                                <span
                                  className={`text-sm ${f.accent ? 'font-semibold' : ''}`}
                                  style={{
                                    color:
                                      f.color?.(v) ||
                                      (f.accent ? 'rgb(var(--accent))' : 'rgb(var(--text-muted))'),
                                  }}
                                >
                                  {f.get(v)}
                                </span>
                              </td>
                            ))}
                          </tr>
                        ))}
                        <tr>
                          <td
                            className="p-3"
                            style={{ backgroundColor: 'rgb(var(--bg-header-muted)/0.2)' }}
                          >
                            <div className="flex items-center gap-2">
                              <Code className="h-4 w-4" style={{ color: 'rgb(var(--accent))' }} />
                              <span
                                className="text-sm font-medium"
                                style={{ color: 'rgb(var(--text-primary))' }}
                              >
                                Навыки
                              </span>
                            </div>
                          </td>
                          {vacancies.map((v) => (
                            <td key={v.id} className="p-3">
                              <div className="flex flex-wrap gap-1">
                                {(v.skills || []).slice(0, 4).map((s, i) => (
                                  <Badge
                                    key={i}
                                    className="text-xs"
                                    style={{
                                      backgroundColor: 'rgb(var(--accent)/0.1)',
                                      color: 'rgb(var(--text-primary))',
                                    }}
                                  >
                                    {s}
                                  </Badge>
                                ))}
                                {(v.skills || []).length > 4 && (
                                  <Badge
                                    className="text-xs"
                                    style={{
                                      backgroundColor: 'rgb(var(--border)/0.5)',
                                      color: 'rgb(var(--text-muted))',
                                    }}
                                  >
                                    +{v.skills.length - 4}
                                  </Badge>
                                )}
                                {(!v.skills || v.skills.length === 0) && (
                                  <span
                                    className="text-sm"
                                    style={{ color: 'rgb(var(--text-muted))' }}
                                  >
                                    —
                                  </span>
                                )}
                              </div>
                            </td>
                          ))}
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </>
            )}
          </div>

          <div className="xl:col-span-4">
            <div
              className="sticky top-24 rounded-2xl border overflow-hidden"
              style={{
                backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
                borderColor: 'rgb(var(--border))',
              }}
            >
              <div
                className="p-4 border-b flex items-center gap-3"
                style={{
                  borderColor: 'rgb(var(--border))',
                  background: 'linear-gradient(135deg, rgb(var(--accent)/0.1), transparent)',
                }}
              >
                <div
                  className="p-2.5 rounded-xl"
                  style={{ backgroundColor: 'rgb(var(--accent)/0.15)' }}
                >
                  <Sparkles className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
                </div>
                <div>
                  <h3 className="font-semibold" style={{ color: 'rgb(var(--text-primary))' }}>
                    AI Анализ
                  </h3>
                  <p className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                    Умные рекомендации
                  </p>
                </div>
              </div>
              <div className="p-4 max-h-[calc(100vh-220px)] overflow-y-auto">
                {analyzing ? (
                  <div className="flex flex-col items-center justify-center py-16">
                    <div className="relative mb-6">
                      <div
                        className="h-20 w-20 rounded-full border-4 animate-spin"
                        style={{
                          borderColor: 'rgb(var(--border))',
                          borderTopColor: 'rgb(var(--accent))',
                        }}
                      />
                      <div className="absolute inset-0 flex items-center justify-center">
                        <Sparkles
                          className="h-8 w-8 animate-pulse"
                          style={{ color: 'rgb(var(--accent))' }}
                        />
                      </div>
                    </div>
                    <p className="font-medium mb-1" style={{ color: 'rgb(var(--text-primary))' }}>
                      Анализирую...
                    </p>
                    <p className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                      Обычно это занимает 5-10 секунд
                    </p>
                  </div>
                ) : analysis ? (
                  <div className="prose prose-sm max-w-none">
                    <ReactMarkdown
                      components={{
                        h1: ({ children }) => (
                          <h1
                            className="text-xl font-bold mt-5 mb-3"
                            style={{ color: 'rgb(var(--text-primary))' }}
                          >
                            {children}
                          </h1>
                        ),
                        h2: ({ children }) => (
                          <h2
                            className="text-lg font-bold mt-5 mb-2"
                            style={{ color: 'rgb(var(--text-primary))' }}
                          >
                            {children}
                          </h2>
                        ),
                        h3: ({ children }) => (
                          <h3
                            className="text-base font-semibold mt-4 mb-2"
                            style={{ color: 'rgb(var(--text-primary))' }}
                          >
                            {children}
                          </h3>
                        ),
                        p: ({ children }) => (
                          <p
                            className="mb-3 leading-relaxed text-sm"
                            style={{ color: 'rgb(var(--text-muted))' }}
                          >
                            {children}
                          </p>
                        ),
                        ul: ({ children }) => (
                          <ul
                            className="mb-3 space-y-1.5 text-sm"
                            style={{ color: 'rgb(var(--text-muted))' }}
                          >
                            {children}
                          </ul>
                        ),
                        ol: ({ children }) => (
                          <ol
                            className="mb-3 space-y-1.5 text-sm list-decimal list-inside"
                            style={{ color: 'rgb(var(--text-muted))' }}
                          >
                            {children}
                          </ol>
                        ),
                        li: ({ children }) => (
                          <li className="flex gap-2">
                            <span style={{ color: 'rgb(var(--accent))' }}>•</span>
                            <span>{children}</span>
                          </li>
                        ),
                        strong: ({ children }) => (
                          <strong
                            className="font-semibold"
                            style={{ color: 'rgb(var(--text-primary))' }}
                          >
                            {children}
                          </strong>
                        ),
                        em: ({ children }) => (
                          <em style={{ color: 'rgb(var(--accent))' }}>{children}</em>
                        ),
                      }}
                    >
                      {analysis}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <div
                      className="w-20 h-20 rounded-2xl mx-auto mb-5 flex items-center justify-center"
                      style={{
                        background:
                          'linear-gradient(135deg, rgb(var(--accent)/0.1), rgb(var(--accent)/0.2))',
                      }}
                    >
                      <Sparkles className="h-10 w-10" style={{ color: 'rgb(var(--accent))' }} />
                    </div>
                    <p className="font-semibold mb-2" style={{ color: 'rgb(var(--text-primary))' }}>
                      Получите AI-рекомендации
                    </p>
                    <p className="text-sm mb-5 px-4" style={{ color: 'rgb(var(--text-muted))' }}>
                      Искусственный интеллект проанализирует вакансии и подскажет лучший выбор
                    </p>
                    <Button
                      onClick={handleAnalyze}
                      disabled={vacancies.length < MIN_VACANCIES}
                      className="text-white w-full"
                      style={{
                        background:
                          'linear-gradient(135deg, rgb(var(--button-from)), rgb(var(--button-to)))',
                      }}
                    >
                      <Sparkles className="h-4 w-4 mr-2" />
                      Запустить анализ
                    </Button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
