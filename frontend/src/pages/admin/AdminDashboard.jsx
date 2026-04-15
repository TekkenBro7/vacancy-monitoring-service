import { useState, useEffect, useCallback } from 'react';
import {
  RefreshCw,
  Calendar,
  TrendingUp,
  Building2,
  Tags,
  MapPin,
  DollarSign,
  Users,
  Server,
  Activity,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import AnalyticsService from '@/api/services/AnalyticsService';
import StatsGrid from '@/components/analytics/StatsGrid';
import { LineChart, BarChart, PieChart, AreaChart } from '@/components/analytics/charts';

export default function AdminDashboard() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [period, setPeriod] = useState(30);
  const [analytics, setAnalytics] = useState(null);

  const fetchAnalytics = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await AnalyticsService.getFullDashboard(period);
      setAnalytics(data);
    } catch (err) {
      console.error('Error fetching analytics:', err);
      setError('Ошибка загрузки аналитики');
    } finally {
      setLoading(false);
    }
  }, [period]);

  useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex items-center gap-3">
          <RefreshCw className="h-6 w-6 animate-spin" style={{ color: 'rgb(var(--accent))' }} />
          <span style={{ color: 'rgb(var(--text-muted))' }}>Загрузка аналитики...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
        <p className="text-red-500">{error}</p>
        <Button onClick={fetchAnalytics}>Повторить</Button>
      </div>
    );
  }

  if (!analytics) return null;

  const {
    overview,
    overview_with_trend,
    vacancies_time_series,
    salary_stats,
    top_companies,
    top_skills,
    top_cities,
    sources_stats,
    vacancy_detailed_stats,
    user_activity,
  } = analytics;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold" style={{ color: 'rgb(var(--text-primary))' }}>
            Аналитика
          </h1>
          <p style={{ color: 'rgb(var(--text-muted))' }}>Обзор статистики и метрик системы</p>
        </div>

        <div className="flex items-center gap-3">
          <div
            className="flex items-center gap-2 p-1 rounded-lg"
            style={{ backgroundColor: 'rgb(var(--bg-header-muted))' }}
          >
            {[7, 14, 30, 90].map((days) => (
              <Button
                key={days}
                variant={period === days ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setPeriod(days)}
                className={period === days ? 'bg-[rgb(var(--accent))]' : ''}
              >
                {days}д
              </Button>
            ))}
          </div>

          <Button variant="outline" size="sm" onClick={fetchAnalytics}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Обновить
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <StatsGrid overview={overview} trends={overview_with_trend} />

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Vacancies Time Series */}
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
              <TrendingUp className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
              Динамика вакансий
            </CardTitle>
            <CardDescription>Новые вакансии за период</CardDescription>
          </CardHeader>
          <CardContent>
            <AreaChart
              data={vacancies_time_series.data}
              xKey="date"
              yKey="count"
              color="#6366f1"
              height={280}
            />
          </CardContent>
        </Card>

        {/* Sources Distribution */}
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
              <Server className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
              Источники вакансий
            </CardTitle>
            <CardDescription>Распределение по источникам</CardDescription>
          </CardHeader>
          <CardContent>
            <PieChart
              data={sources_stats.map((s) => ({ name: s.name, count: s.vacancy_count }))}
              nameKey="name"
              valueKey="count"
              height={280}
              innerRadius={50}
              outerRadius={90}
            />
          </CardContent>
        </Card>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Skills */}
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
              <Tags className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
              Топ навыков
            </CardTitle>
            <CardDescription>Самые востребованные навыки</CardDescription>
          </CardHeader>
          <CardContent>
            <BarChart
              data={top_skills.slice(0, 10)}
              xKey="name"
              yKey="vacancy_count"
              layout="vertical"
              height={350}
            />
          </CardContent>
        </Card>

        {/* Top Companies */}
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
              <Building2 className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
              Топ компаний
            </CardTitle>
            <CardDescription>Компании с наибольшим числом вакансий</CardDescription>
          </CardHeader>
          <CardContent>
            <BarChart
              data={top_companies}
              xKey="name"
              yKey="vacancy_count"
              layout="vertical"
              height={350}
            />
          </CardContent>
        </Card>
      </div>

      {/* Salary Stats */}
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
            <DollarSign className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
            Статистика зарплат
          </CardTitle>
          <CardDescription>Распределение зарплат по диапазонам</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            <div
              className="text-center p-4 rounded-lg"
              style={{ backgroundColor: 'rgb(var(--bg-header-muted))' }}
            >
              <p className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                Минимальная
              </p>
              <p className="text-xl font-bold" style={{ color: 'rgb(var(--text-primary))' }}>
                {salary_stats.min_salary?.toLocaleString() || '—'} ₽
              </p>
            </div>
            <div
              className="text-center p-4 rounded-lg"
              style={{ backgroundColor: 'rgb(var(--bg-header-muted))' }}
            >
              <p className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                Средняя
              </p>
              <p className="text-xl font-bold" style={{ color: 'rgb(var(--accent))' }}>
                {salary_stats.avg_salary?.toLocaleString() || '—'} ₽
              </p>
            </div>
            <div
              className="text-center p-4 rounded-lg"
              style={{ backgroundColor: 'rgb(var(--bg-header-muted))' }}
            >
              <p className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                Медиана
              </p>
              <p className="text-xl font-bold" style={{ color: 'rgb(var(--text-primary))' }}>
                {salary_stats.median_salary?.toLocaleString() || '—'} ₽
              </p>
            </div>
            <div
              className="text-center p-4 rounded-lg"
              style={{ backgroundColor: 'rgb(var(--bg-header-muted))' }}
            >
              <p className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                Максимальная
              </p>
              <p className="text-xl font-bold" style={{ color: 'rgb(var(--text-primary))' }}>
                {salary_stats.max_salary?.toLocaleString() || '—'} ₽
              </p>
            </div>
          </div>
          <BarChart
            data={salary_stats.distribution.map((d) => ({
              name: d.range_label,
              count: d.count,
            }))}
            xKey="name"
            yKey="count"
            layout="horizontal"
            height={250}
          />
        </CardContent>
      </Card>

      {/* Charts Row 3 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Cities */}
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
              <MapPin className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
              География вакансий
            </CardTitle>
            <CardDescription>Топ городов</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {top_cities.slice(0, 8).map((city, index) => (
                <div key={city.id} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span
                      className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                      style={{
                        backgroundColor: `hsl(${240 - index * 20}, 70%, 60%)`,
                        color: 'white',
                      }}
                    >
                      {index + 1}
                    </span>
                    <span style={{ color: 'rgb(var(--text-primary))' }}>{city.name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium" style={{ color: 'rgb(var(--accent))' }}>
                      {city.vacancy_count}
                    </span>
                    <span className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                      ({city.percentage}%)
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Experience Distribution */}
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
              <Activity className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
              По опыту работы
            </CardTitle>
            <CardDescription>Требования к опыту</CardDescription>
          </CardHeader>
          <CardContent>
            <PieChart
              data={vacancy_detailed_stats.by_experience.map((e) => ({
                name: e.experience,
                count: e.count,
              }))}
              nameKey="name"
              valueKey="count"
              height={250}
              showLegend={true}
              innerRadius={40}
              outerRadius={70}
            />
          </CardContent>
        </Card>

        {/* User Activity */}
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
              <Users className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
              Активность пользователей
            </CardTitle>
            <CardDescription>Статистика за период</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div
                className="flex justify-between items-center p-3 rounded-lg"
                style={{ backgroundColor: 'rgb(var(--bg-header-muted))' }}
              >
                <span style={{ color: 'rgb(var(--text-muted))' }}>Новых сегодня</span>
                <span className="font-bold" style={{ color: 'rgb(var(--accent))' }}>
                  +{user_activity.new_users_today}
                </span>
              </div>
              <div
                className="flex justify-between items-center p-3 rounded-lg"
                style={{ backgroundColor: 'rgb(var(--bg-header-muted))' }}
              >
                <span style={{ color: 'rgb(var(--text-muted))' }}>За неделю</span>
                <span className="font-bold" style={{ color: 'rgb(var(--text-primary))' }}>
                  +{user_activity.new_users_week}
                </span>
              </div>
              <div
                className="flex justify-between items-center p-3 rounded-lg"
                style={{ backgroundColor: 'rgb(var(--bg-header-muted))' }}
              >
                <span style={{ color: 'rgb(var(--text-muted))' }}>За месяц</span>
                <span className="font-bold" style={{ color: 'rgb(var(--text-primary))' }}>
                  +{user_activity.new_users_month}
                </span>
              </div>
              <div
                className="flex justify-between items-center p-3 rounded-lg"
                style={{ backgroundColor: 'rgb(var(--bg-header-muted))' }}
              >
                <span style={{ color: 'rgb(var(--text-muted))' }}>С закладками</span>
                <span className="font-bold" style={{ color: 'rgb(var(--text-primary))' }}>
                  {user_activity.users_with_bookmarks}
                </span>
              </div>
              <div
                className="flex justify-between items-center p-3 rounded-lg"
                style={{ backgroundColor: 'rgb(var(--bg-header-muted))' }}
              >
                <span style={{ color: 'rgb(var(--text-muted))' }}>Ср. закладок на юзера</span>
                <span className="font-bold" style={{ color: 'rgb(var(--text-primary))' }}>
                  {user_activity.avg_bookmarks_per_user}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Sources Table */}
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
            <Server className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
            Детали источников
          </CardTitle>
          <CardDescription>Подробная статистика по каждому источнику</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b" style={{ borderColor: 'rgb(var(--border))' }}>
                  <th className="text-left py-3 px-4" style={{ color: 'rgb(var(--text-muted))' }}>
                    Источник
                  </th>
                  <th className="text-left py-3 px-4" style={{ color: 'rgb(var(--text-muted))' }}>
                    Тип
                  </th>
                  <th className="text-right py-3 px-4" style={{ color: 'rgb(var(--text-muted))' }}>
                    Всего
                  </th>
                  <th className="text-right py-3 px-4" style={{ color: 'rgb(var(--text-muted))' }}>
                    Активных
                  </th>
                  <th className="text-right py-3 px-4" style={{ color: 'rgb(var(--text-muted))' }}>
                    Ср. зарплата
                  </th>
                  <th className="text-right py-3 px-4" style={{ color: 'rgb(var(--text-muted))' }}>
                    Доля
                  </th>
                </tr>
              </thead>
              <tbody>
                {sources_stats.map((source) => (
                  <tr
                    key={source.id}
                    className="border-b hover:bg-[rgb(var(--bg-header-muted))]"
                    style={{ borderColor: 'rgb(var(--border))' }}
                  >
                    <td
                      className="py-3 px-4 font-medium"
                      style={{ color: 'rgb(var(--text-primary))' }}
                    >
                      {source.name}
                    </td>
                    <td className="py-3 px-4" style={{ color: 'rgb(var(--text-muted))' }}>
                      {source.source_type}
                    </td>
                    <td
                      className="py-3 px-4 text-right"
                      style={{ color: 'rgb(var(--text-primary))' }}
                    >
                      {source.vacancy_count.toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-right" style={{ color: 'rgb(var(--accent))' }}>
                      {source.active_vacancy_count.toLocaleString()}
                    </td>
                    <td
                      className="py-3 px-4 text-right"
                      style={{ color: 'rgb(var(--text-primary))' }}
                    >
                      {source.avg_salary ? `${source.avg_salary.toLocaleString()} ₽` : '—'}
                    </td>
                    <td
                      className="py-3 px-4 text-right"
                      style={{ color: 'rgb(var(--text-muted))' }}
                    >
                      {source.percentage}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Footer */}
      <div className="text-center text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
        Данные обновлены: {new Date(analytics.generated_at).toLocaleString('ru-RU')}
      </div>
    </div>
  );
}
