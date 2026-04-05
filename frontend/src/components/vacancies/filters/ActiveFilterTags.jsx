import { X, Globe, Building2, MapPin, Banknote, Sparkles, Briefcase, Clock } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

export default function ActiveFilterTags({ filters, availableFilters, onFiltersChange }) {
  const renderTag = (icon, label, onRemove, key) => (
    <Badge
      key={key}
      className="flex items-center gap-1 px-3 py-1 cursor-pointer"
      style={{
        backgroundColor: 'rgb(var(--accent)/0.1)',
        color: 'rgb(var(--accent))',
      }}
    >
      {icon}
      {label}
      <button type="button" onClick={onRemove} className="ml-1 hover:opacity-70">
        <X className="h-3 w-3" />
      </button>
    </Badge>
  );

  return (
    <div
      className="flex flex-wrap gap-2 mt-4 pt-4 border-t"
      style={{ borderColor: 'rgb(var(--border))' }}
    >
      {filters.source_ids?.map((id) => {
        const source = availableFilters?.sources?.find((s) => s.id === id);
        return (
          source &&
          renderTag(
            <Globe className="h-3 w-3" />,
            source.name,
            () =>
              onFiltersChange({
                ...filters,
                source_ids: filters.source_ids.filter((s) => s !== id),
              }),
            `source-${id}`
          )
        );
      })}

      {filters.company_ids?.map((id) => {
        const company = availableFilters?.companies?.find((c) => c.id === id);
        return (
          company &&
          renderTag(
            <Building2 className="h-3 w-3" />,
            company.name,
            () =>
              onFiltersChange({
                ...filters,
                company_ids: filters.company_ids.filter((c) => c !== id),
              }),
            `company-${id}`
          )
        );
      })}

      {filters.city_ids?.map((id) => {
        const city = availableFilters?.cities?.find((c) => c.id === id);
        return (
          city &&
          renderTag(
            <MapPin className="h-3 w-3" />,
            city.name,
            () =>
              onFiltersChange({
                ...filters,
                city_ids: filters.city_ids.filter((c) => c !== id),
              }),
            `city-${id}`
          )
        );
      })}

      {(filters.salary_from || filters.salary_to) &&
        renderTag(
          <Banknote className="h-3 w-3" />,
          `${filters.salary_from ? `от ${filters.salary_from.toLocaleString()}` : ''}${
            filters.salary_from && filters.salary_to ? ' — ' : ''
          }${filters.salary_to ? `до ${filters.salary_to.toLocaleString()}` : ''}`,
          () =>
            onFiltersChange({
              ...filters,
              salary_from: null,
              salary_to: null,
            }),
          'salary'
        )}

      {filters.skill_ids?.map((id) => {
        const skill = availableFilters?.skills?.find((s) => s.id === id);
        return (
          skill &&
          renderTag(
            <Sparkles className="h-3 w-3" />,
            skill.name,
            () =>
              onFiltersChange({
                ...filters,
                skill_ids: filters.skill_ids.filter((s) => s !== id),
              }),
            `skill-${id}`
          )
        );
      })}

      {filters.experience?.map((exp) => {
        const expOption = availableFilters?.experience?.find((e) => e.id === exp);
        return renderTag(
          <Briefcase className="h-3 w-3" />,
          expOption?.name || exp,
          () =>
            onFiltersChange({
              ...filters,
              experience: filters.experience.filter((e) => e !== exp),
            }),
          `exp-${exp}`
        );
      })}

      {filters.employment?.map((emp) => {
        const empOption = availableFilters?.employment?.find((e) => e.id === emp);
        return renderTag(
          <Clock className="h-3 w-3" />,
          empOption?.name || emp,
          () =>
            onFiltersChange({
              ...filters,
              employment: filters.employment.filter((e) => e !== emp),
            }),
          `emp-${emp}`
        );
      })}

      {filters.schedule?.map((sch) => {
        const schOption = availableFilters?.schedule?.find((s) => s.id === sch);
        return renderTag(
          <Clock className="h-3 w-3" />,
          schOption?.name || sch,
          () =>
            onFiltersChange({
              ...filters,
              schedule: filters.schedule.filter((s) => s !== sch),
            }),
          `sch-${sch}`
        );
      })}
    </div>
  );
}
