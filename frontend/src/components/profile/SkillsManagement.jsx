import { Tags, Search } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import SelectedSkills from './SelectedSkills';
import SkillSearch from './SkillSearch';

export default function SkillsManagement({ allSkills, selectedSkills, onAddSkill, onRemoveSkill }) {
  return (
    <div className="space-y-6">
      <Card
        className="backdrop-blur-sm"
        style={{
          backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
          borderColor: 'rgb(var(--border))',
        }}
      >
        <CardHeader>
          <CardTitle className="flex items-center gap-3">
            <div
              className="inline-flex items-center justify-center h-10 w-10 rounded-xl"
              style={{ background: 'rgb(var(--bg-header-muted))' }}
            >
              <Tags className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
            </div>
            <span style={{ color: 'rgb(var(--text-primary))' }}>Мои навыки</span>
          </CardTitle>
          <CardDescription>{selectedSkills.length} навыков выбрано</CardDescription>
        </CardHeader>
        <CardContent>
          <SelectedSkills skills={selectedSkills} onRemove={onRemoveSkill} />
        </CardContent>
      </Card>

      <Card
        className="backdrop-blur-sm"
        style={{
          backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
          borderColor: 'rgb(var(--border))',
        }}
      >
        <CardHeader>
          <CardTitle className="flex items-center gap-3">
            <div
              className="inline-flex items-center justify-center h-10 w-10 rounded-xl"
              style={{ background: 'rgb(var(--bg-header-muted))' }}
            >
              <Search className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
            </div>
            <span style={{ color: 'rgb(var(--text-primary))' }}>Поиск и добавление</span>
          </CardTitle>
          <CardDescription>Найдите навыки из списка и добавьте их</CardDescription>
        </CardHeader>
        <CardContent>
          <SkillSearch
            allSkills={allSkills}
            selectedSkills={selectedSkills}
            onAddSkill={onAddSkill}
          />
        </CardContent>
      </Card>
    </div>
  );
}
