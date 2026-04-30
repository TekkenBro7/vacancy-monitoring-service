import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  MoreVertical,
  Edit2,
  Trash2,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
  Loader2,
  Building,
  MapPin,
  Eye,
  Filter,
  X,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import VacancyService from '@/api/services/VacancyService';
import useNotification from '@/hooks/useNotification';
import VacancyEditModal from '@/components/vacancies/VacancyEditModal';

const ITEMS_PER_PAGE = 15;

export default function AdminVacanciesPage() {
  const notification = useNotification();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [vacancies, setVacancies] = useState([]);
  const [totalItems, setTotalItems] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedVacancy, setSelectedVacancy] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const fetchVacancies = useCallback(async () => {
    setLoading(true);
    try {
      const params = {
        page: currentPage,
        page_size: ITEMS_PER_PAGE,
        include_filters: false,
      };

      if (searchQuery.trim()) {
        params.search = searchQuery.trim();
      }

      if (statusFilter === 'active') {
        params.is_active = true;
      } else if (statusFilter === 'inactive') {
        params.is_active = false;
      }

      const data = await VacancyService.searchVacancies(params);
      setVacancies(data.items || []);
      setTotalItems(data.pagination?.total_items || 0);
      setTotalPages(data.pagination?.total_pages || 0);
    } catch (err) {
      console.error(err);
      notification.error('Ошибка', 'Не удалось загрузить вакансии');
    } finally {
      setLoading(false);
    }
  }, [currentPage, searchQuery, statusFilter, notification]);

  useEffect(() => {
    fetchVacancies();
  }, [fetchVacancies]);

  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchVacancies();
  };

  const openEditModal = (vacancy) => {
    setSelectedVacancy(vacancy);
    setIsEditModalOpen(true);
  };

  const openDeleteModal = (vacancy) => {
    setSelectedVacancy(vacancy);
    setIsDeleteModalOpen(true);
  };

  const handleDelete = async () => {
    if (!selectedVacancy) return;
    setDeleting(true);
    try {
      await VacancyService.deleteVacancy(selectedVacancy.id);
      notification.success('Успешно', 'Вакансия удалена');
      setIsDeleteModalOpen(false);
      setSelectedVacancy(null);
      fetchVacancies();
    } catch (err) {
      const message = err.response?.data?.detail || 'Ошибка при удалении вакансии';
      notification.error('Ошибка', message);
    } finally {
      setDeleting(false);
    }
  };

  const handleEditSuccess = () => {
    setIsEditModalOpen(false);
    setSelectedVacancy(null);
    fetchVacancies();
    notification.success('Успешно', 'Вакансия обновлена');
  };

  const formatSalary = (from, to, currency) => {
    const symbol = currency?.symbol || '₽';
    if (!from && !to) return 'Не указана';
    if (from && !to) return `от ${from.toLocaleString()} ${symbol}`;
    if (!from && to) return `до ${to.toLocaleString()} ${symbol}`;
    return `${from.toLocaleString()} - ${to.toLocaleString()} ${symbol}`;
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold" style={{ color: 'rgb(var(--text-primary))' }}>
            Вакансии
          </h1>
          <p style={{ color: 'rgb(var(--text-muted))' }}>
            Управление вакансиями • {totalItems.toLocaleString()} записей
          </p>
        </div>
      </div>

      <Card
        className="backdrop-blur-sm border"
        style={{
          backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
          borderColor: 'rgb(var(--border))',
        }}
      >
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <form onSubmit={handleSearch} className="relative flex-1">
              <Search
                className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4"
                style={{ color: 'rgb(var(--text-muted))' }}
              />
              <Input
                type="search"
                placeholder="Поиск по названию или описанию..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 h-11"
                style={{
                  backgroundColor: 'rgb(var(--bg-header-muted))',
                  borderColor: 'rgb(var(--border))',
                  color: 'rgb(var(--text-primary))',
                }}
              />
            </form>
            <div className="flex gap-2 flex-wrap">
              {['all', 'active', 'inactive'].map((status) => (
                <Button
                  key={status}
                  variant={statusFilter === status ? 'default' : 'outline'}
                  onClick={() => {
                    setStatusFilter(status);
                    setCurrentPage(1);
                  }}
                  className={`transition-all duration-300 hover:scale-105 active:scale-95 ${statusFilter === status ? 'text-white' : ''}`}
                  style={
                    statusFilter === status
                      ? {
                          background:
                            'linear-gradient(to right, rgb(var(--button-from)), rgb(var(--button-to)))',
                        }
                      : {
                          borderColor: 'rgb(var(--border))',
                          color: 'rgb(var(--text-primary))',
                          backgroundColor: 'rgb(var(--bg-header-muted))',
                        }
                  }
                >
                  {status === 'all' ? 'Все' : status === 'active' ? 'Активные' : 'Неактивные'}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      <Card
        className="backdrop-blur-sm border"
        style={{
          backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
          borderColor: 'rgb(var(--border))',
        }}
      >
        <CardHeader>
          <CardTitle style={{ color: 'rgb(var(--text-primary))' }}>Список вакансий</CardTitle>
          <CardDescription>
            Страница {currentPage} из {totalPages}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin" style={{ color: 'rgb(var(--accent))' }} />
            </div>
          ) : vacancies.length === 0 ? (
            <div className="text-center py-12">
              <p style={{ color: 'rgb(var(--text-muted))' }}>Вакансии не найдены</p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b" style={{ borderColor: 'rgb(var(--border))' }}>
                      <th
                        className="text-left py-3 px-4 text-sm font-medium"
                        style={{ color: 'rgb(var(--text-muted))' }}
                      >
                        Вакансия
                      </th>
                      <th
                        className="text-left py-3 px-4 text-sm font-medium hidden lg:table-cell"
                        style={{ color: 'rgb(var(--text-muted))' }}
                      >
                        Компания
                      </th>
                      <th
                        className="text-left py-3 px-4 text-sm font-medium hidden md:table-cell"
                        style={{ color: 'rgb(var(--text-muted))' }}
                      >
                        Зарплата
                      </th>
                      <th
                        className="text-left py-3 px-4 text-sm font-medium hidden xl:table-cell"
                        style={{ color: 'rgb(var(--text-muted))' }}
                      >
                        Источник
                      </th>
                      <th
                        className="text-center py-3 px-4 text-sm font-medium"
                        style={{ color: 'rgb(var(--text-muted))' }}
                      >
                        Статус
                      </th>
                      <th
                        className="text-right py-3 px-4 text-sm font-medium"
                        style={{ color: 'rgb(var(--text-muted))' }}
                      >
                        Действия
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {vacancies.map((vacancy) => (
                      <tr
                        key={vacancy.id}
                        className="border-b transition-all duration-200 hover:bg-[rgb(var(--bg-header-muted))]"
                        style={{ borderColor: 'rgb(var(--border)/0.5)' }}
                      >
                        <td className="py-4 px-4">
                          <div className="max-w-xs">
                            <div
                              className="font-medium truncate cursor-pointer hover:underline"
                              style={{ color: 'rgb(var(--text-primary))' }}
                              onClick={() => navigate(`/vacancies/${vacancy.id}`)}
                            >
                              {vacancy.title}
                            </div>
                            <div className="flex items-center gap-2 mt-1">
                              {vacancy.location && (
                                <span
                                  className="text-xs flex items-center gap-1"
                                  style={{ color: 'rgb(var(--text-muted))' }}
                                >
                                  <MapPin className="h-3 w-3" />
                                  {vacancy.location.name}
                                </span>
                              )}
                              {vacancy.is_remote && (
                                <Badge
                                  className="text-[10px] px-1.5 py-0"
                                  style={{
                                    backgroundColor: 'rgb(var(--accent)/0.1)',
                                    color: 'rgb(var(--accent))',
                                    border: '1px solid rgb(var(--accent)/0.3)',
                                  }}
                                >
                                  Remote
                                </Badge>
                              )}
                            </div>
                          </div>
                        </td>
                        <td className="py-4 px-4 hidden lg:table-cell">
                          <div className="flex items-center gap-2">
                            <Building
                              className="h-4 w-4 flex-shrink-0"
                              style={{ color: 'rgb(var(--text-muted))' }}
                            />
                            <span
                              className="text-sm truncate max-w-[150px]"
                              style={{ color: 'rgb(var(--text-primary))' }}
                            >
                              {vacancy.company?.name || '—'}
                            </span>
                          </div>
                        </td>
                        <td className="py-4 px-4 hidden md:table-cell">
                          <span
                            className="text-sm font-medium"
                            style={{ color: 'rgb(var(--accent))' }}
                          >
                            {formatSalary(vacancy.salary_from, vacancy.salary_to, vacancy.currency)}
                          </span>
                        </td>
                        <td className="py-4 px-4 hidden xl:table-cell">
                          <span className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                            {vacancy.source?.name || '—'}
                          </span>
                        </td>
                        <td className="py-4 px-4 text-center">
                          <Badge
                            className={
                              vacancy.is_active
                                ? 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30'
                                : 'bg-red-500/15 text-red-600 dark:text-red-400 border-red-500/30'
                            }
                          >
                            {vacancy.is_active ? 'Активна' : 'Неактивна'}
                          </Badge>
                        </td>
                        <td className="py-4 px-4 text-right">
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button
                                variant="ghost"
                                className="h-8 w-8 p-0 transition-all duration-300 hover:scale-110 active:scale-95"
                                style={{ color: 'rgb(var(--text-muted))' }}
                              >
                                <MoreVertical className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent
                              align="end"
                              style={{
                                backgroundColor: 'rgb(var(--bg-header))',
                                borderColor: 'rgb(var(--border))',
                              }}
                            >
                              <DropdownMenuItem
                                className="cursor-pointer"
                                onClick={() => navigate(`/vacancies/${vacancy.id}`)}
                                style={{ color: 'rgb(var(--text-primary))' }}
                              >
                                <Eye className="h-4 w-4 mr-2" />
                                Просмотр
                              </DropdownMenuItem>
                              <DropdownMenuItem
                                className="cursor-pointer"
                                onClick={() => openEditModal(vacancy)}
                                style={{ color: 'rgb(var(--text-primary))' }}
                              >
                                <Edit2 className="h-4 w-4 mr-2" />
                                Редактировать
                              </DropdownMenuItem>
                              {vacancy.vacancy_url && (
                                <DropdownMenuItem
                                  className="cursor-pointer"
                                  onClick={() => window.open(vacancy.vacancy_url, '_blank')}
                                  style={{ color: 'rgb(var(--text-primary))' }}
                                >
                                  <ExternalLink className="h-4 w-4 mr-2" />
                                  Открыть источник
                                </DropdownMenuItem>
                              )}
                              <DropdownMenuItem
                                className="cursor-pointer"
                                onClick={() => openDeleteModal(vacancy)}
                                style={{ color: 'rgb(var(--error-text))' }}
                              >
                                <Trash2 className="h-4 w-4 mr-2" />
                                Удалить
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {totalPages > 1 && (
                <div className="flex items-center justify-between mt-6">
                  <p className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                    Показано {(currentPage - 1) * ITEMS_PER_PAGE + 1}-
                    {Math.min(currentPage * ITEMS_PER_PAGE, totalItems)} из {totalItems}
                  </p>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                      className="transition-all duration-300 hover:scale-110 active:scale-95"
                      style={{
                        borderColor: 'rgb(var(--border))',
                        color: 'rgb(var(--text-muted))',
                        backgroundColor: 'rgb(var(--bg-header-muted))',
                      }}
                    >
                      <ChevronLeft className="h-4 w-4" />
                    </Button>
                    <div className="flex items-center gap-1">
                      {generatePageNumbers(currentPage, totalPages).map((page, idx) =>
                        page === '...' ? (
                          <span
                            key={`ellipsis-${idx}`}
                            className="px-2"
                            style={{ color: 'rgb(var(--text-muted))' }}
                          >
                            ...
                          </span>
                        ) : (
                          <Button
                            key={page}
                            variant={currentPage === page ? 'default' : 'outline'}
                            size="sm"
                            onClick={() => setCurrentPage(page)}
                            className={`transition-all duration-300 hover:scale-110 active:scale-95 ${currentPage === page ? 'text-white' : ''}`}
                            style={
                              currentPage === page
                                ? {
                                    background:
                                      'linear-gradient(to right, rgb(var(--button-from)), rgb(var(--button-to)))',
                                  }
                                : {
                                    borderColor: 'rgb(var(--border))',
                                    color: 'rgb(var(--text-primary))',
                                    backgroundColor: 'rgb(var(--bg-header-muted))',
                                  }
                            }
                          >
                            {page}
                          </Button>
                        )
                      )}
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                      disabled={currentPage === totalPages}
                      className="transition-all duration-300 hover:scale-110 active:scale-95"
                      style={{
                        borderColor: 'rgb(var(--border))',
                        color: 'rgb(var(--text-muted))',
                        backgroundColor: 'rgb(var(--bg-header-muted))',
                      }}
                    >
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>

      {selectedVacancy && (
        <VacancyEditModal
          isOpen={isEditModalOpen}
          onClose={() => {
            setIsEditModalOpen(false);
            setSelectedVacancy(null);
          }}
          vacancy={selectedVacancy}
          onSuccess={handleEditSuccess}
        />
      )}

      <Dialog open={isDeleteModalOpen} onOpenChange={setIsDeleteModalOpen}>
        <DialogContent
          style={{
            backgroundColor: 'rgb(var(--bg-header))',
            borderColor: 'rgb(var(--border))',
          }}
        >
          <DialogHeader>
            <DialogTitle style={{ color: 'rgb(var(--text-primary))' }}>
              Удалить вакансию
            </DialogTitle>
          </DialogHeader>
          <div className="py-4">
            <p style={{ color: 'rgb(var(--text-muted))' }}>
              Вы уверены, что хотите удалить вакансию{' '}
              <span className="font-semibold" style={{ color: 'rgb(var(--text-primary))' }}>
                «{selectedVacancy?.title}»
              </span>
              ? Это действие нельзя отменить. Все связанные комментарии и закладки будут удалены.
            </p>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsDeleteModalOpen(false)}
              disabled={deleting}
              className="transition-all duration-300 hover:scale-105 active:scale-95"
              style={{
                borderColor: 'rgb(var(--border))',
                color: 'rgb(var(--text-primary))',
                backgroundColor: 'rgb(var(--bg-header-muted))',
              }}
            >
              Отмена
            </Button>
            <Button
              onClick={handleDelete}
              disabled={deleting}
              className="text-white bg-red-500 hover:bg-red-600 transition-all duration-300 hover:scale-105 hover:shadow-lg active:scale-95"
            >
              {deleting ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Удаление...
                </span>
              ) : (
                'Удалить'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function generatePageNumbers(current, total) {
  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }

  const pages = [];
  pages.push(1);

  if (current > 3) pages.push('...');

  const start = Math.max(2, current - 1);
  const end = Math.min(total - 1, current + 1);

  for (let i = start; i <= end; i++) {
    pages.push(i);
  }

  if (current < total - 2) pages.push('...');

  pages.push(total);

  return pages;
}
