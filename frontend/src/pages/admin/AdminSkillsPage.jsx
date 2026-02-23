import { useState, useEffect, useCallback } from 'react';
import {
  Search,
  Plus,
  MoreVertical,
  Edit2,
  Trash2,
  ChevronLeft,
  ChevronRight,
  X,
  Loader2,
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
import SkillService from '@/api/services/SkillService';
import useNotification from '@/hooks/useNotification';

const ITEMS_PER_PAGE = 10;

export default function AdminSkillsPage() {
  const notification = useNotification();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [skills, setSkills] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedSkill, setSelectedSkill] = useState(null);
  const [formData, setFormData] = useState({ name: '' });
  const [formError, setFormError] = useState('');

  const fetchSkills = useCallback(async () => {
    setLoading(true);
    try {
      const data = await SkillService.getAll();
      setSkills(data);
    } catch {
      notification.error('Ошибка', 'Не удалось загрузить навыки');
    } finally {
      setLoading(false);
    }
  }, [notification]);

  useEffect(() => {
    fetchSkills();
  }, [fetchSkills]);

  const filteredSkills = skills.filter((skill) =>
    skill.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const totalPages = Math.ceil(filteredSkills.length / ITEMS_PER_PAGE);
  const paginatedSkills = filteredSkills.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

  const openCreateModal = () => {
    setFormData({ name: '' });
    setFormError('');
    setIsCreateModalOpen(true);
  };

  const openEditModal = (skill) => {
    setSelectedSkill(skill);
    setFormData({ name: skill.name });
    setFormError('');
    setIsEditModalOpen(true);
  };

  const openDeleteModal = (skill) => {
    setSelectedSkill(skill);
    setIsDeleteModalOpen(true);
  };

  const validateForm = () => {
    if (!formData.name.trim()) {
      setFormError('Введите название навыка');
      return false;
    }
    if (formData.name.trim().length < 2) {
      setFormError('Название должно быть не менее 2 символов');
      return false;
    }
    if (formData.name.trim().length > 30) {
      setFormError('Название должно быть не более 30 символов');
      return false;
    }
    return true;
  };

  const handleCreate = async () => {
    if (!validateForm()) return;

    setSaving(true);
    try {
      await SkillService.create({ name: formData.name.trim() });
      notification.success('Успешно', 'Навык создан');
      setIsCreateModalOpen(false);
      fetchSkills();
    } catch (err) {
      const message = err.response?.data?.detail || 'Ошибка при создании навыка';
      notification.error('Ошибка', message);
    } finally {
      setSaving(false);
    }
  };

  const handleUpdate = async () => {
    if (!validateForm()) return;

    setSaving(true);
    try {
      await SkillService.update(selectedSkill.id, { name: formData.name.trim() });
      notification.success('Успешно', 'Навык обновлен');
      setIsEditModalOpen(false);
      fetchSkills();
    } catch (err) {
      const message = err.response?.data?.detail || 'Ошибка при обновлении навыка';
      notification.error('Ошибка', message);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    setSaving(true);
    try {
      await SkillService.delete(selectedSkill.id);
      notification.success('Успешно', 'Навык удален');
      setIsDeleteModalOpen(false);
      fetchSkills();
    } catch (err) {
      const message = err.response?.data?.detail || 'Ошибка при удалении навыка';
      notification.error('Ошибка', message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold" style={{ color: 'rgb(var(--text-primary))' }}>
            Навыки
          </h1>
          <p style={{ color: 'rgb(var(--text-muted))' }}>Управление навыками системы</p>
        </div>
        <Button
          onClick={openCreateModal}
          disabled={loading}
          className="text-white transition-all duration-300 hover:scale-105 hover:shadow-lg active:scale-95"
          style={{
            background: 'linear-gradient(to right, rgb(var(--button-from)), rgb(var(--button-to)))',
          }}
        >
          <Plus className="h-4 w-4 mr-2" />
          Добавить навык
        </Button>
      </div>

      <Card
        className="backdrop-blur-sm border"
        style={{
          backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
          borderColor: 'rgb(var(--border))',
        }}
      >
        <CardContent className="p-4">
          <div className="relative">
            <Search
              className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4"
              style={{ color: 'rgb(var(--text-muted))' }}
            />
            <Input
              type="search"
              placeholder="Поиск по названию..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 h-11"
              style={{
                backgroundColor: 'rgb(var(--bg-header-muted))',
                borderColor: 'rgb(var(--border))',
                color: 'rgb(var(--text-primary))',
              }}
            />
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
          <CardTitle style={{ color: 'rgb(var(--text-primary))' }}>Список навыков</CardTitle>
          <CardDescription>
            Всего: {filteredSkills.length} из {skills.length}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin" style={{ color: 'rgb(var(--accent))' }} />
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
                        Название
                      </th>
                      <th
                        className="text-left py-3 px-4 text-sm font-medium hidden md:table-cell"
                        style={{ color: 'rgb(var(--text-muted))' }}
                      >
                        Создан
                      </th>
                      <th
                        className="text-left py-3 px-4 text-sm font-medium hidden lg:table-cell"
                        style={{ color: 'rgb(var(--text-muted))' }}
                      >
                        Обновлен
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
                    {paginatedSkills.map((skill) => (
                      <tr
                        key={skill.id}
                        className="border-b transition-all duration-300 hover:bg-[rgb(var(--bg-header-muted))/50 hover:scale-[1.01] cursor-pointer"
                        style={{ borderColor: 'rgb(var(--border)/0.5)' }}
                      >
                        <td className="py-4 px-4">
                          <div
                            className="font-medium"
                            style={{ color: 'rgb(var(--text-primary))' }}
                          >
                            {skill.name}
                          </div>
                        </td>
                        <td className="py-4 px-4 hidden md:table-cell">
                          <span style={{ color: 'rgb(var(--text-muted))' }}>
                            {new Date(skill.created_at).toLocaleDateString('ru-RU', {
                              day: 'numeric',
                              month: 'long',
                              year: 'numeric',
                            })}
                          </span>
                        </td>
                        <td className="py-4 px-4 hidden lg:table-cell">
                          <span style={{ color: 'rgb(var(--text-muted))' }}>
                            {new Date(skill.updated_at).toLocaleDateString('ru-RU', {
                              day: 'numeric',
                              month: 'long',
                              year: 'numeric',
                            })}
                          </span>
                        </td>
                        <td className="py-4 px-4 text-right">
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button
                                variant="ghost"
                                className="h-8 w-8 p-0 transition-all duration-300 hover:bg-[rgb(var(--accent))/10] hover:scale-110 active:scale-95"
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
                                className="cursor-pointer transition-colors hover:bg-[rgb(var(--bg-header-muted))]"
                                onClick={() => openEditModal(skill)}
                                style={{ color: 'rgb(var(--text-primary))' }}
                              >
                                <Edit2 className="h-4 w-4 mr-2" />
                                Редактировать
                              </DropdownMenuItem>
                              <DropdownMenuItem
                                className="cursor-pointer transition-colors hover:bg-red-500/10 hover:text-red-600 dark:hover:text-red-400"
                                onClick={() => openDeleteModal(skill)}
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
                    {Math.min(currentPage * ITEMS_PER_PAGE, filteredSkills.length)} из{' '}
                    {filteredSkills.length}
                  </p>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                      className="transition-all duration-300 hover:scale-110 active:scale-95 disabled:hover:scale-100"
                      style={{
                        borderColor: 'rgb(var(--border))',
                        color: 'rgb(var(--text-muted))',
                        backgroundColor: 'rgb(var(--bg-header-muted))',
                      }}
                    >
                      <ChevronLeft className="h-4 w-4" />
                    </Button>
                    <div className="flex items-center gap-1">
                      {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
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
                      ))}
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                      disabled={currentPage === totalPages}
                      className="transition-all duration-300 hover:scale-110 active:scale-95 disabled:hover:scale-100"
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

      <Dialog open={isCreateModalOpen} onOpenChange={setIsCreateModalOpen}>
        <DialogContent
          style={{
            backgroundColor: 'rgb(var(--bg-header))',
            borderColor: 'rgb(var(--border))',
          }}
        >
          <DialogHeader>
            <DialogTitle style={{ color: 'rgb(var(--text-primary))' }}>Создать навык</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium" style={{ color: 'rgb(var(--text-primary))' }}>
                Название навыка
              </label>
              <Input
                value={formData.name}
                onChange={(e) => setFormData({ name: e.target.value })}
                placeholder="Например: Python, React, Docker..."
                maxLength={30}
                style={{
                  backgroundColor: 'rgb(var(--bg-header-muted))',
                  borderColor: formError ? 'rgb(var(--error-border))' : 'rgb(var(--border))',
                  color: 'rgb(var(--text-primary))',
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleCreate();
                  }
                }}
              />
              {formError && (
                <p className="text-xs" style={{ color: 'rgb(var(--error-text))' }}>
                  {formError}
                </p>
              )}
              <p className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                Максимум 30 символов. Название должно быть уникальным.
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsCreateModalOpen(false)}
              disabled={saving}
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
              onClick={handleCreate}
              disabled={saving}
              className="text-white transition-all duration-300 hover:scale-105 hover:shadow-lg active:scale-95"
              style={{
                background:
                  'linear-gradient(to right, rgb(var(--button-from)), rgb(var(--button-to)))',
              }}
            >
              {saving ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Создание...
                </span>
              ) : (
                'Создать'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={isEditModalOpen} onOpenChange={setIsEditModalOpen}>
        <DialogContent
          style={{
            backgroundColor: 'rgb(var(--bg-header))',
            borderColor: 'rgb(var(--border))',
          }}
        >
          <DialogHeader>
            <DialogTitle style={{ color: 'rgb(var(--text-primary))' }}>
              Редактировать навык
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium" style={{ color: 'rgb(var(--text-primary))' }}>
                Название навыка
              </label>
              <Input
                value={formData.name}
                onChange={(e) => setFormData({ name: e.target.value })}
                placeholder="Название навыка"
                maxLength={30}
                style={{
                  backgroundColor: 'rgb(var(--bg-header-muted))',
                  borderColor: formError ? 'rgb(var(--error-border))' : 'rgb(var(--border))',
                  color: 'rgb(var(--text-primary))',
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleUpdate();
                  }
                }}
              />
              {formError && (
                <p className="text-xs" style={{ color: 'rgb(var(--error-text))' }}>
                  {formError}
                </p>
              )}
              <p className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                Максимум 30 символов.
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsEditModalOpen(false)}
              disabled={saving}
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
              onClick={handleUpdate}
              disabled={saving}
              className="text-white transition-all duration-300 hover:scale-105 hover:shadow-lg active:scale-95"
              style={{
                background:
                  'linear-gradient(to right, rgb(var(--button-from)), rgb(var(--button-to)))',
              }}
            >
              {saving ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Сохранение...
                </span>
              ) : (
                'Сохранить'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={isDeleteModalOpen} onOpenChange={setIsDeleteModalOpen}>
        <DialogContent
          style={{
            backgroundColor: 'rgb(var(--bg-header))',
            borderColor: 'rgb(var(--border))',
          }}
        >
          <DialogHeader>
            <DialogTitle style={{ color: 'rgb(var(--text-primary))' }}>Удалить навык</DialogTitle>
          </DialogHeader>
          <div className="py-4">
            <p style={{ color: 'rgb(var(--text-muted))' }}>
              Вы уверены, что хотите удалить навык{' '}
              <Badge
                className="mx-1 px-3 py-1"
                style={{
                  backgroundColor: 'rgb(var(--bg-header-muted))',
                  borderColor: 'rgb(var(--border))',
                  color: 'rgb(var(--text-primary))',
                }}
              >
                {selectedSkill?.name}
              </Badge>
              ? Это действие нельзя отменить.
            </p>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsDeleteModalOpen(false)}
              disabled={saving}
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
              disabled={saving}
              className="text-white bg-red-500 hover:bg-red-600 transition-all duration-300 hover:scale-105 hover:shadow-lg active:scale-95"
            >
              {saving ? (
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
