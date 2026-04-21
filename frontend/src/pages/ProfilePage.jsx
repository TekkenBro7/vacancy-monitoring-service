import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, User, Briefcase, Code } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/utils/AuthContext';
import useNotification from '@/hooks/useNotification';
import UserService from '@/api/services/UserService';
import UserProfileService from '@/api/services/UserProfileService';
import SkillService from '@/api/services/SkillService';
import {
  SkillsManagement,
  SkillsStats,
  PasswordSetup,
  PersonalInfo,
  WorkPreferences,
} from '@/components/profile';

export default function ProfilePage() {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const notification = useNotification();

  const [activeTab, setActiveTab] = useState('personal');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [profile, setProfile] = useState(null);
  const [fullUserData, setFullUserData] = useState(null);
  const [securityInfo, setSecurityInfo] = useState(null);

  const [allSkills, setAllSkills] = useState([]);
  const [cities, setCities] = useState([]);
  const [profileOptions, setProfileOptions] = useState(null);

  const [selectedSkills, setSelectedSkills] = useState([]);
  const [initialSkillCount, setInitialSkillCount] = useState(0);

  const fetchAllData = useCallback(async () => {
    if (!user?.id) return;
    setLoading(true);

    try {
      const [userData, secData, profileData, skillsData, optionsData] = await Promise.all([
        UserService.getById(user.id),
        UserService.getSecurityInfo(),
        UserProfileService.getUserProfile(user.id),
        SkillService.getAll(),
        UserProfileService.getProfileOptions(),
      ]);

      setFullUserData(userData);
      setSecurityInfo(secData);
      setProfile(profileData);
      setAllSkills(skillsData);
      setProfileOptions(optionsData);

      const skills = userData.skills || [];
      setSelectedSkills(skills);
      setInitialSkillCount(skills.length);

      try {
        const { default: CityService } = await import('@/api/services/CityService');
        const citiesData = await CityService.getAll();
        setCities(citiesData);
      } catch {
        console.log('CityService not available');
        setCities([]);
      }
    } catch (err) {
      console.error('Failed to load profile data:', err);
      notification.error('Ошибка', 'Не удалось загрузить данные профиля');
    } finally {
      setLoading(false);
    }
  }, [user?.id, notification]);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    fetchAllData();
  }, [isAuthenticated, fetchAllData, navigate]);

  const handleAddSkill = (skill) => {
    if (!selectedSkills.find((s) => s.id === skill.id)) {
      setSelectedSkills([...selectedSkills, skill]);
    }
  };

  const handleRemoveSkill = (skillId) => {
    setSelectedSkills(selectedSkills.filter((s) => s.id !== skillId));
  };

  const handleSaveSkills = async () => {
    setSaving(true);
    try {
      await UserService.updateSkills(
        user.id,
        selectedSkills.map((s) => s.id)
      );
      setInitialSkillCount(selectedSkills.length);
      notification.success('Успешно', 'Навыки сохранены');
    } catch {
      notification.error('Ошибка', 'Не удалось сохранить навыки');
    } finally {
      setSaving(false);
    }
  };

  const handleSaveProfile = async (data) => {
    setSaving(true);
    try {
      const updated = await UserProfileService.updateUserProfile(user.id, data);
      setProfile(updated);
      notification.success('Успешно', 'Профиль обновлён');
    } catch {
      notification.error('Ошибка', 'Не удалось сохранить профиль');
    } finally {
      setSaving(false);
    }
  };

  const tabs = [
    { id: 'personal', label: 'Личные данные', icon: User },
    { id: 'work', label: 'Предпочтения', icon: Briefcase },
    { id: 'skills', label: 'Навыки', icon: Code },
  ];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="h-12 w-12 border-4 border-[rgb(var(--accent))] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p style={{ color: 'rgb(var(--text-muted))' }}>Загрузка профиля...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen transition-colors duration-300 pb-16">
      <div
        className="absolute top-0 left-0 right-0 h-px"
        style={{
          background: 'linear-gradient(to right, transparent, rgb(var(--accent))/30, transparent)',
        }}
      />

      <div className="container mx-auto px-6 py-12 relative z-10">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                onClick={() => navigate(-1)}
                className="h-10 w-10 p-0 rounded-full transition-all duration-300 hover:scale-110"
                style={{ color: 'rgb(var(--text-muted))' }}
              >
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-3xl font-bold" style={{ color: 'rgb(var(--text-primary))' }}>
                  Профиль
                </h1>
                <p style={{ color: 'rgb(var(--text-muted))' }}>
                  {fullUserData?.username} • {fullUserData?.email}
                </p>
              </div>
            </div>
          </div>

          <div
            className="flex gap-2 mb-6 p-1.5 rounded-xl w-fit"
            style={{ backgroundColor: 'rgb(var(--bg-header-muted))' }}
          >
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className="flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium transition-all duration-200"
                  style={{
                    backgroundColor: isActive ? 'rgb(var(--accent))' : 'transparent',
                    color: isActive ? 'white' : 'rgb(var(--text-muted))',
                  }}
                >
                  <Icon className="h-4 w-4" />
                  <span className="hidden sm:inline">{tab.label}</span>
                </button>
              );
            })}
          </div>

          <div className="space-y-6">
            {securityInfo && <PasswordSetup user={securityInfo} />}

            {activeTab === 'personal' && (
              <PersonalInfo
                profile={profile}
                cities={cities}
                onSave={handleSaveProfile}
                saving={saving}
              />
            )}

            {activeTab === 'work' && (
              <WorkPreferences
                profile={profile}
                options={profileOptions}
                onSave={handleSaveProfile}
                saving={saving}
              />
            )}

            {activeTab === 'skills' && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                  <SkillsManagement
                    allSkills={allSkills}
                    selectedSkills={selectedSkills}
                    onAddSkill={handleAddSkill}
                    onRemoveSkill={handleRemoveSkill}
                  />
                </div>
                <div className="lg:col-span-1">
                  <SkillsStats
                    selectedCount={selectedSkills.length}
                    totalCount={allSkills.length}
                    initialCount={initialSkillCount}
                    onSave={handleSaveSkills}
                    saving={saving}
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
