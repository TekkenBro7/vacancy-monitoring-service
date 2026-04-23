import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  GitCompare,
  Plus,
  Trash2,
  Eye,
  Sparkles,
  Loader2,
  FolderOpen,
  ChevronRight,
  Building,
  MapPin,
  DollarSign,
  X,
  AlertCircle,
  Edit2,
  Check,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import ComparisonService from '@/api/services/ComparisonService';
import useNotification from '@/hooks/useNotification';

const MAX_VACANCIES_PER_COMPARISON = 5;
const MIN_VACANCIES_FOR_ANALYSIS = 2;

export default function ComparisonsPage() {
  const navigate = useNavigate();
  const notification = useNotification();

  const [comparisons, setComparisons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedComparison, setSelectedComparison] = useState(null);
  const [comparisonDetail, setComparisonDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);

  const [newComparisonName, setNewComparisonName] = useState('');
  const [creating, setCreating] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const [editingId, setEditingId] = useState(null);
  const [editingName, setEditingName] = useState('');

  const loadComparisons = useCallback(async () => {
    setLoading(true);
    try {
      const data = await ComparisonService.getComparisons();
      setComparisons(data);
    } catch {
      notification.error('Ошибка', 'Не удалось загрузить сравнения');
    } finally {
      setLoading(false);
    }
  }, [notification]);

  const loadComparisonDetail = useCallback(
    async (id) => {
      setDetailLoading(true);
      try {
        const data = await ComparisonService.getComparisonDetail(id);
        setComparisonDetail(data);
        setSelectedComparison(data);
      } catch {
        notification.error('Ошибка', 'Не удалось загрузить детали сравнения');
      } finally {
        setDetailLoading(false);
      }
    },
    [notification]
  );

  useEffect(() => {
    loadComparisons();
  }, [loadComparisons]);

  const handleCreateComparison = async () => {
    if (!newComparisonName.trim()) {
      notification.warning('Внимание', 'Введите название сравнения');
      return;
    }

    setCreating(true);
    try {
      await ComparisonService.createComparison(newComparisonName.trim());
      notification.success('Создано', 'Сравнение успешно создано');
      setNewComparisonName('');
      setCreateModalOpen(false);
      loadComparisons();
    } catch (error) {
      const message = error?.response?.data?.detail || 'Не удалось создать сравнение';
      notification.error('Ошибка', message);
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteComparison = async () => {
    if (!selectedComparison) return;

    setDeleting(true);
    try {
      await ComparisonService.deleteComparison(selectedComparison.id);
      notification.success('Удалено', 'Сравнение удалено');
      setDeleteModalOpen(false);
      setSelectedComparison(null);
      setComparisonDetail(null);
      loadComparisons();
    } catch {
      notification.error('Ошибка', 'Не удалось удалить сравнение');
    } finally {
      setDeleting(false);
    }
  };

  const handleRemoveVacancy = async (vacancyId) => {
    if (!selectedComparison) return;

    try {
      await ComparisonService.removeVacancy(selectedComparison.id, vacancyId);
      notification.success('Удалено', 'Вакансия удалена из сравнения');
      loadComparisonDetail(selectedComparison.id);
      loadComparisons();
    } catch {
      notification.error('Ошибка', 'Не удалось удалить вакансию');
    }
  };

  const handleUpdateName = async (id) => {
    if (!editingName.trim()) {
      setEditingId(null);
      return;
    }

    try {
      await ComparisonService.updateComparison(id, { name: editingName.trim() });
      notification.success('Обновлено', 'Название изменено');
      setEditingId(null);
      loadComparisons();
      if (selectedComparison?.id === id) {
        setSelectedComparison({ ...selectedComparison, name: editingName.trim() });
      }
    } catch {
      notification.error('Ошибка', 'Не удалось обновить название');
    }
  };

  const formatSalary = (from, to, currencyCode) => {
    if (!from && !to) return 'Не указана';
    const parts = [];
    if (from) parts.push(`от ${from.toLocaleString()}`);
    if (to) parts.push(`до ${to.toLocaleString()}`);
    return `${parts.join(' ')} ${currencyCode || ''}`;
  };

  return (
    <div className="min-h-screen py-8 animate-fade-in">
      <div className="container mx-auto px-6">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1
                className="text-3xl font-bold flex items-center gap-3"
                style={{ color: 'rgb(var(--text-primary))' }}
              >
                <GitCompare className="h-8 w-8" style={{ color: 'rgb(var(--accent))' }} />
                Мои сравнения
              </h1>
              <p className="mt-2" style={{ color: 'rgb(var(--text-muted))' }}>
                Сравнивайте вакансии и получайте AI-рекомендации
              </p>
            </div>
            <Button
              onClick={() => setCreateModalOpen(true)}
              className="h-11 px-6 text-white shadow-lg transition-all duration-300 hover:shadow-xl hover:scale-105"
              style={{
                background:
                  'linear-gradient(135deg, rgb(var(--button-from)), rgb(var(--button-to)))',
              }}
            >
              <Plus className="h-5 w-5 mr-2" />
              Новое сравнение
            </Button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1 space-y-4">
              <h2 className="text-lg font-semibold" style={{ color: 'rgb(var(--text-primary))' }}>
                Сравнения
              </h2>

              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2
                    className="h-8 w-8 animate-spin"
                    style={{ color: 'rgb(var(--accent))' }}
                  />
                </div>
              ) : comparisons.length === 0 ? (
                <div
                  className="text-center py-12 rounded-2xl border"
                  style={{
                    backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
                    borderColor: 'rgb(var(--border))',
                  }}
                >
                  <FolderOpen
                    className="h-16 w-16 mx-auto mb-4 opacity-30"
                    style={{ color: 'rgb(var(--text-muted))' }}
                  />
                  <p className="font-medium" style={{ color: 'rgb(var(--text-primary))' }}>
                    Нет сравнений
                  </p>
                  <p className="text-sm mt-1" style={{ color: 'rgb(var(--text-muted))' }}>
                    Создайте первое сравнение
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  {comparisons.map((comparison) => (
                    <div
                      key={comparison.id}
                      onClick={() => loadComparisonDetail(comparison.id)}
                      className={`group p-4 rounded-xl border cursor-pointer transition-all duration-200 hover:shadow-md ${
                        selectedComparison?.id === comparison.id ? 'ring-2' : ''
                      }`}
                      style={{
                        backgroundColor:
                          selectedComparison?.id === comparison.id
                            ? 'rgb(var(--accent)/0.1)'
                            : 'rgb(var(--bg-header-muted)/0.3)',
                        borderColor:
                          selectedComparison?.id === comparison.id
                            ? 'rgb(var(--accent)/0.3)'
                            : 'rgb(var(--border))',
                        '--tw-ring-color': 'rgb(var(--accent)/0.5)',
                      }}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1 min-w-0">
                          {editingId === comparison.id ? (
                            <div className="flex items-center gap-2">
                              <Input
                                value={editingName}
                                onChange={(e) => setEditingName(e.target.value)}
                                className="h-8 text-sm"
                                style={{
                                  backgroundColor: 'rgb(var(--bg-header))',
                                  borderColor: 'rgb(var(--border))',
                                  color: 'rgb(var(--text-primary))',
                                }}
                                onClick={(e) => e.stopPropagation()}
                                onKeyDown={(e) => {
                                  if (e.key === 'Enter') handleUpdateName(comparison.id);
                                  if (e.key === 'Escape') setEditingId(null);
                                }}
                                autoFocus
                              />
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleUpdateName(comparison.id);
                                }}
                                className="p-1.5 rounded-lg hover:bg-black/10"
                              >
                                <Check
                                  className="h-4 w-4"
                                  style={{ color: 'rgb(var(--accent))' }}
                                />
                              </button>
                            </div>
                          ) : (
                            <div className="flex items-center gap-2">
                              <span
                                className="font-medium truncate"
                                style={{ color: 'rgb(var(--text-primary))' }}
                              >
                                {comparison.name}
                              </span>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setEditingId(comparison.id);
                                  setEditingName(comparison.name);
                                }}
                                className="p-1 rounded-lg opacity-0 group-hover:opacity-100 hover:bg-black/10 transition-all"
                              >
                                <Edit2
                                  className="h-3.5 w-3.5"
                                  style={{ color: 'rgb(var(--text-muted))' }}
                                />
                              </button>
                            </div>
                          )}
                          <div className="flex items-center gap-2 mt-1">
                            <Badge
                              className="text-xs"
                              style={{
                                backgroundColor:
                                  comparison.vacancies_count >= MIN_VACANCIES_FOR_ANALYSIS
                                    ? 'rgb(var(--accent)/0.1)'
                                    : 'rgb(var(--border)/0.3)',
                                color:
                                  comparison.vacancies_count >= MIN_VACANCIES_FOR_ANALYSIS
                                    ? 'rgb(var(--accent))'
                                    : 'rgb(var(--text-muted))',
                              }}
                            >
                              {comparison.vacancies_count} / {MAX_VACANCIES_PER_COMPARISON}
                            </Badge>
                            {comparison.vacancies_count >= MIN_VACANCIES_FOR_ANALYSIS && (
                              <Badge
                                className="text-xs"
                                style={{
                                  backgroundColor: 'rgb(34, 197, 94, 0.1)',
                                  color: 'rgb(34, 197, 94)',
                                }}
                              >
                                Готово к анализу
                              </Badge>
                            )}
                          </div>
                        </div>
                        <ChevronRight
                          className="h-5 w-5 flex-shrink-0 transition-transform group-hover:translate-x-1"
                          style={{ color: 'rgb(var(--text-muted))' }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="lg:col-span-2">
              {detailLoading ? (
                <div
                  className="flex items-center justify-center py-24 rounded-2xl border"
                  style={{
                    backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
                    borderColor: 'rgb(var(--border))',
                  }}
                >
                  <Loader2
                    className="h-8 w-8 animate-spin"
                    style={{ color: 'rgb(var(--accent))' }}
                  />
                </div>
              ) : !selectedComparison ? (
                <div
                  className="flex flex-col items-center justify-center py-24 rounded-2xl border"
                  style={{
                    backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
                    borderColor: 'rgb(var(--border))',
                  }}
                >
                  <Eye
                    className="h-16 w-16 mb-4 opacity-30"
                    style={{ color: 'rgb(var(--text-muted))' }}
                  />
                  <p className="font-medium" style={{ color: 'rgb(var(--text-primary))' }}>
                    Выберите сравнение
                  </p>
                  <p className="text-sm mt-1" style={{ color: 'rgb(var(--text-muted))' }}>
                    Нажмите на сравнение слева, чтобы увидеть детали
                  </p>
                </div>
              ) : (
                <div
                  className="rounded-2xl border overflow-hidden"
                  style={{
                    backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
                    borderColor: 'rgb(var(--border))',
                  }}
                >
                  <div className="p-6 border-b" style={{ borderColor: 'rgb(var(--border))' }}>
                    <div className="flex items-center justify-between">
                      <div>
                        <h2
                          className="text-xl font-bold"
                          style={{ color: 'rgb(var(--text-primary))' }}
                        >
                          {selectedComparison.name}
                        </h2>
                        <p className="text-sm mt-1" style={{ color: 'rgb(var(--text-muted))' }}>
                          {comparisonDetail?.vacancies?.length || 0} вакансий
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setDeleteModalOpen(true)}
                          className="text-red-500 hover:text-red-600 hover:bg-red-500/10"
                          style={{ borderColor: 'rgb(239, 68, 68, 0.3)' }}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                        <Button
                          size="sm"
                          onClick={() => navigate(`/comparisons/${selectedComparison.id}`)}
                          className="text-white"
                          style={{
                            background:
                              'linear-gradient(135deg, rgb(var(--button-from)), rgb(var(--button-to)))',
                          }}
                        >
                          <Sparkles className="h-4 w-4 mr-2" />
                          Открыть сравнение
                        </Button>
                      </div>
                    </div>

                    {(comparisonDetail?.vacancies?.length || 0) < MIN_VACANCIES_FOR_ANALYSIS && (
                      <div
                        className="mt-4 p-3 rounded-xl flex items-center gap-3"
                        style={{ backgroundColor: 'rgb(var(--accent)/0.1)' }}
                      >
                        <AlertCircle className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
                        <span className="text-sm" style={{ color: 'rgb(var(--text-primary))' }}>
                          Добавьте ещё{' '}
                          {MIN_VACANCIES_FOR_ANALYSIS - (comparisonDetail?.vacancies?.length || 0)}{' '}
                          вакансию для AI-анализа
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="p-6">
                    {!comparisonDetail?.vacancies?.length ? (
                      <div className="text-center py-12">
                        <FolderOpen
                          className="h-12 w-12 mx-auto mb-3 opacity-30"
                          style={{ color: 'rgb(var(--text-muted))' }}
                        />
                        <p style={{ color: 'rgb(var(--text-muted))' }}>Нет вакансий в сравнении</p>
                        <Button
                          variant="link"
                          onClick={() => navigate('/vacancies')}
                          style={{ color: 'rgb(var(--accent))' }}
                        >
                          Перейти к вакансиям
                        </Button>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {comparisonDetail.vacancies.map((vacancy, index) => (
                          <div
                            key={vacancy.id}
                            className="group p-4 rounded-xl border transition-all duration-200 hover:shadow-md animate-fade-in"
                            style={{
                              backgroundColor: 'rgb(var(--bg-header-muted)/0.5)',
                              borderColor: 'rgb(var(--border))',
                              animationDelay: `${index * 50}ms`,
                            }}
                          >
                            <div className="flex items-start justify-between gap-4">
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-2">
                                  <span
                                    className="text-xs font-medium px-2 py-0.5 rounded-full"
                                    style={{
                                      backgroundColor: 'rgb(var(--accent)/0.1)',
                                      color: 'rgb(var(--accent))',
                                    }}
                                  >
                                    #{index + 1}
                                  </span>
                                  <h3
                                    className="font-semibold truncate cursor-pointer hover:underline"
                                    style={{ color: 'rgb(var(--text-primary))' }}
                                    onClick={() => navigate(`/vacancies/${vacancy.id}`)}
                                  >
                                    {vacancy.title}
                                  </h3>
                                </div>

                                <div
                                  className="flex flex-wrap items-center gap-3 text-sm"
                                  style={{ color: 'rgb(var(--text-muted))' }}
                                >
                                  {vacancy.company_name && (
                                    <div className="flex items-center gap-1.5">
                                      <Building className="h-4 w-4" />
                                      <span>{vacancy.company_name}</span>
                                    </div>
                                  )}
                                  {(vacancy.city_name || vacancy.is_remote) && (
                                    <div className="flex items-center gap-1.5">
                                      <MapPin className="h-4 w-4" />
                                      <span>
                                        {vacancy.city_name || ''}
                                        {vacancy.is_remote && ' (удалённо)'}
                                      </span>
                                    </div>
                                  )}
                                  <div className="flex items-center gap-1.5">
                                    <DollarSign
                                      className="h-4 w-4"
                                      style={{ color: 'rgb(var(--accent))' }}
                                    />
                                    <span style={{ color: 'rgb(var(--accent))' }}>
                                      {formatSalary(
                                        vacancy.salary_from,
                                        vacancy.salary_to,
                                        vacancy.currency_code
                                      )}
                                    </span>
                                  </div>
                                </div>

                                {vacancy.skills?.length > 0 && (
                                  <div className="flex flex-wrap gap-1.5 mt-3">
                                    {vacancy.skills.slice(0, 5).map((skill, idx) => (
                                      <Badge
                                        key={idx}
                                        className="text-xs"
                                        style={{
                                          backgroundColor: 'rgb(var(--accent)/0.1)',
                                          color: 'rgb(var(--text-primary))',
                                        }}
                                      >
                                        {skill}
                                      </Badge>
                                    ))}
                                    {vacancy.skills.length > 5 && (
                                      <Badge
                                        className="text-xs"
                                        style={{
                                          backgroundColor: 'rgb(var(--border)/0.5)',
                                          color: 'rgb(var(--text-muted))',
                                        }}
                                      >
                                        +{vacancy.skills.length - 5}
                                      </Badge>
                                    )}
                                  </div>
                                )}
                              </div>

                              <button
                                onClick={() => handleRemoveVacancy(vacancy.id)}
                                className="p-2 rounded-lg opacity-0 group-hover:opacity-100 hover:bg-red-500/10 transition-all"
                              >
                                <X className="h-4 w-4" style={{ color: 'rgb(239, 68, 68)' }} />
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <Dialog open={createModalOpen} onOpenChange={setCreateModalOpen}>
        <DialogContent
          className="border"
          style={{
            backgroundColor: 'rgb(var(--bg-header))',
            borderColor: 'rgb(var(--border))',
            maxWidth: '420px',
          }}
        >
          <DialogHeader>
            <div className="mx-auto mb-4 h-16 w-16 rounded-2xl bg-gradient-to-br from-purple-500 to-indigo-500 flex items-center justify-center shadow-xl shadow-purple-500/30">
              <Plus className="h-7 w-7 text-white" />
            </div>
            <DialogTitle
              className="text-center text-xl"
              style={{ color: 'rgb(var(--text-primary))' }}
            >
              Новое сравнение
            </DialogTitle>
            <DialogDescription className="text-center">
              Создайте сравнение для анализа вакансий
            </DialogDescription>
          </DialogHeader>

          <div className="py-4">
            <Input
              value={newComparisonName}
              onChange={(e) => setNewComparisonName(e.target.value)}
              placeholder="Название сравнения..."
              className="h-12"
              style={{
                backgroundColor: 'rgb(var(--bg-header-muted))',
                borderColor: 'rgb(var(--border))',
                color: 'rgb(var(--text-primary))',
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleCreateComparison();
              }}
            />
          </div>

          <DialogFooter className="gap-2">
            <Button
              variant="outline"
              onClick={() => setCreateModalOpen(false)}
              className="flex-1 h-11"
              style={{
                borderColor: 'rgb(var(--border))',
                color: 'rgb(var(--text-primary))',
              }}
            >
              Отмена
            </Button>
            <Button
              onClick={handleCreateComparison}
              disabled={creating || !newComparisonName.trim()}
              className="flex-1 h-11 text-white"
              style={{
                background:
                  'linear-gradient(135deg, rgb(var(--button-from)), rgb(var(--button-to)))',
              }}
            >
              {creating ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <Plus className="h-4 w-4 mr-2" />
              )}
              Создать
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={deleteModalOpen} onOpenChange={setDeleteModalOpen}>
        <DialogContent
          className="border"
          style={{
            backgroundColor: 'rgb(var(--bg-header))',
            borderColor: 'rgb(var(--border))',
            maxWidth: '420px',
          }}
        >
          <DialogHeader>
            <div className="mx-auto mb-4 h-16 w-16 rounded-2xl bg-gradient-to-br from-red-500 to-orange-500 flex items-center justify-center shadow-xl shadow-red-500/30">
              <Trash2 className="h-7 w-7 text-white" />
            </div>
            <DialogTitle
              className="text-center text-xl"
              style={{ color: 'rgb(var(--text-primary))' }}
            >
              Удалить сравнение?
            </DialogTitle>
            <DialogDescription className="text-center">
              Сравнение «{selectedComparison?.name}» будет удалено безвозвратно
            </DialogDescription>
          </DialogHeader>

          <DialogFooter className="gap-2 pt-4">
            <Button
              variant="outline"
              onClick={() => setDeleteModalOpen(false)}
              className="flex-1 h-11"
              style={{
                borderColor: 'rgb(var(--border))',
                color: 'rgb(var(--text-primary))',
              }}
            >
              Отмена
            </Button>
            <Button
              onClick={handleDeleteComparison}
              disabled={deleting}
              className="flex-1 h-11 bg-red-500 hover:bg-red-600 text-white"
            >
              {deleting ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <Trash2 className="h-4 w-4 mr-2" />
              )}
              Удалить
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
