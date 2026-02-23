import {
  Users,
  Briefcase,
  Building2,
  Tags,
  TrendingUp,
  DollarSign,
  Clock,
  CheckCircle,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

const stats = [
  {
    title: 'Пользователи',
    value: '1,234',
    change: '+12%',
    icon: Users,
    color: 'from-blue-500 to-cyan-500',
  },
  {
    title: 'Вакансии',
    value: '856',
    change: '+5%',
    icon: Briefcase,
    color: 'from-purple-500 to-pink-500',
  },
  {
    title: 'Компании',
    value: '342',
    change: '+8%',
    icon: Building2,
    color: 'from-emerald-500 to-teal-500',
  },
  {
    title: 'Навыки',
    value: '1,567',
    change: '+15%',
    icon: Tags,
    color: 'from-amber-500 to-orange-500',
  },
];

const recentActivity = [
  {
    id: 1,
    user: 'Иван Петров',
    action: 'зарегистрировался',
    time: '5 минут назад',
  },
  {
    id: 2,
    user: 'ООО "ТехКорп"',
    action: 'добавил вакансию',
    time: '15 минут назад',
  },
  {
    id: 3,
    user: 'Мария Сидорова',
    action: 'обновил профиль',
    time: '1 час назад',
  },
  {
    id: 4,
    user: 'Анна Иванова',
    action: 'откликнулась на вакансию',
    time: '2 часа назад',
  },
];

const topVacancies = [
  {
    id: 1,
    title: 'Senior Frontend Developer',
    company: 'TechCorp Inc.',
    applications: 45,
    status: 'active',
  },
  {
    id: 2,
    title: 'Python Backend Developer',
    company: 'DataSoft',
    applications: 38,
    status: 'active',
  },
  {
    id: 3,
    title: 'DevOps Engineer',
    company: 'CloudTeam',
    applications: 29,
    status: 'active',
  },
];

export default function AdminDashboard() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold" style={{ color: 'rgb(var(--text-primary))' }}>
          Панель администратора
        </h1>
        <p style={{ color: 'rgb(var(--text-muted))' }}>
          Добро пожаловать в панель управления системой
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <Card
            key={stat.title}
            className="backdrop-blur-sm border transition-all duration-300 hover:shadow-xl hover:scale-[1.02] hover:border-[rgb(var(--accent))/50] cursor-pointer"
            style={{
              backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
              borderColor: 'rgb(var(--border))',
            }}
          >
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle
                className="text-sm font-medium"
                style={{ color: 'rgb(var(--text-muted))' }}
              >
                {stat.title}
              </CardTitle>
              <div className={`p-2 rounded-lg bg-gradient-to-br ${stat.color}`}>
                <stat.icon className="h-4 w-4 text-white" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold" style={{ color: 'rgb(var(--text-primary))' }}>
                {stat.value}
              </div>
              <div className="flex items-center gap-1 mt-1">
                <TrendingUp className="h-3 w-3 text-emerald-500" />
                <span className="text-xs text-emerald-500">{stat.change}</span>
                <span className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                  к прошлому месяцу
                </span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card
          className="backdrop-blur-sm border"
          style={{
            backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
            borderColor: 'rgb(var(--border))',
          }}
        >
          <CardHeader>
            <CardTitle
              className="flex items-center gap-2"
              style={{ color: 'rgb(var(--text-primary))' }}
            >
              <Clock className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
              Последняя активность
            </CardTitle>
            <CardDescription>Последние действия пользователей в системе</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((activity) => (
                <div
                  key={activity.id}
                  className="flex items-center gap-4 p-3 rounded-lg transition-all duration-300 hover:bg-[rgb(var(--accent))/10] hover:scale-[1.01] cursor-pointer"
                  style={{ backgroundColor: 'rgb(var(--bg-header-muted))' }}
                >
                  <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                    <span className="text-white font-bold text-sm">{activity.user.charAt(0)}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p
                      className="text-sm font-medium"
                      style={{ color: 'rgb(var(--text-primary))' }}
                    >
                      {activity.user}
                    </p>
                    <p className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                      {activity.action}
                    </p>
                  </div>
                  <span className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                    {activity.time}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card
          className="backdrop-blur-sm border"
          style={{
            backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
            borderColor: 'rgb(var(--border))',
          }}
        >
          <CardHeader>
            <CardTitle
              className="flex items-center gap-2"
              style={{ color: 'rgb(var(--text-primary))' }}
            >
              <Briefcase className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
              Популярные вакансии
            </CardTitle>
            <CardDescription>Вакансии с наибольшим количеством откликов</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {topVacancies.map((vacancy) => (
                <div
                  key={vacancy.id}
                  className="flex items-center justify-between p-3 rounded-lg transition-all duration-300 hover:bg-[rgb(var(--accent))/10] hover:scale-[1.01] cursor-pointer"
                  style={{ backgroundColor: 'rgb(var(--bg-header-muted))' }}
                >
                  <div className="flex-1 min-w-0">
                    <p
                      className="text-sm font-medium"
                      style={{ color: 'rgb(var(--text-primary))' }}
                    >
                      {vacancy.title}
                    </p>
                    <p className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                      {vacancy.company}
                    </p>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <div
                        className="text-sm font-semibold"
                        style={{ color: 'rgb(var(--accent))' }}
                      >
                        {vacancy.applications}
                      </div>
                      <div className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                        откликов
                      </div>
                    </div>
                    <CheckCircle className="h-5 w-5 text-emerald-500" />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card
        className="backdrop-blur-sm border"
        style={{
          backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
          borderColor: 'rgb(var(--border))',
        }}
      >
        <CardHeader>
          <CardTitle style={{ color: 'rgb(var(--text-primary))' }}>Быстрые действия</CardTitle>
          <CardDescription>Часто используемые операции</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { title: 'Добавить пользователя', icon: Users },
              { title: 'Создать вакансию', icon: Briefcase },
              { title: 'Добавить компанию', icon: Building2 },
              { title: 'Управление навыками', icon: Tags },
            ].map((action) => (
              <button
                key={action.title}
                className="
                  flex flex-col items-center gap-3 p-6 rounded-xl
                  bg-[rgb(var(--bg-header-muted))]
                  border border-[rgb(var(--border))]
                  hover:border-[rgb(var(--accent))/50]
                  hover:bg-[rgb(var(--accent))/10]
                  hover:shadow-lg hover:scale-[1.03]
                  transition-all duration-300
                  cursor-pointer
                "
              >
                <action.icon className="h-8 w-8" style={{ color: 'rgb(var(--accent))' }} />
                <span className="text-sm font-medium" style={{ color: 'rgb(var(--text-primary))' }}>
                  {action.title}
                </span>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
