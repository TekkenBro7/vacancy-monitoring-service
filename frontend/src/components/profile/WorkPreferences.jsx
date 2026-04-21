import { useState, useMemo, useCallback } from 'react';
import {
  Briefcase,
  Clock,
  Home,
  GraduationCap,
  DollarSign,
  Save,
  Loader2,
  Check,
} from 'lucide-react';
import { Button } from '@/components/ui/button';

function TriStateToggle({ value, onChange, labels }) {
  return (
    <div
      className="flex rounded-xl p-1 gap-1"
      style={{ backgroundColor: 'rgb(var(--bg-header-muted))' }}
    >
      {[
        { val: true, label: labels.yes },
        { val: null, label: labels.any },
        { val: false, label: labels.no },
      ].map((option) => (
        <button
          key={String(option.val)}
          type="button"
          onClick={() => onChange(option.val)}
          className="flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center justify-center gap-1"
          style={{
            backgroundColor: value === option.val ? 'rgb(var(--accent))' : 'transparent',
            color: value === option.val ? 'white' : 'rgb(var(--text-muted))',
          }}
        >
          {value === option.val && <Check className="h-3 w-3" />}
          {option.label}
        </button>
      ))}
    </div>
  );
}

export default function WorkPreferences({ profile, options, onSave, saving }) {
  const getInitialFormData = useCallback(
    () => ({
      desired_position: profile?.desired_position || '',
      desired_salary: profile?.desired_salary || null,
      preferred_remote: profile?.preferred_remote ?? null,
      preferred_internship: profile?.preferred_internship ?? null,
      preferred_employment: profile?.preferred_employment || null,
      preferred_schedule: profile?.preferred_schedule || null,
    }),
    [profile]
  );

  const [formData, setFormData] = useState(getInitialFormData);

  const profileKey = `${profile?.id}-${profile?.updated_at}`;
  const [lastProfileKey, setLastProfileKey] = useState(profileKey);

  if (profileKey !== lastProfileKey && profile) {
    setLastProfileKey(profileKey);
    setFormData({
      desired_position: profile.desired_position || '',
      desired_salary: profile.desired_salary || null,
      preferred_remote: profile.preferred_remote ?? null,
      preferred_internship: profile.preferred_internship ?? null,
      preferred_employment: profile.preferred_employment || null,
      preferred_schedule: profile.preferred_schedule || null,
    });
  }

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = () => {
    const dataToSend = { ...formData };
    if (dataToSend.desired_salary === '') dataToSend.desired_salary = null;
    onSave(dataToSend);
  };

  const hasChanges = useMemo(() => {
    if (!profile) return false;
    return (
      formData.desired_position !== (profile.desired_position || '') ||
      formData.desired_salary !== (profile.desired_salary || null) ||
      formData.preferred_remote !== (profile.preferred_remote ?? null) ||
      formData.preferred_internship !== (profile.preferred_internship ?? null) ||
      formData.preferred_employment !== (profile.preferred_employment || null) ||
      formData.preferred_schedule !== (profile.preferred_schedule || null)
    );
  }, [formData, profile]);

  return (
    <div
      className="rounded-2xl p-6 border transition-all duration-300"
      style={{
        backgroundColor: 'rgb(var(--bg-header))',
        borderColor: 'rgb(var(--border))',
      }}
    >
      <div className="flex items-center gap-3 mb-6">
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center"
          style={{
            background: `linear-gradient(135deg, rgb(var(--icon-gradient-from)), rgb(var(--icon-gradient-to)))`,
          }}
        >
          <Briefcase className="h-5 w-5 text-white" />
        </div>
        <div>
          <h2 className="text-lg font-semibold" style={{ color: 'rgb(var(--text-primary))' }}>
            Предпочтения по работе
          </h2>
          <p className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
            Укажите желаемые условия работы
          </p>
        </div>
      </div>

      <div className="space-y-5">
        <div>
          <label
            className="block text-sm font-medium mb-2"
            style={{ color: 'rgb(var(--text-primary))' }}
          >
            Желаемая должность
          </label>
          <div className="relative">
            <Briefcase
              className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5"
              style={{ color: 'rgb(var(--text-muted))' }}
            />
            <input
              type="text"
              value={formData.desired_position}
              onChange={(e) => handleChange('desired_position', e.target.value)}
              placeholder="Frontend Developer"
              className="w-full pl-10 pr-4 py-3 rounded-xl border transition-all duration-200 focus:outline-none focus:ring-2"
              style={{
                backgroundColor: 'rgb(var(--bg-header-muted))',
                borderColor: 'rgb(var(--border))',
                color: 'rgb(var(--text-primary))',
              }}
            />
          </div>
        </div>

        <div>
          <label
            className="block text-sm font-medium mb-2"
            style={{ color: 'rgb(var(--text-primary))' }}
          >
            Желаемая зарплата (USD)
          </label>
          <div className="relative">
            <DollarSign
              className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5"
              style={{ color: 'rgb(var(--text-muted))' }}
            />
            <input
              type="number"
              value={formData.desired_salary || ''}
              onChange={(e) =>
                handleChange('desired_salary', e.target.value ? Number(e.target.value) : null)
              }
              placeholder="50000"
              min="0"
              className="w-full pl-10 pr-4 py-3 rounded-xl border transition-all duration-200 focus:outline-none focus:ring-2"
              style={{
                backgroundColor: 'rgb(var(--bg-header-muted))',
                borderColor: 'rgb(var(--border))',
                color: 'rgb(var(--text-primary))',
              }}
            />
          </div>
        </div>

        <div>
          <label
            className="flex items-center gap-2 text-sm font-medium mb-2"
            style={{ color: 'rgb(var(--text-primary))' }}
          >
            <Home className="h-4 w-4" />
            Формат работы
          </label>
          <TriStateToggle
            value={formData.preferred_remote}
            onChange={(val) => handleChange('preferred_remote', val)}
            labels={{ yes: 'Удалённо', any: 'Не важно', no: 'В офисе' }}
          />
        </div>

        <div>
          <label
            className="flex items-center gap-2 text-sm font-medium mb-2"
            style={{ color: 'rgb(var(--text-primary))' }}
          >
            <GraduationCap className="h-4 w-4" />
            Тип позиции
          </label>
          <TriStateToggle
            value={formData.preferred_internship}
            onChange={(val) => handleChange('preferred_internship', val)}
            labels={{ yes: 'Стажировка', any: 'Не важно', no: 'Работа' }}
          />
        </div>

        <div>
          <label
            className="flex items-center gap-2 text-sm font-medium mb-2"
            style={{ color: 'rgb(var(--text-primary))' }}
          >
            <Briefcase className="h-4 w-4" />
            Тип занятости
          </label>
          <select
            value={formData.preferred_employment || ''}
            onChange={(e) => handleChange('preferred_employment', e.target.value || null)}
            className="w-full px-4 py-3 rounded-xl border transition-all duration-200 focus:outline-none focus:ring-2 appearance-none cursor-pointer"
            style={{
              backgroundColor: 'rgb(var(--bg-header-muted))',
              borderColor: 'rgb(var(--border))',
              color: 'rgb(var(--text-primary))',
            }}
          >
            <option value="">Не важно</option>
            {options?.employment_types?.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label
            className="flex items-center gap-2 text-sm font-medium mb-2"
            style={{ color: 'rgb(var(--text-primary))' }}
          >
            <Clock className="h-4 w-4" />
            График работы
          </label>
          <select
            value={formData.preferred_schedule || ''}
            onChange={(e) => handleChange('preferred_schedule', e.target.value || null)}
            className="w-full px-4 py-3 rounded-xl border transition-all duration-200 focus:outline-none focus:ring-2 appearance-none cursor-pointer"
            style={{
              backgroundColor: 'rgb(var(--bg-header-muted))',
              borderColor: 'rgb(var(--border))',
              color: 'rgb(var(--text-primary))',
            }}
          >
            <option value="">Не важно</option>
            {options?.schedule_types?.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="mt-6 flex justify-end">
        <Button
          type="button"
          onClick={handleSubmit}
          disabled={!hasChanges || saving}
          className="flex items-center gap-2 px-6 py-2.5 rounded-xl font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          style={{
            background: hasChanges
              ? `linear-gradient(135deg, rgb(var(--button-from)), rgb(var(--button-to)))`
              : 'rgb(var(--bg-header-muted))',
            color: hasChanges ? 'white' : 'rgb(var(--text-muted))',
          }}
        >
          {saving ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Сохранение...
            </>
          ) : (
            <>
              <Save className="h-4 w-4" />
              Сохранить
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
