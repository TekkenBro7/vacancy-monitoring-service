import { useState, useEffect, useCallback } from 'react';
import { GitCompare, Plus, Check, Loader2, FolderPlus, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
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

export default function AddToComparisonModal({ isOpen, onClose, vacancy, onSuccess }) {
  const notification = useNotification();
  const [comparisons, setComparisons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newComparisonName, setNewComparisonName] = useState('');
  const [creating, setCreating] = useState(false);

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

  useEffect(() => {
    if (isOpen) {
      loadComparisons();
    }
  }, [isOpen, loadComparisons]);

  const handleAddToComparison = async (comparison) => {
    if (comparison.vacancies_count >= MAX_VACANCIES_PER_COMPARISON) {
      notification.warning(
        'Лимит достигнут',
        `В сравнении уже ${MAX_VACANCIES_PER_COMPARISON} вакансий`
      );
      return;
    }

    if (comparison.vacancy_ids?.includes(vacancy.id)) {
      notification.info('Уже добавлено', 'Эта вакансия уже есть в сравнении');
      return;
    }

    setAdding(comparison.id);
    try {
      await ComparisonService.addVacancy(comparison.id, vacancy.id);
      notification.success('Добавлено', `Вакансия добавлена в "${comparison.name}"`);
      onSuccess?.();
      onClose();
    } catch (error) {
      const message = error?.response?.data?.detail || 'Не удалось добавить вакансию';
      notification.error('Ошибка', message);
    } finally {
      setAdding(null);
    }
  };

  const handleCreateComparison = async () => {
    if (!newComparisonName.trim()) {
      notification.warning('Внимание', 'Введите название сравнения');
      return;
    }

    setCreating(true);
    try {
      const newComparison = await ComparisonService.createComparison(newComparisonName.trim());
      await ComparisonService.addVacancy(newComparison.id, vacancy.id);
      notification.success(
        'Создано',
        `Сравнение "${newComparisonName}" создано и вакансия добавлена`
      );
      setNewComparisonName('');
      setShowCreateForm(false);
      onSuccess?.();
      onClose();
    } catch (error) {
      const message = error?.response?.data?.detail || 'Не удалось создать сравнение';
      notification.error('Ошибка', message);
    } finally {
      setCreating(false);
    }
  };

  const isVacancyInComparison = (comparison) => {
    return comparison.vacancy_ids?.includes(vacancy?.id);
  };

  const isComparisonFull = (comparison) => {
    return comparison.vacancies_count >= MAX_VACANCIES_PER_COMPARISON;
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent
        className="border overflow-hidden"
        style={{
          backgroundColor: 'rgb(var(--bg-header))',
          borderColor: 'rgb(var(--border))',
          maxWidth: '480px',
        }}
      >
        <DialogHeader>
          <div className="mx-auto mb-4 h-16 w-16 rounded-2xl bg-gradient-to-br from-purple-500 to-indigo-500 flex items-center justify-center shadow-xl shadow-purple-500/30">
            <GitCompare className="h-7 w-7 text-white" />
          </div>
          <DialogTitle
            className="text-center text-xl"
            style={{ color: 'rgb(var(--text-primary))' }}
          >
            Добавить в сравнение
          </DialogTitle>
          <DialogDescription className="text-center">
            Выберите сравнение или создайте новое
          </DialogDescription>
        </DialogHeader>

        <div className="py-4 space-y-4">
          <div
            className="p-3 rounded-xl border"
            style={{
              backgroundColor: 'rgb(var(--bg-header-muted)/0.5)',
              borderColor: 'rgb(var(--border))',
            }}
          >
            <div
              className="text-sm font-medium truncate"
              style={{ color: 'rgb(var(--text-primary))' }}
            >
              {vacancy?.title}
            </div>
            <div className="text-xs truncate" style={{ color: 'rgb(var(--text-muted))' }}>
              {vacancy?.company?.name || 'Компания не указана'}
            </div>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin" style={{ color: 'rgb(var(--accent))' }} />
            </div>
          ) : (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {comparisons.length === 0 && !showCreateForm ? (
                <div className="text-center py-8" style={{ color: 'rgb(var(--text-muted))' }}>
                  <GitCompare className="h-12 w-12 mx-auto mb-3 opacity-30" />
                  <p className="text-sm">У вас пока нет сравнений</p>
                  <p className="text-xs mt-1">Создайте первое сравнение</p>
                </div>
              ) : (
                comparisons.map((comparison) => {
                  const isInComparison = isVacancyInComparison(comparison);
                  const isFull = isComparisonFull(comparison);
                  const isDisabled = isInComparison || isFull;

                  return (
                    <button
                      key={comparison.id}
                      onClick={() => !isDisabled && handleAddToComparison(comparison)}
                      disabled={isDisabled || adding === comparison.id}
                      className={`w-full flex items-center gap-3 p-3 rounded-xl border transition-all duration-200 ${
                        isDisabled
                          ? 'opacity-50 cursor-not-allowed'
                          : 'hover:scale-[1.02] hover:shadow-md'
                      }`}
                      style={{
                        backgroundColor: isInComparison
                          ? 'rgb(var(--accent)/0.1)'
                          : 'rgb(var(--bg-header-muted)/0.5)',
                        borderColor: isInComparison
                          ? 'rgb(var(--accent)/0.3)'
                          : 'rgb(var(--border))',
                      }}
                    >
                      <div
                        className="h-10 w-10 rounded-xl flex items-center justify-center flex-shrink-0"
                        style={{
                          background: isInComparison
                            ? 'linear-gradient(135deg, rgb(var(--accent)), rgb(var(--accent)/0.8))'
                            : 'linear-gradient(135deg, rgb(var(--accent)/0.2), rgb(var(--accent)/0.1))',
                        }}
                      >
                        {isInComparison ? (
                          <Check className="h-5 w-5 text-white" />
                        ) : (
                          <GitCompare className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
                        )}
                      </div>

                      <div className="flex-1 text-left min-w-0">
                        <div
                          className="font-medium text-sm truncate"
                          style={{ color: 'rgb(var(--text-primary))' }}
                        >
                          {comparison.name}
                        </div>
                        <div
                          className="text-xs flex items-center gap-2"
                          style={{ color: 'rgb(var(--text-muted))' }}
                        >
                          <span>
                            {comparison.vacancies_count} / {MAX_VACANCIES_PER_COMPARISON} вакансий
                          </span>
                          {isFull && (
                            <span
                              className="px-1.5 py-0.5 rounded text-[10px]"
                              style={{
                                backgroundColor: 'rgb(239, 68, 68, 0.1)',
                                color: 'rgb(239, 68, 68)',
                              }}
                            >
                              Заполнено
                            </span>
                          )}
                          {isInComparison && (
                            <span
                              className="px-1.5 py-0.5 rounded text-[10px]"
                              style={{
                                backgroundColor: 'rgb(var(--accent)/0.1)',
                                color: 'rgb(var(--accent))',
                              }}
                            >
                              Уже добавлено
                            </span>
                          )}
                        </div>
                      </div>

                      {adding === comparison.id ? (
                        <Loader2
                          className="h-5 w-5 animate-spin"
                          style={{ color: 'rgb(var(--accent))' }}
                        />
                      ) : (
                        !isDisabled && (
                          <Plus className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
                        )
                      )}
                    </button>
                  );
                })
              )}
            </div>
          )}

          {showCreateForm ? (
            <div
              className="p-4 rounded-xl border space-y-3"
              style={{
                backgroundColor: 'rgb(var(--bg-header-muted)/0.5)',
                borderColor: 'rgb(var(--accent)/0.3)',
              }}
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium" style={{ color: 'rgb(var(--text-primary))' }}>
                  Новое сравнение
                </span>
                <button
                  onClick={() => {
                    setShowCreateForm(false);
                    setNewComparisonName('');
                  }}
                  className="p-1 rounded-lg hover:bg-black/10 transition-colors"
                >
                  <X className="h-4 w-4" style={{ color: 'rgb(var(--text-muted))' }} />
                </button>
              </div>
              <Input
                value={newComparisonName}
                onChange={(e) => setNewComparisonName(e.target.value)}
                placeholder="Название сравнения..."
                className="h-10"
                style={{
                  backgroundColor: 'rgb(var(--bg-header))',
                  borderColor: 'rgb(var(--border))',
                  color: 'rgb(var(--text-primary))',
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleCreateComparison();
                  }
                }}
              />
              <Button
                onClick={handleCreateComparison}
                disabled={creating || !newComparisonName.trim()}
                className="w-full h-10 text-white"
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
                Создать и добавить
              </Button>
            </div>
          ) : (
            <Button
              onClick={() => setShowCreateForm(true)}
              variant="outline"
              className="w-full h-11 border-dashed"
              style={{
                borderColor: 'rgb(var(--border))',
                color: 'rgb(var(--text-primary))',
              }}
            >
              <FolderPlus className="h-4 w-4 mr-2" style={{ color: 'rgb(var(--accent))' }} />
              Создать новое сравнение
            </Button>
          )}
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={onClose}
            className="w-full h-11"
            style={{
              borderColor: 'rgb(var(--border))',
              color: 'rgb(var(--text-primary))',
            }}
          >
            Закрыть
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
