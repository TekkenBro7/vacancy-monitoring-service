import { useState, useEffect, useCallback } from 'react';
import {
  Search,
  Plus,
  MoreVertical,
  Edit2,
  Trash2,
  Shield,
  Mail,
  Calendar,
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
import UserService from '@/api/services/UserService';
import RoleService from '@/api/services/RoleService';
import useNotification from '@/hooks/useNotification';

const ITEMS_PER_PAGE = 10;

export default function AdminUsersPage() {
  const notification = useNotification();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRole, setSelectedRole] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    role_id: '',
  });
  const [formErrors, setFormErrors] = useState({});

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    try {
      const data = await UserService.getAll();
      setUsers(data);
    } catch {
      notification.error('Ошибка', 'Не удалось загрузить пользователей');
    } finally {
      setLoading(false);
    }
  }, [notification]);

  const fetchRoles = useCallback(async () => {
    try {
      const data = await RoleService.getAll();
      setRoles(data);
      if (data.length > 0 && !formData.role_id) {
        setFormData((prev) => ({ ...prev, role_id: data[0].id.toString() }));
      }
    } catch {
      notification.error('Ошибка', 'Не удалось загрузить роли');
    }
  }, [notification, formData.role_id]);

  useEffect(() => {
    fetchUsers();
    fetchRoles();
  }, [fetchUsers, fetchRoles]);

  const filteredUsers = users.filter((user) => {
    const matchesSearch =
      user.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.email.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRole = selectedRole === 'all' || user.role_id.toString() === selectedRole;
    return matchesSearch && matchesRole;
  });

  const totalPages = Math.ceil(filteredUsers.length / ITEMS_PER_PAGE);
  const paginatedUsers = filteredUsers.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

  const validateForm = (isEdit = false) => {
    const errors = {};

    if (!formData.username.trim()) {
      errors.username = 'Введите имя пользователя';
    } else if (formData.username.length < 3) {
      errors.username = 'Имя должно быть не менее 3 символов';
    }

    if (!formData.email.trim()) {
      errors.email = 'Введите email';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = 'Введите корректный email';
    }

    if (!isEdit && !formData.password) {
      errors.password = 'Введите пароль';
    } else if (formData.password && formData.password.length < 6) {
      errors.password = 'Пароль должен быть не менее 6 символов';
    }

    if (!formData.role_id) {
      errors.role_id = 'Выберите роль';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const passwordStrength = (password) => {
    if (!password) return { strength: 0, color: 'bg-gray-700' };

    let score = 0;
    if (password.length >= 6) score += 1;
    if (/[A-Z]/.test(password)) score += 1;
    if (/[0-9]/.test(password)) score += 1;
    if (/[^A-Za-z0-9]/.test(password)) score += 1;

    if (score === 0) return { strength: 0, color: 'bg-red-500' };
    if (score === 1) return { strength: 25, color: 'bg-red-500' };
    if (score === 2) return { strength: 50, color: 'bg-amber-500' };
    if (score === 3) return { strength: 75, color: 'bg-blue-500' };
    return { strength: 100, color: 'bg-emerald-500' };
  };

  const openCreateModal = () => {
    setFormData({ username: '', email: '', password: '', role_id: roles[0]?.id.toString() || '' });
    setFormErrors({});
    setIsCreateModalOpen(true);
  };

  const openEditModal = (user) => {
    setSelectedUser(user);
    setFormData({
      username: user.username,
      email: user.email,
      password: '',
      role_id: user.role_id.toString(),
    });
    setFormErrors({});
    setIsEditModalOpen(true);
  };

  const openDeleteModal = (user) => {
    setSelectedUser(user);
    setIsDeleteModalOpen(true);
  };

  const handleCreate = async () => {
    if (!validateForm(false)) return;

    setSaving(true);
    try {
      await UserService.createWithRole({
        ...formData,
        role_id: parseInt(formData.role_id),
      });
      notification.success('Успешно', 'Пользователь создан');
      setIsCreateModalOpen(false);
      fetchUsers();
    } catch (err) {
      const message = err.response?.data?.detail || 'Ошибка при создании пользователя';
      notification.error('Ошибка', message);
    } finally {
      setSaving(false);
    }
  };

  const handleUpdate = async () => {
    if (!validateForm(true)) return;

    setSaving(true);
    try {
      const updateData = {
        username: formData.username,
        email: formData.email,
        role_id: parseInt(formData.role_id),
      };
      if (formData.password) {
        updateData.password = formData.password;
      }
      await UserService.update(selectedUser.id, updateData);
      notification.success('Успешно', 'Пользователь обновлен');
      setIsEditModalOpen(false);
      fetchUsers();
    } catch (err) {
      const message = err.response?.data?.detail || 'Ошибка при обновлении пользователя';
      notification.error('Ошибка', message);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    setSaving(true);
    try {
      await UserService.delete(selectedUser.id);
      notification.success('Успешно', 'Пользователь удален');
      setIsDeleteModalOpen(false);
      fetchUsers();
    } catch (err) {
      const message = err.response?.data?.detail || 'Ошибка при удалении пользователя';
      notification.error('Ошибка', message);
    } finally {
      setSaving(false);
    }
  };

  const getRoleName = (roleId) => {
    const role = roles.find((r) => r.id === roleId);
    return role?.name || 'Unknown';
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold" style={{ color: 'rgb(var(--text-primary))' }}>
            Пользователи
          </h1>
          <p style={{ color: 'rgb(var(--text-muted))' }}>Управление пользователями системы</p>
        </div>
        <Button
          onClick={openCreateModal}
          disabled={loading}
          className="text-white"
          style={{
            background: 'linear-gradient(to right, rgb(var(--button-from)), rgb(var(--button-to)))',
          }}
        >
          <Plus className="h-4 w-4 mr-2" />
          Добавить пользователя
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
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search
                className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4"
                style={{ color: 'rgb(var(--text-muted))' }}
              />
              <Input
                type="search"
                placeholder="Поиск по имени или email..."
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
            <div className="flex gap-2 flex-wrap">
              <Button
                variant={selectedRole === 'all' ? 'default' : 'outline'}
                onClick={() => setSelectedRole('all')}
                className={selectedRole === 'all' ? 'text-white' : ''}
                style={
                  selectedRole === 'all'
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
                Все
              </Button>
              {roles.map((role) => (
                <Button
                  key={role.id}
                  variant={selectedRole === role.id.toString() ? 'default' : 'outline'}
                  onClick={() => setSelectedRole(role.id.toString())}
                  className={selectedRole === role.id.toString() ? 'text-white' : ''}
                  style={
                    selectedRole === role.id.toString()
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
                  {role.name === 'admin' ? 'Админы' : 'Пользователи'}
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
          <CardTitle style={{ color: 'rgb(var(--text-primary))' }}>Список пользователей</CardTitle>
          <CardDescription>
            Всего: {filteredUsers.length} из {users.length}
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
                        Пользователь
                      </th>
                      <th
                        className="text-left py-3 px-4 text-sm font-medium"
                        style={{ color: 'rgb(var(--text-muted))' }}
                      >
                        Роль
                      </th>
                      <th
                        className="text-left py-3 px-4 text-sm font-medium hidden md:table-cell"
                        style={{ color: 'rgb(var(--text-muted))' }}
                      >
                        Дата регистрации
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
                    {paginatedUsers.map((user) => (
                      <tr
                        key={user.id}
                        className="border-b transition-colors hover:bg-[rgb(var(--bg-header-muted))/50]"
                        style={{ borderColor: 'rgb(var(--border)/0.5)' }}
                      >
                        <td className="py-4 px-4">
                          <div className="flex items-center gap-3">
                            <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                              <span className="text-white font-bold text-sm">
                                {user.username.charAt(0).toUpperCase()}
                              </span>
                            </div>
                            <div>
                              <div
                                className="font-medium"
                                style={{ color: 'rgb(var(--text-primary))' }}
                              >
                                {user.username}
                              </div>
                              <div
                                className="text-sm flex items-center gap-1"
                                style={{ color: 'rgb(var(--text-muted))' }}
                              >
                                <Mail className="h-3 w-3" />
                                {user.email}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="py-4 px-4">
                          <Badge
                            className={
                              getRoleName(user.role_id) === 'admin'
                                ? 'bg-purple-500/20 text-purple-400 border-purple-500/30'
                                : 'bg-blue-500/20 text-blue-400 border-blue-500/30'
                            }
                          >
                            <Shield className="h-3 w-3 mr-1" />
                            {getRoleName(user.role_id) === 'admin'
                              ? 'Администратор'
                              : 'Пользователь'}
                          </Badge>
                        </td>
                        <td className="py-4 px-4 hidden md:table-cell">
                          <div className="flex items-center gap-2 text-sm">
                            <Calendar
                              className="h-4 w-4"
                              style={{ color: 'rgb(var(--text-muted))' }}
                            />
                            <span style={{ color: 'rgb(var(--text-muted))' }}>
                              {new Date(user.created_at).toLocaleDateString('ru-RU')}
                            </span>
                          </div>
                        </td>
                        <td className="py-4 px-4 text-right">
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button
                                variant="ghost"
                                className="h-8 w-8 p-0"
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
                                onClick={() => openEditModal(user)}
                                style={{ color: 'rgb(var(--text-primary))' }}
                              >
                                <Edit2 className="h-4 w-4 mr-2" />
                                Редактировать
                              </DropdownMenuItem>
                              <DropdownMenuItem
                                className="cursor-pointer text-red-500"
                                onClick={() => openDeleteModal(user)}
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
                    {Math.min(currentPage * ITEMS_PER_PAGE, filteredUsers.length)} из{' '}
                    {filteredUsers.length}
                  </p>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
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
                          className={currentPage === page ? 'text-white' : ''}
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
            <DialogTitle style={{ color: 'rgb(var(--text-primary))' }}>
              Создать пользователя
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium" style={{ color: 'rgb(var(--text-primary))' }}>
                Имя пользователя
              </label>
              <Input
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                placeholder="username"
                style={{
                  backgroundColor: 'rgb(var(--bg-header-muted))',
                  borderColor: formErrors.username
                    ? 'rgb(var(--error-border))'
                    : 'rgb(var(--border))',
                  color: 'rgb(var(--text-primary))',
                }}
              />
              {formErrors.username && (
                <p className="text-xs" style={{ color: 'rgb(var(--error-text))' }}>
                  {formErrors.username}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium" style={{ color: 'rgb(var(--text-primary))' }}>
                Email
              </label>
              <Input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="email@example.com"
                style={{
                  backgroundColor: 'rgb(var(--bg-header-muted))',
                  borderColor: formErrors.email ? 'rgb(var(--error-border))' : 'rgb(var(--border))',
                  color: 'rgb(var(--text-primary))',
                }}
              />
              {formErrors.email && (
                <p className="text-xs" style={{ color: 'rgb(var(--error-text))' }}>
                  {formErrors.email}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium" style={{ color: 'rgb(var(--text-primary))' }}>
                Пароль
              </label>
              <Input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                placeholder="••••••••"
                style={{
                  backgroundColor: 'rgb(var(--bg-header-muted))',
                  borderColor: formErrors.password
                    ? 'rgb(var(--error-border))'
                    : 'rgb(var(--border))',
                  color: 'rgb(var(--text-primary))',
                }}
              />
              {formData.password && (
                <div className="space-y-1">
                  <div
                    className="flex justify-between text-xs"
                    style={{ color: 'rgb(var(--text-muted))' }}
                  >
                    <span>Сложность пароля</span>
                    <span>{passwordStrength(formData.password).strength}%</span>
                  </div>
                  <div
                    className="h-2 w-full rounded-full overflow-hidden"
                    style={{ backgroundColor: 'rgb(var(--border)/0.5)' }}
                  >
                    <div
                      className={`h-full ${passwordStrength(formData.password).color} transition-all duration-300`}
                      style={{ width: `${passwordStrength(formData.password).strength}%` }}
                    />
                  </div>
                </div>
              )}
              {formErrors.password && (
                <p className="text-xs" style={{ color: 'rgb(var(--error-text))' }}>
                  {formErrors.password}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium" style={{ color: 'rgb(var(--text-primary))' }}>
                Роль
              </label>
              <select
                value={formData.role_id}
                onChange={(e) => setFormData({ ...formData, role_id: e.target.value })}
                className="flex h-10 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                style={{
                  backgroundColor: 'rgb(var(--bg-header-muted))',
                  borderColor: formErrors.role_id
                    ? 'rgb(var(--error-border))'
                    : 'rgb(var(--border))',
                  color: 'rgb(var(--text-primary))',
                }}
              >
                {roles.map((role) => (
                  <option key={role.id} value={role.id}>
                    {role.name === 'admin' ? 'Администратор' : 'Пользователь'}
                  </option>
                ))}
              </select>
              {formErrors.role_id && (
                <p className="text-xs" style={{ color: 'rgb(var(--error-text))' }}>
                  {formErrors.role_id}
                </p>
              )}
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsCreateModalOpen(false)}
              disabled={saving}
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
              className="text-white"
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
              Редактировать пользователя
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium" style={{ color: 'rgb(var(--text-primary))' }}>
                Имя пользователя
              </label>
              <Input
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                placeholder="username"
                style={{
                  backgroundColor: 'rgb(var(--bg-header-muted))',
                  borderColor: formErrors.username
                    ? 'rgb(var(--error-border))'
                    : 'rgb(var(--border))',
                  color: 'rgb(var(--text-primary))',
                }}
              />
              {formErrors.username && (
                <p className="text-xs" style={{ color: 'rgb(var(--error-text))' }}>
                  {formErrors.username}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium" style={{ color: 'rgb(var(--text-primary))' }}>
                Email
              </label>
              <Input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="email@example.com"
                style={{
                  backgroundColor: 'rgb(var(--bg-header-muted))',
                  borderColor: formErrors.email ? 'rgb(var(--error-border))' : 'rgb(var(--border))',
                  color: 'rgb(var(--text-primary))',
                }}
              />
              {formErrors.email && (
                <p className="text-xs" style={{ color: 'rgb(var(--error-text))' }}>
                  {formErrors.email}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium" style={{ color: 'rgb(var(--text-primary))' }}>
                Новый пароль (оставьте пустым, чтобы не менять)
              </label>
              <Input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                placeholder="••••••••"
                style={{
                  backgroundColor: 'rgb(var(--bg-header-muted))',
                  borderColor: formErrors.password
                    ? 'rgb(var(--error-border))'
                    : 'rgb(var(--border))',
                  color: 'rgb(var(--text-primary))',
                }}
              />
              {formData.password && (
                <div className="space-y-1">
                  <div
                    className="flex justify-between text-xs"
                    style={{ color: 'rgb(var(--text-muted))' }}
                  >
                    <span>Сложность пароля</span>
                    <span>{passwordStrength(formData.password).strength}%</span>
                  </div>
                  <div
                    className="h-2 w-full rounded-full overflow-hidden"
                    style={{ backgroundColor: 'rgb(var(--border)/0.5)' }}
                  >
                    <div
                      className={`h-full ${passwordStrength(formData.password).color} transition-all duration-300`}
                      style={{ width: `${passwordStrength(formData.password).strength}%` }}
                    />
                  </div>
                </div>
              )}
              {formErrors.password && (
                <p className="text-xs" style={{ color: 'rgb(var(--error-text))' }}>
                  {formErrors.password}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium" style={{ color: 'rgb(var(--text-primary))' }}>
                Роль
              </label>
              <select
                value={formData.role_id}
                onChange={(e) => setFormData({ ...formData, role_id: e.target.value })}
                className="flex h-10 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                style={{
                  backgroundColor: 'rgb(var(--bg-header-muted))',
                  borderColor: formErrors.role_id
                    ? 'rgb(var(--error-border))'
                    : 'rgb(var(--border))',
                  color: 'rgb(var(--text-primary))',
                }}
              >
                {roles.map((role) => (
                  <option key={role.id} value={role.id}>
                    {role.name === 'admin' ? 'Администратор' : 'Пользователь'}
                  </option>
                ))}
              </select>
              {formErrors.role_id && (
                <p className="text-xs" style={{ color: 'rgb(var(--error-text))' }}>
                  {formErrors.role_id}
                </p>
              )}
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsEditModalOpen(false)}
              disabled={saving}
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
              className="text-white"
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
            <DialogTitle style={{ color: 'rgb(var(--text-primary))' }}>
              Удалить пользователя
            </DialogTitle>
          </DialogHeader>
          <div className="py-4">
            <p style={{ color: 'rgb(var(--text-muted))' }}>
              Вы уверены, что хотите удалить пользователя{' '}
              <span className="font-semibold" style={{ color: 'rgb(var(--text-primary))' }}>
                {selectedUser?.username}
              </span>
              ? Это действие нельзя отменить.
            </p>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsDeleteModalOpen(false)}
              disabled={saving}
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
              className="text-white bg-red-500 hover:bg-red-600"
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
