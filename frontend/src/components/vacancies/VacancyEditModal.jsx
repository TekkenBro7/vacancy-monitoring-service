import { useState, useEffect, useCallback } from 'react';
import {
  Loader2,
  Save,
  DollarSign,
  Briefcase,
  Globe,
  FileText,
  GraduationCap,
  ToggleRight,
  Link,
  Search,
  X,
  Sparkles,
  Tags,
  MapPin,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import VacancyService from '@/api/services/VacancyService';
import SkillService from '@/api/services/SkillService';
import CurrencyService from '@/api/services/CurrencyService';
import useNotification from '@/hooks/useNotification';

export default function VacancyEditModal({ isOpen, onClose, vacancy, onSuccess }) {
  const notification = useNotification();
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState('general');

  const [allSkills, setAllSkills] = useState([]);
  const [allCurrencies, setAllCurrencies] = useState([]);
  const [refsLoading, setRefsLoading] = useState(true);

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    salary_from: '',
    salary_to: '',
    currency_id: '',
    experience: '',
    education: '',
    employment: '',
    schedule: '',
    vacancy_url: '',
    address: '',
    is_remote: false,
    is_active: true,
    internship: false,
  });

  const [selectedSkills, setSelectedSkills] = useState([]);
  const [skillSearch, setSkillSearch] = useState('');

  const loadReferenceData = useCallback(async () => {
    setRefsLoading(true);
    try {
      const [skills, currencies] = await Promise.all([
        SkillService.getAll(),
        CurrencyService.getAll(),
      ]);

      setAllSkills(skills);
      setAllCurrencies(currencies);
    } catch (err) {
      console.error('Failed to load reference data:', err);
    } finally {
      setRefsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isOpen) {
      loadReferenceData();
    }
  }, [isOpen, loadReferenceData]);

  useEffect(() => {
    if (vacancy) {
      setFormData({
        title: vacancy.title || '',
        description: vacancy.description || '',
        salary_from: vacancy.salary_from ?? '',
        salary_to: vacancy.salary_to ?? '',
        currency_id: vacancy.currency?.id?.toString() || '',
        experience: vacancy.experience || '',
        education: vacancy.education || '',
        employment: vacancy.employment || '',
        schedule: vacancy.schedule || '',
        vacancy_url: vacancy.vacancy_url || '',
        address: vacancy.address || '',
        is_remote: vacancy.is_remote ?? false,
        is_active: vacancy.is_active ?? true,
        internship: vacancy.internship ?? false,
      });
      setSelectedSkills(vacancy.skills || []);
      setActiveTab('general');
      setSkillSearch('');
    }
  }, [vacancy]);

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleAddSkill = (skill) => {
    if (!selectedSkills.find((s) => s.id === skill.id)) {
      setSelectedSkills((prev) => [...prev, skill]);
    }
    setSkillSearch('');
  };

  const handleRemoveSkill = (skillId) => {
    setSelectedSkills((prev) => prev.filter((s) => s.id !== skillId));
  };

  const handleSubmit = async () => {
    if (!formData.title.trim()) {
      notification.error('Ошибка', 'Название вакансии обязательно');
      return;
    }

    setSaving(true);
    try {
      const updateData = {};

      if (formData.title !== vacancy.title) updateData.title = formData.title;
      if (formData.description !== (vacancy.description || ''))
        updateData.description = formData.description || null;

      const salaryFrom = formData.salary_from === '' ? null : parseInt(formData.salary_from);
      const salaryTo = formData.salary_to === '' ? null : parseInt(formData.salary_to);
      if (salaryFrom !== vacancy.salary_from) updateData.salary_from = salaryFrom;
      if (salaryTo !== vacancy.salary_to) updateData.salary_to = salaryTo;

      const currencyId = formData.currency_id === '' ? null : parseInt(formData.currency_id);
      if (currencyId !== (vacancy.currency?.id || null)) updateData.currency_id = currencyId;

      if (formData.experience !== (vacancy.experience || ''))
        updateData.experience = formData.experience || null;
      if (formData.education !== (vacancy.education || ''))
        updateData.education = formData.education || null;
      if (formData.employment !== (vacancy.employment || ''))
        updateData.employment = formData.employment || null;
      if (formData.schedule !== (vacancy.schedule || ''))
        updateData.schedule = formData.schedule || null;
      if (formData.vacancy_url !== (vacancy.vacancy_url || ''))
        updateData.vacancy_url = formData.vacancy_url || null;
      if (formData.address !== (vacancy.address || ''))
        updateData.address = formData.address || null;
      if (formData.is_remote !== vacancy.is_remote) updateData.is_remote = formData.is_remote;
      if (formData.is_active !== vacancy.is_active) updateData.is_active = formData.is_active;
      if (formData.internship !== vacancy.internship) updateData.internship = formData.internship;

      const originalSkillIds = (vacancy.skills || []).map((s) => s.id).sort();
      const newSkillIds = selectedSkills.map((s) => s.id).sort();
      if (JSON.stringify(originalSkillIds) !== JSON.stringify(newSkillIds)) {
        updateData.skill_ids = newSkillIds;
      }

      if (Object.keys(updateData).length === 0) {
        notification.info('Без изменений', 'Ничего не было изменено');
        onClose();
        return;
      }

      await VacancyService.updateVacancy(vacancy.id, updateData);
      onSuccess();
    } catch (err) {
      const message = err.response?.data?.detail || 'Ошибка при обновлении вакансии';
      notification.error('Ошибка', message);
    } finally {
      setSaving(false);
    }
  };

  const filteredSkills = allSkills.filter(
    (skill) =>
      skill.name.toLowerCase().includes(skillSearch.toLowerCase()) &&
      !selectedSkills.find((s) => s.id === skill.id)
  );

  const tabs = [
    { id: 'general', label: 'Основное', icon: FileText },
    { id: 'salary', label: 'Зарплата', icon: DollarSign },
    { id: 'conditions', label: 'Условия', icon: Briefcase },
    { id: 'skills', label: 'Навыки', icon: Tags },
    { id: 'settings', label: 'Настройки', icon: ToggleRight },
  ];

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent
        className="max-w-3xl max-h-[90vh] overflow-hidden flex flex-col"
        style={{
          backgroundColor: 'rgb(var(--bg-header))',
          borderColor: 'rgb(var(--border))',
        }}
      >
        <DialogHeader className="flex-shrink-0">
          <DialogTitle
            className="flex items-center gap-3"
            style={{ color: 'rgb(var(--text-primary))' }}
          >
            <div className="p-2 rounded-lg" style={{ backgroundColor: 'rgb(var(--accent)/0.1)' }}>
              <FileText className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
            </div>
            Редактирование вакансии
          </DialogTitle>
          <p className="text-sm mt-1" style={{ color: 'rgb(var(--text-muted))' }}>
            ID: {vacancy?.id} • {vacancy?.source?.name || 'Источник неизвестен'}
          </p>
        </DialogHeader>

        <div
          className="flex gap-1 p-1 rounded-xl flex-shrink-0 overflow-x-auto"
          style={{ backgroundColor: 'rgb(var(--bg-header-muted))' }}
        >
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-300 flex-1 justify-center whitespace-nowrap ${
                  activeTab === tab.id ? 'shadow-sm' : 'hover:opacity-80'
                }`}
                style={
                  activeTab === tab.id
                    ? {
                        backgroundColor: 'rgb(var(--bg-header))',
                        color: 'rgb(var(--accent))',
                        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                      }
                    : { color: 'rgb(var(--text-muted))' }
                }
              >
                <Icon className="h-4 w-4" />
                <span className="hidden sm:inline">{tab.label}</span>
              </button>
            );
          })}
        </div>

        <div className="flex-1 overflow-y-auto py-4 space-y-5 px-1">
          {refsLoading && activeTab !== 'general' && activeTab !== 'settings' ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-6 w-6 animate-spin" style={{ color: 'rgb(var(--accent))' }} />
              <span className="ml-2 text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                Загрузка данных...
              </span>
            </div>
          ) : (
            <>
              {activeTab === 'general' && (
                <div className="space-y-5 animate-fade-in">
                  <FormField label="Название вакансии" required>
                    <Input
                      value={formData.title}
                      onChange={(e) => handleChange('title', e.target.value)}
                      placeholder="Например: Senior Python Developer"
                      className="h-11"
                      style={{
                        backgroundColor: 'rgb(var(--bg-header-muted))',
                        borderColor: 'rgb(var(--border))',
                        color: 'rgb(var(--text-primary))',
                      }}
                    />
                  </FormField>

                  <FormField label="Описание">
                    <textarea
                      value={formData.description}
                      onChange={(e) => handleChange('description', e.target.value)}
                      placeholder="Описание вакансии (поддерживается HTML)..."
                      rows={8}
                      className="flex w-full rounded-lg border px-4 py-3 text-sm resize-y min-h-[120px] focus:outline-none focus:ring-1 focus:ring-[rgb(var(--accent))]"
                      style={{
                        backgroundColor: 'rgb(var(--bg-header-muted))',
                        borderColor: 'rgb(var(--border))',
                        color: 'rgb(var(--text-primary))',
                      }}
                    />
                  </FormField>

                  <FormField label="URL вакансии">
                    <div className="relative">
                      <Link
                        className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4"
                        style={{ color: 'rgb(var(--text-muted))' }}
                      />
                      <Input
                        value={formData.vacancy_url}
                        onChange={(e) => handleChange('vacancy_url', e.target.value)}
                        placeholder="https://..."
                        className="h-11 pl-10"
                        style={{
                          backgroundColor: 'rgb(var(--bg-header-muted))',
                          borderColor: 'rgb(var(--border))',
                          color: 'rgb(var(--text-primary))',
                        }}
                      />
                    </div>
                  </FormField>

                  <FormField label="Адрес">
                    <div className="relative">
                      <MapPin
                        className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4"
                        style={{ color: 'rgb(var(--text-muted))' }}
                      />
                      <Input
                        value={formData.address}
                        onChange={(e) => handleChange('address', e.target.value)}
                        placeholder="Адрес офиса"
                        className="h-11 pl-10"
                        style={{
                          backgroundColor: 'rgb(var(--bg-header-muted))',
                          borderColor: 'rgb(var(--border))',
                          color: 'rgb(var(--text-primary))',
                        }}
                      />
                    </div>
                  </FormField>
                </div>
              )}

              {activeTab === 'salary' && (
                <div className="space-y-5 animate-fade-in">
                  <div className="grid grid-cols-2 gap-4">
                    <FormField label="Зарплата от">
                      <div className="relative">
                        <DollarSign
                          className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4"
                          style={{ color: 'rgb(var(--text-muted))' }}
                        />
                        <Input
                          type="number"
                          value={formData.salary_from}
                          onChange={(e) => handleChange('salary_from', e.target.value)}
                          placeholder="0"
                          className="h-11 pl-10"
                          style={{
                            backgroundColor: 'rgb(var(--bg-header-muted))',
                            borderColor: 'rgb(var(--border))',
                            color: 'rgb(var(--text-primary))',
                          }}
                        />
                      </div>
                    </FormField>
                    <FormField label="Зарплата до">
                      <div className="relative">
                        <DollarSign
                          className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4"
                          style={{ color: 'rgb(var(--text-muted))' }}
                        />
                        <Input
                          type="number"
                          value={formData.salary_to}
                          onChange={(e) => handleChange('salary_to', e.target.value)}
                          placeholder="0"
                          className="h-11 pl-10"
                          style={{
                            backgroundColor: 'rgb(var(--bg-header-muted))',
                            borderColor: 'rgb(var(--border))',
                            color: 'rgb(var(--text-primary))',
                          }}
                        />
                      </div>
                    </FormField>
                  </div>

                  <FormField label="Валюта">
                    <select
                      value={formData.currency_id}
                      onChange={(e) => handleChange('currency_id', e.target.value)}
                      className="flex h-11 w-full rounded-lg border px-4 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-[rgb(var(--accent))]"
                      style={{
                        backgroundColor: 'rgb(var(--bg-header-muted))',
                        borderColor: 'rgb(var(--border))',
                        color: 'rgb(var(--text-primary))',
                      }}
                    >
                      <option value="">Не указана</option>
                      {allCurrencies.map((currency) => (
                        <option key={currency.id} value={currency.id}>
                          {currency.name} {currency.symbol && `(${currency.symbol})`}
                        </option>
                      ))}
                    </select>
                  </FormField>

                  <div
                    className="p-4 rounded-xl border"
                    style={{
                      backgroundColor: 'rgb(var(--accent)/0.05)',
                      borderColor: 'rgb(var(--accent)/0.2)',
                    }}
                  >
                    <p className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                      Предпросмотр:
                    </p>
                    <p className="text-lg font-bold mt-1" style={{ color: 'rgb(var(--accent))' }}>
                      {formatSalaryPreview(
                        formData.salary_from,
                        formData.salary_to,
                        allCurrencies.find((c) => c.id === parseInt(formData.currency_id))
                      )}
                    </p>
                  </div>
                </div>
              )}

              {activeTab === 'conditions' && (
                <div className="space-y-5 animate-fade-in">
                  <FormField label="Опыт работы">
                    <Input
                      value={formData.experience}
                      onChange={(e) => handleChange('experience', e.target.value)}
                      placeholder="Например: От 3 до 6 лет"
                      className="h-11"
                      style={{
                        backgroundColor: 'rgb(var(--bg-header-muted))',
                        borderColor: 'rgb(var(--border))',
                        color: 'rgb(var(--text-primary))',
                      }}
                    />
                  </FormField>

                  <FormField label="Образование">
                    <Input
                      value={formData.education}
                      onChange={(e) => handleChange('education', e.target.value)}
                      placeholder="Например: Высшее техническое"
                      className="h-11"
                      style={{
                        backgroundColor: 'rgb(var(--bg-header-muted))',
                        borderColor: 'rgb(var(--border))',
                        color: 'rgb(var(--text-primary))',
                      }}
                    />
                  </FormField>

                  <FormField label="Тип занятости">
                    <Input
                      value={formData.employment}
                      onChange={(e) => handleChange('employment', e.target.value)}
                      placeholder="Например: Полная занятость"
                      className="h-11"
                      style={{
                        backgroundColor: 'rgb(var(--bg-header-muted))',
                        borderColor: 'rgb(var(--border))',
                        color: 'rgb(var(--text-primary))',
                      }}
                    />
                  </FormField>

                  <FormField label="График работы">
                    <Input
                      value={formData.schedule}
                      onChange={(e) => handleChange('schedule', e.target.value)}
                      placeholder="Например: Гибкий график"
                      className="h-11"
                      style={{
                        backgroundColor: 'rgb(var(--bg-header-muted))',
                        borderColor: 'rgb(var(--border))',
                        color: 'rgb(var(--text-primary))',
                      }}
                    />
                  </FormField>
                </div>
              )}

              {activeTab === 'skills' && (
                <div className="space-y-5 animate-fade-in">
                  <FormField label={`Текущие навыки (${selectedSkills.length})`}>
                    {selectedSkills.length > 0 ? (
                      <div
                        className="flex flex-wrap gap-2 p-4 rounded-xl border"
                        style={{
                          borderColor: 'rgb(var(--border))',
                          backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
                        }}
                      >
                        {selectedSkills.map((skill) => (
                          <Badge
                            key={skill.id}
                            className="flex items-center gap-1.5 px-3 py-1.5 text-sm cursor-pointer transition-all duration-300 hover:scale-105 hover:shadow-md group"
                            style={{
                              background:
                                'linear-gradient(135deg, rgb(var(--accent)/0.15), rgb(var(--accent)/0.05))',
                              border: '1px solid rgb(var(--accent)/0.3)',
                              color: 'rgb(var(--text-primary))',
                            }}
                            onClick={() => handleRemoveSkill(skill.id)}
                          >
                            <Sparkles
                              className="h-3.5 w-3.5"
                              style={{ color: 'rgb(var(--accent))' }}
                            />
                            {skill.name}
                            <X className="h-3.5 w-3.5 opacity-40 group-hover:opacity-100 transition-opacity text-red-400" />
                          </Badge>
                        ))}
                      </div>
                    ) : (
                      <div
                        className="text-center py-8 rounded-xl border"
                        style={{
                          borderColor: 'rgb(var(--border))',
                          backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
                        }}
                      >
                        <Tags
                          className="h-8 w-8 mx-auto mb-2 opacity-30"
                          style={{ color: 'rgb(var(--text-muted))' }}
                        />
                        <p className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                          Навыки не добавлены
                        </p>
                      </div>
                    )}
                  </FormField>

                  <FormField label="Добавить навыки">
                    <div className="relative">
                      <Search
                        className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4"
                        style={{ color: 'rgb(var(--text-muted))' }}
                      />
                      <Input
                        value={skillSearch}
                        onChange={(e) => setSkillSearch(e.target.value)}
                        placeholder="Поиск навыков..."
                        className="h-11 pl-10"
                        style={{
                          backgroundColor: 'rgb(var(--bg-header-muted))',
                          borderColor: 'rgb(var(--border))',
                          color: 'rgb(var(--text-primary))',
                        }}
                      />
                      {skillSearch && (
                        <button
                          onClick={() => setSkillSearch('')}
                          className="absolute right-3 top-1/2 -translate-y-1/2"
                          style={{ color: 'rgb(var(--text-muted))' }}
                        >
                          <X className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                  </FormField>

                  {skillSearch && (
                    <div
                      className="rounded-xl border max-h-48 overflow-y-auto"
                      style={{
                        backgroundColor: 'rgb(var(--bg-header-muted))',
                        borderColor: 'rgb(var(--border))',
                      }}
                    >
                      {filteredSkills.length > 0 ? (
                        filteredSkills.slice(0, 20).map((skill) => (
                          <button
                            key={skill.id}
                            onClick={() => handleAddSkill(skill)}
                            className="w-full text-left px-4 py-3 transition-all duration-200 flex items-center gap-3 border-b last:border-b-0"
                            style={{
                              borderColor: 'rgb(var(--border)/0.5)',
                              color: 'rgb(var(--text-primary))',
                            }}
                            onMouseEnter={(e) => {
                              e.currentTarget.style.backgroundColor = 'rgb(var(--accent)/0.05)';
                            }}
                            onMouseLeave={(e) => {
                              e.currentTarget.style.backgroundColor = 'transparent';
                            }}
                          >
                            <Sparkles
                              className="h-4 w-4 flex-shrink-0"
                              style={{ color: 'rgb(var(--accent))' }}
                            />
                            <span className="text-sm font-medium">{skill.name}</span>
                          </button>
                        ))
                      ) : (
                        <div className="px-4 py-6 text-center">
                          <p className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                            Ничего не найдено по запросу «{skillSearch}»
                          </p>
                        </div>
                      )}
                    </div>
                  )}

                  <p className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                    💡 Нажмите на навык в списке, чтобы добавить. Нажмите на бейдж, чтобы удалить.
                  </p>
                </div>
              )}

              {activeTab === 'settings' && (
                <div className="space-y-4 animate-fade-in">
                  <ToggleCard
                    label="Активна"
                    description="Вакансия отображается в поиске и на сайте"
                    icon={ToggleRight}
                    value={formData.is_active}
                    onChange={(v) => handleChange('is_active', v)}
                    activeColor="emerald"
                  />

                  <ToggleCard
                    label="Удалённая работа"
                    description="Работа с возможностью удалёнки"
                    icon={Globe}
                    value={formData.is_remote}
                    onChange={(v) => handleChange('is_remote', v)}
                    activeColor="blue"
                  />

                  <ToggleCard
                    label="Стажировка"
                    description="Вакансия подходит для стажёров"
                    icon={GraduationCap}
                    value={formData.internship}
                    onChange={(v) => handleChange('internship', v)}
                    activeColor="purple"
                  />
                </div>
              )}
            </>
          )}
        </div>

        <DialogFooter
          className="flex-shrink-0 border-t pt-4"
          style={{ borderColor: 'rgb(var(--border))' }}
        >
          <Button
            variant="outline"
            onClick={onClose}
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
            onClick={handleSubmit}
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
              <span className="flex items-center gap-2">
                <Save className="h-4 w-4" />
                Сохранить
              </span>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function FormField({ label, required, children }) {
  return (
    <div className="space-y-2">
      <label
        className="text-sm font-medium flex items-center gap-1"
        style={{ color: 'rgb(var(--text-primary))' }}
      >
        {label}
        {required && <span style={{ color: 'rgb(var(--error-text))' }}>*</span>}
      </label>
      {children}
    </div>
  );
}

function ToggleCard({ label, description, icon: Icon, value, onChange, activeColor }) {
  const colorMap = {
    emerald: {
      bg: value ? 'rgba(16, 185, 129, 0.1)' : 'rgb(var(--bg-header-muted)/0.5)',
      border: value ? 'rgba(16, 185, 129, 0.3)' : 'rgb(var(--border))',
      iconBg: value ? 'rgba(16, 185, 129, 0.15)' : 'rgb(var(--accent)/0.1)',
      iconColor: value ? 'rgb(16, 185, 129)' : 'rgb(var(--text-muted))',
      toggleBg: value ? 'rgb(16, 185, 129)' : 'rgb(var(--border))',
    },
    blue: {
      bg: value ? 'rgba(59, 130, 246, 0.1)' : 'rgb(var(--bg-header-muted)/0.5)',
      border: value ? 'rgba(59, 130, 246, 0.3)' : 'rgb(var(--border))',
      iconBg: value ? 'rgba(59, 130, 246, 0.15)' : 'rgb(var(--accent)/0.1)',
      iconColor: value ? 'rgb(59, 130, 246)' : 'rgb(var(--text-muted))',
      toggleBg: value ? 'rgb(59, 130, 246)' : 'rgb(var(--border))',
    },
    purple: {
      bg: value ? 'rgba(139, 92, 246, 0.1)' : 'rgb(var(--bg-header-muted)/0.5)',
      border: value ? 'rgba(139, 92, 246, 0.3)' : 'rgb(var(--border))',
      iconBg: value ? 'rgba(139, 92, 246, 0.15)' : 'rgb(var(--accent)/0.1)',
      iconColor: value ? 'rgb(139, 92, 246)' : 'rgb(var(--text-muted))',
      toggleBg: value ? 'rgb(139, 92, 246)' : 'rgb(var(--border))',
    },
  };

  const colors = colorMap[activeColor] || colorMap.blue;

  return (
    <div
      onClick={() => onChange(!value)}
      className="flex items-center justify-between p-4 rounded-xl border cursor-pointer transition-all duration-300 hover:scale-[1.01] active:scale-[0.99]"
      style={{
        backgroundColor: colors.bg,
        borderColor: colors.border,
      }}
    >
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg" style={{ backgroundColor: colors.iconBg }}>
          <Icon className="h-5 w-5" style={{ color: colors.iconColor }} />
        </div>
        <div>
          <p className="font-medium" style={{ color: 'rgb(var(--text-primary))' }}>
            {label}
          </p>
          <p className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
            {description}
          </p>
        </div>
      </div>
      <div
        className="w-12 h-7 rounded-full relative transition-all duration-300"
        style={{ backgroundColor: colors.toggleBg }}
      >
        <div
          className="w-5 h-5 bg-white rounded-full absolute top-1 transition-all duration-300 shadow-sm"
          style={{ left: value ? '26px' : '4px' }}
        />
      </div>
    </div>
  );
}

function formatSalaryPreview(from, to, currency) {
  const symbol = currency?.symbol || '₽';
  const f = from ? parseInt(from) : null;
  const t = to ? parseInt(to) : null;

  if (!f && !t) return 'По договорённости';
  if (f && !t) return `от ${f.toLocaleString()} ${symbol}`;
  if (!f && t) return `до ${t.toLocaleString()} ${symbol}`;
  return `${f.toLocaleString()} — ${t.toLocaleString()} ${symbol}`;
}
