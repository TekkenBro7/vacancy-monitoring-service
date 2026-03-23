import { Briefcase } from 'lucide-react';
import VacancyCard from './VacancyCard';

export default function VacancyList({ vacancies, loading }) {
  if (loading) {
    return (
      <div className="space-y-6">
        {[...Array(3)].map((_, i) => (
          <div
            key={i}
            className="h-72 rounded-2xl animate-pulse"
            style={{ backgroundColor: 'rgb(var(--bg-header-muted)/0.3)' }}
          />
        ))}
      </div>
    );
  }

  if (!vacancies || vacancies.length === 0) {
    return (
      <div
        className="text-center py-16 px-4 rounded-2xl backdrop-blur-sm border"
        style={{
          backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
          borderColor: 'rgb(var(--border))',
        }}
      >
        <Briefcase className="h-16 w-16 mx-auto mb-4" style={{ color: 'rgb(var(--text-muted))' }} />
        <h3 className="text-xl font-semibold mb-2" style={{ color: 'rgb(var(--text-primary))' }}>
          Вакансии не найдены
        </h3>
        <p style={{ color: 'rgb(var(--text-muted))' }}>
          Попробуйте изменить параметры поиска или зайдите позже
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {vacancies.map((vacancy, index) => (
        <div
          key={vacancy.id}
          className="animate-fade-in-up"
          style={{ animationDelay: `${index * 100}ms` }}
        >
          <VacancyCard vacancy={vacancy} />
        </div>
      ))}
    </div>
  );
}
