import { Sparkles, X, Tags } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

export default function SelectedSkills({ skills, onRemove }) {
  if (skills.length === 0) {
    return (
      <div className="text-center py-12" style={{ color: 'rgb(var(--text-muted))' }}>
        <div
          className="inline-flex items-center justify-center h-16 w-16 rounded-full mb-4"
          style={{ background: 'rgb(var(--bg-header-muted))' }}
        >
          <Tags className="h-8 w-8 opacity-30" style={{ color: 'rgb(var(--text-muted))' }} />
        </div>
        <p className="font-medium">У вас пока нет навыков</p>
        <p className="text-sm mt-1 opacity-70">Добавьте навыки с помощью поиска ниже</p>
      </div>
    );
  }

  return (
    <div className="flex flex-wrap gap-2">
      {skills.map((skill) => (
        <Badge
          key={skill.id}
          className="flex items-center gap-1.5 px-3 py-1.5 text-sm cursor-pointer transition-all duration-300 hover:scale-105 hover:shadow-md group"
          style={{
            background: 'rgb(var(--bg-header-muted))',
            borderColor: 'rgb(var(--border))',
            color: 'rgb(var(--text-primary))',
          }}
          onClick={() => onRemove(skill.id)}
        >
          <Sparkles
            className="h-3.5 w-3.5 transition-colors group-hover:opacity-100"
            style={{ color: 'rgb(var(--accent))' }}
          />
          {skill.name}
          <X className="h-3.5 w-3.5 opacity-40 group-hover:opacity-100 transition-opacity" />
        </Badge>
      ))}
    </div>
  );
}
