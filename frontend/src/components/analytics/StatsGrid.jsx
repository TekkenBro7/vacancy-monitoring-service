import {
  Briefcase,
  Users,
  Building2,
  Tags,
  Bookmark,
  MessageSquare,
  Globe,
  DollarSign,
} from 'lucide-react';
import StatCard from './StatCard';

export default function StatsGrid({ overview, trends }) {
  const stats = [
    {
      title: 'Всего вакансий',
      value: overview.total_vacancies,
      change: trends?.vacancies?.change_percent,
      trend: trends?.vacancies?.trend,
      subtitle: `${overview.active_vacancies} активных`,
      icon: Briefcase,
      color: 'from-blue-500 to-cyan-500',
    },
    {
      title: 'Пользователи',
      value: overview.total_users,
      change: trends?.users?.change_percent,
      trend: trends?.users?.trend,
      icon: Users,
      color: 'from-purple-500 to-pink-500',
    },
    {
      title: 'Компании',
      value: overview.total_companies,
      change: trends?.companies?.change_percent,
      trend: trends?.companies?.trend,
      icon: Building2,
      color: 'from-emerald-500 to-teal-500',
    },
    {
      title: 'Навыки',
      value: overview.total_skills,
      icon: Tags,
      color: 'from-amber-500 to-orange-500',
    },
    {
      title: 'Закладки',
      value: overview.total_bookmarks,
      change: trends?.bookmarks?.change_percent,
      trend: trends?.bookmarks?.trend,
      icon: Bookmark,
      color: 'from-rose-500 to-red-500',
    },
    {
      title: 'Комментарии',
      value: overview.total_comments,
      icon: MessageSquare,
      color: 'from-indigo-500 to-violet-500',
    },
    {
      title: 'Удаленные вакансии',
      value: overview.remote_vacancies,
      subtitle: `${((overview.remote_vacancies / overview.total_vacancies) * 100).toFixed(1)}%`,
      icon: Globe,
      color: 'from-cyan-500 to-blue-500',
    },
    {
      title: 'С указанной зарплатой',
      value: overview.vacancies_with_salary,
      subtitle: `${((overview.vacancies_with_salary / overview.total_vacancies) * 100).toFixed(1)}%`,
      icon: DollarSign,
      color: 'from-green-500 to-emerald-500',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat) => (
        <StatCard key={stat.title} {...stat} />
      ))}
    </div>
  );
}
