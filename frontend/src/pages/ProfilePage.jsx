import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/utils/AuthContext';
import useNotification from '@/hooks/useNotification';
import UserService from '@/api/services/UserService';
import SkillService from '@/api/services/SkillService';
import { SkillsManagement, SkillsStats, PasswordSetup } from '@/components/profile';

export default function ProfilePage() {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const notification = useNotification();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [allSkills, setAllSkills] = useState([]);
  const [selectedSkills, setSelectedSkills] = useState([]);
  const [initialCount, setInitialCount] = useState(0);
  const [fullUserData, setFullUserData] = useState(null);

  useEffect(() => {
    const fetchFullUserData = async () => {
      if (!user?.id) return;
      try {
        const data = await UserService.getById(user.id);
        setFullUserData(data);
      } catch {
        notification.error('Ошибка', 'Не удалось загрузить данные профиля');
      }
    };
    fetchFullUserData();
  }, [user?.id, notification]);

  const fetchUserSkills = useCallback(async () => {
    if (!user?.id) return;
    setLoading(true);
    try {
      const data = await UserService.getById(user.id);
      const skills = data.skills || [];
      setSelectedSkills(skills);
      setInitialCount(skills.length);
    } catch {
      notification.error('Ошибка', 'Не удалось загрузить навыки');
    } finally {
      setLoading(false);
    }
  }, [user?.id, notification]);

  const fetchAllSkills = useCallback(async () => {
    try {
      const data = await SkillService.getAll();
      setAllSkills(data);
    } catch {
      notification.error('Ошибка', 'Не удалось загрузить список навыков');
    }
  }, [notification]);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    if (user?.id) {
      fetchUserSkills();
      fetchAllSkills();
    }
  }, [isAuthenticated, user?.id, fetchUserSkills, fetchAllSkills, navigate]);

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
      setInitialCount(selectedSkills.length);
      notification.success('Профиль обновлен', 'Навыки успешно сохранены');
    } catch {
      notification.error('Ошибка', 'Не удалось сохранить навыки');
    } finally {
      setSaving(false);
    }
  };

  if (loading || !fullUserData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="h-12 w-12 border-4 border-[rgb(var(--accent))] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p style={{ color: 'rgb(var(--text-muted))' }}>Загрузка...</p>
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
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
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
                  <p style={{ color: 'rgb(var(--text-muted))' }}>Управление настройками аккаунта</p>
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <PasswordSetup user={fullUserData} />
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
                  initialCount={initialCount}
                  onSave={handleSaveSkills}
                  saving={saving}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
