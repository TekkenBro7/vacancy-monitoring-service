import { useState, useMemo, useCallback } from 'react';
import { User, Phone, MapPin, FileText, Save, Loader2, X } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function PersonalInfo({ profile, cities = [], onSave, saving }) {
  const getInitialFormData = useCallback(
    () => ({
      full_name: profile?.full_name || '',
      phone: profile?.phone || '',
      city_id: profile?.city_id || null,
      address: profile?.address || '',
      bio: profile?.bio || '',
    }),
    [profile]
  );

  const [formData, setFormData] = useState(getInitialFormData);
  const [citySearch, setCitySearch] = useState(profile?.city?.name || '');
  const [showCityDropdown, setShowCityDropdown] = useState(false);

  const profileKey = `${profile?.id}-${profile?.updated_at}`;
  const [lastProfileKey, setLastProfileKey] = useState(profileKey);

  if (profileKey !== lastProfileKey && profile) {
    setLastProfileKey(profileKey);
    setFormData({
      full_name: profile.full_name || '',
      phone: profile.phone || '',
      city_id: profile.city_id || null,
      address: profile.address || '',
      bio: profile.bio || '',
    });
    setCitySearch(profile.city?.name || '');
  }

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleCitySelect = (city) => {
    setFormData((prev) => ({ ...prev, city_id: city.id }));
    setCitySearch(city.name);
    setShowCityDropdown(false);
  };

  const handleClearCity = () => {
    setFormData((prev) => ({ ...prev, city_id: null }));
    setCitySearch('');
  };

  const handleCityInputChange = (e) => {
    const value = e.target.value;
    setCitySearch(value);
    setShowCityDropdown(true);
    if (!value) {
      setFormData((prev) => ({ ...prev, city_id: null }));
    }
  };

  const filteredCities = useMemo(() => {
    if (!citySearch || !cities.length) return [];
    return cities
      .filter((city) => city.name.toLowerCase().includes(citySearch.toLowerCase()))
      .slice(0, 10);
  }, [cities, citySearch]);

  const handleSubmit = () => {
    onSave(formData);
  };

  const hasChanges = useMemo(() => {
    if (!profile) return false;
    return (
      formData.full_name !== (profile.full_name || '') ||
      formData.phone !== (profile.phone || '') ||
      formData.city_id !== (profile.city_id || null) ||
      formData.address !== (profile.address || '') ||
      formData.bio !== (profile.bio || '')
    );
  }, [formData, profile]);

  const bioLength = formData.bio?.length || 0;

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
          <User className="h-5 w-5 text-white" />
        </div>
        <div>
          <h2 className="text-lg font-semibold" style={{ color: 'rgb(var(--text-primary))' }}>
            Личная информация
          </h2>
          <p className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
            Основные данные профиля
          </p>
        </div>
      </div>

      <div className="space-y-5">
        <div>
          <label
            className="block text-sm font-medium mb-2"
            style={{ color: 'rgb(var(--text-primary))' }}
          >
            Полное имя
          </label>
          <div className="relative">
            <User
              className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5"
              style={{ color: 'rgb(var(--text-muted))' }}
            />
            <input
              type="text"
              value={formData.full_name}
              onChange={(e) => handleChange('full_name', e.target.value)}
              placeholder="Иван Иванов"
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
            Телефон
          </label>
          <div className="relative">
            <Phone
              className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5"
              style={{ color: 'rgb(var(--text-muted))' }}
            />
            <input
              type="tel"
              value={formData.phone}
              onChange={(e) => handleChange('phone', e.target.value)}
              placeholder="+375 29 123 45 67"
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
            Город
          </label>
          <div className="relative">
            <MapPin
              className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 z-10"
              style={{ color: 'rgb(var(--text-muted))' }}
            />
            <input
              type="text"
              value={citySearch}
              onChange={handleCityInputChange}
              onFocus={() => setShowCityDropdown(true)}
              onBlur={() => setTimeout(() => setShowCityDropdown(false), 200)}
              placeholder="Начните вводить город..."
              className="w-full pl-10 pr-10 py-3 rounded-xl border transition-all duration-200 focus:outline-none focus:ring-2"
              style={{
                backgroundColor: 'rgb(var(--bg-header-muted))',
                borderColor: 'rgb(var(--border))',
                color: 'rgb(var(--text-primary))',
              }}
            />
            {formData.city_id && (
              <button
                type="button"
                onClick={handleClearCity}
                className="absolute right-3 top-1/2 -translate-y-1/2 p-1 rounded-full transition-colors hover:opacity-70"
              >
                <X className="h-4 w-4" style={{ color: 'rgb(var(--text-muted))' }} />
              </button>
            )}
            {showCityDropdown && filteredCities.length > 0 && (
              <div
                className="absolute z-20 w-full mt-1 max-h-48 overflow-y-auto rounded-xl border shadow-lg"
                style={{
                  backgroundColor: 'rgb(var(--bg-header))',
                  borderColor: 'rgb(var(--border))',
                }}
              >
                {filteredCities.map((city) => (
                  <button
                    key={city.id}
                    type="button"
                    onMouseDown={() => handleCitySelect(city)}
                    className="w-full px-4 py-2.5 text-left transition-colors hover:opacity-80"
                    style={{
                      color: 'rgb(var(--text-primary))',
                      backgroundColor: 'transparent',
                    }}
                  >
                    {city.name}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        <div>
          <label
            className="block text-sm font-medium mb-2"
            style={{ color: 'rgb(var(--text-primary))' }}
          >
            Адрес
          </label>
          <div className="relative">
            <MapPin
              className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5"
              style={{ color: 'rgb(var(--text-muted))' }}
            />
            <input
              type="text"
              value={formData.address}
              onChange={(e) => handleChange('address', e.target.value)}
              placeholder="ул. Примерная, д. 1"
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
            О себе
          </label>
          <div className="relative">
            <FileText
              className="absolute left-3 top-3 h-5 w-5"
              style={{ color: 'rgb(var(--text-muted))' }}
            />
            <textarea
              value={formData.bio}
              onChange={(e) => handleChange('bio', e.target.value)}
              placeholder="Расскажите о себе, своих интересах и целях..."
              rows={4}
              maxLength={1000}
              className="w-full pl-10 pr-4 py-3 rounded-xl border transition-all duration-200 focus:outline-none focus:ring-2 resize-none"
              style={{
                backgroundColor: 'rgb(var(--bg-header-muted))',
                borderColor: 'rgb(var(--border))',
                color: 'rgb(var(--text-primary))',
              }}
            />
            <span
              className="absolute right-3 bottom-3 text-xs"
              style={{ color: 'rgb(var(--text-muted))' }}
            >
              {bioLength}/1000
            </span>
          </div>
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
