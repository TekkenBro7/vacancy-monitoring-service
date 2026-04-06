import VacancyCard from './VacancyCard';

export default function VacancyList({
  vacancies,
  loading,
  bookmarkedIds = new Set(),
  onBookmarkChange,
}) {
  if (loading) {
    return (
      <div className="space-y-6">
        {[...Array(3)].map((_, i) => (
          <div
            key={i}
            className="h-64 rounded-2xl animate-pulse"
            style={{ backgroundColor: 'rgb(var(--bg-header-muted)/0.3)' }}
          />
        ))}
      </div>
    );
  }

  if (vacancies.length === 0) {
    return (
      <div
        className="text-center py-16 rounded-2xl border"
        style={{
          backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
          borderColor: 'rgb(var(--border))',
        }}
      >
        <h3 className="text-xl font-semibold mb-2" style={{ color: 'rgb(var(--text-primary))' }}>
          Вакансии не найдены
        </h3>
        <p style={{ color: 'rgb(var(--text-muted))' }}>Попробуйте изменить параметры поиска</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {vacancies.map((vacancy) => (
        <VacancyCard
          key={vacancy.id}
          vacancy={vacancy}
          isBookmarked={bookmarkedIds.has(vacancy.id)}
          onBookmarkChange={onBookmarkChange}
        />
      ))}
    </div>
  );
}
