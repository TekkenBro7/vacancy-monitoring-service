import { useState } from 'react';
import { Search, Sparkles } from 'lucide-react';

export default function SkillSearch({ allSkills, selectedSkills, onAddSkill }) {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredSkills = allSkills.filter(
    (skill) =>
      skill.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
      !selectedSkills.find((s) => s.id === skill.id)
  );

  return (
    <div>
      <div className="relative">
        <Search
          className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4"
          style={{ color: 'rgb(var(--text-muted))' }}
        />
        <input
          type="text"
          placeholder="Поиск навыков..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full h-11 pl-10 pr-4 rounded-md border bg-transparent px-3 py-1 text-base focus:outline-none focus:ring-1 focus:ring-[rgb(var(--accent))]"
          style={{
            backgroundColor: 'rgb(var(--bg-header-muted))',
            borderColor: 'rgb(var(--border))',
            color: 'rgb(var(--text-primary))',
          }}
        />
      </div>

      {searchQuery && filteredSkills.length > 0 && (
        <div
          className="mt-4 space-y-2 p-3 rounded-lg border max-h-64 overflow-y-auto transition-all duration-300"
          style={{
            backgroundColor: 'rgb(var(--bg-header-muted))',
            borderColor: 'rgb(var(--border))',
          }}
        >
          {filteredSkills.map((skill) => (
            <button
              key={skill.id}
              onClick={() => {
                onAddSkill(skill);
                setSearchQuery('');
              }}
              className="w-full text-left px-4 py-3 rounded-md transition-all duration-300 hover:scale-[1.02] hover:bg-[rgb(var(--accent))/10]"
              style={{ color: 'rgb(var(--text-primary))' }}
            >
              <div className="flex items-center gap-3">
                <div
                  className="inline-flex items-center justify-center h-9 w-9 rounded-lg"
                  style={{ background: 'rgb(var(--bg-header-muted))' }}
                >
                  <Sparkles className="h-4 w-4" style={{ color: 'rgb(var(--accent))' }} />
                </div>
                <div>
                  <div className="font-medium">{skill.name}</div>
                  <div className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                    Нажмите чтобы добавить
                  </div>
                </div>
              </div>
            </button>
          ))}
        </div>
      )}

      {searchQuery && filteredSkills.length === 0 && (
        <div
          className="mt-4 p-6 rounded-lg border text-center transition-all duration-300"
          style={{
            backgroundColor: 'rgb(var(--bg-header-muted))',
            borderColor: 'rgb(var(--border))',
          }}
        >
          <div
            className="inline-flex items-center justify-center h-16 w-16 rounded-full mx-auto mb-4"
            style={{ background: 'rgb(var(--bg-header-muted))' }}
          >
            <Search className="h-8 w-8 opacity-30" style={{ color: 'rgb(var(--text-muted))' }} />
          </div>
          <p className="font-medium" style={{ color: 'rgb(var(--text-primary))' }}>
            Навыки не найдены
          </p>
          <p className="text-sm mt-1" style={{ color: 'rgb(var(--text-muted))' }}>
            Попробуйте другой поисковый запрос
          </p>
        </div>
      )}

      <p className="text-xs mt-4" style={{ color: 'rgb(var(--text-muted))' }}>
        💡 Нажмите на навык чтобы добавить. Нажмите на бейджик чтобы удалить.
      </p>
    </div>
  );
}
